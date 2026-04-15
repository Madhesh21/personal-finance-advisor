"""
reset_data.py  ─  Wipes all transactions and budgets, keeps categories and users intact.
Run from the project root:
    python database/reset_data.py
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "personal_finance"),
)
cursor = conn.cursor()

cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("TRUNCATE TABLE user_corrections")
cursor.execute("TRUNCATE TABLE budgets")
cursor.execute("TRUNCATE TABLE transactions")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM transactions")
tx_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM budgets")
b_count = cursor.fetchone()[0]

print("=" * 50)
print("  [OK] Database wiped successfully!")
print(f"  Transactions remaining : {tx_count}")
print(f"  Budgets remaining      : {b_count}")
print("  Categories & Users     : Kept intact")
print("=" * 50)

cursor.close()
conn.close()
