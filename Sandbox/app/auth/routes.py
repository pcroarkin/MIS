from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact an administrator.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Log in the user and update last login time
        login_user(user, remember=form.remember_me.data)
        user.update_last_login()
        db.session.commit()
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Register a new user - admin only"""
    if not current_user.is_admin:
        flash('You do not have permission to register new users', 'danger')
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different username.', 'danger')
            return render_template('auth/register.html', title='Register User', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('auth/register.html', title='Register User', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            is_admin=form.is_admin.data,
            is_active=True,
            created_at=datetime.utcnow()
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash(f'User {user.username} has been registered successfully', 'success')
            return redirect(url_for('auth.users'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while registering the user. Please try again.', 'danger')
            return render_template('auth/register.html', title='Register User', form=form)
    
    return render_template('auth/register.html', title='Register User', form=form)

@bp.route('/users')
@login_required
def users():
    """List all users - admin only"""
    if not current_user.is_admin:
        flash('You do not have permission to view users', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.username).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    return render_template('auth/users.html', title='Users', users=users)

@bp.route('/users/<int:id>/activate')
@login_required
def activate_user(id):
    """Activate a user account - admin only"""
    if not current_user.is_admin:
        flash('You do not have permission to activate users', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    if user == current_user:
        flash('You cannot activate/deactivate your own account', 'danger')
    else:
        user.is_active = True
        db.session.commit()
        flash(f'User {user.username} has been activated', 'success')
    
    return redirect(url_for('auth.users'))

@bp.route('/users/<int:id>/deactivate')
@login_required
def deactivate_user(id):
    """Deactivate a user account - admin only"""
    if not current_user.is_admin:
        flash('You do not have permission to deactivate users', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    if user == current_user:
        flash('You cannot activate/deactivate your own account', 'danger')
    elif user.is_admin:
        flash('Cannot deactivate administrator accounts', 'danger')
    else:
        user.is_active = False
        db.session.commit()
        flash(f'User {user.username} has been deactivated', 'success')
    
    return redirect(url_for('auth.users'))

@bp.route('/users/<int:id>/toggle-admin')
@login_required
def toggle_admin(id):
    """Toggle administrator status - admin only"""
    if not current_user.is_admin:
        flash('You do not have permission to modify user roles', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    if user == current_user:
        flash('You cannot modify your own admin status', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        status = 'granted' if user.is_admin else 'revoked'
        flash(f'Administrator privileges {status} for {user.username}', 'success')
    
    return redirect(url_for('auth.users'))

@bp.route('/reset_password/<int:id>', methods=['GET', 'POST'])
@login_required
def reset_password(id):
    # Only admin users can reset passwords
    if not current_user.is_admin:
        flash('You do not have permission to reset passwords', 'danger')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password has been reset successfully', 'success')
        return redirect(url_for('auth.users'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form, user=user)
