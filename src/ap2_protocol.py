import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization
import secrets
import uuid
from datetime import datetime, timedelta
from enum import Enum

# Enhanced AP2 Protocol Implementation for Phase 2

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

@dataclass
class CryptographicProof:
    """Enhanced cryptographic proof for AP2 mandates"""
    signature: str
    public_key_hash: str
    timestamp: str
    nonce: str
    algorithm: str = "RSA-OAEP-SHA256"

@dataclass 
class TrustMetrics:
    """Trust scoring metrics for mandate approval"""
    user_trust_score: float
    transaction_risk_score: float
    auto_approval_threshold: float
    requires_manual_review: bool

class EnhancedAP2Mandate:
    """
    Enhanced AP2 Mandate with advanced cryptographic features
    """
    
    def __init__(self, mandate_type: MandateType, user_id: str, data: Dict):
        self.id = str(uuid.uuid4())
        self.type = mandate_type
        self.user_id = user_id
        self.data = data
        self.status = MandateStatus.PENDING
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(hours=24)
        self.executed_at = None
        
        # Enhanced cryptographic features
        self.nonce = secrets.token_hex(32)
        self.cryptographic_proof = self._generate_cryptographic_proof()
        self.trust_metrics = self._calculate_trust_metrics()
        
    def _generate_cryptographic_proof(self) -> CryptographicProof:
        """Generate enhanced cryptographic proof"""
        # Create payload for signing
        payload = {
            "id": self.id,
            "type": self.type.value,
            "user_id": self.user_id,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "nonce": self.nonce
        }
        
        # Generate signature using HMAC (mock implementation)
        secret_key = f"ap2_secret_{self.user_id}"
        message = json.dumps(payload, sort_keys=True)
        signature = hashlib.sha256(f"{secret_key}{message}".encode()).hexdigest()
        
        # Mock public key hash
        public_key_hash = hashlib.sha256(f"pubkey_{self.user_id}".encode()).hexdigest()[:32]
        
        return CryptographicProof(
            signature=signature,
            public_key_hash=public_key_hash,
            timestamp=self.created_at.isoformat(),
            nonce=self.nonce
        )
    
    def _calculate_trust_metrics(self) -> TrustMetrics:
        """Calculate trust metrics for auto-approval"""
        # Base trust score (mock implementation)
        base_trust = 85.0
        
        # Risk assessment based on mandate type and amount
        if self.type == MandateType.INTENT:
            risk_score = 10.0  # Low risk for intent declarations
        elif self.type == MandateType.CART:
            amount = self.data.get("total_amount", 0)
            risk_score = min(50.0, amount / 20)  # Higher amounts = higher risk
        elif self.type == MandateType.PAYMENT:
            amount = self.data.get("amount", 0)
            urgency = self.data.get("urgency", "normal")
            risk_score = min(80.0, amount / 10)
            if urgency == "emergency":
                risk_score *= 0.7  # Emergency payments get lower risk score
        else:
            risk_score = 30.0
        
        auto_approval_threshold = 80.0
        final_score = base_trust - risk_score
        
        return TrustMetrics(
            user_trust_score=base_trust,
            transaction_risk_score=risk_score,
            auto_approval_threshold=auto_approval_threshold,
            requires_manual_review=final_score < auto_approval_threshold
        )
    
    def verify_cryptographic_proof(self) -> bool:
        """Verify the cryptographic proof"""
        try:
            # Recreate the signature and compare
            payload = {
                "id": self.id,
                "type": self.type.value,
                "user_id": self.user_id,
                "data": self.data,
                "created_at": self.created_at.isoformat(),
                "nonce": self.nonce
            }
            
            secret_key = f"ap2_secret_{self.user_id}"
            message = json.dumps(payload, sort_keys=True)
            expected_signature = hashlib.sha256(f"{secret_key}{message}".encode()).hexdigest()
            
            return expected_signature == self.cryptographic_proof.signature
        except Exception:
            return False
    
    def can_auto_approve(self) -> bool:
        """Check if mandate can be auto-approved based on trust metrics"""
        if not self.verify_cryptographic_proof():
            return False
            
        if self.trust_metrics.requires_manual_review:
            return False
            
        # Type-specific auto-approval rules
        if self.type == MandateType.INTENT:
            # Intent mandates for savings, budgeting are always auto-approved
            intent_type = self.data.get("intent_type", "")
            safe_intents = ["savings_goal", "budget_alert", "spending_analysis"]
            return intent_type in safe_intents
            
        elif self.type == MandateType.CART:
            # Cart mandates under $50 are auto-approved
            total_amount = self.data.get("total_amount", 0)
            return total_amount <= 50.0
            
        elif self.type == MandateType.PAYMENT:
            # Emergency payments under $100 are auto-approved
            amount = self.data.get("amount", 0)
            urgency = self.data.get("urgency", "normal")
            return amount <= 100.0 and urgency == "emergency"
            
        return False
    
    def approve(self) -> bool:
        """Approve mandate for execution"""
        if self.status != MandateStatus.PENDING:
            return False
            
        if not self.verify_cryptographic_proof():
            return False
            
        self.status = MandateStatus.APPROVED
        return True
    
    def execute(self) -> bool:
        """Execute approved mandate"""
        if self.status != MandateStatus.APPROVED:
            return False
            
        self.status = MandateStatus.EXECUTED
        self.executed_at = datetime.now()
        return True
    
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
            "cryptographic_proof": asdict(self.cryptographic_proof),
            "trust_metrics": asdict(self.trust_metrics)
        }

