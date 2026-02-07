# System Architecture Documentation
# Banking Data Analytics and Reporting System

## Executive Summary

This document describes the architecture of a cloud-hosted banking data analytics system built on AWS infrastructure. The system provides secure account management, transaction processing, real-time notifications, and comprehensive analytics capabilities.

---

## System Overview

### Purpose
Provide a secure, scalable platform for:
- Banking operations (deposits, withdrawals, transfers)
- Transaction monitoring and analytics
- Compliance reporting
- Real-time fraud alerts

### Key Technologies
- **Backend:** Python 3.8+ with Flask web framework
- **Database:** AWS DynamoDB (NoSQL)
- **Notifications:** AWS SNS (Simple Notification Service)
- **Hosting:** AWS EC2 (Elastic Compute Cloud)
- **Security:** IAM Roles, bcrypt password hashing, Flask sessions

---

## Architecture Patterns

### 1. Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Layer                      │
│  (Flask Routes, HTML Templates, Static Files)           │
│  - User Interface                                        │
│  - Request/Response Handling                             │
│  - Session Management                                    │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                 Business Logic Layer                     │
│  (Services: Auth, Account, Transaction, Analytics)      │
│  - Business Rules                                        │
│  - Transaction Processing                                │
│  - Validation Logic                                      │
│  - Notification Triggers                                 │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                  Data Access Layer                       │
│  (Models: User, Account, Transaction)                   │
│  - boto3 DynamoDB Operations                            │
│  - Data Validation                                       │
│  - CRUD Operations                                       │
└──────────────────────────────────────────────────────────┘
```

**Benefits:**
- Clear separation of concerns
- Easy to test each layer independently
- Maintainable and scalable
- Follows industry best practices

### 2. Cloud-Native Design

```
                          ┌─────────────┐
                          │   Internet  │
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │   AWS EC2   │
                          │ (Flask App) │
                          └──────┬──────┘
                                 │
                    ┌────────────┼────────────┐
                    │                         │
            ┌───────▼────────┐       ┌───────▼────────┐
            │   DynamoDB     │       │   SNS Topic    │
            │  (3 Tables)    │       │ (Email Alerts) │
            └────────────────┘       └────────────────┘
                    │
            ┌───────┴────────┐
            │                │
    ┌───────▼──────┐  ┌─────▼──────┐
    │   IAM Role   │  │ CloudWatch │
    │  (Security)  │  │   (Logs)   │
    └──────────────┘  └────────────┘
```

---

## Component Details

### 1. Presentation Layer

#### Components
- **Flask Routes** (`app/routes/`)
  - `auth_routes.py`: Login, logout, registration
  - `account_routes.py`: Account management, dashboard
  - `transaction_routes.py`: Deposits, withdrawals, transfers
  - `analytics_routes.py`: Reports, compliance metrics

- **HTML Templates** (`app/templates/`)
  - Base template with Bootstrap 5
  - Responsive design
  - Flash message support
  - Client-side validation

- **Static Assets** (`app/static/`)
  - Custom CSS styling
  - JavaScript for UX enhancements
  - No external dependencies beyond Bootstrap CDN

#### Responsibilities
- Render UI components
- Handle HTTP requests
- Validate user input
- Manage user sessions
- Display flash messages

#### Security Features
- CSRF protection (Flask default)
- XSS prevention (template escaping)
- Session cookies with HttpOnly flag
- Login required decorator for protected routes

---

### 2. Business Logic Layer

#### Services

##### AuthService (`app/services/auth_service.py`)
**Purpose:** User authentication and authorization

**Key Methods:**
- `register_user()`: Create new user with hashed password
- `login_user()`: Authenticate and create session
- `logout_user()`: Clear session
- `change_password()`: Update user password
- `get_current_user()`: Retrieve logged-in user

**Business Rules:**
- Password min 8 chars, 1 uppercase, 1 number
- Email uniqueness enforced
- Account lockout after 5 failed attempts
- 30-minute lockout duration

##### AccountService (`app/services/account_service.py`)
**Purpose:** Account management operations

**Key Methods:**
- `create_account()`: Create new banking account
- `get_user_accounts()`: List all user accounts
- `get_account_balance()`: Retrieve current balance
- `get_account_summary()`: Generate account statistics

**Business Rules:**
- Multiple accounts per user allowed
- Account types: checking, savings
- Non-negative balance enforcement
- Account closure requires zero balance

##### TransactionService (`app/services/transaction_service.py`)
**Purpose:** Transaction processing

**Key Methods:**
- `deposit()`: Add funds to account
- `withdraw()`: Remove funds with validation
- `transfer()`: Move funds between accounts
- `get_transaction_history()`: Retrieve transactions

**Business Rules:**
- Amount validation (> 0, < max limit)
- Insufficient funds check on withdrawals
- Atomic balance updates
- Transaction rollback on failure
- Duplicate transfer prevention

##### NotificationService (`app/services/notification_service.py`)
**Purpose:** SNS-based notifications

**Key Methods:**
- `send_transaction_alert()`: Regular transaction email
- `send_high_value_alert()`: Alert for large transactions
- `send_transfer_confirmation()`: Transfer receipt
- `send_suspicious_activity_alert()`: Compliance alert

**Business Rules:**
- High-value threshold: $10,000
- Alert sent for every transaction (if enabled)
- Suspicious activity: 5+ high-value txns in 24h

##### AnalyticsService (`app/services/analytics_service.py`)
**Purpose:** Data analytics and reporting

**Key Methods:**
- `get_account_analytics()`: Transaction summaries
- `get_monthly_report()`: Monthly breakdown
- `get_yearly_report()`: Annual analysis
- `get_compliance_metrics()`: Regulatory metrics
- `get_dashboard_data()`: Overview statistics

**Analytics Calculated:**
- Total deposits/withdrawals
- Net change
- Average transaction size
- Spending patterns (weekday vs weekend)
- High-value transaction count
- Risk level assessment

---

### 3. Data Access Layer

#### Models

##### UserModel (`app/models/user_model.py`)
**DynamoDB Table:** BankingUsers

**Schema:**
```
Primary Key: user_id (String)
GSI: EmailIndex on email

