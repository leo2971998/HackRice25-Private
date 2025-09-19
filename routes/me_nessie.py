"""User-facing Nessie helpers with Firestore-backed user storage."""

import os
import uuid

import requests
from flask import Blueprint, jsonify, g

from .auth import require_auth
from utils.firestore_db import get_user as firestore_get_user, update_user as firestore_update_user


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
        {"description": "Metro Transit", "amount": 15.00, "purchase_date": "2025-01-15", "type": "purchase"},
        {"description": "CVS Pharmacy", "amount": 28.47, "purchase_date": "2025-01-14", "type": "purchase"},
        {"description": "Starbucks Coffee", "amount": 4.95, "purchase_date": "2025-01-13", "type": "purchase"},
        {"description": "Shell Gas Station", "amount": 45.20, "purchase_date": "2025-01-12", "type": "purchase"},
        {"description": "H-E-B Groceries", "amount": 87.33, "purchase_date": "2025-01-11", "type": "purchase"},
        {"description": "Uber Ride", "amount": 12.50, "purchase_date": "2025-01-10", "type": "purchase"},
        {"description": "Electric Bill", "amount": 89.45, "purchase_date": "2025-01-08", "type": "purchase"},
        {"description": "Water Bill", "amount": 34.20, "purchase_date": "2025-01-07", "type": "purchase"},
        {"description": "Internet Service", "amount": 79.99, "purchase_date": "2025-01-05", "type": "purchase"},
        {"description": "Target", "amount": 156.78, "purchase_date": "2025-01-03", "type": "purchase"},
        {"description": "Paycheck Deposit", "amount": 1350.00, "transaction_date": "2025-01-09", "type": "deposit"},
        {"description": "Freelance Payment", "amount": 450.00, "transaction_date": "2025-01-02", "type": "deposit"},
    ],
    "customer_id": "mock_customer_enhanced",
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
        return jsonify(ENHANCED_MOCK_SUMMARY)

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
            for purchase in purchases:
                purchase["type"] = "purchase"

            recent_transactions = deposits + purchases
            recent_transactions.sort(key=lambda x: x.get("transaction_date", x.get("purchase_date", "")), reverse=True)
            recent_transactions = recent_transactions[:25]

        return jsonify(
            {
                "total_balance": total_balance,
                "accounts": accounts,
                "recent_transactions": recent_transactions,
                "customer_id": cust_id,
            }
        )
    except Exception as exc:
        print(f"Nessie API error in summary: {exc}, falling back to mock")
        return jsonify(ENHANCED_MOCK_SUMMARY)
