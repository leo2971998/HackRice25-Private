# routes/auth.py
import os, sqlite3, time, hashlib
from flask import Blueprint, request, jsonify, current_app, make_response, g
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("auth", __name__)

def db():
    if "db" not in g:
        g.db = sqlite3.connect("app.db", check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    with sqlite3.connect("app.db") as conn:
        conn.execute("""
          CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT, last_name TEXT,
            nessie_customer_id TEXT,
            role TEXT DEFAULT 'user',
            created_at INTEGER
          );
        """)
        conn.commit()
        
        # Add role column to existing users table if it doesn't exist
        try:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass

@bp.record_once
def _on_load(setup_state):
    with setup_state.app.app_context():
        init_db()

def issue_token(user_id):
    payload = {"uid": user_id, "iat": int(time.time())}
    token = jwt.encode(payload, os.environ.get("FLASK_SECRET", "supersecret_change_me"), algorithm="HS256")
    return token

def require_auth(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("session")
        if not token:
            return jsonify(error="unauthorized"), 401
        try:
            payload = jwt.decode(token, os.environ.get("FLASK_SECRET", "supersecret_change_me"), algorithms=["HS256"])
            g.uid = payload["uid"]
        except Exception:
            return jsonify(error="unauthorized"), 401
        return fn(*args, **kwargs)
    return wrapper

def require_admin(fn):
    """Decorator to require admin role for endpoint access"""
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("session")
        if not token:
            return jsonify(error="unauthorized"), 401
        try:
            payload = jwt.decode(token, os.environ.get("FLASK_SECRET", "supersecret_change_me"), algorithms=["HS256"])
            g.uid = payload["uid"]
            
            # Check if user is admin
            row = db().execute("SELECT role FROM users WHERE id=?", (g.uid,)).fetchone()
            if not row:
                return jsonify(error="user not found"), 401
            
            try:
                user_role = row["role"] if row["role"] else "user"
            except (KeyError, TypeError):
                user_role = "user"
                
            if user_role != "admin":
                return jsonify(error="admin access required"), 403
                
        except Exception:
            return jsonify(error="unauthorized"), 401
        return fn(*args, **kwargs)
    return wrapper

@bp.post("/auth/register")
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    pw = data.get("password") or ""
    first = data.get("first_name") or ""
    last  = data.get("last_name") or ""
    role = data.get("role") or "user"  # Default to 'user', allow 'admin'
    
    # Validate role
    if role not in ["user", "admin"]:
        return jsonify(error="Invalid role. Must be 'user' or 'admin'"), 400
    
    if not email or not pw:
        return jsonify(error="email and password required"), 400
    try:
        db().execute(
          "INSERT INTO users(email,password_hash,first_name,last_name,role,created_at) VALUES(?,?,?,?,?,?)",
          (email, generate_password_hash(pw), first, last, role, int(time.time()))
        )
        db().commit()
    except sqlite3.IntegrityError:
        return jsonify(error="email already registered"), 409
    uid = db().execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]
    resp = make_response(jsonify(ok=True, message=f"{role.title()} account created successfully"))
    resp.set_cookie("session", issue_token(uid), httponly=True, samesite="Lax")
    return resp

@bp.post("/auth/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    pw = data.get("password") or ""
    row = db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not row or not check_password_hash(row["password_hash"], pw):
        return jsonify(error="invalid credentials"), 401
    
    # Get user role (default to 'user' for backwards compatibility)
    try:
        user_role = row["role"] if row["role"] else "user"
    except (KeyError, TypeError):
        user_role = "user"
    
    resp = make_response(jsonify(ok=True, role=user_role))
    resp.set_cookie("session", issue_token(row["id"]), httponly=True, samesite="Lax")
    return resp

@bp.post("/auth/logout")
@require_auth
def logout():
    resp = make_response(jsonify(ok=True))
    resp.delete_cookie("session")
    return resp

@bp.get("/me")
@require_auth
def me():
    row = db().execute("SELECT id,email,first_name,last_name,nessie_customer_id,role FROM users WHERE id=?", (g.uid,)).fetchone()
    user_data = dict(row)
    # Default role to 'user' for backwards compatibility
    if not user_data.get("role"):
        user_data["role"] = "user"
    return jsonify(user_data)