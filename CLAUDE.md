# ESG Reporting Portal - Project Guide

**Version:** 1.2
**Last Updated:** 2025-12-02
**Status:** IMPLEMENTED

---

## Project Context

This is a Streamlit-in-Snowflake CRUD application for ESG (Environmental, Social, Governance) reporting. Users can authenticate, manage ESG data rows, and download reports for government submission.

### Key Decisions
- **Snowflake Account:** Using existing account
- **CI/CD Auth:** Key-pair authentication
- **Cortex AI:** Enabled (Claude 3.5 Sonnet)
- **Data Scope:** Single organization

---

## Implementation Checklist

### Phase 1: Environment Setup
- [x] Install SnowCLI via Homebrew
- [x] Initialize project structure
- [x] Configure Snowflake connection (key-pair auth)
- [x] Test connection: `snow connection test`

### Phase 2: Snowflake Infrastructure
- [x] Create `setup/01_database.sql` - Database & warehouse
- [x] Create `setup/02_tables.sql` - ESG_METRICS table
- [x] Create `setup/03_sample_data.sql` - Sample records
- [x] Deploy to Snowflake (6 sample records loaded)

### Phase 3: Streamlit Application
- [x] `app/streamlit_app.py` - Main entry point
- [x] `app/pages/1_Dashboard.py` - Metrics visualization
- [x] `app/pages/2_Data_Entry.py` - CRUD operations
- [x] `app/pages/3_Reports.py` - CSV/report download
- [x] `app/pages/4_AI_Insights.py` - Cortex AI integration
- [x] `app/utils/database.py` - DB operations
- [x] `app/utils/export.py` - Export utilities

### Phase 4: CI/CD
- [x] `.github/workflows/deploy.yml` - GitHub Actions pipeline
- [x] `scripts/deploy.sh` - Local deployment script
- [ ] Configure GitHub secrets
- [ ] Generate RSA key pair for CI/CD

### Phase 5: Documentation
- [x] `README.md` - Full documentation
- [x] `CLAUDE.md` - Project guide (this file)

---

## Project Structure

```
snowflake_esg/
├── app/
│   ├── streamlit_app.py      # Main app
│   ├── pages/                # Multi-page app
│   └── utils/                # Helper modules
├── setup/                    # SQL scripts
├── scripts/                  # Deployment scripts
├── .github/workflows/        # CI/CD
├── snowflake.yml            # SnowCLI config
├── requirements.txt         # Dependencies
├── README.md                # User docs
└── CLAUDE.md                # This file
```

---

## Quick Commands

```bash
# Configure connection
snow connection add

# Test connection
snow connection test

# Deploy everything
./scripts/deploy.sh

# Or deploy manually:
snow sql -f setup/01_database.sql
snow sql -f setup/02_tables.sql
snow sql -f setup/03_sample_data.sql
snow streamlit deploy

# Get app URL
snow streamlit get-url esg_app
```

---

## ESG Table Schema

**Table:** `ESG_REPORTING.PROD.ESG_METRICS`

| Category | Columns |
|----------|---------|
| **Identity** | id, organization_name, reporting_year, reporting_date |
| **Environmental** | ghg_scope1_mtco2e, ghg_scope2_mtco2e, energy_consumption_mwh, renewable_energy_pct, water_consumption_m3, waste_generated_tons, waste_recycled_pct |
| **Social** | total_employees, female_employees_pct, employee_turnover_pct, safety_incidents, training_hours_per_employee |
| **Governance** | board_size, board_independence_pct, board_female_pct, has_ethics_policy, has_whistleblower_policy |
| **Metadata** | notes, created_by, created_at, updated_by, updated_at |

---

## CI/CD Setup (Pending)

### GitHub Secrets Required
| Secret | Description |
|--------|-------------|
| `SNOWFLAKE_ACCOUNT` | Account identifier (e.g., `xy12345.us-east-1`) |
| `SNOWFLAKE_USER` | Service account username |
| `SNOWFLAKE_PRIVATE_KEY` | RSA private key contents |

### Generate Key Pair
```bash
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

# Then in Snowflake:
ALTER USER your_user SET RSA_PUBLIC_KEY='<public key content>';
```

---

## Development Notes

- Streamlit runs inside Snowflake (Streamlit-in-Snowflake)
- Uses `snowflake.snowpark.context.get_active_session()` for DB access
- Cortex AI uses `SNOWFLAKE.CORTEX.COMPLETE()` function
- All data stays within Snowflake environment

---

## Live App

**URL:** https://app.snowflake.com/ZLOFVHD/si80049/#/streamlit-apps/ESG_REPORTING.PROD.ESG_APP

## Next Steps

1. ~~Run `snow connection add` to configure Snowflake credentials~~ ✅
2. ~~Run `./scripts/deploy.sh` to deploy the app~~ ✅
3. Set up GitHub secrets for CI/CD (optional)
4. Add more ESG data through the Data Entry page
