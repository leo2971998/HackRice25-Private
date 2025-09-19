"""User-facing Nessie helpers with Firestore-backed user storage."""

import hashlib
import os
import uuid
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Tuple

import requests
from flask import Blueprint, jsonify, g, request

from .auth import require_auth
from utils.firestore_db import (
    get_user as firestore_get_user,
    update_user as firestore_update_user,
    get_user_ap2_transactions,
)


BASE = os.getenv("NESSIE_BASE", "https://api.nessieisreal.com")
API_KEY = os.environ.get("NESSIE_API_KEY", "")
USE_MOCK = os.environ.get("USE_MOCK", "0") == "1"

bp = Blueprint("me_nessie", __name__)


def nx(path: str) -> str:
    return f"{BASE}{path}?key={API_KEY}"


ENHANCED_MOCK_SUMMARY = {
    "total_balance": 1140.85,
    "accounts": [
        {
            "_id": "mock_account_001",
            "type": "Checking",
            "nickname": "Main Checking",
            "balance": 1140.85,
            "rewards": 0,
        }
    ],
    "recent_transactions": [
        {
            "_id": "mock_purchase_001",
            "description": "Metro Transit",
            "amount": 15.00,
            "purchase_date": "2025-01-15",
            "type": "purchase",
        },
        {
            "_id": "mock_purchase_002",
            "description": "CVS Pharmacy",
            "amount": 28.47,
            "purchase_date": "2025-01-14",
            "type": "purchase",
        },
        {
            "_id": "mock_purchase_003",
            "description": "Starbucks Coffee",
            "amount": 4.95,
            "purchase_date": "2025-01-13",
            "type": "purchase",
        },
        {
            "_id": "mock_purchase_004",
            "description": "Shell Gas Station",
            "amount": 45.20,
            "purchase_date": "2025-01-12",
            "type": "purchase",
        },
        {
            "_id": "mock_purchase_005",
            "description": "H-E-B Groceries",
            "amount": 87.33,
            "purchase_date": "2025-01-11",
            "type": "purchase",
        },
        {
            "_id": "mock_purchase_006",
            "description": "Uber Ride",
            "amount": 12.50,
            "purchase_date": "2025-01-10",
            "type": "purchase",
        },
        {
            "_id": "mock_purchase_007",
            "description": "Electric Bill",
            "amount": 89.45,
            "purchase_date": "2025-01-08",
            "type": "purchase",
        },
        {
            "_id": "mock_purchase_008",
            "description": "Water Bill",
            "amount": 34.20,
            "purchase_date": "2025-01-07",
            "type": "purchase",
        },
        {
            "_id": "mock_purchase_009",
            "description": "Internet Service",
            "amount": 79.99,
            "purchase_date": "2025-01-05",
            "type": "purchase",
        },
        {
            "_id": "mock_purchase_010",
            "description": "Target",
            "amount": 156.78,
            "purchase_date": "2025-01-03",
            "type": "purchase",
        },
        {
            "_id": "mock_deposit_001",
            "description": "Paycheck Deposit",
            "amount": 1350.00,
            "transaction_date": "2025-01-09",
            "type": "deposit",
        },
        {
            "_id": "mock_deposit_002",
            "description": "Freelance Payment",
            "amount": 450.00,
            "transaction_date": "2025-01-02",
            "type": "deposit",
        },
    ],
    "customer_id": "mock_customer_enhanced",
}


def _transaction_category_key(transaction: Dict[str, Any]) -> str:
    """Create a stable hash to use as a transaction category key."""

    base_identifier = (
        transaction.get("_id")
        or "|".join(
            [
                str(transaction.get("type", "")),
                str(transaction.get("description", "")),
                str(transaction.get("transaction_date") or transaction.get("purchase_date") or ""),
                str(transaction.get("amount", "")),
            ]
        )
    )
    return hashlib.sha256(base_identifier.encode("utf-8")).hexdigest()


