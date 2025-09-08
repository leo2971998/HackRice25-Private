# AI Chatbot Microservice
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent directory to path to import utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.gemini_ai import generate_financial_assistance_response
from utils.ai_agent import process_financial_query

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for cross-service communication
    CORS(app, supports_credentials=True)
    
    @app.route('/healthz')
    def healthz():
        return {"status": "ok", "service": "Houston Financial Navigator AI Service"}, 200
    
    @app.route('/ask', methods=['POST'])
    def ask():
        """AI chat endpoint for financial assistance questions"""
        try:
            data = request.get_json() or {}
            question = data.get("question", "").strip()
            
            if not question:
                return jsonify({"error": "Question is required"}), 400
            
            # Use advanced AI agent to generate response
            response = process_financial_query(question, user_context=data.get("context"))
            
            return jsonify({
                "title": response.get("title", ""),
                "summary": response.get("summary", response.get("answer", "")),
                "actionable_steps": response.get("actionable_steps", []),
                "sources": response.get("sources", []),
                "service": "ai-chatbot",
                "provider": response.get("provider", "ai-agent"),
                "agent_used": response.get("agent_used", False)
            })
            
        except Exception as e:
            print(f"Error in AI service: {e}")
            return jsonify({
                "error": "AI service temporarily unavailable",
                "message": str(e)
            }), 500
    
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv('PORT', 8080))
    app.run(debug=True, host="0.0.0.0", port=port)