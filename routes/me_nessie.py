# routes/me_nessie.py
import os, requests, sqlite3, uuid, time
from flask import Blueprint, request, jsonify, g
from .auth import require_auth, db
from dotenv import load_dotenv
load_dotenv()

import os
from flask import Blueprint, jsonify, request, g
from .auth import require_auth, db
BASE = os.getenv("NESSIE_BASE", "https://api.nessieisreal.com")
API_KEY = os.environ.get("NESSIE_API_KEY", "")
USE_MOCK = os.environ.get("USE_MOCK", "0") == "1"

bp = Blueprint("me_nessie", __name__)

def nx(path): 
    return f"{BASE}{path}?key={API_KEY}"
@bp.get("/me/nessie")
@require_auth
def me_nessie():
    return jsonify({"nessie": "user data"}), 200
# Enhanced mock data for better demo experience
ENHANCED_MOCK_SUMMARY = {
    "total_balance": 1140.85,
    "accounts": [{
        "_id": "mock_account_001",
        "type": "Checking",
        "nickname": "Main Checking",
        "balance": 1140.85,
        "rewards": 0
    }],
    "recent_transactions": [
        {"description": "Metro Transit", "amount": 15.00, "purchase_date": "2025-01-15", "type": "purchase"},
        {"description": "CVS Pharmacy", "amount": 28.47, "purchase_date": "2025-01-14", "type": "purchase"},
        {"description": "Starbucks Coffee", "amount": 4.95, "purchase_date": "2025-01-13", "type": "purchase"},
        {"description": "Shell Gas Station", "amount": 45.20, "purchase_date": "2025-01-12", "type": "purchase"},
        {"description": "H-E-B Groceries", "amount": 87.33, "purchase_date": "2025-01-11", "type": "purchase"},
        {"description": "Uber Ride", "amount": 12.50, "purchase_date": "2025-01-10", "type": "purchase"},
        {"description": "Electric Bill", "amount": 89.45, "purchase_date": "2025-01-08", "type": "purchase"},
        {"description": "Water Bill", "amount": 34.20, "purchase_date": "2025-01-07", "type": "purchase"},
        {"description": "Internet Service", "amount": 79.99, "purchase_date": "2025-01-05", "type": "purchase"},
        {"description": "Target", "amount": 156.78, "purchase_date": "2025-01-03", "type": "purchase"},
        {"description": "Paycheck Deposit", "amount": 1350.00, "transaction_date": "2025-01-09", "type": "deposit"},
        {"description": "Freelance Payment", "amount": 450.00, "transaction_date": "2025-01-02", "type": "deposit"}
    ],
    "customer_id": "mock_customer_enhanced"
}

@bp.post("/me/seed")         # create Nessie customer + default checking if missing
@require_auth
def seed():
    u = db().execute("SELECT * FROM users WHERE id=?", (g.uid,)).fetchone()
    cust_id = u["nessie_customer_id"]
    
    # For demo purposes, if we can't reach Nessie API, create a mock customer ID
    if not cust_id:
        try:
            # Use mock mode if enabled
            if USE_MOCK:
                cust_id = f"mock_{str(uuid.uuid4())[:8]}"
            else:
                body = {
                  "first_name": u["first_name"] or "Houston",
                  "last_name":  u["last_name"] or "Resident",
                  "address": { "street_number":"123","street_name":"Main St","city":"Houston","state":"TX","zip":"77002" }
                }
                r = requests.post(nx("/customers"), json=body, timeout=20)
                r.raise_for_status()
                cust_id = r.json()["_id"]
        except Exception as e:
            # If Nessie API is not available, create a mock customer ID for demo
            print(f"Nessie API error: {e}, falling back to mock")
            cust_id = f"mock_fallback_{str(uuid.uuid4())[:8]}"
        
        db().execute("UPDATE users SET nessie_customer_id=? WHERE id=?", (cust_id, g.uid))
        db().commit()
    
    # Try to create accounts, but don't fail if API is unavailable
    try:
        if cust_id.startswith("mock"):
            # Don't try to seed mock customers with real API calls
            pass
        else:
            r2 = requests.get(nx(f"/customers/{cust_id}/accounts"), timeout=20).json()
            if not r2:
                acc = requests.post(nx(f"/customers/{cust_id}/accounts"),
                    json={"type":"Checking","nickname":"Main Checking","rewards":0,"balance":1200}, timeout=20).json()
                aid = acc["_id"]
                # seed 1 deposit + 2 purchases
                requests.post(nx(f"/accounts/{aid}/deposits"),  json={"amount":1200,"description":"Paycheck","transaction_date":"2025-09-01"}, timeout=20)
                requests.post(nx(f"/accounts/{aid}/purchases"), json={"amount":42.35,"description":"H-E-B Groceries","purchase_date":"2025-09-02"}, timeout=20)
                requests.post(nx(f"/accounts/{aid}/purchases"), json={"amount":16.80,"description":"Shell Gas","purchase_date":"2025-09-03"}, timeout=20)
    except Exception:
        # API not available, but we still have a customer ID for demo
        pass
        
    return jsonify(ok=True, customer_id=cust_id)

@bp.get("/me/summary")
@require_auth
def my_summary():
    u = db().execute("SELECT nessie_customer_id FROM users WHERE id=?", (g.uid,)).fetchone()
    if not u or not u["nessie_customer_id"]:
        return jsonify(error="no_nessie_customer"), 404
    
    # Get accounts for this customer
    cust_id = u["nessie_customer_id"]
    
    # If we're in mock mode or this is a mock customer ID, return enhanced mock data
    if USE_MOCK or cust_id.startswith("mock"):
        return jsonify(ENHANCED_MOCK_SUMMARY)
    
    try:
        accounts_resp = requests.get(nx(f"/customers/{cust_id}/accounts"), timeout=20)
        accounts = accounts_resp.json() if accounts_resp.status_code == 200 else []
        
        total_balance = sum(acc.get("balance", 0) for acc in accounts)
        
        # Get recent transactions from first account if exists
        recent_transactions = []
        if accounts:
            account_id = accounts[0]["_id"]
            # Get deposits
            deposits_resp = requests.get(nx(f"/accounts/{account_id}/deposits"), timeout=20)
            deposits = deposits_resp.json() if deposits_resp.status_code == 200 else []
            # Get purchases  
            purchases_resp = requests.get(nx(f"/accounts/{account_id}/purchases"), timeout=20)
            purchases = purchases_resp.json() if purchases_resp.status_code == 200 else []
            
            # Add transaction type for easier processing
            for deposit in deposits:
                deposit["type"] = "deposit"
            for purchase in purchases:
                purchase["type"] = "purchase"
            
            recent_transactions = deposits + purchases
            # Sort by date (most recent first)
            recent_transactions.sort(key=lambda x: x.get("transaction_date", x.get("purchase_date", "")), reverse=True)
            recent_transactions = recent_transactions[:25]  # Last 25 transactions
        
        return jsonify({
            "total_balance": total_balance,
            "accounts": accounts,
            "recent_transactions": recent_transactions,
            "customer_id": cust_id
        })
    except Exception as e:
        # If API fails, fall back to mock data
        print(f"Nessie API error in summary: {e}, falling back to mock")
        return jsonify(ENHANCED_MOCK_SUMMARY)