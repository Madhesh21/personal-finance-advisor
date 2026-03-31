import os
import random
from datetime import datetime, timedelta
import mysql.connector
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "personal_finance")

def seed():
    print("Connecting to database for seeding...")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        
        # Get User ID
        cursor.execute("SELECT user_id FROM users LIMIT 1")
        user = cursor.fetchone()
        if not user:
            print("No users found. Run init_mysql.py first!")
            return
        user_id = user['user_id']
        
        # Check if transactions exist
        cursor.execute("SELECT COUNT(*) as count FROM transactions WHERE user_id = %s", (user_id,))
        if cursor.fetchone()['count'] > 0:
            print("Mock data already exists. Skipping seed.")
            return

        # Fetch Categories
        cursor.execute("SELECT category_id, category_name FROM categories")
        categories = cursor.fetchall()
        cat_map = {row['category_name']: row['category_id'] for row in categories}
        
        mock_tx = [
            ("Salary", 5000.0, "INCOME", "Monthly Salary"),
            ("Rent", 1500.0, "EXPENSE", "Apartment Rent"),
            ("Food", 450.0, "EXPENSE", "Groceries at Whole Foods"),
            ("Food", 60.0, "EXPENSE", "Uber Eats Delivery"),
            ("Food", 25.0, "EXPENSE", "Starbucks Coffee"),
            ("Transport", 120.0, "EXPENSE", "Uber rides and subway"),
            ("Utilities", 150.0, "EXPENSE", "Electric and Water bill"),
            ("Entertainment", 200.0, "EXPENSE", "Netflix, Spotify, and Cinema"),
            ("Healthcare", 75.0, "EXPENSE", "Pharmacy"),
            ("Investments", 300.0, "EXPENSE", "Stock deposit"),
            ("Shopping", 140.0, "EXPENSE", "New shoes")
        ]
        
        base_date = datetime.now() - timedelta(days=30)
        insert_data = []
        
        for c_name, amount, t_type, desc in mock_tx:
            cid = cat_map.get(c_name)
            if cid:
                day_offset = random.randint(1, 28)
                tx_date = (base_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
                insert_data.append((user_id, cid, amount, t_type, tx_date, desc))
                
        # Insert using MySQL format (%s instead of ?)
        query = """
            INSERT INTO transactions 
            (user_id, category_id, amount, transaction_type, transaction_date, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(query, insert_data)
        
        conn.commit()
        print(f"Successfully inserted {cursor.rowcount} mock transactions!")

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    seed()
