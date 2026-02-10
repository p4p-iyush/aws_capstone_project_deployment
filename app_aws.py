"""
AWS Configuration and Setup
All AWS-related configurations for DynamoDB and SNS
"""

import boto3
from botocore.exceptions import ClientError
import os
from decimal import Decimal

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# DynamoDB Table Names
USERS_TABLE = os.environ.get('DYNAMODB_USERS_TABLE', 'BankingUsers')
ACCOUNTS_TABLE = os.environ.get('DYNAMODB_ACCOUNTS_TABLE', 'BankingAccounts')
TRANSACTIONS_TABLE = os.environ.get('DYNAMODB_TRANSACTIONS_TABLE', 'BankingTransactions')

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION)
sns_client = boto3.client('sns', region_name=AWS_REGION)


def create_users_table():
    """Create Users table with EmailIndex"""
    try:
        table = dynamodb.create_table(
            TableName=USERS_TABLE,
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'EmailIndex',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=USERS_TABLE)
        print(f"✓ Created table: {USERS_TABLE}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {USERS_TABLE} already exists")
            return True
        else:
            print(f"✗ Error creating {USERS_TABLE}: {e}")
            return False


def create_accounts_table():
    """Create Accounts table with UserIdIndex and AccountNumberIndex"""
    try:
        table = dynamodb.create_table(
            TableName=ACCOUNTS_TABLE,
            KeySchema=[
                {'AttributeName': 'account_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'account_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'account_number', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'UserIdIndex',
                    'KeySchema': [
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                },
                {
                    'IndexName': 'AccountNumberIndex',
                    'KeySchema': [
                        {'AttributeName': 'account_number', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=ACCOUNTS_TABLE)
        print(f"✓ Created table: {ACCOUNTS_TABLE}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {ACCOUNTS_TABLE} already exists")
            return True
        else:
            print(f"✗ Error creating {ACCOUNTS_TABLE}: {e}")
            return False


def create_transactions_table():
    """Create Transactions table with AccountIdTimestampIndex"""
    try:
        table = dynamodb.create_table(
            TableName=TRANSACTIONS_TABLE,
            KeySchema=[
                {'AttributeName': 'transaction_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'transaction_id', 'AttributeType': 'S'},
                {'AttributeName': 'account_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'AccountIdTimestampIndex',
                    'KeySchema': [
                        {'AttributeName': 'account_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.meta.client.get_waiter('table_exists').wait(TableName=TRANSACTIONS_TABLE)
        print(f"✓ Created table: {TRANSACTIONS_TABLE}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {TRANSACTIONS_TABLE} already exists")
            return True
        else:
            print(f"✗ Error creating {TRANSACTIONS_TABLE}: {e}")
            return False


def setup_aws_resources():
    """Setup all AWS resources (DynamoDB tables)"""
    print("=" * 60)
    print("Setting up AWS Resources")
    print("=" * 60)
    
    results = []
    results.append(create_users_table())
    results.append(create_accounts_table())
    results.append(create_transactions_table())
    
    if all(results):
        print("\n✓ All AWS resources created successfully!")
        return True
    else:
        print("\n✗ Some resources failed to create")
        return False


def get_dynamodb_table(table_name):
    """Get DynamoDB table resource"""
    return dynamodb.Table(table_name)


if __name__ == '__main__':
    setup_aws_resources()
