from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.main import bp
from app.main.forms import ProfileUpdateForm, PasswordChangeForm
from app.models import Order, Customer, Job, Invoice, OrderStatus, JobStatus, InvoiceStatus, db
from datetime import datetime

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """Dashboard view showing key metrics and recent activity"""
    # Get count of orders by status
    order_counts = {
        'pending': Order.query.filter_by(status=OrderStatus.PENDING).count(),
        'in_production': Order.query.filter_by(status=OrderStatus.IN_PRODUCTION).count(),
        'completed': Order.query.filter_by(status=OrderStatus.COMPLETED).count(),
    }
    
    # Get count of jobs by status
    job_counts = {
        'pending': Job.query.filter_by(status=JobStatus.PENDING).count(),
        'prepress': Job.query.filter_by(status=JobStatus.PREPRESS).count(),
        'press': Job.query.filter_by(status=JobStatus.PRESS).count(),
        'postpress': Job.query.filter_by(status=JobStatus.POSTPRESS).count(),
        'quality_check': Job.query.filter_by(status=JobStatus.QUALITY_CHECK).count(),
    }
    
    # Get recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Get overdue invoices
    overdue_invoices = Invoice.query.filter_by(status=InvoiceStatus.OVERDUE).count()
    
    # Get total customers
    total_customers = Customer.query.count()
    
    return render_template('main/index.html', 
                          title='Dashboard',
                          order_counts=order_counts,
                          job_counts=job_counts,
                          recent_orders=recent_orders,
                          overdue_invoices=overdue_invoices,
                          total_customers=total_customers)

@bp.route('/about')
def about():
    """About page with system information"""
    return render_template('main/about.html', title='About')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    return render_template('main/profile.html', title='Profile')

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Handle profile information updates"""
    form = ProfileUpdateForm(current_user.email)
    
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('Your profile has been updated.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('main.profile'))

@bp.route('/profile/password', methods=['POST'])
@login_required
def change_password():
    """Handle password changes"""
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            current_user.last_login = datetime.utcnow()  # Update last login time
            db.session.commit()
            flash('Your password has been updated.', 'success')
        else:
            flash('Invalid current password.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('main.profile'))
