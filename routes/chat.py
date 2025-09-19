# routes/chat.py
from flask import Blueprint, request, jsonify, g
import os
import sys
import uuid
import requests
import jwt
from typing import Any, Dict, List, Optional

# Add utils directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.ai_agent import process_financial_query
from utils.firestore_db import (
    create_chat_session,
    get_chat_session,
    update_chat_session,
    add_message_to_session,
    get_user_chat_sessions,
)
from routes.auth import require_auth

bp = Blueprint("chat", __name__)


def _get_authenticated_user_id() -> Optional[str]:
    """Best-effort lookup of the authenticated user id from the session cookie."""
    token = request.cookies.get("session")
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            os.environ.get("FLASK_SECRET", "supersecret_change_me"),
            algorithms=["HS256"],
        )
        return str(payload.get("uid"))
    except Exception:
        return None


def _serialize_timestamp(value: Any) -> Any:
    """Convert Firestore timestamp objects to ISO strings for JSON responses."""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _serialize_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    serialized: List[Dict[str, Any]] = []
    for message in messages or []:
        if not isinstance(message, dict):
            continue
        item = {**message}
        item["timestamp"] = _serialize_timestamp(item.get("timestamp"))
        serialized.append(item)
    return serialized


def _ensure_chat_session(session_id: str, user_id: str, title: Optional[str] = None) -> Dict[str, Any]:
    """Guarantee that a chat session exists for a given user, creating it if missing."""
    session, _ = get_chat_session(session_id)
    if session and session.get("user_id") == user_id:
        return session

    session_title = title or "New Conversation"
    success, message = create_chat_session(
        session_id,
        {
            "user_id": user_id,
            "title": session_title,
            "messages": [],
            "last_message": "",
            "message_count": 0,
        },
    )
    if not success:
        raise RuntimeError(message)
    session, _ = get_chat_session(session_id)
    return session or {}


@bp.post("/chat/sessions")
@require_auth
def create_session():
    """Create a chat session for the authenticated user."""
    data = request.get_json() or {}
    session_id = data.get("session_id") or str(uuid.uuid4())
    title = (data.get("title") or "New Conversation").strip() or "New Conversation"

    messages = data.get("messages") or []
    last_message = ""
    if isinstance(messages, list) and messages:
        last_message = messages[-1].get("content", "")

    success, message = create_chat_session(
        session_id,
        {
            "user_id": str(g.uid),
            "title": title,
            "messages": messages,
            "last_message": last_message,
            "message_count": len(messages),
        },
    )

    if not success:
        return jsonify({"error": message}), 400

    return jsonify({
        "session_id": session_id,
        "title": title,
    }), 201


@bp.get("/chat/sessions")
@require_auth
def list_sessions():
    """Return recent chat sessions for the authenticated user."""
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        limit = 20

    sessions, message = get_user_chat_sessions(str(g.uid), limit)
    if sessions is None:
        return jsonify({"error": message}), 400

    serialized = []
    for session in sessions:
        serialized.append({
            "id": session.get("id"),
            "title": session.get("title") or "Conversation",
            "last_message": session.get("last_message", ""),
            "message_count": session.get("message_count", 0),
            "created_at": _serialize_timestamp(session.get("created_at")),
            "updated_at": _serialize_timestamp(session.get("updated_at")),
        })

    return jsonify({"sessions": serialized})


@bp.get("/chat/sessions/<session_id>")
@require_auth
def fetch_session(session_id: str):
    """Fetch a specific chat session along with messages."""
    session, message = get_chat_session(session_id)
    if not session:
        return jsonify({"error": message or "Session not found"}), 404

    if str(session.get("user_id")) != str(g.uid):
        return jsonify({"error": "Forbidden"}), 403

    return jsonify({
        "id": session_id,
        "title": session.get("title") or "Conversation",
        "last_message": session.get("last_message", ""),
        "message_count": session.get("message_count", 0),
        "created_at": _serialize_timestamp(session.get("created_at")),
        "updated_at": _serialize_timestamp(session.get("updated_at")),
        "messages": _serialize_messages(session.get("messages", [])),
    })


