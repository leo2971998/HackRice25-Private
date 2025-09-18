# utils/ap2_protocol.py
"""
Mock AP2 (Agent Payments Protocol) Implementation for TrustAgent
Simulates the revolutionary agent payments protocol for autonomous financial operations
"""

import hashlib
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import hmac

class MandateType(Enum):
    INTENT = "intent"          # User expresses financial intent
    CART = "cart"              # Shopping cart with items
    PAYMENT = "payment"        # Actual payment execution

class MandateStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class AP2Mandate:
    """
    Represents an AP2 mandate - a cryptographically signed instruction
    for autonomous financial operations
    """
    
    def __init__(self, mandate_type: MandateType, user_id: str, data: Dict):
        self.id = str(uuid.uuid4())
        self.type = mandate_type
        self.user_id = user_id
        self.data = data
        self.status = MandateStatus.PENDING
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(hours=24)  # 24h default expiry
        self.executed_at = None
        self.signature = self._generate_signature()
        
    def _generate_signature(self) -> str:
        """Generate cryptographic signature for mandate (mock implementation)"""
        payload = {
            "id": self.id,
            "type": self.type.value,
            "user_id": self.user_id,
            "data": self.data,
            "created_at": self.created_at.isoformat()
        }
        
        # Mock cryptographic signature using HMAC
        secret_key = "ap2_secret_key_mock"  # In production, this would be from secure storage
        message = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret_key.encode(), 
            message.encode(), 
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self) -> bool:
        """Verify mandate signature (mock implementation)"""
        expected_signature = self._generate_signature()
        return hmac.compare_digest(self.signature, expected_signature)
    
    def is_valid(self) -> bool:
        """Check if mandate is still valid"""
        return (
            self.status in [MandateStatus.PENDING, MandateStatus.APPROVED] and
            datetime.now() < self.expires_at and
            self.verify_signature()
        )
    
    def approve(self) -> bool:
        """Approve mandate for execution"""
        if self.is_valid() and self.status == MandateStatus.PENDING:
            self.status = MandateStatus.APPROVED
            return True
        return False
    
    def execute(self) -> bool:
        """Execute approved mandate"""
        if self.is_valid() and self.status == MandateStatus.APPROVED:
            self.status = MandateStatus.EXECUTED
            self.executed_at = datetime.now()
            return True
        return False
    
    def cancel(self) -> bool:
        """Cancel pending mandate"""
        if self.status == MandateStatus.PENDING:
            self.status = MandateStatus.CANCELLED
            return True
        return False
    
    def to_dict(self) -> Dict:
        """Convert mandate to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "type": self.type.value,
            "user_id": self.user_id,
            "data": self.data,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "signature": self.signature,
            "is_valid": self.is_valid()
        }

class AP2Protocol:
    """
    Mock AP2 Protocol implementation for autonomous financial operations
    """
    
    def __init__(self):
        self.mandates: Dict[str, AP2Mandate] = {}
    
    def create_intent_mandate(self, user_id: str, intent_data: Dict) -> AP2Mandate:
        """
        Create an intent mandate - user expresses financial intent
        Example: "I want to save $500/month automatically"
        """
        mandate = AP2Mandate(MandateType.INTENT, user_id, intent_data)
        self.mandates[mandate.id] = mandate
        return mandate
    
    def create_cart_mandate(self, user_id: str, cart_data: Dict) -> AP2Mandate:
        """
        Create a cart mandate - shopping cart with pre-approved items
        Example: Recurring subscription payments
        """
        mandate = AP2Mandate(MandateType.CART, user_id, cart_data)
        self.mandates[mandate.id] = mandate
        return mandate
    
    def create_payment_mandate(self, user_id: str, payment_data: Dict) -> AP2Mandate:
        """
        Create a payment mandate - actual payment execution
        Example: Emergency fund withdrawal
        """
        mandate = AP2Mandate(MandateType.PAYMENT, user_id, payment_data)
        self.mandates[mandate.id] = mandate
        return mandate
    
    def get_mandate(self, mandate_id: str) -> Optional[AP2Mandate]:
        """Retrieve mandate by ID"""
        return self.mandates.get(mandate_id)
    
    def get_user_mandates(self, user_id: str, status: Optional[MandateStatus] = None) -> List[AP2Mandate]:
        """Get all mandates for a user, optionally filtered by status"""
        user_mandates = [m for m in self.mandates.values() if m.user_id == user_id]
        
        if status:
            user_mandates = [m for m in user_mandates if m.status == status]
        
        return sorted(user_mandates, key=lambda m: m.created_at, reverse=True)
    
    def approve_mandate(self, mandate_id: str) -> bool:
        """Approve a mandate for execution"""
        mandate = self.get_mandate(mandate_id)
        return mandate.approve() if mandate else False
    
    def execute_mandate(self, mandate_id: str) -> Dict:
        """Execute an approved mandate"""
        mandate = self.get_mandate(mandate_id)
        if not mandate:
            return {"success": False, "error": "Mandate not found"}
        
        if not mandate.execute():
            return {"success": False, "error": "Mandate execution failed"}
        
        # Simulate actual execution based on mandate type
        if mandate.type == MandateType.INTENT:
            return self._execute_intent(mandate)
        elif mandate.type == MandateType.CART:
            return self._execute_cart(mandate)
        elif mandate.type == MandateType.PAYMENT:
            return self._execute_payment(mandate)
        
        return {"success": False, "error": "Unknown mandate type"}
    
    def _execute_intent(self, mandate: AP2Mandate) -> Dict:
        """Execute intent mandate (e.g., set up savings automation)"""
        intent_type = mandate.data.get("intent_type")
        
        if intent_type == "savings_goal":
            amount = mandate.data.get("amount", 0)
            frequency = mandate.data.get("frequency", "monthly")
            return {
                "success": True,
                "action": "savings_automation_created",
                "details": f"Automated ${amount} {frequency} savings goal activated",
                "next_execution": (datetime.now() + timedelta(days=30)).isoformat()
            }
        
        elif intent_type == "budget_alert":
            category = mandate.data.get("category")
            threshold = mandate.data.get("threshold")
            return {
                "success": True,
                "action": "budget_alert_created",
                "details": f"Budget alert for {category} set at ${threshold}",
                "active": True
            }
        
        return {"success": True, "action": "intent_processed"}
    
    def _execute_cart(self, mandate: AP2Mandate) -> Dict:
        """Execute cart mandate (e.g., subscription payment)"""
        items = mandate.data.get("items", [])
        total_amount = sum(item.get("amount", 0) for item in items)
        
        return {
            "success": True,
            "action": "subscription_payment_processed",
            "total_amount": total_amount,
            "items_count": len(items),
            "transaction_id": f"tx_{uuid.uuid4().hex[:8]}"
        }
    
    def _execute_payment(self, mandate: AP2Mandate) -> Dict:
        """Execute payment mandate (e.g., emergency withdrawal)"""
        amount = mandate.data.get("amount", 0)
        purpose = mandate.data.get("purpose", "financial_operation")
        
        return {
            "success": True,
            "action": "payment_executed",
            "amount": amount,
            "purpose": purpose,
            "transaction_id": f"tx_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now().isoformat()
        }
    
    def cleanup_expired_mandates(self) -> int:
        """Remove expired mandates and return count of removed mandates"""
        expired_count = 0
        current_time = datetime.now()
        
        expired_ids = [
            mandate_id for mandate_id, mandate in self.mandates.items()
            if current_time > mandate.expires_at and mandate.status not in [MandateStatus.EXECUTED, MandateStatus.CANCELLED]
        ]
        
        for mandate_id in expired_ids:
            self.mandates[mandate_id].status = MandateStatus.EXPIRED
            expired_count += 1
        
        return expired_count

# Global AP2 protocol instance
ap2_protocol = AP2Protocol()