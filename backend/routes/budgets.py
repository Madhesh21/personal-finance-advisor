from flask import Blueprint, request, jsonify
from config import get_db_connection
import mysql.connector
from datetime import datetime
import calendar

budgets_bp = Blueprint('budgets', __name__)


# ── Helper ──────────────────────────────────────────────────────────────────

def _month_label(month_year: str) -> str:
    """Convert 'YYYY-MM' → 'April 2026' for human-readable alert messages."""
    try:
        dt = datetime.strptime(month_year, '%Y-%m')
        return dt.strftime('%B %Y')
    except ValueError:
        return month_year


def _compute_alert(category_name: str, budget_limit: float,
                   actual_spent: float, month_year: str):
    """
    Return a human-readable alert string if the category is over or
    approaching its budget, otherwise return None.

    Thresholds:
      • ≥ 100 % → "exceeded" alert
      •  ≥ 80 % → "close to limit" warning
      •   < 80 % → None
    """
    if budget_limit <= 0:
        return None

    pct = (actual_spent / budget_limit) * 100
    label = _month_label(month_year)

    if pct >= 100:
        return f"⚠️ You have exceeded your {category_name} budget for {label}"
    elif pct >= 80:
        return f"⚠️ You are close to your {category_name} budget limit for {label}"
    return None


# ── GET /api/budgets ─────────────────────────────────────────────────────────

