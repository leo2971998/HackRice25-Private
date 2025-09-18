# utils/smart_finance.py
"""
Smart Financial Features for TrustAgent
Enhanced budget enforcement, savings automation, and financial intelligence
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from utils.ap2_protocol import ap2_protocol, MandateType

class SmartBudgetEngine:
    """
    AI-powered budget enforcement with real-time alerts and recommendations
    """
    
    def __init__(self):
        self.budget_alerts = {}
        self.spending_patterns = {}
        self.alert_triggers = {}
    
    def set_budget_alert(self, user_id: str, category: str, monthly_limit: float, alert_threshold: float = 0.8) -> Dict:
        """Set up smart budget alert with AP2 mandate"""
        try:
            # Create AP2 intent mandate for budget monitoring
            intent_data = {
                "intent_type": "budget_alert",
                "category": category,
                "monthly_limit": monthly_limit,
                "alert_threshold": alert_threshold,
                "current_month": datetime.now().strftime("%Y-%m")
            }
            
            mandate = ap2_protocol.create_intent_mandate(user_id, intent_data)
            mandate.approve()  # Auto-approve budget alerts
            
            # Store in budget system
            alert_key = f"{user_id}_{category}"
            self.budget_alerts[alert_key] = {
                "user_id": user_id,
                "category": category,
                "monthly_limit": monthly_limit,
                "alert_threshold": alert_threshold,
                "current_spending": 0,
                "mandate_id": mandate.id,
                "created_at": datetime.now().isoformat(),
                "last_alert": None
            }
            
            return {
                "success": True,
                "alert_id": alert_key,
                "mandate_id": mandate.id,
                "message": f"Budget alert set for {category} at ${monthly_limit}/month"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_spending(self, user_id: str, transactions: List[Dict]) -> List[Dict]:
        """Check spending against budget alerts and return triggered alerts"""
        alerts = []
        current_month = datetime.now().strftime("%Y-%m")
        
        for alert_key, alert_data in self.budget_alerts.items():
            if not alert_key.startswith(user_id):
                continue
            
            category = alert_data["category"]
            monthly_limit = alert_data["monthly_limit"]
            alert_threshold = alert_data["alert_threshold"]
            
            # Calculate current month spending for this category
            current_spending = self._calculate_category_spending(transactions, category, current_month)
            alert_data["current_spending"] = current_spending
            
            # Check if alert threshold is reached
            spending_ratio = current_spending / monthly_limit if monthly_limit > 0 else 0
            
            if spending_ratio >= alert_threshold:
                alert = {
                    "type": "budget_alert",
                    "category": category,
                    "current_spending": current_spending,
                    "monthly_limit": monthly_limit,
                    "percentage_used": spending_ratio * 100,
                    "message": f"⚠️ Budget Alert: You've spent ${current_spending:.2f} of your ${monthly_limit} {category} budget ({spending_ratio*100:.1f}%)",
                    "severity": "high" if spending_ratio >= 1.0 else "medium",
                    "recommendations": self._get_budget_recommendations(category, spending_ratio)
                }
                alerts.append(alert)
                alert_data["last_alert"] = datetime.now().isoformat()
        
        return alerts
    
    def _calculate_category_spending(self, transactions: List[Dict], category: str, month: str) -> float:
        """Calculate spending for a specific category in the given month"""
        total = 0
        category_keywords = self._get_category_keywords(category)
        
        for transaction in transactions:
            # Check if transaction is in current month
            trans_date = transaction.get("transaction_date", transaction.get("purchase_date", ""))
            if not trans_date.startswith(month):
                continue
            
            # Check if transaction matches category
            description = transaction.get("description", "").lower()
            amount = abs(transaction.get("amount", 0))
            
            if any(keyword in description for keyword in category_keywords):
                total += amount
        
        return total
    
    def _get_category_keywords(self, category: str) -> List[str]:
        """Get keywords to identify transactions for a category"""
        category_map = {
            "groceries": ["grocery", "supermarket", "food", "h-e-b", "walmart", "kroger"],
            "gas": ["gas", "fuel", "shell", "exxon", "chevron", "bp"],
            "dining": ["restaurant", "food", "pizza", "coffee", "starbucks", "mcdonald"],
            "entertainment": ["movie", "theater", "netflix", "spotify", "gaming"],
            "shopping": ["amazon", "target", "mall", "store", "shop"],
            "utilities": ["electric", "water", "internet", "phone", "cable"],
            "transportation": ["uber", "lyft", "taxi", "parking", "toll"],
            "healthcare": ["doctor", "pharmacy", "medical", "hospital", "cvs"]
        }
        
        return category_map.get(category.lower(), [category.lower()])
    
    def _get_budget_recommendations(self, category: str, spending_ratio: float) -> List[str]:
        """Get smart recommendations based on spending patterns"""
        recommendations = []
        
        if spending_ratio >= 1.0:
            recommendations.append(f"🚨 You've exceeded your {category} budget! Consider reducing spending this month.")
            recommendations.append("💡 Try finding alternatives or delaying non-essential purchases.")
        elif spending_ratio >= 0.8:
            recommendations.append(f"⚠️ You're approaching your {category} budget limit.")
            recommendations.append("💡 Consider tracking daily spending more closely.")
        
        # Category-specific recommendations
        if category.lower() == "groceries":
            recommendations.append("🛒 Try meal planning and shopping with a list to reduce impulse purchases.")
        elif category.lower() == "dining":
            recommendations.append("🍽️ Consider cooking more meals at home to save money.")
        elif category.lower() == "entertainment":
            recommendations.append("🎬 Look for free or low-cost entertainment options in your area.")
        
        return recommendations

class SavingsAutomation:
    """
    Autonomous savings goals with AI-powered recommendations
    """
    
    def __init__(self):
        self.savings_goals = {}
    
    def create_savings_goal(self, user_id: str, goal_data: Dict) -> Dict:
        """Create automated savings goal with AP2 mandate"""
        try:
            goal_name = goal_data.get("name", "Savings Goal")
            target_amount = goal_data.get("target_amount", 1000)
            monthly_amount = goal_data.get("monthly_amount", 100)
            
            # Create AP2 intent mandate for savings automation
            intent_data = {
                "intent_type": "savings_goal",
                "goal_name": goal_name,
                "target_amount": target_amount,
                "monthly_amount": monthly_amount,
                "frequency": "monthly",
                "auto_transfer": goal_data.get("auto_transfer", True)
            }
            
            mandate = ap2_protocol.create_intent_mandate(user_id, intent_data)
            mandate.approve()  # Auto-approve savings goals
            
            # Calculate timeline
            months_to_goal = target_amount / monthly_amount if monthly_amount > 0 else 0
            target_date = datetime.now() + timedelta(days=months_to_goal * 30)
            
            goal_id = f"{user_id}_savings_{len(self.savings_goals)}"
            self.savings_goals[goal_id] = {
                "id": goal_id,
                "user_id": user_id,
                "name": goal_name,
                "target_amount": target_amount,
                "monthly_amount": monthly_amount,
                "current_amount": 0,
                "mandate_id": mandate.id,
                "created_at": datetime.now().isoformat(),
                "target_date": target_date.isoformat(),
                "progress_percentage": 0,
                "next_transfer": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            return {
                "success": True,
                "goal": self.savings_goals[goal_id],
                "message": f"Savings goal '{goal_name}' created with ${monthly_amount}/month automation"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_savings_recommendations(self, user_id: str, financial_data: Dict) -> List[Dict]:
        """Get AI-powered savings recommendations based on financial patterns"""
        recommendations = []
        
        total_balance = financial_data.get("total_balance", 0)
        monthly_income = self._estimate_monthly_income(financial_data)
        monthly_expenses = self._estimate_monthly_expenses(financial_data)
        
        # Disposable income calculation
        disposable_income = monthly_income - monthly_expenses
        
        if disposable_income > 0:
            # Emergency fund recommendation
            emergency_fund_target = monthly_expenses * 3  # 3 months of expenses
            emergency_fund_monthly = min(disposable_income * 0.2, emergency_fund_target / 12)
            
            recommendations.append({
                "type": "emergency_fund",
                "priority": "high",
                "monthly_amount": emergency_fund_monthly,
                "target_amount": emergency_fund_target,
                "description": f"Build an emergency fund of ${emergency_fund_target:.0f} (3 months of expenses)",
                "rationale": "Emergency funds provide financial security for unexpected expenses"
            })
            
            # High-yield savings recommendation
            if disposable_income > 200:
                high_yield_monthly = disposable_income * 0.3
                recommendations.append({
                    "type": "high_yield_savings",
                    "priority": "medium",
                    "monthly_amount": high_yield_monthly,
                    "target_amount": high_yield_monthly * 12,
                    "description": f"High-yield savings account with ${high_yield_monthly:.0f}/month",
                    "rationale": "Earn higher interest while maintaining liquidity"
                })
            
            # Investment recommendation for higher earners
            if disposable_income > 500:
                investment_monthly = disposable_income * 0.2
                recommendations.append({
                    "type": "investment",
                    "priority": "medium",
                    "monthly_amount": investment_monthly,
                    "target_amount": investment_monthly * 12,
                    "description": f"Investment portfolio with ${investment_monthly:.0f}/month",
                    "rationale": "Long-term wealth building through diversified investments"
                })
        
        return recommendations
    
    def _estimate_monthly_income(self, financial_data: Dict) -> float:
        """Estimate monthly income from transaction data"""
        transactions = financial_data.get("recent_transactions", [])
        deposits = [t for t in transactions if t.get("type") == "deposit" or t.get("amount", 0) > 0]
        
        if deposits:
            # Take largest deposit as likely paycheck
            largest_deposit = max(deposits, key=lambda x: x.get("amount", 0))
            return largest_deposit.get("amount", 0)
        
        return 0
    
    def _estimate_monthly_expenses(self, financial_data: Dict) -> float:
        """Estimate monthly expenses from transaction data"""
        transactions = financial_data.get("recent_transactions", [])
        expenses = [abs(t.get("amount", 0)) for t in transactions if t.get("amount", 0) < 0]
        
        if expenses:
            return sum(expenses)
        
        return 0

class SubscriptionOptimizer:
    """
    Subscription management and optimization system
    """
    
    def __init__(self):
        self.subscriptions = {}
    
    def detect_subscriptions(self, user_id: str, transactions: List[Dict]) -> List[Dict]:
        """Detect recurring subscriptions from transaction data"""
        subscription_keywords = [
            "netflix", "spotify", "apple", "amazon prime", "hulu", "disney",
            "subscription", "monthly", "annual", "yearly", "recurring"
        ]
        
        detected = []
        for transaction in transactions:
            description = transaction.get("description", "").lower()
            amount = abs(transaction.get("amount", 0))
            
            if any(keyword in description for keyword in subscription_keywords):
                detected.append({
                    "description": transaction.get("description"),
                    "amount": amount,
                    "estimated_frequency": "monthly",  # Default assumption
                    "category": "subscription",
                    "optimization_score": self._calculate_optimization_score(description, amount)
                })
        
        return detected
    
    def _calculate_optimization_score(self, description: str, amount: float) -> float:
        """Calculate how much a subscription could be optimized (0-10 scale)"""
        # Higher score = more optimization potential
        score = 5.0  # Base score
        
        # Expensive subscriptions have more optimization potential
        if amount > 50:
            score += 2
        elif amount > 20:
            score += 1
        
        # Common services that often have better alternatives
        if any(service in description.lower() for service in ["cable", "tv", "premium"]):
            score += 2
        
        return min(score, 10.0)

class EmergencyResponseSystem:
    """
    Emergency financial response and alert system
    """
    
    def __init__(self):
        self.emergency_triggers = {}
    
    def check_emergency_conditions(self, user_id: str, financial_data: Dict) -> List[Dict]:
        """Check for emergency financial conditions"""
        alerts = []
        balance = financial_data.get("total_balance", 0)
        
        # Low balance emergency
        if balance < 100:
            alerts.append({
                "type": "low_balance_emergency",
                "severity": "high",
                "message": f"⚠️ Emergency Alert: Low account balance (${balance:.2f})",
                "recommended_actions": [
                    "Review recent transactions for unexpected charges",
                    "Contact bank if unauthorized transactions are found",
                    "Consider emergency fund options",
                    "Temporarily reduce non-essential spending"
                ],
                "ap2_assistance": "Create emergency payment mandate for quick fund access"
            })
        
        # Unusual spending pattern
        recent_transactions = financial_data.get("recent_transactions", [])
        large_transactions = [t for t in recent_transactions if abs(t.get("amount", 0)) > 500]
        
        if len(large_transactions) > 2:  # Multiple large transactions
            alerts.append({
                "type": "unusual_spending",
                "severity": "medium",
                "message": "🔍 Unusual Activity: Multiple large transactions detected",
                "recommended_actions": [
                    "Review large transactions for accuracy",
                    "Verify all charges are legitimate",
                    "Consider setting up spending alerts"
                ],
                "transactions": large_transactions[:3]  # Show first 3
            })
        
        return alerts

# Global instances
smart_budget = SmartBudgetEngine()
savings_automation = SavingsAutomation()
subscription_optimizer = SubscriptionOptimizer()
emergency_response = EmergencyResponseSystem()