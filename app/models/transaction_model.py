"""
Transaction Model - Data Access Layer
Handles all DynamoDB operations for transaction records
"""

import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime, timedelta
import uuid
from decimal import Decimal


class TransactionModel:
    """Transaction data model with DynamoDB operations"""
    
    def __init__(self, table_name, region_name='us-east-1'):
        """
        Initialize Transaction Model
        
        Args:
            table_name: DynamoDB table name for transactions
            region_name: AWS region
        """
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
        self.table_name = table_name
    
    def create_transaction(self, account_id, transaction_type, amount, 
                          description='', related_account_id=None, metadata=None):
        """
        Create a new transaction record
        
        Args:
            account_id: Account ID for this transaction
            transaction_type: Type (deposit, withdrawal, transfer_in, transfer_out)
            amount: Transaction amount
            description: Optional description
            related_account_id: For transfers, the other account involved
            metadata: Additional metadata dictionary
            
        Returns:
            dict: Created transaction data
        """
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        transaction_item = {
            'transaction_id': transaction_id,
            'account_id': account_id,
            'transaction_type': transaction_type,
            'amount': Decimal(str(amount)),
            'description': description,
            'status': 'completed',
            'timestamp': timestamp,
            'created_at': timestamp,
            'related_account_id': related_account_id or '',
            'metadata': metadata or {}
        }
        
        self.table.put_item(Item=transaction_item)
        return self._convert_decimals(transaction_item)
    
    def get_transaction_by_id(self, transaction_id):
        """
        Retrieve transaction by ID
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            dict: Transaction data or None
        """
        try:
            response = self.table.get_item(Key={'transaction_id': transaction_id})
            transaction = response.get('Item')
            return self._convert_decimals(transaction) if transaction else None
        except Exception as e:
            print(f"Error getting transaction: {e}")
            return None
    
    def get_account_transactions(self, account_id, limit=50, start_date=None, end_date=None):
        """
        Retrieve transactions for an account with optional date filtering
        
        Args:
            account_id: Account ID
            limit: Maximum number of transactions to return
            start_date: Optional start date (ISO format string)
            end_date: Optional end date (ISO format string)
            
        Returns:
            list: List of transaction dictionaries
        """
        try:
            # Build query
            key_condition = Key('account_id').eq(account_id)
            
            query_params = {
                'IndexName': 'AccountIdTimestampIndex',  # GSI on account_id and timestamp
                'KeyConditionExpression': key_condition,
                'Limit': limit,
                'ScanIndexForward': False  # Sort by timestamp descending (newest first)
            }
            
            # Add date range filter if provided
            if start_date or end_date:
                filter_expressions = []
                
                if start_date:
                    filter_expressions.append(Attr('timestamp').gte(start_date))
                if end_date:
                    filter_expressions.append(Attr('timestamp').lte(end_date))
                
                if filter_expressions:
                    filter_expr = filter_expressions[0]
                    for expr in filter_expressions[1:]:
                        filter_expr = filter_expr & expr
                    query_params['FilterExpression'] = filter_expr
            
            response = self.table.query(**query_params)
            transactions = response.get('Items', [])
            
            return [self._convert_decimals(txn) for txn in transactions]
        except Exception as e:
            print(f"Error getting account transactions: {e}")
            return []
    
    def get_recent_transactions(self, account_id, days=30, limit=100):
        """
        Get recent transactions for an account
        
        Args:
            account_id: Account ID
            days: Number of days to look back
            limit: Maximum transactions to return
            
        Returns:
            list: Recent transactions
        """
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        return self.get_account_transactions(
            account_id=account_id,
            limit=limit,
            start_date=start_date
        )
    
    def get_transaction_summary(self, account_id, start_date=None, end_date=None):
        """
        Calculate transaction summary for an account
        
        Args:
            account_id: Account ID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            dict: Summary with totals by type
        """
        transactions = self.get_account_transactions(
            account_id=account_id,
            limit=1000,  # Get more for summary
            start_date=start_date,
            end_date=end_date
        )
        
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
        
        total_amount = 0.0
        for txn in transactions:
            amount = float(txn['amount'])
            total_amount += amount
            
            # Update largest transaction
            if amount > summary['largest_transaction']:
                summary['largest_transaction'] = amount
            
            # Categorize by type
            txn_type = txn['transaction_type']
            if txn_type == 'deposit':
                summary['total_deposits'] += amount
            elif txn_type == 'withdrawal':
                summary['total_withdrawals'] += amount
            elif txn_type == 'transfer_in':
                summary['total_transfers_in'] += amount
            elif txn_type == 'transfer_out':
                summary['total_transfers_out'] += amount
        
        # Calculate average
        if summary['transaction_count'] > 0:
            summary['average_transaction'] = total_amount / summary['transaction_count']
        
        return summary
    
    def get_high_value_transactions(self, account_id, threshold=10000.0, days=30):
        """
        Get high-value transactions for compliance monitoring
        
        Args:
            account_id: Account ID
            threshold: Amount threshold for high-value
            days: Number of days to look back
            
        Returns:
            list: High-value transactions
        """
        transactions = self.get_recent_transactions(account_id, days=days)
        
        high_value = [
            txn for txn in transactions 
            if float(txn['amount']) >= threshold
        ]
        
        return high_value
    
    def search_transactions(self, account_id, search_term):
        """
        Search transactions by description
        
        Args:
            account_id: Account ID
            search_term: Search string
            
        Returns:
            list: Matching transactions
        """
        transactions = self.get_account_transactions(account_id, limit=500)
        
        search_lower = search_term.lower()
        matching = [
            txn for txn in transactions
            if search_lower in txn.get('description', '').lower()
        ]
        
        return matching
    
    def get_monthly_summary(self, account_id, year, month):
        """
        Get transaction summary for a specific month
        
        Args:
            account_id: Account ID
            year: Year (e.g., 2024)
            month: Month (1-12)
            
        Returns:
            dict: Monthly summary
        """
        from calendar import monthrange
        
        # Calculate start and end dates for the month
        start_date = datetime(year, month, 1).isoformat()
        last_day = monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59).isoformat()
        
        return self.get_transaction_summary(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_yearly_summary(self, account_id, year):
        """
        Get transaction summary for entire year
        
        Args:
            account_id: Account ID
            year: Year
            
        Returns:
            dict: Yearly summary with monthly breakdown
        """
        monthly_summaries = []
        
        for month in range(1, 13):
            summary = self.get_monthly_summary(account_id, year, month)
            summary['month'] = month
            summary['month_name'] = datetime(year, month, 1).strftime('%B')
            monthly_summaries.append(summary)
        
        # Calculate yearly totals
        yearly_total = {
            'year': year,
            'total_deposits': sum(m['total_deposits'] for m in monthly_summaries),
            'total_withdrawals': sum(m['total_withdrawals'] for m in monthly_summaries),
            'total_transfers_in': sum(m['total_transfers_in'] for m in monthly_summaries),
            'total_transfers_out': sum(m['total_transfers_out'] for m in monthly_summaries),
            'transaction_count': sum(m['transaction_count'] for m in monthly_summaries),
            'monthly_breakdown': monthly_summaries
        }
        
        return yearly_total
    
    def _convert_decimals(self, obj):
        """Convert DynamoDB Decimals to float"""
        if obj is None:
            return None
        
        if isinstance(obj, list):
            return [self._convert_decimals(item) for item in obj]
        
        if isinstance(obj, dict):
            return {key: self._convert_decimals(value) for key, value in obj.items()}
        
        if isinstance(obj, Decimal):
            return float(obj)
        
        return obj
