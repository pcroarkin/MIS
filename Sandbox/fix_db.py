import sqlite3
import os
from datetime import datetime

def fix_database():
    """Fix the database by adding missing columns and setting defaults"""
    try:
        # Get the database path from the error message
        db_path = "/Users/pcro/MIS/instance/app.db"
        
        print(f"Attempting to fix database at: {db_path}")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"\nExisting columns: {columns}")
        
        # Add missing columns if they don't exist
        if 'last_login' not in columns:
            print("\nAdding last_login column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN last_login DATETIME
            """)
        
        if 'is_active' not in columns:
            print("\nAdding is_active column...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1
            """)
        
        # Set defaults for existing rows
        print("\nUpdating existing rows...")
        cursor.execute("""
            UPDATE users 
            SET is_active = 1 
            WHERE is_active IS NULL
        """)
        
        # Create indexes
        print("\nCreating indexes...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_users_last_login 
            ON users(last_login)
        """)
        
        # Commit changes
        conn.commit()
        print("\nChanges committed successfully!")
        
        # Verify the changes
        print("\nVerifying table structure:")
        cursor.execute("PRAGMA table_info(users)")
        for col in cursor.fetchall():
            print(f"Column: {col[1]}, Type: {col[2]}, NotNull: {col[3]}, DefaultValue: {col[4]}")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nDatabase connection closed")

if __name__ == '__main__':
    fix_database()
