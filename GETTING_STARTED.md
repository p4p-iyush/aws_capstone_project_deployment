# 🚀 Getting Started - Banking System

## Welcome! 👋

This is a **complete, ready-to-run** banking data analytics system. Follow these steps to get it working in **5-10 minutes**.

---

## 📋 Prerequisites

Before you start, you need:

1. **Python 3.8 or higher** installed
   - Check: `python3 --version`
   - Download: https://www.python.org/downloads/

2. **AWS Account** (free tier is fine)
   - Sign up: https://aws.amazon.com/free/

3. **AWS CLI** installed and configured
   - Install: https://aws.amazon.com/cli/
   - Configure: `aws configure`

---

## 🏃 Quick Start (Recommended)

### Step 1: Run the Setup Script

```bash
./setup.sh
```

This automatically:
- ✓ Creates virtual environment
- ✓ Installs all dependencies
- ✓ Creates configuration file
- ✓ Checks AWS setup

### Step 2: Configure AWS

If not already done:
```bash
aws configure
```

Enter:
- **AWS Access Key ID**: (from AWS IAM)
- **AWS Secret Access Key**: (from AWS IAM)
- **Default region**: us-east-1
- **Default output format**: json

### Step 3: Create Database Tables

```bash
source venv/bin/activate
python3 aws/dynamodb_setup.py
```

Wait for confirmation:
```
✓ Created table: BankingUsers
✓ Created table: BankingAccounts
✓ Created table: BankingTransactions
```

### Step 4: (Optional) Setup Email Notifications

```bash
python3 aws/sns_setup.py
```

Enter your email and confirm the subscription.

### Step 5: Run the Application

```bash
python3 run.py
```

### Step 6: Open Your Browser

Go to: **http://localhost:5000**

**You're done! 🎉**

---

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

### 1. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Configuration
```bash
cp .env.example .env
nano .env  # Edit with your AWS credentials
```

### 4. Setup AWS Resources
```bash
python3 aws/dynamodb_setup.py
python3 aws/sns_setup.py
```

### 5. Run Application
```bash
python3 run.py
```

---

## ✅ Verify Installation

Run the test script:
```bash
python3 test_installation.py
```

You should see:
```
🎉 All tests passed! You're ready to run the application.
```

---

## 🧪 Testing the System

### 1. Register a User
- Open http://localhost:5000
- Click "Create Account"
- Fill in:
  - Email: test@example.com
  - Password: Test123!
  - Full Name: Test User
- Click "Create Account"

### 2. Login
- Use your email and password
- You'll see the dashboard

### 3. Create a Bank Account
- Click "Accounts" → "Create Account"
- Select "Checking Account"
- Initial balance: 1000
- Click "Create Account"

### 4. Make Transactions

**Deposit:**
- Click "Transactions" → "Deposit"
- Amount: 500
- Click "Deposit"

**Withdraw:**
- Click "Transactions" → "Withdraw"
- Amount: 100
- Click "Withdraw"

**Transfer:**
- Create a second account first
- Click "Transactions" → "Transfer"
- Enter destination account number
- Amount: 50
- Click "Transfer"

### 5. View Analytics
- Click "Analytics" → "Dashboard"
- See your transaction summary

### 6. Check Email
If SNS is configured, you'll receive:
- Transaction confirmation emails
- High-value alerts (for transactions > $10,000)

---

## 📂 What's Included

```
banking-system-final/
├── START_HERE.md          ← Quick start guide
├── GETTING_STARTED.md     ← This file
├── setup.sh               ← Automated setup
├── test_installation.py   ← Installation tester
├── run.py                 ← Start the app
│
├── app/                   ← Application code
│   ├── models/            ← Database (DynamoDB)
│   ├── services/          ← Business logic
│   ├── routes/            ← Web endpoints
│   ├── templates/         ← HTML pages
│   └── static/            ← CSS/JS
│
├── aws/                   ← AWS setup
│   ├── dynamodb_setup.py
│   ├── sns_setup.py
│   └── iam_policy.json
│
└── docs/                  ← Full documentation
    ├── DEPLOYMENT.md
    ├── TESTING.md
    └── ARCHITECTURE.md
```

---

## 🔍 Features You Get

### Banking Operations
- ✓ User registration & login
- ✓ Multiple accounts per user
- ✓ Deposits
- ✓ Withdrawals
- ✓ User-to-user transfers
- ✓ Transaction history

### Analytics
- ✓ Account balance dashboard
- ✓ Transaction summaries
- ✓ Spending patterns
- ✓ Monthly/yearly reports
- ✓ Compliance metrics

