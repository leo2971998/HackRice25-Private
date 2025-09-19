"""End-to-end style tests covering the inflation pipeline helpers."""

from datetime import datetime

from utils.inflation import calculate_personal_inflation


def build_transaction(name: str, amount: float) -> dict:
    return {
        "transaction_id": f"tx-{name.lower()}",
        "name": name,
        "amount": amount,
        "date": datetime.utcnow().date().isoformat(),
    }


def test_empty_transactions_returns_defaults():
    snapshot = calculate_personal_inflation([], overrides={})
    assert snapshot["personal_rate"] is None
    assert snapshot["category_totals"] == {}


def test_weighted_average_changes_with_mix():
    groceries = build_transaction("H-E-B", 200)
    gasoline = build_transaction("Shell", 50)
    travel = build_transaction("United", 400)

    snapshot = calculate_personal_inflation([groceries, gasoline, travel], overrides={})
    weights = snapshot["category_weights"]
    assert round(weights["Travel"], 3) > round(weights["Gasoline"], 3)
    assert snapshot["personal_rate"] is not None
