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

def generate_financial_assistance_response(question: str, houston_data: List[Dict] = None, user_context: Dict = None) -> Dict:
    """
    Generate AI response for financial assistance questions using Gemini
    
    Args:
        question: User's question about financial assistance
        houston_data: Optional list of Houston financial assistance programs
        user_context: Optional user context including location, household size, etc.
    
    Returns:
        Dict with 'answer' and 'sources' keys
    """
    try:
        if not configure_gemini():
            # Fallback to mock response if Gemini not available
            return generate_mock_response(question, user_context)
        
        # Build context with Houston financial assistance data
        context = build_houston_context(houston_data)
        
        # Build enhanced user context
        user_context_str = build_user_context_string(user_context or {})
        
        # Create the enhanced prompt
        prompt = f"""
You are a helpful financial assistant specializing in Houston/Harris County financial assistance programs. 

Context about available programs:
{context}

User Context:
{user_context_str}

User Question: {question}

Please provide a helpful, accurate response about financial assistance programs in Houston/Harris County. 
If you recommend specific programs, make sure they are from the Houston/Harris County area.
Keep your response concise but informative.

Consider the user's context when making recommendations and be specific about next steps.
Format your response focusing on practical help and actionable next steps.
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
            return generate_mock_response(question, user_context)
            
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        # Fallback to mock response on error
        return generate_mock_response(question, user_context)

def build_user_context_string(user_context: Dict) -> str:
    """Build user context string for prompts"""
    context_parts = []
    
    if user_context.get("user_location"):
        context_parts.append(f"Location: {user_context['user_location']}")
    
    if user_context.get("household_size"):
        context_parts.append(f"Household size: {user_context['household_size']}")
    
    if user_context.get("income_range"):
        context_parts.append(f"Income range: {user_context['income_range']}")
    
    if user_context.get("urgency_level"):
        context_parts.append(f"Urgency level: {user_context['urgency_level']}")
    
    if user_context.get("previous_assistance"):
        context_parts.append(f"Previous assistance: {', '.join(user_context['previous_assistance'])}")
    
    if user_context.get("conversation_summary"):
        context_parts.append(f"Previous conversation: {user_context['conversation_summary']}")
    
    return "; ".join(context_parts) if context_parts else "No specific user context provided"
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

def generate_mock_response(question: str, user_context: Dict = None) -> Dict:
    """Generate mock response when Gemini is not available"""
    question_lower = question.lower()
    sources = get_default_houston_sources()
    user_context = user_context or {}
    
    # Enhanced intent-based responses
    if "rent" in question_lower or "housing" in question_lower:
        answer = f"""I found several **rental assistance programs** in Houston/Harris County:

- **Houston Housing Authority** offers ongoing rental assistance for qualified low-income families
- **Harris County Emergency Rental Assistance** provides emergency rental assistance  

{_get_personalized_advice("housing", user_context)}

**Next Steps:**
1. Check your eligibility based on income requirements
2. Gather required documentation (ID, proof of income, lease)
3. Submit your application online or in person
4. Contact programs directly for fastest processing"""
        relevant_sources = [s for s in sources if 'housing' in s['name'].lower() or 'rental' in s['name'].lower()]
        
    elif "utility" in question_lower or "electric" in question_lower or "water" in question_lower:
        answer = f"""For **utility assistance** in Houston, here are your options:

- **CenterPoint Energy Bill Help Plus** offers payment assistance programs for low-income households
- **Harris County Community Services** provides emergency utility assistance
- **Weatherization programs** available to help reduce energy costs long-term

{_get_personalized_advice("utilities", user_context)}

**Next Steps:**
1. Contact CenterPoint Energy at (713) 207-2222
2. Call Harris County Community Services at (832) 927-4400
3. Have your recent utility bills ready when calling"""
        relevant_sources = [s for s in sources if 'utility' in s['name'].lower() or 'energy' in s['name'].lower()]
        
    elif "food" in question_lower or "snap" in question_lower:
        answer = f"""**Food Assistance Programs** in Houston:

The **Houston Food Bank** is the largest food distribution organization in the area and provides food assistance to community members in need.

{_get_personalized_advice("food", user_context)}

**Available Services:**
- Mobile food pantries
- Partner agencies throughout Harris County
- Direct distribution centers
- SNAP application assistance

**Next Steps:**
1. Call Houston Food Bank at (713) 223-3700
2. Visit their website to find the nearest distribution site
3. No income verification required for emergency food"""
        relevant_sources = [s for s in sources if 'food' in s['name'].lower()]
        
    else:
        answer = f"""I can help you find information about financial assistance in Houston/Harris County:

- **Rental assistance** programs
- **Utility** payment help  
- **Food assistance** and SNAP
- **Homebuyer aid** programs

{_get_personalized_advice("general", user_context)}

**To get more specific help:**
*Could you be more specific about what type of assistance you need?*"""
        relevant_sources = sources[:3]
    
    return {
        "answer": answer,
        "sources": relevant_sources
    }

def _get_personalized_advice(assistance_type: str, user_context: Dict) -> str:
    """Generate personalized advice based on user context"""
    advice_parts = []
    
    # Urgency-based advice
    if user_context.get("urgency_level") == "high":
        advice_parts.append("⚠️ **For urgent situations**: Call 211 immediately for emergency assistance referrals.")
    
    # Household size considerations
    household_size = user_context.get("household_size")
    if household_size:
        if int(household_size) > 4:
            advice_parts.append(f"💡 **Large household tip**: With {household_size} household members, you may qualify for higher assistance amounts.")
        elif int(household_size) == 1:
            advice_parts.append("💡 **Single person tip**: Some programs have special provisions for single-person households.")
    
    # Previous assistance considerations
    if user_context.get("previous_assistance"):
        advice_parts.append("📋 **Previous assistance**: Mention your previous applications when contacting new programs - this can help speed up the process.")
    
    # Income range considerations
    income_range = user_context.get("income_range")
    if income_range and "low" in income_range.lower():
        advice_parts.append("✅ **Income eligibility**: Based on your income range, you likely qualify for most assistance programs.")
    
    return "\n".join(advice_parts) if advice_parts else ""