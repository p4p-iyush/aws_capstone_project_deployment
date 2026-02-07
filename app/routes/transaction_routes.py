"""
Transaction Routes - Presentation Layer
Handles deposits, withdrawals, transfers, and transaction history
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from app.services.transaction_service import TransactionService
from app.services.account_service import AccountService
from app.services.notification_service import NotificationService
from app.routes.auth_routes import login_required

transaction_bp = Blueprint('transactions', __name__)


@transaction_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    """Make a deposit"""
    user_id = session['user_id']
    
    # Get user accounts
    account_service = AccountService(current_app.config)
    accounts = account_service.get_user_accounts(user_id)
    
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Deposit')
        
        # Validate
        if not account_id or not amount:
            flash('Please select an account and enter an amount', 'danger')
            return render_template('deposit.html', accounts=accounts)
        
        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount format', 'danger')
            return render_template('deposit.html', accounts=accounts)
        
        # Process deposit
        transaction_service = TransactionService(current_app.config)
        result = transaction_service.deposit(
            account_id=account_id,
            amount=amount,
            description=description,
            user_id=user_id
        )
        
        if result['success']:
            flash(result['message'], 'success')
            
            # Send notification
            notification_service = NotificationService(current_app.config)
            account = account_service.get_account_details(account_id, user_id)['account']
            notification_service.check_and_alert_if_needed(
                user_email=session['email'],
                transaction_type='deposit',
                amount=amount,
                account_number=account['account_number'],
                new_balance=result['new_balance']
            )
            
            return redirect(url_for('transactions.history'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('deposit.html', accounts=accounts)


@transaction_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """Make a withdrawal"""
    user_id = session['user_id']
    
    # Get user accounts
    account_service = AccountService(current_app.config)
    accounts = account_service.get_user_accounts(user_id)
    
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Withdrawal')
        
        # Validate
        if not account_id or not amount:
            flash('Please select an account and enter an amount', 'danger')
            return render_template('withdraw.html', accounts=accounts)
        
        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount format', 'danger')
            return render_template('withdraw.html', accounts=accounts)
        
        # Process withdrawal
        transaction_service = TransactionService(current_app.config)
        result = transaction_service.withdraw(
            account_id=account_id,
            amount=amount,
            description=description,
            user_id=user_id
        )
        
        if result['success']:
            flash(result['message'], 'success')
            
            # Send notification
            notification_service = NotificationService(current_app.config)
            account = account_service.get_account_details(account_id, user_id)['account']
            notification_service.check_and_alert_if_needed(
                user_email=session['email'],
                transaction_type='withdrawal',
                amount=amount,
                account_number=account['account_number'],
                new_balance=result['new_balance']
            )
            
            return redirect(url_for('transactions.history'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('withdraw.html', accounts=accounts)


@transaction_bp.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    """Transfer money between accounts"""
    user_id = session['user_id']
    
    # Get user accounts
    account_service = AccountService(current_app.config)
    accounts = account_service.get_user_accounts(user_id)
    
    if request.method == 'POST':
        from_account_id = request.form.get('from_account_id')
        to_account_number = request.form.get('to_account_number')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Transfer')
        
        # Validate
        if not all([from_account_id, to_account_number, amount]):
            flash('Please fill in all required fields', 'danger')
            return render_template('transfer.html', accounts=accounts)
        
        try:
            amount = float(amount)
        except ValueError:
            flash('Invalid amount format', 'danger')
            return render_template('transfer.html', accounts=accounts)
        
        # Process transfer
        transaction_service = TransactionService(current_app.config)
        result = transaction_service.transfer(
            from_account_id=from_account_id,
            to_account_number=to_account_number,
            amount=amount,
            description=description,
            user_id=user_id
        )
        
        if result['success']:
            flash(result['message'], 'success')
            
            # Send notification
            notification_service = NotificationService(current_app.config)
            from_account = account_service.get_account_details(from_account_id, user_id)['account']
            notification_service.send_transfer_confirmation(
                sender_email=session['email'],
                recipient_account=to_account_number,
                amount=amount,
                new_balance=result['new_balance']
            )
            
            return redirect(url_for('transactions.history'))
        else:
            flash(result['message'], 'danger')
    
    return render_template('transfer.html', accounts=accounts)


@transaction_bp.route('/history')
@login_required
def history():
    """View transaction history for all accounts"""
    user_id = session['user_id']
    
    # Get user accounts
    account_service = AccountService(current_app.config)
    accounts = account_service.get_user_accounts(user_id)
    
    # Get transactions for each account
    transaction_service = TransactionService(current_app.config)
    all_transactions = []
    
    for account in accounts:
        result = transaction_service.get_transaction_history(
            account_id=account['account_id'],
            user_id=user_id,
            limit=50
        )
        
        if result['success']:
            # Add account info to each transaction
            for txn in result['transactions']:
                txn['account_number'] = account['account_number']
                txn['account_type'] = account['account_type']
            all_transactions.extend(result['transactions'])
    
    # Sort by timestamp (newest first)
    all_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('transactions.html', 
                         transactions=all_transactions,
                         accounts=accounts)


@transaction_bp.route('/history/<account_id>')
@login_required
def account_history(account_id):
    """View transaction history for specific account"""
    user_id = session['user_id']
    
    # Get account details
    account_service = AccountService(current_app.config)
    account_result = account_service.get_account_details(account_id, user_id)
    
    if not account_result['success']:
        flash(account_result['message'], 'danger')
        return redirect(url_for('transactions.history'))
    
    # Get transactions
    transaction_service = TransactionService(current_app.config)
    result = transaction_service.get_transaction_history(
        account_id=account_id,
        user_id=user_id,
        limit=100
    )
    
    return render_template('account_transactions.html',
                         account=account_result['account'],
                         transactions=result['transactions'])
