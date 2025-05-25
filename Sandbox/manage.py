#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Customer, Order, Job, Product, Material, Invoice
from app.products import add_default_products
from app.materials import add_default_materials
from flask_migrate import upgrade

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Provides important objects to the shell context."""
    return {
        'db': db, 
        'User': User, 
        'Customer': Customer, 
        'Order': Order, 
        'Job': Job,
        'Product': Product,
        'Material': Material,
        'Invoice': Invoice
    }

@app.cli.command("init_db")
def init_db():
    """Initialize the database with required tables and initial data."""
    print("Creating database tables...")
    db.create_all()
    
    # Check if admin user exists
    if not User.query.filter_by(username='admin').first():
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@printmis.com',
            is_admin=True
        )
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    
    # Add default products
    if add_default_products():
        print("Default products added!")
    
    # Add default materials
    if add_default_materials():
        print("Default materials added!")
    
    print("Database initialization complete!")

@app.cli.command("demo_data")
def create_demo_data():
    """Create demo data for testing."""
    from datetime import datetime, timedelta
    
    # Create a demo customer
    if not Customer.query.filter_by(name='ABC Printing Co.').first():
        customer = Customer(
            name='ABC Printing Co.',
            contact_person='John Smith',
            email='john@abcprinting.com',
            phone='555-123-4567',
            address='123 Main St',
            city='Anytown',
            state='CA',
            postal_code='12345',
            country='USA'
        )
        db.session.add(customer)
        db.session.commit()
        print("Demo customer created!")
        
        # Create a demo order
        order = Order(
            order_number='ORD-20230101-001',
            customer_id=customer.id,
            status='APPROVED',
            created_at=datetime.utcnow() - timedelta(days=7),
            due_date=datetime.utcnow() + timedelta(days=7),
            total_amount=500.00
        )
        db.session.add(order)
        db.session.commit()
        print("Demo order created!")
        
        # Add jobs to the order
        product = Product.query.first()
        if product:
            job = Job(
                job_number='JOB-20230101-001',
                order_id=order.id,
                product_id=product.id,
                quantity=1000,
                status='PREPRESS',
                width=88.9,  # 3.5 inches in mm
                height=50.8,  # 2 inches in mm
                pages=2,
                colors='4/4',
                paper_type='100# Gloss Cover'
            )
            db.session.add(job)
            db.session.commit()
            print("Demo job created!")
            
        # Create a demo invoice
        invoice = Invoice(
            invoice_number='INV-20230101-001',
            order_id=order.id,
            created_at=datetime.utcnow() - timedelta(days=5),
            due_date=datetime.utcnow() + timedelta(days=25),
            amount=450.00,
            tax_amount=50.00,
            total_amount=500.00,
            status='SENT'
        )
        db.session.add(invoice)
        db.session.commit()
        print("Demo invoice created!")
    else:
        print("Demo data already exists!")

if __name__ == '__main__':
    app.run(debug=True)
