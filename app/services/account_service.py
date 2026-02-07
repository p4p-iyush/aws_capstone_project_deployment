"""
Account Service - Business Logic Layer
Handles account operations, balance management, and account queries
"""

from app.models.account_model import AccountModel
from app.models.user_model import UserModel


class AccountService:
    """Account management service"""
    
    def __init__(self, config):
        """
        Initialize Account Service
        
        Args:
            config: Flask app configuration object
        """
        self.config = config
        self.account_model = AccountModel(
            table_name=config['DYNAMODB_ACCOUNTS_TABLE'],
            region_name=config['AWS_REGION']
        )
        self.user_model = UserModel(
            table_name=config['DYNAMODB_USERS_TABLE'],
            region_name=config['AWS_REGION']
        )
    
    def create_account(self, user_id, account_type='checking', initial_balance=0.00):
        """
        Create a new account for user
        
        Args:
            user_id: User ID
            account_type: Type of account (checking, savings)
            initial_balance: Initial balance
            
        Returns:
            dict: {'success': bool, 'message': str, 'account': dict}
        """
        # Verify user exists
        user = self.user_model.get_user_by_id(user_id)
        if not user:
            return {
                'success': False,
                'message': 'User not found',
                'account': None
            }
        
        # Validate account type
        valid_types = ['checking', 'savings']
        if account_type not in valid_types:
            return {
                'success': False,
                'message': f'Invalid account type. Must be one of: {valid_types}',
                'account': None
            }
        
        # Validate initial balance
        if initial_balance < 0:
            return {
                'success': False,
                'message': 'Initial balance cannot be negative',
                'account': None
            }
        
        try:
            account = self.account_model.create_account(
                user_id=user_id,
                account_type=account_type,
                initial_balance=initial_balance
            )
            
            return {
                'success': True,
                'message': f'{account_type.capitalize()} account created successfully',
                'account': account
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Account creation failed: {str(e)}',
                'account': None
            }
    
    def get_user_accounts(self, user_id):
        """
        Get all accounts for a user
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of accounts
        """
        try:
            accounts = self.account_model.get_user_accounts(user_id)
            return accounts
        except Exception as e:
            print(f"Error fetching user accounts: {e}")
            return []
    
    def get_account_details(self, account_id, user_id):
        """
        Get account details with ownership verification
        
        Args:
            account_id: Account ID
            user_id: User ID (for verification)
            
        Returns:
            dict: {'success': bool, 'message': str, 'account': dict}
        """
        try:
            account = self.account_model.get_account_by_id(account_id)
            
            if not account:
                return {
                    'success': False,
                    'message': 'Account not found',
                    'account': None
                }
            
            # Verify ownership
            if account['user_id'] != user_id:
                return {
                    'success': False,
                    'message': 'Unauthorized access to account',
                    'account': None
                }
            
            return {
                'success': True,
                'message': 'Account retrieved successfully',
                'account': account
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving account: {str(e)}',
                'account': None
            }
    
    def get_account_balance(self, account_id, user_id):
        """
        Get current account balance with verification
        
        Args:
            account_id: Account ID
            user_id: User ID (for verification)
            
        Returns:
            dict: {'success': bool, 'balance': float, 'message': str}
        """
        result = self.get_account_details(account_id, user_id)
        
        if result['success']:
            return {
                'success': True,
                'balance': result['account']['balance'],
                'message': 'Balance retrieved successfully'
            }
        else:
            return {
                'success': False,
                'balance': None,
                'message': result['message']
            }
    
    def get_total_balance(self, user_id):
        """
        Calculate total balance across all user accounts
        
        Args:
            user_id: User ID
            
        Returns:
            float: Total balance
        """
        accounts = self.get_user_accounts(user_id)
        total = sum(acc['balance'] for acc in accounts)
        return total
    
    def get_account_summary(self, user_id):
        """
        Get summary of all user accounts
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Account summary with totals
        """
        accounts = self.get_user_accounts(user_id)
        
        summary = {
            'total_accounts': len(accounts),
            'total_balance': 0.0,
            'accounts_by_type': {},
            'active_accounts': 0,
            'accounts': accounts
        }
        
        for account in accounts:
            # Add to total
            summary['total_balance'] += account['balance']
            
            # Count active accounts
            if account['status'] == 'active':
                summary['active_accounts'] += 1
            
            # Group by type
            acc_type = account['account_type']
            if acc_type not in summary['accounts_by_type']:
                summary['accounts_by_type'][acc_type] = {
                    'count': 0,
                    'total_balance': 0.0
                }
            
            summary['accounts_by_type'][acc_type]['count'] += 1
            summary['accounts_by_type'][acc_type]['total_balance'] += account['balance']
        
        return summary
    
    def close_account(self, account_id, user_id):
        """
        Close an account with verification
        
        Args:
            account_id: Account ID
            user_id: User ID (for verification)
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        # Verify ownership
        result = self.get_account_details(account_id, user_id)
        if not result['success']:
            return {
                'success': False,
                'message': result['message']
            }
        
        try:
            self.account_model.close_account(account_id)
            return {
                'success': True,
                'message': 'Account closed successfully'
            }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Account closure failed: {str(e)}'
            }
    
    def get_primary_account(self, user_id):
        """
        Get user's primary (first active) account
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Account or None
        """
        accounts = self.get_user_accounts(user_id)
        
        # Return first active account
        for account in accounts:
            if account['status'] == 'active':
                return account
        
        return None
