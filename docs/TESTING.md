# Testing Checklist
# Banking Data Analytics System

## Pre-Deployment Testing (Local)

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] AWS credentials configured locally

### Database Connectivity
- [ ] Can connect to DynamoDB (test with boto3)
- [ ] All three tables exist and are active
- [ ] GSIs are properly configured

### Application Startup
- [ ] Flask app starts without errors
- [ ] Can access `http://localhost:5000`
- [ ] Static files (CSS/JS) load correctly
- [ ] No console errors in browser

---

## Functional Testing

### Authentication Tests

#### Registration
- [ ] Can access registration page
- [ ] **Test Case 1:** Register with valid data
  - Email: test1@example.com
  - Password: SecurePass123!
  - Full name: Test User One
  - **Expected:** Success message, redirect to login
  
- [ ] **Test Case 2:** Duplicate email registration
  - Use same email as above
  - **Expected:** Error message "User already exists"
  
- [ ] **Test Case 3:** Weak password
  - Password: weak
  - **Expected:** Error "Password must be at least 8 characters"
  
- [ ] **Test Case 4:** Password mismatch
  - Password: SecurePass123!
  - Confirm: DifferentPass123!
  - **Expected:** Error "Passwords do not match"
  
- [ ] **Test Case 5:** Invalid email format
  - Email: invalid-email
  - **Expected:** Error "Invalid email format"

#### Login
- [ ] Can access login page
- [ ] **Test Case 1:** Valid credentials
  - Use registered email/password
  - **Expected:** Success, redirect to dashboard
  
- [ ] **Test Case 2:** Invalid password
  - Correct email, wrong password
  - **Expected:** Error "Invalid email or password"
  
- [ ] **Test Case 3:** Non-existent user
  - Email: nonexistent@example.com
  - **Expected:** Error "Invalid email or password"
  
- [ ] **Test Case 4:** Account lockout
  - Try 5 failed login attempts
  - **Expected:** Account locked for 30 minutes
  
- [ ] **Test Case 5:** Session persistence
  - Login, navigate away, come back
  - **Expected:** Still logged in

#### Logout
- [ ] Logout button visible when logged in
- [ ] Clicking logout clears session
- [ ] Redirects to login page
- [ ] Cannot access protected pages after logout

---

### Account Management Tests

#### Dashboard
- [ ] Dashboard loads successfully
- [ ] Shows correct total balance
- [ ] Displays all user accounts
- [ ] Shows recent transaction activity
- [ ] Quick action buttons work (Deposit, Withdraw, Transfer)

#### Account Creation
- [ ] Can access account creation page
- [ ] **Test Case 1:** Create checking account
  - Type: Checking
  - Initial balance: $100.00
  - **Expected:** Success, account created with unique number
  
- [ ] **Test Case 2:** Create savings account
  - Type: Savings
  - Initial balance: $1000.00
  - **Expected:** Success
  
- [ ] **Test Case 3:** Negative initial balance
  - Initial balance: -$50.00
  - **Expected:** Error "Cannot be negative"
  
- [ ] **Test Case 4:** Multiple accounts per user
  - Create 3 accounts
  - **Expected:** All visible in account list

#### Account Details
- [ ] Can view individual account details
- [ ] Shows correct balance
- [ ] Displays account number (partially masked)
- [ ] Shows account type and status
- [ ] Analytics section present

---

### Transaction Tests

#### Deposits
- [ ] Can access deposit page
- [ ] **Test Case 1:** Valid deposit
  - Amount: $500.00
  - **Expected:** Balance increases, success message
  
- [ ] **Test Case 2:** Small deposit
  - Amount: $0.01
  - **Expected:** Success
  
- [ ] **Test Case 3:** Large deposit
  - Amount: $50,000.00
  - **Expected:** Success, SNS alert sent
  
- [ ] **Test Case 4:** Zero amount
  - Amount: $0.00
  - **Expected:** Error "Must be greater than zero"
  
- [ ] **Test Case 5:** Negative amount
  - Amount: -$100.00
  - **Expected:** Error or prevented by input validation
  
- [ ] **Test Case 6:** Invalid format
  - Amount: "abc"
  - **Expected:** Error "Invalid amount format"

#### Withdrawals
- [ ] Can access withdrawal page
- [ ] **Test Case 1:** Valid withdrawal
  - Amount: $100.00 (less than balance)
  - **Expected:** Balance decreases, success message
  
- [ ] **Test Case 2:** Insufficient funds
  - Amount: $999,999.00
  - **Expected:** Error "Insufficient funds"
  
