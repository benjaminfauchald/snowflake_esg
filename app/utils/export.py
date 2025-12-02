"""
Export utilities for ESG Reporting application.
Handles report generation and file exports.
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
from io import BytesIO
from typing import Optional


def get_session():
    """Get the active Snowpark session."""
    return get_active_session()


def export_to_csv(df: pd.DataFrame) -> bytes:
    """Export DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode('utf-8')


def export_to_excel(df: pd.DataFrame) -> bytes:
    """Export DataFrame to Excel bytes."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='ESG Report', index=False)
    return output.getvalue()


def get_filtered_data(
    organization: Optional[str] = None,
    year: Optional[int] = None
) -> pd.DataFrame:
    """Get filtered ESG data for reporting."""
    session = get_session()

    query = "SELECT * FROM ESG_REPORT_VIEW WHERE 1=1"

    if organization and organization != "All":
        query += f" AND ORGANIZATION_NAME = '{organization}'"

    if year and year != "All":
        query += f" AND REPORTING_YEAR = {year}"

    query += " ORDER BY REPORTING_YEAR DESC, ORGANIZATION_NAME"

    return session.sql(query).to_pandas()


def generate_report_filename(organization: str, year: str, format: str) -> str:
    """Generate a filename for the report."""
    org_part = organization.replace(" ", "_") if organization != "All" else "All_Orgs"
    year_part = str(year) if year != "All" else "All_Years"
    return f"ESG_Report_{org_part}_{year_part}.{format}"
