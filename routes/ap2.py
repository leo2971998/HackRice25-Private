# routes/ap2.py
"""
AP2 (Agent Payments Protocol) Routes for TrustAgent
Handles mandate creation, approval, and execution for autonomous financial operations
"""

import os
from flask import Blueprint, request, jsonify, g
from .auth import require_auth
from utils.ap2_protocol import ap2_protocol, MandateType, MandateStatus

bp = Blueprint("ap2", __name__)

@bp.get("/api/ap2/health")
def ap2_health():
    """Health check for AP2 protocol"""
    return jsonify({
        "status": "ok",
        "protocol": "AP2",
        "version": "1.0.0",
        "features": ["intent_mandates", "cart_mandates", "payment_mandates", "autonomous_execution"]
    })

@bp.post("/api/ap2/mandates/intent")
@require_auth
def create_intent_mandate():
    """Create an intent mandate for autonomous financial operations"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        intent_type = data.get("intent_type")
        if not intent_type:
            return jsonify({"error": "intent_type is required"}), 400
        
        # Create intent mandate
        mandate = ap2_protocol.create_intent_mandate(g.uid, data)
        
        # Auto-approve certain safe intent types
        safe_intents = ["savings_goal", "budget_alert", "spending_analysis"]
        if intent_type in safe_intents:
            mandate.approve()
        
        return jsonify({
            "success": True,
            "mandate": mandate.to_dict(),
            "message": f"Intent mandate created for {intent_type}"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to create intent mandate: {str(e)}"}), 500

@bp.post("/api/ap2/mandates/cart")
@require_auth
def create_cart_mandate():
    """Create a cart mandate for subscription or recurring payments"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        items = data.get("items", [])
        if not items:
            return jsonify({"error": "items are required for cart mandate"}), 400
        
        # Calculate total amount
        total_amount = sum(item.get("amount", 0) for item in items)
        data["total_amount"] = total_amount
        
        # Create cart mandate
        mandate = ap2_protocol.create_cart_mandate(g.uid, data)
        
        # Auto-approve small subscription amounts (under $50)
        if total_amount < 50:
            mandate.approve()
        
        return jsonify({
            "success": True,
            "mandate": mandate.to_dict(),
            "message": f"Cart mandate created with {len(items)} items (${total_amount})"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to create cart mandate: {str(e)}"}), 500

@bp.post("/api/ap2/mandates/payment")
@require_auth
def create_payment_mandate():
    """Create a payment mandate for immediate financial operations"""
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        amount = data.get("amount")
        purpose = data.get("purpose")
        
        if not amount or not purpose:
            return jsonify({"error": "amount and purpose are required"}), 400
        
        # Create payment mandate
        mandate = ap2_protocol.create_payment_mandate(g.uid, data)
        
        # Auto-approve emergency payments under $100
        if purpose == "emergency" and amount < 100:
            mandate.approve()
        
        return jsonify({
            "success": True,
            "mandate": mandate.to_dict(),
            "message": f"Payment mandate created for {purpose} (${amount})"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to create payment mandate: {str(e)}"}), 500

@bp.get("/api/ap2/mandates")
@require_auth
def get_user_mandates():
    """Get all mandates for the current user"""
    try:
        status_filter = request.args.get("status")
        mandate_status = None
        
        if status_filter:
            try:
                mandate_status = MandateStatus(status_filter.lower())
            except ValueError:
                return jsonify({"error": f"Invalid status: {status_filter}"}), 400
        
        mandates = ap2_protocol.get_user_mandates(g.uid, mandate_status)
        
        return jsonify({
            "success": True,
            "mandates": [mandate.to_dict() for mandate in mandates],
            "count": len(mandates)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get mandates: {str(e)}"}), 500

@bp.get("/api/ap2/mandates/<mandate_id>")
@require_auth
def get_mandate(mandate_id):
    """Get specific mandate details"""
    try:
        mandate = ap2_protocol.get_mandate(mandate_id)
        
        if not mandate:
            return jsonify({"error": "Mandate not found"}), 404
        
        # Verify user owns this mandate
        if mandate.user_id != g.uid:
            return jsonify({"error": "Access denied"}), 403
        
        return jsonify({
            "success": True,
            "mandate": mandate.to_dict()
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get mandate: {str(e)}"}), 500

@bp.post("/api/ap2/mandates/<mandate_id>/approve")
@require_auth
def approve_mandate(mandate_id):
    """Approve a pending mandate"""
    try:
        mandate = ap2_protocol.get_mandate(mandate_id)
        
        if not mandate:
            return jsonify({"error": "Mandate not found"}), 404
        
        # Verify user owns this mandate
        if mandate.user_id != g.uid:
            return jsonify({"error": "Access denied"}), 403
        
        if ap2_protocol.approve_mandate(mandate_id):
            return jsonify({
                "success": True,
                "mandate": mandate.to_dict(),
                "message": "Mandate approved successfully"
            })
        else:
            return jsonify({"error": "Failed to approve mandate"}), 400
        
    except Exception as e:
        return jsonify({"error": f"Failed to approve mandate: {str(e)}"}), 500

@bp.post("/api/ap2/mandates/<mandate_id>/execute")
@require_auth
def execute_mandate(mandate_id):
    """Execute an approved mandate"""
    try:
        mandate = ap2_protocol.get_mandate(mandate_id)
        
        if not mandate:
            return jsonify({"error": "Mandate not found"}), 404
        
        # Verify user owns this mandate
        if mandate.user_id != g.uid:
            return jsonify({"error": "Access denied"}), 403
        
        result = ap2_protocol.execute_mandate(mandate_id)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "mandate": mandate.to_dict(),
                "execution_result": result,
                "message": "Mandate executed successfully"
            })
        else:
            return jsonify({
                "error": result.get("error", "Execution failed")
            }), 400
        
    except Exception as e:
        return jsonify({"error": f"Failed to execute mandate: {str(e)}"}), 500

@bp.post("/api/ap2/mandates/<mandate_id>/cancel")
@require_auth
def cancel_mandate(mandate_id):
    """Cancel a pending mandate"""
    try:
        mandate = ap2_protocol.get_mandate(mandate_id)
        
        if not mandate:
            return jsonify({"error": "Mandate not found"}), 404
        
        # Verify user owns this mandate
        if mandate.user_id != g.uid:
            return jsonify({"error": "Access denied"}), 403
        
        if mandate.cancel():
            return jsonify({
                "success": True,
                "mandate": mandate.to_dict(),
                "message": "Mandate cancelled successfully"
            })
        else:
            return jsonify({"error": "Cannot cancel mandate in current state"}), 400
        
    except Exception as e:
        return jsonify({"error": f"Failed to cancel mandate: {str(e)}"}), 500

@bp.get("/api/ap2/stats")
@require_auth
def get_ap2_stats():
    """Get AP2 usage statistics for the user"""
    try:
        all_mandates = ap2_protocol.get_user_mandates(g.uid)
        
        stats = {
            "total_mandates": len(all_mandates),
            "by_type": {},
            "by_status": {},
            "total_executed": 0,
            "pending_approval": 0
        }
        
        for mandate in all_mandates:
            # Count by type
            mandate_type = mandate.type.value
            stats["by_type"][mandate_type] = stats["by_type"].get(mandate_type, 0) + 1
            
            # Count by status
            mandate_status = mandate.status.value
            stats["by_status"][mandate_status] = stats["by_status"].get(mandate_status, 0) + 1
            
            # Special counts
            if mandate.status == MandateStatus.EXECUTED:
                stats["total_executed"] += 1
            elif mandate.status == MandateStatus.PENDING:
                stats["pending_approval"] += 1
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get AP2 stats: {str(e)}"}), 500

@bp.post("/api/ap2/cleanup")
@require_auth
def cleanup_expired_mandates():
    """Clean up expired mandates (admin function)"""
    try:
        expired_count = ap2_protocol.cleanup_expired_mandates()
        
        return jsonify({
            "success": True,
            "message": f"Cleaned up {expired_count} expired mandates"
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to cleanup mandates: {str(e)}"}), 500