import os, requests
from flask import Blueprint, request, jsonify
# routes/nessie_admin.py
from dotenv import load_dotenv
load_dotenv()

import os
from flask import Blueprint, jsonify, request, g
from .auth import require_auth, require_admin, db
BASE = os.getenv("NESSIE_BASE", "https://api.nessieisreal.com")
API_KEY = os.environ["NESSIE_API_KEY"]  # set in Cloud Run/locally

def nx(path: str):
    return f"{BASE}{path}?key={API_KEY}"

bp = Blueprint("nessie_admin", __name__)

@bp.get("/admin/status")
@require_admin
def admin_status():
    return jsonify({"status": "admin ok"}), 200

@bp.post("/nessie/customers")
@require_admin
def create_customer():
    body = request.get_json() or {}
    # Minimal allowed fields per docs: first_name, last_name, address{street_number, street_name, city, state, zip}
    r = requests.post(nx("/customers"), json=body, timeout=20)
    return (r.json(), r.status_code)

@bp.get("/nessie/customers")
@require_admin
def list_customers():
    r = requests.get(nx("/customers"), timeout=20)
    return (r.json(), r.status_code)

@bp.post("/nessie/customers/<customer_id>/accounts")
@require_admin
def create_account(customer_id):
    body = request.get_json() or {}
    # Example body: {"type":"Checking","nickname":"My Main","rewards":0,"balance":5000}
    r = requests.post(nx(f"/customers/{customer_id}/accounts"), json=body, timeout=20)
    return (r.json(), r.status_code)

@bp.get("/nessie/customers/<customer_id>/accounts")
@require_admin
def list_accounts(customer_id):
    r = requests.get(nx(f"/customers/{customer_id}/accounts"), timeout=20)
    return (r.json(), r.status_code)

@bp.post("/nessie/accounts/<account_id>/deposits")
@require_admin
def add_deposit(account_id):
    body = request.get_json() or {}
    # Typical fields include amount and a description/transaction_date. Use the docs' schema in Swagger to confirm.
    r = requests.post(nx(f"/accounts/{account_id}/deposits"), json=body, timeout=20)
    return (r.json(), r.status_code)

@bp.post("/nessie/accounts/<account_id>/purchases")
@require_admin
def add_purchase(account_id):
    body = request.get_json() or {}
    # Either supply a merchant_id (preferred) or a free-text description + amount per docs.
    r = requests.post(nx(f"/accounts/{account_id}/purchases"), json=body, timeout=20)
    return (r.json(), r.status_code)