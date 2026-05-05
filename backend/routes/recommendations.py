from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import get_db_connection
import mysql.connector
from datetime import datetime

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/api/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id    = get_jwt_identity()
    month_year = request.args.get('month_year', datetime.now().strftime('%Y-%m'))
    try:
        year, month = month_year.split('-')
    except ValueError:
        return jsonify({"success": False, "error": "Invalid month_year format. Use YYYY-MM"}), 400

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        recommendations = []

        cursor.execute("""
            SELECT transaction_type, SUM(amount) AS total
            FROM transactions
            WHERE user_id = %s AND YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s
            GROUP BY transaction_type
        """, (user_id, int(year), int(month)))

        totals = {"INCOME": 0.0, "EXPENSE": 0.0}
        for row in cursor.fetchall():
            totals[row['transaction_type']] = float(row['total'])

        income  = totals['INCOME']
        expense = totals['EXPENSE']
        net_balance = income - expense

        if income > 0:
            savings_rate = net_balance / income
            if savings_rate < 0.20:
                recommendations.append({
                    "type": "SAVINGS", "title": "Increase your savings",
                    "message": f"Your current savings rate is {round(savings_rate*100,1)}%. Try to save at least 20% of your income."
                })

        if net_balance > 0:
            recommendations.append({
                "type": "EMERGENCY_FUND", "title": "Build an Emergency Fund",
                "message": f"You have a positive net balance of ${net_balance:,.2f}. Consider moving some to an emergency fund."
            })

        cursor.execute("""
            SELECT c.category_name,
                   COALESCE(b.monthly_limit, 0) AS budget_limit,
                   COALESCE(SUM(t.amount), 0)   AS actual_spent
            FROM categories c
            LEFT JOIN budgets b ON b.category_id = c.category_id
                AND b.user_id = %s AND b.month_year = %s
            LEFT JOIN transactions t ON t.category_id = c.category_id
                AND t.user_id = %s AND t.transaction_type = 'EXPENSE'
                AND YEAR(t.transaction_date) = %s AND MONTH(t.transaction_date) = %s
            WHERE c.category_type = 'EXPENSE'
            GROUP BY c.category_name, b.monthly_limit
        """, (user_id, month_year, user_id, int(year), int(month)))

        category_spending = cursor.fetchall()
        highest_expense_cat, highest_expense_amt = None, 0.0

        for row in category_spending:
            cat_name     = row['category_name']
            budget_limit = float(row['budget_limit'])
            actual_spent = float(row['actual_spent'])

            if cat_name.lower() not in ('rent', 'mortgage', 'utilities', 'insurance'):
                if actual_spent > highest_expense_amt:
                    highest_expense_amt = actual_spent
                    highest_expense_cat = cat_name

            if budget_limit > 0 and actual_spent > budget_limit:
                excess = actual_spent - budget_limit
                recommendations.append({
                    "type": "BUDGET_EXCEEDED",
                    "title": f"Reduce {cat_name} expenses",
                    "message": f"You are over your {cat_name} budget by ${excess:,.2f}. Try to cut back."
                })

        if expense > 0 and highest_expense_cat and highest_expense_amt > 0:
            pct = (highest_expense_amt / expense) * 100
            if pct > 20:
                recommendations.append({
                    "type": "HIGH_SPENDING",
                    "title": f"Review {highest_expense_cat} spending",
                    "message": f"{pct:.1f}% of your spending is on {highest_expense_cat}. Consider reducing by 20%."
                })

        return jsonify({"success": True, "month_year": month_year, "data": recommendations}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close(); conn.close()
