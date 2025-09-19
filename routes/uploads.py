"""Receipt and document ingestion endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from routes.auth import require_auth
from utils.gemini import analyse_receipt

bp = Blueprint("uploads", __name__)


@bp.post("/uploads/receipt")
@require_auth
def upload_receipt():
    data = request.get_json() or {}
    items = data.get("items") or []
    total = float(data.get("total") or 0)
    if not items:
        return jsonify({"error": "items are required"}), 400

    summary = analyse_receipt(items, total)
    return jsonify({"summary": summary})
