# utils/gemini_ai.py
import os
import json
from typing import List, Dict

import google.generativeai as genai
import numpy as np

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
    """Generate AI response for financial assistance questions using Gemini.

    Returns a dictionary containing both a plain text summary (``answer``) for
    backward compatibility and a ``structured`` field with rich data for the UI
    (title, summary and actionable steps).
    """
    try:
        if not configure_gemini():
            # Fallback to mock response if Gemini not available
            return generate_mock_response(question, user_context)

        # Handle non-financial queries without calling the API
        from .ai_agent import HoustonFinancialAgent
        agent = HoustonFinancialAgent()
        intent = agent.classify_intent(question)["primary_intent"]["intent"]
        if intent == "non_financial":
            return generate_mock_response(question, user_context)

        # Build context with Houston financial assistance data
        context = build_houston_context(houston_data)
        
        # Build enhanced user context
        user_context_str = build_user_context_string(user_context or {})
        
        # Create the enhanced prompt expecting JSON output
        prompt = f"""
You are a helpful financial assistant specializing in Houston/Harris County financial assistance programs.

Context about available programs:
{context}

User Context:
{user_context_str}

User Question: {question}

Respond ONLY in valid JSON with the following structure:
{{
  "title": "short response title",
  "summary": "3-5 sentence summary with actionable tone",
  "actionable_steps": ["short imperative step", "additional step"],
  "sources": []
}}
Do not add any additional text outside the JSON.
"""

        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)

        if response and response.text:
            raw_text = response.text.strip()
            try:
                parsed = json.loads(raw_text)
            except json.JSONDecodeError:
                parsed = {
                    "title": "Financial Assistance Information",
                    "summary": raw_text,
                    "actionable_steps": [],
                    "sources": []
                }

            sources = extract_relevant_sources(
                question, houston_data or get_default_houston_sources()
            )
            structured = {
                "title": parsed.get("title", ""),
                "summary": parsed.get("summary", raw_text),
                "actionable_steps": parsed.get("actionable_steps", []),
                "sources": sources,
            }

            return {
                "answer": structured["summary"],
                "structured": structured,
                "sources": sources,
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


def build_houston_context(houston_data: List[Dict]) -> str:
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
    """Extract sources relevant to the user's question using semantic search."""
    try:
        query_embedding = genai.embed_content(
            model="models/embedding-001", content=question
        )["embedding"]

        source_embeddings = []
        for src in all_sources:
            text = f"{src.get('name', '')} {src.get('why', '')}"
            embedding = genai.embed_content(
                model="models/embedding-001", content=text
            )["embedding"]
            source_embeddings.append(embedding)

        similarities = []
        q = np.array(query_embedding)
        q_norm = np.linalg.norm(q)
        for emb, src in zip(source_embeddings, all_sources):
            e = np.array(emb)
            sim = float(np.dot(q, e) / (q_norm * np.linalg.norm(e)))
            similarities.append((sim, src))

        similarities.sort(key=lambda x: x[0], reverse=True)
        ranked = [s for _, s in similarities]
        return ranked[:5]
    except Exception:
        # Fallback to simple keyword matching
        question_lower = question.lower()
        relevant_sources = []

        for source in all_sources:
            source_text = f"{source.get('name', '')} {source.get('why', '')}".lower()
            if any(k in question_lower for k in ['rent', 'housing']) and \
               any(k in source_text for k in ['rent', 'housing', 'shelter']):
                relevant_sources.append(source)
            elif any(k in question_lower for k in ['utility', 'electric', 'water', 'gas']) and \
                 any(k in source_text for k in ['utility', 'electric', 'water', 'gas', 'bill']):
                relevant_sources.append(source)
            elif any(k in question_lower for k in ['food', 'snap', 'hungry']) and \
                 any(k in source_text for k in ['food', 'snap', 'meal', 'nutrition']):
                relevant_sources.append(source)
            elif any(k in question_lower for k in ['home', 'buy', 'purchase', 'mortgage']) and \
                 any(k in source_text for k in ['home', 'buy', 'mortgage', 'purchase']):
                relevant_sources.append(source)

        if not relevant_sources:
            relevant_sources = all_sources[:3]
        return relevant_sources[:5]

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
    from .ai_agent import HoustonFinancialAgent
    
    question_lower = question.lower()
    sources = get_default_houston_sources()
    user_context = user_context or {}
    
    # Use intent classification to determine response type
    agent = HoustonFinancialAgent()
    intent_result = agent.classify_intent(question)
    primary_intent = intent_result["primary_intent"]["intent"]
    
    # Handle non-financial queries
    if primary_intent == "non_financial":
        answer = """I'm a financial assistance chatbot focused on helping Houston residents find financial aid programs. I can't provide information about time, weather, or general topics.

**I can help you with:**
- Rental and housing assistance
- Utility bill payment help
- Food assistance programs
- Emergency financial aid
- Budgeting and financial planning

*How can I assist you with your financial needs today?*"""
        structured = {
            "title": "Financial Assistance Focus",
            "summary": answer,
            "actionable_steps": [],
            "sources": []
        }
        return {
            "answer": structured["summary"],
            "structured": structured,
            "sources": []
        }
    
    # Handle budgeting help requests
    elif primary_intent == "budgeting_help":
        answer = f"""**Houston Financial Budgeting Tips & Resources:**

**📊 Essential Budgeting Steps:**
1. **Track your income and expenses** for at least one month
2. **Use the 50/30/20 rule**: 50% needs, 30% wants, 20% savings/debt
3. **Prioritize fixed expenses**: rent, utilities, insurance, minimum debt payments
4. **Build an emergency fund** even if it's just $25/month to start

**💡 Houston-Specific Money-Saving Tips:**
- Use **Metro LIFT** programs for reduced transit costs if you qualify
- Apply for **LIHEAP** (Low Income Home Energy Assistance) to reduce utility costs
- Visit **Houston Food Bank** locations to reduce grocery expenses
- Check **Harris County** property tax exemptions you might qualify for

**🛠 Free Budgeting Resources:**
- **United Way of Greater Houston** offers free financial counseling
- **Harris County Community Services** provides financial education classes
- **Houston Public Library** has free financial literacy workshops

{_get_personalized_advice("budgeting", user_context)}

**Next Steps:**
1. Download a free budgeting app or use a simple spreadsheet
2. Contact United Way at 211 for free financial counseling
3. Look into assistance programs if your budget shows shortfalls"""
        
        relevant_sources = [s for s in sources if any(keyword in s['name'].lower() for keyword in ['community', 'counseling', 'assistance'])][:3]
        structured = {
            "title": "Budgeting Help",
            "summary": answer,
            "actionable_steps": [],
            "sources": relevant_sources
        }
        return {
            "answer": structured["summary"],
            "structured": structured,
            "sources": relevant_sources
        }
    
    # Enhanced intent-based responses for financial assistance
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

    structured = {
        "title": "Financial Assistance Information",
        "summary": answer,
        "actionable_steps": [],
        "sources": relevant_sources
    }
    return {
        "answer": structured["summary"],
        "structured": structured,
        "sources": relevant_sources
    }

def _get_personalized_advice(assistance_type: str, user_context: Dict) -> str:
    """Generate personalized advice based on user context"""
    advice_parts = []
    
    # Budgeting-specific advice
    if assistance_type == "budgeting":
        household_size = user_context.get("household_size")
        if household_size:
            if int(household_size) > 4:
                advice_parts.append(f"💡 **Large household budget tip**: With {household_size} people, consider bulk buying and meal planning to save 15-20% on groceries.")
            elif int(household_size) == 1:
                advice_parts.append("💡 **Single person budget tip**: Focus on preventing lifestyle inflation and automate savings even if small amounts.")
        
        income_range = user_context.get("income_range")
        if income_range and "low" in income_range.lower():
            advice_parts.append("✅ **Low income budgeting**: Prioritize basic needs and look into assistance programs to free up money for savings.")
        
        return "\n".join(advice_parts) if advice_parts else ""
    
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