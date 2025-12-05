#!/usr/bin/env python3
"""
Budibase ESG App Setup Script
Creates the SET ESG One Report (Form 56-1) data structure via Budibase Public API

Usage:
    1. Get your API key from Budibase Cloud (User menu > API keys)
    2. Create a new app in Budibase UI first (API can't create apps)
    3. Get the App ID from the URL (after /builder/app/)
    4. Run: python setup_esg_app.py --api-key YOUR_KEY --app-id YOUR_APP_ID
"""

import requests
import json
import argparse
from datetime import date

# Budibase Cloud API base URL
API_BASE = "https://budibase.app/api/public/v1"

# ESG Metrics table schema matching Snowflake structure
ESG_METRICS_SCHEMA = {
    "name": "ESG_METRICS",
    "primaryDisplay": "REPORT_YEAR",
    "schema": {
        # Report Info
        "REPORT_YEAR": {
            "name": "REPORT_YEAR",
            "type": "number",
            "constraints": {"presence": True}
        },
        "REPORT_STATUS": {
            "name": "REPORT_STATUS",
            "type": "options",
            "constraints": {
                "inclusion": ["Draft", "In Review", "Submitted to SET", "Approved"]
            }
        },
        "SECTOR": {
            "name": "SECTOR",
            "type": "options",
            "constraints": {
                "inclusion": ["Technology", "Services", "Industrial", "Property & Construction",
                             "Resources", "Consumer Products", "Agro & Food", "Financials"]
            }
        },
        "SUBMISSION_DEADLINE": {
            "name": "SUBMISSION_DEADLINE",
            "type": "datetime"
        },

        # Environmental - Climate & GHG
        "GHG_SCOPE1_TCO2E": {
            "name": "GHG_SCOPE1_TCO2E",
            "type": "number"
        },
        "GHG_SCOPE2_TCO2E": {
            "name": "GHG_SCOPE2_TCO2E",
            "type": "number"
        },
        "GHG_SCOPE3_TCO2E": {
            "name": "GHG_SCOPE3_TCO2E",
            "type": "number"
        },
        "GHG_REDUCTION_TARGET_PCT": {
            "name": "GHG_REDUCTION_TARGET_PCT",
            "type": "number"
        },
        "GHG_REDUCTION_ACHIEVED_PCT": {
            "name": "GHG_REDUCTION_ACHIEVED_PCT",
            "type": "number"
        },

        # Environmental - Energy
        "ENERGY_TOTAL_MWH": {
            "name": "ENERGY_TOTAL_MWH",
            "type": "number"
        },
        "ENERGY_RENEWABLE_MWH": {
            "name": "ENERGY_RENEWABLE_MWH",
            "type": "number"
        },
        "ENERGY_INTENSITY": {
            "name": "ENERGY_INTENSITY",
            "type": "number"
        },
        "SOLAR_INSTALLED_KW": {
            "name": "SOLAR_INSTALLED_KW",
            "type": "number"
        },

        # Environmental - Water & Waste
        "WATER_CONSUMPTION_M3": {
            "name": "WATER_CONSUMPTION_M3",
            "type": "number"
        },
        "WATER_RECYCLED_PCT": {
            "name": "WATER_RECYCLED_PCT",
            "type": "number"
        },
        "WASTE_TOTAL_TONS": {
            "name": "WASTE_TOTAL_TONS",
            "type": "number"
        },
        "WASTE_RECYCLED_PCT": {
            "name": "WASTE_RECYCLED_PCT",
            "type": "number"
        },
        "HAZARDOUS_WASTE_TONS": {
            "name": "HAZARDOUS_WASTE_TONS",
            "type": "number"
        },
        "ZERO_WASTE_TO_LANDFILL": {
            "name": "ZERO_WASTE_TO_LANDFILL",
            "type": "boolean"
        },

        # Environmental - Compliance
        "ENV_VIOLATIONS": {
            "name": "ENV_VIOLATIONS",
            "type": "number"
        },
        "ENV_FINES_THB": {
            "name": "ENV_FINES_THB",
            "type": "number"
        },

        # Social - Workforce
        "EMPLOYEES_TOTAL": {
            "name": "EMPLOYEES_TOTAL",
            "type": "number"
        },
        "EMPLOYEES_PERMANENT": {
            "name": "EMPLOYEES_PERMANENT",
            "type": "number"
        },
        "EMPLOYEES_CONTRACT": {
            "name": "EMPLOYEES_CONTRACT",
            "type": "number"
        },
        "NEW_HIRES": {
            "name": "NEW_HIRES",
            "type": "number"
        },
        "TURNOVER_RATE_PCT": {
            "name": "TURNOVER_RATE_PCT",
            "type": "number"
        },

        # Social - Diversity
        "WOMEN_WORKFORCE_PCT": {
            "name": "WOMEN_WORKFORCE_PCT",
            "type": "number"
        },
        "WOMEN_MANAGEMENT_PCT": {
            "name": "WOMEN_MANAGEMENT_PCT",
            "type": "number"
        },
        "WOMEN_EXECUTIVE_PCT": {
            "name": "WOMEN_EXECUTIVE_PCT",
            "type": "number"
        },
        "DISABLED_EMPLOYEES": {
            "name": "DISABLED_EMPLOYEES",
            "type": "number"
        },
        "LOCAL_EMPLOYMENT_PCT": {
            "name": "LOCAL_EMPLOYMENT_PCT",
            "type": "number"
        },

        # Social - Compensation
        "MIN_WAGE_COMPLIANCE": {
            "name": "MIN_WAGE_COMPLIANCE",
            "type": "boolean"
        },
        "AVG_SALARY_THB": {
            "name": "AVG_SALARY_THB",
            "type": "number"
        },
        "BENEFITS_BEYOND_LEGAL": {
            "name": "BENEFITS_BEYOND_LEGAL",
            "type": "boolean"
        },
        "PROVIDENT_FUND_PCT": {
            "name": "PROVIDENT_FUND_PCT",
            "type": "number"
        },

        # Social - Health & Safety
        "LOST_TIME_INJURIES": {
            "name": "LOST_TIME_INJURIES",
            "type": "number"
        },
        "INJURY_RATE": {
            "name": "INJURY_RATE",
            "type": "number"
        },
        "FATALITIES": {
            "name": "FATALITIES",
            "type": "number"
        },
        "SAFETY_TRAINING_HOURS": {
            "name": "SAFETY_TRAINING_HOURS",
            "type": "number"
        },
        "SAFETY_COMMITTEE": {
            "name": "SAFETY_COMMITTEE",
            "type": "boolean"
        },

        # Social - Training
        "TRAINING_HOURS_AVG": {
            "name": "TRAINING_HOURS_AVG",
            "type": "number"
        },
        "TRAINING_BUDGET_THB": {
            "name": "TRAINING_BUDGET_THB",
            "type": "number"
        },
        "CAREER_DEVELOPMENT_PROGRAM": {
            "name": "CAREER_DEVELOPMENT_PROGRAM",
            "type": "boolean"
        },

        # Social - Community & Supply Chain
        "CSR_BUDGET_THB": {
            "name": "CSR_BUDGET_THB",
            "type": "number"
        },
        "COMMUNITY_PROJECTS": {
            "name": "COMMUNITY_PROJECTS",
            "type": "number"
        },
        "LOCAL_SUPPLIER_PCT": {
            "name": "LOCAL_SUPPLIER_PCT",
            "type": "number"
        },
        "SUPPLIER_CODE_OF_CONDUCT": {
            "name": "SUPPLIER_CODE_OF_CONDUCT",
            "type": "boolean"
        },
        "SUPPLIER_ESG_ASSESSMENT": {
            "name": "SUPPLIER_ESG_ASSESSMENT",
            "type": "boolean"
        },

        # Governance - Board
        "BOARD_TOTAL": {
            "name": "BOARD_TOTAL",
            "type": "number"
        },
        "BOARD_INDEPENDENT_PCT": {
            "name": "BOARD_INDEPENDENT_PCT",
            "type": "number"
        },
        "BOARD_WOMEN_PCT": {
            "name": "BOARD_WOMEN_PCT",
            "type": "number"
        },
        "BOARD_MEETINGS_YEAR": {
            "name": "BOARD_MEETINGS_YEAR",
            "type": "number"
        },
        "BOARD_ATTENDANCE_PCT": {
            "name": "BOARD_ATTENDANCE_PCT",
            "type": "number"
        },

        # Governance - Committees
        "HAS_AUDIT_COMMITTEE": {
            "name": "HAS_AUDIT_COMMITTEE",
            "type": "boolean"
        },
        "HAS_RISK_COMMITTEE": {
            "name": "HAS_RISK_COMMITTEE",
            "type": "boolean"
        },
        "HAS_CG_COMMITTEE": {
            "name": "HAS_CG_COMMITTEE",
            "type": "boolean"
        },
        "HAS_SUSTAINABILITY_COMMITTEE": {
            "name": "HAS_SUSTAINABILITY_COMMITTEE",
            "type": "boolean"
        },

        # Governance - Ethics
        "CODE_OF_CONDUCT": {
            "name": "CODE_OF_CONDUCT",
            "type": "boolean"
        },
        "ANTI_CORRUPTION_POLICY": {
            "name": "ANTI_CORRUPTION_POLICY",
            "type": "boolean"
        },
        "WHISTLEBLOWER_POLICY": {
            "name": "WHISTLEBLOWER_POLICY",
            "type": "boolean"
        },
        "ETHICS_TRAINING_PCT": {
            "name": "ETHICS_TRAINING_PCT",
            "type": "number"
        },
        "CORRUPTION_CASES": {
            "name": "CORRUPTION_CASES",
            "type": "number"
        },

        # Governance - Certifications
        "CGR_SCORE": {
            "name": "CGR_SCORE",
            "type": "options",
            "constraints": {
                "inclusion": ["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"]
            }
        },
        "ISO14001_CERTIFIED": {
            "name": "ISO14001_CERTIFIED",
            "type": "boolean"
        },
        "ISO45001_CERTIFIED": {
            "name": "ISO45001_CERTIFIED",
            "type": "boolean"
        },
        "SET_ESG_RATING": {
            "name": "SET_ESG_RATING",
            "type": "boolean"
        },
        "THSI_MEMBER": {
            "name": "THSI_MEMBER",
            "type": "boolean"
        },

        # Data Quality
        "EXTERNAL_ASSURANCE": {
            "name": "EXTERNAL_ASSURANCE",
            "type": "boolean"
        },
        "ASSURANCE_PROVIDER": {
            "name": "ASSURANCE_PROVIDER",
            "type": "string"
        },

        # Metadata
        "NOTES": {
            "name": "NOTES",
            "type": "longform"
        }
    }
}

