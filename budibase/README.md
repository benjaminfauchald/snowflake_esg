# Budibase ESG App Setup

This directory contains scripts to set up the SET ESG One Report (Form 56-1) app in Budibase Cloud.

## Prerequisites

1. **Budibase Cloud account** at [budibase.app](https://budibase.app)
2. **Python 3.8+** with `requests` library
3. **API Key** from Budibase (User menu > API keys)

## Quick Start

### Step 1: Create App in Budibase UI

1. Log into [budibase.app](https://budibase.app)
2. Click "Create new app"
3. Name it "ESG One Report" (or your preferred name)
4. Note the **App ID** from the URL: `https://budibase.app/builder/app/app_dev_XXXXX`

### Step 2: Get Your API Key

1. Click your profile icon (top right)
2. Select "API keys"
3. Generate a new key and copy it

### Step 3: Run Setup Script

```bash
# Install requests if needed
pip install requests

# Run the setup script
python setup_esg_app.py \
  --api-key YOUR_API_KEY \
  --app-id app_dev_YOUR_APP_ID
```

This will:
- Create the ESG_METRICS table with all fields
- Insert sample FY2023 data

### Step 4: Build the UI in Budibase

The API can only create data tables. You need to build the UI in Budibase's visual builder:

1. **Dashboard Screen**
   - Add cards for key metrics (GHG emissions, employees, board composition)
   - Add charts for year-over-year trends
   - Use "Chart" component with ESG_METRICS as data source

2. **Data Table Screen**
   - Add Table component linked to ESG_METRICS
   - Enable CRUD actions (Add, Edit, Delete)

3. **Form Screen** (optional)
   - Create detailed forms for E/S/G sections
   - Use form groups for better organization

## Table Schema

The ESG_METRICS table includes all fields from the Thai SET One Report:

| Category | Fields |
|----------|--------|
| **Report Info** | REPORT_YEAR, REPORT_STATUS, SECTOR, SUBMISSION_DEADLINE |
| **Environmental** | GHG Scope 1/2/3, Energy, Water, Waste, Compliance |
| **Social** | Workforce, Diversity, Safety, Training, Community |
| **Governance** | Board composition, Committees, Ethics, Certifications |

## API Reference

Base URL: `https://budibase.app/api/public/v1`

### Headers Required
```
x-budibase-api-key: YOUR_API_KEY
x-budibase-app-id: YOUR_APP_ID
Content-Type: application/json
```

### CRUD Operations

```bash
# Create row
POST /tables/{tableId}/rows

# Get rows
POST /tables/{tableId}/rows/search

# Update row
PUT /tables/{tableId}/rows/{rowId}

# Delete row
DELETE /tables/{tableId}/rows/{rowId}
```

## Comparison: Streamlit vs Budibase

| Feature | Streamlit (Snowflake) | Budibase |
|---------|----------------------|----------|
| Hosting | Snowflake | Cloud or Self-hosted |
| Data | Snowflake tables | Internal DB or External |
| Code | Python | Low-code visual builder |
| Charts | Plotly, Altair | Built-in charts |
| Auth | Snowflake SSO | Built-in or SSO |
| API | Snowpark | REST API |

## Resources

- [Budibase Docs](https://docs.budibase.com/)
- [Public API Reference](https://docs.budibase.com/docs/public-api)
- [OpenAPI Spec](https://raw.githubusercontent.com/Budibase/budibase/master/packages/server/specs/openapi.yaml)
