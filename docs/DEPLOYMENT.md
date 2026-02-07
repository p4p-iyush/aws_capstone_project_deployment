# Complete AWS Deployment Guide
# Banking Data Analytics System

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Python 3.8+** installed locally
4. **Git** installed
5. **SSH key pair** for EC2 access

## Step-by-Step Deployment

### PHASE 1: AWS Account Setup

#### 1.1 Configure AWS CLI

```bash
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key  
# - Default region: us-east-1
# - Default output format: json
```

Verify configuration:
```bash
aws sts get-caller-identity
```

---

### PHASE 2: DynamoDB Setup

#### 2.1 Create DynamoDB Tables

Navigate to the aws directory:
```bash
cd aws/
python3 dynamodb_setup.py
```

**Expected Output:**
```
✓ Created table: BankingUsers
✓ Created table: BankingAccounts
✓ Created table: BankingTransactions
```

#### 2.2 Verify Tables

```bash
aws dynamodb list-tables
aws dynamodb describe-table --table-name BankingUsers
aws dynamodb describe-table --table-name BankingAccounts
aws dynamodb describe-table --table-name BankingTransactions
```

Check for `TableStatus: "ACTIVE"` in all tables.

---

### PHASE 3: SNS Setup

#### 3.1 Create SNS Topic

```bash
python3 sns_setup.py
```

Follow the prompts to subscribe your email.

**Manual method:**
```bash
# Create topic
aws sns create-topic --name BankingTransactionAlerts

# Subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:BankingTransactionAlerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

#### 3.2 Confirm Email Subscription

1. Check your email inbox
2. Click the confirmation link from AWS
3. Verify subscription:

```bash
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:BankingTransactionAlerts
```

**Save the Topic ARN** - you'll need it later!

---

### PHASE 4: IAM Role & Policy Setup

#### 4.1 Create IAM Role

```bash
# Create the role
aws iam create-role \
  --role-name BankingAppEC2Role \
  --assume-role-policy-document file://ec2-trust-policy.json

# Attach inline policy
aws iam put-role-policy \
  --role-name BankingAppEC2Role \
  --policy-name BankingAppPolicy \
  --policy-document file://iam_policy.json

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name BankingAppProfile

# Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name BankingAppProfile \
  --role-name BankingAppEC2Role
```

#### 4.2 Verify IAM Setup

```bash
aws iam get-role --role-name BankingAppEC2Role
aws iam get-instance-profile --instance-profile-name BankingAppProfile
```

---

### PHASE 5: EC2 Security Group Setup

#### 5.1 Create Security Group

```bash
# Create security group
aws ec2 create-security-group \
  --group-name banking-app-sg \
  --description "Security group for Banking Application" \
  --vpc-id vpc-YOUR_VPC_ID

# Note the GroupId from output
```

#### 5.2 Add Inbound Rules

```bash
# SSH access (port 22) - RESTRICT TO YOUR IP!
aws ec2 authorize-security-group-ingress \
  --group-id sg-YOUR_SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr YOUR_IP_ADDRESS/32

# HTTP access (port 5000) - For testing
aws ec2 authorize-security-group-ingress \
  --group-id sg-YOUR_SG_ID \
  --protocol tcp \
  --port 5000 \
  --cidr 0.0.0.0/0

# HTTPS (port 443) - For production
aws ec2 authorize-security-group-ingress \
  --group-id sg-YOUR_SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

---

### PHASE 6: EC2 Instance Launch

#### 6.1 Launch EC2 Instance

```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name YOUR_KEY_PAIR_NAME \
  --security-group-ids sg-YOUR_SG_ID \
  --iam-instance-profile Name=BankingAppProfile \
  --user-data file://ec2_user_data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=BankingApp}]'
```

**Find Ubuntu AMI ID for your region:**
```bash
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text
```

#### 6.2 Get Instance Details

```bash
# Get instance ID
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=BankingApp" \
  --query 'Reservations[0].Instances[0].InstanceId' \
  --output text

# Get public IP
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=BankingApp" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

**Wait for instance to be running:**
```bash
aws ec2 wait instance-running --instance-ids i-YOUR_INSTANCE_ID
```

---

### PHASE 7: Deploy Application Code

#### 7.1 Connect to EC2

```bash
# Get public IP
EC2_IP=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=BankingApp" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

# SSH into instance
ssh -i ~/.ssh/YOUR_KEY.pem ec2-user@$EC2_IP
```

#### 7.2 Upload Application Code

**From your local machine:**

```bash
# Compress the application
cd /path/to/banking-system
tar -czf banking-app.tar.gz app/ aws/ requirements.txt run.py

# Upload to EC2
scp -i ~/.ssh/YOUR_KEY.pem banking-app.tar.gz ec2-user@$EC2_IP:/home/ec2-user/

# SSH back in
ssh -i ~/.ssh/YOUR_KEY.pem ec2-user@$EC2_IP

