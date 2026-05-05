import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv(r'c:\Users\rasta\Desktop\financial-advisor\database\.env')

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST', '127.0.0.1'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'personal_finance'),
)
cursor = conn.cursor()

# Check if password_hash column already exists
cursor.execute("""
    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'users' AND COLUMN_NAME = 'password_hash'
""", (os.getenv('DB_NAME', 'personal_finance'),))

count = cursor.fetchone()[0]

if count == 0:
    cursor.execute("""
        ALTER TABLE users
        ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '' AFTER email
    """)
    conn.commit()
    print("Migration complete: password_hash column added to users table.")
else:
    print("Column password_hash already exists — no changes needed.")

cursor.close()
conn.close()