def _decorate_transactions(transactions: Dict[str, Any]) -> None:
    for transaction in transactions:
        transaction.setdefault("type", "deposit" if transaction.get("transaction_date") else "purchase")
        transaction["category_key"] = _transaction_category_key(transaction)


MOCK_USER_STATE: Dict[str, Dict[str, Any]] = {}


def _get_mock_user_state(user_id: str) -> Dict[str, Any]:
    state = MOCK_USER_STATE.get(user_id)
    if not state:
        state = {
            "total_balance": ENHANCED_MOCK_SUMMARY["total_balance"],
            "accounts": deepcopy(ENHANCED_MOCK_SUMMARY["accounts"]),
            "recent_transactions": deepcopy(ENHANCED_MOCK_SUMMARY["recent_transactions"]),
            "user_categories": {},
            "ap2_summary": {
                "active_count": 2,
                "pending_count": 0,
                "estimated_savings": 500,
            },
        }
        _decorate_transactions(state["recent_transactions"])
        MOCK_USER_STATE[user_id] = state
    return state


def _get_primary_account(customer_id: str) -> Tuple[str, Any]:
    accounts_resp = requests.get(nx(f"/customers/{customer_id}/accounts"), timeout=20)
    accounts_resp.raise_for_status()
    accounts = accounts_resp.json()
    if not accounts:
        raise ValueError("No accounts for customer")
    return accounts[0]["_id"], accounts


def _build_ap2_summary(user_id: str) -> Dict[str, Any]:
    transactions, _ = get_user_ap2_transactions(user_id)
    if not transactions:
        return {"active_count": 0, "pending_count": 0, "estimated_savings": 0}

    active_statuses = {"approved", "executed"}
    active = [tx for tx in transactions if tx.get("status") in active_statuses]
    pending = [tx for tx in transactions if tx.get("status") == "pending"]

    estimated = 0
    for tx in active:
        intent_data = tx.get("intent_mandate") or {}
        cart_data = tx.get("cart_mandate") or {}
        payment_data = tx.get("payment_mandate") or {}
        estimated += intent_data.get("amount", 0) or cart_data.get("total_amount", 0) or payment_data.get("amount", 0)

    return {
        "active_count": len(active),
        "pending_count": len(pending),
        "estimated_savings": round(estimated, 2),
    }


@bp.post("/me/seed")
@require_auth
def seed():
    user, message = firestore_get_user(g.uid)
    if not user:
        return jsonify({"error": message}), 404

    cust_id = user.get("nessie_customer_id") or ""

    if not cust_id:
        try:
            if USE_MOCK:
                cust_id = f"mock_{str(uuid.uuid4())[:8]}"
            else:
                body = {
                    "first_name": user.get("first_name") or "Houston",
                    "last_name": user.get("last_name") or "Resident",
                    "address": {
                        "street_number": "123",
                        "street_name": "Main St",
                        "city": "Houston",
                        "state": "TX",
                        "zip": "77002",
                    },
                }
                response = requests.post(nx("/customers"), json=body, timeout=20)
                response.raise_for_status()
                cust_id = response.json()["_id"]
        except Exception as exc:
            print(f"Nessie API error: {exc}, falling back to mock")
            cust_id = f"mock_fallback_{str(uuid.uuid4())[:8]}"

        firestore_update_user(g.uid, {"nessie_customer_id": cust_id})

    try:
        if cust_id.startswith("mock"):
            pass
        else:
            accounts = requests.get(nx(f"/customers/{cust_id}/accounts"), timeout=20).json()
            if not accounts:
                account_payload = {
                    "type": "Checking",
                    "nickname": "Main Checking",
                    "rewards": 0,
                    "balance": 1200,
                }
                created = requests.post(nx(f"/customers/{cust_id}/accounts"), json=account_payload, timeout=20).json()
                account_id = created.get("_id")
                if account_id:
                    requests.post(nx(f"/accounts/{account_id}/deposits"), json={"amount": 1200, "description": "Paycheck", "transaction_date": "2025-09-01"}, timeout=20)
                    requests.post(nx(f"/accounts/{account_id}/purchases"), json={"amount": 42.35, "description": "H-E-B Groceries", "purchase_date": "2025-09-02"}, timeout=20)
                    requests.post(nx(f"/accounts/{account_id}/purchases"), json={"amount": 16.80, "description": "Shell Gas", "purchase_date": "2025-09-03"}, timeout=20)
    except Exception:
        pass

    return jsonify(ok=True, customer_id=cust_id)


