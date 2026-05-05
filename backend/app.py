"""
Personal Finance Advisor — Flask Backend
Entry point: registers all blueprints and starts the dev server.
"""

import os
import sys
from datetime import timedelta

# Ensure the backend directory is on the Python path so that
# 'from config import ...' and 'from utils import ...' work correctly
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import JWT_SECRET_KEY
from routes.auth         import auth_bp
from routes.transactions import transactions_bp
from routes.categories   import categories_bp
from routes.budgets      import budgets_bp
from routes.upload       import upload_bp
from routes.categorize   import categorize_bp
from routes.recommendations import recommendations_bp
from routes.analytics    import analytics_bp
from routes.chatbot      import chatbot_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # ── JWT Configuration ────────────────────────────────────────────────────
    app.config['JWT_SECRET_KEY']       = JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

    jwt = JWTManager(app)

    # ── JWT Error Handlers ───────────────────────────────────────────────────
    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"success": False, "error": "Authentication required", "reason": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"success": False, "error": "Invalid token", "reason": reason}), 422

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify({"success": False, "error": "Token has expired"}), 401

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Max upload size (16 MB) ───────────────────────────────────────────────
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # ── Register Blueprints ───────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(categorize_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(chatbot_bp)

    # ── Health-check route ────────────────────────────────────────────────────
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok", "version": "1.0.0",
                        "service": "Personal Finance Advisor API"}), 200

    # ── Root info route ───────────────────────────────────────────────────────
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            "message": "Personal Finance Advisor API is running.",
            "endpoints": {
                "register":           "POST /api/auth/register",
                "login":              "POST /api/auth/login",
                "me":                 "GET  /api/auth/me",
                "logout":             "POST /api/auth/logout",
                "transactions":       "GET  /api/transactions",
                "add_transaction":    "POST /api/transactions",
                "delete_transaction": "DELETE /api/transactions/<id>",
                "tx_summary":         "GET  /api/transactions/summary",
                "categories":         "GET  /api/categories",
                "budgets":            "GET  /api/budgets",
                "set_budget":         "POST /api/budgets",
                "budget_summary":     "GET  /api/budgets/summary",
                "budget_alerts":      "GET  /api/budgets/alerts",
                "recommendations":    "GET  /api/recommendations",
                "analytics_trends":   "GET  /api/analytics/trends",
                "analytics_dist":     "GET  /api/analytics/distribution",
                "analytics_metrics":  "GET  /api/analytics/metrics",
                "upload_csv":         "POST /api/upload/csv",
                "chatbot":            "POST /api/chat",
            }
        }), 200

    # ── Global error handlers ─────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "Method not allowed"}), 405

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"success": False, "error": "File too large. Maximum size is 16 MB"}), 413

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app


if __name__ == '__main__':
    flask_app = create_app()
    flask_app.run(host='0.0.0.0', port=5000, debug=True)
