import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
from app.database.connection import get_db_connection, init_connection_pool

def create_admin(email, password, full_name="System Administrator"):
    init_connection_pool()
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()
        pw_hash = generate_password_hash(password)
        if existing:
            cursor.execute(
                "UPDATE users SET password_hash = %s, role = 'ADMIN', full_name = %s WHERE email = %s",
                (pw_hash, full_name, email)
            )
            print(f"Updated existing user {email} to ADMIN role.")
        else:
            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, 'ADMIN')",
                (full_name, email, pw_hash)
            )
            print(f"Created new ADMIN user: {email}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or promote an admin user in RailSync")
    parser.add_argument("--email", default="admin@railsync.com", help="Admin email")
    parser.add_argument("--password", default="Admin@123", help="Admin password")
    parser.add_argument("--name", default="RailSync Admin", help="Full name")
    args = parser.parse_args()
    create_admin(args.email, args.password, args.name)
