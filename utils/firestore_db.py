# utils/firestore_db.py
import os
from google.cloud import firestore
from google.cloud.firestore import Client

def get_firestore_client() -> Client:
    """Get Firestore client with proper configuration"""
    try:
        # Initialize Firestore client
        # In production, this will use the service account from Cloud Run
        # In development, it will use GOOGLE_APPLICATION_CREDENTIALS or default auth
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'gen-lang-client-0536110235')
        return firestore.Client(project=project_id)
    except Exception as e:
        print(f"Warning: Could not initialize Firestore client: {e}")
        return None

def test_firestore_connection():
    """Test Firestore connection by writing and reading a test document"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore client could not be initialized"
        
        # Test collection
        test_ref = db.collection('health_checks').document('test')
        
        # Write test data
        test_data = {'status': 'connected', 'timestamp': firestore.SERVER_TIMESTAMP}
        test_ref.set(test_data)
        
        # Read test data
        doc = test_ref.get()
        if doc.exists:
            return True, "Firestore connection successful"
        else:
            return False, "Could not read test document"
            
    except Exception as e:
        return False, f"Firestore connection failed: {str(e)}"

# User operations
def create_user(user_id: str, user_data: dict):
    """Create a new user in Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        user_ref = db.collection('users').document(user_id)
        user_ref.set(user_data)
        return True, "User created successfully"
    except Exception as e:
        return False, f"Failed to create user: {str(e)}"

def get_user(user_id: str):
    """Get user data from Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return None, "Firestore not available"
        
        user_ref = db.collection('users').document(user_id)
        doc = user_ref.get()
        
        if doc.exists:
            return doc.to_dict(), "User found"
        else:
            return None, "User not found"
    except Exception as e:
        return None, f"Failed to get user: {str(e)}"

def update_user(user_id: str, user_data: dict):
    """Update user data in Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        user_ref = db.collection('users').document(user_id)
        user_ref.update(user_data)
        return True, "User updated successfully"
    except Exception as e:
        return False, f"Failed to update user: {str(e)}"

def delete_user(user_id: str):
    """Delete user data from Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        user_ref = db.collection('users').document(user_id)
        user_ref.delete()
        return True, "User deleted successfully"
    except Exception as e:
        return False, f"Failed to delete user: {str(e)}"

# Chat Sessions operations
def create_chat_session(session_id: str, session_data: dict):
    """Create a new chat session in Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        # Add server timestamp
        session_data['created_at'] = firestore.SERVER_TIMESTAMP
        session_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        session_ref = db.collection('chat_sessions').document(session_id)
        session_ref.set(session_data)
        return True, "Chat session created successfully"
    except Exception as e:
        return False, f"Failed to create chat session: {str(e)}"

def get_chat_session(session_id: str):
    """Get chat session data from Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return None, "Firestore not available"
        
        session_ref = db.collection('chat_sessions').document(session_id)
        doc = session_ref.get()
        
        if doc.exists:
            return doc.to_dict(), "Chat session found"
        else:
            return None, "Chat session not found"
    except Exception as e:
        return None, f"Failed to get chat session: {str(e)}"

def update_chat_session(session_id: str, session_data: dict):
    """Update chat session data in Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        # Add updated timestamp
        session_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        session_ref = db.collection('chat_sessions').document(session_id)
        session_ref.update(session_data)
        return True, "Chat session updated successfully"
    except Exception as e:
        return False, f"Failed to update chat session: {str(e)}"

