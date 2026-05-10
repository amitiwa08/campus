"""
Flask AI Service for Compliance Training Manager.
AI Developer 2 responsibility.
Port: 5000
"""

import logging
import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from routes.ai_routes import ai_bp, init_clients

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["30 per minute"],
)

# Special rate limit for expensive endpoints
limiter.limit("10 per minute")(ai_bp)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(429)
def rate_limit_exceeded(error):
    return (
        jsonify(
            {
                "error": "Rate limit exceeded",
                "retry_after": 60,
            }
        ),
        429,
    )


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# Root endpoint
@app.route("/")
def index():
    return jsonify({"message": "AI Service is running. Access /api/ai/health for status."}), 200

# Register blueprints
app.register_blueprint(ai_bp)


# Startup event
@app.before_request
def startup():
    """Initialize clients on first request."""
    global clients_initialized
    if not hasattr(app, "clients_initialized"):
        try:
            init_clients()
            app.clients_initialized = True
            logger.info("AI service ready")
        except Exception as e:
            logger.error(f"Startup error: {e}")
            return jsonify({"error": "Service unavailable"}), 503


if __name__ == "__main__":
    port = int(os.getenv("AI_PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"

    logger.info(f"Starting AI service on port {port}")
    app.run(host="0.0.0.0", port=port, debug=debug, threaded=True)
