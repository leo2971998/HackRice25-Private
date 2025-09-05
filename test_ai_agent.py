#!/usr/bin/env python3
"""
Test script for AI Agent functionality
Run this to verify the new LangChain-based agent system
"""

import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.ai_agent import get_houston_agent, process_financial_query

def test_agent_initialization():
    """Test agent initialization"""
    print("=== Testing AI Agent Initialization ===")
    
    try:
        agent = get_houston_agent()
        
        if agent.initialized:
            print("   ✅ LangChain agent initialized successfully")
            print(f"   ✅ Vector store available: {agent.vectorstore is not None}")
            print(f"   ✅ Embeddings available: {agent.embeddings is not None}")
        else:
            print("   ⚠️  Agent not fully initialized (likely missing API keys)")
            print("   ✅ Fallback mode available")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Agent initialization failed: {e}")
        return False

def test_query_processing():
    """Test query processing with different types of questions"""
    print("\n=== Testing Query Processing ===")
    
    test_queries = [
        "I need help with rent assistance in Houston",
        "Can you help me with budgeting?",
        "What financial assistance is available for utilities?",
        "I'm struggling with my budget, what should I do?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: '{query}'")
        
        try:
            response = process_financial_query(query)
            
            print(f"   Provider: {response.get('provider', 'unknown')}")
            print(f"   Agent used: {response.get('agent_used', False)}")
            print(f"   Answer length: {len(response.get('answer', ''))}")
            print(f"   Sources found: {len(response.get('sources', []))}")
            print(f"   Answer preview: {response.get('answer', '')[:100]}...")
            print("   ✅ Query processed successfully")
            
        except Exception as e:
            print(f"   ❌ Query processing failed: {e}")

def test_semantic_search():
    """Test semantic search functionality"""
    print("\n=== Testing Semantic Search ===")
    
    try:
        agent = get_houston_agent()
        
        if agent.vectorizer is not None:
            # Test semantic search directly
            search_result = agent._search_houston_resources("rental assistance")
            print(f"   ✅ Semantic search returned result: {len(search_result)} chars")
            print(f"   Sample result: {search_result[:100]}...")
        else:
            print("   ⚠️  TF-IDF vectorizer not available, using keyword fallback")
            # Test keyword fallback
            search_result = agent._search_houston_resources("rental assistance") 
            print(f"   ✅ Keyword fallback returned result: {len(search_result)} chars")
            
    except Exception as e:
        print(f"   ❌ Semantic search test failed: {e}")

def test_tools():
    """Test individual tools"""
    print("\n=== Testing Agent Tools ===")
    
    try:
        agent = get_houston_agent()
        
        if agent.initialized:
            # Test search tool
            search_result = agent._search_houston_resources("rent help")
            print(f"   ✅ Houston resources search: {len(search_result)} chars")
            
            # Test budgeting tool
            budget_advice = agent._provide_budgeting_advice("low income family")
            print(f"   ✅ Budgeting advice: {len(budget_advice)} chars")
            
            # Test clarification tool
            clarification = agent._clarify_intent("need help")
            print(f"   ✅ Intent clarification: {len(clarification)} chars")
        else:
            print("   ⚠️  Tools not available (agent not initialized)")
            
    except Exception as e:
        print(f"   ❌ Tools test failed: {e}")

def main():
    print("=== Houston Financial Navigator - AI Agent Test ===\n")
    
    # Test components
    test_agent_initialization()
    test_query_processing()
    test_semantic_search()
    test_tools()
    
    print("\n=== Test Complete ===")
    print("\nNote: If LangChain dependencies are not installed, the system will")
    print("gracefully fall back to the existing Gemini AI implementation.")

if __name__ == "__main__":
    main()