"""
Analytics Routes - Presentation Layer
Handles analytics dashboard and reporting
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from app.services.analytics_service import AnalyticsService
from app.services.account_service import AccountService
from app.routes.auth_routes import login_required
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/dashboard')
@login_required
def dashboard():
    """Analytics dashboard"""
    user_id = session['user_id']
    
    # Get user accounts
    account_service = AccountService(current_app.config)
    accounts = account_service.get_user_accounts(user_id)
    
    # Get analytics for primary account or first account
    analytics_data = None
    if accounts:
        primary_account = accounts[0]  # Use first account as default
        
        analytics_service = AnalyticsService(current_app.config)
        analytics_data = analytics_service.get_account_analytics(
            account_id=primary_account['account_id'],
            user_id=user_id,
            days=30
        )
    
    return render_template('analytics_dashboard.html',
                         accounts=accounts,
                         analytics=analytics_data)


@analytics_bp.route('/account/<account_id>')
@login_required
def account_analytics(account_id):
    """Detailed analytics for specific account"""
    user_id = session['user_id']
    
    # Get account details
    account_service = AccountService(current_app.config)
    account_result = account_service.get_account_details(account_id, user_id)
    
    if not account_result['success']:
        flash(account_result['message'], 'danger')
        return redirect(url_for('analytics.dashboard'))
    
    # Get analytics
    analytics_service = AnalyticsService(current_app.config)
    
    # Get different time periods
    analytics_30d = analytics_service.get_account_analytics(account_id, user_id, days=30)
    analytics_90d = analytics_service.get_account_analytics(account_id, user_id, days=90)
    
    # Get compliance metrics
    compliance = analytics_service.get_compliance_metrics(account_id, user_id, days=90)
    
    return render_template('account_analytics.html',
                         account=account_result['account'],
                         analytics_30d=analytics_30d,
                         analytics_90d=analytics_90d,
                         compliance=compliance)


@analytics_bp.route('/monthly-report')
@login_required
def monthly_report():
    """Monthly transaction report"""
    user_id = session['user_id']
    
    # Get parameters
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    account_id = request.args.get('account_id')
    
    # Get user accounts
    account_service = AccountService(current_app.config)
    accounts = account_service.get_user_accounts(user_id)
    
    # Use first account if none specified
    if not account_id and accounts:
        account_id = accounts[0]['account_id']
    
    report = None
    if account_id:
        analytics_service = AnalyticsService(current_app.config)
        report = analytics_service.get_monthly_report(account_id, user_id, year, month)
    
    return render_template('monthly_report.html',
                         accounts=accounts,
                         report=report,
                         year=year,
                         month=month,
                         selected_account=account_id)


@analytics_bp.route('/yearly-report')
@login_required
def yearly_report():
    """Yearly transaction report"""
    user_id = session['user_id']
    
    # Get parameters
    year = request.args.get('year', datetime.now().year, type=int)
    account_id = request.args.get('account_id')
    
    # Get user accounts
    account_service = AccountService(current_app.config)
    accounts = account_service.get_user_accounts(user_id)
    
    # Use first account if none specified
    if not account_id and accounts:
        account_id = accounts[0]['account_id']
    
    report = None
    if account_id:
        analytics_service = AnalyticsService(current_app.config)
        report = analytics_service.get_yearly_report(account_id, user_id, year)
    
    return render_template('yearly_report.html',
                         accounts=accounts,
                         report=report,
                         year=year,
                         selected_account=account_id)


@analytics_bp.route('/compliance')
@login_required
def compliance():
    """Compliance and regulatory metrics"""
    user_id = session['user_id']
    
    # Get user accounts
    account_service = AccountService(current_app.config)
    accounts = account_service.get_user_accounts(user_id)
    
    # Get compliance metrics for all accounts
    analytics_service = AnalyticsService(current_app.config)
    compliance_data = []
    
    for account in accounts:
        metrics = analytics_service.get_compliance_metrics(
            account_id=account['account_id'],
            user_id=user_id,
            days=90
        )
        
        if metrics:
            metrics['account_number'] = account['account_number']
            metrics['account_type'] = account['account_type']
            compliance_data.append(metrics)
    
    return render_template('compliance.html',
                         compliance_data=compliance_data)


@analytics_bp.route('/api/analytics/<account_id>')
@login_required
def api_analytics(account_id):
    """API endpoint for analytics data"""
    user_id = session['user_id']
    days = request.args.get('days', 30, type=int)
    
    analytics_service = AnalyticsService(current_app.config)
    analytics = analytics_service.get_account_analytics(account_id, user_id, days)
    
    if analytics:
        return jsonify({'success': True, 'analytics': analytics})
    else:
        return jsonify({'success': False, 'message': 'Analytics not available'}), 404
