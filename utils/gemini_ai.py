# utils/gemini_ai.py
import os
import google.generativeai as genai
from typing import List, Dict

def configure_gemini():
    """Configure Gemini AI with API key"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables")
        return False
    
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error configuring Gemini AI: {e}")
        return False

def test_gemini_connection():
    """Test Gemini AI connection with a simple prompt"""
    try:
        if not configure_gemini():
            return False, "Gemini API key not configured"
        
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, this is a test. Please respond with 'Connection successful'.")
        
        if response and response.text:
            return True, f"Gemini connection successful: {response.text.strip()}"
        else:
            return False, "Gemini response was empty"
            
    except Exception as e:
        return False, f"Gemini connection failed: {str(e)}"

def generate_financial_assistance_response(question: str, houston_data: List[Dict] = None) -> Dict:
    """
    Generate AI response for financial assistance questions using Gemini
    
    Args:
        question: User's question about financial assistance
        houston_data: Optional list of Houston financial assistance programs
    
    Returns:
        Dict with 'answer' and 'sources' keys
    """
    try:
        if not configure_gemini():
            # Fallback to mock response if Gemini not available
            return generate_mock_response(question)
        
        # Build context with Houston financial assistance data
        context = build_houston_context(houston_data)
        
        # Create the prompt
        prompt = f"""
You are a helpful financial assistant specializing in Houston/Harris County financial assistance programs. 

Context about available programs:
{context}

User Question: {question}

Please provide a helpful, accurate response about financial assistance programs in Houston/Harris County. 
If you recommend specific programs, make sure they are from the Houston/Harris County area.
Keep your response concise but informative.

Format your response focusing on practical help and next steps.
"""

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        if response and response.text:
            # Parse the AI response and combine with local data sources
            ai_answer = response.text.strip()
            sources = extract_relevant_sources(question, houston_data or get_default_houston_sources())
            
            return {
                "answer": ai_answer,
                "sources": sources
            }
        else:
            return generate_mock_response(question)
            
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        # Fallback to mock response on error
        return generate_mock_response(question)

def build_houston_context(houston_data: List[Dict] = None) -> str:
    """Build context string from Houston assistance program data"""
    if not houston_data:
        houston_data = get_default_houston_sources()
    
    context_parts = []
    for program in houston_data:
        context_part = f"- {program.get('name', 'Unknown Program')}: {program.get('why', 'Financial assistance program')}"
        if program.get('eligibility'):
            context_part += f" (Eligibility: {program['eligibility']})"
        context_parts.append(context_part)
    
    return "\n".join(context_parts)

def extract_relevant_sources(question: str, all_sources: List[Dict]) -> List[Dict]:
    """Extract sources relevant to the user's question"""
    question_lower = question.lower()
    relevant_sources = []
    
    # Simple keyword matching for now - in production, this could use embeddings
    for source in all_sources:
        source_text = f"{source.get('name', '')} {source.get('why', '')}".lower()
        
        # Check for relevant keywords
        if any(keyword in question_lower for keyword in ['rent', 'housing']) and \
           any(keyword in source_text for keyword in ['rent', 'housing', 'shelter']):
            relevant_sources.append(source)
        elif any(keyword in question_lower for keyword in ['utility', 'electric', 'water', 'gas']) and \
             any(keyword in source_text for keyword in ['utility', 'electric', 'water', 'gas', 'bill']):
            relevant_sources.append(source)
        elif any(keyword in question_lower for keyword in ['food', 'snap', 'hungry']) and \
             any(keyword in source_text for keyword in ['food', 'snap', 'meal', 'nutrition']):
            relevant_sources.append(source)
        elif any(keyword in question_lower for keyword in ['home', 'buy', 'purchase', 'mortgage']) and \
             any(keyword in source_text for keyword in ['home', 'buy', 'mortgage', 'purchase']):
            relevant_sources.append(source)
    
    # If no specific matches, return a few general ones
    if not relevant_sources:
        relevant_sources = all_sources[:3]
    
    return relevant_sources[:5]  # Limit to 5 sources

