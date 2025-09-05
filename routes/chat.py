# routes/chat.py
from flask import Blueprint, request, jsonify

bp = Blueprint("chat", __name__)

@bp.post("/ask")
def ask():
    """Handle AI chat questions and return mock responses for now"""
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    # Mock response for now - this should be replaced with actual AI/search logic
    mock_sources = [
        {
            "name": "Houston Housing Authority - Rental Assistance",
            "why": "Provides rental assistance programs for low-income families",
            "url": "https://www.housingforhouston.com/",
            "apply_url": "https://www.housingforhouston.com/apply",
            "phone": "(713) 260-0600", 
            "eligibility": "Must meet income requirements (typically 50% of area median income)",
            "county": "Harris County",
            "last_verified": "2025-01-15"
        },
        {
            "name": "Harris County Emergency Rental Assistance",
            "why": "Emergency rental and utility assistance for eligible residents",
            "url": "https://www.harriscountytx.gov/",
            "phone": "(832) 927-4400",
            "eligibility": "Income at or below 80% of area median income",
            "county": "Harris County", 
            "last_verified": "2025-01-15"
        }
    ]
    
    # Generate a basic response based on question keywords
    question_lower = question.lower()
    if "rent" in question_lower or "housing" in question_lower:
        answer = "I found several rental assistance programs in Houston/Harris County. The Houston Housing Authority offers ongoing rental assistance for qualified low-income families, and Harris County provides emergency rental assistance. Both programs have income requirements and application processes."
        sources = mock_sources
    elif "utility" in question_lower or "electric" in question_lower or "water" in question_lower:
        answer = "For utility assistance in Houston, you can apply for the Low Income Home Energy Assistance Program (LIHEAP) through Harris County, or contact CenterPoint Energy for bill payment assistance programs. Many programs are available year-round."
        sources = [
            {
                "name": "Harris County LIHEAP",
                "why": "Low Income Home Energy Assistance Program",
                "url": "https://www.harriscountytx.gov/",
                "phone": "(832) 927-4400",
                "eligibility": "Income guidelines apply",
                "county": "Harris County",
                "last_verified": "2025-01-15"
            }
        ]
    elif "food" in question_lower or "snap" in question_lower:
        answer = "For food assistance, you can apply for SNAP benefits through the Texas Health and Human Services, visit local food banks like the Houston Food Bank, or find community meal programs. Many programs serve Harris County residents."
        sources = [
            {
                "name": "Houston Food Bank",
                "why": "Largest food distribution organization in Houston",
                "url": "https://www.houstonfoodbank.org/",
                "phone": "(713) 223-3700",
                "eligibility": "Open to all community members in need",
                "county": "Harris County",
                "last_verified": "2025-01-15"
            }
        ]
    else:
        answer = f"I can help you find information about rental assistance, utility programs, food assistance, and homebuyer aid in Houston/Harris County. Could you be more specific about what type of help you need?"
        sources = []
    
    return jsonify({
        "answer": answer,
        "sources": sources
    })