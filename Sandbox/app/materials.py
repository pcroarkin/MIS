from app import db
from app.models import Material
from flask import flash

def get_materials():
    """Get all materials"""
    return Material.query.order_by(Material.name).all()

def get_material(id):
    """Get a material by ID"""
    return Material.query.get_or_404(id)

def create_material(name, description, unit_price, stock_level, reorder_level, unit):
    """Create a new material"""
    material = Material(
        name=name,
        description=description,
        unit_price=unit_price,
        stock_level=stock_level,
        reorder_level=reorder_level,
        unit=unit
    )
    db.session.add(material)
    db.session.commit()
    flash(f'Material {name} created successfully', 'success')
    return material

def update_material(id, name, description, unit_price, stock_level, reorder_level, unit):
    """Update an existing material"""
    material = get_material(id)
    material.name = name
    material.description = description
    material.unit_price = unit_price
    material.stock_level = stock_level
    material.reorder_level = reorder_level
    material.unit = unit
    db.session.commit()
    flash(f'Material {name} updated successfully', 'success')
    return material

def update_stock(id, quantity, is_addition=True):
    """Update material stock level"""
    material = get_material(id)
    
    if is_addition:
        material.stock_level += quantity
        action = "added to"
    else:
        if material.stock_level < quantity:
            flash(f'Cannot remove {quantity} {material.unit} from {material.name}. Only {material.stock_level} {material.unit} available.', 'danger')
            return False
        material.stock_level -= quantity
        action = "removed from"
    
    db.session.commit()
    flash(f'{quantity} {material.unit} {action} {material.name} stock', 'success')
    
    # Check if stock is below reorder level
    if material.stock_level <= material.reorder_level:
        flash(f'Warning: {material.name} stock is low ({material.stock_level} {material.unit}). Reorder level is {material.reorder_level} {material.unit}.', 'warning')
    
    return True

def delete_material(id):
    """Delete a material"""
    material = get_material(id)
    name = material.name
    db.session.delete(material)
    db.session.commit()
    flash(f'Material {name} deleted successfully', 'success')
    return True

def add_default_materials():
    """Add default materials if none exist"""
    if Material.query.count() == 0:
        materials = [
            {
                'name': '100# Gloss Text',
                'description': '100# (148 gsm) gloss coated text paper',
                'unit_price': 0.15,
                'stock_level': 5000,
                'reorder_level': 1000,
                'unit': 'sheets'
            },
            {
                'name': '80# Uncoated Text',
                'description': '80# (118 gsm) uncoated text paper',
                'unit_price': 0.12,
                'stock_level': 8000,
                'reorder_level': 1500,
                'unit': 'sheets'
            },
            {
                'name': '100# Gloss Cover',
                'description': '100# (270 gsm) gloss coated cover stock',
                'unit_price': 0.25,
                'stock_level': 3000,
                'reorder_level': 800,
                'unit': 'sheets'
            },
            {
                'name': '13oz Scrim Vinyl',
                'description': '13oz scrim banner vinyl',
                'unit_price': 2.50,
                'stock_level': 500,
                'reorder_level': 100,
                'unit': 'sq ft'
            },
            {
                'name': 'Black Toner',
                'description': 'Black toner cartridge for digital press',
                'unit_price': 120.00,
                'stock_level': 5,
                'reorder_level': 2,
                'unit': 'cartridges'
            },
            {
                'name': 'Cyan Toner',
                'description': 'Cyan toner cartridge for digital press',
                'unit_price': 150.00,
                'stock_level': 4,
                'reorder_level': 2,
                'unit': 'cartridges'
            },
            {
                'name': 'Magenta Toner',
                'description': 'Magenta toner cartridge for digital press',
                'unit_price': 150.00,
                'stock_level': 4,
                'reorder_level': 2,
                'unit': 'cartridges'
            },
            {
                'name': 'Yellow Toner',
                'description': 'Yellow toner cartridge for digital press',
                'unit_price': 150.00,
                'stock_level': 4,
                'reorder_level': 2,
                'unit': 'cartridges'
            }
        ]
        
        for material_data in materials:
            material = Material(
                name=material_data['name'],
                description=material_data['description'],
                unit_price=material_data['unit_price'],
                stock_level=material_data['stock_level'],
                reorder_level=material_data['reorder_level'],
                unit=material_data['unit']
            )
            db.session.add(material)
        
        db.session.commit()
        return True
    
    return False