# Sample data matching Snowflake insert
SAMPLE_DATA = {
    "REPORT_YEAR": 2023,
    "REPORT_STATUS": "Submitted to SET",
    "SECTOR": "Technology",
    "SUBMISSION_DEADLINE": "2024-04-30",

    # Environmental
    "GHG_SCOPE1_TCO2E": 8500,
    "GHG_SCOPE2_TCO2E": 4200,
    "GHG_SCOPE3_TCO2E": 45000,
    "GHG_REDUCTION_TARGET_PCT": 15,
    "GHG_REDUCTION_ACHIEVED_PCT": 12,
    "ENERGY_TOTAL_MWH": 25000,
    "ENERGY_RENEWABLE_MWH": 8750,
    "SOLAR_INSTALLED_KW": 500,
    "WATER_CONSUMPTION_M3": 180000,
    "WATER_RECYCLED_PCT": 35,
    "WASTE_TOTAL_TONS": 450,
    "WASTE_RECYCLED_PCT": 75,
    "HAZARDOUS_WASTE_TONS": 12,
    "ZERO_WASTE_TO_LANDFILL": False,
    "ENV_VIOLATIONS": 0,
    "ENV_FINES_THB": 0,

    # Social
    "EMPLOYEES_TOTAL": 1850,
    "EMPLOYEES_PERMANENT": 1650,
    "EMPLOYEES_CONTRACT": 200,
    "NEW_HIRES": 280,
    "TURNOVER_RATE_PCT": 8.5,
    "WOMEN_WORKFORCE_PCT": 45,
    "WOMEN_MANAGEMENT_PCT": 38,
    "WOMEN_EXECUTIVE_PCT": 25,
    "DISABLED_EMPLOYEES": 28,
    "LOCAL_EMPLOYMENT_PCT": 85,
    "MIN_WAGE_COMPLIANCE": True,
    "AVG_SALARY_THB": 45000,
    "BENEFITS_BEYOND_LEGAL": True,
    "PROVIDENT_FUND_PCT": 5,
    "LOST_TIME_INJURIES": 3,
    "INJURY_RATE": 0.42,
    "FATALITIES": 0,
    "SAFETY_TRAINING_HOURS": 5200,
    "SAFETY_COMMITTEE": True,
    "TRAINING_HOURS_AVG": 28,
    "TRAINING_BUDGET_THB": 2800000,
    "CAREER_DEVELOPMENT_PROGRAM": True,
    "CSR_BUDGET_THB": 5500000,
    "COMMUNITY_PROJECTS": 12,
    "LOCAL_SUPPLIER_PCT": 72,
    "SUPPLIER_CODE_OF_CONDUCT": True,
    "SUPPLIER_ESG_ASSESSMENT": True,

    # Governance
    "BOARD_TOTAL": 11,
    "BOARD_INDEPENDENT_PCT": 45,
    "BOARD_WOMEN_PCT": 27,
    "BOARD_MEETINGS_YEAR": 12,
    "BOARD_ATTENDANCE_PCT": 95,
    "HAS_AUDIT_COMMITTEE": True,
    "HAS_RISK_COMMITTEE": True,
    "HAS_CG_COMMITTEE": True,
    "HAS_SUSTAINABILITY_COMMITTEE": True,
    "CODE_OF_CONDUCT": True,
    "ANTI_CORRUPTION_POLICY": True,
    "WHISTLEBLOWER_POLICY": True,
    "ETHICS_TRAINING_PCT": 98,
    "CORRUPTION_CASES": 0,
    "CGR_SCORE": "4 Stars",
    "ISO14001_CERTIFIED": True,
    "ISO45001_CERTIFIED": True,
    "SET_ESG_RATING": True,
    "THSI_MEMBER": True,
    "EXTERNAL_ASSURANCE": True,
    "ASSURANCE_PROVIDER": "KPMG Thailand",
    "NOTES": "FY2023 One Report - Submitted to SET April 2024"
}


