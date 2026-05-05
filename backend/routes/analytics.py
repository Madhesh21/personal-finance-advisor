from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import get_db_connection
import mysql.connector
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/api/analytics/trends', methods=['GET'])
@jwt_required()
def get_trends():
    user_id      = get_jwt_identity()
    months_param = request.args.get('months', '6')
    month_year   = request.args.get('month_year')

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if month_year:
            try:
                year, month = map(int, month_year.split('-'))
            except ValueError:
                return jsonify({"success": False, "error": "Invalid month_year format. Use YYYY-MM"}), 400

            cursor.execute('''
                SELECT DAY(transaction_date) as day, transaction_type, SUM(amount) as total
                FROM transactions
                WHERE user_id = %s AND YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s
                GROUP BY day, transaction_type ORDER BY day ASC
            ''', (user_id, year, month))

            trends_map = {}
            for row in cursor.fetchall():
                d = int(row['day'])
                if d not in trends_map:
                    trends_map[d] = {"label": str(d), "income": 0.0, "expense": 0.0}
                if row['transaction_type'] == 'INCOME':
                    trends_map[d]["income"] += float(row['total'])
                else:
                    trends_map[d]["expense"] += float(row['total'])

            result_data = sorted(trends_map.values(), key=lambda x: int(x["label"]))
            return jsonify({"success": True, "type": "daily", "month_year": month_year, "data": result_data}), 200

        else:
            where_clause = "WHERE user_id = %s"
            params = [user_id]

            if months_param != 'all':
                try:
                    months = max(1, int(months_param))
                except ValueError:
                    months = 6
                now = datetime.now()
                y, m = now.year, now.month
                for _ in range(months - 1):
                    m -= 1
                    if m == 0:
                        m = 12; y -= 1
                where_clause += " AND transaction_date >= %s"
                params.append(f"{y}-{m:02d}-01")

            cursor.execute(f'''
                SELECT YEAR(transaction_date) as yr, MONTH(transaction_date) as mo,
                       transaction_type, SUM(amount) as total
                FROM transactions {where_clause}
                GROUP BY yr, mo, transaction_type ORDER BY yr ASC, mo ASC
            ''', tuple(params))

            months_map = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            trends_map = {}
            for row in cursor.fetchall():
                yr = row['yr']; mo = row['mo']
                m_label  = f"{months_map[mo-1]} {yr}"
                sort_key = f"{yr}{mo:02d}"
                if m_label not in trends_map:
                    trends_map[m_label] = {"label": m_label, "income": 0.0, "expense": 0.0, "sort_key": sort_key}
                if row['transaction_type'] == 'INCOME':
                    trends_map[m_label]["income"] += float(row['total'])
                else:
                    trends_map[m_label]["expense"] += float(row['total'])

            sorted_trends = sorted(trends_map.values(), key=lambda x: x["sort_key"])
            for item in sorted_trends:
                del item["sort_key"]

            return jsonify({"success": True, "type": "monthly",
                            "months_requested": months_param, "data": sorted_trends}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close(); conn.close()


@analytics_bp.route('/api/analytics/distribution', methods=['GET'])
@jwt_required()
def get_distribution():
    user_id    = get_jwt_identity()
    month_year = request.args.get('month_year', datetime.now().strftime('%Y-%m'))

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        where_clause = "WHERE t.user_id = %s AND c.category_type = 'EXPENSE'"
        params = [user_id]

        if month_year != 'all':
            try:
                year, month = map(int, month_year.split('-'))
                where_clause += " AND YEAR(t.transaction_date) = %s AND MONTH(t.transaction_date) = %s"
                params.extend([year, month])
            except ValueError:
                return jsonify({"success": False, "error": "Invalid month_year format"}), 400

        cursor.execute(f'''
            SELECT c.category_name, SUM(t.amount) as actual_spent
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            {where_clause}
            GROUP BY c.category_name ORDER BY actual_spent DESC
        ''', tuple(params))

        rows = cursor.fetchall()
        total_expense = sum(float(r['actual_spent']) for r in rows)
        distribution = [{
            "category_name": r['category_name'],
            "actual_spent":  float(r['actual_spent']),
            "percentage":    round(float(r['actual_spent']) / total_expense * 100, 1) if total_expense > 0 else 0
        } for r in rows]

        return jsonify({"success": True, "month_year": month_year,
                        "total_expense": total_expense, "data": distribution}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close(); conn.close()


@analytics_bp.route('/api/analytics/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    user_id    = get_jwt_identity()
    month_year = request.args.get('month_year', datetime.now().strftime('%Y-%m'))

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        where_totals   = "WHERE user_id = %s"
        where_expenses = "WHERE t.user_id = %s AND c.category_type = 'EXPENSE'"
        params_t = [user_id]
        params_e = [user_id]

        if month_year != 'all':
            try:
                year, month = map(int, month_year.split('-'))
                where_totals   += " AND YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s"
                where_expenses += " AND YEAR(t.transaction_date) = %s AND MONTH(t.transaction_date) = %s"
                params_t.extend([year, month])
                params_e.extend([year, month])
            except ValueError:
                return jsonify({"success": False, "error": "Invalid month_year format"}), 400

        cursor.execute(f'''
            SELECT transaction_type, SUM(amount) as total
            FROM transactions {where_totals} GROUP BY transaction_type
        ''', tuple(params_t))

        totals = {"INCOME": 0.0, "EXPENSE": 0.0}
        for row in cursor.fetchall():
            totals[row['transaction_type']] = float(row['total'])

        income  = totals['INCOME']
        expense = totals['EXPENSE']
        savings_rate = round(((income - expense) / income) * 100, 1) if income > 0 else 0.0

        cursor.execute(f'''
            SELECT c.category_name, SUM(t.amount) as actual_spent
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            {where_expenses}
            GROUP BY c.category_name ORDER BY actual_spent DESC LIMIT 3
        ''', tuple(params_e))

        top_expenses = [{"category_name": r['category_name'],
                         "actual_spent": float(r['actual_spent'])} for r in cursor.fetchall()]

        return jsonify({
            "success": True, "month_year": month_year,
            "data": {
                "total_income":    income,
                "total_expense":   expense,
                "net_balance":     income - expense,
                "savings_rate_pct": savings_rate,
                "top_expenses":    top_expenses,
            }
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close(); conn.close()
