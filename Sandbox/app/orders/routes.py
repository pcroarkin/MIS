import os
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app import db
from app.orders import bp
from app.orders.forms import CustomerForm, OrderForm, JobForm, QuoteForm, SearchForm
from app.models import Customer, Order, Job, Product, OrderStatus, JobStatus

@bp.route('/')
@login_required
def index():
    """List all orders"""
    page = request.args.get('page', 1, type=int)
    orders = Order.query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    
    return render_template('orders/index.html', 
                          title='Orders', 
                          orders=orders)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_order():
    """Create a new order"""
    form = OrderForm()
    # Populate customer choices
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.order_by(Customer.name).all()]
    
    if form.validate_on_submit():
        # Generate a unique order number: ORD-YYYYMMDD-XXX
        date_str = datetime.utcnow().strftime('%Y%m%d')
        last_order = Order.query.filter(Order.order_number.like(f'ORD-{date_str}-%')).order_by(
            Order.order_number.desc()).first()
        
        if last_order:
            last_num = int(last_order.order_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
            
        order_number = f'ORD-{date_str}-{new_num:03d}'
        
        order = Order(
            order_number=order_number,
            customer_id=form.customer_id.data,
            status=OrderStatus[form.status.data],
            due_date=form.due_date.data,
            notes=form.notes.data
        )
        
        db.session.add(order)
        db.session.commit()
        flash(f'Order {order_number} has been created successfully', 'success')
        return redirect(url_for('orders.view_order', id=order.id))
    
    return render_template('orders/create_order.html', title='Create Order', form=form)

@bp.route('/<int:id>')
@login_required
def view_order(id):
    """View an order and its jobs"""
    order = Order.query.get_or_404(id)
    jobs = order.jobs.all()
    
    return render_template('orders/view_order.html', 
                          title=f'Order {order.order_number}', 
                          order=order,
                          jobs=jobs)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_order(id):
    """Edit an existing order"""
    order = Order.query.get_or_404(id)
    form = OrderForm()
    # Populate customer choices
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.order_by(Customer.name).all()]
    
    if form.validate_on_submit():
        order.customer_id = form.customer_id.data
        order.status = OrderStatus[form.status.data]
        order.due_date = form.due_date.data
        order.notes = form.notes.data
        order.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash(f'Order {order.order_number} has been updated successfully', 'success')
        return redirect(url_for('orders.view_order', id=order.id))
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.customer_id.data = order.customer_id
        form.status.data = order.status.name
        form.due_date.data = order.due_date
        form.notes.data = order.notes
    
    return render_template('orders/edit_order.html', 
                          title=f'Edit Order {order.order_number}', 
                          form=form, 
                          order=order)

@bp.route('/<int:id>/add_job', methods=['GET', 'POST'])
@login_required
def add_job(id):
    """Add a job to an existing order"""
    order = Order.query.get_or_404(id)
    form = JobForm()
    # Populate product choices
    form.product_id.choices = [(p.id, p.name) for p in Product.query.order_by(Product.name).all()]
    
    if form.validate_on_submit():
        # Generate a unique job number: JOB-YYYYMMDD-XXX
        date_str = datetime.utcnow().strftime('%Y%m%d')
        last_job = Job.query.filter(Job.job_number.like(f'JOB-{date_str}-%')).order_by(
            Job.job_number.desc()).first()
        
        if last_job:
            last_num = int(last_job.job_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
            
        job_number = f'JOB-{date_str}-{new_num:03d}'
        
        job = Job(
            job_number=job_number,
            order_id=order.id,
            product_id=form.product_id.data,
            quantity=form.quantity.data,
            status=JobStatus.PENDING,
            width=form.width.data,
            height=form.height.data,
            pages=form.pages.data,
            colors=form.colors.data,
            paper_type=form.paper_type.data,
            finishing=form.finishing.data,
            estimated_hours=form.estimated_hours.data,
            notes=form.notes.data
        )
        
        # Handle file upload if present
        if form.file_upload.data:
            filename = secure_filename(form.file_upload.data.filename)
            # Create directory if it doesn't exist
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(order.id))
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Save the file
            file_path = os.path.join(upload_dir, filename)
            form.file_upload.data.save(file_path)
            
            # Store relative path
            job.file_path = os.path.join('uploads', str(order.id), filename)
        
        db.session.add(job)
        db.session.commit()
        
        flash(f'Job {job_number} has been created successfully', 'success')
        return redirect(url_for('orders.view_order', id=order.id))
    
    return render_template('orders/add_job.html', 
                          title=f'Add Job to Order {order.order_number}', 
                          form=form, 
                          order=order)

@bp.route('/jobs/<int:id>')
@login_required
def view_job(id):
    """View job details"""
    job = Job.query.get_or_404(id)
    
    return render_template('orders/view_job.html', 
                          title=f'Job {job.job_number}', 
                          job=job)

