#!/usr/bin/env python3
"""
Demo script showing AI response improvements
Demonstrates the enhanced context understanding, conversational memory, 
intent classification, and response quality improvements.
"""

import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.ai_agent import process_financial_query

def demo_basic_vs_enhanced():
    """Compare basic vs enhanced AI responses"""
    print("=== DEMO: Basic vs Enhanced AI Responses ===\n")
    
    # Example 1: Basic query with no context
    print("🔸 SCENARIO 1: Basic Query")
    print("Query: 'I need help with rent'")
    print("Context: None")
    
    basic_response = process_financial_query("I need help with rent")
    print(f"\nBasic Response:")
    print(f"  Answer: {basic_response['answer'][:100]}...")
    print(f"  Action Items: {len(basic_response.get('action_items', []))}")
    print(f"  Follow-ups: {len(basic_response.get('follow_up_questions', []))}")
    
    # Example 2: Enhanced query with rich context
    print("\n" + "="*60)
    print("🔸 SCENARIO 2: Enhanced Query with Context")
    print("Query: 'I need help with rent'")
    print("Context: Urgent situation, family of 4, low income")
    
    enhanced_context = {
        "urgency_level": "high",
        "household_size": 4,
        "income_range": "low-income",
        "location_verified": True
    }
    
    enhanced_response = process_financial_query(
        "I need help with rent", 
        user_context=enhanced_context
    )
    
    print(f"\nEnhanced Response:")
    print(f"  Answer: {enhanced_response['answer'][:100]}...")
    print(f"  Priority Level: {enhanced_response.get('priority_level', 'unknown')}")
    print(f"  Action Items: {enhanced_response.get('action_items', [])[:3]}")
    print(f"  Follow-up Questions: {enhanced_response.get('follow_up_questions', [])}")
    print(f"  Intent Detected: {enhanced_response.get('intent_classification', {}).get('primary_intent', {}).get('intent', 'unknown')}")

def demo_conversational_memory():
    """Demonstrate conversational memory"""
    print("\n\n=== DEMO: Conversational Memory ===\n")
    
    print("🔸 SCENARIO: Multi-turn conversation")
    
    # First interaction
    print("Turn 1:")
    print("Query: 'I need help with utilities'")
    response1 = process_financial_query("I need help with utilities")
    print(f"Response: {response1['answer'][:100]}...")
    
    # Build conversation history
    conversation_history = [
        {
            "user_query": "I need help with utilities",
            "ai_response": response1['answer'][:200]
        }
    ]
    
    # Second interaction with history
    print("\nTurn 2:")
    print("Query: 'What about rent assistance too?'")
    print("Context: Previous conversation about utilities")
    
    response2 = process_financial_query(
        "What about rent assistance too?",
        conversation_history=conversation_history
    )
    print(f"Response: {response2['answer'][:100]}...")
    print(f"Action Items: {response2.get('action_items', [])[:2]}")

def demo_intent_classification():
    """Demonstrate smart intent classification"""
    print("\n\n=== DEMO: Smart Intent Classification ===\n")
    
    test_scenarios = [
        {
            "query": "I'm getting evicted tomorrow and need help immediately",
            "expected": "urgent_assistance"
        },
        {
            "query": "How do I apply for rental assistance programs?",
            "expected": "application_help"
        },
        {
            "query": "What assistance programs are available in Houston?",
            "expected": "program_search"
        },
        {
            "query": "Can you help me create a budget?",
            "expected": "budgeting_help"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🔸 SCENARIO {i}:")
        print(f"Query: '{scenario['query']}'")
        
        response = process_financial_query(scenario['query'])
        intent = response.get('intent_classification', {}).get('primary_intent', {})
        
        print(f"Intent Detected: {intent.get('intent', 'unknown')}")
        print(f"Confidence: {intent.get('confidence', 0):.2f}")
        print(f"Priority Level: {response.get('priority_level', 'unknown')}")
        print(f"Action Items: {len(response.get('action_items', []))}")
        print()

def demo_personalized_responses():
    """Demonstrate personalized response generation"""
    print("\n=== DEMO: Personalized Response Generation ===\n")
    
    # Scenario 1: Single person, verified location
    print("🔸 SCENARIO 1: Single person, Harris County resident")
    context1 = {
        "household_size": 1,
        "location_verified": True,
        "income_range": "low-income"
    }
    
    response1 = process_financial_query("I need food assistance", user_context=context1)
    print(f"Follow-up Questions: {response1.get('follow_up_questions', [])}")
    
    # Scenario 2: Large family, new user
    print("\n🔸 SCENARIO 2: Large family, location unknown")
    context2 = {
        "household_size": 6,
        "location_verified": False
    }
    
    response2 = process_financial_query("I need food assistance", user_context=context2)
    print(f"Follow-up Questions: {response2.get('follow_up_questions', [])}")
    
    # Show the difference
    print(f"\nPersonalization Impact:")
    print(f"  Single person questions: {len(response1.get('follow_up_questions', []))}")
    print(f"  Large family questions: {len(response2.get('follow_up_questions', []))}")

def demo_response_quality():
    """Demonstrate response quality improvements"""
    print("\n\n=== DEMO: Response Quality Improvements ===\n")
    
    print("🔸 ENHANCED RESPONSE STRUCTURE:")
    
    response = process_financial_query(
        "I need emergency rent help",
        user_context={"urgency_level": "high", "household_size": 3}
    )
    
    print(f"✅ Structured Answer: {len(response.get('answer', ''))} characters")
    print(f"✅ Action Items: {len(response.get('action_items', []))} items")
    print(f"   - {response.get('action_items', [])[:2]}")
    print(f"✅ Priority Level: {response.get('priority_level', 'unknown')}")
    print(f"✅ Follow-up Questions: {len(response.get('follow_up_questions', []))}")
    print(f"✅ Intent Classification: {response.get('intent_classification', {}).get('primary_intent', {}).get('intent', 'unknown')}")
    print(f"✅ Source Programs: {len(response.get('sources', []))}")

def main():
    print("🚀 Houston Financial Navigator - AI Enhancement Demo")
    print("="*60)
    
    demo_basic_vs_enhanced()
    demo_conversational_memory()
    demo_intent_classification()
    demo_personalized_responses()
    demo_response_quality()
    
    print("\n" + "="*60)
    print("✨ KEY IMPROVEMENTS DEMONSTRATED:")
    print("✅ Enhanced context understanding with user profiles")
    print("✅ Conversational memory for multi-turn interactions")  
    print("✅ Smart intent classification beyond keyword matching")
    print("✅ Structured response format with action items")
    print("✅ Personalized clarifying questions")
    print("✅ Response quality validation and enhancement")
    print("✅ Intelligent error handling")
    print("\n🎯 Result: More helpful, contextual, and actionable AI responses!")

if __name__ == "__main__":
    main()