# Banking Data Analytics & Reporting System

A cloud-hosted banking data analytics system built with Flask, Python, and AWS services (DynamoDB, SNS, EC2).

## 🏗️ Architecture

This system follows a three-tier architecture:
- **Presentation Layer**: Flask routes and HTML templates
- **Business Logic Layer**: Service classes for banking operations
- **Data Access Layer**: DynamoDB models with boto3

## 🚀 Features

### Core Banking Operations
- ✅ User registration and authentication with bcrypt password hashing
- ✅ Secure session management
- ✅ Multiple account management per user
- ✅ Deposit and withdrawal transactions
- ✅ User-to-user money transfers
- ✅ Complete transaction history tracking

### Analytics & Reporting
- 📊 Real-time account balance dashboard
- 📈 Transaction summaries (daily, monthly, yearly)
- 🔍 Transaction search and filtering
- 📉 Spending patterns analysis
- 🚨 High-value transaction alerts
- 📋 Compliance metric placeholders

### AWS Integration
- 🗄️ DynamoDB for scalable data storage
- 📧 SNS for real-time email notifications
- 🖥️ EC2 hosting with proper IAM roles
- 🔒 Security best practices implementation

## 📋 Prerequisites

- Python 3.8+
- AWS Account with appropriate permissions
- AWS CLI configured (for deployment)
- boto3 library

## 🛠️ Installation

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd banking-system
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
```bash
export FLASK_ENV=development
export AWS_REGION=us-east-1
export SECRET_KEY=your-secret-key-here
export DYNAMODB_USERS_TABLE=BankingUsers
export DYNAMODB_ACCOUNTS_TABLE=BankingAccounts
export DYNAMODB_TRANSACTIONS_TABLE=BankingTransactions
export SNS_TOPIC_ARN=arn:aws:sns:region:account:topic-name
```

5. **Create DynamoDB tables** (see AWS Setup section)

6. **Run the application**
```bash
python run.py
```

Visit `http://localhost:5000` in your browser.

## ☁️ AWS Setup

### Step 1: Create DynamoDB Tables

```bash
# Navigate to AWS directory
cd aws/

# Run DynamoDB setup script
python dynamodb_setup.py
```

This creates three tables:
- **BankingUsers**: Stores user credentials and profile
- **BankingAccounts**: Stores account balances and details
- **BankingTransactions**: Stores all transaction records

### Step 2: Configure IAM Role

Create an IAM role for EC2 with the policy in `aws/iam_policy.json`:

```bash
# Create role
aws iam create-role --role-name BankingAppEC2Role \
  --assume-role-policy-document file://ec2-trust-policy.json

# Attach policy
aws iam put-role-policy --role-name BankingAppEC2Role \
  --policy-name BankingAppPolicy \
  --policy-document file://iam_policy.json

# Create instance profile
aws iam create-instance-profile --instance-profile-name BankingAppProfile
aws iam add-role-to-instance-profile \
  --instance-profile-name BankingAppProfile \
  --role-name BankingAppEC2Role
```

### Step 3: Setup SNS Topic

```bash
# Run SNS setup script
python aws/sns_setup.py
```

Or manually:
```bash
# Create SNS topic
aws sns create-topic --name BankingTransactionAlerts

# Subscribe email
aws sns subscribe --topic-arn <topic-arn> \
  --protocol email --notification-endpoint your-email@example.com
```

### Step 4: Launch EC2 Instance

```bash
# Launch instance with user data script
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxx \
  --iam-instance-profile Name=BankingAppProfile \
  --user-data file://aws/ec2_user_data.sh
```

## 🔒 Security Features

### Password Security
- Bcrypt hashing with cost factor 12 (production: 14)
- Salted password storage
- No plaintext passwords stored

### Session Management
- Secure cookie configuration
- HttpOnly and SameSite flags
- 2-hour session timeout
- Server-side session storage

### Account Lockout
- 5 failed login attempts = 30-minute lockout
- Automatic unlock after timeout period

### AWS Security
- IAM roles with least privilege principle
- No hardcoded credentials
- Instance profile for EC2
- Encrypted data in transit

## 📊 DynamoDB Schema

### Users Table
```
Primary Key: user_id (String)
GSI: EmailIndex on email

Attributes:
- user_id: Unique identifier
- email: User email (unique)
- password_hash: Bcrypt hashed password
- full_name: User's full name
- phone: Phone number
- created_at: Timestamp
- is_active: Boolean
- failed_login_attempts: Number
- account_locked_until: Timestamp
```

### Accounts Table
```
Primary Key: account_id (String)
GSI: UserIdIndex on user_id
GSI: AccountNumberIndex on account_number

Attributes:
- account_id: Unique identifier
- user_id: Owner's user ID
- account_number: 10-digit account number
- account_type: checking/savings
- balance: Decimal
- status: active/closed
- created_at: Timestamp
```

### Transactions Table
```
Primary Key: transaction_id (String)
GSI: AccountIdTimestampIndex on account_id + timestamp

Attributes:
- transaction_id: Unique identifier
- account_id: Account involved
- transaction_type: deposit/withdrawal/transfer_in/transfer_out
- amount: Decimal
- description: String
- timestamp: ISO datetime
- related_account_id: For transfers
- status: completed/pending/failed
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## 📝 API Endpoints

### Authentication
- `GET /auth/login` - Login page
- `POST /auth/login` - Process login
- `GET /auth/register` - Registration page
- `POST /auth/register` - Create new user
- `GET /auth/logout` - Logout user

### Accounts
- `GET /account/dashboard` - View dashboard
- `GET /account/details/<account_id>` - Account details
- `POST /account/create` - Create new account

### Transactions
- `POST /transactions/deposit` - Make deposit
- `POST /transactions/withdraw` - Make withdrawal
- `POST /transactions/transfer` - Transfer money
- `GET /transactions/history` - View transaction history

### Analytics
- `GET /analytics/dashboard` - Analytics dashboard
- `GET /analytics/monthly/<year>/<month>` - Monthly report
- `GET /analytics/yearly/<year>` - Yearly report

## 🚀 Deployment to EC2

1. SSH into your EC2 instance
2. Clone repository
3. Install dependencies
4. Set environment variables
5. Run with Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

For production with systemd service, see `docs/DEPLOYMENT.md`

## 📖 Documentation

- [Architecture Details](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Testing Checklist](docs/TESTING.md)

## 🤝 Contributing

This is an academic/demo project. Contributions for educational purposes are welcome.

## 📄 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This is a demonstration project for educational purposes. For production banking systems:
- Implement additional security measures
- Add comprehensive audit logging
- Implement proper encryption at rest
- Add rate limiting and DDoS protection
- Implement proper monitoring and alerting
- Conduct security audits and penetration testing
- Ensure compliance with banking regulations (PSD2, SOX, etc.)

## 📧 Support

For questions or issues, please open an issue on GitHub.

---

**Built with ❤️ using Flask, Python, and AWS**
