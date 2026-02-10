"""
Banking Data Analytics System
Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import os
from decimal import Decimal
from models import User, Account, Transaction

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'

# Configuration
HIGH_VALUE_THRESHOLD = float(os.environ.get('HIGH_VALUE_THRESHOLD', 10000))


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page - redirect to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Validation
        if not all([email, password, confirm_password, full_name]):
            flash('Please fill in all required fields', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'danger')
            return render_template('register.html')
        
        try:
            # Create user
            user = User.create(email, password, full_name, phone)
            
            # Create default checking account
            Account.create(user['user_id'], 'checking', 0.00)
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please provide email and password', 'danger')
            return render_template('login.html')
        
        try:
            user = User.verify_password(email, password)
            
            if user:
                session['user_id'] = user['user_id']
                session['email'] = user['email']
                session['full_name'] = user['full_name']
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'danger')
                
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))


# ============================================================================
# DASHBOARD
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user_id = session['user_id']
    
    # Get all user accounts
    accounts = Account.get_user_accounts(user_id)
    
    # Calculate totals
    total_balance = sum(float(acc['balance']) for acc in accounts)
    
    # Get recent transactions from all accounts
    recent_transactions = []
    for account in accounts:
        txns = Transaction.get_recent_transactions(account['account_id'], days=7)
        for txn in txns:
            txn['account_number'] = account['account_number']
        recent_transactions.extend(txns[:5])
    
    # Sort by timestamp
    recent_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_transactions = recent_transactions[:10]
    
    # Calculate spending
    spending_7d = 0
    spending_30d = 0
    
    for account in accounts:
        txns_30d = Transaction.get_recent_transactions(account['account_id'], days=30)
        txns_7d = Transaction.get_recent_transactions(account['account_id'], days=7)
        
        spending_7d += sum(
            float(t['amount']) for t in txns_7d 
            if t['transaction_type'] in ['withdrawal', 'transfer_out']
        )
        
        spending_30d += sum(
            float(t['amount']) for t in txns_30d 
            if t['transaction_type'] in ['withdrawal', 'transfer_out']
        )
    
    return render_template('dashboard.html',
                         accounts=accounts,
                         total_balance=total_balance,
                         recent_transactions=recent_transactions,
                         spending_7d=spending_7d,
                         spending_30d=spending_30d)


# ============================================================================
# ACCOUNT ROUTES
# ============================================================================

@app.route('/accounts')
@login_required
def accounts():
    """List all accounts"""
    user_id = session['user_id']
    user_accounts = Account.get_user_accounts(user_id)
    
    total_balance = sum(float(acc['balance']) for acc in user_accounts)
    active_count = sum(1 for acc in user_accounts if acc['status'] == 'active')
    
    return render_template('accounts.html',
                         accounts=user_accounts,
                         total_balance=total_balance,
                         active_count=active_count)


@app.route('/accounts/create', methods=['GET', 'POST'])
@login_required
def create_account():
    """Create new account"""
    if request.method == 'POST':
        account_type = request.form.get('account_type', 'checking')
        initial_balance = request.form.get('initial_balance', '0')
        
        try:
            initial_balance = float(initial_balance)
            if initial_balance < 0:
                flash('Initial balance cannot be negative', 'danger')
                return render_template('create_account.html')
            
            account = Account.create(session['user_id'], account_type, initial_balance)
            flash(f'{account_type.capitalize()} account created successfully!', 'success')
            return redirect(url_for('accounts'))
            
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Account creation failed: {str(e)}', 'danger')
    
    return render_template('create_account.html')


# ============================================================================
# TRANSACTION ROUTES
# ============================================================================

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    """Make a deposit"""
    user_id = session['user_id']
    accounts = Account.get_user_accounts(user_id)
    
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Deposit')
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than zero', 'danger')
                return render_template('deposit.html', accounts=accounts)
            
            # Update balance
            updated_account = Account.update_balance(account_id, amount, 'add')
            
            # Record transaction
            Transaction.create(account_id, 'deposit', amount, description)
            
            flash(f'Deposit of ${amount:.2f} successful!', 'success')
            return redirect(url_for('transactions'))
            
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Deposit failed: {str(e)}', 'danger')
    
    return render_template('deposit.html', accounts=accounts)


@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """Make a withdrawal"""
    user_id = session['user_id']
    accounts = Account.get_user_accounts(user_id)
    
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Withdrawal')
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than zero', 'danger')
                return render_template('withdraw.html', accounts=accounts)
            
            # Update balance
            updated_account = Account.update_balance(account_id, amount, 'subtract')
            
            # Record transaction
            Transaction.create(account_id, 'withdrawal', amount, description)
            
            flash(f'Withdrawal of ${amount:.2f} successful!', 'success')
            return redirect(url_for('transactions'))
            
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Withdrawal failed: {str(e)}', 'danger')
    
    return render_template('withdraw.html', accounts=accounts)


@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    """Transfer money"""
    user_id = session['user_id']
    accounts = Account.get_user_accounts(user_id)
    
    if request.method == 'POST':
        from_account_id = request.form.get('from_account_id')
        to_account_number = request.form.get('to_account_number')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Transfer')
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than zero', 'danger')
                return render_template('transfer.html', accounts=accounts)
            
            # Get destination account
            to_account = Account.get_by_number(to_account_number)
            if not to_account:
                flash('Destination account not found', 'danger')
                return render_template('transfer.html', accounts=accounts)
            
            # Prevent self-transfer
            if from_account_id == to_account['account_id']:
                flash('Cannot transfer to same account', 'danger')
                return render_template('transfer.html', accounts=accounts)
            
            # Debit sender
            Account.update_balance(from_account_id, amount, 'subtract')
            
            try:
                # Credit receiver
                Account.update_balance(to_account['account_id'], amount, 'add')
                
                # Record transactions
                Transaction.create(from_account_id, 'transfer_out', amount, 
                                 f'{description} to {to_account_number}',
                                 to_account['account_id'])
                
                from_account = Account.get_by_id(from_account_id)
                Transaction.create(to_account['account_id'], 'transfer_in', amount,
                                 f'{description} from {from_account["account_number"]}',
                                 from_account_id)
                
                flash(f'Transfer of ${amount:.2f} successful!', 'success')
                return redirect(url_for('transactions'))
                
            except Exception as credit_error:
                # Rollback
                Account.update_balance(from_account_id, amount, 'add')
                raise credit_error
            
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Transfer failed: {str(e)}', 'danger')
    
    return render_template('transfer.html', accounts=accounts)


@app.route('/transactions')
@login_required
def transactions():
    """View all transactions"""
    user_id = session['user_id']
    accounts = Account.get_user_accounts(user_id)
    
    all_transactions = []
    for account in accounts:
        txns = Transaction.get_account_transactions(account['account_id'], limit=50)
        for txn in txns:
            txn['account_number'] = account['account_number']
            txn['account_type'] = account['account_type']
        all_transactions.extend(txns)
    
    # Sort by timestamp
    all_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('transactions.html',
                         transactions=all_transactions,
                         accounts=accounts)


# ============================================================================
# ANALYTICS ROUTES
# ============================================================================

@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard"""
    user_id = session['user_id']
    accounts = Account.get_user_accounts(user_id)
    
    if not accounts:
        flash('No accounts found. Create an account first.', 'info')
        return redirect(url_for('create_account'))
    
    # Use first account for analytics
    primary_account = accounts[0]
    
    # Get summary
    summary = Transaction.get_transaction_summary(primary_account['account_id'], days=30)
    
    # Add account info
    summary['account_number'] = primary_account['account_number']
    summary['current_balance'] = float(primary_account['balance'])
    
    # Calculate net change
    summary['net_change'] = (
        summary['total_deposits'] + summary['total_transfers_in'] -
        summary['total_withdrawals'] - summary['total_transfers_out']
    )
    
    return render_template('analytics.html',
                         summary=summary,
                         accounts=accounts,
                         selected_account=primary_account)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ============================================================================
# TEMPLATE FILTERS
# ============================================================================

@app.template_filter('currency')
def currency_filter(value):
    """Format value as currency"""
    try:
        return f"${float(value):,.2f}"
    except:
        return "$0.00"


@app.template_filter('datetime_format')
def datetime_format(value, format='%Y-%m-%d %H:%M'):
    """Format datetime string"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return dt.strftime(format)
    except:
        return value


@app.template_filter('transaction_badge')
def transaction_badge(transaction_type):
    """Get badge class for transaction type"""
    badges = {
        'deposit': 'success',
        'withdrawal': 'warning',
        'transfer_in': 'info',
        'transfer_out': 'primary'
    }
    return badges.get(transaction_type, 'secondary')


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
