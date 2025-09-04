from flask import Flask
from flask_cors import CORS
from routes.nessie_admin import bp as nessie_admin_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(nessie_admin_bp)

@app.route("/")
def health_check():
    return {"status": "ok", "message": "Houston Financial Navigator API"}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)