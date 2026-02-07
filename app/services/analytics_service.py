"""
Analytics Service - Business Logic Layer
Handles transaction analytics, reporting, and compliance metrics
"""

from app.models.transaction_model import TransactionModel
from app.models.account_model import AccountModel
from datetime import datetime, timedelta
from collections import defaultdict


class AnalyticsService:
    """Analytics and reporting service"""
    
    def __init__(self, config):
        """
        Initialize Analytics Service
        
        Args:
            config: Flask app configuration object
        """
        self.config = config
        self.transaction_model = TransactionModel(
            table_name=config['DYNAMODB_TRANSACTIONS_TABLE'],
            region_name=config['AWS_REGION']
        )
        self.account_model = AccountModel(
            table_name=config['DYNAMODB_ACCOUNTS_TABLE'],
            region_name=config['AWS_REGION']
        )
        self.high_value_threshold = config['HIGH_VALUE_TRANSACTION_THRESHOLD']
        self.suspicious_threshold = config['SUSPICIOUS_ACTIVITY_THRESHOLD']
    
    def get_account_analytics(self, account_id, user_id, days=30):
        """
        Get comprehensive analytics for an account
        
        Args:
            account_id: Account ID
            user_id: User ID for verification
            days: Number of days for analysis
            
        Returns:
            dict: Analytics summary
        """
        # Verify ownership
        account = self.account_model.get_account_by_id(account_id)
        if not account or account['user_id'] != user_id:
            return None
        
        # Get transactions
        transactions = self.transaction_model.get_recent_transactions(
            account_id=account_id,
            days=days
        )
        
        # Calculate analytics
        analytics = {
            'account_id': account_id,
            'account_number': account['account_number'],
            'current_balance': account['balance'],
            'period_days': days,
            'transaction_count': len(transactions),
            'total_deposits': 0.0,
            'total_withdrawals': 0.0,
            'total_transfers_out': 0.0,
            'total_transfers_in': 0.0,
            'net_change': 0.0,
            'average_transaction': 0.0,
            'largest_transaction': 0.0,
            'smallest_transaction': float('inf') if transactions else 0.0,
            'high_value_count': 0,
            'transactions_by_day': defaultdict(int),
            'transactions_by_type': defaultdict(int),
            'spending_pattern': {},
            'recent_transactions': transactions[:10]  # Last 10
        }
        
        if not transactions:
            analytics['smallest_transaction'] = 0.0
            return analytics
        
        # Process each transaction
        for txn in transactions:
            amount = float(txn['amount'])
            txn_type = txn['transaction_type']
            txn_date = datetime.fromisoformat(txn['timestamp']).date()
            
            # Update totals by type
            if txn_type == 'deposit':
                analytics['total_deposits'] += amount
            elif txn_type == 'withdrawal':
                analytics['total_withdrawals'] += amount
            elif txn_type == 'transfer_out':
                analytics['total_transfers_out'] += amount
            elif txn_type == 'transfer_in':
                analytics['total_transfers_in'] += amount
            
            # Track high-value transactions
            if amount >= self.high_value_threshold:
                analytics['high_value_count'] += 1
            
            # Update min/max
            if amount > analytics['largest_transaction']:
                analytics['largest_transaction'] = amount
            if amount < analytics['smallest_transaction']:
                analytics['smallest_transaction'] = amount
            
            # Count by day
            analytics['transactions_by_day'][str(txn_date)] += 1
            
            # Count by type
            analytics['transactions_by_type'][txn_type] += 1
        
        # Calculate net change
        analytics['net_change'] = (
            analytics['total_deposits'] + analytics['total_transfers_in'] -
            analytics['total_withdrawals'] - analytics['total_transfers_out']
        )
        
        # Calculate average
        if analytics['transaction_count'] > 0:
            total_amount = (
                analytics['total_deposits'] + analytics['total_withdrawals'] +
                analytics['total_transfers_out'] + analytics['total_transfers_in']
            )
            analytics['average_transaction'] = total_amount / analytics['transaction_count']
        
        # Spending pattern analysis
        analytics['spending_pattern'] = self._analyze_spending_pattern(transactions)
        
        return analytics
    
    def get_monthly_report(self, account_id, user_id, year, month):
        """
        Generate monthly transaction report
        
        Args:
            account_id: Account ID
            user_id: User ID for verification
            year: Year
            month: Month (1-12)
            
        Returns:
            dict: Monthly report
        """
        # Verify ownership
        account = self.account_model.get_account_by_id(account_id)
        if not account or account['user_id'] != user_id:
            return None
        
        # Get monthly summary from transaction model
        summary = self.transaction_model.get_monthly_summary(
            account_id=account_id,
            year=year,
            month=month
        )
        
        # Add account context
        summary['account_number'] = account['account_number']
        summary['account_type'] = account['account_type']
        summary['current_balance'] = account['balance']
        summary['month_name'] = datetime(year, month, 1).strftime('%B')
        summary['year'] = year
        
        return summary
    
    def get_yearly_report(self, account_id, user_id, year):
        """
        Generate yearly transaction report
        
        Args:
            account_id: Account ID
            user_id: User ID for verification
            year: Year
            
        Returns:
            dict: Yearly report with monthly breakdown
        """
        # Verify ownership
        account = self.account_model.get_account_by_id(account_id)
        if not account or account['user_id'] != user_id:
            return None
        
        # Get yearly summary
        summary = self.transaction_model.get_yearly_summary(
            account_id=account_id,
            year=year
        )
        
        # Add account context
        summary['account_number'] = account['account_number']
        summary['account_type'] = account['account_type']
        summary['current_balance'] = account['balance']
        
        return summary
    
    def get_compliance_metrics(self, account_id, user_id, days=90):
        """
        Get compliance and regulatory metrics
        
        Args:
            account_id: Account ID
            user_id: User ID for verification
            days: Analysis period
            
        Returns:
            dict: Compliance metrics
        """
        # Verify ownership
        account = self.account_model.get_account_by_id(account_id)
        if not account or account['user_id'] != user_id:
            return None
        
        # Get high-value transactions
        high_value_txns = self.transaction_model.get_high_value_transactions(
            account_id=account_id,
            threshold=self.high_value_threshold,
            days=days
        )
        
        # Get all recent transactions
        all_txns = self.transaction_model.get_recent_transactions(
            account_id=account_id,
            days=days
        )
        
        # Analyze for suspicious patterns
        suspicious_patterns = self._detect_suspicious_patterns(all_txns)
        
        metrics = {
            'period_days': days,
            'high_value_transaction_count': len(high_value_txns),
            'high_value_total_amount': sum(float(t['amount']) for t in high_value_txns),
            'high_value_threshold': self.high_value_threshold,
            'suspicious_activity_detected': suspicious_patterns['detected'],
            'suspicious_patterns': suspicious_patterns['patterns'],
            'risk_level': self._calculate_risk_level(high_value_txns, suspicious_patterns),
            'large_cash_transactions': [
                t for t in high_value_txns 
                if t['transaction_type'] in ['deposit', 'withdrawal']
            ],
            'compliance_status': 'REVIEW_REQUIRED' if suspicious_patterns['detected'] else 'NORMAL'
        }
        
        return metrics
    
    def get_dashboard_data(self, user_id):
        """
        Get complete dashboard data for user
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Dashboard data
        """
        # Get all user accounts
        accounts = self.account_model.get_user_accounts(user_id)
        
        dashboard = {
            'total_balance': 0.0,
            'account_count': len(accounts),
            'accounts': [],
            'recent_activity': [],
            'spending_summary': {
                'last_7_days': 0.0,
                'last_30_days': 0.0
            }
        }
        
        # Process each account
        for account in accounts:
            # Calculate total balance
            dashboard['total_balance'] += account['balance']
            
            # Get recent transactions
            recent_txns = self.transaction_model.get_recent_transactions(
                account_id=account['account_id'],
                days=30
            )
            
            # Add to recent activity
            dashboard['recent_activity'].extend(recent_txns[:5])
            
            # Calculate spending
            last_7_days_txns = self.transaction_model.get_recent_transactions(
                account_id=account['account_id'],
                days=7
            )
            
            spending_7_days = sum(
                float(t['amount']) for t in last_7_days_txns 
                if t['transaction_type'] in ['withdrawal', 'transfer_out']
            )
            
            spending_30_days = sum(
                float(t['amount']) for t in recent_txns 
                if t['transaction_type'] in ['withdrawal', 'transfer_out']
            )
            
            dashboard['spending_summary']['last_7_days'] += spending_7_days
            dashboard['spending_summary']['last_30_days'] += spending_30_days
            
            # Add account summary
            dashboard['accounts'].append({
                'account_id': account['account_id'],
                'account_number': account['account_number'],
                'account_type': account['account_type'],
                'balance': account['balance'],
                'status': account['status'],
                'transaction_count': len(recent_txns)
            })
        
        # Sort recent activity by timestamp
        dashboard['recent_activity'].sort(
            key=lambda x: x['timestamp'], 
            reverse=True
        )
        dashboard['recent_activity'] = dashboard['recent_activity'][:10]
        
        return dashboard
    
    def _analyze_spending_pattern(self, transactions):
        """Analyze spending patterns from transactions"""
        pattern = {
            'weekday_spending': 0.0,
            'weekend_spending': 0.0,
            'morning_transactions': 0,  # 6am-12pm
            'afternoon_transactions': 0,  # 12pm-6pm
            'evening_transactions': 0,  # 6pm-12am
            'night_transactions': 0  # 12am-6am
        }
        
        for txn in transactions:
            if txn['transaction_type'] in ['withdrawal', 'transfer_out']:
                dt = datetime.fromisoformat(txn['timestamp'])
                amount = float(txn['amount'])
                
                # Weekday vs weekend
                if dt.weekday() < 5:  # Monday-Friday
                    pattern['weekday_spending'] += amount
                else:
                    pattern['weekend_spending'] += amount
                
                # Time of day
                hour = dt.hour
                if 6 <= hour < 12:
                    pattern['morning_transactions'] += 1
                elif 12 <= hour < 18:
                    pattern['afternoon_transactions'] += 1
                elif 18 <= hour < 24:
                    pattern['evening_transactions'] += 1
                else:
                    pattern['night_transactions'] += 1
        
        return pattern
    
    def _detect_suspicious_patterns(self, transactions):
        """Detect suspicious activity patterns"""
        patterns = {
            'detected': False,
            'patterns': []
        }
        
        # Check for multiple high-value transactions in 24 hours
        high_value_in_24h = []
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for txn in transactions:
            txn_time = datetime.fromisoformat(txn['timestamp'])
            if txn_time >= cutoff_time and float(txn['amount']) >= self.high_value_threshold:
                high_value_in_24h.append(txn)
        
        if len(high_value_in_24h) >= self.suspicious_threshold:
            patterns['detected'] = True
            patterns['patterns'].append({
                'type': 'multiple_high_value_transactions',
                'count': len(high_value_in_24h),
                'threshold': self.suspicious_threshold,
                'description': f'{len(high_value_in_24h)} high-value transactions in 24 hours'
            })
        
        # Check for rapid succession transactions
        if len(transactions) >= 10:
            recent_10 = transactions[:10]
            time_span = (
                datetime.fromisoformat(recent_10[0]['timestamp']) -
                datetime.fromisoformat(recent_10[-1]['timestamp'])
            )
            
            if time_span.total_seconds() < 3600:  # 10 transactions in 1 hour
                patterns['detected'] = True
                patterns['patterns'].append({
                    'type': 'rapid_transaction_pattern',
                    'count': 10,
                    'time_span_minutes': time_span.total_seconds() / 60,
                    'description': '10 transactions in under 1 hour'
                })
        
        return patterns
    
    def _calculate_risk_level(self, high_value_txns, suspicious_patterns):
        """Calculate risk level based on transaction patterns"""
        risk_score = 0
        
        # High value transaction count
        if len(high_value_txns) > 5:
            risk_score += 2
        elif len(high_value_txns) > 2:
            risk_score += 1
        
        # Suspicious patterns
        if suspicious_patterns['detected']:
            risk_score += len(suspicious_patterns['patterns']) * 2
        
        # Determine risk level
        if risk_score >= 5:
            return 'HIGH'
        elif risk_score >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