Attributes:
- user_id: UUID v4
- email: Lowercase email
- password_hash: Bcrypt hash
- full_name: String
- phone: String
- created_at: ISO 8601 timestamp
- failed_login_attempts: Number
- account_locked_until: Timestamp
```

**Operations:**
- `create_user()`: Register new user
- `get_user_by_email()`: Query via GSI
- `verify_password()`: Authenticate user
- `change_password()`: Update credentials

##### AccountModel (`app/models/account_model.py`)
**DynamoDB Table:** BankingAccounts

**Schema:**
```
Primary Key: account_id (String)
GSI: UserIdIndex on user_id
GSI: AccountNumberIndex on account_number

Attributes:
- account_id: UUID v4
- user_id: Foreign key
- account_number: 10-digit unique
- account_type: checking/savings
- balance: Decimal (high precision)
- status: active/closed
- created_at: Timestamp
```

**Operations:**
- `create_account()`: Generate account with unique number
- `update_balance()`: Atomic balance update with ADD operation
- `get_user_accounts()`: Query via UserIdIndex
- `get_account_by_number()`: Query via AccountNumberIndex

**Critical Features:**
- Decimal type for precise balance tracking
- Atomic updates prevent race conditions
- Conditional writes ensure data integrity

##### TransactionModel (`app/models/transaction_model.py`)
**DynamoDB Table:** BankingTransactions

**Schema:**
```
Primary Key: transaction_id (String)
GSI: AccountIdTimestampIndex (account_id HASH, timestamp RANGE)

Attributes:
- transaction_id: UUID v4
- account_id: Foreign key
- transaction_type: deposit/withdrawal/transfer_in/transfer_out
- amount: Decimal
- timestamp: ISO 8601
- description: String
- related_account_id: String (for transfers)
```

**Operations:**
- `create_transaction()`: Record transaction
- `get_account_transactions()`: Query via GSI, sorted by time
- `get_transaction_summary()`: Aggregate statistics
- `get_high_value_transactions()`: Compliance queries

---

## AWS Services Integration

### DynamoDB

**Choice Rationale:**
- NoSQL flexibility for rapid development
- Automatic scaling
- Low latency for banking operations
- Built-in global secondary indexes
- Atomic operations support

**Capacity Planning:**
- Provisioned: 5 Read/Write units per table
- On-Demand mode recommended for production
- Auto-scaling enabled

**Cost Optimization:**
- Use sparse indexes
- Efficient query patterns
- Time-based data archiving

### SNS (Simple Notification Service)

**Use Cases:**
- Transaction confirmations
- High-value transaction alerts
- Suspicious activity notifications
- Account status changes

**Topic Structure:**
```
BankingTransactionAlerts
├── Email Subscriptions
│   ├── User emails (transaction confirmations)
│   └── Compliance email (fraud alerts)
```

**Message Format:**
- Plain text email body
- Structured with transaction details
- Timestamp in UTC
- Reference numbers for tracking

### EC2 (Elastic Compute Cloud)

**Instance Configuration:**
- Type: t2.micro (free tier eligible)
- OS: Ubuntu 20.04 LTS
- Python 3.8+
- Gunicorn WSGI server with 4 workers

**Networking:**
- Public subnet for internet access
- Security group: ports 22 (SSH), 5000 (HTTP), 443 (HTTPS)
- Elastic IP for static addressing (optional)

**Application Deployment:**
- systemd service for auto-start
- Gunicorn for production serving
- Environment variables via .env file
- Logs to journald

### IAM (Identity and Access Management)

**Role Structure:**
```
BankingAppEC2Role
├── DynamoDB Access Policy
│   ├── Read/Write to all 3 tables
│   └── Query/Scan on GSIs
├── SNS Publish Policy
│   └── Publish to BankingTransactionAlerts
└── CloudWatch Logs Policy
    └── Write application logs
