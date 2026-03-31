import os
import mysql.connector
from dotenv import load_dotenv

# Load credentials from the shared database/.env file
_env_path = os.path.join(os.path.dirname(__file__), '..', 'database', '.env')
load_dotenv(_env_path)

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "127.0.0.1"),
    "port":     int(os.getenv("DB_PORT", 3306)),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "personal_finance"),
}


def get_db_connection():
    """Return a new MySQL connection using shared config."""
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn
