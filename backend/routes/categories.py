from flask import Blueprint, request, jsonify
from config import get_db_connection
import mysql.connector

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/api/categories', methods=['GET'])
def get_categories():
    """
    GET /api/categories
    Returns all categories, optionally filtered by type.
    Query params:
      - type: 'INCOME' | 'EXPENSE'  (optional)
    """
    cat_type = request.args.get('type', None)

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if cat_type and cat_type.upper() in ('INCOME', 'EXPENSE'):
            cursor.execute(
                "SELECT * FROM categories WHERE category_type = %s ORDER BY category_name",
                (cat_type.upper(),)
            )
        else:
            cursor.execute("SELECT * FROM categories ORDER BY category_type, category_name")

        categories = cursor.fetchall()
        return jsonify({"success": True, "data": categories}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


@categories_bp.route('/api/categories', methods=['POST'])
def add_category():
    """
    POST /api/categories
    Add a custom category.
    Body (JSON): { "category_name": "...", "category_type": "INCOME" | "EXPENSE" }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No JSON body provided"}), 400

    name = data.get('category_name', '').strip()
    cat_type = data.get('category_type', '').strip().upper()

    # Validate
    if not name:
        return jsonify({"success": False, "error": "category_name is required"}), 400
    if cat_type not in ('INCOME', 'EXPENSE'):
        return jsonify({"success": False, "error": "category_type must be INCOME or EXPENSE"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check duplicate
        cursor.execute(
            "SELECT category_id FROM categories WHERE category_name = %s AND category_type = %s",
            (name, cat_type)
        )
        if cursor.fetchone():
            return jsonify({"success": False, "error": "Category already exists"}), 409

        cursor.execute(
            "INSERT INTO categories (category_name, category_type) VALUES (%s, %s)",
            (name, cat_type)
        )
        conn.commit()
        new_id = cursor.lastrowid

        return jsonify({
            "success": True,
            "message": "Category created",
            "data": {"category_id": new_id, "category_name": name, "category_type": cat_type}
        }), 201

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
