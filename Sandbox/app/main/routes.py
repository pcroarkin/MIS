from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.main import bp
from app.models import Order, Customer, Job, Invoice, OrderStatus, JobStatus, InvoiceStatus

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

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('main/profile.html', title='Profile', user=current_user)
