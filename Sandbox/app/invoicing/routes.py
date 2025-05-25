from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app import db
from app.invoicing import bp
from app.invoicing.forms import InvoiceForm, PaymentForm, InvoiceSearchForm, InvoiceReportForm
from app.models import Invoice, Order, Customer, Payment, InvoiceStatus

@bp.route('/')
@login_required
def index():
    """Invoice dashboard showing recent and outstanding invoices"""
    # Get counts of invoices by status
    draft_count = Invoice.query.filter_by(status=InvoiceStatus.DRAFT).count()
    sent_count = Invoice.query.filter_by(status=InvoiceStatus.SENT).count()
    paid_count = Invoice.query.filter_by(status=InvoiceStatus.PAID).count()
    overdue_count = Invoice.query.filter_by(status=InvoiceStatus.OVERDUE).count()
    
    # Calculate total outstanding amount
    outstanding_invoices = Invoice.query.filter(Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.OVERDUE])).all()
    total_outstanding = sum(invoice.total_amount for invoice in outstanding_invoices)
    
    # Get recent invoices
    recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(10).all()
    
    # Get overdue invoices
    overdue_invoices = Invoice.query.filter_by(status=InvoiceStatus.OVERDUE).order_by(Invoice.due_date).all()
    
    return render_template('invoicing/index.html', 
                          title='Invoicing Dashboard',
                          draft_count=draft_count,
                          sent_count=sent_count,
                          paid_count=paid_count,
                          overdue_count=overdue_count,
                          total_outstanding=total_outstanding,
                          recent_invoices=recent_invoices,
                          overdue_invoices=overdue_invoices)

