import pkgutil
import importlib.util
import sys


def get_loader(name):
    if name == "__main__":
        class MainLoader:
            def get_filename(self, _):
                return sys.modules["__main__"].__file__
        return MainLoader()
    try:
        spec = importlib.util.find_spec(name)
    except ValueError:
        return None
    return spec.loader if spec else None


pkgutil.get_loader = get_loader
from dotenv import load_dotenv
load_dotenv()

import time
from flask import Flask, request
from flask_cors import CORS

from routes.auth import bp as auth_bp
from routes.plaid import bp as plaid_bp
from routes.transactions import bp as transactions_bp
from routes.inflation import bp as inflation_bp
from routes.assistant import bp as assistant_bp
from routes.uploads import bp as uploads_bp


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:3000"]}})

    @app.after_request
    def add_cache_headers(response):
        if request.method == "GET" and response.status_code == 200:
            response.headers['Cache-Control'] = 'public, max-age=120'
            response.headers['Expires'] = time.strftime(
                '%a, %d %b %Y %H:%M:%S GMT',
                time.gmtime(time.time() + 120)
            )
        return response

    app.register_blueprint(auth_bp)
    app.register_blueprint(plaid_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(inflation_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(uploads_bp)

    @app.get("/healthz")
    def healthz():
        return "ok", 200

    return app


app = create_app()


@app.route("/")
def health_check():
    return {"status": "ok", "message": "Inflate-Wise API"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
