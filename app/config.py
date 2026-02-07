"""
Configuration settings for Banking Data Analytics System
Handles environment-specific settings and AWS configurations
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session Configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = True  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # AWS Configuration
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    
    # DynamoDB Table Names
    DYNAMODB_USERS_TABLE = os.environ.get('DYNAMODB_USERS_TABLE', 'BankingUsers')
    DYNAMODB_ACCOUNTS_TABLE = os.environ.get('DYNAMODB_ACCOUNTS_TABLE', 'BankingAccounts')
    DYNAMODB_TRANSACTIONS_TABLE = os.environ.get('DYNAMODB_TRANSACTIONS_TABLE', 'BankingTransactions')
    
    # SNS Configuration
    SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')
    ENABLE_SNS_NOTIFICATIONS = os.environ.get('ENABLE_SNS_NOTIFICATIONS', 'true').lower() == 'true'
    
    # Transaction Thresholds for Alerts
    HIGH_VALUE_TRANSACTION_THRESHOLD = float(os.environ.get('HIGH_VALUE_THRESHOLD', '10000.00'))
    
    # Security Settings
    BCRYPT_LOG_ROUNDS = 12  # Cost factor for password hashing
    MAX_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCKOUT_DURATION = timedelta(minutes=30)
    
    # Pagination
    TRANSACTIONS_PER_PAGE = 20
    
    # Business Rules
    MIN_BALANCE = 0.00
    MAX_TRANSACTION_AMOUNT = 1000000.00
    MIN_TRANSFER_AMOUNT = 0.01
    
    # Compliance & Regulatory
    COMPLIANCE_REPORTING_EMAIL = os.environ.get('COMPLIANCE_EMAIL', 'compliance@example.com')
    SUSPICIOUS_ACTIVITY_THRESHOLD = 5  # Number of large transactions in 24h
    
    # Analytics
    ANALYTICS_CACHE_DURATION = timedelta(minutes=15)


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS
    
    # Stricter security settings
    BCRYPT_LOG_ROUNDS = 14


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    # Use different table names for testing
    DYNAMODB_USERS_TABLE = 'TestBankingUsers'
    DYNAMODB_ACCOUNTS_TABLE = 'TestBankingAccounts'
    DYNAMODB_TRANSACTIONS_TABLE = 'TestBankingTransactions'
    
    # Disable SNS in tests
    ENABLE_SNS_NOTIFICATIONS = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name=None):
    """
    Get configuration based on environment name
    
    Args:
        env_name: Environment name (development, production, testing)
        
    Returns:
        Config class for the specified environment
    """
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env_name, config['default'])
