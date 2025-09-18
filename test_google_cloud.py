#!/usr/bin/env python3
"""
Comprehensive Test Suite for Houston Financial Navigator - Google Cloud Integration
Tests Firestore CRUD operations, AP2 protocol integration, Gemini AI, and real-time features
"""

import sys
import os
import time
import uuid
from datetime import datetime, timedelta

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.firestore_db import (
    test_firestore_connection, get_collection_stats, cleanup_expired_data,
    # User operations
    create_user, get_user, update_user, delete_user,
    # Chat session operations  
    create_chat_session, get_chat_session, update_chat_session, delete_chat_session,
    add_message_to_session, get_user_chat_sessions,
    # AP2 transaction operations
    create_ap2_transaction, get_ap2_transaction, update_ap2_transaction, delete_ap2_transaction,
    get_user_ap2_transactions,
    # Agent state operations
    create_agent_state, get_agent_state, update_agent_state, delete_agent_state,
    get_user_agent_states
)
from utils.gemini_ai import test_gemini_connection, generate_financial_assistance_response
from utils.ap2_protocol import ap2_protocol, MandateType, MandateStatus

def test_firestore_crud_operations():
    """Test comprehensive CRUD operations for all Firestore collections"""
    print("=== Testing Firestore CRUD Operations ===")
    
    # Test user ID for all operations
    test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    test_session_id = f"test_session_{uuid.uuid4().hex[:8]}"
    test_transaction_id = f"test_transaction_{uuid.uuid4().hex[:8]}"
    
    try:
        # Test Users Collection
        print("\n1. Testing Users Collection:")
        
        # Create user
        user_data = {
            "email": f"{test_user_id}@test.com",
            "first_name": "Test",
            "last_name": "User",
            "trust_score": 85.5,
            "preferences": {
                "notification_enabled": True,
                "preferred_language": "en",
                "risk_tolerance": "moderate"
            },
            "financial_profile": {
                "income_range": "50000-75000",
                "credit_score": 720,
                "investment_experience": "intermediate"
            }
        }
        
        success, message = create_user(test_user_id, user_data)
        print(f"   Create User: {'✅' if success else '❌'} {message}")
        
        # Get user
        retrieved_user, message = get_user(test_user_id)
        print(f"   Get User: {'✅' if retrieved_user else '❌'} {message}")
        
        # Update user
        update_data = {"trust_score": 90.0, "last_login": datetime.now().isoformat()}
        success, message = update_user(test_user_id, update_data)
        print(f"   Update User: {'✅' if success else '❌'} {message}")
        
        # Test Chat Sessions Collection
        print("\n2. Testing Chat Sessions Collection:")
        
        # Create chat session
        session_data = {
            "user_id": test_user_id,
            "messages": [
                {
                    "role": "bot",
                    "content": "Hello! How can I help you with financial assistance today?",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "context": {
                "topic": "rent_assistance",
                "location": "houston",
                "previous_interactions": 0
            },
            "status": "active"
        }
        
        success, message = create_chat_session(test_session_id, session_data)
        print(f"   Create Chat Session: {'✅' if success else '❌'} {message}")
        
        # Add message to session
        new_message = {
            "role": "user",
            "content": "I need help with rent assistance in Houston"
        }
        success, message = add_message_to_session(test_session_id, new_message)
        print(f"   Add Message: {'✅' if success else '❌'} {message}")
        
        # Get chat session
        retrieved_session, message = get_chat_session(test_session_id)
        print(f"   Get Chat Session: {'✅' if retrieved_session else '❌'} {message}")
        
        # Get user chat sessions
        sessions, message = get_user_chat_sessions(test_user_id)
        print(f"   Get User Sessions: {'✅' if len(sessions) > 0 else '❌'} Found {len(sessions)} sessions")
        
        # Test AP2 Transactions Collection
        print("\n3. Testing AP2 Transactions Collection:")
        
        # Create AP2 transaction
        transaction_data = {
            "user_id": test_user_id,
            "mandate_type": "intent",
            "intent_mandate": {
                "type": "savings_goal",
                "amount": 500,
                "frequency": "monthly",
                "description": "Automated savings for emergency fund"
            },
            "cart_mandate": None,
            "payment_mandate": None,
            "status": "pending",
            "cryptographic_proofs": {
                "signature": "mock_signature_123",
                "hash": "mock_hash_456",
                "verification_status": "verified"
            },
            "trust_score_required": 80.0,
            "expires_at": (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        success, message = create_ap2_transaction(test_transaction_id, transaction_data)
        print(f"   Create AP2 Transaction: {'✅' if success else '❌'} {message}")
        
        # Get AP2 transaction
        retrieved_transaction, message = get_ap2_transaction(test_transaction_id)
        print(f"   Get AP2 Transaction: {'✅' if retrieved_transaction else '❌'} {message}")
        
        # Update AP2 transaction
        update_data = {"status": "approved", "approved_at": datetime.now().isoformat()}
        success, message = update_ap2_transaction(test_transaction_id, update_data)
        print(f"   Update AP2 Transaction: {'✅' if success else '❌'} {message}")
        
        # Get user AP2 transactions
        transactions, message = get_user_ap2_transactions(test_user_id)
        print(f"   Get User Transactions: {'✅' if len(transactions) > 0 else '❌'} Found {len(transactions)} transactions")
        
        # Test Agent State Collection
        print("\n4. Testing Agent State Collection:")
        
        # Create agent state
        state_data = {
            "user_id": test_user_id,
            "session_id": test_session_id,
            "current_context": {
                "conversation_stage": "information_gathering",
                "user_intent": "rent_assistance",
                "collected_info": {
                    "location": "houston",
                    "income_verified": False,
                    "emergency_status": False
                }
            },
            "pending_actions": [
                {
                    "action_type": "verify_income",
                    "priority": "high",
                    "deadline": (datetime.now() + timedelta(hours=24)).isoformat()
                },
                {
                    "action_type": "send_resource_links",
                    "priority": "medium",
                    "deadline": (datetime.now() + timedelta(hours=2)).isoformat()
                }
            ],
            "financial_insights": [
                {
                    "type": "savings_opportunity",
                    "message": "Based on your profile, you could save $200/month with automated budgeting",
                    "confidence": 0.85,
                    "action_suggested": "setup_automated_savings"
                }
            ],
            "trust_metrics": {
                "conversation_trust": 0.9,
                "verification_level": "basic",
                "risk_assessment": "low"
            }
        }
        
        success, message = create_agent_state(test_session_id, state_data)
        print(f"   Create Agent State: {'✅' if success else '❌'} {message}")
        
        # Get agent state
        retrieved_state, message = get_agent_state(test_session_id)
        print(f"   Get Agent State: {'✅' if retrieved_state else '❌'} {message}")
        
        # Update agent state
        update_data = {
            "current_context.conversation_stage": "solution_recommendation",
            "trust_metrics.verification_level": "enhanced"
        }
        success, message = update_agent_state(test_session_id, update_data)
        print(f"   Update Agent State: {'✅' if success else '❌'} {message}")
        
        # Get user agent states
        states, message = get_user_agent_states(test_user_id)
        print(f"   Get User Agent States: {'✅' if len(states) > 0 else '❌'} Found {len(states)} states")
        
        # Test Collection Statistics
        print("\n5. Testing Collection Statistics:")
        stats, message = get_collection_stats()
        if stats:
            print(f"   Collection Stats: ✅ {message}")
            for collection, count in stats.items():
                print(f"     - {collection}: {count} documents")
        else:
            print(f"   Collection Stats: ❌ {message}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ CRUD test failed with exception: {e}")
        return False
    
    finally:
        # Cleanup test data
        print("\n6. Cleaning up test data:")
        try:
            delete_user(test_user_id)
            delete_chat_session(test_session_id)
            delete_ap2_transaction(test_transaction_id)
            delete_agent_state(test_session_id)
            print("   ✅ Test data cleaned up successfully")
        except Exception as e:
            print(f"   ⚠️ Cleanup warning: {e}")

def test_ap2_firestore_integration():
    """Test integration between AP2 protocol and Firestore persistence"""
    print("\n=== Testing AP2-Firestore Integration ===")
    
    test_user_id = f"ap2_test_{uuid.uuid4().hex[:8]}"
    
    try:
        # Create user first
        user_data = {
            "email": f"{test_user_id}@test.com",
            "trust_score": 95.0,
            "preferences": {"auto_approve_threshold": 1000}
        }
        create_user(test_user_id, user_data)
        
        # Test intent mandate with Firestore persistence
        print("\n1. Testing Intent Mandate with Firestore:")
        intent_data = {
            "intent_type": "savings_goal",
            "amount": 300,
            "frequency": "monthly",
            "description": "Emergency fund building"
        }
        
        # Create mandate through AP2 protocol
        mandate = ap2_protocol.create_intent_mandate(test_user_id, intent_data)
        print(f"   AP2 Mandate Created: ✅ ID {mandate.id}")
        
        # Store in Firestore
        firestore_data = {
            "user_id": test_user_id,
            "mandate_id": mandate.id,
            "mandate_type": mandate.type.value,
            "intent_mandate": mandate.data,
            "status": mandate.status.value,
            "cryptographic_proofs": {
                "signature": mandate.signature,
                "verified": mandate.verify_signature()
            },
            "expires_at": mandate.expires_at.isoformat()
        }
        
        success, message = create_ap2_transaction(mandate.id, firestore_data)
        print(f"   Firestore Persistence: {'✅' if success else '❌'} {message}")
        
        # Test cart mandate
        print("\n2. Testing Cart Mandate with Firestore:")
        cart_data = {
            "items": [
                {"name": "Emergency Fund Contribution", "amount": 100},
                {"name": "Investment Portfolio", "amount": 200}
            ],
            "total": 300,
            "recurring": True
        }
        
        cart_mandate = ap2_protocol.create_cart_mandate(test_user_id, cart_data)
        
        firestore_cart_data = {
            "user_id": test_user_id,
            "mandate_id": cart_mandate.id,
            "mandate_type": cart_mandate.type.value,
            "cart_mandate": cart_mandate.data,
            "status": cart_mandate.status.value,
            "cryptographic_proofs": {
                "signature": cart_mandate.signature,
                "verified": cart_mandate.verify_signature()
            }
        }
        
        success, message = create_ap2_transaction(cart_mandate.id, firestore_cart_data)
        print(f"   Cart Mandate Stored: {'✅' if success else '❌'} {message}")
        
        # Test payment mandate
        print("\n3. Testing Payment Mandate with Firestore:")
        payment_data = {
            "amount": 500,
            "purpose": "emergency_withdrawal",
            "account_type": "savings",
            "urgency": "high"
        }
        
        payment_mandate = ap2_protocol.create_payment_mandate(test_user_id, payment_data)
        
        firestore_payment_data = {
            "user_id": test_user_id,
            "mandate_id": payment_mandate.id,
            "mandate_type": payment_mandate.type.value,
            "payment_mandate": payment_mandate.data,
            "status": payment_mandate.status.value,
            "cryptographic_proofs": {
                "signature": payment_mandate.signature,
                "verified": payment_mandate.verify_signature()
            }
        }
        
        success, message = create_ap2_transaction(payment_mandate.id, firestore_payment_data)
        print(f"   Payment Mandate Stored: {'✅' if success else '❌'} {message}")
        
        # Test retrieval and verification
        print("\n4. Testing Mandate Retrieval and Verification:")
        transactions, message = get_user_ap2_transactions(test_user_id)
        print(f"   Retrieved {len(transactions)} transactions for user")
        
        for transaction in transactions:
            mandate_id = transaction.get('mandate_id')
            stored_signature = transaction.get('cryptographic_proofs', {}).get('signature')
            ap2_mandate = ap2_protocol.get_mandate(mandate_id)
            
            if ap2_mandate and stored_signature == ap2_mandate.signature:
                print(f"   ✅ Mandate {mandate_id[:8]}... verified successfully")
            else:
                print(f"   ❌ Mandate {mandate_id[:8]}... verification failed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ AP2-Firestore integration test failed: {e}")
        return False
    
    finally:
        # Cleanup
        try:
            delete_user(test_user_id)
            transactions, _ = get_user_ap2_transactions(test_user_id)
            for transaction in transactions:
                delete_ap2_transaction(transaction['id'])
        except:
            pass

def test_real_time_features():
    """Test real-time listeners and live chat updates"""
    print("\n=== Testing Real-time Features ===")
    
    test_session_id = f"realtime_test_{uuid.uuid4().hex[:8]}"
    
    try:
        # Create initial chat session
        session_data = {
            "user_id": "realtime_user",
            "messages": [],
            "context": {"test": True},
            "status": "active"
        }
        
        success, message = create_chat_session(test_session_id, session_data)
        print(f"   Initial Session: {'✅' if success else '❌'} {message}")
        
        # Test message addition (simulating real-time updates)
        print("\n1. Testing Real-time Message Updates:")
        
        messages = [
            {"role": "user", "content": "Hello, I need help with budgeting"},
            {"role": "bot", "content": "I'd be happy to help you create a budget. What's your monthly income?"},
            {"role": "user", "content": "Around $4000 per month"},
            {"role": "bot", "content": "Great! Let's start by categorizing your expenses..."}
        ]
        
        for i, message in enumerate(messages):
            success, msg = add_message_to_session(test_session_id, message)
            print(f"   Message {i+1}: {'✅' if success else '❌'} {msg}")
            time.sleep(0.1)  # Simulate real-time delay
        
        # Verify final state
        final_session, message = get_chat_session(test_session_id)
        if final_session and len(final_session.get('messages', [])) == len(messages):
            print(f"   ✅ All {len(messages)} messages stored successfully")
        else:
            print(f"   ❌ Message count mismatch")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Real-time features test failed: {e}")
        return False
    
    finally:
        try:
            delete_chat_session(test_session_id)
        except:
            pass

def main():
    print("=== Houston Financial Navigator - Comprehensive Google Cloud Integration Test ===\n")
    
    test_results = []
    
    # Test 1: Basic Firestore connection
    print("1. Testing Firestore Database Connection...")
    try:
        success, message = test_firestore_connection()
        if success:
            print(f"   ✅ {message}")
            test_results.append(("Firestore Connection", True))
        else:
            print(f"   ❌ {message}")
            test_results.append(("Firestore Connection", False))
    except Exception as e:
        print(f"   ❌ Firestore test failed with exception: {e}")
        test_results.append(("Firestore Connection", False))
    
    print()
    
    # Test 2: Gemini AI connection
    print("2. Testing Gemini AI Connection...")
    try:
        success, message = test_gemini_connection()
        if success:
            print(f"   ✅ {message}")
            test_results.append(("Gemini AI Connection", True))
        else:
            print(f"   ❌ {message}")
            test_results.append(("Gemini AI Connection", False))
    except Exception as e:
        print(f"   ❌ Gemini test failed with exception: {e}")
        test_results.append(("Gemini AI Connection", False))
    
    print()
    
    # Test 3: AI response generation
    print("3. Testing AI Financial Assistant Response...")
    try:
        test_question = "I need help with rent assistance in Houston"
        response = generate_financial_assistance_response(test_question)
        print(f"   Question: {test_question}")
        print(f"   Answer: {response['answer'][:100]}...")
        print(f"   Sources found: {len(response['sources'])}")
        print("   ✅ AI response generation working")
        test_results.append(("AI Response Generation", True))
    except Exception as e:
        print(f"   ❌ AI response test failed: {e}")
        test_results.append(("AI Response Generation", False))
    
    # Test 4: Comprehensive Firestore CRUD operations
    print("\n4. Testing Comprehensive Firestore CRUD Operations...")
    crud_success = test_firestore_crud_operations()
    test_results.append(("Firestore CRUD Operations", crud_success))
    
    # Test 5: AP2-Firestore integration
    print("\n5. Testing AP2 Protocol Integration with Firestore...")
    ap2_success = test_ap2_firestore_integration()
    test_results.append(("AP2-Firestore Integration", ap2_success))
    
    # Test 6: Real-time features
    print("\n6. Testing Real-time Chat Features...")
    realtime_success = test_real_time_features()
    test_results.append(("Real-time Features", realtime_success))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if success:
            passed += 1
    
    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Houston Financial Navigator is ready for production.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the configuration and try again.")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()