import sqlite3
import os
from datetime import datetime

def update_database():
    """Update the database schema by adding new columns to users table"""
    try:
        # Get the database file path
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, 'app.db')
        
        print(f"Using database at: {db_path}")
        
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Check if users table exists, if not create it
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(64) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128),
                first_name VARCHAR(64),
                last_name VARCHAR(64),
                is_admin BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        print("Ensured users table exists")
        
        # Read and execute the SQL script
        with open('update_users.sql', 'r') as sql_file:
            sql_script = sql_file.read()
            
        # Split the script into individual statements
        statements = sql_script.split(';')
        
        # Execute each statement
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                    print(f"Executed successfully: {statement.strip()}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"Column already exists: {e}")
                    else:
                        raise
        
        # Commit the changes
        conn.commit()
        print("Database update completed successfully")
        
    except sqlite3.Error as e:
        print(f"SQLite error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    update_database()
