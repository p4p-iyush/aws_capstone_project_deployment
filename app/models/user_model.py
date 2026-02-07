"""
User Model - Data Access Layer
Handles all DynamoDB operations for user data
"""

import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
import bcrypt
import uuid
from decimal import Decimal


class UserModel:
    """User data model with DynamoDB operations"""
    
    def __init__(self, table_name, region_name='us-east-1'):
        """
        Initialize User Model
        
        Args:
            table_name: DynamoDB table name for users
            region_name: AWS region
        """
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table = self.dynamodb.Table(table_name)
        self.table_name = table_name
    
    def create_user(self, email, password, full_name, phone=None):
        """
        Create a new user with hashed password
        
        Args:
            email: User email (unique identifier)
            password: Plain text password (will be hashed)
            full_name: User's full name
            phone: Optional phone number
            
        Returns:
            dict: Created user data (without password hash)
            
        Raises:
            ValueError: If user already exists or validation fails
        """
        # Validate email uniqueness
        if self.get_user_by_email(email):
            raise ValueError("User with this email already exists")
        
        # Generate unique user ID
        user_id = str(uuid.uuid4())
        
        # Hash password using bcrypt
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')
        
        # Prepare user item
        user_item = {
            'user_id': user_id,
            'email': email.lower(),
            'password_hash': password_hash,
            'full_name': full_name,
            'phone': phone or '',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'is_active': True,
            'failed_login_attempts': 0,
            'last_login': None,
            'account_locked_until': None
        }
        
        # Store in DynamoDB
        self.table.put_item(Item=user_item)
        
        # Return user data without password hash
        return self._sanitize_user(user_item)
    
    def get_user_by_email(self, email):
        """
        Retrieve user by email address
        
        Args:
            email: User email
            
        Returns:
            dict: User data or None if not found
        """
        try:
            response = self.table.query(
                IndexName='EmailIndex',  # GSI on email
                KeyConditionExpression=Key('email').eq(email.lower())
            )
            
            if response['Items']:
                return response['Items'][0]
            return None
        except Exception as e:
            print(f"Error querying user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """
        Retrieve user by user_id
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            dict: User data or None if not found
        """
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            return response.get('Item')
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    def verify_password(self, email, password):
        """
        Verify user password and handle login attempts
        
        Args:
            email: User email
            password: Plain text password to verify
            
        Returns:
            dict: User data if authentication successful, None otherwise
        """
        user = self.get_user_by_email(email)
        
        if not user:
            return None
        
        # Check if account is locked
        if user.get('account_locked_until'):
            locked_until = datetime.fromisoformat(user['account_locked_until'])
            if datetime.utcnow() < locked_until:
                raise ValueError("Account is temporarily locked. Please try again later.")
            else:
                # Unlock account
                self._unlock_account(user['user_id'])
        
        # Verify password
        password_match = bcrypt.checkpw(
            password.encode('utf-8'),
            user['password_hash'].encode('utf-8')
        )
        
        if password_match:
            # Reset failed attempts and update last login
            self._successful_login(user['user_id'])
            return self._sanitize_user(user)
        else:
            # Increment failed login attempts
            self._failed_login_attempt(user['user_id'], user.get('failed_login_attempts', 0))
            return None
    
    def update_user(self, user_id, **kwargs):
        """
        Update user attributes
        
        Args:
            user_id: User ID
            **kwargs: Attributes to update (full_name, phone, etc.)
            
        Returns:
            dict: Updated user data
        """
        # Build update expression
        update_expr = "SET updated_at = :updated_at"
        expr_values = {':updated_at': datetime.utcnow().isoformat()}
        
        allowed_fields = ['full_name', 'phone']
        for field in allowed_fields:
            if field in kwargs:
                update_expr += f", {field} = :{field}"
                expr_values[f':{field}'] = kwargs[field]
        
        try:
            response = self.table.update_item(
                Key={'user_id': user_id},
                UpdateExpression=update_expr,
                ExpressionAttributeValues=expr_values,
                ReturnValues='ALL_NEW'
            )
            return self._sanitize_user(response['Attributes'])
        except Exception as e:
            print(f"Error updating user: {e}")
            raise
    
    def change_password(self, user_id, old_password, new_password):
        """
        Change user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            bool: True if successful
        """
        user = self.get_user_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        # Verify old password
        if not bcrypt.checkpw(old_password.encode('utf-8'), 
                             user['password_hash'].encode('utf-8')):
            raise ValueError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')
        
        # Update password
        self.table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET password_hash = :ph, updated_at = :ua',
            ExpressionAttributeValues={
                ':ph': new_password_hash,
                ':ua': datetime.utcnow().isoformat()
            }
        )
        
        return True
    
    def _successful_login(self, user_id):
        """Update user after successful login"""
        self.table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET failed_login_attempts = :zero, last_login = :now, account_locked_until = :null',
            ExpressionAttributeValues={
                ':zero': 0,
                ':now': datetime.utcnow().isoformat(),
                ':null': None
            }
        )
    
    def _failed_login_attempt(self, user_id, current_attempts):
        """Handle failed login attempt"""
        new_attempts = current_attempts + 1
        
        update_expr = 'SET failed_login_attempts = :attempts'
        expr_values = {':attempts': new_attempts}
        
        # Lock account after 5 failed attempts
        if new_attempts >= 5:
            from datetime import timedelta
            lock_until = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
            update_expr += ', account_locked_until = :lock_until'
            expr_values[':lock_until'] = lock_until
        
        self.table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values
        )
    
    def _unlock_account(self, user_id):
        """Unlock user account"""
        self.table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET account_locked_until = :null, failed_login_attempts = :zero',
            ExpressionAttributeValues={
                ':null': None,
                ':zero': 0
            }
        )
    
    def _sanitize_user(self, user):
        """Remove sensitive data from user object"""
        if user:
            user_copy = user.copy()
            user_copy.pop('password_hash', None)
            return user_copy
        return None