# Extract files
cd /home/ec2-user
tar -xzf banking-app.tar.gz
```

#### 7.3 Install Dependencies

```bash
# On EC2 instance
cd /home/ec2-user/banking-system
pip3 install -r requirements.txt --user
```

#### 7.4 Configure Environment Variables

```bash
# Create .env file
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(openssl rand -hex 32)
AWS_REGION=us-east-1
DYNAMODB_USERS_TABLE=BankingUsers
DYNAMODB_ACCOUNTS_TABLE=BankingAccounts
DYNAMODB_TRANSACTIONS_TABLE=BankingTransactions
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:BankingTransactionAlerts
ENABLE_SNS_NOTIFICATIONS=true
HIGH_VALUE_THRESHOLD=10000.00
EOF
```

**Important:** Replace `ACCOUNT_ID` with your actual AWS account ID!

---

### PHASE 8: Start Application

#### 8.1 Test Run (Development Mode)

```bash
# On EC2 instance
cd /home/ec2-user/banking-system
python3 run.py
```

Access in browser: `http://EC2_PUBLIC_IP:5000`

Press `Ctrl+C` to stop.

#### 8.2 Production Deployment with Gunicorn

```bash
# Install Gunicorn
pip3 install gunicorn --user

# Run with Gunicorn
~/.local/bin/gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

Access: `http://EC2_PUBLIC_IP:5000`

#### 8.3 Setup as System Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/banking-app.service
```

Paste this content:
```ini
[Unit]
Description=Banking Data Analytics Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/banking-system
Environment="PATH=/home/ec2-user/.local/bin:/usr/local/bin:/usr/bin"
EnvironmentFile=/home/ec2-user/banking-system/.env
ExecStart=/home/ec2-user/.local/bin/gunicorn -w 4 -b 0.0.0.0:5000 run:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable banking-app
sudo systemctl start banking-app
sudo systemctl status banking-app
```

View logs:
```bash
sudo journalctl -u banking-app -f
```

---

### PHASE 9: Testing & Verification

#### 9.1 Test Application

1. **Open browser:** `http://EC2_PUBLIC_IP:5000`
2. **Register a new user**
3. **Login**
4. **Create an account**
5. **Make a deposit**
6. **Check email for SNS notification**
7. **View dashboard and analytics**

#### 9.2 Test DynamoDB

```bash
# Check if data is being stored
aws dynamodb scan --table-name BankingUsers --max-items 1
aws dynamodb scan --table-name BankingAccounts --max-items 1
aws dynamodb scan --table-name BankingTransactions --max-items 1
```

#### 9.3 Test SNS

From the application:
- Make a transaction over $10,000
- Check email for high-value alert

---

### PHASE 10: Monitoring & Logs

#### 10.1 Application Logs

```bash
# Real-time logs
sudo journalctl -u banking-app -f

# Last 100 lines
sudo journalctl -u banking-app -n 100

# Filter by priority
sudo journalctl -u banking-app -p err
```

#### 10.2 CloudWatch Logs (Optional)

Setup CloudWatch agent for advanced monitoring.

---

## Troubleshooting

### Application won't start

```bash
# Check service status
sudo systemctl status banking-app

# Check logs
sudo journalctl -u banking-app -n 50

# Test manually
cd /home/ec2-user/banking-system
python3 run.py
```

### Can't connect to DynamoDB

```bash
# Verify IAM role
aws sts get-caller-identity

# Test DynamoDB access
python3 -c "import boto3; print(boto3.resource('dynamodb').tables.all())"
```

### SNS notifications not working

```bash
# Verify subscription
aws sns list-subscriptions

# Check topic permissions
aws sns get-topic-attributes --topic-arn YOUR_TOPIC_ARN
```

---

## Security Hardening (Production)

1. **Use HTTPS** with SSL/TLS certificate
2. **Setup Application Load Balancer**
3. **Enable DynamoDB encryption at rest**
4. **Use AWS Secrets Manager** for sensitive data
5. **Implement rate limiting**
6. **Setup AWS WAF** for DDoS protection
7. **Enable CloudTrail** for audit logging
8. **Use VPC** with private subnets
9. **Implement MFA** for admin access
10. **Regular security audits**

---

## Maintenance

### Update Application

```bash
# SSH to EC2
ssh -i ~/.ssh/YOUR_KEY.pem ec2-user@$EC2_IP

# Backup current version
cd /home/ec2-user
cp -r banking-system banking-system.backup

# Upload new version
# ... use scp or git pull ...

# Restart service
sudo systemctl restart banking-app
```

### Monitor Costs

```bash
# Check billing
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

---

## Architecture Diagram

```
                    Internet
                        |
                        v
                [EC2 Instance]
                (Flask App + Gunicorn)
                        |
            +-----------+-----------+
            |                       |
            v                       v
        [DynamoDB]              [SNS Topic]
        (3 Tables)              (Email Alerts)
```

---

## Success Checklist

- [ ] DynamoDB tables created
- [ ] SNS topic configured and email confirmed
- [ ] IAM role and policy created
- [ ] Security group configured
- [ ] EC2 instance launched
- [ ] Application deployed
- [ ] Service running
- [ ] Can register and login
- [ ] Transactions working
- [ ] SNS notifications received
- [ ] Analytics dashboard functional

---

## Support

For issues, check:
1. Application logs: `sudo journalctl -u banking-app`
2. AWS CloudWatch
3. DynamoDB table metrics
4. SNS delivery logs

---

**Deployment Complete!** 🎉
