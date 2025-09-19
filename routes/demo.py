"""Demo seeding utilities that store users in Firestore."""

import os
import uuid
from typing import Dict, Optional

import requests
from flask import Blueprint, jsonify

from utils.firestore_db import (
    create_user as firestore_create_user,
    get_user as firestore_get_user,
    get_user_by_email,
    update_user as firestore_update_user,
)


BASE = os.getenv("NESSIE_BASE", "https://api.nessieisreal.com")
API_KEY = os.environ.get("NESSIE_API_KEY", "")
USE_MOCK = os.environ.get("USE_MOCK", "0") == "1"

bp = Blueprint("demo", __name__)


def nx(path: str) -> str:
    return f"{BASE}{path}?key={API_KEY}"


def _demo_email() -> str:
    suffix = API_KEY[-8:] if API_KEY else "default"
    return f"demo_user_{suffix}@demo.local"


def _find_existing_demo_user() -> Optional[Dict]:
    email = _demo_email()
    user, _ = get_user_by_email(email)
    return user


def _create_demo_user() -> Dict:
    email = _demo_email()

    if USE_MOCK:
        customer_id = f"demo_mock_{str(uuid.uuid4())[:8]}"
    else:
        try:
            body = {
                "first_name": "Demo",
                "last_name": "User",
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
            customer_id = response.json()["_id"]
        except Exception as exc:  # pragma: no cover - fallback path
            print(f"Nessie API error: {exc}, falling back to mock")
            customer_id = f"demo_fallback_{str(uuid.uuid4())[:8]}"

    payload = {
        "password_hash": "demo_hash",
        "first_name": "Demo",
        "last_name": "User",
        "nessie_customer_id": customer_id,
        "role": "user",
    }

    success, result = firestore_create_user(email, payload)
    if not success and "already registered" not in result.lower():
        raise RuntimeError(result)

    if success:
        created_id = result
        user, _ = firestore_get_user(created_id)
        if user:
            return user

    existing_user = _find_existing_demo_user()
    if not existing_user:
        raise RuntimeError("Unable to provision demo user in Firestore")

    # Ensure Nessie customer ID is up to date
    firestore_update_user(existing_user["id"], {"nessie_customer_id": customer_id})
    existing_user["nessie_customer_id"] = customer_id
    return existing_user


def _get_frozen_seed_data() -> Dict:
    return {
        "deposit": {
            "amount": 1350.00,
            "description": "Paycheck Deposit",
            "transaction_date": "2025-01-09",
        },
        "purchases": [
            {"amount": 87.33, "description": "H-E-B Groceries", "purchase_date": "2025-01-11"},
            {"amount": 45.20, "description": "Shell Gas Station", "purchase_date": "2025-01-12"},
            {"amount": 4.95, "description": "Starbucks Coffee", "purchase_date": "2025-01-13"},
            {"amount": 28.47, "description": "CVS Pharmacy", "purchase_date": "2025-01-14"},
            {"amount": 12.50, "description": "Uber Ride", "purchase_date": "2025-01-10"},
            {"amount": 15.00, "description": "Metro Transit", "purchase_date": "2025-01-15"},
        ],
    }


def _seed_demo_data(customer_id: str) -> bool:
    if customer_id.startswith("demo_mock") or customer_id.startswith("demo_fallback") or USE_MOCK:
        return True

    try:
        accounts_resp = requests.get(nx(f"/customers/{customer_id}/accounts"), timeout=20)
        accounts = accounts_resp.json() if accounts_resp.status_code == 200 else []

        if not accounts:
            account_data = {
                "type": "Checking",
                "nickname": "Main Checking",
                "rewards": 0,
                "balance": 1350.00,
            }
            acc_resp = requests.post(nx(f"/customers/{customer_id}/accounts"), json=account_data, timeout=20)
            acc_resp.raise_for_status()
            account_id = acc_resp.json()["_id"]

            seed_data = _get_frozen_seed_data()
            requests.post(nx(f"/accounts/{account_id}/deposits"), json=seed_data["deposit"], timeout=20)
            for purchase in seed_data["purchases"]:
                requests.post(nx(f"/accounts/{account_id}/purchases"), json=purchase, timeout=20)

        return True
    except Exception as exc:  # pragma: no cover - remote API failure tolerance
        print(f"Error seeding demo data: {exc}")
        return False


MOCK_SUMMARY_DATA = {
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
        {"description": "Starbucks", "amount": 4.95, "purchase_date": "2025-01-13", "type": "purchase"},
        {"description": "Shell Gas Station", "amount": 45.20, "purchase_date": "2025-01-12", "type": "purchase"},
        {"description": "H-E-B Groceries", "amount": 87.33, "purchase_date": "2025-01-11", "type": "purchase"},
        {"description": "Uber Ride", "amount": 12.50, "purchase_date": "2025-01-10", "type": "purchase"},
        {"description": "Paycheck Deposit", "amount": 1350.00, "transaction_date": "2025-01-09", "type": "deposit"},
    ],
    "customer_id": "demo_customer_mock",
}


@bp.get("/demo")
def demo_root():
    return jsonify({"demo": "ok"}), 200


@bp.post("/demo/seed")
def demo_seed():
    try:
        existing_user = _find_existing_demo_user()
        if existing_user and existing_user.get("nessie_customer_id"):
            return jsonify(
                {
                    "ok": True,
                    "customer_id": existing_user["nessie_customer_id"],
                    "user_id": existing_user["id"],
                    "reused": True,
                }
            )

        demo_user = _create_demo_user()
        customer_id = demo_user["nessie_customer_id"]
        _seed_demo_data(customer_id)

        return jsonify({"ok": True, "customer_id": customer_id, "user_id": demo_user["id"], "reused": False})
    except Exception as exc:
        return jsonify({"error": f"Demo seed failed: {exc}"}), 500


@bp.get("/demo/summary")
def demo_summary():
    if USE_MOCK:
        return jsonify(MOCK_SUMMARY_DATA)

    try:
        demo_user = _find_existing_demo_user()
        if not demo_user:
            return jsonify({"error": "No demo user found. Call /demo/seed first"}), 404

        customer_id = demo_user.get("nessie_customer_id") or ""
        if not customer_id:
            return jsonify({"error": "Demo user missing customer"}), 404

        if customer_id.startswith("demo_mock") or customer_id.startswith("demo_fallback"):
            return jsonify(MOCK_SUMMARY_DATA)

        try:
            accounts_resp = requests.get(nx(f"/customers/{customer_id}/accounts"), timeout=20)
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
                    "customer_id": customer_id,
                }
            )
        except Exception as api_error:
            print(f"Nessie API error, falling back to mock: {api_error}")
            return jsonify(MOCK_SUMMARY_DATA)

    except Exception as exc:
        return jsonify({"error": f"Demo summary failed: {exc}"}), 500
