"""Sanity checks for Plaid + Gemini helper fallbacks."""

from utils.plaid_client import create_link_token, sync_transactions
from utils.gemini import categorize_transaction


def test_plaid_link_token_fallback_without_credentials(monkeypatch):
    monkeypatch.delenv("PLAID_CLIENT_ID", raising=False)
    monkeypatch.delenv("PLAID_SECRET", raising=False)

    token = create_link_token("demo-user")
    assert token["link_token"].startswith("mock-link-token")
    assert token.get("mode") == "mock"


def test_sync_transactions_returns_mock_data(monkeypatch):
    monkeypatch.delenv("PLAID_CLIENT_ID", raising=False)
    monkeypatch.delenv("PLAID_SECRET", raising=False)

    result = sync_transactions("mock-access-token")
    assert len(result["added"]) > 0


def test_categorize_transaction_heuristic_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    category = categorize_transaction("HEB #1234")
    assert category == "Groceries"
