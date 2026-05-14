import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST", "localhost")
    )

def cleanup_expired_reservations():
    """Releases seats that were booked more than 5 minutes ago."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        expiry_limit = datetime.now() - timedelta(minutes=5)
        cur.execute(
            "UPDATE seats SET is_booked = FALSE, booked_at = NULL, username = NULL "
            "WHERE is_booked = TRUE AND booked_at < %s;",
            (expiry_limit,)
        )
        count = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        if count > 0:
            print(f"⏰ Timer: Released {count} expired seat(s).")
    except Exception as e:
        print(f"Error in cleanup: {e}")
