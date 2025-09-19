"""Authentication routes backed by Firestore."""

import os
import time
from typing import Callable

import jwt
from flask import Blueprint, g, jsonify, make_response, request
from werkzeug.security import check_password_hash, generate_password_hash

from utils.firestore_db import (
    create_user as firestore_create_user,
    delete_user as firestore_delete_user,
    get_user as firestore_get_user,
    get_user_by_email,
    list_user_documents,
    update_user as firestore_update_user,
)


bp = Blueprint("auth", __name__)


def issue_token(user_id: str) -> str:
    payload = {"uid": user_id, "iat": int(time.time())}
    token = jwt.encode(payload, os.environ.get("FLASK_SECRET", "supersecret_change_me"), algorithm="HS256")
    return token


def require_auth(fn: Callable):
    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("session")
        if not token:
            return jsonify(error="unauthorized"), 401
        try:
            payload = jwt.decode(token, os.environ.get("FLASK_SECRET", "supersecret_change_me"), algorithms=["HS256"])
            g.uid = payload["uid"]
        except Exception:
            return jsonify(error="unauthorized"), 401
        return fn(*args, **kwargs)

    return wrapper


def require_admin(fn: Callable):
    """Decorator to require admin role for endpoint access."""

    from functools import wraps

    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("session")
        if not token:
            return jsonify(error="unauthorized"), 401
        try:
            payload = jwt.decode(token, os.environ.get("FLASK_SECRET", "supersecret_change_me"), algorithms=["HS256"])
            g.uid = payload["uid"]

            user, _ = firestore_get_user(g.uid)
            if not user:
                return jsonify(error="user not found"), 401

            if (user.get("role") or "user").lower() != "admin":
                return jsonify(error="admin access required"), 403

        except Exception:
            return jsonify(error="unauthorized"), 401
        return fn(*args, **kwargs)

    return wrapper


@bp.post("/auth/register")
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    pw = data.get("password") or ""
    first = data.get("first_name") or ""
    last = data.get("last_name") or ""
    requested_role = (data.get("role") or "user").strip().lower()

    if requested_role == "admin":
        return jsonify(error="Admin accounts must be created by an existing administrator."), 403

    if not email or not pw:
        return jsonify(error="email and password required"), 400

    payload = {
        "password_hash": generate_password_hash(pw),
        "first_name": first,
        "last_name": last,
        "role": "user",
    }

    success, result = firestore_create_user(email, payload)
    if not success:
        status = 409 if "already registered" in result.lower() else 500
        return jsonify(error=result), status

    uid = result
    resp = make_response(jsonify(ok=True, message="Account created successfully"))
    resp.set_cookie("session", issue_token(uid), httponly=True, samesite="Lax")
    return resp


@bp.post("/auth/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    pw = data.get("password") or ""

    user, _ = get_user_by_email(email)
    if not user or not check_password_hash(user.get("password_hash", ""), pw):
        return jsonify(error="invalid credentials"), 401

    user_role = (user.get("role") or "user").lower()

    resp = make_response(jsonify(ok=True, role=user_role))
    resp.set_cookie("session", issue_token(user["id"]), httponly=True, samesite="Lax")
    return resp


@bp.post("/auth/logout")
@require_auth
def logout():
    resp = make_response(jsonify(ok=True))
    resp.delete_cookie("session")
    return resp


@bp.get("/me")
@require_auth
def me():
    user, _ = firestore_get_user(g.uid)
    if not user:
        return jsonify(error="user not found"), 404
    return jsonify(user)


@bp.get("/auth/users")
@require_admin
def list_users():
    users, message = list_user_documents()
    if message == "Firestore not available":
        return jsonify(error=message), 500
    return jsonify(users)


@bp.patch("/auth/users/<user_id>")
@require_admin
def update_user(user_id: str):
    payload = request.get_json() or {}
    new_role = (payload.get("role") or "user").strip().lower()
    if new_role not in {"user", "admin"}:
        return jsonify(error="Role must be 'user' or 'admin'."), 400

    user, _ = firestore_get_user(user_id)
    if not user:
        return jsonify(error="User not found."), 404

    current_role = (user.get("role") or "user").lower()
    if current_role == "admin" and new_role != "admin":
        users, _ = list_user_documents()
        remaining_admins = [u for u in users if (u.get("role") or "user") == "admin" and u.get("id") != user_id]
        if len(remaining_admins) == 0:
            return jsonify(error="Cannot remove the last administrator."), 400

    success, message = firestore_update_user(user_id, {"role": new_role})
    if not success:
        status = 404 if "not found" in message.lower() else 500
        return jsonify(error=message), status
    return jsonify(ok=True)


@bp.delete("/auth/users/<user_id>")
@require_admin
def delete_user(user_id: str):
    if user_id == getattr(g, "uid", None):
        return jsonify(error="Administrators cannot delete their own account."), 400

    user, _ = firestore_get_user(user_id)
    if not user:
        return jsonify(error="User not found."), 404

    existing_role = (user.get("role") or "user").lower()
    if existing_role == "admin":
        users, _ = list_user_documents()
        remaining_admins = [u for u in users if (u.get("role") or "user") == "admin" and u.get("id") != user_id]
        if len(remaining_admins) == 0:
            return jsonify(error="Cannot remove the last administrator."), 400

    success, message = firestore_delete_user(user_id)
    if not success:
        status = 404 if "not found" in message.lower() else 500
        return jsonify(error=message), status
    return jsonify(ok=True)