class EnhancedAP2Protocol:
    """
    Enhanced AP2 Protocol with advanced cryptographic features and trust scoring
    """
    
    def __init__(self):
        self.mandates: Dict[str, EnhancedAP2Mandate] = {}
        self.session_id = str(uuid.uuid4())
        
    def create_intent_mandate(self, user_id: str, intent_data: Dict) -> EnhancedAP2Mandate:
        """
        Create an intent mandate - user expresses financial intent
        Example: Set savings goal, budget alert, spending analysis
        """
        mandate = EnhancedAP2Mandate(MandateType.INTENT, user_id, intent_data)
        self.mandates[mandate.id] = mandate
        
        # Auto-approve safe intent mandates
        if mandate.can_auto_approve():
            mandate.approve()
            
        return mandate
    
    def create_cart_mandate(self, user_id: str, cart_data: Dict) -> EnhancedAP2Mandate:
        """
        Create a cart mandate - shopping cart with items
        Example: Subscription management, recurring payments
        """
        mandate = EnhancedAP2Mandate(MandateType.CART, user_id, cart_data)
        self.mandates[mandate.id] = mandate
        
        # Auto-approve low-value cart mandates
        if mandate.can_auto_approve():
            mandate.approve()
            
        return mandate
    
    def create_payment_mandate(self, user_id: str, payment_data: Dict) -> EnhancedAP2Mandate:
        """
        Create a payment mandate - actual payment execution
        Example: Emergency fund withdrawal
        """
        mandate = EnhancedAP2Mandate(MandateType.PAYMENT, user_id, payment_data)
        self.mandates[mandate.id] = mandate
        
        # Auto-approve emergency payments under threshold
        if mandate.can_auto_approve():
            mandate.approve()
            
        return mandate
    
    def get_mandate(self, mandate_id: str) -> Optional[EnhancedAP2Mandate]:
        """Retrieve mandate by ID"""
        return self.mandates.get(mandate_id)
    
    def get_user_mandates(self, user_id: str, status: Optional[MandateStatus] = None) -> List[EnhancedAP2Mandate]:
        """Get all mandates for a user, optionally filtered by status"""
        user_mandates = [m for m in self.mandates.values() if m.user_id == user_id]
        
        if status:
            user_mandates = [m for m in user_mandates if m.status == status]
            
        return sorted(user_mandates, key=lambda x: x.created_at, reverse=True)
    
    def process_auto_approvals(self) -> int:
        """Process all pending mandates for auto-approval"""
        auto_approved = 0
        
        for mandate in self.mandates.values():
            if mandate.status == MandateStatus.PENDING and mandate.can_auto_approve():
                mandate.approve()
                auto_approved += 1
                
        return auto_approved
    
    def cleanup_expired_mandates(self) -> int:
        """Mark expired mandates and return count"""
        expired_count = 0
        now = datetime.now()
        
        for mandate in self.mandates.values():
            if mandate.status == MandateStatus.PENDING and mandate.expires_at < now:
                mandate.status = MandateStatus.EXPIRED
                expired_count += 1
                
        return expired_count

# Global enhanced AP2 protocol instance
enhanced_ap2_protocol = EnhancedAP2Protocol()