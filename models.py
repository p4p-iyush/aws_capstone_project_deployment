"""
Database Models
All DynamoDB operations for Users, Accounts, and Transactions
"""

import uuid
import bcrypt
from datetime import datetime, timedelta
from decimal import Decimal
from app_aws import get_dynamodb_table, USERS_TABLE, ACCOUNTS_TABLE, TRANSACTIONS_TABLE
import random


class User:
    """User model for authentication and profile management"""
    
    @staticmethod
    def create(email, password, full_name, phone=''):
        """Create a new user"""
        table = get_dynamodb_table(USERS_TABLE)
        
        # Check if user already exists
        response = table.query(
            IndexName='EmailIndex',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': email.lower()}
        )
        
        if response['Items']:
            raise ValueError('User with this email already exists')
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
        
        user_id = str(uuid.uuid4())
        user_data = {
            'user_id': user_id,
            'email': email.lower(),
            'password_hash': password_hash.decode('utf-8'),
            'full_name': full_name,
            'phone': phone,
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True,
            'failed_login_attempts': 0,
            'last_login': None
        }
        
        table.put_item(Item=user_data)
        user_data.pop('password_hash')
        return user_data
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        table = get_dynamodb_table(USERS_TABLE)
        response = table.query(
            IndexName='EmailIndex',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': email.lower()}
        )
        
        if response['Items']:
            return response['Items'][0]
        return None
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        table = get_dynamodb_table(USERS_TABLE)
        response = table.get_item(Key={'user_id': user_id})
        return response.get('Item')
    
    @staticmethod
    def verify_password(email, password):
        """Verify user password"""
        user = User.get_by_email(email)
        if not user:
            return None
        
        # Check if account is locked
        if user.get('account_locked_until'):
            lock_time = datetime.fromisoformat(user['account_locked_until'])
            if datetime.utcnow() < lock_time:
                raise ValueError('Account is locked. Please try again later.')
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Reset failed attempts and update last login
            table = get_dynamodb_table(USERS_TABLE)
            table.update_item(
                Key={'user_id': user['user_id']},
                UpdateExpression='SET failed_login_attempts = :zero, last_login = :now REMOVE account_locked_until',
                ExpressionAttributeValues={
                    ':zero': 0,
                    ':now': datetime.utcnow().isoformat()
                }
            )
            user.pop('password_hash', None)
            return user
        else:
            # Increment failed attempts
            table = get_dynamodb_table(USERS_TABLE)
            failed_attempts = user.get('failed_login_attempts', 0) + 1
            
            if failed_attempts >= 5:
                lock_until = datetime.utcnow() + timedelta(minutes=30)
                table.update_item(
                    Key={'user_id': user['user_id']},
                    UpdateExpression='SET failed_login_attempts = :attempts, account_locked_until = :lock',
                    ExpressionAttributeValues={
                        ':attempts': failed_attempts,
                        ':lock': lock_until.isoformat()
                    }
                )
                raise ValueError('Account locked due to too many failed attempts')
            else:
                table.update_item(
                    Key={'user_id': user['user_id']},
                    UpdateExpression='SET failed_login_attempts = :attempts',
                    ExpressionAttributeValues={':attempts': failed_attempts}
                )
            
            return None


