"""
DynamoDB Table Setup Script
Creates all required tables with proper schema and GSIs
"""

import boto3
import sys
from botocore.exceptions import ClientError


def create_users_table(dynamodb, table_name='BankingUsers'):
    """Create Users table with email GSI"""
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'user_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'EmailIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'email',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
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
        
        # Wait for table to be created
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"✓ Created table: {table_name}")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {table_name} already exists")
            return True
        else:
            print(f"✗ Error creating {table_name}: {e}")
            return False


def create_accounts_table(dynamodb, table_name='BankingAccounts'):
    """Create Accounts table with user_id and account_number GSIs"""
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'account_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'account_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'user_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'account_number',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'UserIdIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                },
                {
                    'IndexName': 'AccountNumberIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'account_number',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
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
        
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"✓ Created table: {table_name}")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {table_name} already exists")
            return True
        else:
            print(f"✗ Error creating {table_name}: {e}")
            return False


def create_transactions_table(dynamodb, table_name='BankingTransactions'):
    """Create Transactions table with account_id + timestamp GSI"""
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'transaction_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'transaction_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'account_id',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'timestamp',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'AccountIdTimestampIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'account_id',
                            'KeyType': 'HASH'  # Partition key
                        },
                        {
                            'AttributeName': 'timestamp',
                            'KeyType': 'RANGE'  # Sort key
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
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
        
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"✓ Created table: {table_name}")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠ Table {table_name} already exists")
            return True
        else:
            print(f"✗ Error creating {table_name}: {e}")
            return False


def main():
    """Main function to create all tables"""
    print("=" * 60)
    print("DynamoDB Table Creation Script")
    print("Banking Data Analytics System")
    print("=" * 60)
    
    # Get region from environment or use default
    import os
    region = os.environ.get('AWS_REGION', 'us-east-1')
    
    print(f"\nRegion: {region}")
    print("\nCreating DynamoDB tables...\n")
    
    try:
        # Create DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name=region)
        
        # Create all tables
        results = []
        results.append(create_users_table(dynamodb))
        results.append(create_accounts_table(dynamodb))
        results.append(create_transactions_table(dynamodb))
        
        # Summary
        print("\n" + "=" * 60)
        if all(results):
            print("✓ All tables created successfully!")
            print("\nTable Names:")
            print("  - BankingUsers")
            print("  - BankingAccounts")
            print("  - BankingTransactions")
            print("\nNext steps:")
            print("  1. Update your .env file with table names")
            print("  2. Setup SNS topic: python aws/sns_setup.py")
            print("  3. Create IAM role with aws/iam_policy.json")
        else:
            print("⚠ Some tables could not be created. Check errors above.")
            sys.exit(1)
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
