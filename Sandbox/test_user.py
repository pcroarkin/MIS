import sqlite3
from datetime import datetime

def test_database():
    """Test the database structure and user table"""
    try:
        # Connect to the database
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # Create a test user if none exists
        cursor.execute("""
            INSERT INTO users (
                username, email, password_hash, first_name, last_name, 
                is_admin, created_at, last_login, is_active
            ) VALUES (
                'testuser', 'test@example.com', 'dummy_hash', 'Test', 'User',
                0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1
            )
        """)
        conn.commit()
        print("\nTest user created")
        
        # Get table info
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("\nUser table structure:")
        for col in columns:
            print(f"Column: {col[1]}, Type: {col[2]}, Nullable: {col[3]}, Default: {col[4]}")
        
        # Get user count
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"\nTotal users in database: {count}")
        
        # Get all users
        cursor.execute("""
            SELECT username, email, first_name, last_name, is_admin, is_active, created_at, last_login 
            FROM users
        """)
        users = cursor.fetchall()
        
        print("\nUser details:")
        for user in users:
            print("\nUser:")
            print(f"Username: {user[0]}")
            print(f"Email: {user[1]}")
            print(f"First Name: {user[2]}")
            print(f"Last Name: {user[3]}")
            print(f"Is Admin: {user[4]}")
            print(f"Is Active: {user[5]}")
            print(f"Created At: {user[6]}")
            print(f"Last Login: {user[7]}")
        
        print("\nTest completed successfully!")
        
    except sqlite3.Error as e:
        print(f"\nSQLite error occurred: {str(e)}")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed")

if __name__ == '__main__':
    test_database()
