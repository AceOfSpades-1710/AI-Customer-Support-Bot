import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor  # For dict-like results

load_dotenv()

# Neon connection string from .env
DB_URL = os.getenv('NEON_KEY')
if not DB_URL:
    raise ValueError("NEON_KEY not found in .env file")

def get_connection():
    """Get a connection to Neon Postgres."""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Create the sessions table if it doesn't exist."""
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    history TEXT
                )
            ''')
            conn.commit()
        print("Neon database initialized successfully.")
    except psycopg2.Error as e:
        print(f"Init DB error: {e}")
    finally:
        conn.close()

def get_history(session_id):
    """Retrieve conversation history for a session."""
    conn = get_connection()
    if not conn:
        return ""
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT history FROM sessions WHERE session_id = %s', (session_id,))
            result = cursor.fetchone()
            return result[0] if result else ""
    except psycopg2.Error as e:
        print(f"Get history error: {e}")
        return ""
    finally:
        conn.close()

def save_history(session_id, history):
    """Save or update conversation history for a session."""
    conn = get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO sessions (session_id, history) VALUES (%s, %s)
                ON CONFLICT (session_id) DO UPDATE SET history = %s
            ''', (session_id, history, history))
            conn.commit()
    except psycopg2.Error as e:
        print(f"Save history error: {e}")
    finally:
        conn.close()