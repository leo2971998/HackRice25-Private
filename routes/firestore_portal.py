# routes/firestore_portal.py
"""
Firestore Portal Routes for TrustAgent
Provides CRUD operations and data management interface for all Firestore collections
"""

from flask import Blueprint, request, jsonify, g
from .auth import require_auth
from utils.firestore_db import (
    # User operations
    create_user, get_user, update_user, delete_user,
    # Chat session operations  
    create_chat_session, get_chat_session, update_chat_session, delete_chat_session,
    add_message_to_session, get_user_chat_sessions,
    # AP2 transaction operations
    create_ap2_transaction, get_ap2_transaction, update_ap2_transaction, delete_ap2_transaction,
    get_user_ap2_transactions,
    # Agent state operations
    create_agent_state, get_agent_state, update_agent_state, delete_agent_state,
    get_user_agent_states,
    # Utility operations
    get_collection_stats, cleanup_expired_data
)

bp = Blueprint("firestore_portal", __name__)

@bp.get("/api/portal/health")
def portal_health():
    """Health check for Firestore portal"""
    return jsonify({
        "status": "ok",
        "service": "Firestore Portal",
        "version": "1.0.0",
        "collections": ["users", "chat_sessions", "ap2_transactions", "agent_state"]
    })

@bp.get("/api/portal/stats")
@require_auth
def get_portal_stats():
    """Get comprehensive statistics about all collections"""
    try:
        stats, message = get_collection_stats()
        
        return jsonify({
            "success": True,
            "stats": stats,
            "message": message,
            "user_id": g.uid
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get portal stats: {str(e)}"}), 500

# User Management Portal
@bp.post("/api/portal/users")
@require_auth
def portal_create_user():
    """Create a new user via portal"""
    try:
        data = request.get_json() or {}
        user_id = data.get("user_id") or g.uid
        
        # Remove user_id from data to avoid duplication
        user_data = {k: v for k, v in data.items() if k != "user_id"}
        
        success, message = create_user(user_id, user_data)
        
        return jsonify({
            "success": success,
            "message": message,
            "user_id": user_id
        }), 201 if success else 400
        
    except Exception as e:
        return jsonify({"error": f"Failed to create user: {str(e)}"}), 500

@bp.get("/api/portal/users/<user_id>")
@require_auth
def portal_get_user(user_id):
    """Get user data via portal"""
    try:
        user_data, message = get_user(user_id)
        
        return jsonify({
            "success": user_data is not None,
            "user": user_data,
            "message": message
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get user: {str(e)}"}), 500

@bp.put("/api/portal/users/<user_id>")
@require_auth
def portal_update_user(user_id):
    """Update user data via portal"""
    try:
        data = request.get_json() or {}
        
        success, message = update_user(user_id, data)
        
        return jsonify({
            "success": success,
            "message": message,
            "user_id": user_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500

@bp.delete("/api/portal/users/<user_id>")
@require_auth
def portal_delete_user(user_id):
    """Delete user data via portal"""
    try:
        success, message = delete_user(user_id)
        
        return jsonify({
            "success": success,
            "message": message,
            "user_id": user_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete user: {str(e)}"}), 500

# Chat Session Management Portal
@bp.post("/api/portal/chat_sessions")
@require_auth
def portal_create_chat_session():
    """Create a new chat session via portal"""
    try:
        data = request.get_json() or {}
        session_id = data.get("session_id", f"session_{g.uid}_{int(__import__('time').time())}")
        
        # Remove session_id from data to avoid duplication
        session_data = {k: v for k, v in data.items() if k != "session_id"}
        session_data["user_id"] = g.uid  # Ensure user association
        
        success, message = create_chat_session(session_id, session_data)
        
        return jsonify({
            "success": success,
            "message": message,
            "session_id": session_id
        }), 201 if success else 400
        
    except Exception as e:
        return jsonify({"error": f"Failed to create chat session: {str(e)}"}), 500

@bp.get("/api/portal/chat_sessions/<session_id>")
@require_auth
def portal_get_chat_session(session_id):
    """Get chat session data via portal"""
    try:
        session_data, message = get_chat_session(session_id)
        
        return jsonify({
            "success": session_data is not None,
            "session": session_data,
            "message": message
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get chat session: {str(e)}"}), 500

@bp.get("/api/portal/chat_sessions")
@require_auth
def portal_get_user_chat_sessions():
    """Get all chat sessions for current user via portal"""
    try:
        limit = int(request.args.get("limit", 10))
        sessions, message = get_user_chat_sessions(g.uid, limit)
        
        return jsonify({
            "success": True,
            "sessions": sessions,
            "count": len(sessions),
            "message": message
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get chat sessions: {str(e)}"}), 500

@bp.post("/api/portal/chat_sessions/<session_id>/messages")
@require_auth
def portal_add_message(session_id):
    """Add message to chat session via portal"""
    try:
        data = request.get_json() or {}
        
        success, message = add_message_to_session(session_id, data)
        
        return jsonify({
            "success": success,
            "message": message,
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to add message: {str(e)}"}), 500

@bp.delete("/api/portal/chat_sessions/<session_id>")
@require_auth
def portal_delete_chat_session(session_id):
    """Delete chat session via portal"""
    try:
        success, message = delete_chat_session(session_id)
        
        return jsonify({
            "success": success,
            "message": message,
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete chat session: {str(e)}"}), 500

# AP2 Transaction Management Portal
@bp.post("/api/portal/ap2_transactions")
@require_auth
def portal_create_ap2_transaction():
    """Create a new AP2 transaction via portal"""
    try:
        data = request.get_json() or {}
        transaction_id = data.get("transaction_id", f"tx_{g.uid}_{int(__import__('time').time())}")
        
        # Remove transaction_id from data to avoid duplication
        transaction_data = {k: v for k, v in data.items() if k != "transaction_id"}
        transaction_data["user_id"] = g.uid  # Ensure user association
        
        success, message = create_ap2_transaction(transaction_id, transaction_data)
        
        return jsonify({
            "success": success,
            "message": message,
            "transaction_id": transaction_id
        }), 201 if success else 400
        
    except Exception as e:
        return jsonify({"error": f"Failed to create AP2 transaction: {str(e)}"}), 500

@bp.get("/api/portal/ap2_transactions/<transaction_id>")
@require_auth
def portal_get_ap2_transaction(transaction_id):
    """Get AP2 transaction data via portal"""
    try:
        transaction_data, message = get_ap2_transaction(transaction_id)
        
        return jsonify({
            "success": transaction_data is not None,
            "transaction": transaction_data,
            "message": message
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get AP2 transaction: {str(e)}"}), 500

@bp.get("/api/portal/ap2_transactions")
@require_auth
def portal_get_user_ap2_transactions():
    """Get all AP2 transactions for current user via portal"""
    try:
        status = request.args.get("status")
        limit = int(request.args.get("limit", 50))
        
        transactions, message = get_user_ap2_transactions(g.uid, status, limit)
        
        return jsonify({
            "success": True,
            "transactions": transactions,
            "count": len(transactions),
            "message": message
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get AP2 transactions: {str(e)}"}), 500

@bp.put("/api/portal/ap2_transactions/<transaction_id>")
@require_auth
def portal_update_ap2_transaction(transaction_id):
    """Update AP2 transaction data via portal"""
    try:
        data = request.get_json() or {}
        
        success, message = update_ap2_transaction(transaction_id, data)
        
        return jsonify({
            "success": success,
            "message": message,
            "transaction_id": transaction_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to update AP2 transaction: {str(e)}"}), 500

@bp.delete("/api/portal/ap2_transactions/<transaction_id>")
@require_auth
def portal_delete_ap2_transaction(transaction_id):
    """Delete AP2 transaction via portal"""
    try:
        success, message = delete_ap2_transaction(transaction_id)
        
        return jsonify({
            "success": success,
            "message": message,
            "transaction_id": transaction_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete AP2 transaction: {str(e)}"}), 500

# Agent State Management Portal
@bp.post("/api/portal/agent_state")
@require_auth
def portal_create_agent_state():
    """Create a new agent state via portal"""
    try:
        data = request.get_json() or {}
        session_id = data.get("session_id", f"state_{g.uid}_{int(__import__('time').time())}")
        
        # Remove session_id from data to avoid duplication
        state_data = {k: v for k, v in data.items() if k != "session_id"}
        state_data["user_id"] = g.uid  # Ensure user association
        
        success, message = create_agent_state(session_id, state_data)
        
        return jsonify({
            "success": success,
            "message": message,
            "session_id": session_id
        }), 201 if success else 400
        
    except Exception as e:
        return jsonify({"error": f"Failed to create agent state: {str(e)}"}), 500

@bp.get("/api/portal/agent_state/<session_id>")
@require_auth
def portal_get_agent_state(session_id):
    """Get agent state data via portal"""
    try:
        state_data, message = get_agent_state(session_id)
        
        return jsonify({
            "success": state_data is not None,
            "state": state_data,
            "message": message
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get agent state: {str(e)}"}), 500

@bp.get("/api/portal/agent_state")
@require_auth
def portal_get_user_agent_states():
    """Get all agent states for current user via portal"""
    try:
        limit = int(request.args.get("limit", 10))
        states, message = get_user_agent_states(g.uid, limit)
        
        return jsonify({
            "success": True,
            "states": states,
            "count": len(states),
            "message": message
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get agent states: {str(e)}"}), 500

@bp.put("/api/portal/agent_state/<session_id>")
@require_auth
def portal_update_agent_state(session_id):
    """Update agent state data via portal"""
    try:
        data = request.get_json() or {}
        
        success, message = update_agent_state(session_id, data)
        
        return jsonify({
            "success": success,
            "message": message,
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to update agent state: {str(e)}"}), 500

@bp.delete("/api/portal/agent_state/<session_id>")
@require_auth
def portal_delete_agent_state(session_id):
    """Delete agent state via portal"""
    try:
        success, message = delete_agent_state(session_id)
        
        return jsonify({
            "success": success,
            "message": message,
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete agent state: {str(e)}"}), 500

# Utility and Maintenance Portal
@bp.post("/api/portal/cleanup")
@require_auth
def portal_cleanup_expired_data():
    """Clean up expired data via portal"""
    try:
        deleted_count, message = cleanup_expired_data()
        
        return jsonify({
            "success": True,
            "deleted_count": deleted_count,
            "message": message
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to cleanup data: {str(e)}"}), 500

@bp.get("/api/portal/demo")
def portal_demo():
    """Demo endpoint showing available portal operations"""
    return jsonify({
        "service": "Firestore Portal",
        "description": "Comprehensive CRUD operations for TrustAgent Firestore collections",
        "collections": {
            "users": {
                "endpoints": [
                    "POST /api/portal/users - Create user",
                    "GET /api/portal/users/<user_id> - Get user",
                    "PUT /api/portal/users/<user_id> - Update user",
                    "DELETE /api/portal/users/<user_id> - Delete user"
                ],
                "structure": {
                    "email": "string",
                    "first_name": "string",
                    "last_name": "string",
                    "trust_score": "number",
                    "preferences": "object",
                    "financial_profile": "object"
                }
            },
            "chat_sessions": {
                "endpoints": [
                    "POST /api/portal/chat_sessions - Create session",
                    "GET /api/portal/chat_sessions/<session_id> - Get session",
                    "GET /api/portal/chat_sessions - Get user sessions",
                    "POST /api/portal/chat_sessions/<session_id>/messages - Add message",
                    "DELETE /api/portal/chat_sessions/<session_id> - Delete session"
                ],
                "structure": {
                    "user_id": "string",
                    "messages": "array",
                    "context": "object",
                    "status": "string"
                }
            },
            "ap2_transactions": {
                "endpoints": [
                    "POST /api/portal/ap2_transactions - Create transaction",
                    "GET /api/portal/ap2_transactions/<transaction_id> - Get transaction",
                    "GET /api/portal/ap2_transactions - Get user transactions",
                    "PUT /api/portal/ap2_transactions/<transaction_id> - Update transaction",
                    "DELETE /api/portal/ap2_transactions/<transaction_id> - Delete transaction"
                ],
                "structure": {
                    "user_id": "string",
                    "mandate_type": "string",
                    "intent_mandate": "object",
                    "cart_mandate": "object",
                    "payment_mandate": "object",
                    "status": "string",
                    "cryptographic_proofs": "object"
                }
            },
            "agent_state": {
                "endpoints": [
                    "POST /api/portal/agent_state - Create state",
                    "GET /api/portal/agent_state/<session_id> - Get state",
                    "GET /api/portal/agent_state - Get user states",
                    "PUT /api/portal/agent_state/<session_id> - Update state",
                    "DELETE /api/portal/agent_state/<session_id> - Delete state"
                ],
                "structure": {
                    "user_id": "string",
                    "session_id": "string",
                    "current_context": "object",
                    "pending_actions": "array",
                    "financial_insights": "array",
                    "trust_metrics": "object"
                }
            }
        },
        "utility_endpoints": [
            "GET /api/portal/stats - Get collection statistics",
            "POST /api/portal/cleanup - Clean up expired data",
            "GET /api/portal/demo - This demo endpoint"
        ]
    })