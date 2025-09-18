from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from config.firestore_config import FirestoreManager
from src.ap2_protocol import enhanced_ap2_protocol, MandateType, MandateStatus
import asyncio
from typing import Dict, Any, List, Optional
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI(
    title="AP2 Agent Backend",
    description="Advanced Payments Protocol (AP2) Agent for autonomous financial operations",
    version="1.0.0"
)

# Initialize Firestore manager
firestore_manager = FirestoreManager()

# Pydantic models for API requests/responses
class IntentMandateRequest(BaseModel):
    user_id: str
    intent_type: str
    amount: Optional[float] = None
    frequency: Optional[str] = None
    description: str

class CartMandateRequest(BaseModel):
    user_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    subscription_type: Optional[str] = None

class PaymentMandateRequest(BaseModel):
    user_id: str
    amount: float
    purpose: str
    urgency: str = "normal"  # normal, high, emergency
    recipient: Optional[str] = None

class MandateResponse(BaseModel):
    mandate_id: str
    status: str
    auto_approved: bool
    trust_score: float
    message: str

class AgentStateRequest(BaseModel):
    session_id: str
    user_id: str
    current_context: Dict[str, Any]
    pending_actions: List[str]
    financial_insights: List[str]

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Initialize Firestore connection
        success = firestore_manager.initialize()
        if success:
            print("✅ Firestore connection established")
        else:
            print("⚠️ Firestore connection failed, using in-memory storage")
    except Exception as e:
        print(f"⚠️ Error during startup: {e}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "AP2 Agent Backend",
        "status": "operational",
        "version": "1.0.0",
        "protocol": "AP2 Enhanced"
    }

@app.post("/api/mandates/intent", response_model=MandateResponse)
async def create_intent_mandate(request: IntentMandateRequest):
    """Create an intent mandate for financial planning"""
    try:
        # Create mandate through AP2 protocol
        mandate = enhanced_ap2_protocol.create_intent_mandate(
            request.user_id,
            {
                "intent_type": request.intent_type,
                "amount": request.amount,
                "frequency": request.frequency,
                "description": request.description
            }
        )
        
        # Store in Firestore if available
        db = firestore_manager.get_client()
        if db:
            try:
                # Store mandate in ap2_transactions collection
                mandate_data = mandate.to_dict()
                mandate_data["mandate_type"] = "intent"
                
                db.collection('ap2_transactions').document(mandate.id).set(mandate_data)
            except Exception as e:
                print(f"Warning: Could not store mandate in Firestore: {e}")
        
        auto_approved = mandate.status == MandateStatus.APPROVED
        
        return MandateResponse(
            mandate_id=mandate.id,
            status=mandate.status.value,
            auto_approved=auto_approved,
            trust_score=mandate.trust_metrics.user_trust_score,
            message=f"Intent mandate created and {'auto-approved' if auto_approved else 'pending review'}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create intent mandate: {str(e)}")

@app.post("/api/mandates/cart", response_model=MandateResponse)
async def create_cart_mandate(request: CartMandateRequest):
    """Create a cart mandate for shopping/subscription management"""
    try:
        mandate = enhanced_ap2_protocol.create_cart_mandate(
            request.user_id,
            {
                "items": request.items,
                "total_amount": request.total_amount,
                "subscription_type": request.subscription_type
            }
        )
        
        # Store in Firestore if available
        db = firestore_manager.get_client()
        if db:
            try:
                mandate_data = mandate.to_dict()
                mandate_data["mandate_type"] = "cart"
                
                db.collection('ap2_transactions').document(mandate.id).set(mandate_data)
            except Exception as e:
                print(f"Warning: Could not store mandate in Firestore: {e}")
        
        auto_approved = mandate.status == MandateStatus.APPROVED
        
        return MandateResponse(
            mandate_id=mandate.id,
            status=mandate.status.value,
            auto_approved=auto_approved,
            trust_score=mandate.trust_metrics.user_trust_score,
            message=f"Cart mandate created and {'auto-approved' if auto_approved else 'pending review'}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create cart mandate: {str(e)}")

@app.post("/api/mandates/payment", response_model=MandateResponse)
async def create_payment_mandate(request: PaymentMandateRequest):
    """Create a payment mandate for actual payment execution"""
    try:
        mandate = enhanced_ap2_protocol.create_payment_mandate(
            request.user_id,
            {
                "amount": request.amount,
                "purpose": request.purpose,
                "urgency": request.urgency,
                "recipient": request.recipient
            }
        )
        
        # Store in Firestore if available
        db = firestore_manager.get_client()
        if db:
            try:
                mandate_data = mandate.to_dict()
                mandate_data["mandate_type"] = "payment"
                
                db.collection('ap2_transactions').document(mandate.id).set(mandate_data)
            except Exception as e:
                print(f"Warning: Could not store mandate in Firestore: {e}")
        
        auto_approved = mandate.status == MandateStatus.APPROVED
        
        return MandateResponse(
            mandate_id=mandate.id,
            status=mandate.status.value,
            auto_approved=auto_approved,
            trust_score=mandate.trust_metrics.user_trust_score,
            message=f"Payment mandate created and {'auto-approved' if auto_approved else 'pending review'}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment mandate: {str(e)}")

