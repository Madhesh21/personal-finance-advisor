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
      - months: int or string 'all' (default 6)
      - month_year: YYYY-MM (if provided, returns daily trend for that month)
    """
    user_id = request.args.get('user_id', 1, type=int)
    months_param = request.args.get('months', '6')
    month_year = request.args.get('month_year')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if month_year:
            # Case 1: Daily Trend for a specific month
            try:
                year, month = map(int, month_year.split('-'))
            except ValueError:
                return jsonify({"success": False, "error": "Invalid month_year format. Use YYYY-MM"}), 400

            cursor.execute('''
                SELECT 
                    DAY(transaction_date) as day,
                    transaction_type,
                    SUM(amount) as total
                FROM transactions
                WHERE user_id = %s 
                  AND YEAR(transaction_date) = %s 
                  AND MONTH(transaction_date) = %s
                GROUP BY day, transaction_type
                ORDER BY day ASC
            ''', (user_id, year, month))
            
            rows = cursor.fetchall()
            trends_map = {}
            for row in rows:
                d = int(row['day'])
                t_type = row['transaction_type']
                val = float(row['total'])
                
                if d not in trends_map:
                    trends_map[d] = {"label": str(d), "income": 0.0, "expense": 0.0}
                
                if t_type == 'INCOME':
                    trends_map[d]["income"] += val
                elif t_type == 'EXPENSE':
                    trends_map[d]["expense"] += val
            
            # Ensure we sorted by day
            result_data = sorted(list(trends_map.values()), key=lambda x: int(x["label"]))
            
            return jsonify({
                "success": True,
                "type": "daily",
                "month_year": month_year,
                "data": result_data
            }), 200

        else:
            # Case 2: Monthly Trend (Recent or All-time)
            where_clause = "WHERE user_id = %s"
            params = [user_id]

            if months_param != 'all':
                try:
                    months = int(months_param)
                    if months < 1: months = 1
                except ValueError:
                    months = 6

                # Calculate start date
                now = datetime.now()
                y, m = now.year, now.month
                for _ in range(months - 1):
                    m -= 1
                    if m == 0:
                        m = 12
                        y -= 1
                start_date_str = f"{y}-{m:02d}-01"
                where_clause += " AND transaction_date >= %s"
                params.append(start_date_str)

            cursor.execute(f'''
                SELECT 
                    YEAR(transaction_date) as yr,
                    MONTH(transaction_date) as mo,
                    transaction_type,
                    SUM(amount) as total
                FROM transactions
                {where_clause}
                GROUP BY yr, mo, transaction_type
                ORDER BY yr ASC, mo ASC
            ''', tuple(params))
            
            rows = cursor.fetchall()
            months_map = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            trends_map = {}
            for row in rows:
                yr = row['yr']
                mo = row['mo']
                m_label = f"{months_map[mo-1]} {yr}"
                t_type = row['transaction_type']
                val = float(row['total'])
                sort_key = f"{yr}{mo:02d}"
                
                if m_label not in trends_map:
                    trends_map[m_label] = {"label": m_label, "income": 0.0, "expense": 0.0, "sort_key": sort_key}
                
                if t_type == 'INCOME':
                    trends_map[m_label]["income"] += val
                elif t_type == 'EXPENSE':
                    trends_map[m_label]["expense"] += val
                    
            sorted_trends = sorted(list(trends_map.values()), key=lambda x: x["sort_key"])
            for item in sorted_trends:
                del item["sort_key"]
            
            return jsonify({
                "success": True,
                "type": "monthly",
                "months_requested": months_param,
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        where_clause = "WHERE t.user_id = %s AND c.category_type = 'EXPENSE'"
        params = [user_id]

        if month_year != 'all':
            try:
                year, month = map(int, month_year.split('-'))
                where_clause += " AND YEAR(t.transaction_date) = %s AND MONTH(t.transaction_date) = %s"
                params.extend([year, month])
            except ValueError:
                return jsonify({"success": False, "error": "Invalid month_year format. Use YYYY-MM or 'all'"}), 400

        cursor.execute(f'''
            SELECT 
                c.category_name,
                SUM(t.amount) as actual_spent
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            {where_clause}
            GROUP BY c.category_name
            ORDER BY actual_spent DESC
        ''', tuple(params))
        
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        where_clause_totals = "WHERE user_id = %s"
        params_totals = [user_id]
        
        where_clause_expenses = "WHERE t.user_id = %s AND c.category_type = 'EXPENSE'"
        params_expenses = [user_id]

        if month_year != 'all':
            try:
                year, month = map(int, month_year.split('-'))
                where_clause_totals += " AND YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s"
                params_totals.extend([year, month])
                
                where_clause_expenses += " AND YEAR(t.transaction_date) = %s AND MONTH(t.transaction_date) = %s"
                params_expenses.extend([year, month])
            except ValueError:
                return jsonify({"success": False, "error": "Invalid month_year format. Use YYYY-MM or 'all'"}), 400

        # Fetch Summary Totals
        cursor.execute(f'''
            SELECT transaction_type, SUM(amount) as total
            FROM transactions
            {where_clause_totals}
            GROUP BY transaction_type
        ''', tuple(params_totals))
        
        totals = {"INCOME": 0.0, "EXPENSE": 0.0}
        for row in cursor.fetchall():
            totals[row['transaction_type']] = float(row['total'])
            
        income = totals['INCOME']
        expense = totals['EXPENSE']
        net_balance = income - expense
        
        savings_rate_pct = 0.0
        if income > 0:
            savings_rate_pct = round(((income - expense) / income) * 100, 1)
            
        # Fetch Top 3 Expenses
        cursor.execute(f'''
            SELECT c.category_name, SUM(t.amount) as actual_spent
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            {where_clause_expenses}
            GROUP BY c.category_name
            ORDER BY actual_spent DESC
            LIMIT 3
        ''', tuple(params_expenses))
        
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