def delete_chat_session(session_id: str):
    """Delete chat session from Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        session_ref = db.collection('chat_sessions').document(session_id)
        session_ref.delete()
        return True, "Chat session deleted successfully"
    except Exception as e:
        return False, f"Failed to delete chat session: {str(e)}"

def add_message_to_session(session_id: str, message: dict):
    """Add a message to an existing chat session"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        # Add timestamp to message
        message['timestamp'] = firestore.SERVER_TIMESTAMP
        
        session_ref = db.collection('chat_sessions').document(session_id)
        session_ref.update({
            'messages': firestore.ArrayUnion([message]),
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return True, "Message added successfully"
    except Exception as e:
        return False, f"Failed to add message: {str(e)}"

def get_user_chat_sessions(user_id: str, limit: int = 10):
    """Get chat sessions for a user"""
    try:
        db = get_firestore_client()
        if not db:
            return [], "Firestore not available"
        
        sessions = db.collection('chat_sessions')\
                    .where('user_id', '==', user_id)\
                    .order_by('updated_at', direction=firestore.Query.DESCENDING)\
                    .limit(limit)\
                    .stream()
        
        session_list = []
        for session in sessions:
            session_data = session.to_dict()
            session_data['id'] = session.id
            session_list.append(session_data)
            
        return session_list, "Sessions retrieved successfully"
    except Exception as e:
        return [], f"Failed to get user chat sessions: {str(e)}"

# AP2 Transactions operations
def create_ap2_transaction(transaction_id: str, transaction_data: dict):
    """Create a new AP2 transaction in Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        # Add server timestamp
        transaction_data['created_at'] = firestore.SERVER_TIMESTAMP
        transaction_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        transaction_ref = db.collection('ap2_transactions').document(transaction_id)
        transaction_ref.set(transaction_data)
        return True, "AP2 transaction created successfully"
    except Exception as e:
        return False, f"Failed to create AP2 transaction: {str(e)}"

def get_ap2_transaction(transaction_id: str):
    """Get AP2 transaction data from Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return None, "Firestore not available"
        
        transaction_ref = db.collection('ap2_transactions').document(transaction_id)
        doc = transaction_ref.get()
        
        if doc.exists:
            return doc.to_dict(), "AP2 transaction found"
        else:
            return None, "AP2 transaction not found"
    except Exception as e:
        return None, f"Failed to get AP2 transaction: {str(e)}"

def update_ap2_transaction(transaction_id: str, transaction_data: dict):
    """Update AP2 transaction data in Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        # Add updated timestamp
        transaction_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        transaction_ref = db.collection('ap2_transactions').document(transaction_id)
        transaction_ref.update(transaction_data)
        return True, "AP2 transaction updated successfully"
    except Exception as e:
        return False, f"Failed to update AP2 transaction: {str(e)}"

def delete_ap2_transaction(transaction_id: str):
    """Delete AP2 transaction from Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        transaction_ref = db.collection('ap2_transactions').document(transaction_id)
        transaction_ref.delete()
        return True, "AP2 transaction deleted successfully"
    except Exception as e:
        return False, f"Failed to delete AP2 transaction: {str(e)}"

def get_user_ap2_transactions(user_id: str, status: str = None, limit: int = 50):
    """Get AP2 transactions for a user"""
    try:
        db = get_firestore_client()
        if not db:
            return [], "Firestore not available"
        
        query = db.collection('ap2_transactions').where('user_id', '==', user_id)
        
        if status:
            query = query.where('status', '==', status)
            
        query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
        
        transactions = query.stream()
        
        transaction_list = []
        for transaction in transactions:
            transaction_data = transaction.to_dict()
            transaction_data['id'] = transaction.id
            transaction_list.append(transaction_data)
            
        return transaction_list, "Transactions retrieved successfully"
    except Exception as e:
        return [], f"Failed to get user AP2 transactions: {str(e)}"

# Agent State operations
def create_agent_state(session_id: str, state_data: dict):
    """Create a new agent state in Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        # Add server timestamp
        state_data['created_at'] = firestore.SERVER_TIMESTAMP
        state_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        state_ref = db.collection('agent_state').document(session_id)
        state_ref.set(state_data)
        return True, "Agent state created successfully"
    except Exception as e:
        return False, f"Failed to create agent state: {str(e)}"

def get_agent_state(session_id: str):
    """Get agent state data from Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return None, "Firestore not available"
        
        state_ref = db.collection('agent_state').document(session_id)
        doc = state_ref.get()
        
        if doc.exists:
            return doc.to_dict(), "Agent state found"
        else:
            return None, "Agent state not found"
    except Exception as e:
        return None, f"Failed to get agent state: {str(e)}"

def update_agent_state(session_id: str, state_data: dict):
    """Update agent state data in Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        # Add updated timestamp
        state_data['updated_at'] = firestore.SERVER_TIMESTAMP
        
        state_ref = db.collection('agent_state').document(session_id)
        state_ref.update(state_data)
        return True, "Agent state updated successfully"
    except Exception as e:
        return False, f"Failed to update agent state: {str(e)}"

def delete_agent_state(session_id: str):
    """Delete agent state from Firestore"""
    try:
        db = get_firestore_client()
        if not db:
            return False, "Firestore not available"
        
        state_ref = db.collection('agent_state').document(session_id)
        state_ref.delete()
        return True, "Agent state deleted successfully"
    except Exception as e:
        return False, f"Failed to delete agent state: {str(e)}"

def get_user_agent_states(user_id: str, limit: int = 10):
    """Get agent states for a user"""
    try:
        db = get_firestore_client()
        if not db:
            return [], "Firestore not available"
        
        states = db.collection('agent_state')\
                   .where('user_id', '==', user_id)\
                   .order_by('updated_at', direction=firestore.Query.DESCENDING)\
                   .limit(limit)\
                   .stream()
        
        state_list = []
        for state in states:
            state_data = state.to_dict()
            state_data['id'] = state.id
            state_list.append(state_data)
            
        return state_list, "Agent states retrieved successfully"
    except Exception as e:
        return [], f"Failed to get user agent states: {str(e)}"

# Real-time listeners for chat updates
def listen_to_chat_session(session_id: str, callback):
    """Set up real-time listener for chat session updates"""
    try:
        db = get_firestore_client()
        if not db:
            return None, "Firestore not available"
        
        session_ref = db.collection('chat_sessions').document(session_id)
        
        def on_snapshot(doc_snapshot, changes, read_time):
            for doc in doc_snapshot:
                if doc.exists:
                    callback(doc.to_dict())
        
        # Return the listener so it can be detached later
        listener = session_ref.on_snapshot(on_snapshot)
        return listener, "Listener created successfully"
    except Exception as e:
        return None, f"Failed to create listener: {str(e)}"

# Utility functions for data management
def cleanup_expired_data():
    """Clean up expired chat sessions and agent states"""
    try:
        db = get_firestore_client()
        if not db:
            return 0, "Firestore not available"
        
        # Define expiry time (e.g., 7 days ago)
        from datetime import datetime, timedelta
        expiry_time = datetime.now() - timedelta(days=7)
        
        # Clean up old chat sessions
        old_sessions = db.collection('chat_sessions')\
                        .where('updated_at', '<', expiry_time)\
                        .stream()
        
        sessions_deleted = 0
        for session in old_sessions:
            session.reference.delete()
            sessions_deleted += 1
        
        # Clean up old agent states
        old_states = db.collection('agent_state')\
                      .where('updated_at', '<', expiry_time)\
                      .stream()
        
        states_deleted = 0
        for state in old_states:
            state.reference.delete()
            states_deleted += 1
        
        total_deleted = sessions_deleted + states_deleted
        return total_deleted, f"Cleaned up {sessions_deleted} sessions and {states_deleted} agent states"
    except Exception as e:
        return 0, f"Failed to cleanup expired data: {str(e)}"

def get_collection_stats():
    """Get statistics about all collections"""
    try:
        db = get_firestore_client()
        if not db:
            return {}, "Firestore not available"
        
        stats = {}
        collections = ['users', 'chat_sessions', 'ap2_transactions', 'agent_state']
        
        for collection_name in collections:
            docs = db.collection(collection_name).stream()
            count = sum(1 for _ in docs)
            stats[collection_name] = count
        
        return stats, "Statistics retrieved successfully"
    except Exception as e:
        return {}, f"Failed to get collection stats: {str(e)}"