### Notifications
- ✓ Email alerts via AWS SNS
- ✓ Transaction confirmations
- ✓ High-value alerts
- ✓ Transfer receipts

### Security
- ✓ Password hashing (bcrypt)
- ✓ Secure sessions
- ✓ Account lockout
- ✓ IAM role-based access

---

## ⚙️ Configuration

### Environment Variables (.env)

Key settings in your `.env` file:

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# Tables
DYNAMODB_USERS_TABLE=BankingUsers
DYNAMODB_ACCOUNTS_TABLE=BankingAccounts
DYNAMODB_TRANSACTIONS_TABLE=BankingTransactions

# SNS
SNS_TOPIC_ARN=arn:aws:sns:...
ENABLE_SNS_NOTIFICATIONS=true
```

---

## 🐛 Troubleshooting

### "Command not found: python3"
**Solution:** Install Python 3.8+
```bash
# macOS
brew install python3

# Ubuntu/Debian
sudo apt install python3

# Windows
Download from python.org
```

### "Module not found"
**Solution:** Install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Unable to connect to DynamoDB"
**Solution:** Check AWS credentials
```bash
aws sts get-caller-identity
# Should show your AWS account info
```

### "Table does not exist"
**Solution:** Create tables
```bash
python3 aws/dynamodb_setup.py
```

### "Port 5000 already in use"
**Solution:** Use different port
```bash
export FLASK_PORT=8000
python3 run.py
```

### "Permission denied: setup.sh"
**Solution:** Make executable
```bash
chmod +x setup.sh
./setup.sh
```

---

## 📚 Documentation

### Quick References
- **START_HERE.md** - Ultra-quick start
- **GETTING_STARTED.md** - This file
- **README.md** - Project overview

### Detailed Guides
- **docs/DEPLOYMENT.md** - AWS EC2 deployment
- **docs/TESTING.md** - Test checklist
- **docs/ARCHITECTURE.md** - Technical details
- **docs/QUICKSTART.md** - Alternative setup

---

## 💰 AWS Costs

### Free Tier (First 12 Months)
- DynamoDB: 25GB free
- SNS: 1,000 emails free
- EC2: 750 hours/month free (t2.micro)

**Estimated cost: $0/month** within free tier

### After Free Tier
- DynamoDB: ~$5-10/month
- SNS: ~$1-2/month
- EC2: ~$8/month (if deploying)

**Total: ~$15-20/month** for light usage

---

## 🚀 Next Steps

### For Development
1. ✓ Complete quick start above
2. ✓ Test all features
3. ✓ Review code in `app/`
4. ✓ Add your own features

### For Production
1. Read `docs/DEPLOYMENT.md`
2. Deploy to EC2
3. Enable HTTPS
4. Setup monitoring
5. Configure backups

### For Learning
1. Study `docs/ARCHITECTURE.md`
2. Review business logic in `app/services/`
3. Examine DynamoDB models in `app/models/`
4. Understand Flask routes in `app/routes/`

---

## 🆘 Need Help?

### Check These First
1. Run: `python3 test_installation.py`
2. Check logs in terminal
3. Verify AWS credentials
4. Ensure tables are created

### Documentation
- START_HERE.md - Quick start
- docs/DEPLOYMENT.md - Full deployment
- docs/TESTING.md - Test guide

### Common Commands
```bash
# Activate environment
source venv/bin/activate

# Run application
python3 run.py

# Create tables
python3 aws/dynamodb_setup.py

# Test installation
python3 test_installation.py

# Check AWS
aws sts get-caller-identity
```

---

## ✅ Success Checklist

Before you start:
- [ ] Python 3.8+ installed
- [ ] AWS account created
- [ ] AWS CLI installed

Setup complete when:
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] AWS credentials configured
- [ ] DynamoDB tables created
- [ ] Application runs without errors
- [ ] Can access http://localhost:5000

First test complete when:
- [ ] Registered new user
- [ ] Logged in successfully
- [ ] Created bank account
- [ ] Made deposit
- [ ] Viewed transaction history

---

## 🎉 You're All Set!

If you've completed the quick start, you now have a **fully functional banking system** running on your computer!

**What's working:**
- ✓ Web application on Flask
- ✓ Database on AWS DynamoDB
- ✓ Email notifications via SNS
- ✓ Secure authentication
- ✓ Transaction processing
- ✓ Analytics dashboard

**Access it:** http://localhost:5000

**Enjoy! 🚀**

---

*For questions or issues, check the docs/ folder for detailed guides.*