def get_default_houston_sources() -> List[Dict]:
    """Get default Houston financial assistance sources"""
    return [
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
        },
        {
            "name": "CenterPoint Energy - Utility Assistance",
            "why": "Helps with electric bill payment assistance and weatherization",
            "url": "https://www.centerpointenergy.com/",
            "phone": "(713) 207-2222",
            "eligibility": "Low-income households behind on electric bills",
            "county": "Harris County",
            "last_verified": "2025-01-15"
        },
        {
            "name": "Houston Food Bank",
            "why": "Largest food distribution organization in Houston",
            "url": "https://www.houstonfoodbank.org/",
            "phone": "(713) 223-3700",
            "eligibility": "Open to all community members in need",
            "county": "Harris County",
            "last_verified": "2025-01-15"
        },
        {
            "name": "Houston First-Time Homebuyer Program",
            "why": "Down payment assistance for first-time homebuyers",
            "url": "https://houstontx.gov/",
            "phone": "(832) 394-6200",
            "eligibility": "First-time homebuyers meeting income requirements",
            "county": "Harris County",
            "last_verified": "2025-01-15"
        },
        {
            "name": "CenterPoint Energy Bill Help Plus",
            "why": "Utility assistance program for electricity and gas bills",
            "url": "https://www.centerpointenergy.com/",
            "phone": "(713) 207-2222",
            "eligibility": "Low-income households facing energy hardship",
            "county": "Harris County",
            "last_verified": "2025-01-15"
        },
        {
            "name": "Harris County Community Services - Utility Assistance",
            "why": "Emergency assistance for utility bills including water, electric, and gas",
            "url": "https://csd.harriscountytx.gov/",
            "phone": "(832) 927-4400",
            "eligibility": "Harris County residents with income at or below 150% of federal poverty level",
            "county": "Harris County",
            "last_verified": "2025-01-15"
        },
        {
            "name": "Houston Food Bank Emergency Food",
            "why": "Food assistance and nutrition programs for individuals and families",
            "url": "https://www.houstonfoodbank.org/",
            "phone": "(713) 223-3700",
            "eligibility": "Open to all in need, no income verification required",
            "county": "Harris County",
            "last_verified": "2025-01-15"
        },
        {
            "name": "Coalition for the Homeless - Emergency Shelter",
            "why": "Emergency shelter and transitional housing services",
            "url": "https://www.homelesshouston.org/",
            "phone": "(713) 739-7514",
            "eligibility": "Individuals and families experiencing homelessness",
            "county": "Harris County",
            "last_verified": "2025-01-15"
        }
    ]

def generate_mock_response(question: str) -> Dict:
    """Generate mock response when Gemini is not available"""
    question_lower = question.lower()
    sources = get_default_houston_sources()
    
    if "rent" in question_lower or "housing" in question_lower:
        answer = """I found several **rental assistance programs** in Houston/Harris County:

- **Houston Housing Authority** offers ongoing rental assistance for qualified low-income families
- **Harris County** provides emergency rental assistance  

Both programs have income requirements and application processes. Here are your next steps:

1. Check your eligibility based on income requirements
2. Gather required documentation
3. Submit your application online or in person"""
        relevant_sources = [s for s in sources if 'housing' in s['name'].lower() or 'rental' in s['name'].lower()]
    elif "utility" in question_lower or "electric" in question_lower or "water" in question_lower:
        answer = """For **utility assistance** in Houston, here are your options:

- **CenterPoint Energy** offers payment assistance programs for low-income households
- **Weatherization programs** available to help reduce energy costs long-term

*Contact them directly* to learn about eligibility requirements."""
        relevant_sources = [s for s in sources if 'utility' in s['name'].lower() or 'energy' in s['name'].lower()]
    elif "food" in question_lower or "snap" in question_lower:
        answer = """# Food Assistance Programs

The **Houston Food Bank** is the largest food distribution organization in the area and provides food assistance to community members in need. 

They have multiple distribution sites throughout Harris County:

- Mobile food pantries
- Partner agencies
- Direct distribution centers"""
        relevant_sources = [s for s in sources if 'food' in s['name'].lower()]
    else:
        answer = """I can help you find information about:

- **Rental assistance** programs
- **Utility** payment help  
- **Food assistance** and SNAP
- **Homebuyer aid** programs

*Could you be more specific about what type of help you need?*"""
        relevant_sources = sources[:3]
    
    return {
        "answer": answer,
        "sources": relevant_sources
    }