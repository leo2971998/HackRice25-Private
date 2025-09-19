"""Endpoints delivering personal inflation insights."""

from __future__ import annotations

from flask import Blueprint, jsonify, request, g

from routes.auth import require_auth
from utils.firestore_db import (
    get_category_overrides,
    get_inflation_snapshot,
    get_user,
    save_inflation_snapshot,
)
from utils.inflation import calculate_personal_inflation
from utils.plaid_client import sync_transactions

bp = Blueprint("inflation", __name__)


@bp.get("/inflation/personal")
@require_auth
def personal_inflation():
    force_refresh = request.args.get("refresh") == "true"
    if not force_refresh:
        cached = get_inflation_snapshot(g.uid)
        if cached:
            return jsonify({"personal_inflation": cached})

    user, _ = get_user(g.uid, include_sensitive=True)
    if not user:
        return jsonify({"error": "User not found"}), 404

    access_token = user.get("plaid_access_token")
    if not access_token:
        return jsonify({"error": "Plaid account not linked"}), 400

    overrides = get_category_overrides(g.uid)
    sync = sync_transactions(access_token, user.get("plaid_cursor"))
    transactions = (sync.get("added") or []) + (sync.get("modified") or [])
    summary = calculate_personal_inflation(transactions, overrides)
    save_inflation_snapshot(g.uid, summary)
    return jsonify({"personal_inflation": summary})