- [ ] **Test Case 3:** Exact balance withdrawal
  - Amount: [exact current balance]
  - **Expected:** Success, balance = $0.00
  
- [ ] **Test Case 4:** Large withdrawal
  - Amount: $20,000.00
  - **Expected:** Success (if sufficient funds), SNS alert
  
- [ ] **Test Case 5:** Zero amount
  - Amount: $0.00
  - **Expected:** Error

#### Transfers
- [ ] Can access transfer page
- [ ] **Test Case 1:** Valid transfer
  - From: Account A
  - To: Account B number
  - Amount: $250.00
  - **Expected:** From balance decreases, To balance increases
  
- [ ] **Test Case 2:** Self-transfer prevention
  - From: Account A
  - To: Account A number
  - **Expected:** Error "Cannot transfer to same account"
  
- [ ] **Test Case 3:** Invalid account number
  - To: 9999999999
  - **Expected:** Error "Account not found"
  
- [ ] **Test Case 4:** Insufficient funds transfer
  - Amount: More than balance
  - **Expected:** Error "Insufficient funds"
  
- [ ] **Test Case 5:** Transfer to inactive account
  - To: Closed account number
  - **Expected:** Error "Account is not active"
  
- [ ] **Test Case 6:** Large transfer
  - Amount: $15,000.00
  - **Expected:** Success, SNS alert, confirmation email

#### Transaction History
- [ ] Can access transaction history page
- [ ] All transactions displayed
- [ ] Sorted by date (newest first)
- [ ] Shows transaction type with correct badge color
- [ ] Shows amount, description, and status
- [ ] Can filter by account
- [ ] Pagination works (if many transactions)

---

### Analytics Tests

#### Dashboard Analytics
- [ ] Analytics dashboard loads
- [ ] Shows correct total deposits
- [ ] Shows correct total withdrawals
- [ ] Calculates net change correctly
- [ ] Displays average transaction
- [ ] Shows transaction count
- [ ] Largest transaction displayed correctly

#### Monthly Reports
- [ ] Can select month and year
- [ ] Report generates correctly
- [ ] Shows breakdown by transaction type
- [ ] Totals are accurate
- [ ] Can switch between accounts

#### Yearly Reports
- [ ] Can select year
- [ ] Report shows all 12 months
- [ ] Monthly breakdown is accurate
- [ ] Yearly totals calculated correctly
- [ ] Can export or print (if implemented)

#### Compliance Metrics
- [ ] Compliance page loads
- [ ] Shows high-value transaction count
- [ ] Displays suspicious activity patterns (if any)
- [ ] Risk level calculated correctly
- [ ] Shows large cash transactions

---

### SNS Notification Tests

#### Email Notifications
- [ ] **Test Case 1:** Deposit notification
  - Make deposit
  - **Expected:** Email received with transaction details
  
- [ ] **Test Case 2:** Withdrawal notification
  - Make withdrawal
  - **Expected:** Email received
  
- [ ] **Test Case 3:** Transfer confirmation
  - Complete transfer
  - **Expected:** Both sender and receiver notified
  
- [ ] **Test Case 4:** High-value alert
  - Transaction > $10,000
  - **Expected:** Additional security alert email
  
- [ ] **Test Case 5:** Notification content
  - Check email has: amount, account, timestamp
  - **Expected:** All details present and formatted correctly

#### Suspicious Activity Alerts
- [ ] Make 5+ high-value transactions in 24 hours
- [ ] **Expected:** Compliance alert generated
- [ ] Email sent to compliance address

---

## Security Testing

### Password Security
- [ ] Passwords are hashed (not stored in plaintext)
- [ ] Can verify password hashing:
  ```python
  # In DynamoDB, password_hash should be bcrypt hash
  # Should start with $2b$
  ```
- [ ] Password change requires old password
- [ ] Cannot reuse exact same password (if implemented)

### Session Security
- [ ] Sessions expire after timeout (2 hours default)
- [ ] Session cookie has HttpOnly flag
- [ ] Session cookie has Secure flag (in production)
- [ ] Logout clears session completely
- [ ] Cannot access protected routes without login

### Authorization
- [ ] Cannot access other users' accounts
- [ ] Cannot view other users' transactions
- [ ] Cannot transfer from accounts not owned by user
- [ ] API endpoints validate ownership

### Input Validation
- [ ] SQL injection attempts fail (N/A for DynamoDB, but test anyway)
- [ ] XSS attempts are escaped in templates
- [ ] CSRF protection enabled (Flask default)
- [ ] File upload validation (if implemented)

