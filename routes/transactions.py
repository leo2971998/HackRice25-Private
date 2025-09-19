"""Endpoints for transaction sync, categorisation, and summaries."""

from __future__ import annotations

from flask import Blueprint, jsonify, request, g

from routes.auth import require_auth
from utils.firestore_db import (
    get_category_overrides,
    get_user,
    save_inflation_snapshot,
    save_plaid_cursor,
    set_category_override,
)
from utils.inflation import calculate_personal_inflation
from utils.plaid_client import get_account_balances, sync_transactions

bp = Blueprint("transactions", __name__)


@bp.get("/transactions")
@require_auth
def get_transactions():
    user, _ = get_user(g.uid, include_sensitive=True)
    if not user:
        return jsonify({"error": "User not found"}), 404

    access_token = user.get("plaid_access_token")
    if not access_token:
        return jsonify({"error": "Plaid account not linked"}), 400

    cursor = user.get("plaid_cursor")
    sync = sync_transactions(access_token, cursor)
    next_cursor = sync.get("next_cursor")
    if next_cursor and next_cursor != cursor:
        save_plaid_cursor(g.uid, next_cursor)

    transactions = (sync.get("added") or []) + (sync.get("modified") or [])
    overrides = get_category_overrides(g.uid)
    summary = calculate_personal_inflation(transactions, overrides)
    save_inflation_snapshot(g.uid, summary)

    balances, _ = get_account_balances(access_token)

    return jsonify({
        "transactions": summary.get("transactions", []),
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
