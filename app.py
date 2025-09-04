from dotenv import load_dotenv
load_dotenv()

import time
from flask import Flask, make_response, request
from flask_cors import CORS

from routes.auth import bp as auth_bp
from routes.nessie_admin import bp as nessie_admin_bp
from routes.me_nessie import bp as me_nessie_bp
from routes.demo import bp as demo_bp

def create_app():
    app = Flask(__name__)
    # allow your dev frontend to send cookies
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://localhost:5173","http://localhost:3000"]}})
    
    # Add caching middleware for GET requests (120s cache)
    @app.after_request
    def add_cache_headers(response):
        if request.method == "GET" and response.status_code == 200:
            # Cache GET requests for 120 seconds
            response.headers['Cache-Control'] = 'public, max-age=120'
            response.headers['Expires'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', 
                                                      time.gmtime(time.time() + 120))
        return response
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(nessie_admin_bp)
    app.register_blueprint(me_nessie_bp)
    app.register_blueprint(demo_bp)

    @app.get("/healthz")
    def healthz(): return "ok", 200
    
    return app

app = create_app()

@app.route("/")
def health_check():
    return {"status": "ok", "message": "Houston Financial Navigator API"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)