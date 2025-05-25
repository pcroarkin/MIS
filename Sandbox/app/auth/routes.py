from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm
from app.models import User
from werkzeug.urls import url_parse

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
        
        login_user(user, remember=form.remember_me.data)
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
    # Only admin users can register new users
    if not current_user.is_admin:
        flash('You do not have permission to register new users', 'danger')
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            is_admin=form.is_admin.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User has been registered successfully', 'success')
        return redirect(url_for('auth.users'))
    
    return render_template('auth/register.html', title='Register User', form=form)

@bp.route('/users')
@login_required
def users():
    # Only admin users can view user list
    if not current_user.is_admin:
        flash('You do not have permission to view users', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('auth/users.html', title='Users', users=users)

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
