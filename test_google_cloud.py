#!/usr/bin/env python3
"""
Test script for Google Cloud integrations
Run this to verify Firestore and Gemini AI connections
"""

import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.firestore_db import test_firestore_connection
from utils.gemini_ai import test_gemini_connection, generate_financial_assistance_response

def main():
    print("=== Houston Financial Navigator - Google Cloud Integration Test ===\n")
    
    # Test Firestore connection
    print("1. Testing Firestore Database Connection...")
    try:
        success, message = test_firestore_connection()
        if success:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
    except Exception as e:
        print(f"   ❌ Firestore test failed with exception: {e}")
    
    print()
    
    # Test Gemini AI connection
    print("2. Testing Gemini AI Connection...")
    try:
        success, message = test_gemini_connection()
        if success:
            print(f"   ✅ {message}")
        else:
            print(f"   ❌ {message}")
    except Exception as e:
        print(f"   ❌ Gemini test failed with exception: {e}")
    
    print()
    
    # Test AI response generation
    print("3. Testing AI Financial Assistant Response...")
    try:
        test_question = "I need help with rent assistance in Houston"
        response = generate_financial_assistance_response(test_question)
        
        print(f"   Question: {test_question}")
        print(f"   Answer: {response['answer'][:100]}...")
        print(f"   Sources found: {len(response['sources'])}")
        print("   ✅ AI response generation working")
    except Exception as e:
        print(f"   ❌ AI response test failed: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()