import os
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "personal_finance")

def init_db():
    print(f"Connecting to MySQL server at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    try:
        # First connect without specifying a database to create it if it doesn't exist
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        print(f"Creating database `{DB_NAME}` if it does not exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        
        # Read the schema file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        print(f"Reading schema from {schema_path}...")
        with open(schema_path, 'r') as file:
            full_sql = file.read()
            
        # Execute the schema commands
        # We split by ';' to execute them individually, but skip empty commands
        commands = full_sql.split(';')
        for count, command in enumerate(commands):
            command = command.strip()
            if command:
                cursor.execute(command)
        
        # Insert Default Categories (Using INSERT IGNORE or checking first)
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            print("Inserting default categories...")
            default_categories = [
                ('Salary', 'INCOME'), ('Freelance', 'INCOME'), ('Investments', 'INCOME'),
                ('Food', 'EXPENSE'), ('Rent', 'EXPENSE'), ('Transport', 'EXPENSE'),
                ('Utilities', 'EXPENSE'), ('Entertainment', 'EXPENSE'), ('Shopping', 'EXPENSE'),
                ('Healthcare', 'EXPENSE'), ('Other', 'EXPENSE')
            ]
            cursor.executemany(
                "INSERT INTO categories (category_name, category_type) VALUES (%s, %s)", 
                default_categories
            )
            
        # Insert a Default User
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            print("Inserting default user...")
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s)", 
                ('Default User', 'user@example.com')
            )

        conn.commit()
        print("Database initialization completed effectively!")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Error: Database does not exist")
        else:
            print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    init_db()
