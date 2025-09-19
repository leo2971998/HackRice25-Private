import React, { useState, useEffect, useRef } from 'react';
import { collection, query, orderBy, onSnapshot, addDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '../config/firebase';
import { useAuth } from '@/context/Auth';
import './ChatInterface.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  mandateId?: string;
  type?: 'text' | 'mandate' | 'system';
}

interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
  messageCount: number;
}

interface AP2MandateData {
  type: 'intent' | 'cart' | 'payment';
  data: any;
  autoApproved?: boolean;
  trustScore?: number;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { user } = useAuth();
  const userId = user?.id || 'anonymous';
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize chat session
  useEffect(() => {
    if (!currentSessionId) {
      createNewChatSession();
    }
  }, []);

  // Listen to chat sessions in sidebar
  useEffect(() => {
    if (!userId) return;

    const sessionsQuery = query(
      collection(db, 'chat_sessions'),
      orderBy('updated_at', 'desc')
    );

    const unsubscribe = onSnapshot(sessionsQuery, (snapshot) => {
      const sessions: ChatSession[] = [];
      snapshot.forEach((doc) => {
        const data = doc.data();
        if (data.user_id === userId) {
          sessions.push({
            id: doc.id,
            title: data.title || 'Chat Session',
            lastMessage: data.last_message || 'No messages',
            timestamp: data.updated_at?.toDate() || new Date(),
            messageCount: data.message_count || 0
          });
        }
      });
      setChatSessions(sessions);
    });

    return () => unsubscribe();
  }, [userId]);

  // Listen to messages for current session
  useEffect(() => {
    if (!currentSessionId) return;

    const messagesQuery = query(
      collection(db, 'chat_sessions', currentSessionId, 'messages'),
      orderBy('timestamp', 'asc')
    );

    const unsubscribe = onSnapshot(messagesQuery, (snapshot) => {
      const newMessages: Message[] = [];
      snapshot.forEach((doc) => {
        const data = doc.data();
        newMessages.push({
          id: doc.id,
          text: data.content || data.text,
          sender: data.role === 'user' ? 'user' : 'agent',
          timestamp: data.timestamp?.toDate() || new Date(),
          mandateId: data.mandate_id,
          type: data.type || 'text'
        });
      });
      setMessages(newMessages);
    });

    return () => unsubscribe();
  }, [currentSessionId]);

  const createNewChatSession = async () => {
    try {
      const sessionData = {
        user_id: userId,
        title: `Chat ${new Date().toLocaleDateString()}`,
        created_at: serverTimestamp(),
        updated_at: serverTimestamp(),
        message_count: 0,
        last_message: 'New chat session'
      };

      const docRef = await addDoc(collection(db, 'chat_sessions'), sessionData);
      setCurrentSessionId(docRef.id);
      setMessages([]);
      
      // Add welcome message
      await addMessage('agent', 'Hello! I\'m Inflate-Wise, your AI financial co-pilot. I can help you understand your personal inflation rate, analyze your spending patterns, and provide insights to combat inflation. How can I assist you today?', 'system');
    } catch (error) {
      console.error('Error creating chat session:', error);
    }
  };

