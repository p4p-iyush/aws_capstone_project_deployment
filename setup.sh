#!/bin/bash
# Banking System Setup Script
# This script helps you get started quickly

set -e

echo "=============================================="
echo "Banking System - Setup Script"
echo "=============================================="
echo ""

# Check Python version
echo "1. Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "2. Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "3. Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "4. Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file
echo "5. Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo "⚠️  IMPORTANT: Edit .env file with your AWS credentials!"
else
    echo "✓ .env file already exists"
fi
echo ""

# Check AWS credentials
echo "6. Checking AWS configuration..."
if command -v aws &> /dev/null; then
    if aws sts get-caller-identity &> /dev/null; then
        echo "✓ AWS CLI configured and working"
        AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
        AWS_REGION=$(aws configure get region)
        echo "  Account: $AWS_ACCOUNT"
        echo "  Region: $AWS_REGION"
    else
        echo "⚠️  AWS CLI not configured. Run: aws configure"
    fi
else
    echo "⚠️  AWS CLI not installed. Install from: https://aws.amazon.com/cli/"
fi
echo ""

echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Next Steps:"
echo ""
echo "1. Configure AWS (if not done):"
echo "   aws configure"
echo ""
echo "2. Edit .env file with your settings:"
echo "   nano .env"
echo ""
echo "3. Create DynamoDB tables:"
echo "   python3 aws/dynamodb_setup.py"
echo ""
echo "4. Setup SNS notifications:"
echo "   python3 aws/sns_setup.py"
echo ""
echo "5. Run the application:"
echo "   python3 run.py"
echo ""
echo "6. Open browser:"
echo "   http://localhost:5000"
echo ""
echo "For detailed instructions, see: START_HERE.md"
echo "=============================================="
