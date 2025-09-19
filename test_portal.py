"""Smoke tests for the updated Inflate-Wise data pipeline."""

from datetime import datetime, timedelta

from utils.inflation import calculate_personal_inflation


def test_calculate_personal_inflation_uses_recent_transactions():
    today = datetime.utcnow().date()
    transactions = [
        {"transaction_id": "t1", "name": "H-E-B", "amount": 82.5, "date": today.isoformat()},
        {"transaction_id": "t2", "name": "Shell", "amount": 45.2, "date": (today - timedelta(days=2)).isoformat()},
        {"transaction_id": "t3", "name": "Netflix", "amount": 15.99, "date": (today - timedelta(days=40)).isoformat()},
    ]

    snapshot = calculate_personal_inflation(transactions, overrides={})

    assert snapshot["total_spend"] > 0
    assert "Groceries" in snapshot["category_totals"]
    assert "Gasoline" in snapshot["category_totals"]
    # Netflix is outside 30 day window and should not affect totals
    assert "Entertainment" not in snapshot["category_totals"]


def test_overrides_take_priority_over_ai_categories():
    today = datetime.utcnow().date()
    transactions = [
        {"transaction_id": "t4", "name": "Starbucks", "amount": 12.5, "date": today.isoformat()},
    ]
    overrides = {"t4": "Travel"}

    snapshot = calculate_personal_inflation(transactions, overrides)
    assert snapshot["category_totals"].get("Travel") == 12.5
    assert snapshot["category_weights"].get("Travel") == 1.0
