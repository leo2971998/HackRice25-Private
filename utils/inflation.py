"""Utilities for mapping transactions to CPI categories and computing personal inflation."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Tuple

import requests

from utils.gemini import categorize_transaction

APP_CATEGORY_TO_CPI = {
    "Groceries": {"series_id": "CUSR0000SAF11", "label": "Food at home"},
    "Gasoline": {"series_id": "CUSR0000SETB01", "label": "Gasoline (all types)"},
    "Restaurants": {"series_id": "CUSR0000SEFV", "label": "Food away from home"},
    "Utilities": {"series_id": "CUSR0000SAH2", "label": "Household energy"},
    "Housing": {"series_id": "CUSR0000SAH1", "label": "Shelter"},
    "Shopping": {"series_id": "CUSR0000SACL1E", "label": "Apparel"},
    "Entertainment": {"series_id": "CUSR0000SAS4", "label": "Recreation"},
    "Travel": {"series_id": "CUSR0000SETG01", "label": "Airline fares"},
    "Healthcare": {"series_id": "CUSR0000SAM", "label": "Medical care"},
    "Income": {"series_id": "CUSR0000SA0", "label": "All items"},
    "Other": {"series_id": "CUSR0000SA0", "label": "All items"},
}

SAMPLE_CPI = {
    "CUSR0000SA0": {"label": "All items", "latest": {"period": "2024-08", "value": 3.2}},
    "CUSR0000SAF11": {"label": "Food at home", "latest": {"period": "2024-08", "value": 1.1}},
    "CUSR0000SEFV": {"label": "Food away from home", "latest": {"period": "2024-08", "value": 4.4}},
    "CUSR0000SAH1": {"label": "Shelter", "latest": {"period": "2024-08", "value": 5.6}},
    "CUSR0000SAH2": {"label": "Household energy", "latest": {"period": "2024-08", "value": -2.3}},
    "CUSR0000SETB01": {"label": "Gasoline (all types)", "latest": {"period": "2024-08", "value": 2.1}},
    "CUSR0000SACL1E": {"label": "Apparel", "latest": {"period": "2024-08", "value": 1.9}},
    "CUSR0000SAS4": {"label": "Recreation", "latest": {"period": "2024-08", "value": 3.0}},
    "CUSR0000SETG01": {"label": "Airline fares", "latest": {"period": "2024-08", "value": 6.5}},
    "CUSR0000SAM": {"label": "Medical care", "latest": {"period": "2024-08", "value": 1.0}},
}


def fetch_cpi_snapshot(series_ids: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    """Fetch latest CPI values for the requested BLS series ids with offline fallback."""

    ids = list(series_ids)
    if not ids:
        return {}

    try:
        payload = {"seriesid": ids, "latest": True}
        response = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        results = {}
        for series in data.get("Results", {}).get("series", []):
            series_id = series.get("seriesID")
            entries = series.get("data", [])
            if not entries:
                continue
            latest = entries[0]
            results[series_id] = {
                "label": SAMPLE_CPI.get(series_id, {}).get("label", series_id),
                "latest": {"period": f"{latest.get('year')}-{latest.get('periodName')}", "value": float(latest.get("value", 0))},
            }
        for series_id in ids:
            results.setdefault(series_id, SAMPLE_CPI.get(series_id, SAMPLE_CPI["CUSR0000SA0"]))
        return results
    except Exception:
        return {series_id: SAMPLE_CPI.get(series_id, SAMPLE_CPI["CUSR0000SA0"]) for series_id in ids}


def normalise_transactions(transactions: Iterable[Dict[str, Any]], *, months: int = 1) -> List[Dict[str, Any]]:
    """Return a filtered list of recent debit transactions."""

    cutoff = datetime.utcnow().date() - timedelta(days=30 * max(months, 1))
    clean: List[Dict[str, Any]] = []
    for tx in transactions:
        if (tx.get("transaction_type") or "").lower() == "deposit":
            continue
        amount = float(tx.get("amount") or 0)
        if amount <= 0:
            continue
        try:
            tx_date = datetime.fromisoformat((tx.get("date") or "")).date()
        except Exception:
            continue
        if tx_date < cutoff:
            continue
        clean.append({
            "transaction_id": tx.get("transaction_id") or tx.get("id") or tx.get("name"),
            "name": tx.get("name") or tx.get("merchant_name") or "Unknown",
            "merchant_name": tx.get("merchant_name"),
            "amount": round(amount, 2),
            "date": tx_date.isoformat(),
        })
    return clean


def assign_categories(transactions: List[Dict[str, Any]], overrides: Dict[str, str]) -> List[Dict[str, Any]]:
    """Attach categories to each transaction using overrides and Gemini when required."""

    for tx in transactions:
        override = overrides.get(tx["transaction_id"])
        if override:
            tx["category"] = override
            continue
        description = tx.get("merchant_name") or tx.get("name")
        tx["category"] = categorize_transaction(description)
    return transactions


def compute_spending_breakdown(transactions: List[Dict[str, Any]]) -> Tuple[Dict[str, float], float]:
    totals: Dict[str, float] = defaultdict(float)
    for tx in transactions:
        cat = tx.get("category", "Other")
        totals[cat] += float(tx.get("amount") or 0)
    total_spend = sum(totals.values())
    return {k: round(v, 2) for k, v in totals.items()}, round(total_spend, 2)


def calculate_personal_inflation(transactions: List[Dict[str, Any]], overrides: Dict[str, str]) -> Dict[str, Any]:
    """Compute a personal inflation snapshot for the user."""

    recent = normalise_transactions(transactions)
    if not recent:
        return {
            "personal_rate": None,
            "national_rate": SAMPLE_CPI["CUSR0000SA0"]["latest"]["value"],
            "category_totals": {},
            "category_weights": {},
            "top_drivers": [],
            "cpi_reference": SAMPLE_CPI,
        }

    categorized = assign_categories(recent, overrides)
    totals, total_spend = compute_spending_breakdown(categorized)

    weights = {cat: (amount / total_spend) for cat, amount in totals.items() if total_spend}

    series_ids = [APP_CATEGORY_TO_CPI.get(cat, APP_CATEGORY_TO_CPI["Other"]) ["series_id"] for cat in totals]
    unique_series = list(dict.fromkeys(series_ids))
    cpi_data = fetch_cpi_snapshot(unique_series)

    weighted_rate = 0.0
    for cat, weight in weights.items():
        series_id = APP_CATEGORY_TO_CPI.get(cat, APP_CATEGORY_TO_CPI["Other"])["series_id"]
        series = cpi_data.get(series_id, SAMPLE_CPI.get(series_id, SAMPLE_CPI["CUSR0000SA0"]))
        rate = float(series.get("latest", {}).get("value", 0))
        weighted_rate += weight * rate

    national = SAMPLE_CPI["CUSR0000SA0"]["latest"]["value"]
    top_drivers = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:3]

    return {
        "personal_rate": round(weighted_rate, 2),
        "national_rate": national,
        "category_totals": totals,
        "category_weights": {k: round(v, 3) for k, v in weights.items()},
        "top_drivers": [label for label, _ in top_drivers],
        "cpi_reference": cpi_data,
        "total_spend": total_spend,
        "transactions": categorized,
    }
