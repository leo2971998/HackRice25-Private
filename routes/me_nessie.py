# routes/me_nessie.py
import os, requests, sqlite3
from flask import Blueprint, request, jsonify, g
from .auth import require_auth, db

BASE = os.getenv("NESSIE_BASE", "https://api.nessieisreal.com")
API_KEY = os.environ.get("NESSIE_API_KEY", "")

bp = Blueprint("me_nessie", __name__)

def nx(path): 
    return f"{BASE}{path}?key={API_KEY}"

@bp.post("/me/seed")         # create Nessie customer + default checking if missing
@require_auth
def seed():
    u = db().execute("SELECT * FROM users WHERE id=?", (g.uid,)).fetchone()
    cust_id = u["nessie_customer_id"]
    # 1) create customer if missing
    if not cust_id:
        body = {
          "first_name": u["first_name"] or "Houston",
          "last_name":  u["last_name"] or "Resident",
          "address": { "street_number":"123","street_name":"Main St","city":"Houston","state":"TX","zip":"77002" }
        }
        r = requests.post(nx("/customers"), json=body, timeout=20)
        r.raise_for_status()
        cust_id = r.json()["_id"]
        db().execute("UPDATE users SET nessie_customer_id=? WHERE id=?", (cust_id, g.uid))
        db().commit()
    # 2) if no accounts, create a checking account and a couple txns
    r2 = requests.get(nx(f"/customers/{cust_id}/accounts"), timeout=20).json()
    if not r2:
        acc = requests.post(nx(f"/customers/{cust_id}/accounts"),
            json={"type":"Checking","nickname":"Main Checking","rewards":0,"balance":1200}, timeout=20).json()
        aid = acc["_id"]
        # seed 1 deposit + 2 purchases
        requests.post(nx(f"/accounts/{aid}/deposits"),  json={"amount":1200,"description":"Paycheck","transaction_date":"2025-09-01"}, timeout=20)
        requests.post(nx(f"/accounts/{aid}/purchases"), json={"amount":42.35,"description":"H-E-B Groceries","purchase_date":"2025-09-02"}, timeout=20)
        requests.post(nx(f"/accounts/{aid}/purchases"), json={"amount":16.80,"description":"Shell Gas","purchase_date":"2025-09-03"}, timeout=20)
    return jsonify(ok=True, customer_id=cust_id)

@bp.get("/me/summary")
@require_auth
def my_summary():
    u = db().execute("SELECT nessie_customer_id FROM users WHERE id=?", (g.uid,)).fetchone()
    if not u or not u["nessie_customer_id"]:
        return jsonify(error="no_nessie_customer"), 404
    
    # Get accounts for this customer
    cust_id = u["nessie_customer_id"]
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
            
            recent_transactions = deposits + purchases
            # Sort by date (most recent first)
            recent_transactions.sort(key=lambda x: x.get("transaction_date", x.get("purchase_date", "")), reverse=True)
            recent_transactions = recent_transactions[:10]  # Last 10 transactions
        
        return jsonify({
            "total_balance": total_balance,
            "accounts": accounts,
            "recent_transactions": recent_transactions,
            "customer_id": cust_id
        })
    except Exception as e:
        return jsonify(error=f"Failed to fetch summary: {str(e)}"), 500