"""Gemini powered financial assistant endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request, g

from routes.auth import require_auth
from utils.firestore_db import (
    get_category_overrides,
    get_inflation_snapshot,
    get_user,
    save_inflation_snapshot,
)
from utils.gemini import build_financial_coach_response
from utils.inflation import calculate_personal_inflation
from utils.plaid_client import sync_transactions

bp = Blueprint("assistant", __name__)


@bp.post("/assistant/ask")
@require_auth
def assistant_ask():
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    user, _ = get_user(g.uid, include_sensitive=True)
    if not user:
        return jsonify({"error": "User not found"}), 404

    inflation_snapshot = get_inflation_snapshot(g.uid)
    if not inflation_snapshot:
        access_token = user.get("plaid_access_token")
        if access_token:
            overrides = get_category_overrides(g.uid)
            sync = sync_transactions(access_token, user.get("plaid_cursor"))
            transactions = (sync.get("added") or []) + (sync.get("modified") or [])
            inflation_snapshot = calculate_personal_inflation(transactions, overrides)
            save_inflation_snapshot(g.uid, inflation_snapshot)
        else:
            inflation_snapshot = {}

    context = {
        "user": {
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "email": user.get("email"),
        },
        "personal_inflation": inflation_snapshot,
    }

    answer = build_financial_coach_response(context, question)
    return jsonify({"answer": answer, "context": context})