@bp.route('/list')
@login_required
def list_invoices():
    """List all invoices with filtering options"""
    form = InvoiceSearchForm()
    
    # Populate customer choices
    form.customer_id.choices = [(0, 'All Customers')] + [
        (c.id, c.name) for c in Customer.query.order_by(Customer.name).all()
    ]
    
    # Get filter parameters from request
    status = request.args.get('status', 'all')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    customer_id = request.args.get('customer_id', '0', type=int)
    
    # Set form values from request
    if status != 'all':
        form.status.data = status
    if start_date_str:
        form.start_date.data = datetime.strptime(start_date_str, '%Y-%m-%d')
    if end_date_str:
        form.end_date.data = datetime.strptime(end_date_str, '%Y-%m-%d')
    if customer_id:
        form.customer_id.data = customer_id
    
    # Start with base query
    query = Invoice.query
    
    # Apply filters
    if status != 'all':
        query = query.filter_by(status=InvoiceStatus[status])
    
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        query = query.filter(Invoice.created_at >= start_date)
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        query = query.filter(Invoice.created_at <= end_date)
    
    if customer_id > 0:
        # Join through orders to filter by customer
        query = query.join(Order).filter(Order.customer_id == customer_id)
    
    # Get paginated results
    page = request.args.get('page', 1, type=int)
    invoices = query.order_by(Invoice.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    
    return render_template('invoicing/list.html',
                          title='Invoices',
                          form=form,
                          invoices=invoices)

@bp.route('/create/<int:order_id>', methods=['GET', 'POST'])
@login_required
def create_invoice(order_id):
    """Create a new invoice for an order"""
    order = Order.query.get_or_404(order_id)
    form = InvoiceForm()
    
    if form.validate_on_submit():
        # Generate a unique invoice number: INV-YYYYMMDD-XXX
        date_str = datetime.utcnow().strftime('%Y%m%d')
        last_invoice = Invoice.query.filter(Invoice.invoice_number.like(f'INV-{date_str}-%')).order_by(
            Invoice.invoice_number.desc()).first()
        
        if last_invoice:
            last_num = int(last_invoice.invoice_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
            
        invoice_number = f'INV-{date_str}-{new_num:03d}'
        
        # Calculate total amount
        amount = form.amount.data
        tax_amount = form.tax_amount.data or 0
        total_amount = amount + tax_amount
        
        invoice = Invoice(
            invoice_number=invoice_number,
            order_id=order.id,
            due_date=form.due_date.data,
            amount=amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status=InvoiceStatus[form.status.data],
            notes=form.notes.data
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        flash(f'Invoice {invoice_number} has been created successfully', 'success')
        return redirect(url_for('invoicing.view_invoice', id=invoice.id))
    
    # Pre-populate form with default values
    if request.method == 'GET':
        form.due_date.data = datetime.utcnow() + timedelta(days=30)  # Default to 30 days from now
        form.amount.data = order.total_amount or 0
        form.tax_amount.data = 0
        form.status.data = InvoiceStatus.DRAFT.name
    
    return render_template('invoicing/create_invoice.html',
                          title=f'Create Invoice for Order {order.order_number}',
                          form=form,
                          order=order)

@bp.route('/<int:id>')
@login_required
def view_invoice(id):
    """View invoice details"""
    invoice = Invoice.query.get_or_404(id)
    payments = Payment.query.filter_by(invoice_id=invoice.id).order_by(Payment.payment_date).all()
    
    # Calculate total paid amount
    total_paid = sum(payment.amount for payment in payments)
    balance_due = invoice.total_amount - total_paid
    
    return render_template('invoicing/view_invoice.html',
                          title=f'Invoice {invoice.invoice_number}',
                          invoice=invoice,
                          payments=payments,
                          total_paid=total_paid,
                          balance_due=balance_due)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_invoice(id):
    """Edit an existing invoice"""
    invoice = Invoice.query.get_or_404(id)
    
    # Don't allow editing of paid invoices
    if invoice.status == InvoiceStatus.PAID:
        flash('Paid invoices cannot be edited', 'warning')
        return redirect(url_for('invoicing.view_invoice', id=invoice.id))
    
    form = InvoiceForm()
    
    if form.validate_on_submit():
        # Calculate total amount
        amount = form.amount.data
        tax_amount = form.tax_amount.data or 0
        total_amount = amount + tax_amount
        
        invoice.due_date = form.due_date.data
        invoice.amount = amount
        invoice.tax_amount = tax_amount
        invoice.total_amount = total_amount
        invoice.status = InvoiceStatus[form.status.data]
        invoice.notes = form.notes.data
        
        db.session.commit()
        
        flash(f'Invoice {invoice.invoice_number} has been updated successfully', 'success')
        return redirect(url_for('invoicing.view_invoice', id=invoice.id))
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.due_date.data = invoice.due_date
        form.amount.data = invoice.amount
        form.tax_amount.data = invoice.tax_amount
        form.notes.data = invoice.notes
        form.status.data = invoice.status.name
    
    return render_template('invoicing/edit_invoice.html',
                          title=f'Edit Invoice {invoice.invoice_number}',
                          form=form,
                          invoice=invoice)

@bp.route('/<int:id>/payment', methods=['GET', 'POST'])
@login_required
def record_payment(id):
    """Record a payment for an invoice"""
    invoice = Invoice.query.get_or_404(id)
    
    # Calculate current balance
    payments = Payment.query.filter_by(invoice_id=invoice.id).all()
    total_paid = sum(payment.amount for payment in payments)
    balance_due = invoice.total_amount - total_paid
    
    form = PaymentForm()
    
    if form.validate_on_submit():
        payment_amount = form.amount.data
        
        # Validate payment amount
        if payment_amount > balance_due:
            flash('Payment amount exceeds the remaining balance', 'danger')
        else:
            payment = Payment(
                invoice_id=invoice.id,
                amount=payment_amount,
                payment_date=form.payment_date.data,
                payment_method=form.payment_method.data,
                reference_number=form.reference_number.data,
                notes=form.notes.data
            )
            
            db.session.add(payment)
            
            # Update invoice status if fully paid
            new_total_paid = total_paid + payment_amount
            if new_total_paid >= invoice.total_amount:
                invoice.status = InvoiceStatus.PAID
            else:
                # Ensure it's marked as sent at minimum
                if invoice.status == InvoiceStatus.DRAFT:
                    invoice.status = InvoiceStatus.SENT
            
            db.session.commit()
            
            flash('Payment recorded successfully', 'success')
            return redirect(url_for('invoicing.view_invoice', id=invoice.id))
    
    # Pre-populate form with default values
    if request.method == 'GET':
        form.amount.data = balance_due  # Default to remaining balance
        form.payment_date.data = datetime.utcnow()
    
    return render_template('invoicing/record_payment.html',
                          title=f'Record Payment for Invoice {invoice.invoice_number}',
                          form=form,
                          invoice=invoice,
                          balance_due=balance_due)

@bp.route('/<int:id>/mark_sent')
@login_required
def mark_sent(id):
    """Mark an invoice as sent"""
    invoice = Invoice.query.get_or_404(id)
    
    if invoice.status == InvoiceStatus.DRAFT:
        invoice.status = InvoiceStatus.SENT
        db.session.commit()
        flash('Invoice marked as sent', 'success')
    else:
        flash('Only draft invoices can be marked as sent', 'warning')
    
    return redirect(url_for('invoicing.view_invoice', id=invoice.id))

@bp.route('/<int:id>/mark_overdue')
@login_required
def mark_overdue(id):
    """Mark an invoice as overdue"""
    invoice = Invoice.query.get_or_404(id)
    
    if invoice.status == InvoiceStatus.SENT:
        invoice.status = InvoiceStatus.OVERDUE
        db.session.commit()
        flash('Invoice marked as overdue', 'success')
    else:
        flash('Only sent invoices can be marked as overdue', 'warning')
    
    return redirect(url_for('invoicing.view_invoice', id=invoice.id))

@bp.route('/<int:id>/cancel')
@login_required
def cancel_invoice(id):
    """Cancel an invoice"""
    invoice = Invoice.query.get_or_404(id)
    
    if invoice.status in [InvoiceStatus.DRAFT, InvoiceStatus.SENT, InvoiceStatus.OVERDUE]:
        invoice.status = InvoiceStatus.CANCELLED
        db.session.commit()
        flash('Invoice has been cancelled', 'success')
    else:
        flash('Paid invoices cannot be cancelled', 'warning')
    
    return redirect(url_for('invoicing.view_invoice', id=invoice.id))

@bp.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    """Generate financial reports"""
    form = InvoiceReportForm()
    report_data = None
    
    if form.validate_on_submit():
        # Define date range for report
        start_date = form.start_date.data
        end_date = form.end_date.data
        report_type = form.report_type.data
        
        # Base query - invoices within date range
        query = Invoice.query.filter(
            (Invoice.created_at >= start_date) & 
            (Invoice.created_at <= end_date)
        )
        
        if report_type == 'outstanding':
            # Outstanding invoices (sent or overdue)
            invoices = query.filter(Invoice.status.in_([InvoiceStatus.SENT, InvoiceStatus.OVERDUE])).order_by(Invoice.due_date).all()
            title = "Outstanding Invoices Report"
            
        elif report_type == 'paid':
            # Paid invoices
            invoices = query.filter_by(status=InvoiceStatus.PAID).order_by(Invoice.created_at.desc()).all()
            title = "Paid Invoices Report"
            
        elif report_type == 'overdue':
            # Overdue invoices
            invoices = query.filter_by(status=InvoiceStatus.OVERDUE).order_by(Invoice.due_date).all()
            title = "Overdue Invoices Report"
            
        elif report_type == 'monthly':
            # Monthly summary - group by month
            invoices = query.order_by(Invoice.created_at).all()
            
            # Group by month
            monthly_data = {}
            for invoice in invoices:
                month_key = invoice.created_at.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'month': invoice.created_at.strftime('%B %Y'),
                        'count': 0,
                        'total': 0,
                        'paid': 0,
                        'outstanding': 0
                    }
                
                monthly_data[month_key]['count'] += 1
                monthly_data[month_key]['total'] += invoice.total_amount
                
                if invoice.status == InvoiceStatus.PAID:
                    monthly_data[month_key]['paid'] += invoice.total_amount
                elif invoice.status in [InvoiceStatus.SENT, InvoiceStatus.OVERDUE]:
                    monthly_data[month_key]['outstanding'] += invoice.total_amount
            
            # Sort by month
            months = sorted(monthly_data.keys())
            sorted_monthly_data = [monthly_data[month] for month in months]
            
            # Prepare report data
            report_data = {
                'title': "Monthly Invoicing Summary",
                'start_date': start_date,
                'end_date': end_date,
                'monthly_data': sorted_monthly_data,
                'total_invoiced': sum(invoice.total_amount for invoice in invoices),
                'total_paid': sum(invoice.total_amount for invoice in invoices if invoice.status == InvoiceStatus.PAID),
                'total_outstanding': sum(invoice.total_amount for invoice in invoices if invoice.status in [InvoiceStatus.SENT, InvoiceStatus.OVERDUE])
            }
            
            return render_template('invoicing/monthly_report.html',
                                  title="Monthly Invoicing Summary",
                                  form=form,
                                  report_data=report_data)
        
        # For non-monthly reports, calculate totals
        total_amount = sum(invoice.total_amount for invoice in invoices)
        
        # Prepare report data
        report_data = {
            'title': title,
            'start_date': start_date,
            'end_date': end_date,
            'invoices': invoices,
            'total_amount': total_amount,
            'count': len(invoices)
        }
    
    # Default to current month for initial form display
    if request.method == 'GET':
        today = datetime.utcnow()
        form.start_date.data = datetime(today.year, today.month, 1)  # First day of current month
        form.end_date.data = today
    
    return render_template('invoicing/reports.html',
                          title='Financial Reports',
                          form=form,
                          report_data=report_data)
