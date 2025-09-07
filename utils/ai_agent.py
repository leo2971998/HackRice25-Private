# utils/ai_agent.py
"""
Advanced AI Agent for Houston Financial Navigator
Implements LangChain-based agent with tools and semantic search
"""

import os
import logging
from typing import List, Dict, Optional, Any
from functools import lru_cache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import LangChain components with fallback
try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain.tools import Tool
    from langchain.memory import ConversationBufferMemory
    from langchain.schema import BaseMessage
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
    logger.info("LangChain dependencies loaded successfully")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    logger.warning(f"LangChain not available: {e}")
    
    # Create dummy classes for type hints when LangChain is not available
    class Tool:
        def __init__(self, name, description, func):
            self.name = name
            self.description = description
            self.func = func

# Import sklearn for simple semantic similarity
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("Sklearn not available for semantic search")

# Fallback imports
from .gemini_ai import generate_financial_assistance_response, get_default_houston_sources


class HoustonFinancialAgent:
    """Advanced AI agent for Houston financial assistance with semantic search and tools"""
    
    def __init__(self):
        self.agent = None
        self.vectorizer = None
        self.document_vectors = None
        self.documents = []
        self.memory = None
        self.initialized = False
        
        # Always initialize semantic search (doesn't require API keys)
        self._initialize_semantic_search()
        
        # Try to initialize agent components
        if LANGCHAIN_AVAILABLE:
            self._initialize_agent()
    
    def _initialize_agent(self) -> bool:
        """Initialize the LangChain agent with tools and memory"""
        try:
            # Check for API key
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.warning("GEMINI_API_KEY not found, agent initialization skipped")
                return False
            
            # Initialize LLM
            llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=api_key,
                temperature=0.3
            )
            
            # Initialize memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
            
            # Create tools
            tools = self._create_tools()
            
            # Create agent
            self.agent = create_openai_tools_agent(
                llm=llm,
                tools=tools,
                prompt=self._get_agent_prompt()
            )
            
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=tools,
                memory=self.memory,
                verbose=True,
                handle_parsing_errors=True
            )
            
            self.initialized = True
            logger.info("Houston Financial Agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            return False
    
    def _initialize_semantic_search(self):
        """Initialize simple semantic search with TF-IDF"""
        try:
            # Get Houston sources and convert to documents
            sources = get_default_houston_sources()
            self.documents = []
            texts = []
            
            for source in sources:
                # Create document content
                content = f"""
                Program: {source.get('name', '')}
                Description: {source.get('why', '')}
                Eligibility: {source.get('eligibility', '')}
                Phone: {source.get('phone', '')}
                County: {source.get('county', '')}
                """
                
                doc_data = {
                    'content': content.strip(),
                    'metadata': {
                        'name': source.get('name', ''),
                        'url': source.get('url', ''),
                        'phone': source.get('phone', ''),
                        'type': 'financial_assistance'
                    }
                }
                self.documents.append(doc_data)
                texts.append(content.strip())
            
            # Initialize TF-IDF vectorizer if sklearn is available
            if SKLEARN_AVAILABLE:
                self.vectorizer = TfidfVectorizer(
                    stop_words='english',
                    max_features=1000,
                    ngram_range=(1, 2)
                )
                self.document_vectors = self.vectorizer.fit_transform(texts)
                logger.info(f"Semantic search initialized with {len(texts)} documents")
            else:
                logger.info("Semantic search using keyword fallback")
            
        except Exception as e:
            logger.error(f"Failed to initialize semantic search: {e}")
            self.vectorizer = None
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent"""
        tools = []
        
        # Semantic search tool
        tools.append(Tool(
            name="search_houston_resources",
            description="Search for relevant Houston/Harris County financial assistance programs based on user needs",
            func=self._search_houston_resources
        ))
        
        # Budgeting advice tool
        tools.append(Tool(
            name="budgeting_advice",
            description="Provide budgeting advice and financial planning guidance",
            func=self._provide_budgeting_advice
        ))
        
        # Intent clarification tool  
        tools.append(Tool(
            name="clarify_intent",
            description="Ask clarifying questions to better understand user's specific financial needs",
            func=self._clarify_intent
        ))
        
        return tools
    
    def _search_houston_resources(self, query: str) -> str:
        """Search for relevant Houston financial resources using semantic search"""
        try:
            if self.vectorizer is not None and self.document_vectors is not None and SKLEARN_AVAILABLE:
                # Use TF-IDF semantic search
                query_vector = self.vectorizer.transform([query])
                similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
                
                # Get top 3 most similar documents
                top_indices = np.argsort(similarities)[::-1][:3]
                
                if len(top_indices) == 0 or similarities[top_indices[0]] < 0.1:
                    return "No highly relevant Houston financial assistance programs found for your specific query"
                
                # Format results
                response = "I found these relevant Houston financial assistance programs:\n\n"
                for i, idx in enumerate(top_indices, 1):
                    if similarities[idx] > 0.1:  # Only include reasonably relevant results
                        doc = self.documents[idx]
                        response += f"{i}. {doc['metadata'].get('name', 'Program')}\n"
                        response += f"   {doc['content'][:200]}...\n"
                        if doc['metadata'].get('phone'):
                            response += f"   Phone: {doc['metadata']['phone']}\n"
                        response += f"   Relevance: {similarities[idx]:.2f}\n\n"
                
                return response
                
            else:
                # Fallback to keyword search
                return self._keyword_search_fallback(query)
                
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return "Error searching resources, please try again"
    
    def _keyword_search_fallback(self, query: str) -> str:
        """Fallback keyword search when semantic search is not available"""
        query_lower = query.lower()
        relevant_docs = []
        
        for doc in self.documents:
            content_lower = doc['content'].lower()
            
            # Simple keyword matching
            keywords_found = 0
            query_words = query_lower.split()
            
            for word in query_words:
                if len(word) > 2 and word in content_lower:
                    keywords_found += 1
            
            if keywords_found > 0:
                relevant_docs.append((doc, keywords_found))
        
        # Sort by number of keyword matches
        relevant_docs.sort(key=lambda x: x[1], reverse=True)
        
        if not relevant_docs:
            return "No relevant Houston financial assistance programs found for your specific query"
        
        # Format results
        response = "I found these relevant Houston financial assistance programs:\n\n"
        for i, (doc, score) in enumerate(relevant_docs[:3], 1):
            response += f"{i}. {doc['metadata'].get('name', 'Program')}\n"
            response += f"   {doc['content'][:200]}...\n"
            if doc['metadata'].get('phone'):
                response += f"   Phone: {doc['metadata']['phone']}\n"
            response += "\n"
        
        return response
    
    def _provide_budgeting_advice(self, situation: str) -> str:
        """Provide budgeting advice based on user's financial situation"""
        advice = f"""
        Based on your situation: {situation}
        
        Here's some budgeting advice:
        
        1. **50/30/20 Rule**: Allocate 50% of income to needs, 30% to wants, 20% to savings
        2. **Track Expenses**: Monitor where your money goes for 1-2 months
        3. **Emergency Fund**: Aim for 3-6 months of expenses saved
        4. **Houston-Specific Tips**:
           - Look into Harris County utility assistance programs
           - Consider Houston Metro for affordable transportation
           - Check local food banks if grocery costs are high
        
        Would you like specific help with any particular area of your budget?
        """
        return advice.strip()
    
    def _build_enhanced_context(self, user_context: Optional[Dict] = None, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """Build enhanced context from user data and conversation history"""
        enhanced_context = {
            "user_location": "Harris County",  # Default to Harris County
            "household_size": None,
            "previous_assistance": [],
            "urgency_level": "normal",
            "location_verified": False,
            "income_range": None,
            "conversation_summary": ""
        }
        
        # Add user context if provided
        if user_context:
            enhanced_context.update({
                "user_location": user_context.get("location", "Harris County"),
                "household_size": user_context.get("household_size"),
                "previous_assistance": user_context.get("assistance_history", []),
                "location_verified": user_context.get("location_verified", False),
                "income_range": user_context.get("income_range")
            })
        
        # Add conversation context if provided
        if conversation_history:
            enhanced_context["conversation_summary"] = self._build_conversation_context(conversation_history)
            
        return enhanced_context
    
    def _build_conversation_context(self, conversation_history: List[Dict]) -> str:
        """Build context summary from previous interactions"""
        if not conversation_history:
            return ""
        
        context_parts = []
        for interaction in conversation_history[-3:]:  # Last 3 interactions
            if interaction.get("user_query"):
                context_parts.append(f"User asked: {interaction['user_query']}")
            if interaction.get("ai_response"):
                # Summarize AI response to key points
                response = interaction["ai_response"]
                if len(response) > 100:
                    response = response[:100] + "..."
                context_parts.append(f"AI responded: {response}")
        
        return " | ".join(context_parts)
    
    def classify_intent(self, question: str) -> Dict:
        """Classify user intent more sophisticatedly"""
        question_lower = question.lower()
        
        intents = {
            "non_financial": {
                "keywords": ["time", "date", "weather", "hello", "hi there", "good morning", "good afternoon", "how are you", "what's up", "what time", "current time", "clock", "day", "today's date"],
                "priority": "low"
            },
            "urgent_assistance": {
                "keywords": ["emergency", "eviction", "evicted", "shut off", "shutoff", "disconnect", "urgent", "immediately", "help now", "tomorrow", "today"],
                "priority": "high"
            },
            "program_search": {
                "keywords": ["help with", "assistance", "programs", "available", "find", "need help", "what programs", "options"],
                "priority": "medium"
            },
            "application_help": {
                "keywords": ["apply", "how to", "requirements", "documents", "process", "steps", "application"],
                "priority": "medium"
            },
            "follow_up": {
                "keywords": ["status", "application", "submitted", "waiting", "approved", "denied", "my application"],
                "priority": "medium"
            },
            "budgeting_help": {
                "keywords": ["budget", "budgeting", "money management", "financial planning", "expenses", "my budget", "financial tips", "budget tips", "save money", "spending"],
                "priority": "low"
            }
        }
        
        detected_intents = []
        for intent_name, intent_data in intents.items():
            # Count keyword matches, including partial matches
            matches = 0
            for keyword in intent_data["keywords"]:
                if keyword in question_lower:
                    matches += 1
                # Also check for word-level matches for better accuracy
                for word in question_lower.split():
                    if word in keyword.split():
                        matches += 0.5
            
            if matches > 0:
                confidence = min(matches / len(intent_data["keywords"]), 1.0)  # Cap at 1.0
                detected_intents.append({
                    "intent": intent_name,
                    "confidence": confidence,
                    "priority": intent_data["priority"]
                })
        
        # Sort by confidence
        detected_intents.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "primary_intent": detected_intents[0] if detected_intents else {"intent": "general_inquiry", "confidence": 0.0, "priority": "low"},
            "all_intents": detected_intents
        }
    
    def format_response(self, raw_response: Dict, query: str, context: Dict) -> Dict:
        """Format response with standardized structure"""
        intent_analysis = self.classify_intent(query)
        
        formatted_response = {
            "answer": raw_response.get("answer", ""),
            "sources": raw_response.get("sources", []),
            "provider": raw_response.get("provider", "unknown"),
            "agent_used": raw_response.get("agent_used", False),
            "action_items": self._extract_action_items(raw_response.get("answer", "")),
            "priority_level": intent_analysis["primary_intent"]["priority"],
            "follow_up_questions": self._generate_clarifying_questions(query, context),
            "intent_classification": intent_analysis
        }
        
        return formatted_response
    
    def _extract_action_items(self, answer: str) -> List[str]:
        """Extract actionable next steps from the response"""
        action_items = []
        
        # Look for numbered lists or bullet points
        import re
        
        # Find numbered steps (1. 2. 3. etc.)
        numbered_steps = re.findall(r'\d+\.\s*([^\n]+)', answer)
        action_items.extend(numbered_steps)
        
        # Find bullet points (- or • )
        bullet_points = re.findall(r'[-•]\s*([^\n]+)', answer)
        action_items.extend(bullet_points)
        
        # If no structured actions found, create general ones
        if not action_items:
            if "contact" in answer.lower() or "call" in answer.lower():
                action_items.append("Contact the recommended organizations directly")
            if "apply" in answer.lower() or "application" in answer.lower():
                action_items.append("Gather required documents for application")
            if "eligibility" in answer.lower():
                action_items.append("Check eligibility requirements")
        
        return action_items[:5]  # Limit to 5 action items
    
    def _generate_clarifying_questions(self, user_query: str, user_context: Dict = None) -> List[str]:
        """Generate personalized clarifying questions"""
        questions = []
        
        if not user_context:
            user_context = {}
        
        query_lower = user_query.lower()
        
        # Location verification
        if not user_context.get("location_verified"):
            questions.append("Are you located in Harris County, Texas?")
        
        # Income-related questions for financial assistance
        if any(keyword in query_lower for keyword in ["financial", "assistance", "help", "support"]) and not user_context.get("income_range"):
            questions.append("What's your approximate monthly household income range?")
        
        # Household size for program eligibility
        if not user_context.get("household_size") and any(keyword in query_lower for keyword in ["family", "household", "assistance"]):
            questions.append("How many people are in your household?")
        
        # Urgency assessment
        if any(keyword in query_lower for keyword in ["urgent", "emergency", "immediately", "eviction", "shut off"]):
            questions.append("Do you have any specific deadlines or urgent situations?")
        
        # Previous assistance history
        if not user_context.get("previous_assistance") and "assistance" in query_lower:
            questions.append("Have you received financial assistance before?")
        
        # Specific type of help
        if len(query_lower.split()) < 5:  # Short, vague queries
            questions.append("What specific type of financial assistance do you need? (rent, utilities, food, etc.)")
        
        return questions[:3]  # Limit to avoid overwhelming
    
    def validate_response(self, response: Dict) -> Dict:
        """Ensure response quality before returning"""
        answer = response.get("answer", "")
        
        # Enhance short responses
        if len(answer) < 50:
            response["answer"] = self._enhance_short_response(answer, response.get("sources", []))
        
        # Ensure sources are provided
        if not response.get("sources"):
            response["sources"] = get_default_houston_sources()[:3]
        
        # Add next steps if missing actionable content
        if not self._contains_actionable_steps(answer):
            response["answer"] += "\n\n" + self._add_next_steps(response.get("intent_classification", {}))
        
        return response
    
    def _enhance_short_response(self, answer: str, sources: List[Dict]) -> str:
        """Enhance short responses with additional helpful information"""
        if not answer or len(answer.strip()) < 20:
            answer = "I can help you find financial assistance resources in Houston/Harris County."
        
        enhanced = f"{answer}\n\nHere are some helpful resources:\n\n"
        
        for i, source in enumerate(sources[:2], 1):
            enhanced += f"{i}. **{source.get('name', 'Program')}**: {source.get('why', 'Financial assistance')}\n"
            if source.get('phone'):
                enhanced += f"   Phone: {source['phone']}\n"
            enhanced += "\n"
        
        return enhanced
    
    def _contains_actionable_steps(self, answer: str) -> bool:
        """Check if response contains actionable steps"""
        action_indicators = [
            "contact", "call", "apply", "visit", "go to", "submit", 
            "gather", "prepare", "check", "verify", "steps:", "next:"
        ]
        answer_lower = answer.lower()
        return any(indicator in answer_lower for indicator in action_indicators)
    
    def _add_next_steps(self, intent_classification: Dict) -> str:
        """Add general next steps based on intent"""
        primary_intent = intent_classification.get("primary_intent", {}).get("intent", "general_inquiry")
        
        if primary_intent == "urgent_assistance":
            return """**Immediate Next Steps:**
1. Call 211 for emergency assistance referrals
2. Contact Harris County Community Services at (832) 927-4400
3. Visit your local community center for emergency resources"""
        
        elif primary_intent == "program_search":
            return """**Next Steps:**
1. Review the programs listed above and their eligibility requirements
2. Contact the organizations directly using the phone numbers provided
3. Gather required documentation (ID, income proof, utility bills)"""
        
        elif primary_intent == "application_help":
            return """**Application Steps:**
1. Check eligibility requirements for each program
2. Gather required documents (ID, proof of income, utility bills)
3. Contact the organizations to start the application process"""
        
        else:
            return """**General Next Steps:**
1. Contact the recommended organizations for more information
2. Ask about eligibility requirements and application processes
3. Prepare necessary documentation in advance"""
    
    def _handle_ai_failure(self, question: str, error: Exception) -> Dict:
        """More intelligent error handling based on error type"""
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            # Quick resource list for timeout errors
            return {
                "answer": "I'm experiencing slow response times. Here are some quick resources while I recover:",
                "sources": get_default_houston_sources()[:3],
                "provider": "timeout-fallback",
                "action_items": ["Contact these organizations directly", "Try your request again in a few minutes"],
                "priority_level": "medium"
            }
        elif "rate" in error_str and "limit" in error_str:
            # Check for cached response
            return self._get_cached_response_if_available(question)
        else:
            # Emergency contact info for other errors
            return {
                "answer": """I'm having technical difficulties right now. For immediate assistance, please contact:

• **Harris County Community Services**: (832) 927-4400
• **Houston 311**: (713) 837-0311
• **211 Texas**: Dial 2-1-1 for emergency assistance referrals

I apologize for the inconvenience and recommend trying again later.""",
                "sources": get_default_houston_sources()[:2],
                "provider": "emergency-fallback",
                "action_items": ["Call the numbers above for immediate help", "Try again later"],
                "priority_level": "high"
            }
    
    def _get_cached_response_if_available(self, question: str) -> Dict:
        """Provide cached or simplified response for rate limiting"""
        # Simple implementation - could be enhanced with actual caching
        return {
            "answer": "I'm currently rate-limited but here are some general Houston financial assistance resources:",
            "sources": get_default_houston_sources()[:3],
            "provider": "rate-limit-fallback",
            "action_items": ["Contact these organizations directly", "Try your specific question again later"],
            "priority_level": "medium"
        }
        """Ask clarifying questions to better understand user needs"""
        clarifying_questions = """
        To help you better, could you please clarify:
        
        1. What specific type of financial assistance do you need? (rent, utilities, food, etc.)
        2. Are you a Harris County resident?
        3. What's your current household size?
        4. Do you have any specific urgent deadlines or situations?
        5. Have you applied for assistance programs before?
        
        The more details you can provide, the better I can help you find the right resources.
        """
        return clarifying_questions.strip()
    
    def _get_agent_prompt(self) -> str:
        """Get the system prompt for the agent"""
        return """You are a helpful AI assistant specializing in Houston/Harris County financial assistance programs.

Your role is to:
1. Help users find relevant financial assistance programs
2. Provide budgeting advice and financial planning guidance  
3. Ask clarifying questions when needed to better understand user needs
4. Connect users with appropriate local resources

You have access to tools for:
- Searching Houston financial assistance programs
- Providing budgeting advice
- Clarifying user intent

Always be empathetic, practical, and focused on actionable next steps. 
When recommending programs, include contact information when available.
"""
    
    def process_query(self, query: str, user_context: Optional[Dict] = None, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Process a user query using the agent or fallback to basic AI"""
        try:
            # Build enhanced context from user data and conversation history
            enhanced_context = self._build_enhanced_context(user_context, conversation_history)
            
            if self.initialized and self.agent_executor:
                # Use the advanced agent with enhanced context
                logger.info("Processing query with LangChain agent")
                agent_input = {
                    "input": query,
                    "context": enhanced_context
                }
                response = self.agent_executor.invoke(agent_input)
                
                raw_response = {
                    "answer": response.get("output", ""),
                    "sources": self._extract_sources_from_response(response),
                    "provider": "langchain-agent",
                    "agent_used": True
                }
            else:
                # Fallback to existing Gemini AI with enhanced context
                logger.info("Falling back to basic Gemini AI")
                raw_response = self._fallback_response(query, enhanced_context)
            
            # Apply response formatting and validation
            formatted_response = self.format_response(raw_response, query, enhanced_context)
            validated_response = self.validate_response(formatted_response)
            
            return validated_response
                
        except Exception as e:
            logger.error(f"Error processing query with agent: {e}")
            return self._handle_ai_failure(query, e)
    
    def _fallback_response(self, query: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Fallback to existing AI implementation"""
        response = generate_financial_assistance_response(query, user_context=user_context)
        response["provider"] = "fallback-gemini"
        response["agent_used"] = False
        return response
    
    def _extract_sources_from_response(self, response: Dict) -> List[Dict]:
        """Extract source information from agent response"""
        # For now, return default sources - could be enhanced to extract from agent response
        return get_default_houston_sources()[:3]


# Global agent instance
@lru_cache(maxsize=1)
def get_houston_agent() -> HoustonFinancialAgent:
    """Get or create the global Houston Financial Agent instance"""
    return HoustonFinancialAgent()


# Convenience function for external use
def process_financial_query(query: str, user_context: Optional[Dict] = None, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Process a financial assistance query using the AI agent"""
    agent = get_houston_agent()
    return agent.process_query(query, user_context, conversation_history)