class BudibaseAPI:
    def __init__(self, api_key: str, app_id: str):
        self.api_key = api_key
        self.app_id = app_id
        self.headers = {
            "x-budibase-api-key": api_key,
            "x-budibase-app-id": app_id,
            "Content-Type": "application/json"
        }

    def create_table(self, schema: dict) -> dict:
        """Create a table with the given schema"""
        url = f"{API_BASE}/tables"
        response = requests.post(url, headers=self.headers, json=schema)
        response.raise_for_status()
        return response.json()

    def get_tables(self) -> dict:
        """List all tables in the app"""
        url = f"{API_BASE}/tables/search"
        response = requests.post(url, headers=self.headers, json={})
        response.raise_for_status()
        return response.json()

    def create_row(self, table_id: str, data: dict) -> dict:
        """Create a row in the specified table"""
        url = f"{API_BASE}/tables/{table_id}/rows"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_rows(self, table_id: str) -> dict:
        """Get all rows from a table"""
        url = f"{API_BASE}/tables/{table_id}/rows/search"
        response = requests.post(url, headers=self.headers, json={})
        response.raise_for_status()
        return response.json()

    def update_row(self, table_id: str, row_id: str, data: dict) -> dict:
        """Update a row"""
        url = f"{API_BASE}/tables/{table_id}/rows/{row_id}"
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def delete_row(self, table_id: str, row_id: str) -> dict:
        """Delete a row"""
        url = f"{API_BASE}/tables/{table_id}/rows/{row_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return response.json()


