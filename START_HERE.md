# 🏦 Banking System - START HERE

## 🚀 Quick Start (5 Minutes)

### Step 1: Run Setup Script
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- ✓ Check Python installation
- ✓ Create virtual environment
- ✓ Install all dependencies
- ✓ Create .env configuration file

### Step 2: Configure AWS Credentials

**Option A: Use AWS CLI (Recommended)**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json
```

**Option B: Edit .env file directly**
```bash
nano .env
```
Add your credentials:
```
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
```

### Step 3: Create DynamoDB Tables
```bash
source venv/bin/activate
python3 aws/dynamodb_setup.py
```

You should see:
```
✓ Created table: BankingUsers
✓ Created table: BankingAccounts
✓ Created table: BankingTransactions
```

### Step 4: Setup Email Notifications (Optional)
```bash
python3 aws/sns_setup.py
```
- Enter your email when prompted
- Check your email and confirm the subscription

### Step 5: Run the Application
```bash
python3 run.py
```

You should see:
```
╔════════════════════════════════════════════════════════════╗
║   Banking Data Analytics & Reporting System                ║
║   Running on: http://0.0.0.0:5000                         ║
╚════════════════════════════════════════════════════════════╝
```

### Step 6: Open Browser
Navigate to: **http://localhost:5000**

---

## 🧪 Test the System

### 1. Register a New User
- Click "Create Account"
- Fill in the form:
  - Email: your-email@example.com
  - Password: Test123! (must have uppercase and number)
  - Full Name: Your Name
- Click "Create Account"

### 2. Login
- Use your registered email and password
- You should see the dashboard

### 3. Create a Bank Account
- Click "Create Account" in the navigation
- Select "Checking Account"
- Initial balance: 1000 (optional)
- Click "Create Account"

### 4. Make a Deposit
- Click "Deposit" in navigation
- Select your account
- Amount: 500
- Description: Test deposit
- Click "Deposit"
- ✓ Check your email for notification (if SNS configured)

### 5. Make a Withdrawal
- Click "Withdraw"
- Amount: 100
- Click "Withdraw"

### 6. Transfer Money
- Create a second account first
- Click "Transfer"
- Enter the account number of your second account
- Amount: 50
- Click "Transfer"

### 7. View Analytics
- Click "Analytics" > "Dashboard"
- See your transaction summary
- View spending patterns

---

## 📁 Project Structure

```
banking-system-final/
├── START_HERE.md          ← You are here!
├── setup.sh               ← Run this first
├── run.py                 ← Application entry point
├── requirements.txt       ← Python dependencies
├── .env.example           ← Configuration template
│
├── app/                   ← Main application
│   ├── __init__.py        ← Flask app factory
│   ├── config.py          ← Configuration
│   ├── models/            ← Database layer (DynamoDB)
│   ├── services/          ← Business logic
│   ├── routes/            ← API endpoints
│   ├── templates/         ← HTML pages
│   └── static/            ← CSS/JS files
│
├── aws/                   ← AWS setup scripts
│   ├── dynamodb_setup.py  ← Create tables
│   ├── sns_setup.py       ← Setup notifications
│   ├── iam_policy.json    ← IAM permissions
│   └── ec2_user_data.sh   ← EC2 deployment
│
└── docs/                  ← Documentation
    ├── DEPLOYMENT.md      ← AWS deployment guide
    ├── TESTING.md         ← Test checklist
    ├── ARCHITECTURE.md    ← Technical details
    └── QUICKSTART.md      ← Alternative setup guide
```

---

## ⚠️ Troubleshooting

### Problem: "Module not found"
**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: "Unable to connect to DynamoDB"
**Solution:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Or set in .env file
nano .env
```

### Problem: "Table does not exist"
**Solution:**
```bash
python3 aws/dynamodb_setup.py
```

### Problem: "Permission denied" on setup.sh
**Solution:**
```bash
chmod +x setup.sh
./setup.sh
```

### Problem: Application doesn't start
**Solution:**
```bash
# Check if port 5000 is available
lsof -i :5000

# Use different port
export FLASK_PORT=8000
python3 run.py
```

---

## 🔑 Important Files to Configure

### 1. .env File
Copy from `.env.example` and update:
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
- `SNS_TOPIC_ARN` - Your SNS topic (after running sns_setup.py)
- `SECRET_KEY` - Change to random string in production

### 2. AWS Region
Default is `us-east-1`. Change in .env if needed:
```
AWS_REGION=your-region
```

---

## 📚 Next Steps

### For Local Development
1. ✓ Follow steps above
2. ✓ Test all features
3. ✓ Check transaction emails
4. ✓ View analytics dashboard

### For AWS Deployment
1. Read `docs/DEPLOYMENT.md`
2. Create EC2 instance
3. Deploy application
4. Configure security groups
5. Access via public IP

### For Production
1. Change `SECRET_KEY` to random value
2. Set `FLASK_ENV=production`
3. Enable HTTPS
4. Setup monitoring
5. Configure backups

---

## 🆘 Getting Help

### Documentation
- **Quick Setup**: This file (START_HERE.md)
- **Full Deployment**: docs/DEPLOYMENT.md
- **Testing Guide**: docs/TESTING.md
- **Architecture**: docs/ARCHITECTURE.md

### Common Commands
```bash
# Activate virtual environment
source venv/bin/activate

# Run application
python3 run.py

# Create tables
python3 aws/dynamodb_setup.py

# Setup notifications
python3 aws/sns_setup.py

# Check AWS config
aws sts get-caller-identity

# List DynamoDB tables
aws dynamodb list-tables
```

---

## ✅ Success Checklist

- [ ] Setup script completed without errors
- [ ] AWS credentials configured
- [ ] DynamoDB tables created
- [ ] SNS topic created (optional)
- [ ] Application runs on http://localhost:5000
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Can create account
- [ ] Can make deposit
- [ ] Can view transactions
- [ ] Email notifications work (if SNS configured)

---

## 🎉 You're Ready!

If all steps completed successfully, you now have a fully functional banking system running locally!

**Access it at:** http://localhost:5000

**What you can do:**
- ✓ Register and login
- ✓ Create multiple accounts
- ✓ Deposit/withdraw money
- ✓ Transfer between accounts
- ✓ View transaction history
- ✓ See analytics dashboard
- ✓ Get email notifications

**Enjoy! 🚀**
