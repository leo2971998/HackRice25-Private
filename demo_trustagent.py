#!/usr/bin/env python3
"""
TrustAgent Demo Script - Phase 1 AP2 Implementation
Demonstrates the revolutionary Agent Payments Protocol features
"""

import sys
import json
from datetime import datetime
from utils.ap2_protocol import ap2_protocol, MandateType, MandateStatus
from utils.smart_finance import smart_budget, savings_automation, subscription_optimizer, emergency_response

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def main():
    print_header("🚀 TrustAgent Phase 1 - AP2-Powered Financial Co-Pilot Demo")
    
    user_id = "demo_user_2024"
    
    # 1. Demonstrate AP2 Protocol
    print_header("🛡️  AP2 (Agent Payments Protocol) Demonstration")
    
    print_info("Creating Intent Mandate for Automated Savings...")
    intent_mandate = ap2_protocol.create_intent_mandate(user_id, {
        "intent_type": "savings_goal",
        "goal_name": "Emergency Fund",
        "target_amount": 6000,
        "monthly_amount": 500,
        "frequency": "monthly"
    })
    
    print_success(f"Intent Mandate Created: {intent_mandate.id}")
    print(f"   Type: {intent_mandate.type.value}")
    print(f"   Status: {intent_mandate.status.value}")
    print(f"   Signature: {intent_mandate.signature[:30]}...")
    print(f"   Valid: {intent_mandate.is_valid()}")
    
    print_info("Approving mandate for execution...")
    intent_mandate.approve()
    print_success(f"Mandate approved: {intent_mandate.status.value}")
    
    print_info("Executing approved mandate...")
    execution_result = ap2_protocol.execute_mandate(intent_mandate.id)
    print_success(f"Execution successful: {execution_result.get('success')}")
    print(f"   Action: {execution_result.get('action')}")
    print(f"   Details: {execution_result.get('details')}")
    
    # 2. Demonstrate Cart Mandate for Subscriptions
    print_info("Creating Cart Mandate for Subscription Management...")
    cart_mandate = ap2_protocol.create_cart_mandate(user_id, {
        "subscription_type": "streaming_services",
        "items": [
            {"name": "Netflix", "amount": 15.99, "frequency": "monthly"},
            {"name": "Spotify", "amount": 9.99, "frequency": "monthly"}
        ],
        "auto_optimize": True
    })
    
    cart_mandate.approve()
    cart_result = ap2_protocol.execute_mandate(cart_mandate.id)
    print_success(f"Cart mandate executed: ${cart_result.get('total_amount')}")
    
    # 3. Demonstrate Payment Mandate for Emergency Response
    print_info("Creating Payment Mandate for Emergency Fund Access...")
    payment_mandate = ap2_protocol.create_payment_mandate(user_id, {
        "purpose": "emergency",
        "amount": 500,
        "reason": "Medical emergency fund access",
        "auto_approve_threshold": 1000
    })
    
    payment_mandate.approve()
    payment_result = ap2_protocol.execute_mandate(payment_mandate.id)
    print_success(f"Emergency payment executed: ${payment_result.get('amount')}")
    
    # 4. Demonstrate Smart Budget Features
    print_header("🧠 Smart Budget Enforcement")
    
    budget_result = smart_budget.set_budget_alert(user_id, "dining", 400, 0.8)
    print_success(f"Budget alert created: {budget_result.get('message')}")
    
    # Simulate transaction checking
    mock_transactions = [
        {"description": "Restaurant XYZ", "amount": -85.50, "transaction_date": "2024-01"},
        {"description": "Coffee Shop", "amount": -12.75, "transaction_date": "2024-01"},
        {"description": "Pizza Place", "amount": -28.90, "transaction_date": "2024-01"},
        {"description": "Dining Out", "amount": -125.00, "transaction_date": "2024-01"},
        {"description": "Fast Food", "amount": -15.80, "transaction_date": "2024-01"},
        {"description": "Grocery Store", "amount": -95.40, "transaction_date": "2024-01"}
    ]
    
    alerts = smart_budget.check_spending(user_id, mock_transactions)
    if alerts:
        print_success(f"Budget monitoring active - {len(alerts)} alerts triggered")
        for alert in alerts:
            print(f"   🚨 {alert['message']}")
    
    # 5. Demonstrate Savings Automation
    print_header("💰 Autonomous Savings Automation")
    
    savings_goal = savings_automation.create_savings_goal(user_id, {
        "name": "Vacation Fund",
        "target_amount": 3000,
        "monthly_amount": 250,
        "auto_transfer": True
    })
    print_success(f"Savings automation created: {savings_goal.get('message')}")
    
    # Get AI recommendations
    financial_data = {
        "total_balance": 2500,
        "recent_transactions": mock_transactions
    }
    
    recommendations = savings_automation.get_savings_recommendations(user_id, financial_data)
    print_success(f"AI generated {len(recommendations)} savings recommendations")
    for rec in recommendations:
        print(f"   💡 {rec['description']} (${rec['monthly_amount']:.0f}/month)")
    
    # 6. Demonstrate Subscription Optimization
    print_header("📱 Subscription Optimization")
    
    subscriptions = subscription_optimizer.detect_subscriptions(user_id, [
        {"description": "Netflix Subscription", "amount": -15.99},
        {"description": "Spotify Premium", "amount": -9.99},
        {"description": "Apple iCloud", "amount": -2.99},
        {"description": "Amazon Prime", "amount": -12.99}
    ])
    
    total_monthly = sum(sub.get("amount", 0) for sub in subscriptions)
    print_success(f"Detected {len(subscriptions)} subscriptions (${total_monthly:.2f}/month)")
    
    optimization_potential = sum(sub.get("optimization_score", 0) for sub in subscriptions)
    print(f"   🎯 Optimization potential score: {optimization_potential:.1f}/10")
    
    # 7. Demonstrate Emergency Response
    print_header("🚨 Emergency Financial Response")
    
    emergency_alerts = emergency_response.check_emergency_conditions(user_id, {
        "total_balance": 85.50,  # Low balance scenario
        "recent_transactions": [
            {"description": "Large Medical Bill", "amount": -850.00},
            {"description": "Unexpected Car Repair", "amount": -1200.00}
        ]
    })
    
    print_success(f"Emergency monitoring active - {len(emergency_alerts)} conditions detected")
    for alert in emergency_alerts:
        print(f"   🚨 {alert['message']}")
        print(f"      Severity: {alert['severity']}")
    
    # 8. Summary Statistics
    print_header("📊 TrustAgent AP2 Summary")
    
    all_mandates = ap2_protocol.get_user_mandates(user_id)
    stats = {
        "total_mandates": len(all_mandates),
        "executed_mandates": len([m for m in all_mandates if m.status == MandateStatus.EXECUTED]),
        "mandate_types": list(set([m.type.value for m in all_mandates]))
    }
    
    print_success(f"AP2 Protocol Status:")
    print(f"   📋 Total Mandates: {stats['total_mandates']}")
    print(f"   ⚡ Executed: {stats['executed_mandates']}")
    print(f"   🔧 Types: {', '.join(stats['mandate_types'])}")
    
    print_success("Smart Finance Features:")
    print(f"   🎯 Budget alerts configured: Active")
    print(f"   💰 Savings automation: Active")
    print(f"   📱 Subscription optimization: Active")
    print(f"   🚨 Emergency monitoring: Active")
    
    print_header("🎉 TrustAgent Phase 1 Demo Complete!")
    print_info("Revolutionary AP2-powered financial co-pilot successfully demonstrated!")
    print_info("Features include:")
    print("   • Cryptographically signed financial mandates")
    print("   • Autonomous savings and budget enforcement")
    print("   • AI-powered financial recommendations")
    print("   • Real-time emergency response system")
    print("   • Smart subscription optimization")
    print("   • Scenario analysis and planning tools")
    
    return True

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        sys.exit(1)