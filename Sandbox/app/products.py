from app import db
from app.models import Product
from flask import flash

def get_products():
    """Get all products"""
    return Product.query.order_by(Product.name).all()

def get_product(id):
    """Get a product by ID"""
    return Product.query.get_or_404(id)

def create_product(name, description, unit_price):
    """Create a new product"""
    product = Product(
        name=name,
        description=description,
        unit_price=unit_price
    )
    db.session.add(product)
    db.session.commit()
    flash(f'Product {name} created successfully', 'success')
    return product

def update_product(id, name, description, unit_price):
    """Update an existing product"""
    product = get_product(id)
    product.name = name
    product.description = description
    product.unit_price = unit_price
    db.session.commit()
    flash(f'Product {name} updated successfully', 'success')
    return product

def delete_product(id):
    """Delete a product"""
    product = get_product(id)
    
    # Check if product is in use
    if product.jobs.count() > 0:
        flash(f'Cannot delete product {product.name} because it is in use', 'danger')
        return False
    
    name = product.name
    db.session.delete(product)
    db.session.commit()
    flash(f'Product {name} deleted successfully', 'success')
    return True

def add_default_products():
    """Add default products if none exist"""
    if Product.query.count() == 0:
        products = [
            {
                'name': 'Business Cards',
                'description': 'Standard business cards, 3.5" x 2", full color both sides',
                'unit_price': 45.00
            },
            {
                'name': 'Flyers - Letter Size',
                'description': '8.5" x 11" flyers, full color one side',
                'unit_price': 0.25
            },
            {
                'name': 'Brochures - Trifold',
                'description': '8.5" x 11" trifold brochures, full color both sides',
                'unit_price': 0.65
            },
            {
                'name': 'Posters - 18" x 24"',
                'description': '18" x 24" posters, full color one side',
                'unit_price': 15.00
            },
            {
                'name': 'Postcards - 4" x 6"',
                'description': '4" x 6" postcards, full color both sides',
                'unit_price': 0.20
            },
            {
                'name': 'Banners - 3\' x 6\'',
                'description': '3\' x 6\' vinyl banner, full color one side',
                'unit_price': 75.00
            }
        ]
        
        for product_data in products:
            product = Product(
                name=product_data['name'],
                description=product_data['description'],
                unit_price=product_data['unit_price']
            )
            db.session.add(product)
        
        db.session.commit()
        return True
    
    return False
