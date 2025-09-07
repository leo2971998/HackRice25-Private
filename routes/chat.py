# routes/chat.py
from flask import Blueprint, request, jsonify
import os
import sys
import requests

# Add utils directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.gemini_ai import generate_financial_assistance_response
from utils.ai_agent import process_financial_query

bp = Blueprint("chat", __name__)

@bp.post("/ask")
def ask():
    """Handle AI chat questions using AI microservice or fallback to local processing"""
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    # Try to use AI microservice first if URL is configured
    ai_service_url = os.getenv('AI_SERVICE_URL')
    
    if ai_service_url:
        try:
            # Call the AI microservice
            response = requests.post(
                f"{ai_service_url}/ask",
                json={"question": question},
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                return jsonify({
                    "answer": ai_response["answer"],
                    "sources": ai_response["sources"],
                    "provider": "ai-microservice"
                })
            else:
                print(f"AI service returned error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to AI service: {e}")
        except Exception as e:
            print(f"Error calling AI service: {e}")
    
    # Fallback to local AI processing with advanced agent if available
    try:
        # Extract user context and conversation history from request
        user_context = data.get("context", {})
        conversation_history = data.get("conversation_history", [])
        
        # Process with the advanced AI agent
        response = process_financial_query(question, user_context=user_context, conversation_history=conversation_history)
        
        return jsonify({
            "answer": response["answer"],
            "sources": response["sources"],
            "provider": response.get("provider", "ai-agent"),
            "agent_used": response.get("agent_used", False),
            "action_items": response.get("action_items", []),
            "priority_level": response.get("priority_level", "medium"),
            "follow_up_questions": response.get("follow_up_questions", []),
            "intent_classification": response.get("intent_classification", {})
        })
        
    except Exception as e:
        # Final fallback to a generic error response
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            "answer": "I'm sorry, I'm having trouble processing your request right now. Please try again later or contact Houston/Harris County services directly for assistance.",
            "sources": [],
            "provider": "fallback"
        }), 500