@bp.post("/ask")
@require_auth
def ask():
    """Handle AI chat questions using AI microservice or fallback to local processing"""
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    session_id = data.get("session_id") or None

    if not question:
        return jsonify({"error": "Question is required"}), 400

    authed_user_id = g.uid
    session_data: Optional[Dict[str, Any]] = None

    if session_id:
        try:
            session_data = _ensure_chat_session(session_id, authed_user_id, data.get("title"))
        except Exception as exc:
            return jsonify({"error": f"Failed to prepare session: {exc}"}), 400
    else:
        session_id = str(uuid.uuid4())
        try:
            session_data = _ensure_chat_session(session_id, authed_user_id, data.get("title"))
        except Exception as exc:
            return jsonify({"error": f"Failed to create session: {exc}"}), 400

    conversation_history: List[Dict[str, Any]] = []
    if session_data and isinstance(session_data.get("messages"), list):
        conversation_history = [
            {"role": m.get("role"), "content": m.get("content")}
            for m in session_data.get("messages", [])
            if isinstance(m, dict)
        ]
    elif isinstance(data.get("conversation_history"), list):
        conversation_history = [
            {"role": m.get("role"), "content": m.get("content")}
            for m in data.get("conversation_history")
            if isinstance(m, dict) and m.get("role") and m.get("content")
        ]

    # Now that we have authentication, always save the message
    add_message_to_session(session_id, {"role": "user", "content": question})

    # Try to use AI microservice first if URL is configured
    ai_service_url = os.getenv('AI_SERVICE_URL')

    if ai_service_url:
        try:
            # Call the AI microservice
            response = requests.post(
                f"{ai_service_url}/ask",
                json={"question": question, "session_id": session_id},
                timeout=30,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                ai_response = response.json()
                return jsonify({
                    "title": ai_response.get("title", ""),
                    "summary": ai_response.get("summary", ""),
                    "actionable_steps": ai_response.get("actionable_steps", []),
                    "sources": ai_response.get("sources", []),
                    "provider": "ai-microservice",
                    "session_id": session_id,
                })
            else:
                print(f"AI service returned error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to AI service: {e}")
        except Exception as e:
            print(f"Error calling AI service: {e}")

    # Fallback to local AI processing with advanced agent if available
    try:
        # Extract user context from request
        user_context = data.get("context", {})

        # Process with the advanced AI agent
        response = process_financial_query(
            question,
            user_context=user_context,
            conversation_history=conversation_history,
        )

        response_payload = {
            "title": response.get("title", ""),
            "summary": response.get("summary", ""),
            "actionable_steps": response.get("actionable_steps", []),
            "sources": response.get("sources", []),
            "provider": response.get("provider", "ai-agent"),
            "agent_used": response.get("agent_used", False),
            "priority_level": response.get("priority_level", "medium"),
            "follow_up_questions": response.get("follow_up_questions", []),
            "intent_classification": response.get("intent_classification", {}),
            "session_id": session_id,
        }

        # Now that we have authentication, always save the bot response
        bot_message: Dict[str, Any] = {
            "role": "bot",
            "content": response.get("summary", ""),
        }
        if response.get("sources"):
            bot_message["sources"] = response.get("sources")
        add_message_to_session(session_id, bot_message)

        # Update session metadata
        session_snapshot, _ = get_chat_session(session_id)
        if session_snapshot:
            messages = session_snapshot.get("messages", []) or []
            metadata: Dict[str, Any] = {
                "last_message": response.get("summary", ""),
                "message_count": len(messages),
            }
            existing_title = session_snapshot.get("title")
            if existing_title in (None, "", "New Conversation"):
                metadata["title"] = question[:60]
            update_chat_session(session_id, metadata)

        return jsonify(response_payload)

    except Exception as e:
        # Final fallback to a generic error response
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            "title": "Service Unavailable",
            "summary": "I'm sorry, I'm having trouble processing your request right now. Please try again later or contact Houston/Harris County services directly for assistance.",
            "actionable_steps": [],
            "sources": [],
            "provider": "fallback",
        }), 500
