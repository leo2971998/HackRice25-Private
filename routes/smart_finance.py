# routes/smart_finance.py
"""
Smart Financial Features Routes for TrustAgent
Budget enforcement, savings automation, subscription optimization
"""

from flask import Blueprint, request, jsonify, g
from .auth import require_auth
from utils.smart_finance import smart_budget, savings_automation, subscription_optimizer, emergency_response
from utils.ap2_protocol import ap2_protocol

bp = Blueprint("smart_finance", __name__)

@bp.get("/api/smart-finance/health")
def smart_finance_health():
    """Health check for smart finance features"""
    return jsonify({
        "status": "ok",
        "features": [
            "smart_budget_alerts",
            "savings_automation", 
            "subscription_optimization",
            "emergency_response",
            "what_if_scenarios"
        ]
    })

# Budget Management Endpoints
@bp.post("/api/smart-finance/budget/alerts")
@require_auth
def create_budget_alert():
    """Create smart budget alert with AP2 integration"""
    try:
        data = request.get_json() or {}
        
        category = data.get("category")
        monthly_limit = data.get("monthly_limit")
        alert_threshold = data.get("alert_threshold", 0.8)
        
        if not category or not monthly_limit:
            return jsonify({"error": "category and monthly_limit are required"}), 400
        
        result = smart_budget.set_budget_alert(g.uid, category, monthly_limit, alert_threshold)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify({"error": result.get("error")}), 500
            
    except Exception as e:
        return jsonify({"error": f"Failed to create budget alert: {str(e)}"}), 500