class Account:
    """Account model for banking operations"""
    
    @staticmethod
    def create(user_id, account_type='checking', initial_balance=0.00):
        """Create a new account"""
        table = get_dynamodb_table(ACCOUNTS_TABLE)
        
        # Generate unique account number
        account_number = str(random.randint(1000000000, 9999999999))
        
        account_id = str(uuid.uuid4())
        account_data = {
            'account_id': account_id,
            'user_id': user_id,
            'account_number': account_number,
            'account_type': account_type,
            'balance': Decimal(str(initial_balance)),
            'currency': 'USD',
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        table.put_item(Item=account_data)
        return account_data
    
    @staticmethod
    def get_by_id(account_id):
        """Get account by ID"""
        table = get_dynamodb_table(ACCOUNTS_TABLE)
        response = table.get_item(Key={'account_id': account_id})
        return response.get('Item')
    
    @staticmethod
    def get_by_number(account_number):
        """Get account by account number"""
        table = get_dynamodb_table(ACCOUNTS_TABLE)
        response = table.query(
            IndexName='AccountNumberIndex',
            KeyConditionExpression='account_number = :number',
            ExpressionAttributeValues={':number': account_number}
        )
        
        if response['Items']:
            return response['Items'][0]
        return None
    
    @staticmethod
    def get_user_accounts(user_id):
        """Get all accounts for a user"""
        table = get_dynamodb_table(ACCOUNTS_TABLE)
        response = table.query(
            IndexName='UserIdIndex',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        return response.get('Items', [])
    
    @staticmethod
    def update_balance(account_id, amount, operation='add'):
        """Update account balance atomically"""
        table = get_dynamodb_table(ACCOUNTS_TABLE)
        
        # Get current account
        account = Account.get_by_id(account_id)
        if not account:
            raise ValueError('Account not found')
        
        if account['status'] != 'active':
            raise ValueError('Account is not active')
        
        amount_decimal = Decimal(str(amount))
        
        # Check for insufficient funds on subtract
        if operation == 'subtract':
            if account['balance'] < amount_decimal:
                raise ValueError('Insufficient funds')
        
        # Perform atomic update
        update_expr = 'SET balance = balance + :amt, updated_at = :now'
        if operation == 'subtract':
            update_expr = 'SET balance = balance - :amt, updated_at = :now'
        
        response = table.update_item(
            Key={'account_id': account_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues={
                ':amt': amount_decimal,
                ':now': datetime.utcnow().isoformat()
            },
            ReturnValues='ALL_NEW'
        )
        
        return response['Attributes']


class Transaction:
    """Transaction model for recording all transactions"""
    
    @staticmethod
    def create(account_id, transaction_type, amount, description='', related_account_id=None):
        """Create a new transaction record"""
        table = get_dynamodb_table(TRANSACTIONS_TABLE)
        
        transaction_id = str(uuid.uuid4())
        transaction_data = {
            'transaction_id': transaction_id,
            'account_id': account_id,
            'transaction_type': transaction_type,
            'amount': Decimal(str(amount)),
            'description': description,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'completed',
            'created_at': datetime.utcnow().isoformat()
        }
        
        if related_account_id:
            transaction_data['related_account_id'] = related_account_id
        
        table.put_item(Item=transaction_data)
        return transaction_data
    
    @staticmethod
    def get_account_transactions(account_id, limit=50):
        """Get transactions for an account"""
        table = get_dynamodb_table(TRANSACTIONS_TABLE)
        response = table.query(
            IndexName='AccountIdTimestampIndex',
            KeyConditionExpression='account_id = :aid',
            ExpressionAttributeValues={':aid': account_id},
            ScanIndexForward=False,
            Limit=limit
        )
        return response.get('Items', [])
    
    @staticmethod
    def get_recent_transactions(account_id, days=30):
        """Get recent transactions"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        table = get_dynamodb_table(TRANSACTIONS_TABLE)
        response = table.query(
            IndexName='AccountIdTimestampIndex',
            KeyConditionExpression='account_id = :aid AND #ts >= :cutoff',
            ExpressionAttributeNames={'#ts': 'timestamp'},
            ExpressionAttributeValues={
                ':aid': account_id,
                ':cutoff': cutoff_date.isoformat()
            },
            ScanIndexForward=False
        )
        return response.get('Items', [])
    
    @staticmethod
    def get_transaction_summary(account_id, days=30):
        """Get transaction summary statistics"""
        transactions = Transaction.get_recent_transactions(account_id, days)
        
        summary = {
            'total_deposits': 0.0,
            'total_withdrawals': 0.0,
            'total_transfers_in': 0.0,
            'total_transfers_out': 0.0,
            'transaction_count': len(transactions),
            'largest_transaction': 0.0,
            'average_transaction': 0.0
        }
        
        if not transactions:
            return summary
        
        for txn in transactions:
            amount = float(txn['amount'])
            
            if txn['transaction_type'] == 'deposit':
                summary['total_deposits'] += amount
            elif txn['transaction_type'] == 'withdrawal':
                summary['total_withdrawals'] += amount
            elif txn['transaction_type'] == 'transfer_in':
                summary['total_transfers_in'] += amount
            elif txn['transaction_type'] == 'transfer_out':
                summary['total_transfers_out'] += amount
            
            if amount > summary['largest_transaction']:
                summary['largest_transaction'] = amount
        
        total_amount = (
            summary['total_deposits'] + summary['total_withdrawals'] +
            summary['total_transfers_in'] + summary['total_transfers_out']
        )
        
        if summary['transaction_count'] > 0:
            summary['average_transaction'] = total_amount / summary['transaction_count']
        
        return summary