@bp.get("/me/summary")
@require_auth
def my_summary():
    user, message = firestore_get_user(g.uid)
    if not user:
        return jsonify({"error": message}), 404

    cust_id = user.get("nessie_customer_id") or ""
    if not cust_id:
        return jsonify(error="no_nessie_customer"), 404

    if USE_MOCK or cust_id.startswith("mock"):
        state = _get_mock_user_state(g.uid)
        payload = deepcopy(state)
        return jsonify(
            {
                "total_balance": payload["total_balance"],
                "accounts": payload["accounts"],
                "recent_transactions": payload["recent_transactions"],
                "customer_id": ENHANCED_MOCK_SUMMARY["customer_id"],
                "user_categories": payload.get("user_categories", {}),
                "ap2_summary": payload.get("ap2_summary", {}),
            }
        )

    try:
        accounts_resp = requests.get(nx(f"/customers/{cust_id}/accounts"), timeout=20)
        accounts = accounts_resp.json() if accounts_resp.status_code == 200 else []

        total_balance = sum(acc.get("balance", 0) for acc in accounts)
        recent_transactions = []

        if accounts:
            account_id = accounts[0]["_id"]
            deposits_resp = requests.get(nx(f"/accounts/{account_id}/deposits"), timeout=20)
            deposits = deposits_resp.json() if deposits_resp.status_code == 200 else []
            purchases_resp = requests.get(nx(f"/accounts/{account_id}/purchases"), timeout=20)
            purchases = purchases_resp.json() if purchases_resp.status_code == 200 else []

            for deposit in deposits:
                deposit["type"] = "deposit"
                deposit["category_key"] = _transaction_category_key(deposit)
            for purchase in purchases:
                purchase["type"] = "purchase"
                purchase["category_key"] = _transaction_category_key(purchase)

            recent_transactions = deposits + purchases
            recent_transactions.sort(key=lambda x: x.get("transaction_date", x.get("purchase_date", "")), reverse=True)
            recent_transactions = recent_transactions[:25]

        user_categories = {}
        if user.get("transaction_categories"):
            user_categories = user["transaction_categories"]

        return jsonify(
            {
                "total_balance": total_balance,
                "accounts": accounts,
                "recent_transactions": recent_transactions,
                "customer_id": cust_id,
                "user_categories": user_categories,
                "ap2_summary": _build_ap2_summary(g.uid),
            }
        )
    except Exception as exc:
        print(f"Nessie API error in summary: {exc}, falling back to mock")
        state = _get_mock_user_state(g.uid)
        payload = deepcopy(state)
        return jsonify(
            {
                "total_balance": payload["total_balance"],
                "accounts": payload["accounts"],
                "recent_transactions": payload["recent_transactions"],
                "customer_id": ENHANCED_MOCK_SUMMARY["customer_id"],
                "user_categories": payload.get("user_categories", {}),
                "ap2_summary": payload.get("ap2_summary", {}),
            }
        )