```

**Security Principles:**
- Least privilege access
- No hardcoded credentials
- Instance profile attachment
- Service-level permissions only

---

## Data Flow Diagrams

### User Registration Flow

```
User → [Register Form] → Auth Route → Auth Service
                                           ↓
                                   Validate Input
                                           ↓
                                   Hash Password (bcrypt)
                                           ↓
                                   User Model
                                           ↓
                                   DynamoDB: Create User
                                           ↓
                                   Account Model
                                           ↓
                                   DynamoDB: Create Default Account
                                           ↓
                                   Success → Redirect to Login
```

### Transaction Flow (Deposit)

```
User → [Deposit Form] → Transaction Route → Transaction Service
                                                      ↓
                                              Validate Amount
                                                      ↓
                                              Account Model
                                                      ↓
                                      DynamoDB: Atomic Balance Update
                                                      ↓
                                              Transaction Model
                                                      ↓
                                      DynamoDB: Record Transaction
                                                      ↓
                                              Notification Service
                                                      ↓
                                              SNS: Publish Alert
                                                      ↓
                                              Email Sent to User
                                                      ↓
                                              Success Message
```

### Transfer Flow (with Rollback)

```
User → [Transfer Form] → Transaction Service
                                ↓
                        Validate Accounts
                                ↓
                    Debit Source Account (DynamoDB)
                                ↓
                        [Try] Credit Dest Account
                                ↓
                      ┌─────────┴─────────┐
                      │                   │
                  Success              Failure
                      │                   │
              Record Transactions    Rollback Debit
                      │                   │
              Send Confirmation      Return Error
```

---

## Security Architecture

### Authentication & Authorization

**Multi-Layer Security:**
1. **Password Security**
   - bcrypt hashing (cost factor 12)
   - Salted automatically
   - Never stored in plaintext
   - Minimum complexity requirements

2. **Session Management**
   - Server-side session storage
   - HttpOnly cookies (XSS prevention)
   - SameSite=Lax (CSRF protection)
   - 2-hour timeout

3. **Account Lockout**
   - 5 failed attempts = 30-min lock
   - Automatic unlock after timeout
   - Prevents brute force attacks

4. **Authorization**
   - Login required decorator
   - User ownership validation
   - Cannot access other users' data

### AWS Security

**IAM Best Practices:**
- Instance profiles (no credential files)
- Least privilege policies
- Resource-level permissions
- No wildcard (*) access

**Network Security:**
- Security groups (stateful firewall)
- Restricted SSH access (specific IP)
- HTTPS enforced in production
- VPC isolation (recommended)

**Data Security:**
- DynamoDB encryption at rest
- TLS in transit
- No sensitive data in logs
- Password hashing with bcrypt

---

## Scalability & Performance

### Horizontal Scaling

**Current Limitations:**
- Single EC2 instance
- Stateful sessions (filesystem-based)

**Scaling Strategy:**
```
┌──────────────────────────────────┐
│    Application Load Balancer     │
└────────┬────────────┬─────────────┘
         │            │
    ┌────▼────┐  ┌───▼─────┐
    │  EC2-1  │  │  EC2-2  │
    └─────────┘  └─────────┘
         │            │
    ┌────▼────────────▼────┐
    │     DynamoDB          │
    │  (Auto-scaling)       │
    └───────────────────────┘
