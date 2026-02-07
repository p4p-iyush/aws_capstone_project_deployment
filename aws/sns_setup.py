"""
SNS Topic Setup Script
Creates SNS topic for transaction notifications
"""

import boto3
import sys
import os
from botocore.exceptions import ClientError


def create_sns_topic(topic_name='BankingTransactionAlerts', region='us-east-1'):
    """
    Create SNS topic for banking notifications
    
    Args:
        topic_name: Name of SNS topic
        region: AWS region
        
    Returns:
        str: Topic ARN
    """
    try:
        sns_client = boto3.client('sns', region_name=region)
        
        # Create topic
        response = sns_client.create_topic(Name=topic_name)
        topic_arn = response['TopicArn']
        
        print(f"✓ Created SNS topic: {topic_name}")
        print(f"  Topic ARN: {topic_arn}")
        
        return topic_arn
        
    except ClientError as e:
        print(f"✗ Error creating SNS topic: {e}")
        return None


def subscribe_email(topic_arn, email_address, region='us-east-1'):
    """
    Subscribe an email address to the SNS topic
    
    Args:
        topic_arn: SNS topic ARN
        email_address: Email to subscribe
        region: AWS region
        
    Returns:
        bool: Success status
    """
    try:
        sns_client = boto3.client('sns', region_name=region)
        
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email_address
        )
        
        print(f"✓ Subscribed email: {email_address}")
        print(f"  Subscription ARN: {response['SubscriptionArn']}")
        print(f"  ⚠ Check {email_address} and confirm the subscription!")
        
        return True
        
    except ClientError as e:
        print(f"✗ Error subscribing email: {e}")
        return False


def main():
    """Main function"""
    print("=" * 60)
    print("SNS Topic Setup Script")
    print("Banking Data Analytics System")
    print("=" * 60)
    
    # Get configuration
    region = os.environ.get('AWS_REGION', 'us-east-1')
    topic_name = os.environ.get('SNS_TOPIC_NAME', 'BankingTransactionAlerts')
    
    print(f"\nRegion: {region}")
    print(f"Topic Name: {topic_name}\n")
    
    # Create topic
    topic_arn = create_sns_topic(topic_name, region)
    
    if not topic_arn:
        print("\n✗ Failed to create SNS topic")
        sys.exit(1)
    
    # Ask for email subscription
    print("\n" + "-" * 60)
    subscribe = input("Do you want to subscribe an email now? (y/n): ").lower()
    
    if subscribe == 'y':
        email = input("Enter email address: ").strip()
        if email:
            subscribe_email(topic_arn, email, region)
        else:
            print("⚠ No email provided, skipping subscription")
    
    # Print next steps
    print("\n" + "=" * 60)
    print("✓ SNS Setup Complete!")
    print("\nImportant:")
    print(f"  1. Add to .env: SNS_TOPIC_ARN={topic_arn}")
    print("  2. Confirm email subscription (check inbox)")
    print("  3. Add SNS permissions to IAM role")
    print("\nTo subscribe more emails later, run:")
    print(f"  aws sns subscribe --topic-arn {topic_arn} \\")
    print(f"    --protocol email --notification-endpoint your@email.com")
    print("=" * 60)


if __name__ == '__main__':
    main()