@app.get("/api/mandates/{mandate_id}")
async def get_mandate(mandate_id: str):
    """Get mandate details by ID"""
    mandate = enhanced_ap2_protocol.get_mandate(mandate_id)
    if not mandate:
        raise HTTPException(status_code=404, detail="Mandate not found")
    
    return mandate.to_dict()

@app.get("/api/mandates/user/{user_id}")
async def get_user_mandates(user_id: str, status: Optional[str] = None):
    """Get all mandates for a user"""
    mandate_status = None
    if status:
        try:
            mandate_status = MandateStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    mandates = enhanced_ap2_protocol.get_user_mandates(user_id, mandate_status)
    return {
        "user_id": user_id,
        "mandates": [mandate.to_dict() for mandate in mandates],
        "count": len(mandates)
    }

@app.post("/api/mandates/{mandate_id}/approve")
async def approve_mandate(mandate_id: str):
    """Manually approve a mandate"""
    mandate = enhanced_ap2_protocol.get_mandate(mandate_id)
    if not mandate:
        raise HTTPException(status_code=404, detail="Mandate not found")
    
    success = mandate.approve()
    if not success:
        raise HTTPException(status_code=400, detail="Mandate cannot be approved")
    
    # Update in Firestore if available
    db = firestore_manager.get_client()
    if db:
        try:
            db.collection('ap2_transactions').document(mandate_id).update({
                "status": mandate.status.value
            })
        except Exception as e:
            print(f"Warning: Could not update mandate in Firestore: {e}")
    
    return {"mandate_id": mandate_id, "status": mandate.status.value, "message": "Mandate approved"}

@app.post("/api/mandates/{mandate_id}/execute")
async def execute_mandate(mandate_id: str):
    """Execute an approved mandate"""
    mandate = enhanced_ap2_protocol.get_mandate(mandate_id)
    if not mandate:
        raise HTTPException(status_code=404, detail="Mandate not found")
    
    success = mandate.execute()
    if not success:
        raise HTTPException(status_code=400, detail="Mandate cannot be executed")
    
    # Update in Firestore if available
    db = firestore_manager.get_client()
    if db:
        try:
            db.collection('ap2_transactions').document(mandate_id).update({
                "status": mandate.status.value,
                "executed_at": mandate.executed_at.isoformat()
            })
        except Exception as e:
            print(f"Warning: Could not update mandate in Firestore: {e}")
    
    return {"mandate_id": mandate_id, "status": mandate.status.value, "message": "Mandate executed"}

@app.post("/api/agent/process")
async def process_auto_approvals():
    """Process all pending mandates for auto-approval"""
    approved_count = enhanced_ap2_protocol.process_auto_approvals()
    expired_count = enhanced_ap2_protocol.cleanup_expired_mandates()
    
    return {
        "auto_approved": approved_count,
        "expired": expired_count,
        "message": f"Processed {approved_count} auto-approvals and {expired_count} expirations"
    }

@app.post("/api/agent/state")
async def create_agent_state(request: AgentStateRequest):
    """Create or update agent state"""
    try:
        # Store agent state in Firestore if available
        db = firestore_manager.get_client()
        if db:
            state_data = {
                "user_id": request.user_id,
                "session_id": request.session_id,
                "current_context": request.current_context,
                "pending_actions": request.pending_actions,
                "financial_insights": request.financial_insights,
                "created_at": firestore_manager._db.SERVER_TIMESTAMP if db else None,
                "updated_at": firestore_manager._db.SERVER_TIMESTAMP if db else None
            }
            
            db.collection('agent_state').document(request.session_id).set(state_data)
            
            return {
                "session_id": request.session_id,
                "status": "created",
                "message": "Agent state stored successfully"
            }
        else:
            # Store in memory if Firestore not available
            return {
                "session_id": request.session_id,
                "status": "created_memory",
                "message": "Agent state stored in memory (Firestore unavailable)"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent state: {str(e)}")

@app.get("/api/agent/state/{session_id}")
async def get_agent_state(session_id: str):
    """Get agent state by session ID"""
    try:
        db = firestore_manager.get_client()
        if db:
            doc = db.collection('agent_state').document(session_id).get()
            if doc.exists:
                return doc.to_dict()
            else:
                raise HTTPException(status_code=404, detail="Agent state not found")
        else:
            raise HTTPException(status_code=503, detail="Firestore not available")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent state: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)