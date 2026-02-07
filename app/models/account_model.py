"""
Account Model - Data Access Layer
Handles all DynamoDB operations for banking accounts
"""

import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import uuid
from decimal import Decimal


class AccountModel:
    """Account data model with DynamoDB operations"""
    
    def __init__(self, table_name, region_name='us-east-1'):
        """
        Initialize Account Model
        
        Args:
            table_name: DynamoDB table name for accounts
            region_name: AWS region
        """
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
        self.table_name = table_name
    
    def create_account(self, user_id, account_type='checking', initial_balance=0.00):
        """
        Create a new banking account for a user
        
        Args:
            user_id: User ID who owns this account
            account_type: Type of account (checking, savings, etc.)
            initial_balance: Initial account balance
            
        Returns:
            dict: Created account data
        """
        account_id = str(uuid.uuid4())
        account_number = self._generate_account_number()
        
        account_item = {
            'account_id': account_id,
            'user_id': user_id,
            'account_number': account_number,
            'account_type': account_type,
            'balance': Decimal(str(initial_balance)),
            'currency': 'USD',
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'last_transaction_date': None,
            'overdraft_limit': Decimal('0.00'),
            'interest_rate': Decimal('0.00')
        }
        
        self.table.put_item(Item=account_item)
        return self._convert_decimals(account_item)
    
    def get_account_by_id(self, account_id):
        """
        Retrieve account by account_id
        
        Args:
            account_id: Unique account identifier
            
        Returns:
            dict: Account data or None if not found
        """
        try:
            response = self.table.get_item(Key={'account_id': account_id})
            account = response.get('Item')
            return self._convert_decimals(account) if account else None
        except Exception as e:
            print(f"Error getting account by ID: {e}")
            return None
    
    def get_account_by_number(self, account_number):
        """
        Retrieve account by account number
        
        Args:
            account_number: Account number
            
        Returns:
            dict: Account data or None if not found
        """
        try:
            response = self.table.query(
                IndexName='AccountNumberIndex',  # GSI on account_number
                KeyConditionExpression=Key('account_number').eq(account_number)
            )
            
            if response['Items']:
                return self._convert_decimals(response['Items'][0])
            return None
        except Exception as e:
            print(f"Error querying account by number: {e}")
            return None
    
    def get_user_accounts(self, user_id):
        """
        Retrieve all accounts for a user
        
        Args:
            user_id: User ID
            
        Returns:
            list: List of account dictionaries
        """
        try:
            response = self.table.query(
                IndexName='UserIdIndex',  # GSI on user_id
                KeyConditionExpression=Key('user_id').eq(user_id)
            )
            
            accounts = response.get('Items', [])
            return [self._convert_decimals(acc) for acc in accounts]
        except Exception as e:
            print(f"Error getting user accounts: {e}")
            return []
    
    def update_balance(self, account_id, amount, operation='add'):
        """
        Update account balance atomically
        
        Args:
            account_id: Account ID
            amount: Amount to add or subtract
            operation: 'add' or 'subtract'
            
        Returns:
            dict: Updated account data
            
        Raises:
            ValueError: If insufficient funds or invalid operation
        """
        # Get current account to check balance
        account = self.get_account_by_id(account_id)
        
        if not account:
            raise ValueError("Account not found")
        
        if account['status'] != 'active':
            raise ValueError("Account is not active")
        
        amount_decimal = Decimal(str(amount))
        
        # Check for insufficient funds on subtract
        if operation == 'subtract':
            if account['balance'] < amount_decimal:
                raise ValueError("Insufficient funds")
            amount_decimal = -amount_decimal
        elif operation != 'add':
            raise ValueError("Invalid operation. Use 'add' or 'subtract'")
        
        # Atomic update using DynamoDB's ADD operation
        try:
            response = self.table.update_item(
                Key={'account_id': account_id},
                UpdateExpression='SET balance = balance + :amount, updated_at = :updated_at, last_transaction_date = :txn_date',
                ConditionExpression='attribute_exists(account_id) AND #status = :active',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':amount': amount_decimal,
                    ':updated_at': datetime.utcnow().isoformat(),
                    ':txn_date': datetime.utcnow().isoformat(),
                    ':active': 'active'
                },
                ReturnValues='ALL_NEW'
            )
            
            return self._convert_decimals(response['Attributes'])
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise ValueError("Account status changed during transaction")
        except Exception as e:
            print(f"Error updating balance: {e}")
            raise
    
    def get_balance(self, account_id):
        """
        Get current account balance
        
        Args:
            account_id: Account ID
            
        Returns:
            float: Current balance
        """
        account = self.get_account_by_id(account_id)
        if account:
            return float(account['balance'])
        return None
    
    def close_account(self, account_id):
        """
        Close/deactivate an account
        
        Args:
            account_id: Account ID
            
        Returns:
            bool: True if successful
        """
        account = self.get_account_by_id(account_id)
        
        if not account:
            raise ValueError("Account not found")
        
        if account['balance'] != 0:
            raise ValueError("Cannot close account with non-zero balance")
        
        self.table.update_item(
            Key={'account_id': account_id},
            UpdateExpression='SET #status = :status, updated_at = :updated_at',
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':status': 'closed',
                ':updated_at': datetime.utcnow().isoformat()
            }
        )
        
        return True
    
    def _generate_account_number(self):
        """
        Generate a unique 10-digit account number
        
        Returns:
            str: Account number
        """
        import random
        # Generate a 10-digit account number
        # In production, ensure uniqueness with retry logic
        account_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        
        # Check if exists (basic uniqueness check)
        existing = self.get_account_by_number(account_number)
        if existing:
            return self._generate_account_number()  # Retry if duplicate
        
        return account_number
    
    def _convert_decimals(self, obj):
        """
        Convert DynamoDB Decimal types to float for JSON serialization
        
        Args:
            obj: Dictionary or list containing Decimal values
            
        Returns:
            Object with Decimals converted to float
        """
        if obj is None:
            return None
        
        if isinstance(obj, list):
            return [self._convert_decimals(item) for item in obj]
        
        if isinstance(obj, dict):
            return {key: self._convert_decimals(value) for key, value in obj.items()}
        
        if isinstance(obj, Decimal):
            return float(obj)
        
        return obj