@bp.post("/api/smart-finance/budget/check")
@require_auth
def check_budget_spending():
    """Check current spending against budget alerts"""
    try:
        data = request.get_json() or {}
        transactions = data.get("transactions", [])
        
        alerts = smart_budget.check_spending(g.uid, transactions)
        
        return jsonify({
            "success": True,
            "alerts": alerts,
            "alert_count": len(alerts)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to check budget: {str(e)}"}), 500

# Savings Automation Endpoints
@bp.post("/api/smart-finance/savings/goals")
@require_auth
def create_savings_goal():
    """Create automated savings goal with AP2 mandate"""
    try:
        data = request.get_json() or {}
        
        required_fields = ["name", "target_amount", "monthly_amount"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
        result = savings_automation.create_savings_goal(g.uid, data)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify({"error": result.get("error")}), 500
            
    except Exception as e:
        return jsonify({"error": f"Failed to create savings goal: {str(e)}"}), 500

@bp.get("/api/smart-finance/savings/recommendations")
@require_auth
def get_savings_recommendations():
    """Get AI-powered savings recommendations"""
    try:
        # Get user's financial data (mock for now)
        financial_data = request.args.to_dict()
        
        # Add some defaults if not provided
        if not financial_data:
            financial_data = {
                "total_balance": 1000,
                "recent_transactions": []
            }
        
        recommendations = savings_automation.get_savings_recommendations(g.uid, financial_data)
        
        return jsonify({
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get recommendations: {str(e)}"}), 500

# Subscription Optimization Endpoints
@bp.post("/api/smart-finance/subscriptions/detect")
@require_auth
def detect_subscriptions():
    """Detect subscriptions from transaction data"""
    try:
        data = request.get_json() or {}
        transactions = data.get("transactions", [])
        
        subscriptions = subscription_optimizer.detect_subscriptions(g.uid, transactions)
        
        # Calculate total monthly cost
        total_monthly = sum(sub.get("amount", 0) for sub in subscriptions)
        
        return jsonify({
            "success": True,
            "subscriptions": subscriptions,
            "count": len(subscriptions),
            "estimated_monthly_cost": total_monthly,
            "optimization_potential": sum(sub.get("optimization_score", 0) for sub in subscriptions)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to detect subscriptions: {str(e)}"}), 500

# Emergency Response Endpoints
@bp.post("/api/smart-finance/emergency/check")
@require_auth
def check_emergency_conditions():
    """Check for emergency financial conditions"""
    try:
        data = request.get_json() or {}
        financial_data = data.get("financial_data", {})
        
        alerts = emergency_response.check_emergency_conditions(g.uid, financial_data)
        
        return jsonify({
            "success": True,
            "emergency_alerts": alerts,
            "alert_count": len(alerts),
            "requires_immediate_attention": any(alert.get("severity") == "high" for alert in alerts)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to check emergency conditions: {str(e)}"}), 500

# What-If Scenario Analysis
@bp.post("/api/smart-finance/scenarios/analyze")
@require_auth
def analyze_scenario():
    """Analyze 'What If' financial scenarios"""
    try:
        data = request.get_json() or {}
        
        scenario_type = data.get("scenario_type")
        parameters = data.get("parameters", {})
        
        if not scenario_type:
            return jsonify({"error": "scenario_type is required"}), 400
        
        result = analyze_financial_scenario(scenario_type, parameters, g.uid)
        
        return jsonify({
            "success": True,
            "scenario": scenario_type,
            "analysis": result
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to analyze scenario: {str(e)}"}), 500

def analyze_financial_scenario(scenario_type: str, parameters: dict, user_id: str) -> dict:
    """Analyze different financial scenarios"""
    
    if scenario_type == "income_change":
        current_income = parameters.get("current_income", 3000)
        new_income = parameters.get("new_income", 3500)
        
        change_percent = ((new_income - current_income) / current_income) * 100
        monthly_difference = new_income - current_income
        
        return {
            "income_change_percent": change_percent,
            "monthly_difference": monthly_difference,
            "annual_difference": monthly_difference * 12,
            "recommendations": [
                f"With ${monthly_difference:.0f} extra monthly, consider increasing savings by 20%",
                "Update your budget categories to reflect new income level",
                "Consider automating the extra income into savings or investments"
            ] if monthly_difference > 0 else [
                f"Budget reduction needed: ${abs(monthly_difference):.0f} less monthly income",
                "Review and prioritize essential expenses",
                "Consider emergency fund if income loss is temporary"
            ]
        }
    
    elif scenario_type == "expense_reduction":
        current_expenses = parameters.get("current_expenses", 2500)
        reduction_amount = parameters.get("reduction_amount", 300)
        
        new_expenses = current_expenses - reduction_amount
        savings_potential = reduction_amount * 12
        
        return {
            "expense_reduction": reduction_amount,
            "new_monthly_expenses": new_expenses,
            "annual_savings_potential": savings_potential,
            "recommendations": [
                f"Reducing expenses by ${reduction_amount:.0f}/month saves ${savings_potential:.0f}/year",
                "Consider automating these savings into a high-yield account",
                "Track progress monthly to ensure sustainability"
            ]
        }
    
    elif scenario_type == "emergency_fund":
        monthly_expenses = parameters.get("monthly_expenses", 2500)
        current_savings = parameters.get("current_savings", 500)
        target_months = parameters.get("target_months", 6)
        
        target_amount = monthly_expenses * target_months
        needed_amount = target_amount - current_savings
        monthly_contribution = needed_amount / 12  # 1 year to build
        
        return {
            "target_emergency_fund": target_amount,
            "current_amount": current_savings,
            "amount_needed": needed_amount,
            "recommended_monthly_contribution": monthly_contribution,
            "time_to_goal_months": 12,
            "recommendations": [
                f"Build ${target_amount:.0f} emergency fund ({target_months} months of expenses)",
                f"Save ${monthly_contribution:.0f}/month to reach goal in 1 year",
                "Consider high-yield savings account for emergency fund"
            ]
        }
    
    else:
        return {
            "error": f"Unknown scenario type: {scenario_type}",
            "supported_scenarios": ["income_change", "expense_reduction", "emergency_fund"]
        }

# Enhanced Dashboard Data
@bp.get("/api/smart-finance/dashboard")
@require_auth
def get_smart_dashboard():
    """Get comprehensive smart finance dashboard data"""
    try:
        # Get user's AP2 mandates
        user_mandates = ap2_protocol.get_user_mandates(g.uid)
        
        # Get AP2 stats
        stats = {
            "total_mandates": len(user_mandates),
            "active_automations": len([m for m in user_mandates if m.status.value == "executed"]),
            "pending_approvals": len([m for m in user_mandates if m.status.value == "pending"])
        }
        
        # Mock financial insights
        insights = [
            {
                "type": "savings_opportunity",
                "message": "You could save an extra $150/month by optimizing subscriptions",
                "action": "Review subscription analysis",
                "priority": "medium"
            },
            {
                "type": "budget_performance",
                "message": "You're 15% under budget in dining this month - great job!",
                "action": "Continue current spending pattern",
                "priority": "positive"
            },
            {
                "type": "automation_suggestion",
                "message": "Set up automated savings for your emergency fund goal",
                "action": "Create savings mandate",
                "priority": "high"
            }
        ]
        
        return jsonify({
            "success": True,
            "ap2_stats": stats,
            "active_mandates": len([m for m in user_mandates if m.status.value in ["pending", "approved"]]),
            "insights": insights,
            "features_enabled": [
                "budget_alerts",
                "savings_automation",
                "subscription_optimization",
                "emergency_monitoring",
                "scenario_analysis"
            ]
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get dashboard: {str(e)}"}), 500