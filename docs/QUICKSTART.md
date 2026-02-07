# Quick Start Guide
# Banking Data Analytics System

Get up and running in 30 minutes!

---

## Option 1: Local Development Setup (Fastest)

### Prerequisites
- Python 3.8+ installed
- AWS account created
- AWS CLI configured

### Steps

#### 1. Clone/Download Project
```bash
cd ~/projects
# Extract the banking-system folder
cd banking-system
```

#### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Setup AWS Resources

**Create DynamoDB Tables:**
```bash
cd aws
python3 dynamodb_setup.py
cd ..
```

**Create SNS Topic:**
```bash
cd aws
python3 sns_setup.py
# Follow prompts to subscribe your email
# Check email and confirm subscription
cd ..
```

#### 5. Configure Environment
```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Update the following in `.env`:
```
SECRET_KEY=your-random-secret-key-here
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:BankingTransactionAlerts
```

#### 6. Run Application
```bash
python3 run.py
```

#### 7. Access Application
Open browser: `http://localhost:5000`

**Test it:**
1. Click "Create Account"
2. Register with your email
3. Login
4. Create a checking account
5. Make a deposit of $500
6. Check your email for SNS notification!

---

## Option 2: AWS EC2 Deployment (Production)

### Prerequisites
- AWS account with billing enabled
- AWS CLI configured
- SSH key pair created in AWS

### Quick Deploy Script

```bash
#!/bin/bash
# AWS Region
REGION=us-east-1

# 1. Create DynamoDB tables
echo "Creating DynamoDB tables..."
python3 aws/dynamodb_setup.py

# 2. Create SNS topic
echo "Creating SNS topic..."
TOPIC_ARN=$(aws sns create-topic --name BankingTransactionAlerts \
  --query 'TopicArn' --output text)
echo "Topic ARN: $TOPIC_ARN"

# 3. Subscribe your email
read -p "Enter your email for alerts: " EMAIL
aws sns subscribe --topic-arn $TOPIC_ARN \
  --protocol email --notification-endpoint $EMAIL
echo "Check email and confirm subscription!"

# 4. Create IAM role
echo "Creating IAM role..."
aws iam create-role --role-name BankingAppEC2Role \
  --assume-role-policy-document file://aws/ec2-trust-policy.json

aws iam put-role-policy --role-name BankingAppEC2Role \
  --policy-name BankingAppPolicy \
  --policy-document file://aws/iam_policy.json

aws iam create-instance-profile \
  --instance-profile-name BankingAppProfile

aws iam add-role-to-instance-profile \
  --instance-profile-name BankingAppProfile \
  --role-name BankingAppEC2Role

sleep 10  # Wait for IAM propagation

# 5. Create security group
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" \
  --query 'Vpcs[0].VpcId' --output text)

SG_ID=$(aws ec2 create-security-group \
  --group-name banking-app-sg \
  --description "Banking App Security Group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' --output text)

# Add inbound rules
aws ec2 authorize-security-group-ingress --group-id $SG_ID \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress --group-id $SG_ID \
  --protocol tcp --port 5000 --cidr 0.0.0.0/0

# 6. Get Ubuntu AMI
AMI_ID=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text)

# 7. Launch EC2 instance
read -p "Enter your SSH key pair name: " KEY_NAME

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --key-name $KEY_NAME \
  --security-group-ids $SG_ID \
  --iam-instance-profile Name=BankingAppProfile \
  --user-data file://aws/ec2_user_data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=BankingApp}]' \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "Launched instance: $INSTANCE_ID"
echo "Waiting for instance to be running..."

aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# 8. Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Topic ARN: $TOPIC_ARN"
echo ""
echo "Next steps:"
echo "1. Confirm email subscription"
echo "2. Wait 5 minutes for instance setup"
echo "3. SSH: ssh -i ~/.ssh/$KEY_NAME.pem ubuntu@$PUBLIC_IP"
echo "4. Upload code and configure .env"
echo "5. Start service: sudo systemctl start banking-app"
echo "6. Access: http://$PUBLIC_IP:5000"
echo "========================================="
```

Save as `deploy.sh` and run:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## Testing Checklist (Quick)

### 1. Registration & Login
- [ ] Register new user (test@example.com)
- [ ] Verify password requirements work
- [ ] Login with credentials
- [ ] Check dashboard loads

### 2. Account Management
- [ ] Create checking account
- [ ] View account details
- [ ] Check balance display

### 3. Transactions
- [ ] Deposit $1000
- [ ] Withdraw $200
- [ ] Transfer $100 to another account
- [ ] View transaction history

### 4. Notifications
- [ ] Verify deposit email received
- [ ] Make $15,000 deposit
- [ ] Check for high-value alert email

### 5. Analytics
- [ ] Open analytics dashboard
- [ ] Check transaction summary
- [ ] View compliance metrics

---

## Common Issues & Fixes

### Issue: "Module not found" error
**Fix:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: "Unable to connect to DynamoDB"
**Fix:**
```bash
aws sts get-caller-identity  # Verify AWS credentials
export AWS_REGION=us-east-1
```

