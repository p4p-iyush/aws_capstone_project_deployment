# Banking Data Analytics System - Project Structure

```
banking-system/
│
├── app/
│   ├── __init__.py                 # Flask app initialization
│   ├── config.py                   # Configuration settings
│   │
│   ├── models/                     # Data Access Layer
│   │   ├── __init__.py
│   │   ├── user_model.py          # User data model
│   │   ├── account_model.py       # Account data model
│   │   └── transaction_model.py   # Transaction data model
│   │
│   ├── services/                   # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Authentication logic
│   │   ├── account_service.py     # Account operations
│   │   ├── transaction_service.py # Transaction processing
│   │   ├── analytics_service.py   # Analytics & reporting
│   │   └── notification_service.py# SNS notification handler
│   │
│   ├── routes/                     # Presentation Layer
│   │   ├── __init__.py
│   │   ├── auth_routes.py         # Login/Register routes
│   │   ├── account_routes.py      # Account management routes
│   │   ├── transaction_routes.py  # Transaction routes
│   │   └── analytics_routes.py    # Dashboard/Analytics routes
│   │
│   ├── templates/                  # HTML Templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── transactions.html
│   │   └── analytics.html
│   │
│   └── static/                     # CSS/JS files
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
│
├── aws/                            # AWS Configuration
│   ├── dynamodb_setup.py          # DynamoDB table creation
│   ├── iam_policy.json            # IAM policy template
│   ├── sns_setup.py               # SNS topic configuration
│   └── ec2_user_data.sh           # EC2 bootstrap script
│
├── tests/                          # Testing
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_transactions.py
│   └── test_analytics.py
│
├── docs/                           # Documentation
│   ├── DEPLOYMENT.md              # Deployment guide
│   ├── TESTING.md                 # Testing checklist
│   └── ARCHITECTURE.md            # Architecture details
│
├── requirements.txt                # Python dependencies
├── run.py                         # Application entry point
└── README.md                      # Project overview
```

## Layer Responsibilities

### 1. **Presentation Layer** (`routes/`)
- Handle HTTP requests/responses
- Validate user input
- Render templates
- Session management

### 2. **Business Logic Layer** (`services/`)
- Core banking operations
- Transaction processing
- Analytics calculations
- Notification triggers
- Business rules enforcement

### 3. **Data Access Layer** (`models/`)
- DynamoDB interactions via boto3
- Data validation
- CRUD operations
- Query building

## Security Architecture

1. **Password Security**: bcrypt hashing (cost factor 12)
2. **Session Management**: Flask-Session with secure cookies
3. **IAM Roles**: EC2 instance profile with least privilege
4. **Input Validation**: Server-side validation for all inputs
5. **HTTPS**: SSL/TLS encryption (production)

## Scalability Considerations

- DynamoDB auto-scaling enabled
- Stateless application design
- SNS for async notifications
- Horizontal scaling ready (load balancer compatible)
