"""Utility helpers for interacting with Google Cloud Firestore."""

from __future__ import annotations

import hashlib
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from google.cloud import firestore
from google.cloud.firestore import Client

SENSITIVE_FIELDS = {"password_hash", "plaid_access_token"}


def get_firestore_client() -> Optional[Client]:
    """Return an initialized Firestore client if configuration is available."""

    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0536110235")
        return firestore.Client(project=project_id)
    except Exception as exc:  # pragma: no cover - defensive for local dev without credentials
        print(f"Warning: Could not initialize Firestore client: {exc}")
        return None


def _user_doc_id(email: str) -> str:
    """Derive a stable Firestore document ID from an email address."""

    normalized = (email or "").strip().lower().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()


def _sanitize_user_document(data: Dict[str, Any], *, doc_id: Optional[str] = None) -> Dict[str, Any]:
    """Normalize Firestore user documents for API responses."""

    result = dict(data)
    if doc_id:
        result.setdefault("id", doc_id)

    for field in SENSITIVE_FIELDS:
        result.pop(field, None)

    created_at = result.get("created_at")
    if hasattr(created_at, "timestamp"):
        result["created_at"] = int(created_at.timestamp())

    if not result.get("role"):
        result["role"] = "user"

    result.setdefault("plaid_linked_at", None)
    result.setdefault("plaid_item_id", None)
    result.setdefault("plaid_institution", None)
    result.setdefault("category_overrides", {})
    result.setdefault("plaid_cursor", None)

    return result


def create_user(email: str, user_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Create a new user document.

    Returns a tuple of (success flag, user_id or error message).
    """

    db = get_firestore_client()
    if not db:
        return False, "Firestore not available"

    doc_id = _user_doc_id(email)
    try:
        user_ref = db.collection("users").document(doc_id)
        if user_ref.get().exists:
            return False, "email already registered"

        payload = dict(user_data)
        payload.setdefault("email", email)
        payload.setdefault("created_at", int(time.time()))
        payload.setdefault("role", "user")
        payload.setdefault("category_overrides", {})
        payload.setdefault("plaid_linked_at", None)
        payload.setdefault("plaid_item_id", None)
        payload.setdefault("plaid_institution", None)
        payload.setdefault("plaid_cursor", None)
        user_ref.set(payload)
        return True, doc_id
    except Exception as exc:  # pragma: no cover - surface useful error info
        return False, f"Failed to create user: {exc}"


def get_user(user_id: str, *, include_sensitive: bool = False) -> Tuple[Optional[Dict[str, Any]], str]:
    """Fetch a user document by ID."""

    db = get_firestore_client()
    if not db:
        return None, "Firestore not available"

    try:
        doc = db.collection("users").document(user_id).get()
        if not doc.exists:
            return None, "User not found"
        data = doc.to_dict() or {}
        if include_sensitive:
            result = dict(data)
            result.setdefault("id", doc.id)
            return result, "User found"
        return _sanitize_user_document(data, doc_id=doc.id), "User found"
    except Exception as exc:  # pragma: no cover
        return None, f"Failed to get user: {exc}"


def get_user_by_email(email: str, *, include_sensitive: bool = False) -> Tuple[Optional[Dict[str, Any]], str]:
    """Fetch a user document by email address."""

    db = get_firestore_client()
    if not db:
        return None, "Firestore not available"

    doc_id = _user_doc_id(email)
    try:
        doc = db.collection("users").document(doc_id).get()
        if not doc.exists:
            return None, "User not found"
        data = doc.to_dict() or {}
        if include_sensitive:
            result = dict(data)
            result.setdefault("id", doc.id)
            return result, "User found"
        return _sanitize_user_document(data, doc_id=doc.id), "User found"
    except Exception as exc:  # pragma: no cover
        return None, f"Failed to get user: {exc}"


def list_user_documents() -> Tuple[List[Dict[str, Any]], str]:
    """Return all user documents."""

    db = get_firestore_client()
    if not db:
        return [], "Firestore not available"

    try:
        docs = db.collection("users").stream()
        users: List[Dict[str, Any]] = []
        for doc in docs:
            users.append(_sanitize_user_document(doc.to_dict() or {}, doc_id=doc.id))
        users.sort(key=lambda item: item.get("created_at", 0), reverse=True)
        return users, "Users listed"
    except Exception as exc:  # pragma: no cover
        return [], f"Failed to list users: {exc}"


def update_user(user_id: str, user_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Update a user document."""

    db = get_firestore_client()
    if not db:
        return False, "Firestore not available"

    try:
        user_ref = db.collection("users").document(user_id)
        if not user_ref.get().exists:
            return False, "User not found"
        user_ref.update(user_data)
        return True, "User updated successfully"
    except Exception as exc:  # pragma: no cover
        return False, f"Failed to update user: {exc}"


def delete_user(user_id: str) -> Tuple[bool, str]:
    """Delete a user document."""

    db = get_firestore_client()
    if not db:
        return False, "Firestore not available"

    try:
        user_ref = db.collection("users").document(user_id)
        if not user_ref.get().exists:
            return False, "User not found"
        user_ref.delete()
        return True, "User deleted successfully"
    except Exception as exc:  # pragma: no cover
        return False, f"Failed to delete user: {exc}"


# --- Plaid credential helpers -------------------------------------------------

def save_plaid_credentials(user_id: str, *, access_token: str, item_id: str, institution: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    """Persist Plaid credentials for a user."""

    payload: Dict[str, Any] = {
        "plaid_access_token": access_token,
        "plaid_item_id": item_id,
        "plaid_linked_at": int(time.time()),
    }
    if institution:
        payload["plaid_institution"] = institution
    return update_user(user_id, payload)


def clear_plaid_credentials(user_id: str) -> Tuple[bool, str]:
    """Remove Plaid credentials when a user unlinks their accounts."""

    payload = {
        "plaid_access_token": firestore.DELETE_FIELD,
        "plaid_item_id": firestore.DELETE_FIELD,
        "plaid_linked_at": None,
        "plaid_institution": None,
        "plaid_cursor": None,
    }
    return update_user(user_id, payload)


def save_plaid_cursor(user_id: str, cursor: Optional[str]) -> Tuple[bool, str]:
    """Persist the last Plaid transactions cursor."""

    return update_user(user_id, {"plaid_cursor": cursor})


# --- Category overrides -------------------------------------------------------

def get_category_overrides(user_id: str) -> Dict[str, str]:
    """Return stored category overrides keyed by Plaid transaction id."""

    user, _ = get_user(user_id, include_sensitive=True)
    if not user:
        return {}
    return dict(user.get("category_overrides") or {})


def set_category_override(user_id: str, transaction_id: str, category: str) -> Tuple[bool, str]:
    """Persist a user's preferred category override for a transaction."""

    overrides = get_category_overrides(user_id)
    overrides[transaction_id] = category
    return update_user(user_id, {"category_overrides": overrides})


# --- Personal insights cache --------------------------------------------------

def save_inflation_snapshot(user_id: str, snapshot: Dict[str, Any]) -> Tuple[bool, str]:
    """Persist the latest personal inflation snapshot for fast retrieval."""

    return update_user(user_id, {"last_inflation_snapshot": snapshot, "last_inflation_computed_at": int(time.time())})


def get_inflation_snapshot(user_id: str) -> Dict[str, Any]:
    """Fetch the cached personal inflation snapshot if available."""

    user, _ = get_user(user_id, include_sensitive=True)
    if not user:
        return {}
    return dict(user.get("last_inflation_snapshot") or {})
