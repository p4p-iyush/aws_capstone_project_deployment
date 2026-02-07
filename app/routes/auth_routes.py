"""
Authentication Routes - Presentation Layer
Handles login, logout, and registration endpoints
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.services.auth_service import AuthService
from functools import wraps

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('account.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validate inputs
        if not email or not password:
            flash('Please provide both email and password', 'danger')
            return render_template('login.html')
        
        # Authenticate
        auth_service = AuthService(current_app.config)
        result = auth_service.login_user(email, password)
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('account.dashboard'))
        else:
            flash(result['message'], 'danger')
            return render_template('login.html', email=email)
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page and user creation"""
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('account.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validate inputs
        if not all([email, password, confirm_password, full_name]):
            flash('Please fill in all required fields', 'danger')
            return render_template('register.html', 
                                 email=email, full_name=full_name, phone=phone)
        
        # Register user
        auth_service = AuthService(current_app.config)
        result = auth_service.register_user(
            email=email,
            password=password,
            confirm_password=confirm_password,
            full_name=full_name,
            phone=phone
        )
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(result['message'], 'danger')
            return render_template('register.html',
                                 email=email, full_name=full_name, phone=phone)
    
    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """Logout user"""
    auth_service = AuthService(current_app.config)
    result = auth_service.logout_user()
    flash(result['message'], 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """View user profile"""
    auth_service = AuthService(current_app.config)
    user = auth_service.get_current_user()
    
    if not user:
        flash('Session expired. Please login again.', 'warning')
        return redirect(url_for('auth.login'))
    
    return render_template('profile.html', user=user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([old_password, new_password, confirm_password]):
            flash('Please fill in all password fields', 'danger')
            return render_template('change_password.html')
        
        auth_service = AuthService(current_app.config)
        result = auth_service.change_password(
            user_id=session['user_id'],
            old_password=old_password,
            new_password=new_password,
            confirm_password=confirm_password
        )
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('auth.profile'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('change_password.html')
