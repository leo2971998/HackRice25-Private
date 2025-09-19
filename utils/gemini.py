"""Gemini helper utilities for categorisation and personalised coaching."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict, Iterable, Optional

import google.generativeai as genai

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro-latest")

CATEGORY_PROMPT = """You are an expert financial analyst categorising spending into macro economic buckets.\\n\\n"""

CATEGORY_OPTIONS = [
    "Groceries",
    "Gasoline",
    "Restaurants",
    "Utilities",
    "Housing",
    "Shopping",
    "Entertainment",
    "Travel",
    "Healthcare",
    "Income",
    "Other",
]


@lru_cache(maxsize=1)
def _get_model() -> Optional[genai.GenerativeModel]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(DEFAULT_MODEL)


def categorize_transaction(description: str) -> str:
    """Use Gemini to map a raw description to a spending category.

    Falls back to lightweight heuristics when the API key is missing.
    """

    description = (description or "").strip()
    if not description:
        return "Other"

    model = _get_model()
    if not model:
        lower = description.lower()
        normalized = lower.replace("-", " ").replace("*", " ")
        condensed = normalized.replace(" ", "")
        if any(keyword in normalized or keyword in condensed for keyword in ["heb", "grocery", "kroger", "market"]):
            return "Groceries"
        if any(keyword in normalized for keyword in ["shell", "exxon", "chevron", "gas", "fuel"]):
            return "Gasoline"
        if any(keyword in normalized for keyword in ["uber", "lyft", "airlines", "hotel", "travel", "united", "delta", "southwest"]):
            return "Travel"
        if any(keyword in normalized for keyword in ["netflix", "hulu", "spotify", "movie"]):
            return "Entertainment"
        if any(keyword in normalized for keyword in ["energy", "electric", "water", "utility"]):
            return "Utilities"
        if any(keyword in normalized for keyword in ["rent", "mortgage", "apartment"]):
            return "Housing"
        if any(keyword in normalized for keyword in ["clinic", "pharmacy", "health"]):
            return "Healthcare"
        if any(keyword in normalized for keyword in ["restaurant", "cafe", "coffee", "bar", "dining"]):
            return "Restaurants"
        if any(keyword in normalized for keyword in ["amazon", "target", "mall", "store"]):
            return "Shopping"
        return "Other"

    prompt = CATEGORY_PROMPT + "Valid categories: " + ", ".join(CATEGORY_OPTIONS) + "\\nReturn only the category name."\
        + f"\\nTransaction description: {description}"

    try:
        response = model.generate_content(prompt)
        if response and response.text:
            text = response.text.strip()
            for option in CATEGORY_OPTIONS:
                if option.lower() in text.lower():
                    return option
    except Exception as exc:  # pragma: no cover - surfaces Gemini API issues
        print(f"Gemini categorisation failed: {exc}")

    return "Other"


def categorize_transactions(transactions: Iterable[Dict[str, Any]]) -> list[Dict[str, Any]]:
    """Categorize a list of transactions using Gemini AI.
    
    Returns the transactions with an added 'ai_category' field.
    """
    categorized = []
    for transaction in transactions:
        # Make a copy to avoid modifying the original
        categorized_transaction = dict(transaction)
        
        # Get the transaction description/name
        description = transaction.get("name") or transaction.get("description") or ""
        
        # Categorize the transaction
        category = categorize_transaction(description)
        categorized_transaction["ai_category"] = category
        
        categorized.append(categorized_transaction)
    
    return categorized


def build_financial_coach_response(context: Dict[str, Any], question: str) -> str:
    """Craft a personalised coaching response using Gemini."""

    model = _get_model()
    if not model:
        # Offline fallback emphasising the data provided.
        inflation = context.get("personal_inflation", {})
        rate = inflation.get("personal_rate")
        top_drivers = inflation.get("top_drivers", [])
        lines = [
            "Inflate-Wise summary:",
            f"• Personal inflation rate: {rate}%" if rate is not None else "• Personal inflation rate is being calculated.",
        ]
        if top_drivers:
            lines.append("• Top contributors: " + ", ".join(top_drivers))
        return "\n".join(lines)

    prompt = (
        "You are Inflate-Wise, an empathetic personal finance coach. Use the provided data to answer the user question."
        " Provide concrete guidance grounded in the numbers."
    )

    try:
        structured_context = genai.protos.Content(parts=[genai.protos.Part(text=str(context))])
        response = model.generate_content([
            genai.protos.Content(parts=[genai.protos.Part(text=prompt)], role="system"),
            structured_context,
            genai.protos.Content(parts=[genai.protos.Part(text=question)], role="user"),
        ])
        if response and response.text:
            return response.text.strip()
    except Exception as exc:  # pragma: no cover
        print(f"Gemini coaching failed: {exc}")

    return "I'm still crunching the numbers, but focus on your highest spending categories this month."


def analyse_receipt(items: Iterable[str], total: float) -> str:
    """Generate a narrative around a scanned receipt."""

    model = _get_model()
    summary = "Consider categorising recurring purchases so Inflate-Wise can personalise inflation tracking."
    if not model:
        return summary

    prompt = (
        "Summarise this receipt in a friendly tone and suggest how it affects the user's inflation categories. Items: "
        + ", ".join(items)
        + f". Total: ${total:.2f}."
    )
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
    except Exception as exc:  # pragma: no cover
        print(f"Gemini receipt summary failed: {exc}")
    return summary
