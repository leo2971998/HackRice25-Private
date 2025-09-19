"""Gemini powered financial assistant endpoints."""

from __future__ import annotations

import requests
from flask import Blueprint, jsonify, request, g, current_app

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
from routes.inflation import fetch_cpi_data_by_category

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

    # Get economic inflation data to provide current context
    economic_inflation_data = {}
    try:
        economic_inflation_data = fetch_cpi_data_by_category()
    except Exception as e:
        # If we can't get economic data, continue without it
        pass

    context = {
        "user": {
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "email": user.get("email"),
        },
        "personal_inflation": inflation_snapshot,
        "economic_inflation_data": economic_inflation_data,
    }

    answer = build_financial_coach_response(context, question)
    return jsonify({"answer": answer, "context": context})


@bp.post("/assistant/credit-card-recommendation")
@require_auth
def credit_card_recommendation():
    """Generate AI-powered credit card recommendations based on user's spending patterns."""
    
    user, _ = get_user(g.uid, include_sensitive=True)
    if not user:
        return jsonify({"error": "User not found"}), 404

    access_token = user.get("plaid_access_token")
    if not access_token:
        return jsonify({"error": "Plaid account not linked. Connect your bank account to get personalized recommendations."}), 400

    # Get user's transactions to analyze spending patterns
    overrides = get_category_overrides(g.uid)
    sync = sync_transactions(access_token, user.get("plaid_cursor"))
    transactions = (sync.get("added") or []) + (sync.get("modified") or [])
    
    if not transactions:
        return jsonify({"error": "No transaction data available for recommendations."}), 400

    # Analyze spending categories
    spending_by_category = {}
    total_spending = 0
    
    for tx in transactions:
        amount = float(tx.get("amount", 0))
        if amount > 0:  # Only count spending, not income
            category = tx.get("category", "Other")
            spending_by_category[category] = spending_by_category.get(category, 0) + amount
            total_spending += amount
    
    if total_spending == 0:
        return jsonify({"error": "No spending data available for recommendations."}), 400

    # Find top spending categories
    top_categories = sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Get economic inflation data for context
    economic_inflation_data = {}
    try:
        economic_inflation_data = fetch_cpi_data_by_category()
    except Exception:
        pass

    # Build context for AI recommendation
    context = {
        "user": {
            "first_name": user.get("first_name"),
            "spending_analysis": {
                "total_monthly_spending": total_spending,
                "top_categories": [{"category": cat, "amount": amt, "percentage": (amt/total_spending)*100} 
                                for cat, amt in top_categories],
                "spending_breakdown": spending_by_category
            }
        },
        "economic_inflation_data": economic_inflation_data,
    }

    # Create AI prompt specifically for credit card recommendations
    recommendation_prompt = f"""Based on the user's spending patterns, recommend the best credit card for them. 
    Their top spending categories are: {', '.join([cat for cat, _ in top_categories])}.
    Total monthly spending: ${total_spending:.2f}.
    
    Provide a specific credit card recommendation with:
    1. Card name and issuer
    2. Why it's good for their spending pattern
    3. Key rewards/benefits
    4. Approximate value they could earn
    
    Keep the response concise and actionable."""

    answer = build_financial_coach_response(context, recommendation_prompt)
    
    return jsonify({
        "recommendation": answer, 
        "spending_analysis": context["user"]["spending_analysis"],
        "context": context
    })