@bp.post("/me/transactions/deposits")
@require_auth
def create_deposit():
    body = request.get_json() or {}
    amount = float(body.get("amount", 0))
    description = (body.get("description") or "Deposit").strip()
    date = body.get("date") or datetime.utcnow().strftime("%Y-%m-%d")

    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400

    user, message = firestore_get_user(g.uid)
    if not user:
        return jsonify({"error": message}), 404

    cust_id = user.get("nessie_customer_id") or ""
    if not cust_id:
        return jsonify({"error": "no_nessie_customer"}), 400

    transaction = {
        "description": description or "Deposit",
        "amount": round(amount, 2),
        "transaction_date": date,
        "type": "deposit",
        "status": "posted",
    }

    if USE_MOCK or cust_id.startswith("mock"):
        state = _get_mock_user_state(g.uid)
        transaction["_id"] = f"mock_deposit_{uuid.uuid4().hex[:8]}"
        transaction["category_key"] = _transaction_category_key(transaction)
        state["recent_transactions"].insert(0, transaction)
        state["total_balance"] = round(state["total_balance"] + amount, 2)
        return jsonify({"transaction": transaction, "total_balance": state["total_balance"]})

    try:
        account_id, accounts = _get_primary_account(cust_id)
        payload = {
            "amount": amount,
            "description": description or "Deposit",
            "transaction_date": date,
        }
        response = requests.post(nx(f"/accounts/{account_id}/deposits"), json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        data["type"] = "deposit"
        data["category_key"] = _transaction_category_key(data)
        return jsonify({"transaction": data, "accounts": accounts})
    except Exception as exc:
        return jsonify({"error": f"Failed to create deposit: {exc}"}), 500


@bp.post("/me/transactions/purchases")
@require_auth
def create_purchase():
    body = request.get_json() or {}
    amount = float(body.get("amount", 0))
    description = (body.get("description") or "Purchase").strip()
    date = body.get("date") or datetime.utcnow().strftime("%Y-%m-%d")

    if amount <= 0:
        return jsonify({"error": "amount must be positive"}), 400

    user, message = firestore_get_user(g.uid)
    if not user:
        return jsonify({"error": message}), 404

    cust_id = user.get("nessie_customer_id") or ""
    if not cust_id:
        return jsonify({"error": "no_nessie_customer"}), 400

    transaction = {
        "description": description or "Purchase",
        "amount": round(amount, 2),
        "purchase_date": date,
        "type": "purchase",
        "status": "posted",
    }

    if USE_MOCK or cust_id.startswith("mock"):
        state = _get_mock_user_state(g.uid)
        transaction["_id"] = f"mock_purchase_{uuid.uuid4().hex[:8]}"
        transaction["category_key"] = _transaction_category_key(transaction)
        state["recent_transactions"].insert(0, transaction)
        state["total_balance"] = round(state["total_balance"] - amount, 2)
        return jsonify({"transaction": transaction, "total_balance": state["total_balance"]})

    try:
        account_id, accounts = _get_primary_account(cust_id)
        payload = {
            "amount": amount,
            "description": description or "Purchase",
            "purchase_date": date,
        }
        response = requests.post(nx(f"/accounts/{account_id}/purchases"), json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        data["type"] = "purchase"
        data["category_key"] = _transaction_category_key(data)
        return jsonify({"transaction": data, "accounts": accounts})
    except Exception as exc:
        return jsonify({"error": f"Failed to create purchase: {exc}"}), 500


@bp.post("/me/transactions/categorize")
@require_auth
def categorize_transaction():
    body = request.get_json() or {}
    category_key = body.get("category_key")
    category = (body.get("category") or "").strip()

    if not category_key or not category:
        return jsonify({"error": "category_key and category are required"}), 400

    user, message = firestore_get_user(g.uid)
    if not user:
        return jsonify({"error": message}), 404

    categories = user.get("transaction_categories", {})
    categories[category_key] = category

    success, update_message = firestore_update_user(g.uid, {"transaction_categories": categories})
    if not success:
        print(f"Warning: failed to persist category preference: {update_message}")

    if USE_MOCK or (user.get("nessie_customer_id") or "").startswith("mock"):
        state = _get_mock_user_state(g.uid)
        state.setdefault("user_categories", {})[category_key] = category

    return jsonify({"category_key": category_key, "category": category, "persisted": success})
