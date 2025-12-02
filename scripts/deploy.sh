#!/bin/bash

# ESG Reporting Portal - Local Deployment Script
# This script deploys the ESG application to Snowflake

set -e

echo "=========================================="
echo "ESG Reporting Portal - Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if snow CLI is installed
if ! command -v snow &> /dev/null; then
    echo -e "${RED}Error: Snowflake CLI (snow) is not installed.${NC}"
    echo "Install it with: brew install snowflake-cli"
    exit 1
fi

echo -e "${GREEN}✓ Snowflake CLI found${NC}"

# Test connection
echo ""
echo "Testing Snowflake connection..."
if snow connection test; then
    echo -e "${GREEN}✓ Connection successful${NC}"
else
    echo -e "${RED}✗ Connection failed${NC}"
    echo ""
    echo "Please configure your connection:"
    echo "  snow connection add"
    echo ""
    echo "Or set environment variables:"
    echo "  export SNOWFLAKE_CONNECTIONS_DEFAULT_ACCOUNT=<your-account>"
    echo "  export SNOWFLAKE_CONNECTIONS_DEFAULT_USER=<your-user>"
    exit 1
fi

# Deploy infrastructure
echo ""
echo "=========================================="
echo "Step 1: Deploying Database Infrastructure"
echo "=========================================="

echo "Creating database and schemas..."
snow sql -f setup/01_database.sql
echo -e "${GREEN}✓ Database created${NC}"

echo ""
echo "Creating tables..."
snow sql -f setup/02_tables.sql
echo -e "${GREEN}✓ Tables created${NC}"

# Check for existing data
echo ""
echo "Checking for existing data..."
count=$(snow sql -q "SELECT COUNT(*) as cnt FROM ESG_REPORTING.PROD.ESG_METRICS" --format json 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); print(data[0]['CNT'] if data else 0)" 2>/dev/null || echo "0")

if [ "$count" -eq "0" ]; then
    echo "No existing data found. Loading sample data..."
    snow sql -f setup/03_sample_data.sql
    echo -e "${GREEN}✓ Sample data loaded${NC}"
else
    echo -e "${YELLOW}! Data already exists ($count records). Skipping sample data load.${NC}"
fi

# Deploy Streamlit app
echo ""
echo "=========================================="
echo "Step 2: Deploying Streamlit Application"
echo "=========================================="

echo "Deploying app..."
snow streamlit deploy --replace
echo -e "${GREEN}✓ Streamlit app deployed${NC}"

# Get app URL
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Getting app URL..."
snow streamlit get-url esg_app 2>/dev/null || echo -e "${YELLOW}App URL available in Snowflake Streamlit UI${NC}"

echo ""
echo -e "${GREEN}✓ Deployment successful!${NC}"
echo ""
echo "Next steps:"
echo "1. Open the Snowflake UI and navigate to Streamlit"
echo "2. Find 'ESG Reporting Portal' in your apps"
echo "3. Click to launch the application"
echo ""