---

## Performance Testing

### Load Testing
- [ ] **Test Case 1:** Concurrent users
  - Simulate 10 users logging in simultaneously
  - **Expected:** All succeed without errors
  
- [ ] **Test Case 2:** Rapid transactions
  - Make 10 transactions in quick succession
  - **Expected:** All processed correctly
  
- [ ] **Test Case 3:** Large data volume
  - Create 1000+ transactions
  - **Expected:** History page loads in < 3 seconds

### Database Performance
- [ ] DynamoDB queries return in < 1 second
- [ ] GSI queries are efficient
- [ ] No timeout errors

---

## AWS Integration Testing

### DynamoDB
- [ ] Data persists correctly
- [ ] Can query by primary key
- [ ] GSI queries work
- [ ] Atomic updates work (balance changes)
- [ ] Conditional writes prevent race conditions

### SNS
- [ ] Topic exists
- [ ] Subscriptions confirmed
- [ ] Messages published successfully
- [ ] Emails delivered (check spam folder)
- [ ] Failed delivery handling

### IAM
- [ ] EC2 instance can access DynamoDB
- [ ] EC2 instance can publish to SNS
- [ ] No access to unauthorized resources
- [ ] Least privilege principle enforced

---

## Deployment Testing (EC2)

### Pre-Deployment
- [ ] Security group configured correctly
- [ ] IAM role attached to EC2
- [ ] Environment variables set
- [ ] Dependencies installed

### Post-Deployment
- [ ] Application starts on boot
- [ ] Gunicorn runs with 4 workers
- [ ] Can access via public IP
- [ ] Logs are being written
- [ ] Service restarts on failure

### Health Checks
- [ ] `/health` endpoint returns 200
- [ ] Application responds within 5 seconds
- [ ] No memory leaks after 1 hour
- [ ] CPU usage reasonable (< 50% under load)

---

## User Acceptance Testing

### User Experience
- [ ] UI is intuitive
- [ ] Navigation is clear
- [ ] Forms are easy to use
- [ ] Error messages are helpful
- [ ] Success messages are encouraging

### Accessibility
- [ ] Tab navigation works
- [ ] Form labels present
- [ ] Color contrast sufficient
- [ ] Responsive on mobile (basic)

### Browser Compatibility
- [ ] Works in Chrome
- [ ] Works in Firefox
- [ ] Works in Safari
- [ ] Works in Edge

---

## Compliance Testing

### Banking Regulations (Demo)
- [ ] High-value transactions flagged
- [ ] Transaction history auditable
- [ ] User data privacy maintained
- [ ] Compliance reports generated

### Data Protection
- [ ] Passwords hashed with bcrypt
- [ ] Sensitive data not logged
- [ ] HTTPS enforced (production)
- [ ] Data encrypted at rest (DynamoDB)

---

## Edge Cases & Error Handling

- [ ] Empty account list handled gracefully
- [ ] No transactions history shows appropriate message
- [ ] Network errors handled with retry logic
- [ ] DynamoDB throttling handled
- [ ] SNS publish failures logged
- [ ] Invalid session redirects to login
- [ ] Expired session handled gracefully
- [ ] Concurrent balance updates don't cause issues
- [ ] Decimal precision maintained (no rounding errors)
- [ ] Large numbers (> $1M) handled correctly

---

## Test Data Cleanup

After testing:
- [ ] Delete test accounts from DynamoDB
- [ ] Remove test transactions
- [ ] Unsubscribe test emails from SNS
- [ ] Clear test data from logs

```bash
# Scan and delete test data
aws dynamodb scan --table-name BankingUsers \
  --filter-expression "contains(email, :test)" \
  --expression-attribute-values '{":test":{"S":"test"}}'
  
# Delete items (manual or scripted)
```

---

## Testing Results Template

```markdown
## Test Execution Report

**Date:** YYYY-MM-DD
**Tester:** Name
**Environment:** Local / EC2
**Version:** v1.0.0

### Summary
- Total Tests: X
- Passed: Y
- Failed: Z
- Blocked: W

### Failed Tests
1. Test ID: FUNC-001
   Description: Transfer to invalid account
   Expected: Error message
   Actual: Application crash
   Severity: High
   
### Notes
- No critical issues found
- Minor UI improvements needed
- Performance is acceptable
```

---

## Automated Testing (Optional)

If you want to add automated tests:

```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Sign-Off

Tested by: _________________  
Date: _________________  
Approved by: _________________  
Date: _________________  

---

**All tests must pass before production deployment!**
