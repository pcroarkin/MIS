import sqlite3
import os
from datetime import datetime

def test_database_fix():
    """Test that the database has been fixed correctly"""
    try:
        # Get the database path from the error message
        db_path = "/Users/pcro/MIS/instance/app.db"
        
        print("Database Fix Verification Test")
        print("=============================")
        print(f"\nTesting database at: {db_path}")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Check table structure
        print("\nTest 1: Checking table structure...")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        required_columns = {
            'id', 'username', 'email', 'password_hash', 
            'first_name', 'last_name', 'is_admin', 
            'created_at', 'last_login', 'is_active'
        }
        existing_columns = {col[1] for col in columns}
        missing_columns = required_columns - existing_columns
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
        else:
            print("✅ All required columns present")
            print("\nColumn details:")
            for col in columns:
                print(f"- {col[1]}: {col[2]}, Nullable: {not col[3]}, Default: {col[4]}")
        
        # Test 2: Check indexes
        print("\nTest 2: Checking indexes...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='users'")
        indexes = cursor.fetchall()
        index_names = {idx[0] for idx in indexes}
        print("Existing indexes:", ', '.join(index_names))
        
        # Test 3: Try sample operations
        print("\nTest 3: Testing data operations...")
        
        # Test 3.1: Insert a test user
        print("\nTesting user insertion...")
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, ('testuser', 'test@example.com', 'hash', 'Test', 'User', 0, datetime.utcnow(), 1))
            print("✅ User insertion successful")
        except Exception as e:
            print(f"❌ User insertion failed: {str(e)}")
        
        # Test 3.2: Update last_login
        print("\nTesting last_login update...")
        try:
            cursor.execute("""
                UPDATE users 
                SET last_login = ? 
                WHERE username = ?
            """, (datetime.utcnow(), 'testuser'))
            print("✅ Last login update successful")
        except Exception as e:
            print(f"❌ Last login update failed: {str(e)}")
        
        # Test 3.3: Verify data
        print("\nVerifying test user data...")
        cursor.execute("SELECT * FROM users WHERE username = 'testuser'")
        test_user = cursor.fetchone()
        if test_user:
            print("✅ Test user verification successful")
        else:
            print("❌ Test user verification failed")
        
        # Cleanup test data
        cursor.execute("DELETE FROM users WHERE username = 'testuser'")
        
        # Commit changes
        conn.commit()
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nDatabase connection closed")

if __name__ == '__main__':
    test_database_fix()
