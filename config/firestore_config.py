try:
    import firebase_admin
    from firebase_admin import credentials, firestore as admin_firestore
    FIREBASE_ADMIN_AVAILABLE = True
except ImportError:
    print("firebase_admin not available, using fallback to google-cloud-firestore")
    FIREBASE_ADMIN_AVAILABLE = False

import os
from typing import Optional

class FirestoreManager:
    """
    Enhanced Firestore Manager for TrustAgent
    Provides centralized Firebase configuration and connection management
    """
    
    def __init__(self):
        self._db = None
        self._app = None
        self._initialized = False
    
    def initialize(self, service_account_path: Optional[str] = None) -> bool:
        """
        Initialize Firebase app and Firestore client
        
        Args:
            service_account_path: Path to service account JSON file
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if self._initialized:
                return True
            
            if not FIREBASE_ADMIN_AVAILABLE:
                print("Firebase Admin SDK not available, using fallback")
                return False
                
            # Check if Firebase app is already initialized
            try:
                self._app = firebase_admin.get_app()
            except ValueError:
                # Initialize Firebase app
                if service_account_path and os.path.exists(service_account_path):
                    # Use service account credentials
                    cred = credentials.Certificate(service_account_path)
                    self._app = firebase_admin.initialize_app(cred)
                else:
                    # Use default credentials (ADC in production)
                    cred = credentials.ApplicationDefault()
                    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'gen-lang-client-0536110235')
                    self._app = firebase_admin.initialize_app(cred, {
                        'projectId': project_id
                    })
            
            # Initialize Firestore client
            self._db = admin_firestore.client()
            self._initialized = True
            
            return True
            
        except Exception as e:
            print(f"Error initializing FirestoreManager: {e}")
            return False
    
    def get_client(self) -> Optional[object]:
        """
        Get Firestore client instance
        
        Returns:
            Firestore client or None if not initialized
        """
        if not self._initialized:
            self.initialize()
        
        return self._db
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test Firestore connection
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self._initialized:
                success = self.initialize()
                if not success:
                    return False, "Failed to initialize Firestore"
            
            # Test write/read operation
            test_ref = self._db.collection('health_checks').document('firebase_admin_test')
            test_data = {
                'status': 'connected',
                'timestamp': admin_firestore.SERVER_TIMESTAMP if FIREBASE_ADMIN_AVAILABLE else None,
                'service': 'firebase_admin'
            }
            
            test_ref.set(test_data)
            
            # Verify read
            doc = test_ref.get()
            if doc.exists:
                return True, "Firebase Admin SDK connection successful"
            else:
                return False, "Could not read test document"
                
        except Exception as e:
            return False, f"Firebase Admin SDK connection failed: {str(e)}"
    
    def cleanup(self):
        """Clean up Firebase app and connections"""
        try:
            if self._app and FIREBASE_ADMIN_AVAILABLE:
                firebase_admin.delete_app(self._app)
                self._app = None
                self._db = None
                self._initialized = False
        except Exception as e:
            print(f"Error during cleanup: {e}")

# Global instance for easy access
firestore_manager = FirestoreManager()

# Backward compatibility functions to work with existing codebase
def get_firestore_client():
    """Get Firestore client - maintains compatibility with existing code"""
    # Try Firebase Admin SDK first
    client = firestore_manager.get_client()
    if client:
        return client
    
    # Fallback to google-cloud-firestore direct client
    from google.cloud import firestore as gcp_firestore
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'gen-lang-client-0536110235')
        return gcp_firestore.Client(project=project_id)
    except Exception as e:
        print(f"Warning: Could not initialize Firestore client: {e}")
        return None

def test_firestore_connection():
    """Test connection using Firebase Admin SDK"""
    return firestore_manager.test_connection()