from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app import db
from app.production import bp
from app.production.forms import (UpdateJobStatusForm, ProductionScheduleForm, 
                                JobCompletionForm, MaterialUsageForm, 
                                QualityCheckForm, ProductionReportForm)
from app.models import Job, Material, Order, JobStatus, OrderStatus

@bp.route('/')
@login_required
def index():
    """Production dashboard showing jobs in progress and pending"""
    # Get jobs by status
    pending_jobs = Job.query.filter_by(status=JobStatus.PENDING).order_by(Job.created_at).all()
    prepress_jobs = Job.query.filter_by(status=JobStatus.PREPRESS).order_by(Job.start_date).all()
    press_jobs = Job.query.filter_by(status=JobStatus.PRESS).order_by(Job.start_date).all()
    postpress_jobs = Job.query.filter_by(status=JobStatus.POSTPRESS).order_by(Job.start_date).all()
    qc_jobs = Job.query.filter_by(status=JobStatus.QUALITY_CHECK).order_by(Job.start_date).all()
    
    return render_template('production/index.html', 
                          title='Production Dashboard',
                          pending_jobs=pending_jobs,
                          prepress_jobs=prepress_jobs,
                          press_jobs=press_jobs,
                          postpress_jobs=postpress_jobs,
                          qc_jobs=qc_jobs)

@bp.route('/schedule')
@login_required
def schedule():
    """Production schedule view"""
    jobs = Job.query.filter(
        Job.status.in_([JobStatus.PENDING, JobStatus.PREPRESS, JobStatus.PRESS, JobStatus.POSTPRESS, JobStatus.QUALITY_CHECK])
    ).order_by(Job.start_date, Job.created_at).all()
    
    # Group jobs by status for scheduling display
    job_schedule = {
        'pending': [j for j in jobs if j.status == JobStatus.PENDING],
        'prepress': [j for j in jobs if j.status == JobStatus.PREPRESS],
        'press': [j for j in jobs if j.status == JobStatus.PRESS],
        'postpress': [j for j in jobs if j.status == JobStatus.POSTPRESS],
        'quality_check': [j for j in jobs if j.status == JobStatus.QUALITY_CHECK]
    }
    
    return render_template('production/schedule.html', 
                          title='Production Schedule',
                          job_schedule=job_schedule)

@bp.route('/jobs/<int:id>')
@login_required
def view_job(id):
    """View production details for a job"""
    job = Job.query.get_or_404(id)
    
    return render_template('production/view_job.html', 
                          title=f'Production: {job.job_number}',
                          job=job)

@bp.route('/jobs/<int:id>/update_status', methods=['GET', 'POST'])
@login_required
def update_job_status(id):
    """Update the status of a job"""
    job = Job.query.get_or_404(id)
    form = UpdateJobStatusForm()
    
    if form.validate_on_submit():
        old_status = job.status
        job.status = JobStatus[form.status.data]
        
        # If moving to first production phase from pending, set start date
        if old_status == JobStatus.PENDING and job.status != JobStatus.PENDING and not job.start_date:
            job.start_date = datetime.utcnow()
        
        # If moving to completed, ensure the job completion date is set
        if job.status == JobStatus.COMPLETED and not job.completion_date:
            job.completion_date = datetime.utcnow()
        
        # Update order status if needed
        if job.status == JobStatus.PENDING:
            job.order.status = OrderStatus.PENDING
        elif job.status in [JobStatus.PREPRESS, JobStatus.PRESS, JobStatus.POSTPRESS, JobStatus.QUALITY_CHECK]:
            job.order.status = OrderStatus.IN_PRODUCTION
        elif job.status == JobStatus.COMPLETED:
            # Check if all jobs for this order are completed
            all_completed = all(j.status == JobStatus.COMPLETED for j in job.order.jobs)
            if all_completed:
                job.order.status = OrderStatus.COMPLETED
        
        # Add notes if provided
        if form.notes.data:
            if job.notes:
                job.notes += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Status changed to {job.status.value}:\n{form.notes.data}"
            else:
                job.notes = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Status changed to {job.status.value}:\n{form.notes.data}"
        
        db.session.commit()
        flash(f'Job status updated to {job.status.value}', 'success')
        return redirect(url_for('production.view_job', id=job.id))
    
    # Pre-populate form
    if request.method == 'GET':
        form.status.data = job.status.name
    
    return render_template('production/update_status.html',
                          title=f'Update Status: {job.job_number}',
                          form=form,
                          job=job)