### Issue: "SNS publish failed"
**Fix:**
1. Check Topic ARN in .env
2. Verify IAM permissions
3. Confirm email subscription

### Issue: "Table does not exist"
**Fix:**
```bash
python3 aws/dynamodb_setup.py
aws dynamodb list-tables  # Verify creation
```

### Issue: Can't access EC2 application
**Fix:**
1. Check security group allows port 5000
2. Verify instance is running
3. Check application logs:
   ```bash
   sudo journalctl -u banking-app -n 50
   ```

---

## Development Workflow

### Making Changes

1. **Edit Code**
   ```bash
   nano app/routes/transaction_routes.py
   ```

2. **Test Locally**
   ```bash
   python3 run.py
   # Test in browser
   ```

3. **Deploy to EC2**
   ```bash
   # Upload changes
   scp -r app/ ubuntu@EC2_IP:/home/ubuntu/banking-system/
   
   # SSH and restart
   ssh ubuntu@EC2_IP
   sudo systemctl restart banking-app
   ```

### Adding New Features

1. Create branch (if using Git)
2. Add feature code
3. Test thoroughly
4. Update documentation
5. Deploy

---

## Useful Commands

### AWS CLI Commands

```bash
# List DynamoDB tables
aws dynamodb list-tables

# Describe table
aws dynamodb describe-table --table-name BankingUsers

# Scan table (view data)
aws dynamodb scan --table-name BankingUsers --max-items 5

# List SNS topics
aws sns list-topics

# List subscriptions
aws sns list-subscriptions

# EC2 instance status
aws ec2 describe-instance-status --instance-ids i-xxxxx

# View CloudWatch logs
aws logs tail /aws/banking-app --follow
```

### Application Commands

```bash
# Check application status
sudo systemctl status banking-app

# View logs
sudo journalctl -u banking-app -f

# Restart application
sudo systemctl restart banking-app

# Stop application
sudo systemctl stop banking-app

# Start application
sudo systemctl start banking-app
```

### Database Commands (Python)

```python
# Connect to DynamoDB
import boto3
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# List tables
tables = list(dynamodb.tables.all())
print([t.name for t in tables])

# Query users table
users_table = dynamodb.Table('BankingUsers')
response = users_table.scan(Limit=5)
print(response['Items'])

# Get specific user
user = users_table.get_item(Key={'user_id': 'your-user-id'})
print(user['Item'])
```

---

## Next Steps

### After Setup

1. **Security Hardening**
   - Change all default passwords
   - Restrict security group to specific IPs
   - Enable HTTPS with SSL certificate
   - Setup CloudWatch alarms

2. **Monitoring**
   - Enable CloudWatch detailed monitoring
   - Setup SNS alerts for errors
   - Configure log retention

3. **Backup**
   - Enable DynamoDB PITR (Point-in-time recovery)
   - Create AMI of EC2 instance
   - Setup automated backups

4. **Scaling**
   - Add Application Load Balancer
   - Create Auto Scaling Group
   - Setup Redis for sessions

### Learning Resources

- [AWS Free Tier](https://aws.amazon.com/free/)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

---

## Support

### Getting Help

1. Check documentation in `docs/` folder
2. Review error logs
3. Consult AWS documentation
4. Search Stack Overflow

### Reporting Issues

Include:
- Error message
- Steps to reproduce
- Environment (local/EC2)
- Relevant logs

---

## Cleanup (When Done Testing)

### Delete AWS Resources

```bash
# Stop EC2 instance
aws ec2 terminate-instances --instance-ids i-xxxxx

# Delete security group (after instance terminated)
aws ec2 delete-security-group --group-id sg-xxxxx

# Delete IAM resources
aws iam remove-role-from-instance-profile \
  --instance-profile-name BankingAppProfile \
  --role-name BankingAppEC2Role
aws iam delete-instance-profile --instance-profile-name BankingAppProfile
aws iam delete-role-policy --role-name BankingAppEC2Role --policy-name BankingAppPolicy
aws iam delete-role --role-name BankingAppEC2Role

# Delete DynamoDB tables
aws dynamodb delete-table --table-name BankingUsers
aws dynamodb delete-table --table-name BankingAccounts
aws dynamodb delete-table --table-name BankingTransactions

# Delete SNS topic
aws sns delete-topic --topic-arn arn:aws:sns:region:account:BankingTransactionAlerts
```

**Warning:** This will delete all data permanently!

---

## Success!

You should now have a fully functional banking system running either locally or on AWS EC2!

**What you've built:**
- ✅ Secure user authentication
- ✅ Multiple account management
- ✅ Transaction processing (deposit, withdraw, transfer)
- ✅ Real-time email notifications
- ✅ Analytics dashboard
- ✅ Compliance monitoring
- ✅ Cloud-native AWS architecture

**Next Challenge:**
- Add two-factor authentication
- Implement scheduled reports
- Build a mobile app
- Add real-time fraud detection
- Scale to multiple regions

---

**Happy Banking! 🏦**