@bp.route('/jobs/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    """Edit an existing job"""
    job = Job.query.get_or_404(id)
    form = JobForm()
    # Populate product choices
    form.product_id.choices = [(p.id, p.name) for p in Product.query.order_by(Product.name).all()]
    
    if form.validate_on_submit():
        job.product_id = form.product_id.data
        job.quantity = form.quantity.data
        job.width = form.width.data
        job.height = form.height.data
        job.pages = form.pages.data
        job.colors = form.colors.data
        job.paper_type = form.paper_type.data
        job.finishing = form.finishing.data
        job.estimated_hours = form.estimated_hours.data
        job.notes = form.notes.data
        job.updated_at = datetime.utcnow()
        
        # Handle file upload if present
        if form.file_upload.data:
            # Remove old file if exists
            if job.file_path and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], job.file_path)):
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], job.file_path))
            
            filename = secure_filename(form.file_upload.data.filename)
            # Create directory if it doesn't exist
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(job.order_id))
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Save the file
            file_path = os.path.join(upload_dir, filename)
            form.file_upload.data.save(file_path)
            
            # Store relative path
            job.file_path = os.path.join('uploads', str(job.order_id), filename)
        
        db.session.commit()
        flash(f'Job {job.job_number} has been updated successfully', 'success')
        return redirect(url_for('orders.view_job', id=job.id))
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.product_id.data = job.product_id
        form.quantity.data = job.quantity
        form.width.data = job.width
        form.height.data = job.height
        form.pages.data = job.pages
        form.colors.data = job.colors
        form.paper_type.data = job.paper_type
        form.finishing.data = job.finishing
        form.estimated_hours.data = job.estimated_hours
        form.notes.data = job.notes
    
    return render_template('orders/edit_job.html', 
                          title=f'Edit Job {job.job_number}', 
                          form=form, 
                          job=job)

@bp.route('/customers')
@login_required
def customers():
    """List all customers"""
    page = request.args.get('page', 1, type=int)
    customers = Customer.query.order_by(Customer.name).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    
    return render_template('orders/customers.html', 
                          title='Customers', 
                          customers=customers)

@bp.route('/customers/create', methods=['GET', 'POST'])
@login_required
def create_customer():
    """Create a new customer"""
    form = CustomerForm()
    
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            contact_person=form.contact_person.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            postal_code=form.postal_code.data,
            country=form.country.data,
            tax_id=form.tax_id.data,
            notes=form.notes.data
        )
        
        db.session.add(customer)
        db.session.commit()
        flash(f'Customer {customer.name} has been created successfully', 'success')
        return redirect(url_for('orders.customers'))
    
    return render_template('orders/create_customer.html', 
                          title='Create Customer', 
                          form=form)

@bp.route('/customers/<int:id>')
@login_required
def view_customer(id):
    """View customer details and orders"""
    customer = Customer.query.get_or_404(id)
    orders = Order.query.filter_by(customer_id=customer.id).order_by(Order.created_at.desc()).all()
    
    return render_template('orders/view_customer.html', 
                          title=f'Customer: {customer.name}', 
                          customer=customer,
                          orders=orders)

@bp.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    """Edit an existing customer"""
    customer = Customer.query.get_or_404(id)
    form = CustomerForm()
    
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.contact_person = form.contact_person.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        customer.city = form.city.data
        customer.state = form.state.data
        customer.postal_code = form.postal_code.data
        customer.country = form.country.data
        customer.tax_id = form.tax_id.data
        customer.notes = form.notes.data
        
        db.session.commit()
        flash(f'Customer {customer.name} has been updated successfully', 'success')
        return redirect(url_for('orders.view_customer', id=customer.id))
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.name.data = customer.name
        form.contact_person.data = customer.contact_person
        form.email.data = customer.email
        form.phone.data = customer.phone
        form.address.data = customer.address
        form.city.data = customer.city
        form.state.data = customer.state
        form.postal_code.data = customer.postal_code
        form.country.data = customer.country
        form.tax_id.data = customer.tax_id
        form.notes.data = customer.notes
    
    return render_template('orders/edit_customer.html', 
                          title=f'Edit Customer: {customer.name}', 
                          form=form, 
                          customer=customer)

@bp.route('/quotes/create', methods=['GET', 'POST'])
@login_required
def create_quote():
    """Create a new quote"""
    form = QuoteForm()
    # Populate customer choices
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.order_by(Customer.name).all()]
    
    if form.validate_on_submit():
        # Generate a unique order number: QUO-YYYYMMDD-XXX
        date_str = datetime.utcnow().strftime('%Y%m%d')
        last_order = Order.query.filter(Order.order_number.like(f'QUO-{date_str}-%')).order_by(
            Order.order_number.desc()).first()
        
        if last_order:
            last_num = int(last_order.order_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
            
        order_number = f'QUO-{date_str}-{new_num:03d}'
        
        order = Order(
            order_number=order_number,
            customer_id=form.customer_id.data,
            status=OrderStatus.QUOTE,
            due_date=form.due_date.data,
            notes=form.notes.data
        )
        
        db.session.add(order)
        db.session.commit()
        flash(f'Quote {order_number} has been created successfully', 'success')
        return redirect(url_for('orders.view_order', id=order.id))
    
    return render_template('orders/create_quote.html', title='Create Quote', form=form)

@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Search for customers, orders, or jobs"""
    form = SearchForm()
    results = None
    
    if form.validate_on_submit() or request.args.get('query'):
        query = form.query.data or request.args.get('query')
        search_type = form.search_type.data or request.args.get('search_type', 'order')
        
        if search_type == 'customer':
            results = Customer.query.filter(
                (Customer.name.ilike(f'%{query}%')) |
                (Customer.contact_person.ilike(f'%{query}%')) |
                (Customer.email.ilike(f'%{query}%'))
            ).all()
        elif search_type == 'order':
            results = Order.query.filter(
                (Order.order_number.ilike(f'%{query}%')) |
                (Order.notes.ilike(f'%{query}%'))
            ).all()
        elif search_type == 'job':
            results = Job.query.filter(
                (Job.job_number.ilike(f'%{query}%')) |
                (Job.notes.ilike(f'%{query}%'))
            ).all()
        
        form.query.data = query
        form.search_type.data = search_type
    
    return render_template('orders/search.html', 
                          title='Search', 
                          form=form,
                          results=results,
                          search_type=form.search_type.data or 'order')
