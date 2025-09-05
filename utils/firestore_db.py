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