  const addMessage = async (sender: 'user' | 'agent', text: string, type: string = 'text', mandateId?: string) => {
    if (!currentSessionId) return;

    try {
      const messageData = {
        content: text,
        role: sender,
        timestamp: serverTimestamp(),
        type: type,
        mandate_id: mandateId
      };

      await addDoc(collection(db, 'chat_sessions', currentSessionId, 'messages'), messageData);

      // Update session last message
      const sessionRef = collection(db, 'chat_sessions');
      // Note: In a real implementation, you'd update the session document here
    } catch (error) {
      console.error('Error adding message:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setIsLoading(true);

    // Add user message
    await addMessage('user', userMessage);

    try {
      // Process message through AP2 agent
      const response = await processMessageWithAP2Agent(userMessage);
      
      // Add agent response
      await addMessage('agent', response.text, response.type, response.mandateId);
      
    } catch (error) {
      console.error('Error processing message:', error);
      await addMessage('agent', 'Sorry, I encountered an error processing your request. Please try again.', 'system');
    } finally {
      setIsLoading(false);
    }
  };

  const processMessageWithAP2Agent = async (message: string): Promise<{text: string, type: string, mandateId?: string}> => {
    // Simple intent detection (in a real app, use NLP)
    const lowerMessage = message.toLowerCase();
    
    try {
      // Intent mandate detection
      if (lowerMessage.includes('save') && (lowerMessage.includes('goal') || lowerMessage.includes('money'))) {
        const amount = extractAmount(message) || 500;
        const mandate = await createAP2Mandate('intent', {
          intent_type: 'savings_goal',
          amount: amount,
          frequency: 'monthly',
          description: `Save $${amount} monthly based on user request`
        });
        
        return {
          text: `I've created a savings goal mandate for $${amount} monthly. This has been ${mandate.auto_approved ? 'automatically approved' : 'submitted for review'} with a trust score of ${mandate.trust_score}%. Mandate ID: ${mandate.mandate_id}`,
          type: 'mandate',
          mandateId: mandate.mandate_id
        };
      }
      
      // Payment mandate detection
      if (lowerMessage.includes('pay') || lowerMessage.includes('transfer') || lowerMessage.includes('emergency')) {
        const amount = extractAmount(message) || 100;
        const urgency = lowerMessage.includes('emergency') ? 'emergency' : 'normal';
        
        const mandate = await createAP2Mandate('payment', {
          amount: amount,
          purpose: 'User requested payment',
          urgency: urgency
        });
        
        return {
          text: `I've created a payment mandate for $${amount} with ${urgency} priority. This has been ${mandate.auto_approved ? 'automatically approved' : 'submitted for review'} with a trust score of ${mandate.trust_score}%. Mandate ID: ${mandate.mandate_id}`,
          type: 'mandate',
          mandateId: mandate.mandate_id
        };
      }
      
      // Cart mandate detection
      if (lowerMessage.includes('subscription') || lowerMessage.includes('recurring')) {
        const amount = extractAmount(message) || 25;
        const mandate = await createAP2Mandate('cart', {
          items: [{ name: 'Subscription Service', price: amount }],
          total_amount: amount,
          subscription_type: 'monthly'
        });
        
        return {
          text: `I've created a subscription mandate for $${amount} monthly. This has been ${mandate.auto_approved ? 'automatically approved' : 'submitted for review'} with a trust score of ${mandate.trust_score}%. Mandate ID: ${mandate.mandate_id}`,
          type: 'mandate',
          mandateId: mandate.mandate_id
        };
      }
      
      // General financial assistance
      return {
        text: `I understand you're asking about "${message}". I can help you with:
        
        🎯 **Financial Goals**: Set savings targets and budget alerts
        🛒 **Smart Purchases**: Manage subscriptions and recurring payments  
        💳 **Secure Payments**: Process emergency transactions with AP2 protocol
        📊 **Financial Analysis**: Track spending patterns and insights
        
        Try saying things like:
        - "Help me save $500 monthly"
        - "Set up a $25 subscription"
        - "I need an emergency payment of $200"`,
        type: 'text'
      };
      
    } catch (error) {
      console.error('Error calling AP2 agent:', error);
      return {
        text: 'I apologize, but I\'m having trouble connecting to the AP2 agent right now. Please try again in a moment.',
        type: 'system'
      };
    }
  };

  const createAP2Mandate = async (type: 'intent' | 'cart' | 'payment', data: any) => {
    const response = await fetch(`/api/mandates/${type}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        ...data
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to create AP2 mandate');
    }
    
    return await response.json();
  };

  const extractAmount = (text: string): number | null => {
    const match = text.match(/\$?(\d+(?:,\d{3})*(?:\.\d{2})?)/);
    return match ? parseFloat(match[1].replace(',', '')) : null;
  };

  const selectChatSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="chat-interface">
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <h3>Chat History</h3>
          <button 
            className="new-chat-btn"
            onClick={createNewChatSession}
          >
            + New Chat
          </button>
        </div>
        
        <div className="chat-sessions">
          {chatSessions.map((session) => (
            <div
              key={session.id}
              className={`chat-session-item ${session.id === currentSessionId ? 'active' : ''}`}
              onClick={() => selectChatSession(session.id)}
            >
              <div className="session-title">{session.title}</div>
              <div className="session-preview">{session.lastMessage}</div>
              <div className="session-time">
                {session.timestamp.toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        <div className="chat-header">
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <h2>Inflate-Wise - AI Financial Co-Pilot</h2>
        </div>

        <div className="messages-container">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender} ${message.type}`}
            >
              <div className="message-content">
                {message.text}
              </div>
              <div className="message-timestamp">
                {message.timestamp.toLocaleTimeString()}
              </div>
              {message.mandateId && (
                <div className="mandate-id">
                  Mandate: {message.mandateId}
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="message agent loading">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about savings goals, payments, or financial planning..."
            disabled={isLoading}
            className="message-input"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className="send-button"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;