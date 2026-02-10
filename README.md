# Banking Data Analytics System

A cloud-based banking application built with Flask and AWS DynamoDB for secure account management, transactions, and analytics.

## Features

- **User Authentication** - Secure registration and login with password hashing
- **Account Management** - Create multiple checking/savings accounts
- **Transactions** - Deposit, withdraw, and transfer money
- **Transaction History** - View complete transaction records
- **Analytics Dashboard** - Track spending patterns and account summaries
- **AWS DynamoDB** - Scalable NoSQL database backend
- **Security** - bcrypt password hashing, account lockout protection

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: AWS DynamoDB
- **Authentication**: bcrypt
- **Frontend**: Bootstrap 5
- **Deployment**: AWS EC2

## Prerequisites

- Python 3.8+
- AWS Account
- AWS CLI configured

## Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd banking-system
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

5. **Setup AWS DynamoDB tables**
```bash
python app_aws.py
```

6. **Run the application**
```bash
python app.py
```

7. **Open browser**
```
http://localhost:5000
```

## AWS Setup

### Create DynamoDB Tables

Run the AWS setup script:
```bash
python app_aws.py
```

This creates three tables:
- `BankingUsers` - User accounts and authentication
- `BankingAccounts` - Bank accounts and balances
- `BankingTransactions` - Transaction records

### Configure AWS Credentials

**Option 1: AWS CLI**
```bash
aws configure
```

**Option 2: Environment Variables**

Edit `.env` file:
```
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
```

## Project Structure

```
banking-system/
├── app.py              # Main Flask application
├── app_aws.py          # AWS DynamoDB configuration
├── models.py           # Database models (User, Account, Transaction)
├── templates/          # HTML templates
├── static/             # CSS and JavaScript
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # This file
```

## Usage

### Register a New User
1. Go to `/register`
2. Fill in email, password, and full name
3. Click "Register"

### Login
1. Go to `/login`
2. Enter email and password
3. Access your dashboard

### Create Account
1. Click "Accounts" → "Create Account"
2. Choose account type (Checking/Savings)
3. Set initial balance (optional)

### Make a Deposit
1. Click "Transactions" → "Deposit"
2. Select account
3. Enter amount and description
4. Submit

### Transfer Money
1. Click "Transactions" → "Transfer"
2. Select source account
3. Enter destination account number
4. Enter amount
5. Submit

### View Analytics
1. Click "Analytics"
2. See transaction summaries and spending patterns

## Database Schema

### BankingUsers Table
- Primary Key: `user_id`
- GSI: `EmailIndex` on `email`
- Attributes: email, password_hash, full_name, phone, created_at

### BankingAccounts Table
- Primary Key: `account_id`
- GSI: `UserIdIndex` on `user_id`
- GSI: `AccountNumberIndex` on `account_number`
- Attributes: account_number, user_id, balance, account_type, status

### BankingTransactions Table
- Primary Key: `transaction_id`
- GSI: `AccountIdTimestampIndex` on `account_id` + `timestamp`
- Attributes: account_id, transaction_type, amount, description, timestamp

## Security Features

- **Password Hashing**: bcrypt with 12 rounds
- **Account Lockout**: 5 failed attempts = 30 min lockout
- **Secure Sessions**: Flask session management
- **Input Validation**: Server-side validation on all forms
- **Atomic Transactions**: DynamoDB conditional writes

## API Endpoints

- `GET /` - Home (redirects to dashboard or login)
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - Logout
- `GET /dashboard` - Main dashboard
- `GET /accounts` - List accounts
- `GET/POST /accounts/create` - Create new account
- `GET/POST /deposit` - Make deposit
- `GET/POST /withdraw` - Make withdrawal
- `GET/POST /transfer` - Transfer money
- `GET /transactions` - Transaction history
- `GET /analytics` - Analytics dashboard

## Deployment

### Local Development
```bash
python app.py
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### AWS EC2 Deployment
1. Launch EC2 instance (Ubuntu 20.04)
2. Install Python 3 and dependencies
3. Clone repository
4. Setup environment variables
5. Create DynamoDB tables
6. Run with Gunicorn

## Testing

1. **Register** a test user
2. **Create** a checking account
3. **Deposit** $1000
4. **Withdraw** $200
5. **Transfer** to another account
6. **View** transaction history
7. **Check** analytics dashboard

## Troubleshooting

**Can't connect to DynamoDB?**
- Check AWS credentials in `.env`
- Verify AWS CLI: `aws sts get-caller-identity`

**Tables don't exist?**
- Run: `python app_aws.py`

**Import errors?**
- Activate venv: `source venv/bin/activate`
- Install: `pip install -r requirements.txt`

## Cost Estimate

**AWS Free Tier (First 12 Months)**
- DynamoDB: 25 GB storage FREE
- Total: $0/month

**After Free Tier**
- DynamoDB: ~$5-10/month
- EC2 (optional): ~$8/month

## License

MIT License

## Author

Your Name

## Contributing

Pull requests welcome!
