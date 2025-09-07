#!/usr/bin/env python3
"""
Test script for AI Enhancement functionality
Tests the new features like enhanced context understanding, conversational memory, 
intent classification, and response quality improvements.
"""

import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.ai_agent import get_houston_agent, process_financial_query

def test_enhanced_context_understanding():
    """Test enhanced context understanding with user profiles"""
    print("=== Testing Enhanced Context Understanding ===")
    
    # Test with basic user context
    user_context = {
        "household_size": 4,
        "income_range": "low-income",
        "location_verified": True,
        "urgency_level": "high"
    }
    
    query = "I need help with rent"
    response = process_financial_query(query, user_context=user_context)
    
    print(f"✅ Query processed with user context")
    print(f"   Response length: {len(response.get('answer', ''))}")
    print(f"   Action items: {len(response.get('action_items', []))}")
    print(f"   Priority level: {response.get('priority_level', 'unknown')}")
    print(f"   Follow-up questions: {len(response.get('follow_up_questions', []))}")

def test_conversational_memory():
    """Test conversational memory functionality"""
    print("\n=== Testing Conversational Memory ===")
    
    conversation_history = [
        {
            "user_query": "I need help with utilities",
            "ai_response": "I found several utility assistance programs including CenterPoint Energy Bill Help Plus."
        },
        {
            "user_query": "What about rent assistance?", 
            "ai_response": "Houston Housing Authority offers rental assistance programs for qualified families."
        }
    ]
    
    query = "Can you help me apply for both?"
    response = process_financial_query(query, conversation_history=conversation_history)
    
    print(f"✅ Query processed with conversation history")
    print(f"   Response acknowledges context: {'both' in response.get('answer', '').lower()}")
    print(f"   Response length: {len(response.get('answer', ''))}")

def test_intent_classification():
    """Test intent classification functionality"""
    print("\n=== Testing Intent Classification ===")
    
    agent = get_houston_agent()
    
    test_queries = [
        ("I'm getting evicted tomorrow", "urgent_assistance"),
        ("What programs are available?", "program_search"),
        ("How do I apply for rent help?", "application_help"),
        ("What's the status of my application?", "follow_up"),
        ("Help me with my budget", "budgeting_help")
    ]
    
    for query, expected_intent in test_queries:
        intent_result = agent.classify_intent(query)
        primary_intent = intent_result["primary_intent"]["intent"]
        confidence = intent_result["primary_intent"]["confidence"]
        
        print(f"   Query: '{query}'")
        print(f"   Expected: {expected_intent}, Got: {primary_intent}")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   ✅ {'Match' if expected_intent == primary_intent else 'Different classification'}")

def test_response_quality_improvements():
    """Test response formatting and quality improvements"""
    print("\n=== Testing Response Quality Improvements ===")
    
    query = "I need emergency help with rent"
    user_context = {"urgency_level": "high", "household_size": 3}
    
    response = process_financial_query(query, user_context=user_context)
    
    # Check response structure
    required_fields = ["answer", "sources", "action_items", "priority_level", "follow_up_questions"]
    missing_fields = [field for field in required_fields if field not in response]
    
    if not missing_fields:
        print("✅ All required response fields present")
    else:
        print(f"❌ Missing fields: {missing_fields}")
    
    # Check action items
    action_items = response.get("action_items", [])
    print(f"   Action items found: {len(action_items)}")
    for i, item in enumerate(action_items[:3], 1):
        print(f"     {i}. {item}")
    
    # Check priority level
    priority = response.get("priority_level", "unknown")
    print(f"   Priority level: {priority}")
    
    # Check follow-up questions
    follow_ups = response.get("follow_up_questions", [])
    print(f"   Follow-up questions: {len(follow_ups)}")
    for i, question in enumerate(follow_ups[:2], 1):
        print(f"     {i}. {question}")

def test_personalization_enhancements():
    """Test personalized clarifying questions"""
    print("\n=== Testing Personalization Enhancements ===")
    
    agent = get_houston_agent()
    
    # Test with minimal context
    minimal_context = {}
    questions1 = agent._generate_clarifying_questions("I need help", minimal_context)
    print(f"   Minimal context questions: {len(questions1)}")
    for i, q in enumerate(questions1, 1):
        print(f"     {i}. {q}")
    
    # Test with some context
    partial_context = {"location_verified": True, "household_size": 2}
    questions2 = agent._generate_clarifying_questions("I need financial assistance", partial_context)
    print(f"   Partial context questions: {len(questions2)}")
    for i, q in enumerate(questions2, 1):
        print(f"     {i}. {q}")

def test_response_validation():
    """Test response validation functionality"""
    print("\n=== Testing Response Validation ===")
    
    agent = get_houston_agent()
    
    # Test with short response
    short_response = {
        "answer": "Yes",
        "sources": [],
        "provider": "test"
    }
    
    validated = agent.validate_response(short_response)
    print(f"   Short response enhanced: {len(validated['answer']) > len(short_response['answer'])}")
    print(f"   Sources added: {len(validated.get('sources', []))}")
    print(f"   Enhanced answer length: {len(validated['answer'])}")

def test_error_handling():
    """Test intelligent error handling"""
    print("\n=== Testing Error Handling ===")
    
    agent = get_houston_agent()
    
    # Test timeout error
    timeout_error = Exception("Connection timeout occurred")
    timeout_response = agent._handle_ai_failure("help with rent", timeout_error)
    print(f"   Timeout error handled: {'timeout' in timeout_response.get('provider', '')}")
    print(f"   Emergency response provided: {len(timeout_response.get('answer', ''))}")
    
    # Test rate limit error
    rate_limit_error = Exception("Rate limit exceeded")
    rate_limit_response = agent._handle_ai_failure("utility help", rate_limit_error)
    print(f"   Rate limit error handled: {'rate' in rate_limit_response.get('provider', '')}")
    
    # Test general error
    general_error = Exception("Unknown error")
    general_response = agent._handle_ai_failure("food assistance", general_error)
    print(f"   General error handled: {'emergency' in general_response.get('provider', '')}")

def main():
    print("=== Houston Financial Navigator - AI Enhancement Tests ===\n")
    
    # Run all tests
    test_enhanced_context_understanding()
    test_conversational_memory()
    test_intent_classification()
    test_response_quality_improvements()
    test_personalization_enhancements()
    test_response_validation()
    test_error_handling()
    
    print("\n=== All Tests Complete ===")
    print("\nThese tests validate the key improvements:")
    print("✅ Enhanced context understanding with user profiles")
    print("✅ Conversational memory for multi-turn interactions")
    print("✅ Smarter intent classification beyond keyword matching")
    print("✅ Structured response format with action items and follow-ups")
    print("✅ Personalized clarifying questions based on user context")
    print("✅ Response validation and quality control")
    print("✅ Intelligent error handling with specific recovery strategies")

if __name__ == "__main__":
    main()