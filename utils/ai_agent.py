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
    
    def _clarify_intent(self, user_query: str) -> str:
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
    
    def process_query(self, query: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a user query using the agent or fallback to basic AI"""
        try:
            if self.initialized and self.agent_executor:
                # Use the advanced agent
                logger.info("Processing query with LangChain agent")
                response = self.agent_executor.invoke({"input": query})
                
                return {
                    "answer": response.get("output", ""),
                    "sources": self._extract_sources_from_response(response),
                    "provider": "langchain-agent",
                    "agent_used": True
                }
            else:
                # Fallback to existing Gemini AI
                logger.info("Falling back to basic Gemini AI")
                return self._fallback_response(query, user_context)
                
        except Exception as e:
            logger.error(f"Error processing query with agent: {e}")
            return self._fallback_response(query, user_context)
    
    def _fallback_response(self, query: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Fallback to existing AI implementation"""
        response = generate_financial_assistance_response(query)
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
def process_financial_query(query: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
    """Process a financial assistance query using the AI agent"""
    agent = get_houston_agent()
    return agent.process_query(query, user_context)