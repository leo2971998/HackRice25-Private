from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS

from routes.auth import bp as auth_bp
from routes.nessie_admin import bp as nessie_admin_bp
from routes.me_nessie import bp as me_nessie_bp

def create_app():
    app = Flask(__name__)
    # allow your dev frontend to send cookies
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://localhost:5173","http://localhost:3000"]}})
    app.register_blueprint(auth_bp)
    app.register_blueprint(nessie_admin_bp)
    app.register_blueprint(me_nessie_bp)

    @app.get("/healthz")
    def healthz(): return "ok", 200
    
    return app

app = create_app()

@app.route("/")
def health_check():
    return {"status": "ok", "message": "Houston Financial Navigator API"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)