@budgets_bp.route('/api/budgets', methods=['GET'])
def get_budgets():
    """
    GET /api/budgets
    Returns all budget limits for a user.
    Query params:
      - user_id:    int    (default: 1)
      - month_year: YYYY-MM (default: current month)
    """
    user_id    = request.args.get('user_id', 1, type=int)
    month_year = request.args.get('month_year', datetime.now().strftime('%Y-%m'))

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT b.budget_id, b.user_id, b.category_id,
                   c.category_name, c.category_type,
                   b.monthly_limit, b.month_year
            FROM budgets b
            JOIN categories c ON b.category_id = c.category_id
            WHERE b.user_id = %s AND b.month_year = %s
            ORDER BY c.category_name
        """, (user_id, month_year))

        budgets = cursor.fetchall()
        for row in budgets:
            row['monthly_limit'] = float(row['monthly_limit'])

        return jsonify({"success": True, "data": budgets, "month_year": month_year}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ── POST /api/budgets ────────────────────────────────────────────────────────

@budgets_bp.route('/api/budgets', methods=['POST'])
def set_budget():
    """
    POST /api/budgets
    Set or update a monthly budget for a category (upsert).
    Body (JSON): {
        "user_id":       1,
        "category_id":   3,
        "monthly_limit": 500.00,
        "month_year":    "2026-04"   (optional, defaults to current month)
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No JSON body provided"}), 400

    user_id       = data.get('user_id', 1)
    category_id   = data.get('category_id')
    monthly_limit = data.get('monthly_limit')
    month_year    = data.get('month_year', datetime.now().strftime('%Y-%m'))

    if category_id is None:
        return jsonify({"success": False, "error": "category_id is required"}), 400
    if monthly_limit is None or float(monthly_limit) < 0:
        return jsonify({"success": False,
                        "error": "monthly_limit must be a non-negative number"}), 400

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Upsert: update if a row exists, otherwise insert
        cursor.execute(
            "SELECT budget_id FROM budgets "
            "WHERE user_id=%s AND category_id=%s AND month_year=%s",
            (user_id, category_id, month_year)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE budgets SET monthly_limit=%s WHERE budget_id=%s",
                (float(monthly_limit), existing['budget_id'])
            )
            msg       = "Budget updated"
            budget_id = existing['budget_id']
        else:
            cursor.execute(
                "INSERT INTO budgets (user_id, category_id, monthly_limit, month_year) "
                "VALUES (%s, %s, %s, %s)",
                (user_id, category_id, float(monthly_limit), month_year)
            )
            msg       = "Budget created"
            budget_id = cursor.lastrowid

        conn.commit()
        return jsonify({
            "success": True,
            "message": msg,
            "data": {
                "budget_id":     budget_id,
                "user_id":       user_id,
                "category_id":   category_id,
                "monthly_limit": float(monthly_limit),
                "month_year":    month_year
            }
        }), 200 if existing else 201

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ── DELETE /api/budgets/<budget_id> ─────────────────────────────────────────

@budgets_bp.route('/api/budgets/<int:budget_id>', methods=['DELETE'])
def delete_budget(budget_id):
    """
    DELETE /api/budgets/<budget_id>
    Remove a specific budget limit.
    """
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT budget_id FROM budgets WHERE budget_id=%s", (budget_id,))
        if not cursor.fetchone():
            return jsonify({"success": False, "error": "Budget not found"}), 404

        cursor.execute("DELETE FROM budgets WHERE budget_id=%s", (budget_id,))
        conn.commit()

        return jsonify({"success": True, "message": "Budget deleted",
                        "budget_id": budget_id}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ── GET /api/budgets/summary ─────────────────────────────────────────────────

@budgets_bp.route('/api/budgets/summary', methods=['GET'])
def budget_summary():
    """
    GET /api/budgets/summary
    Returns actual vs planned spending per category for a given month.
    Now includes:
      - percent_used  : (actual / limit) * 100
      - alert         : Human-readable alert string or null

    Query params:
      - user_id:    int    (default: 1)
      - month_year: YYYY-MM (default: current month)
    """
    user_id    = request.args.get('user_id', 1, type=int)
    month_year = request.args.get('month_year', datetime.now().strftime('%Y-%m'))
    year, month = month_year.split('-')

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.category_id,
                c.category_name,
                b.budget_id,
                COALESCE(b.monthly_limit, 0)                         AS budget_limit,
                COALESCE(SUM(t.amount), 0)                           AS actual_spent,
                COALESCE(b.monthly_limit, 0) - COALESCE(SUM(t.amount), 0) AS remaining
            FROM categories c
            LEFT JOIN budgets b
                ON b.category_id = c.category_id
               AND b.user_id     = %s
               AND b.month_year  = %s
            LEFT JOIN transactions t
                ON t.category_id       = c.category_id
               AND t.user_id           = %s
               AND t.transaction_type  = 'EXPENSE'
               AND YEAR(t.transaction_date)  = %s
               AND MONTH(t.transaction_date) = %s
            WHERE c.category_type = 'EXPENSE'
            GROUP BY c.category_id, c.category_name, b.budget_id, b.monthly_limit
            ORDER BY actual_spent DESC
        """, (user_id, month_year, user_id, int(year), int(month)))

        rows = cursor.fetchall()

        for row in rows:
            budget_limit = float(row['budget_limit'])
            actual_spent = float(row['actual_spent'])

            row['budget_limit'] = budget_limit
            row['actual_spent'] = actual_spent
            row['remaining']    = float(row['remaining'])

            # Computed fields
            if budget_limit > 0:
                row['percent_used'] = round((actual_spent / budget_limit) * 100, 1)
            else:
                row['percent_used'] = 0.0

            row['alert'] = _compute_alert(
                row['category_name'], budget_limit, actual_spent, month_year
            )

        return jsonify({
            "success":    True,
            "month_year": month_year,
            "data":       rows
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# ── GET /api/budgets/alerts ──────────────────────────────────────────────────

@budgets_bp.route('/api/budgets/alerts', methods=['GET'])
def budget_alerts():
    """
    GET /api/budgets/alerts
    Returns only categories that have an active alert (warning or exceeded).
    Useful for rendering a clean alert/notification panel in the frontend.

    Query params:
      - user_id:    int    (default: 1)
      - month_year: YYYY-MM (default: current month)
    """
    user_id    = request.args.get('user_id', 1, type=int)
    month_year = request.args.get('month_year', datetime.now().strftime('%Y-%m'))
    year, month = month_year.split('-')

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.category_id,
                c.category_name,
                COALESCE(b.monthly_limit, 0)    AS budget_limit,
                COALESCE(SUM(t.amount), 0)      AS actual_spent
            FROM categories c
            JOIN budgets b
                ON b.category_id = c.category_id
               AND b.user_id     = %s
               AND b.month_year  = %s
            LEFT JOIN transactions t
                ON t.category_id       = c.category_id
               AND t.user_id           = %s
               AND t.transaction_type  = 'EXPENSE'
               AND YEAR(t.transaction_date)  = %s
               AND MONTH(t.transaction_date) = %s
            WHERE c.category_type = 'EXPENSE'
            GROUP BY c.category_id, c.category_name, b.monthly_limit
        """, (user_id, month_year, user_id, int(year), int(month)))

        rows = cursor.fetchall()

        alerts = []
        for row in rows:
            budget_limit = float(row['budget_limit'])
            actual_spent = float(row['actual_spent'])

            if budget_limit <= 0:
                continue

            pct   = round((actual_spent / budget_limit) * 100, 1)
            alert = _compute_alert(row['category_name'], budget_limit,
                                   actual_spent, month_year)

            if alert:  # only include if an alert was triggered
                alerts.append({
                    "category_id":   row['category_id'],
                    "category_name": row['category_name'],
                    "budget_limit":  budget_limit,
                    "actual_spent":  actual_spent,
                    "percent_used":  pct,
                    "alert":         alert
                })

        # Sort: exceeded (100%+) first, then by percent_used descending
        alerts.sort(key=lambda x: x['percent_used'], reverse=True)

        return jsonify({
            "success":     True,
            "month_year":  month_year,
            "alert_count": len(alerts),
            "alerts":      alerts
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
