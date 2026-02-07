"""
Transaction Service - Business Logic Layer
Handles deposits, withdrawals, transfers, and transaction history
"""

from app.models.account_model import AccountModel
from app.models.transaction_model import TransactionModel
from decimal import Decimal
from datetime import datetime


class TransactionService:
    """Transaction processing service"""
    
    def __init__(self, config):
        """
        Initialize Transaction Service
        
        Args:
            config: Flask app configuration object
        """
        self.config = config
        self.account_model = AccountModel(
            table_name=config['DYNAMODB_ACCOUNTS_TABLE'],
            region_name=config['AWS_REGION']
        )
        self.transaction_model = TransactionModel(
            table_name=config['DYNAMODB_TRANSACTIONS_TABLE'],
            region_name=config['AWS_REGION']
        )
        self.max_transaction_amount = config['MAX_TRANSACTION_AMOUNT']
        self.min_transfer_amount = config['MIN_TRANSFER_AMOUNT']
    
    def deposit(self, account_id, amount, description='Deposit', user_id=None):
        """
        Process a deposit transaction
        
        Args:
            account_id: Account ID
            amount: Deposit amount
            description: Transaction description
            user_id: User ID for verification (optional)
            
        Returns:
            dict: {'success': bool, 'message': str, 'transaction': dict, 'new_balance': float}
        """
        # Validate amount
        validation = self._validate_amount(amount)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message'],
                'transaction': None,
                'new_balance': None
            }
        
        # Verify account ownership if user_id provided
        if user_id:
            account = self.account_model.get_account_by_id(account_id)
            if not account or account['user_id'] != user_id:
                return {
                    'success': False,
                    'message': 'Unauthorized account access',
                    'transaction': None,
                    'new_balance': None
                }
        
        try:
            # Update account balance
            updated_account = self.account_model.update_balance(
                account_id=account_id,
                amount=amount,
                operation='add'
            )
            
            # Record transaction
            transaction = self.transaction_model.create_transaction(
                account_id=account_id,
                transaction_type='deposit',
                amount=amount,
                description=description
            )
            
            return {
                'success': True,
                'message': f'Deposit of ${amount:.2f} successful',
                'transaction': transaction,
                'new_balance': updated_account['balance']
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Deposit failed: {str(e)}',
                'transaction': None,
                'new_balance': None
            }
    
    def withdraw(self, account_id, amount, description='Withdrawal', user_id=None):
        """
        Process a withdrawal transaction
        
        Args:
            account_id: Account ID
            amount: Withdrawal amount
            description: Transaction description
            user_id: User ID for verification (optional)
            
        Returns:
            dict: {'success': bool, 'message': str, 'transaction': dict, 'new_balance': float}
        """
        # Validate amount
        validation = self._validate_amount(amount)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message'],
                'transaction': None,
                'new_balance': None
            }
        
        # Verify account ownership if user_id provided
        if user_id:
            account = self.account_model.get_account_by_id(account_id)
            if not account or account['user_id'] != user_id:
                return {
                    'success': False,
                    'message': 'Unauthorized account access',
                    'transaction': None,
                    'new_balance': None
                }
        
        try:
            # Update account balance (will check for insufficient funds)
            updated_account = self.account_model.update_balance(
                account_id=account_id,
                amount=amount,
                operation='subtract'
            )
            
            # Record transaction
            transaction = self.transaction_model.create_transaction(
                account_id=account_id,
                transaction_type='withdrawal',
                amount=amount,
                description=description
            )
            
            return {
                'success': True,
                'message': f'Withdrawal of ${amount:.2f} successful',
                'transaction': transaction,
                'new_balance': updated_account['balance']
            }
            
        except ValueError as e:
            return {
                'success': False,
                'message': str(e),
                'transaction': None,
                'new_balance': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Withdrawal failed: {str(e)}',
                'transaction': None,
                'new_balance': None
            }
    
    def transfer(self, from_account_id, to_account_number, amount, description='Transfer', user_id=None):
        """
        Process a transfer between accounts
        
        Args:
            from_account_id: Source account ID
            to_account_number: Destination account number
            amount: Transfer amount
            description: Transfer description
            user_id: User ID for verification (optional)
            
        Returns:
            dict: {'success': bool, 'message': str, 'transactions': list, 'new_balance': float}
        """
        # Validate amount
        validation = self._validate_amount(amount, is_transfer=True)
        if not validation['valid']:
            return {
                'success': False,
                'message': validation['message'],
                'transactions': None,
                'new_balance': None
            }
        
        # Get source account
        from_account = self.account_model.get_account_by_id(from_account_id)
        if not from_account:
            return {
                'success': False,
                'message': 'Source account not found',
                'transactions': None,
                'new_balance': None
            }
        
        # Verify ownership if user_id provided
        if user_id and from_account['user_id'] != user_id:
            return {
                'success': False,
                'message': 'Unauthorized account access',
                'transactions': None,
                'new_balance': None
            }
        
        # Get destination account
        to_account = self.account_model.get_account_by_number(to_account_number)
        if not to_account:
            return {
                'success': False,
                'message': 'Destination account not found',
                'transactions': None,
                'new_balance': None
            }
        
        # Prevent self-transfer
        if from_account['account_id'] == to_account['account_id']:
            return {
                'success': False,
                'message': 'Cannot transfer to the same account',
                'transactions': None,
                'new_balance': None
            }
        
        # Check destination account status
        if to_account['status'] != 'active':
            return {
                'success': False,
                'message': 'Destination account is not active',
                'transactions': None,
                'new_balance': None
            }
        
        try:
            # Debit from source account
            updated_from = self.account_model.update_balance(
                account_id=from_account_id,
                amount=amount,
                operation='subtract'
            )
            
            try:
                # Credit to destination account
                updated_to = self.account_model.update_balance(
                    account_id=to_account['account_id'],
                    amount=amount,
                    operation='add'
                )
                
                # Record both transactions
                txn_out = self.transaction_model.create_transaction(
                    account_id=from_account_id,
                    transaction_type='transfer_out',
                    amount=amount,
                    description=f'{description} to {to_account_number}',
                    related_account_id=to_account['account_id']
                )
                
                txn_in = self.transaction_model.create_transaction(
                    account_id=to_account['account_id'],
                    transaction_type='transfer_in',
                    amount=amount,
                    description=f'{description} from {from_account["account_number"]}',
                    related_account_id=from_account_id
                )
                
                return {
                    'success': True,
                    'message': f'Transfer of ${amount:.2f} to {to_account_number} successful',
                    'transactions': [txn_out, txn_in],
                    'new_balance': updated_from['balance']
                }
                
            except Exception as credit_error:
                # Rollback: Re-credit the source account
                self.account_model.update_balance(
                    account_id=from_account_id,
                    amount=amount,
                    operation='add'
                )
                raise credit_error
                
        except ValueError as e:
            return {
                'success': False,
                'message': str(e),
                'transactions': None,
                'new_balance': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Transfer failed: {str(e)}',
                'transactions': None,
                'new_balance': None
            }
    
    def get_transaction_history(self, account_id, user_id, limit=50):
        """
        Get transaction history for an account
        
        Args:
            account_id: Account ID
            user_id: User ID for verification
            limit: Number of transactions to retrieve
            
        Returns:
            dict: {'success': bool, 'transactions': list}
        """
        # Verify account ownership
        account = self.account_model.get_account_by_id(account_id)
        if not account or account['user_id'] != user_id:
            return {
                'success': False,
                'transactions': [],
                'message': 'Unauthorized account access'
            }
        
        try:
            transactions = self.transaction_model.get_account_transactions(
                account_id=account_id,
                limit=limit
            )
            
            return {
                'success': True,
                'transactions': transactions,
                'message': f'Retrieved {len(transactions)} transactions'
            }
        except Exception as e:
            return {
                'success': False,
                'transactions': [],
                'message': f'Error retrieving transactions: {str(e)}'
            }
    
    def get_recent_transactions(self, account_id, user_id, days=30):
        """
        Get recent transactions for an account
        
        Args:
            account_id: Account ID
            user_id: User ID for verification
            days: Number of days to look back
            
        Returns:
            dict: {'success': bool, 'transactions': list}
        """
        # Verify account ownership
        account = self.account_model.get_account_by_id(account_id)
        if not account or account['user_id'] != user_id:
            return {
                'success': False,
                'transactions': []
            }
        
        try:
            transactions = self.transaction_model.get_recent_transactions(
                account_id=account_id,
                days=days
            )
            
            return {
                'success': True,
                'transactions': transactions
            }
        except Exception as e:
            return {
                'success': False,
                'transactions': []
            }
    
    def _validate_amount(self, amount, is_transfer=False):
        """
        Validate transaction amount
        
        Args:
            amount: Amount to validate
            is_transfer: Whether this is a transfer transaction
            
        Returns:
            dict: {'valid': bool, 'message': str}
        """
        try:
            amount_decimal = Decimal(str(amount))
        except:
            return {'valid': False, 'message': 'Invalid amount format'}
        
        if amount_decimal <= 0:
            return {'valid': False, 'message': 'Amount must be greater than zero'}
        
        if is_transfer and amount_decimal < Decimal(str(self.min_transfer_amount)):
            return {
                'valid': False,
                'message': f'Minimum transfer amount is ${self.min_transfer_amount:.2f}'
            }
        
        if amount_decimal > Decimal(str(self.max_transaction_amount)):
            return {
                'valid': False,
                'message': f'Maximum transaction amount is ${self.max_transaction_amount:,.2f}'
            }
        
        return {'valid': True, 'message': 'Valid amount'}
