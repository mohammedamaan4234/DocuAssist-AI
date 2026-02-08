"""Sample data initialization script for DocuAssist AI."""

import json
from app.rag.vector_store import VectorStore
from app.config import settings
from app.utils.logger import logger

# Sample documents representing a typical software company knowledge base
SAMPLE_DOCUMENTS = [
    {
        "id": "password_reset",
        "text": """How to Reset Your Password

If you've forgotten your password, follow these steps to reset it:

1. Go to the login page of our application
2. Below the password field, click "Forgot Password?"
3. Enter the email address associated with your account
4. Check your email inbox for a message from our support team
5. Click the reset link in the email (link expires in 24 hours)
6. Create a new password (must be at least 8 characters, with uppercase, lowercase, and number)
7. Confirm your new password
8. You'll be redirected to login - use your new password

If you don't receive the email within 5 minutes, check your spam folder or contact support.""",
        "metadata": {"source": "help_docs", "category": "account", "priority": "high"}
    },
    {
        "id": "account_creation",
        "text": """Creating a New Account

Getting started is easy! Here's how to create your account:

1. Visit our website and click "Sign Up"
2. Enter your email address
3. Create a strong password (minimum 8 characters)
4. Select your organization type (individual, startup, enterprise)
5. Accept our Terms of Service and Privacy Policy
6. Click "Create Account"
7. Verify your email by clicking the link we send you
8. Complete your profile with your name and preferences
9. Start using the platform!

Your account includes:
- 30-day free trial with full features
- Community support access
- Basic analytics dashboard

For enterprise plans, contact sales@company.com""",
        "metadata": {"source": "help_docs", "category": "account"}
    },
    {
        "id": "billing_faq",
        "text": """Billing and Payment FAQ

How much does it cost?
Our pricing is transparent and based on usage:
- Starter: $29/month (up to 100 users)
- Professional: $99/month (up to 500 users)
- Enterprise: Custom pricing (unlimited users)

Can I change my plan?
Yes, you can upgrade or downgrade your plan at any time. Changes take effect at your next billing cycle.

What payment methods do you accept?
We accept all major credit cards (Visa, Mastercard, American Express) and bank transfers for enterprise customers.

Do you offer annual billing?
Yes! Annual plans receive a 20% discount. You can pay annually at account.company.com/billing.

What's your refund policy?
We offer a 30-day money-back guarantee. If you're not satisfied within 30 days, we'll refund your payment in full. Please contact support@company.com.

Can I get an invoice?
Yes, invoices are automatically generated and available in your account dashboard. You can download them anytime.

What happens if I exceed usage limits?
We'll notify you before overage charges apply. You can upgrade your plan or set usage alerts.""",
        "metadata": {"source": "help_docs", "category": "billing"}
    },
    {
        "id": "contact_support",
        "text": """How to Contact Support

We're here to help! Here are the ways you can reach our support team:

Email Support
Email: support@company.com
Response time: Within 24 hours (business days)
Best for: Complex issues, detailed questions

Live Chat
Available: Monday-Friday, 9 AM - 5 PM EST
On website: Click the chat bubble in bottom right
Best for: Quick answers, account issues

Help Center
Visit: help.company.com
Thousands of articles and FAQs
Search for answers anytime

Community Forum
Join: community.company.com
Get help from other users
Share tips and best practices

Phone Support
Included with: Enterprise plans
Number: 1-800-COMPANY
Hours: Monday-Friday, 9 AM - 6 PM EST

Bug Reports
Found a bug? Report it at: bugs.company.com
Include: Steps to reproduce, browser/OS, screenshots

Feature Requests
Suggest features: feedback.company.com
Vote on community requests
Direct input on product roadmap

Premium Support (Enterprise)
- Priority response (<1 hour)
- Dedicated account manager
- Custom SLAs
- Training sessions

Response Time Guidelines
- Critical issues: 1 hour
- High priority: 4 hours
- Medium priority: 24 hours
- Low priority: 48 hours""",
        "metadata": {"source": "help_docs", "category": "support"}
    },
    {
        "id": "two_factor_auth",
        "text": """Setting Up Two-Factor Authentication (2FA)

Two-factor authentication adds an extra layer of security to your account.

Why Enable 2FA?
- Prevents unauthorized access even if password is compromised
- Protects sensitive data and account information
- Required for enterprise customers

How to Enable 2FA:

1. Go to Settings > Security
2. Click "Enable Two-Factor Authentication"
3. Choose your authenticator method:
   a) Authenticator App (Google Authenticator, Authy, etc.)
   b) SMS Text Message
   c) Email Code
4. Scan the QR code with your authenticator app
5. Enter the 6-digit code shown in your app
6. Save backup codes in a secure location
7. Confirm setup

Using 2FA:
- When you log in, you'll be prompted for a verification code
- Use your configured method (app, SMS, or email)
- Enter the code to complete login
- The code changes every 30 seconds

Backup Codes:
- Provided when enabling 2FA
- Use these if you lose access to your authenticator
- Each code can only be used once
- Store in a safe place (password manager)

Disabling 2FA:
- Go to Settings > Security
- Click "Disable Two-Factor Authentication"
- Confirm your password
- Confirm with a verification code

Troubleshooting:
- Lost authenticator app? Use backup codes
- Not receiving SMS? Check spam folder
- Time sync issue? Sync your device time""",
        "metadata": {"source": "help_docs", "category": "security"}
    },
    {
        "id": "data_export",
        "text": """Exporting Your Data

You own your data. Here's how to export it:

Available Export Formats:
- CSV (spreadsheets)
- JSON (structured data)
- PDF (reports)
- XML (system integration)

What Can You Export?
- User analytics and reports
- Transaction history
- Settings and configurations
- Account activity logs
- Custom data fields

How to Export Data:

1. Go to Settings > Data & Privacy
2. Select export format and type
3. Choose date range (if applicable)
4. Click "Prepare Export"
5. You'll receive email with download link
6. Download your data (available for 7 days)

Schedule Automated Exports:
- Premium feature
- Set up weekly, monthly, or quarterly exports
- Files delivered to your email
- Archive exports for backup

Data Privacy:
- Exports are encrypted during transmission
- Download links expire after 7 days
- We don't retain export files longer than 30 days
- Ensure downloaded files are securely stored

Delete Your Data:
- All data deleted immediately upon account termination
- No recovery possible after deletion
- Backup your data before account deletion
- 30-day grace period to recover account

Compliance:
- GDPR compliant
- CCPA compliant
- HIPAA eligible (Enterprise)
- SOC 2 Type II certified""",
        "metadata": {"source": "help_docs", "category": "data"}
    },
    {
        "id": "api_integration",
        "text": """API Integration Guide

Integrate DocuAssist into your applications using our REST API.

API Endpoints:
- Base URL: https://api.company.com/v1
- Authentication: API Key (header: X-API-Key)
- Rate Limit: 1000 requests per hour

Common Endpoints:

GET /users - List users in your account
GET /users/{id} - Get specific user
POST /users - Create new user
PUT /users/{id} - Update user
DELETE /users/{id} - Delete user

GET /analytics - Get analytics data
GET /analytics/{metric} - Get specific metric
POST /analytics/custom - Create custom report

Error Handling:
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (invalid API key)
- 429: Rate limited (exceeded request limit)
- 500: Server error (try again later)

Example: Get User Data
```
curl -X GET https://api.company.com/v1/users/123
  -H "X-API-Key: your-api-key"
  -H "Content-Type: application/json"
```

Response:
```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "plan": "professional"
}
```

Webhooks:
- Receive real-time updates
- Set up at: account.company.com/webhooks
- Events: user.created, user.updated, payment.received

SDK Support:
- JavaScript/Node.js
- Python
- Ruby
- Go
- Java

All SDKs available at: github.com/company/sdks""",
        "metadata": {"source": "help_docs", "category": "developers"}
    },
    {
        "id": "mobile_app",
        "text": """Using the Mobile App

Access your account on the go with our mobile app.

Supported Platforms:
- iOS 14+
- Android 10+

Features:
- Real-time notifications
- Offline access to key features
- Biometric login (fingerprint, face)
- Mobile-optimized interface
- Quick actions

Download:
- App Store: Search "Company"
- Google Play: Search "Company"
- Free with any account tier

First Launch:
1. Install from App Store or Google Play
2. Open the app
3. Sign in with your credentials
4. Enable notifications (optional)
5. Grant required permissions
6. Customize dashboard

Offline Features:
- View saved documents
- Check previous analytics
- Read cached reports
- Note: Some features require internet connection

Security:
- Automatic logout after 5 minutes
- Biometric authentication
- Local data encryption
- Optional PIN lock
- Session management in settings

Troubleshooting:
- App won't open? Force close and restart
- Login issues? Clear app cache
- Sync problems? Check internet connection
- Notifications not working? Check settings

Support:
- In-app help: Settings > Get Help
- Email: mobile-support@company.com
- Rate this app to help us improve""",
        "metadata": {"source": "help_docs", "category": "mobile"}
    }
]


def initialize_sample_data():
    """Initialize vector store with sample documents."""
    try:
        logger.info("Initializing sample documents...")
        vector_store = VectorStore()
        
        # Add documents to vector store
        count = vector_store.add_documents(SAMPLE_DOCUMENTS)
        
        logger.info(f"Successfully initialized {count} sample documents")
        print(f"\n✅ Successfully indexed {count} sample documents!")
        print("\nSample documents include:")
        for doc in SAMPLE_DOCUMENTS:
            print(f"  • {doc['id']}: {doc['metadata']['category']}")
        
        # Check health
        health = vector_store.health_check()
        print(f"\n📊 Vector Store Status:")
        print(f"  Status: {health['status']}")
        print(f"  Total Vectors: {health['total_vectors']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize sample data: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("DocuAssist AI - Sample Data Initialization")
    print("=" * 50)
    initialize_sample_data()
