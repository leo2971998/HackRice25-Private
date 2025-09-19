# utils/ai_agent.py
"""
Inflate-Wise AI Agent for Personal Inflation Analysis
Implements transaction categorization and inflation insights using Gemini
"""

import os
import logging
from typing import List, Dict, Optional, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Gemini for inflation analysis
try:
    import google.generativeai as genai
    from utils.gemini import build_financial_coach_response, categorize_transactions
    GEMINI_AVAILABLE = True
    logger.info("Gemini AI available for inflation analysis")
except ImportError as e:
    GEMINI_AVAILABLE = False
    logger.warning(f"Gemini AI not available: {e}")


class InflateWiseAgent:
    """AI agent focused on personal inflation analysis and financial insights"""
    
    def __init__(self):
        self.initialized = self._initialize_gemini()
    
    def _initialize_gemini(self) -> bool:
        """Initialize Gemini AI for inflation analysis"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.warning("GEMINI_API_KEY not found, agent initialization skipped")
                return False
            
            genai.configure(api_key=api_key)
            logger.info("Gemini AI initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            return False
    
    def categorize_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Categorize transactions using Gemini AI for inflation analysis"""
        if not self.initialized or not transactions:
            return transactions
        
        try:
            return categorize_transactions(transactions)
        except Exception as e:
            logger.error(f"Error categorizing transactions: {e}")
            return transactions
    
    def generate_inflation_insights(self, context: Dict[str, Any], question: str) -> str:
        """Generate personalized inflation insights using Gemini"""
        if not self.initialized:
            return self._fallback_inflation_response(context, question)
        
        try:
            return build_financial_coach_response(context, question)
        except Exception as e:
            logger.error(f"Error generating inflation insights: {e}")
            return self._fallback_inflation_response(context, question)
    
    def _fallback_inflation_response(self, context: Dict[str, Any], question: str) -> str:
        """Fallback response when Gemini is unavailable"""
        inflation_data = context.get("personal_inflation", {})
        rate = inflation_data.get("personal_rate")
        
        fallback_lines = [
            "Inflate-Wise Analysis:",
            f"• Your personal inflation rate: {rate}%" if rate is not None else "• Personal inflation rate is being calculated",
        ]
        
        if inflation_data.get("top_drivers"):
            fallback_lines.append(f"• Top spending drivers: {', '.join(inflation_data['top_drivers'])}")
        
        if inflation_data.get("spending_by_category"):
            fallback_lines.append("• Focus on categories with highest inflation impact for savings")
        
        fallback_lines.append("• Connect your accounts for more detailed analysis")
        
        return "\n".join(fallback_lines)


# Global agent instance
_agent_instance = None

def get_inflation_agent() -> InflateWiseAgent:
    """Get or create the global inflation agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = InflateWiseAgent()
    return _agent_instance

def process_inflation_query(query: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
    """Process an inflation-related query using the InflateWise agent"""
    agent = get_inflation_agent()
    
    try:
        answer = agent.generate_inflation_insights(user_context or {}, query)
        
        return {
            "answer": answer,
            "title": "Personal Inflation Analysis",
            "summary": answer,
            "actionable_steps": _extract_action_items(answer),
            "sources": [],
            "provider": "inflate-wise-agent",
            "agent_used": True
        }
    except Exception as e:
        logger.error(f"Error processing inflation query: {e}")
        return {
            "answer": "I'm experiencing technical difficulties. Please try again or contact support.",
            "title": "Error",
            "summary": "Technical error occurred",
            "actionable_steps": ["Try asking your question again", "Contact support if the issue persists"],
            "sources": [],
            "provider": "error-fallback",
            "agent_used": False
        }

def _extract_action_items(answer: str) -> List[str]:
    """Extract actionable insights from the AI response"""
    action_items = []
    
    # Look for numbered lists or bullet points
    import re
    
    # Find numbered steps (1. 2. 3. etc.)
    numbered_steps = re.findall(r'\d+\.\s*([^\\n]+)', answer)
    action_items.extend(numbered_steps)
    
    # Find bullet points (- or • )
    bullet_points = re.findall(r'[-•]\s*([^\\n]+)', answer)
    action_items.extend(bullet_points)
    
    # If no structured actions found, create general inflation-focused ones
    if not action_items:
        if "inflation" in answer.lower():
            action_items.append("Monitor your personal inflation rate regularly")
        if "spending" in answer.lower() or "category" in answer.lower():
            action_items.append("Review spending categories with highest inflation impact")
        if "budget" in answer.lower():
            action_items.append("Adjust budget to account for inflation")
        
        # Always include a default action
        if not action_items:
            action_items.append("Connect your financial accounts for personalized inflation analysis")
    
    return action_items[:5]  # Limit to top 5 actions

# Legacy compatibility function for existing imports
def process_financial_query(query: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
    """Legacy compatibility wrapper - redirects to inflation query processing"""
    return process_inflation_query(query, user_context)