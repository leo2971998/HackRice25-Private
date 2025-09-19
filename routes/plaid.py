"""Plaid integration endpoints supporting link token creation and token exchange."""

from __future__ import annotations

from flask import Blueprint, jsonify, request, g

from routes.auth import require_auth
from utils.firestore_db import (
    clear_plaid_credentials,
    get_user,
    save_plaid_credentials,
    save_plaid_cursor,
)
from utils.plaid_client import (
    create_link_token,
    exchange_public_token,
    get_account_balances,
)

bp = Blueprint("plaid", __name__)


@bp.get("/plaid/status")
@require_auth
def plaid_status():
    user, _ = get_user(g.uid, include_sensitive=True)
    if not user:
        return jsonify({"linked": False})

    access_token = user.get("plaid_access_token")
    item_id = user.get("plaid_item_id")
    institution = user.get("plaid_institution")

    if not access_token or not item_id:
        return jsonify({"linked": False})

    balances, error = get_account_balances(access_token)
    payload = {
        "linked": True,
        "item_id": item_id,
        "institution": institution,
        "balances": balances,
    }
    if error:
        payload["warning"] = error
    return jsonify(payload)


@bp.post("/plaid/link-token")
@require_auth
def plaid_link_token():
    token = create_link_token(str(g.uid))
    return jsonify(token)


@bp.post("/plaid/exchange")
@require_auth
def plaid_exchange():
    data = request.get_json() or {}
    public_token = data.get("public_token")
    institution = data.get("institution")

    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    exchange = exchange_public_token(public_token)
    access_token = exchange.get("access_token")
    item_id = exchange.get("item_id")

    if not access_token or not item_id:
        return jsonify({"error": "Failed to exchange public token"}), 400

    success, message = save_plaid_credentials(
        g.uid,
        access_token=access_token,
        item_id=item_id,
        institution=institution,
    )
    if not success:
        return jsonify({"error": message}), 500

    save_plaid_cursor(g.uid, None)
    balances, _ = get_account_balances(access_token)

    return jsonify({
        "ok": True,
        "item_id": item_id,
        "balances": balances,
        "mode": "mock" if str(access_token).startswith("mock-") else "live",
    })


@bp.delete("/plaid/link")
@require_auth
def unlink_plaid():
    success, message = clear_plaid_credentials(g.uid)
    if not success:
        return jsonify({"error": message}), 500
    return jsonify({"ok": True})
