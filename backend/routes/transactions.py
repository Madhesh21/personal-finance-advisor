from flask import Blueprint, request, jsonify
from config import get_db_connection
import mysql.connector
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/api/transactions', methods=['GET'])
def get_transactions():
    """
    GET /api/transactions
    Returns transactions for a user with optional filters.
    Query params:
      - user_id     : int     (default: 1)
      - category_id : int     (optional)
      - type        : INCOME | EXPENSE  (optional)
      - start_date  : YYYY-MM-DD        (optional)
      - end_date    : YYYY-MM-DD        (optional)
      - limit       : int     (default: 50)
      - offset      : int     (default: 0)
    """
    user_id     = request.args.get('user_id', 1, type=int)
    category_id = request.args.get('category_id', None, type=int)
    tx_type     = request.args.get('type', None)
    start_date  = request.args.get('start_date', None)
    end_date    = request.args.get('end_date', None)
    limit       = request.args.get('limit', 50, type=int)
    offset      = request.args.get('offset', 0, type=int)

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query  = """
            SELECT
                t.transaction_id,
                t.user_id,
                t.amount,
                t.transaction_type,
                t.transaction_date,
                t.description,
                t.created_at,
                c.category_id,
                c.category_name
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.user_id = %s
        """
        params = [user_id]

        if category_id:
            query  += " AND t.category_id = %s"
            params.append(category_id)

        if tx_type and tx_type.upper() in ('INCOME', 'EXPENSE'):
            query  += " AND t.transaction_type = %s"
            params.append(tx_type.upper())

        if start_date:
            query  += " AND t.transaction_date >= %s"
            params.append(start_date)

        if end_date:
            query  += " AND t.transaction_date <= %s"
            params.append(end_date)

        query += " ORDER BY t.transaction_date DESC, t.transaction_id DESC"
        query += " LIMIT %s OFFSET %s"
        params += [limit, offset]

        cursor.execute(query, params)
        transactions = cursor.fetchall()

        # Convert non-JSON-serialisable types
        for row in transactions:
            row['amount']           = float(row['amount'])
            row['transaction_date'] = str(row['transaction_date'])
            row['created_at']       = str(row['created_at'])

        # Total count (for pagination)
        count_query  = "SELECT COUNT(*) AS total FROM transactions WHERE user_id = %s"
        count_params = [user_id]
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']

        return jsonify({
            "success": True,
            "data":    transactions,
            "total":   total,
            "limit":   limit,
            "offset":  offset
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


@transactions_bp.route('/api/transactions', methods=['POST'])
def add_transaction():
    """
    POST /api/transactions
    Manually add a single transaction.
    Body (JSON): {
        "user_id":          1,
        "category_id":      3,
        "amount":           150.00,
        "transaction_type": "EXPENSE",
        "transaction_date": "2026-03-28",
        "description":      "Grocery shopping"
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No JSON body provided"}), 400

    # Extract fields
    user_id         = data.get('user_id', 1)
    category_id     = data.get('category_id')
    amount          = data.get('amount')
    transaction_type = data.get('transaction_type')
    if transaction_type:
        transaction_type = transaction_type.upper()
    transaction_date = data.get('transaction_date', datetime.now().strftime('%Y-%m-%d'))
    description     = data.get('description', '').strip()[:255]

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ── Auto-detect/Enforce type if category is known ─────────────────────
        cursor.execute("SELECT category_type FROM categories WHERE category_id = %s", (category_id,))
        cat_row = cursor.fetchone()
        
        if cat_row:
            # Overwrite user-provided type if it conflicts with category type
            transaction_type = cat_row['category_type']
        elif not transaction_type:
            # Fallback if category not found (shouldn't happen with valid FK)
            transaction_type = 'EXPENSE'

        # Validate
        errors = []
        if category_id is None:
            errors.append("category_id is required")
        if amount is None:
            errors.append("amount is required")
        elif float(amount) <= 0:
            errors.append("amount must be greater than 0")
        if transaction_type not in ('INCOME', 'EXPENSE'):
            errors.append("transaction_type must be INCOME or EXPENSE")
        try:
            datetime.strptime(str(transaction_date), '%Y-%m-%d')
        except ValueError:
            errors.append("transaction_date must be in YYYY-MM-DD format")

        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        cursor.execute(
            """
            INSERT INTO transactions
                (user_id, category_id, amount, transaction_type, transaction_date, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, category_id, float(amount), transaction_type, transaction_date, description)
        )
        conn.commit()
        new_id = cursor.lastrowid

        # Return the newly created transaction
        cursor.execute(
            """
            SELECT t.*, c.category_name
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.transaction_id = %s
            """,
            (new_id,)
        )
        new_tx = cursor.fetchone()
        new_tx['amount']           = float(new_tx['amount'])
        new_tx['transaction_date'] = str(new_tx['transaction_date'])
        new_tx['created_at']       = str(new_tx['created_at'])

        return jsonify({
            "success": True,
            "message": "Transaction added",
            "data":    new_tx
        }), 201

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


@transactions_bp.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """
    DELETE /api/transactions/<id>
    Delete a specific transaction by ID.
    """
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT transaction_id FROM transactions WHERE transaction_id = %s",
            (transaction_id,)
        )
        if not cursor.fetchone():
            return jsonify({"success": False, "error": "Transaction not found"}), 404

        cursor.execute(
            "DELETE FROM transactions WHERE transaction_id = %s",
            (transaction_id,)
        )
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Transaction {transaction_id} deleted"
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


@transactions_bp.route('/api/transactions/summary', methods=['GET'])
def transaction_summary():
    """
    GET /api/transactions/summary
    Returns total income, total expense, and net balance for a user.
    Query params:
      - user_id    : int      (default: 1)
      - month_year : YYYY-MM  (optional, filters to that month)
    """
    user_id    = request.args.get('user_id', 1, type=int)
    month_year = request.args.get('month_year', None)

    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        base_query = """
            SELECT
                transaction_type,
                SUM(amount) AS total
            FROM transactions
            WHERE user_id = %s
        """
        params = [user_id]

        if month_year:
            year, month = month_year.split('-')
            base_query += " AND YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s"
            params += [int(year), int(month)]

        base_query += " GROUP BY transaction_type"
        cursor.execute(base_query, params)
        rows = cursor.fetchall()

        totals = {"INCOME": 0.0, "EXPENSE": 0.0}
        for row in rows:
            totals[row['transaction_type']] = float(row['total'])

        net_balance = totals['INCOME'] - totals['EXPENSE']

        return jsonify({
            "success":     True,
            "total_income":  totals['INCOME'],
            "total_expense": totals['EXPENSE'],
            "net_balance":   net_balance,
            "month_year":    month_year or "all-time"
        }), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
