from config import get_db_connection
import mysql.connector


def get_category_map() -> dict:
    """
    Returns a dict mapping lowercase category_name -> category_id.
    Example: {'food': 3, 'salary': 1, 'rent': 4, ...}
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT category_id, category_name FROM categories")
        rows = cursor.fetchall()
        return {row['category_name'].lower(): row['category_id'] for row in rows}
    finally:
        cursor.close()
        conn.close()


def bulk_insert_transactions(records: list[dict], user_id: int) -> int:
    """
    Bulk-insert a list of transaction records for a given user.

    Args:
        records : list of dicts with keys:
                    transaction_date, amount, category_id,
                    transaction_type, description
        user_id : int

    Returns:
        Number of rows inserted.
    """
    if not records:
        return 0

    query = """
        INSERT INTO transactions
            (user_id, category_id, amount, transaction_type, transaction_date, description, auto_categorized)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
    """
    data = [
        (
            user_id,
            r['category_id'],
            r['amount'],
            r['transaction_type'],
            r['transaction_date'],
            r['description'],
            r.get('auto_categorized', 0)
        )
        for r in records
    ]

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(query, data)
        conn.commit()
        return cursor.rowcount
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
