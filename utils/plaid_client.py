"""Helpers for interacting with Plaid's API with graceful sandbox fallbacks."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

MOCK_TRANSACTIONS = [
    {
        "transaction_id": "mock-1",
        "name": "H-E-B #443",
        "merchant_name": "H-E-B",
        "amount": 86.23,
        "date": (datetime.utcnow() - timedelta(days=3)).date().isoformat(),
    },
    {
        "transaction_id": "mock-2",
        "name": "Shell Oil 23891",
        "merchant_name": "Shell",
        "amount": 42.18,
        "date": (datetime.utcnow() - timedelta(days=4)).date().isoformat(),
    },
    {
        "transaction_id": "mock-3",
        "name": "Netflix",
        "merchant_name": "Netflix",
        "amount": 15.99,
        "date": (datetime.utcnow() - timedelta(days=6)).date().isoformat(),
    },
    {
        "transaction_id": "mock-4",
        "name": "United Airlines",
        "merchant_name": "United",
        "amount": 302.47,
        "date": (datetime.utcnow() - timedelta(days=15)).date().isoformat(),
    },
]


class PlaidUnavailable(Exception):
    """Raised when Plaid credentials are missing or the SDK cannot be initialised."""


def _build_client():
    """Return an instantiated Plaid client or ``None`` when credentials are absent."""

    client_id = os.getenv("PLAID_CLIENT_ID")
    secret = os.getenv("PLAID_SECRET")
    if not client_id or not secret:
        return None

    try:
        from plaid import ApiClient, Configuration, Environment
        from plaid.api import plaid_api
    except Exception as exc:  # pragma: no cover - Plaid SDK import guard
        print(f"Plaid SDK unavailable: {exc}")
        return None

    env_name = (os.getenv("PLAID_ENV", "sandbox") or "sandbox").lower()
    environment = {
        "production": Environment.Production,
        "development": Environment.Development,
    }.get(env_name, Environment.Sandbox)

    config = Configuration(
        host=environment.value,
        api_key={
            "clientId": client_id,
            "secret": secret,
        },
    )

    api_client = ApiClient(config)
    return plaid_api.PlaidApi(api_client)


def create_link_token(user_id: str) -> Dict[str, Any]:
    """Create a Plaid Link token for the given user or return mock data."""

    client = _build_client()
    if not client:
        return {
            "link_token": f"mock-link-token-{uuid.uuid4()}",
            "expiration": None,
            "mode": "mock",
        }

    try:
        from plaid.model.link_token_create_request import LinkTokenCreateRequest
        from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
        from plaid.model.products import Products
        from plaid.model.country_code import CountryCode
    except Exception as exc:  # pragma: no cover - Plaid model import guard
        print(f"Plaid model import failed: {exc}")
        return {
            "link_token": f"mock-link-token-{uuid.uuid4()}",
            "expiration": None,
            "mode": "mock",
        }

    request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(client_user_id=user_id),
        client_name="Inflate-Wise",
        products=[Products("transactions")],
        language="en",
        country_codes=[CountryCode("US")],
    )

    response = client.link_token_create(request)
    return response.to_dict()


def exchange_public_token(public_token: str) -> Dict[str, Any]:
    """Exchange a Plaid public token for an access token or provide mock data."""

    client = _build_client()
    if not client:
        return {
            "access_token": f"mock-access-token-{uuid.uuid4()}",
            "item_id": f"mock-item-{uuid.uuid4()}",
        }

    try:
        from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    except Exception as exc:  # pragma: no cover
        print(f"Plaid model import failed: {exc}")
        return {
            "access_token": f"mock-access-token-{uuid.uuid4()}",
            "item_id": f"mock-item-{uuid.uuid4()}",
        }

    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = client.item_public_token_exchange(request)
    return response.to_dict()


def sync_transactions(access_token: str, cursor: Optional[str] = None) -> Dict[str, Any]:
    """Sync the latest transactions from Plaid.

    When the Plaid client is unavailable a high fidelity mock payload is returned
    to keep the product demoable offline.
    """

    client = _build_client()
    if not client:
        return {
            "added": MOCK_TRANSACTIONS,
            "modified": [],
            "removed": [],
            "next_cursor": None,
            "has_more": False,
        }

    try:
        from plaid.model.transactions_sync_request import TransactionsSyncRequest
    except Exception as exc:  # pragma: no cover
        print(f"Plaid model import failed: {exc}")
        return {
            "added": MOCK_TRANSACTIONS,
            "modified": [],
            "removed": [],
            "next_cursor": cursor,
            "has_more": False,
        }

    request = TransactionsSyncRequest(access_token=access_token, cursor=cursor)
    response = client.transactions_sync(request)
    return response.to_dict()


def get_account_balances(access_token: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Return account balance information for the linked item."""

    client = _build_client()
    if not client:
        return {
            "accounts": [
                {
                    "name": "Plaid Checking",
                    "type": "depository",
                    "subtype": "checking",
                    "mask": "0000",
                    "balances": {"available": 2450.32, "current": 2450.32},
                },
                {
                    "name": "Plaid Credit Card",
                    "type": "credit",
                    "subtype": "credit card",
                    "mask": "1234",
                    "balances": {"available": 1800.00, "current": 1204.18},
                },
            ]
        }, None

    try:
        from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
    except Exception as exc:  # pragma: no cover
        return None, f"Plaid model import failed: {exc}"

    request = AccountsBalanceGetRequest(access_token=access_token)
    try:
        response = client.accounts_balance_get(request)
        return response.to_dict(), None
    except Exception as exc:  # pragma: no cover - surfaces Plaid API issues
        return None, str(exc)
