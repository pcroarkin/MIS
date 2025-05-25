from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade, init, migrate
import os

def init_and_upgrade_db():
    """Initialize and upgrade the database using Flask-Migrate"""
    try:
        # Import the app and db from your application
        from app import create_app, db
        from app.models import User  # Import models to ensure they're registered
        
        print("Creating application instance...")
        app = create_app()
        
        # Ensure the instance folder exists
        os.makedirs('instance', exist_ok=True)
        
        with app.app_context():
            print("\nInitializing Flask-Migrate...")
            migrate = Migrate(app, db)
            
            print("\nChecking if migrations directory exists...")
            migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
            if not os.path.exists(migrations_dir):
                print("Initializing migrations directory...")
                init()
            
            print("\nCreating migration for current models...")
            migrate()
            
            print("\nApplying migrations...")
            upgrade()
            
            print("\nVerifying database tables...")
            tables = db.engine.table_names()
            print(f"Available tables: {', '.join(tables)}")
            
            # Verify User table columns
            if 'users' in tables:
                with db.engine.connect() as conn:
                    result = conn.execute("""
                        SELECT name, type FROM pragma_table_info('users')
                    """)
                    columns = result.fetchall()
                    print("\nUser table columns:")
                    for col in columns:
                        print(f"- {col[0]}: {col[1]}")
            
            print("\nDatabase upgrade completed successfully!")
            
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("\nTraceback:")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    init_and_upgrade_db()