@bp.route('/jobs/<int:id>/schedule', methods=['GET', 'POST'])
@login_required
def schedule_job(id):
    """Schedule a job for production"""
    job = Job.query.get_or_404(id)
    form = ProductionScheduleForm()
    
    if form.validate_on_submit():
        job.start_date = form.start_date.data
        job.completion_date = form.completion_date.data
        job.estimated_hours = form.estimated_hours.data
        
        # Add notes if provided
        if form.notes.data:
            if job.notes:
                job.notes += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Production schedule updated:\n{form.notes.data}"
            else:
                job.notes = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Production schedule updated:\n{form.notes.data}"
        
        db.session.commit()
        flash('Job scheduled successfully', 'success')
        return redirect(url_for('production.view_job', id=job.id))
    
    # Pre-populate form
    if request.method == 'GET':
        form.start_date.data = job.start_date
        form.completion_date.data = job.completion_date
        form.estimated_hours.data = job.estimated_hours
    
    return render_template('production/schedule_job.html',
                          title=f'Schedule Job: {job.job_number}',
                          form=form,
                          job=job)

@bp.route('/jobs/<int:id>/complete', methods=['GET', 'POST'])
@login_required
def complete_job(id):
    """Mark a job as completed"""
    job = Job.query.get_or_404(id)
    form = JobCompletionForm()
    
    if form.validate_on_submit():
        job.status = JobStatus.COMPLETED
        job.completion_date = form.completion_date.data
        job.actual_hours = form.actual_hours.data
        
        # Check if all jobs for this order are completed
        all_completed = True
        for other_job in job.order.jobs:
            if other_job.id != job.id and other_job.status != JobStatus.COMPLETED:
                all_completed = False
                break
        
        if all_completed:
            job.order.status = OrderStatus.COMPLETED
        
        # Add notes if provided
        if form.notes.data:
            if job.notes:
                job.notes += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Job completed:\n{form.notes.data}"
            else:
                job.notes = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Job completed:\n{form.notes.data}"
        
        db.session.commit()
        flash('Job marked as completed', 'success')
        return redirect(url_for('production.view_job', id=job.id))
    
    # Pre-populate form with default values
    if request.method == 'GET':
        form.completion_date.data = datetime.utcnow()
        form.actual_hours.data = job.estimated_hours  # Default to estimated hours
    
    return render_template('production/complete_job.html',
                          title=f'Complete Job: {job.job_number}',
                          form=form,
                          job=job)

@bp.route('/jobs/<int:id>/quality_check', methods=['GET', 'POST'])
@login_required
def quality_check(id):
    """Perform a quality check on a job"""
    job = Job.query.get_or_404(id)
    form = QualityCheckForm()
    
    if form.validate_on_submit():
        if form.passed.data == 'pass':
            job.status = JobStatus.COMPLETED
            job.completion_date = datetime.utcnow()
            result_text = "PASSED"
        else:
            job.status = JobStatus.PRESS  # Send back to production
            result_text = "FAILED - Requires rework"
        
        # Add notes about quality check
        if job.notes:
            job.notes += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Quality Check {result_text}:\n{form.notes.data}"
        else:
            job.notes = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Quality Check {result_text}:\n{form.notes.data}"
        
        db.session.commit()
        flash(f'Quality check completed: {result_text}', 'success')
        return redirect(url_for('production.view_job', id=job.id))
    
    return render_template('production/quality_check.html',
                          title=f'Quality Check: {job.job_number}',
                          form=form,
                          job=job)

