from flask import Blueprint, request, jsonify
from config import get_db_connection
import mysql.connector

budgets_bp = Blueprint('budgets', __name__)


@budgets_bp.route('/api/budgets', methods=['GET'])
def get_budgets():
    """
    GET /api/budgets
    Returns all budget limits for a user.
    Query params:
      - user_id: int (default: 1)
      - month_year: 'YYYY-MM' (default: current month)
    """
    user_id   = request.args.get('user_id', 1, type=int)
    from datetime import datetime
    month_year = request.args.get('month_year', datetime.now().strftime('%Y-%m'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT b.budget_id, b.user_id, b.category_id,
                   c.category_name, c.category_type,
                   b.monthly_limit, b.month_year
            FROM budgets b
            JOIN categories c ON b.category_id = c.category_id
            WHERE b.user_id = %s AND b.month_year = %s
            ORDER BY c.category_name
        """
        cursor.execute(query, (user_id, month_year))
        budgets = cursor.fetchall()

        return jsonify({"success": True, "data": budgets, "month_year": month_year}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


@budgets_bp.route('/api/budgets', methods=['POST'])
def set_budget():
    """
    POST /api/budgets
    Set or update a monthly budget for a category.
    Body (JSON): {
        "user_id": 1,
        "category_id": 3,
        "monthly_limit": 500.00,
        "month_year": "2026-03"   (optional, defaults to current month)
    }
    """
    from datetime import datetime
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No JSON body provided"}), 400

    user_id       = data.get('user_id', 1)
    category_id   = data.get('category_id')
    monthly_limit = data.get('monthly_limit')
    month_year    = data.get('month_year', datetime.now().strftime('%Y-%m'))

    # Validate required fields
    if category_id is None:
        return jsonify({"success": False, "error": "category_id is required"}), 400
    if monthly_limit is None or float(monthly_limit) < 0:
        return jsonify({"success": False, "error": "monthly_limit must be a non-negative number"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Upsert: update if exists, insert otherwise
        cursor.execute(
            "SELECT budget_id FROM budgets WHERE user_id=%s AND category_id=%s AND month_year=%s",
            (user_id, category_id, month_year)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE budgets SET monthly_limit=%s WHERE budget_id=%s",
                (float(monthly_limit), existing['budget_id'])
            )
            msg = "Budget updated"
            budget_id = existing['budget_id']
        else:
            cursor.execute(
                "INSERT INTO budgets (user_id, category_id, monthly_limit, month_year) VALUES (%s,%s,%s,%s)",
                (user_id, category_id, float(monthly_limit), month_year)
            )
            msg = "Budget created"
            budget_id = cursor.lastrowid

        conn.commit()
        return jsonify({
            "success": True,
            "message": msg,
            "data": {
                "budget_id": budget_id,
                "user_id": user_id,
                "category_id": category_id,
                "monthly_limit": float(monthly_limit),
                "month_year": month_year
            }
        }), 200 if existing else 201

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


@budgets_bp.route('/api/budgets/summary', methods=['GET'])
def budget_summary():
    """
    GET /api/budgets/summary
    Returns actual vs planned spending per category for a given month.
    Query params:
      - user_id: int (default: 1)
      - month_year: 'YYYY-MM'
    """
    from datetime import datetime
    user_id    = request.args.get('user_id', 1, type=int)
    month_year = request.args.get('month_year', datetime.now().strftime('%Y-%m'))
    year, month = month_year.split('-')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                c.category_id,
                c.category_name,
                COALESCE(b.monthly_limit, 0)                        AS budget_limit,
                COALESCE(SUM(t.amount), 0)                          AS actual_spent,
                COALESCE(b.monthly_limit, 0) - COALESCE(SUM(t.amount), 0) AS remaining
            FROM categories c
            LEFT JOIN budgets b
                ON b.category_id = c.category_id
                AND b.user_id = %s
                AND b.month_year = %s
            LEFT JOIN transactions t
                ON t.category_id = c.category_id
                AND t.user_id = %s
                AND t.transaction_type = 'EXPENSE'
                AND YEAR(t.transaction_date) = %s
                AND MONTH(t.transaction_date) = %s
            WHERE c.category_type = 'EXPENSE'
            GROUP BY c.category_id, c.category_name, b.monthly_limit
            ORDER BY actual_spent DESC
        """
        cursor.execute(query, (user_id, month_year, user_id, int(year), int(month)))
        summary = cursor.fetchall()

        # Convert Decimal to float for JSON serialisation
        for row in summary:
            for k in ('budget_limit', 'actual_spent', 'remaining'):
                row[k] = float(row[k])

        return jsonify({"success": True, "data": summary, "month_year": month_year}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