def main():
    parser = argparse.ArgumentParser(description="Set up ESG app in Budibase")
    parser.add_argument("--api-key", required=True, help="Your Budibase API key")
    parser.add_argument("--app-id", required=True, help="Your Budibase App ID (from URL)")
    parser.add_argument("--skip-sample-data", action="store_true", help="Skip inserting sample data")
    args = parser.parse_args()

    api = BudibaseAPI(args.api_key, args.app_id)

    print("=" * 60)
    print("SET ESG One Report (Form 56-1) - Budibase Setup")
    print("=" * 60)

    # Step 1: Create ESG_METRICS table
    print("\n[1/3] Creating ESG_METRICS table...")
    try:
        result = api.create_table(ESG_METRICS_SCHEMA)
        table_id = result["data"]["_id"]
        print(f"    Table created: {table_id}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print("    Table may already exist, searching...")
            tables = api.get_tables()
            for t in tables.get("data", []):
                if t["name"] == "ESG_METRICS":
                    table_id = t["_id"]
                    print(f"    Found existing table: {table_id}")
                    break
            else:
                raise Exception("Could not find or create ESG_METRICS table")
        else:
            raise

    # Step 2: Insert sample data
    if not args.skip_sample_data:
        print("\n[2/3] Inserting sample data (FY2023)...")
        try:
            row = api.create_row(table_id, SAMPLE_DATA)
            print(f"    Row created: {row['data']['_id']}")
        except requests.exceptions.HTTPError as e:
            print(f"    Warning: Could not insert sample data: {e}")
    else:
        print("\n[2/3] Skipping sample data (--skip-sample-data)")

    # Step 3: Summary
    print("\n[3/3] Setup complete!")
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("""
1. Open your Budibase app in the browser
2. Go to Design tab to create screens:
   - Dashboard screen with metrics/charts
   - Data table screen with ESG_METRICS
   - Form screen for adding/editing records
3. Recommended screen layout:
   - Use tabs for E (Environmental), S (Social), G (Governance)
   - Add charts for key metrics (GHG emissions, workforce diversity, etc.)
   - Add export button for CSV download

Table ID: {table_id}
    """.format(table_id=table_id))

    # Print API examples for reference
    print("\n" + "=" * 60)
    print("API EXAMPLES (for reference):")
    print("=" * 60)
    print(f"""
# Create row:
curl -X POST "{API_BASE}/tables/{table_id}/rows" \\
  -H "x-budibase-api-key: {args.api_key[:8]}..." \\
  -H "x-budibase-app-id: {args.app_id}" \\
  -H "Content-Type: application/json" \\
  -d '{{"REPORT_YEAR": 2024, "REPORT_STATUS": "Draft", ...}}'

# Get all rows:
curl -X POST "{API_BASE}/tables/{table_id}/rows/search" \\
  -H "x-budibase-api-key: {args.api_key[:8]}..." \\
  -H "x-budibase-app-id: {args.app_id}" \\
  -H "Content-Type: application/json" \\
  -d '{{}}'
    """)


if __name__ == "__main__":
    main()
