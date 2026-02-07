"""
Account Routes - Presentation Layer
Handles account management and dashboard
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from app.services.account_service import AccountService
from app.services.analytics_service import AnalyticsService
from app.routes.auth_routes import login_required

account_bp = Blueprint('account', __name__)


@account_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user_id = session['user_id']
    
    # Get dashboard data
    analytics_service = AnalyticsService(current_app.config)
    dashboard_data = analytics_service.get_dashboard_data(user_id)
    
    return render_template('dashboard.html', data=dashboard_data)


@account_bp.route('/accounts')
@login_required
def list_accounts():
    """List all user accounts"""
    user_id = session['user_id']
    
    account_service = AccountService(current_app.config)
    accounts = account_service.get_user_accounts(user_id)
    summary = account_service.get_account_summary(user_id)
    
    return render_template('accounts.html', accounts=accounts, summary=summary)


@account_bp.route('/account/<account_id>')
@login_required
def account_detail(account_id):
    """View account details"""
    user_id = session['user_id']
    
    account_service = AccountService(current_app.config)
    result = account_service.get_account_details(account_id, user_id)
    
    if not result['success']:
        flash(result['message'], 'danger')
        return redirect(url_for('account.list_accounts'))
    
    # Get analytics for this account
    analytics_service = AnalyticsService(current_app.config)
    analytics = analytics_service.get_account_analytics(account_id, user_id, days=30)
    
    return render_template('account_detail.html', 
                         account=result['account'],
                         analytics=analytics)


@account_bp.route('/create-account', methods=['GET', 'POST'])
@login_required
def create_account():
    """Create a new account"""
    if request.method == 'POST':
        account_type = request.form.get('account_type', 'checking')
        initial_balance = request.form.get('initial_balance', '0')
        
        try:
            initial_balance = float(initial_balance)
        except ValueError:
            flash('Invalid initial balance amount', 'danger')
            return render_template('create_account.html')
        
        account_service = AccountService(current_app.config)
        result = account_service.create_account(
            user_id=session['user_id'],
            account_type=account_type,
            initial_balance=initial_balance
        )
        
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('account.list_accounts'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('create_account.html')


@account_bp.route('/api/balance/<account_id>')
@login_required
def get_balance(account_id):
    """API endpoint to get account balance"""
    user_id = session['user_id']
    
    account_service = AccountService(current_app.config)
    result = account_service.get_account_balance(account_id, user_id)
    
    return jsonify(result)
