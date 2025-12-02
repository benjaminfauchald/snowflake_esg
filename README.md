# ESG Reporting Portal

A Streamlit-in-Snowflake application for managing Environmental, Social, and Governance (ESG) reporting data with AI-powered insights using Snowflake Cortex.

## Features

- **Dashboard**: Visualize ESG metrics with interactive charts and trends
- **Data Entry**: Full CRUD operations (Create, Read, Update, Delete) for ESG records
- **Reports**: Download ESG data as CSV or formatted government reports
- **AI Insights**: Get AI-powered analysis using Snowflake Cortex (Claude 3.5 Sonnet)

## Prerequisites

- Snowflake account with Streamlit enabled
- Snowflake CLI (SnowCLI) installed
- Python 3.10+ (for local development)

## Quick Start

### 1. Install Snowflake CLI

```bash
# macOS
brew tap snowflakedb/snowflake-cli
brew install snowflake-cli

# Verify installation
snow --version
```

### 2. Configure Connection

```bash
# Add a new connection
snow connection add

# Or set environment variables
export SNOWFLAKE_CONNECTIONS_DEFAULT_ACCOUNT=<your-account>
export SNOWFLAKE_CONNECTIONS_DEFAULT_USER=<your-user>
export SNOWFLAKE_CONNECTIONS_DEFAULT_PASSWORD=<your-password>

# Test connection
snow connection test
```

### 3. Deploy

```bash
# Run the deployment script
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

Or deploy manually:

```bash
# Create database and tables
snow sql -f setup/01_database.sql
snow sql -f setup/02_tables.sql

# Load sample data (optional)
snow sql -f setup/03_sample_data.sql

# Deploy Streamlit app
snow streamlit deploy
```

### 4. Access the App

1. Open Snowflake UI
2. Navigate to Streamlit in the left sidebar
3. Find "ESG Reporting Portal"
4. Click to launch

## Project Structure

```
snowflake_esg/
├── app/
│   ├── streamlit_app.py      # Main application
│   ├── pages/
│   │   ├── 1_Dashboard.py    # Metrics dashboard
│   │   ├── 2_Data_Entry.py   # CRUD operations
│   │   ├── 3_Reports.py      # Export & download
│   │   └── 4_AI_Insights.py  # Cortex AI integration
│   └── utils/
│       ├── database.py       # Database operations
│       └── export.py         # Export utilities
├── setup/
│   ├── 01_database.sql       # Database & schema creation
│   ├── 02_tables.sql         # Table definitions
│   └── 03_sample_data.sql    # Sample ESG data
├── scripts/
│   └── deploy.sh             # Deployment script
├── .github/
│   └── workflows/
│       └── deploy.yml        # CI/CD pipeline
├── snowflake.yml             # Snowflake project config
├── requirements.txt          # Python dependencies
└── README.md
```

## ESG Metrics Schema

The application tracks comprehensive ESG metrics:

### Environmental
- GHG Emissions (Scope 1 & 2)
- Energy consumption
- Renewable energy percentage
- Water consumption
- Waste generated & recycled

### Social
- Total employees
- Gender diversity
- Employee turnover
- Safety incidents
- Training hours

### Governance
- Board size & composition
- Board independence
- Gender diversity on board
- Ethics & whistleblower policies

## CI/CD Setup

### GitHub Actions

The project includes a CI/CD pipeline that:
1. Validates configuration files
2. Deploys database infrastructure
3. Deploys Streamlit application
4. Loads sample data (if empty)

### Required Secrets

Add these secrets to your GitHub repository:

| Secret | Description |
|--------|-------------|
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier (e.g., `xy12345.us-east-1`) |
| `SNOWFLAKE_USER` | Service account username |
| `SNOWFLAKE_PRIVATE_KEY` | RSA private key for authentication |

### Generate Key Pair

```bash
# Generate private key
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt

# Generate public key
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

# Register public key in Snowflake
# ALTER USER your_user SET RSA_PUBLIC_KEY='<contents of rsa_key.pub>';
```

## Cortex AI Features

The AI Insights page provides:

- **Natural Language Queries**: Ask questions about your ESG data
- **Data Validation**: AI-powered anomaly detection
- **Report Summaries**: Auto-generate executive summaries

Powered by Snowflake Cortex with Claude 3.5 Sonnet.

## Development

### Local Testing

Streamlit-in-Snowflake apps run in the Snowflake environment. For local development:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Note: Full functionality requires Snowflake connection
```

### Modifying the App

1. Edit files in the `app/` directory
2. Test changes locally if possible
3. Deploy with `snow streamlit deploy --replace`

## License

MIT License

## Support

For issues or questions:
1. Check Snowflake documentation
2. Review SnowCLI documentation
3. Open an issue in this repository
