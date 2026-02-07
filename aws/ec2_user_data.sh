#!/bin/bash
# EC2 User Data Script for Banking Application
# This script runs on instance launch to setup the environment

# Update system
echo "==== Updating system packages ===="
yum update -y

# Install Python 3 and pip
echo "==== Installing Python 3 ===="
yum install -y python3 python3-pip git

# Install system dependencies
yum install -y gcc python3-devel

# Create application directory
echo "==== Setting up application ===="
cd /home/ec2-user
mkdir -p banking-app
cd banking-app

# Clone repository (replace with your actual repo URL)
# git clone https://github.com/yourusername/banking-system.git .

# For now, we'll assume code is uploaded manually
# Create necessary directories
mkdir -p app/templates app/static/css app/static/js app/models app/services app/routes

# Install Python dependencies
echo "==== Installing Python dependencies ===="
pip3 install flask boto3 bcrypt flask-session gunicorn python-dotenv

# Create systemd service file
echo "==== Creating systemd service ===="
cat > /etc/systemd/system/banking-app.service << 'EOF'
[Unit]
Description=Banking Data Analytics Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/banking-app
Environment="FLASK_ENV=production"
Environment="AWS_REGION=us-east-1"
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
chown -R ec2-user:ec2-user /home/ec2-user/banking-app

# Create environment file template
cat > /home/ec2-user/banking-app/.env << 'EOF'
FLASK_ENV=production
SECRET_KEY=CHANGE_THIS_TO_A_RANDOM_SECRET_KEY
AWS_REGION=us-east-1
DYNAMODB_USERS_TABLE=BankingUsers
DYNAMODB_ACCOUNTS_TABLE=BankingAccounts
DYNAMODB_TRANSACTIONS_TABLE=BankingTransactions
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:BankingTransactionAlerts
ENABLE_SNS_NOTIFICATIONS=true
EOF

# Enable and start service (will fail until code is deployed)
systemctl daemon-reload
# systemctl enable banking-app
# systemctl start banking-app

echo "==== Setup complete ===="
echo "Next steps:"
echo "1. Upload application code to /home/ec2-user/banking-app"
echo "2. Update .env file with correct values"
echo "3. Run: sudo systemctl start banking-app"
echo "4. Check status: sudo systemctl status banking-app"
echo "5. View logs: sudo journalctl -u banking-app -f"