```

**Required Changes:**
- Redis/ElastiCache for sessions
- Sticky sessions on ALB
- Health check endpoint
- Shared filesystem or S3 for uploads

### Database Optimization

**Query Patterns:**
- GSIs for all non-primary queries
- Efficient key design
- Sparse indexes where applicable
- Batch operations for bulk writes

**DynamoDB Best Practices:**
- Partition key with high cardinality (user_id, account_id)
- Sort key for range queries (timestamp)
- Consistent reads only when necessary
- On-Demand billing for variable load

### Caching Strategy

**Potential Caching Layers:**
1. **Application Cache:**
   - User session data
   - Account balances (short TTL)
   - Analytics summaries

2. **CloudFront CDN:**
   - Static assets (CSS, JS, images)
   - Template caching

3. **DynamoDB DAX:**
   - Read-heavy workloads
   - Microsecond latency

---

## Monitoring & Observability

### Application Logs

**Logging Strategy:**
- Python logging module
- JSON structured logs
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Log Destinations:**
- systemd journald (local)
- CloudWatch Logs (production)
- Centralized log aggregation

### CloudWatch Metrics

**Key Metrics:**
- EC2 CPU utilization
- DynamoDB read/write capacity
- SNS message delivery rate
- Application error rate

**Alarms:**
- High CPU (> 80%)
- DynamoDB throttling
- Failed SNS deliveries
- Application errors (> 5/min)

### Compliance Monitoring

**Regulatory Metrics:**
- High-value transaction count
- Suspicious activity patterns
- Transaction volumes by type
- Failed authentication attempts

**Reporting:**
- Daily compliance summary
- Weekly analytics dashboard
- Monthly audit reports

---

## Disaster Recovery & Backup

### Data Backup

**DynamoDB:**
- Point-in-time recovery (PITR) enabled
- On-demand backups before major changes
- 35-day retention period

**Application Code:**
- Git version control
- Automated CI/CD pipeline
- Tagged releases

### Recovery Procedures

**RTO/RPO Targets:**
- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 5 minutes

**Recovery Steps:**
1. Launch new EC2 from AMI
2. Attach IAM role
3. Deploy latest code
4. Point DNS to new instance
5. Verify functionality

---

## Future Enhancements

### Phase 1 (Short-term)
- [ ] HTTPS with SSL/TLS certificate
- [ ] Application Load Balancer
- [ ] Auto-scaling group
- [ ] Redis session storage
- [ ] CloudWatch dashboards

### Phase 2 (Medium-term)
- [ ] Multi-region deployment
- [ ] Real-time fraud detection with Lambda
- [ ] Mobile app (React Native)
- [ ] Two-factor authentication (2FA)
- [ ] Advanced analytics with QuickSight

### Phase 3 (Long-term)
- [ ] Machine learning fraud detection
- [ ] GraphQL API
- [ ] Microservices architecture
- [ ] Kubernetes deployment
- [ ] Blockchain integration for audit trail

---

## Compliance & Regulations

### Banking Standards

**Applicable Frameworks:**
- PCI DSS (Payment Card Industry Data Security Standard)
- SOX (Sarbanes-Oxley Act)
- GDPR (for European users)
- PSD2 (Payment Services Directive)

**Current Compliance:**
- ✓ Data encryption (in transit and at rest)
- ✓ Audit trail (transaction logs)
- ✓ Access controls (IAM)
- ✓ Password policies
- ✗ Third-party security audit (required for production)

### Data Privacy

**User Data Protection:**
- Minimal data collection
- No sale of user data
- Data deletion on request
- Privacy policy (to be added)

---

## Conclusion

This architecture provides a solid foundation for a banking data analytics system with:

**Strengths:**
- Secure authentication and authorization
- Scalable cloud infrastructure
- Real-time notifications
- Comprehensive analytics
- Clear separation of concerns

**Production Readiness:**
- ⚠️ Demo/academic project
- ✓ Can be production-ized with enhancements
- ⚠️ Requires security audit
- ⚠️ Needs high availability setup

**Total Cost (AWS Free Tier):**
- EC2 t2.micro: Free for 12 months
- DynamoDB: 25 GB storage free
- SNS: 1,000 emails/month free
- **Estimated:** $0/month (within free tier limits)

**After Free Tier:**
- Estimated: $10-20/month for light usage
- $50-100/month for moderate usage

---

**Architecture Version:** 1.0  
**Last Updated:** 2024-01-15  
**Author:** Banking System Team