@bp.route('/materials')
@login_required
def materials():
    """List all materials"""
    page = request.args.get('page', 1, type=int)
    materials = Material.query.order_by(Material.name).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    
    return render_template('production/materials.html',
                          title='Materials Inventory',
                          materials=materials)

@bp.route('/jobs/<int:id>/material_usage', methods=['GET', 'POST'])
@login_required
def record_material_usage(id):
    """Record materials used for a job"""
    job = Job.query.get_or_404(id)
    form = MaterialUsageForm()
    
    # Populate material choices
    form.material_id.choices = [(m.id, f"{m.name} ({m.stock_level} {m.unit} available)") 
                               for m in Material.query.order_by(Material.name).all()]
    
    if form.validate_on_submit():
        material = Material.query.get(form.material_id.data)
        
        # Update stock level
        if material.stock_level >= form.quantity.data:
            material.stock_level -= form.quantity.data
            
            # Add notes about material usage
            usage_note = f"Used {form.quantity.data} {material.unit} of {material.name}"
            if form.notes.data:
                usage_note += f": {form.notes.data}"
                
            if job.notes:
                job.notes += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] {usage_note}"
            else:
                job.notes = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] {usage_note}"
            
            db.session.commit()
            flash(f'Recorded usage of {form.quantity.data} {material.unit} of {material.name}', 'success')
            
            # Check if stock is low
            if material.stock_level <= material.reorder_level:
                flash(f'Warning: {material.name} stock is low ({material.stock_level} {material.unit} remaining)', 'warning')
                
            return redirect(url_for('production.view_job', id=job.id))
        else:
            flash(f'Error: Not enough {material.name} in stock. Available: {material.stock_level} {material.unit}', 'danger')
    
    return render_template('production/material_usage.html',
                          title=f'Record Material Usage: {job.job_number}',
                          form=form,
                          job=job)

@bp.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    """Generate production reports"""
    form = ProductionReportForm()
    report_data = None
    
    if form.validate_on_submit():
        # Define date range for report
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # Base query - jobs within date range
        query = Job.query.filter(
            (Job.created_at >= start_date) & 
            (Job.created_at <= end_date)
        )
        
        # Filter by status if specified
        if form.status.data != 'all':
            if form.status.data == 'pending':
                query = query.filter_by(status=JobStatus.PENDING)
            elif form.status.data == 'in_progress':
                query = query.filter(Job.status.in_([
                    JobStatus.PREPRESS, JobStatus.PRESS, JobStatus.POSTPRESS, JobStatus.QUALITY_CHECK
                ]))
            elif form.status.data == 'completed':
                query = query.filter_by(status=JobStatus.COMPLETED)
        
        # Execute query
        jobs = query.order_by(Job.created_at).all()
        
        # Calculate summary statistics
        total_jobs = len(jobs)
        completed_jobs = sum(1 for j in jobs if j.status == JobStatus.COMPLETED)
        total_hours = sum(j.actual_hours or 0 for j in jobs)
        
        # Group jobs by product type
        product_counts = {}
        for job in jobs:
            product_name = job.product.name if job.product else 'Unknown'
            if product_name in product_counts:
                product_counts[product_name] += 1
            else:
                product_counts[product_name] = 1
        
        # Prepare report data
        report_data = {
            'start_date': start_date,
            'end_date': end_date,
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'completion_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            'total_hours': total_hours,
            'product_breakdown': product_counts,
            'jobs': jobs
        }
    
    # Default to current month for initial form display
    if request.method == 'GET':
        today = datetime.utcnow()
        form.start_date.data = datetime(today.year, today.month, 1)  # First day of current month
        form.end_date.data = today
    
    return render_template('production/reports.html',
                          title='Production Reports',
                          form=form,
                          report_data=report_data)
