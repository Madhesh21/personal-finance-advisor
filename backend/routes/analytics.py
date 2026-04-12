from flask import Blueprint, request, jsonify
from config import get_db_connection
import mysql.connector
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/analytics/trends', methods=['GET'])
def get_trends():
    """
    GET /api/analytics/trends
    Query params:
      - user_id: int (default 1)
      - months: int (default 6) - number of past months to include, up to current date
    """
    user_id = request.args.get('user_id', 1, type=int)
    months  = request.args.get('months', 6, type=int)

    if months < 1:
        months = 1

    # Calculate start date
    now = datetime.now()
    y = now.year
    m = now.month
    for _ in range(months - 1):
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    start_date_str = f"{y}-{m:02d}-01"

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT 
                DATE_FORMAT(transaction_date, '%Y-%m') as month_year,
                transaction_type,
                SUM(amount) as total
            FROM transactions
            WHERE user_id = %s AND transaction_date >= %s
            GROUP BY month_year, transaction_type
            ORDER BY month_year ASC
        ''', (user_id, start_date_str))
        
        rows = cursor.fetchall()
        
        trends_map = {}
        for row in rows:
            m_yr = row['month_year']
            t_type = row['transaction_type']
            val = float(row['total'])
            
            if m_yr not in trends_map:
                trends_map[m_yr] = {"month": m_yr, "income": 0.0, "expense": 0.0}
            
            if t_type == 'INCOME':
                trends_map[m_yr]["income"] += val
            elif t_type == 'EXPENSE':
                trends_map[m_yr]["expense"] += val
                
        sorted_trends = sorted(list(trends_map.values()), key=lambda x: x["month"])
        
        return jsonify({
            "success": True,
            "months_requested": months,
            "data": sorted_trends
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


@analytics_bp.route('/api/analytics/distribution', methods=['GET'])
def get_distribution():
    """
    GET /api/analytics/distribution
    Query params:
      - user_id: int (default 1)
      - month_year: YYYY-MM (default: current month)
    """
    user_id = request.args.get('user_id', 1, type=int)
    month_year = request.args.get('month_year', datetime.now().strftime('%Y-%m'))
    
    try:
        year, month = month_year.split('-')
    except ValueError:
        return jsonify({"success": False, "error": "Invalid month_year format. Use YYYY-MM"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT 
                c.category_name,
                SUM(t.amount) as actual_spent
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = %s 
              AND t.transaction_type = 'EXPENSE'
              AND YEAR(t.transaction_date) = %s 
              AND MONTH(t.transaction_date) = %s
            GROUP BY c.category_name
            ORDER BY actual_spent DESC
        ''', (user_id, int(year), int(month)))
        
        rows = cursor.fetchall()
        
        total_expense = sum(float(r['actual_spent']) for r in rows)
        
        distribution = []
        for row in rows:
            spent = float(row['actual_spent'])
            pct = (spent / total_expense * 100) if total_expense > 0 else 0
            distribution.append({
                "category_name": row['category_name'],
                "actual_spent": spent,
                "percentage": round(pct, 1)
            })
            
        return jsonify({
            "success": True,
            "month_year": month_year,
            "total_expense": total_expense,
            "data": distribution
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


@analytics_bp.route('/api/analytics/metrics', methods=['GET'])
def get_metrics():
    """
    GET /api/analytics/metrics
    Query params:
      - user_id: int (default 1)
      - month_year: YYYY-MM (default: current month)
    """
    user_id = request.args.get('user_id', 1, type=int)
    month_year = request.args.get('month_year', datetime.now().strftime('%Y-%m'))
    
    try:
        year, month = month_year.split('-')
    except ValueError:
        return jsonify({"success": False, "error": "Invalid month_year format. Use YYYY-MM"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT transaction_type, SUM(amount) as total
            FROM transactions
            WHERE user_id = %s 
              AND YEAR(transaction_date) = %s 
              AND MONTH(transaction_date) = %s
            GROUP BY transaction_type
        ''', (user_id, int(year), int(month)))
        
        totals = {"INCOME": 0.0, "EXPENSE": 0.0}
        for row in cursor.fetchall():
            totals[row['transaction_type']] = float(row['total'])
            
        income = totals['INCOME']
        expense = totals['EXPENSE']
        net_balance = income - expense
        
        savings_rate_pct = 0.0
        if income > 0:
            savings_rate_pct = round(((income - expense) / income) * 100, 1)
            
        cursor.execute('''
            SELECT c.category_name, SUM(t.amount) as actual_spent
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = %s 
              AND t.transaction_type = 'EXPENSE'
              AND YEAR(t.transaction_date) = %s 
              AND MONTH(t.transaction_date) = %s
            GROUP BY c.category_name
            ORDER BY actual_spent DESC
            LIMIT 3
        ''', (user_id, int(year), int(month)))
        
        top_expenses = []
        for r in cursor.fetchall():
            top_expenses.append({
                "category_name": r['category_name'],
                "actual_spent": float(r['actual_spent'])
            })
            
        return jsonify({
            "success": True,
            "month_year": month_year,
            "data": {
                "total_income": income,
                "total_expense": expense,
                "net_balance": net_balance,
                "savings_rate_pct": savings_rate_pct,
                "top_expenses": top_expenses
            }
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
