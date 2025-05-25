from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Customer, Order, Job, Product, Material, Invoice

# Create the Flask application context
app = create_app()

# Create the migration object
migrate = Migrate(app, db)

def init_migrations():
    """Initialize migrations directory"""
    with app.app_context():
        migrate.init_app(app, db)
        migrate.init()

def create_migration():
    """Create a new migration"""
    with app.app_context():
        migrate.init_app(app, db)
        migrate.migrate()

def upgrade_db():
    """Apply all pending migrations"""
    with app.app_context():
        migrate.init_app(app, db)
        migrate.upgrade()

if __name__ == '__main__':
    # Initialize migrations
    init_migrations()
    
    # Create and apply migration
    create_migration()
    upgrade_db()
    
    print("Migration complete!")
