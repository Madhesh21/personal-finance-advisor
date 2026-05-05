"""
Authentication routes — register, login, me, logout.
JWT tokens (HS256) are returned on successful register/login.
"""

import re
import bcrypt
import mysql.connector
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config import get_db_connection

auth_bp = Blueprint('auth', __name__)

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


# ── POST /api/auth/register ──────────────────────────────────────────────────

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register a new user account.
    Body (JSON): { "name": "...", "email": "...", "password": "...", "phone": "..." }
    Returns:     { "success": true, "token": "...", "user": { ... } }
    """
    data = request.get_json() or {}

    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')
    phone    = data.get('phone', '').strip()

    errors = []
    if not name:
        errors.append("Full name is required")
    if not email or not _EMAIL_RE.match(email):
        errors.append("A valid email address is required")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"success": False,
                            "error": "An account with this email already exists"}), 409

        cursor.execute(
            "INSERT INTO users (name, email, password_hash, phone) VALUES (%s, %s, %s, %s)",
            (name, email, pw_hash, phone or None)
        )
        conn.commit()
        user_id = cursor.lastrowid

        cursor.execute(
            "SELECT user_id, name, email, phone, created_at FROM users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        user['created_at'] = str(user['created_at'])

        token = create_access_token(identity=str(user_id))
        return jsonify({
            "success": True,
            "message": "Account created successfully",
            "token":   token,
            "user":    user,
        }), 201

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ── POST /api/auth/login ─────────────────────────────────────────────────────

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Log in an existing user.
    Body (JSON): { "email": "...", "password": "..." }
    Returns:     { "success": true, "token": "...", "user": { ... } }
    """
    data = request.get_json() or {}

    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"success": False,
                        "error": "Email and password are required"}), 400

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT user_id, name, email, phone, password_hash, created_at "
            "FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()

        if not user or not bcrypt.checkpw(
            password.encode('utf-8'), user['password_hash'].encode('utf-8')
        ):
            return jsonify({"success": False,
                            "error": "Invalid email or password"}), 401

        token = create_access_token(identity=str(user['user_id']))
        return jsonify({
            "success": True,
            "message": "Logged in successfully",
            "token":   token,
            "user": {
                "user_id":    user['user_id'],
                "name":       user['name'],
                "email":      user['email'],
                "phone":      user['phone'],
                "created_at": str(user['created_at']),
            },
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ── GET /api/auth/me ─────────────────────────────────────────────────────────

@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def me():
    """
    Returns the currently authenticated user's profile.
    Requires: Authorization: Bearer <token>
    """
    user_id = get_jwt_identity()
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT user_id, name, email, phone, created_at FROM users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404

        user['created_at'] = str(user['created_at'])
        return jsonify({"success": True, "user": user}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ── POST /api/auth/logout ─────────────────────────────────────────────────────

@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Stateless logout — client discards the token."""
    return jsonify({"success": True, "message": "Logged out successfully"}), 200
