"""Endpoints for transaction sync, categorisation, and summaries."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from flask import Blueprint, jsonify, request, g

from routes.auth import require_auth
from utils.firestore_db import (
    create_manual_transaction,
    get_category_overrides,
    get_user,
    list_manual_transactions,
    save_inflation_snapshot,
    save_plaid_cursor,
    set_category_override,
)
from utils.inflation import calculate_personal_inflation
from utils.plaid_client import get_account_balances, sync_transactions

bp = Blueprint("transactions", __name__)


def _coerce_amount(value: Any) -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return 0.0
    return round(amount, 2)


def _coerce_date(value: Any) -> str:
    if not value:
        return datetime.utcnow().date().isoformat()
    if isinstance(value, datetime):
        return value.date().isoformat()
    try:
        return datetime.fromisoformat(str(value)).date().isoformat()
    except Exception:
        return datetime.utcnow().date().isoformat()


def _format_manual_transaction(raw: Dict[str, Any]) -> Dict[str, Any]:
    transaction_type = (raw.get("transaction_type") or "purchase").lower()
    occurred_at = raw.get("occurred_at")
    if hasattr(occurred_at, "isoformat"):
        occurred_at = occurred_at.isoformat()
    elif not occurred_at:
        occurred_at = datetime.utcnow().date().isoformat()

    name = raw.get("name") or raw.get("merchant_name") or raw.get("description")
    if not name:
        name = "Manual deposit" if transaction_type == "deposit" else "Manual purchase"

    category = raw.get("category")
    if not category:
        category = "Income" if transaction_type == "deposit" else "Other"

    transaction: Dict[str, Any] = {
        "transaction_id": raw.get("id") or raw.get("transaction_id") or name,
        "name": name,
        "merchant_name": raw.get("merchant_name"),
        "amount": _coerce_amount(raw.get("amount")),
        "date": occurred_at,
        "transaction_type": transaction_type,
        "category": category,
    }
    if raw.get("notes"):
        transaction["notes"] = raw["notes"]
    return transaction


@bp.get("/transactions")
@require_auth
def get_transactions():
    user, _ = get_user(g.uid, include_sensitive=True)
    if not user:
        return jsonify({"error": "User not found"}), 404

    manual_docs, _ = list_manual_transactions(g.uid)
    manual_transactions = [_format_manual_transaction(doc) for doc in manual_docs]

    access_token = user.get("plaid_access_token")
    transactions: List[Dict[str, Any]] = []
    next_cursor = None
    balances: Dict[str, Any] | None = None

    if access_token:
        cursor = user.get("plaid_cursor")
        sync = sync_transactions(access_token, cursor)
        next_cursor = sync.get("next_cursor")
        if next_cursor and next_cursor != cursor:
            save_plaid_cursor(g.uid, next_cursor)

        transactions = (sync.get("added") or []) + (sync.get("modified") or [])
        transactions.extend(manual_transactions)
        balances, _ = get_account_balances(access_token)
    else:
        transactions = list(manual_transactions)

    manual_balance = 0.0
    for ledger_tx in manual_transactions:
        if ledger_tx.get("transaction_type") == "deposit":
            manual_balance += ledger_tx.get("amount", 0)
        else:
            manual_balance -= ledger_tx.get("amount", 0)
    manual_balance = round(manual_balance, 2)

    manual_account = {
        "name": "Manual Spending Ledger",
        "type": "mock",
        "subtype": "wallet",
        "balances": {"available": manual_balance, "current": manual_balance},
    }

    if balances and isinstance(balances, dict):
        balances.setdefault("accounts", [])
        balances["accounts"].append(manual_account)
    else:
        balances = {"accounts": [manual_account]}

    overrides = get_category_overrides(g.uid)
    summary = calculate_personal_inflation(transactions, overrides)
    save_inflation_snapshot(g.uid, summary)

    manual_lookup = {tx["transaction_id"]: tx for tx in manual_transactions}
    combined: List[Dict[str, Any]] = []
    seen_ids = set()
    for tx in summary.get("transactions", []):
        record = dict(tx)
        ledger_meta = manual_lookup.get(record.get("transaction_id"))
        if ledger_meta:
            record["transaction_type"] = ledger_meta.get("transaction_type", record.get("transaction_type", "purchase"))
            if ledger_meta.get("notes"):
                record["notes"] = ledger_meta["notes"]
        else:
            record.setdefault("transaction_type", "purchase")
        combined.append(record)
        seen_ids.add(record.get("transaction_id"))

    for ledger_tx in manual_transactions:
        if ledger_tx.get("transaction_id") not in seen_ids:
            combined.append(ledger_tx)
            seen_ids.add(ledger_tx.get("transaction_id"))

    combined.sort(key=lambda item: item.get("date", ""), reverse=True)

    return jsonify({
        "transactions": combined,
        "category_totals": summary.get("category_totals", {}),
        "personal_inflation": {
            "personal_rate": summary.get("personal_rate"),
            "national_rate": summary.get("national_rate"),
            "top_drivers": summary.get("top_drivers", []),
            "category_weights": summary.get("category_weights", {}),
            "total_spend": summary.get("total_spend", 0),
        },
        "cpi_reference": summary.get("cpi_reference", {}),
        "balances": balances,
        "overrides": overrides,
        "next_cursor": next_cursor,
    })


@bp.post("/transactions/categorize")
@require_auth
def override_category():
    data = request.get_json() or {}
    transaction_id = data.get("transaction_id")
    category = data.get("category")

    if not transaction_id or not category:
        return jsonify({"error": "transaction_id and category are required"}), 400

    success, message = set_category_override(g.uid, transaction_id, category)
    if not success:
        return jsonify({"error": message}), 500

    return jsonify({"ok": True, "transaction_id": transaction_id, "category": category})


@bp.post("/transactions/manual/deposit")
@require_auth
def create_deposit():
    data = request.get_json() or {}
    amount = _coerce_amount(data.get("amount"))
    source = (data.get("source") or data.get("name") or "").strip()
    notes = (data.get("notes") or "").strip()
    occurred_at = _coerce_date(data.get("date") or data.get("occurred_at"))

    if amount <= 0:
        return jsonify({"error": "amount must be greater than zero"}), 400

    payload = {
        "transaction_type": "deposit",
        "amount": amount,
        "name": source or "Manual deposit",
        "category": "Income",
        "occurred_at": occurred_at,
    }
    if notes:
        payload["notes"] = notes

    success, result = create_manual_transaction(g.uid, payload)
    if not success:
        status = 503 if "not available" in result.lower() else 500
        return jsonify({"error": result}), status

    transaction = _format_manual_transaction({**payload, "id": result})
    return jsonify({"ok": True, "transaction": transaction}), 201


@bp.post("/transactions/manual/purchase")
@require_auth
def create_purchase():
    data = request.get_json() or {}
    amount = _coerce_amount(data.get("amount"))
    merchant = (data.get("merchant") or data.get("name") or "").strip()
    category = (data.get("category") or "Other").strip() or "Other"
    notes = (data.get("notes") or "").strip()
    occurred_at = _coerce_date(data.get("date") or data.get("occurred_at"))

    if amount <= 0:
        return jsonify({"error": "amount must be greater than zero"}), 400

    payload = {
        "transaction_type": "purchase",
        "amount": amount,
        "name": merchant or "Manual purchase",
        "merchant_name": merchant or None,
        "category": category,
        "occurred_at": occurred_at,
    }
    if notes:
        payload["notes"] = notes

    success, result = create_manual_transaction(g.uid, payload)
    if not success:
        status = 503 if "not available" in result.lower() else 500
        return jsonify({"error": result}), status

    transaction = _format_manual_transaction({**payload, "id": result})
    return jsonify({"ok": True, "transaction": transaction}), 201
