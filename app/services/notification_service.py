"""
Notification Service - Business Logic Layer
Handles AWS SNS email notifications for transactions and alerts
"""

import boto3
from botocore.exceptions import ClientError
import json
from datetime import datetime


class NotificationService:
    """SNS notification service for transaction alerts"""
    
    def __init__(self, config):
        """
        Initialize Notification Service
        
        Args:
            config: Flask app configuration object
        """
        self.config = config
        self.sns_enabled = config['ENABLE_SNS_NOTIFICATIONS']
        self.topic_arn = config.get('SNS_TOPIC_ARN', '')
        self.high_value_threshold = config['HIGH_VALUE_TRANSACTION_THRESHOLD']
        
        if self.sns_enabled and self.topic_arn:
            try:
                self.sns_client = boto3.client('sns', region_name=config['AWS_REGION'])
            except Exception as e:
                print(f"Warning: Could not initialize SNS client: {e}")
                self.sns_enabled = False
        else:
            self.sns_enabled = False
    
    def send_transaction_alert(self, user_email, transaction_type, amount, account_number, new_balance):
        """
        Send transaction notification email
        
        Args:
            user_email: User's email address
            transaction_type: Type of transaction
            amount: Transaction amount
            account_number: Account number
            new_balance: New account balance
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if not self.sns_enabled:
            return {
                'success': False,
                'message': 'SNS notifications are disabled'
            }
        
        try:
            # Format transaction type
            type_display = transaction_type.replace('_', ' ').title()
            
            # Build message
            subject = f'Banking Alert: {type_display} Transaction'
            message = self._build_transaction_message(
                user_email, type_display, amount, account_number, new_balance
            )
            
            # Send via SNS
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            
            return {
                'success': True,
                'message': 'Notification sent successfully',
                'message_id': response.get('MessageId')
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            return {
                'success': False,
                'message': f'SNS Error ({error_code}): {error_msg}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Notification failed: {str(e)}'
            }
    
    def send_high_value_alert(self, user_email, transaction_type, amount, account_number):
        """
        Send alert for high-value transactions
        
        Args:
            user_email: User's email
            transaction_type: Transaction type
            amount: Transaction amount
            account_number: Account number
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if not self.sns_enabled:
            return {'success': False, 'message': 'SNS disabled'}
        
        try:
            subject = '🚨 High-Value Transaction Alert'
            message = f"""
SECURITY ALERT: High-Value Transaction Detected
================================================

Dear Customer,

A high-value transaction has been processed on your account.

Transaction Details:
-------------------
Type: {transaction_type.replace('_', ' ').title()}
Amount: ${amount:,.2f}
Account: ****{account_number[-4:]}
Date/Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

If you did not authorize this transaction, please contact our security team immediately.

Security Hotline: 1-800-BANK-SEC
Email: security@bankingapp.com

Thank you,
Banking Security Team
            """
            
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            
            return {
                'success': True,
                'message': 'High-value alert sent',
                'message_id': response.get('MessageId')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Alert failed: {str(e)}'
            }
    
    def send_transfer_confirmation(self, sender_email, recipient_account, amount, new_balance):
        """
        Send transfer confirmation to sender
        
        Args:
            sender_email: Sender's email
            recipient_account: Recipient account number
            amount: Transfer amount
            new_balance: Sender's new balance
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if not self.sns_enabled:
            return {'success': False, 'message': 'SNS disabled'}
        
        try:
            subject = 'Transfer Confirmation'
            message = f"""
Transfer Successful
===================

Your transfer has been completed successfully.

Transfer Details:
----------------
Amount: ${amount:,.2f}
To Account: ****{recipient_account[-4:]}
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
Your New Balance: ${new_balance:,.2f}

Reference Number: TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}

Thank you for banking with us!
            """
            
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            
            return {
                'success': True,
                'message': 'Transfer confirmation sent'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Confirmation failed: {str(e)}'
            }
    
    def send_suspicious_activity_alert(self, user_email, details):
        """
        Send suspicious activity alert to compliance team
        
        Args:
            user_email: User email
            details: Dictionary of suspicious activity details
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if not self.sns_enabled:
            return {'success': False, 'message': 'SNS disabled'}
        
        try:
            subject = '⚠️ Suspicious Activity Detected - Compliance Review Required'
            message = f"""
COMPLIANCE ALERT: Suspicious Activity Pattern
==============================================

User Account: {user_email}
Detection Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Activity Details:
----------------
{json.dumps(details, indent=2)}

Action Required:
- Review account activity
- Verify transactions with customer
- Assess risk level
- Document findings

This alert has been logged for regulatory compliance.

Compliance Team
            """
            
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            
            return {
                'success': True,
                'message': 'Compliance alert sent'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Alert failed: {str(e)}'
            }
    
    def check_and_alert_if_needed(self, user_email, transaction_type, amount, account_number, new_balance):
        """
        Check if notification is needed and send appropriate alerts
        
        Args:
            user_email: User email
            transaction_type: Transaction type
            amount: Transaction amount
            account_number: Account number
            new_balance: New balance
            
        Returns:
            dict: Alert status
        """
        alerts_sent = []
        
        # Always send transaction notification
        alert_result = self.send_transaction_alert(
            user_email, transaction_type, amount, account_number, new_balance
        )
        if alert_result['success']:
            alerts_sent.append('transaction_notification')
        
        # Send high-value alert if threshold exceeded
        if amount >= self.high_value_threshold:
            high_value_result = self.send_high_value_alert(
                user_email, transaction_type, amount, account_number
            )
            if high_value_result['success']:
                alerts_sent.append('high_value_alert')
        
        return {
            'alerts_sent': alerts_sent,
            'count': len(alerts_sent)
        }
    
    def _build_transaction_message(self, email, transaction_type, amount, account_number, new_balance):
        """Build formatted transaction notification message"""
        return f"""
Transaction Notification
========================

Dear Customer,

A transaction has been processed on your account.

Transaction Details:
-------------------
Type: {transaction_type}
Amount: ${amount:,.2f}
Account: ****{account_number[-4:]}
New Balance: ${new_balance:,.2f}
Date/Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

If you did not authorize this transaction, please contact us immediately.

Thank you for banking with us!

Customer Service: 1-800-BANKING
Email: support@bankingapp.com
        """
