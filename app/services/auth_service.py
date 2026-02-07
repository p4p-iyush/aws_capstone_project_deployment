"""
Authentication Service - Business Logic Layer
Handles user authentication, registration, and session management
"""

from flask import session
from app.models.user_model import UserModel
from app.models.account_model import AccountModel
import re


class AuthService:
    """Authentication and user management service"""
    
    def __init__(self, config):
        """
        Initialize Auth Service
        
        Args:
            config: Flask app configuration object
        """
        self.config = config
        self.user_model = UserModel(
            table_name=config['DYNAMODB_USERS_TABLE'],
            region_name=config['AWS_REGION']
        )
        self.account_model = AccountModel(
            table_name=config['DYNAMODB_ACCOUNTS_TABLE'],
            region_name=config['AWS_REGION']
        )
    
    def register_user(self, email, password, confirm_password, full_name, phone=''):
        """
        Register a new user with validation
        
        Args:
            email: User email
            password: Password
            confirm_password: Password confirmation
            full_name: User's full name
            phone: Optional phone number
            
        Returns:
            dict: {'success': bool, 'message': str, 'user': dict}
        """
        # Validate inputs
        validation_result = self._validate_registration(
            email, password, confirm_password, full_name
        )
        
        if not validation_result['valid']:
            return {
                'success': False,
                'message': validation_result['message'],
                'user': None
            }
        
        try:
            # Create user
            user = self.user_model.create_user(
                email=email,
                password=password,
                full_name=full_name,
                phone=phone
            )
            
            # Automatically create a default checking account
            account = self.account_model.create_account(
                user_id=user['user_id'],
                account_type='checking',
                initial_balance=0.00
            )
            
            return {
                'success': True,
                'message': 'Registration successful! Please login.',
                'user': user,
                'account': account
            }
            
        except ValueError as e:
            return {
                'success': False,
                'message': str(e),
                'user': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Registration failed: {str(e)}',
                'user': None
            }
    
    def login_user(self, email, password):
        """
        Authenticate user and create session
        
        Args:
            email: User email
            password: Password
            
        Returns:
            dict: {'success': bool, 'message': str, 'user': dict}
        """
        try:
            # Verify credentials
            user = self.user_model.verify_password(email, password)
            
            if user:
                # Create session
                self._create_session(user)
                
                return {
                    'success': True,
                    'message': 'Login successful!',
                    'user': user
                }
            else:
                return {
                    'success': False,
                    'message': 'Invalid email or password',
                    'user': None
                }
                
        except ValueError as e:
            # Account locked or other validation error
            return {
                'success': False,
                'message': str(e),
                'user': None
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Login failed: {str(e)}',
                'user': None
            }
    
    def logout_user(self):
        """
        Logout user by clearing session
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        session.clear()
        return {
            'success': True,
            'message': 'Logged out successfully'
        }
    
    def get_current_user(self):
        """
        Get currently logged-in user from session
        
        Returns:
            dict: User data or None
        """
        user_id = session.get('user_id')
        if user_id:
            return self.user_model.get_user_by_id(user_id)
        return None
    
    def is_authenticated(self):
        """
        Check if user is authenticated
        
        Returns:
            bool: True if authenticated
        """
        return 'user_id' in session
    
    def change_password(self, user_id, old_password, new_password, confirm_password):
        """
        Change user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            confirm_password: New password confirmation
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        # Validate new password
        if new_password != confirm_password:
            return {
                'success': False,
                'message': 'New passwords do not match'
            }
        
        if len(new_password) < 8:
            return {
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }
        
        try:
            self.user_model.change_password(user_id, old_password, new_password)
            return {
                'success': True,
                'message': 'Password changed successfully'
            }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Password change failed: {str(e)}'
            }
    
    def update_profile(self, user_id, full_name=None, phone=None):
        """
        Update user profile information
        
        Args:
            user_id: User ID
            full_name: New full name (optional)
            phone: New phone number (optional)
            
        Returns:
            dict: {'success': bool, 'message': str, 'user': dict}
        """
        try:
            updates = {}
            if full_name:
                updates['full_name'] = full_name
            if phone:
                updates['phone'] = phone
            
            if not updates:
                return {
                    'success': False,
                    'message': 'No updates provided',
                    'user': None
                }
            
            user = self.user_model.update_user(user_id, **updates)
            
            return {
                'success': True,
                'message': 'Profile updated successfully',
                'user': user
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Profile update failed: {str(e)}',
                'user': None
            }
    
    def _create_session(self, user):
        """
        Create user session
        
        Args:
            user: User dictionary
        """
        session['user_id'] = user['user_id']
        session['email'] = user['email']
        session['full_name'] = user['full_name']
    
    def _validate_registration(self, email, password, confirm_password, full_name):
        """
        Validate registration inputs
        
        Returns:
            dict: {'valid': bool, 'message': str}
        """
        # Email validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return {'valid': False, 'message': 'Invalid email format'}
        
        # Password validation
        if len(password) < 8:
            return {'valid': False, 'message': 'Password must be at least 8 characters long'}
        
        if password != confirm_password:
            return {'valid': False, 'message': 'Passwords do not match'}
        
        # Password strength check
        if not any(char.isdigit() for char in password):
            return {'valid': False, 'message': 'Password must contain at least one number'}
        
        if not any(char.isupper() for char in password):
            return {'valid': False, 'message': 'Password must contain at least one uppercase letter'}
        
        # Full name validation
        if len(full_name.strip()) < 2:
            return {'valid': False, 'message': 'Please provide a valid full name'}
        
        return {'valid': True, 'message': 'Validation successful'}
