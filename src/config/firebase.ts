// Firebase configuration for TrustAgent frontend
import { initializeApp } from 'firebase/app';
import { getFirestore, connectFirestoreEmulator } from 'firebase/firestore';
import { getAuth, connectAuthEmulator } from 'firebase/auth';

// Firebase configuration object
// In production, these values should come from environment variables
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "demo-api-key",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "demo-project.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "gen-lang-client-0536110235",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "demo-project.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "123456789",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:123456789:web:abcdef"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firestore
export const db = getFirestore(app);

// Initialize Auth
export const auth = getAuth(app);

// Connect to emulators in development
if (import.meta.env.DEV) {
  try {
    // Connect to Firestore emulator if not already connected
    // Note: In a real implementation, you'd check if emulator is already connected
    connectFirestoreEmulator(db, 'localhost', 8080);
    
    // Connect to Auth emulator if not already connected
    connectAuthEmulator(auth, 'http://localhost:9099');
  } catch (error) {
    // Emulators might already be connected or not available
    console.log('Firebase emulators not available or already connected');
  }
}

export default app;