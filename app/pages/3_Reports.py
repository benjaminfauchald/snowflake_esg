"""
ESG Reports - Download and Export

Generate and download ESG reports for government submission.
"""

import streamlit as st
import pandas as pd
from datetime import date
from utils.database import get_all_records, get_years, get_organizations
from utils.export import export_to_csv, get_filtered_data, generate_report_filename

st.set_page_config(page_title="ESG Reports", page_icon="📥", layout="wide")

st.title("📥 ESG Reports")
st.markdown("Download ESG data for government reporting and analysis")

# Filters
st.markdown("### Filter Data")

col1, col2 = st.columns(2)

try:
    years = ["All"] + get_years()
    orgs = ["All"] + get_organizations()
except Exception:
    years = ["All"]
    orgs = ["All"]

with col1:
    selected_year = st.selectbox("Reporting Year", options=years)

with col2:
    selected_org = st.selectbox("Organization", options=orgs)

# Get filtered data
try:
    year_filter = None if selected_year == "All" else selected_year
    org_filter = None if selected_org == "All" else selected_org
    df = get_filtered_data(organization=org_filter, year=year_filter)
except Exception as e:
    st.error(f"Error loading data: {e}")
    df = pd.DataFrame()

st.markdown("---")

# Preview section
st.markdown("### Report Preview")

if df.empty:
    st.warning("No data matches the selected filters.")
else:
    # Show summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Records", len(df))

    with col2:
        if "TOTAL_GHG_EMISSIONS" in df.columns:
            st.metric("Total Emissions (mtCO2e)", f"{df['TOTAL_GHG_EMISSIONS'].sum():,.0f}")
        elif "GHG_SCOPE1_MTCO2E" in df.columns:
            total_emissions = df["GHG_SCOPE1_MTCO2E"].sum() + df["GHG_SCOPE2_MTCO2E"].fillna(0).sum()
            st.metric("Total Emissions (mtCO2e)", f"{total_emissions:,.0f}")

    with col3:
        if "RENEWABLE_ENERGY_PCT" in df.columns:
            st.metric("Avg Renewable %", f"{df['RENEWABLE_ENERGY_PCT'].mean():.1f}%")

    with col4:
        if "TOTAL_EMPLOYEES" in df.columns:
            st.metric("Total Employees", f"{df['TOTAL_EMPLOYEES'].sum():,}")

    # Data preview
    st.markdown("#### Data Preview")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Download section
    st.markdown("### Download Report")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### CSV Format")
        st.markdown("Download as CSV file for spreadsheet applications.")

        csv_data = export_to_csv(df)
        csv_filename = generate_report_filename(
            str(selected_org),
            str(selected_year),
            "csv"
        )

        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=csv_filename,
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )

    with col2:
        st.markdown("#### Government Report Format")
        st.markdown("Formatted report for regulatory submission.")

        # Create a formatted report
        report_lines = [
            "=" * 60,
            "ESG COMPLIANCE REPORT",
            "=" * 60,
            "",
            f"Generated: {date.today().strftime('%Y-%m-%d')}",
            f"Organization: {selected_org}",
            f"Reporting Period: {selected_year}",
            "",
            "-" * 60,
            "SUMMARY STATISTICS",
            "-" * 60,
            "",
            f"Total Records: {len(df)}",
        ]

        if "GHG_SCOPE1_MTCO2E" in df.columns:
            total_scope1 = df["GHG_SCOPE1_MTCO2E"].sum()
            total_scope2 = df["GHG_SCOPE2_MTCO2E"].fillna(0).sum()
            report_lines.extend([
                "",
                "ENVIRONMENTAL METRICS:",
                f"  - Total Scope 1 Emissions: {total_scope1:,.2f} mtCO2e",
                f"  - Total Scope 2 Emissions: {total_scope2:,.2f} mtCO2e",
                f"  - Combined Emissions: {total_scope1 + total_scope2:,.2f} mtCO2e",
            ])

        if "RENEWABLE_ENERGY_PCT" in df.columns:
            avg_renewable = df["RENEWABLE_ENERGY_PCT"].mean()
            report_lines.append(f"  - Average Renewable Energy: {avg_renewable:.1f}%")

        if "TOTAL_EMPLOYEES" in df.columns:
            total_emp = df["TOTAL_EMPLOYEES"].sum()
            avg_female = df["FEMALE_EMPLOYEES_PCT"].mean() if "FEMALE_EMPLOYEES_PCT" in df.columns else 0
            report_lines.extend([
                "",
                "SOCIAL METRICS:",
                f"  - Total Workforce: {total_emp:,}",
                f"  - Average Female Representation: {avg_female:.1f}%",
            ])

        if "BOARD_SIZE" in df.columns:
            avg_board = df["BOARD_SIZE"].mean()
            avg_ind = df["BOARD_INDEPENDENCE_PCT"].mean() if "BOARD_INDEPENDENCE_PCT" in df.columns else 0
            report_lines.extend([
                "",
                "GOVERNANCE METRICS:",
                f"  - Average Board Size: {avg_board:.0f}",
                f"  - Average Board Independence: {avg_ind:.1f}%",
            ])

        report_lines.extend([
            "",
            "-" * 60,
            "CERTIFICATION",
            "-" * 60,
            "",
            "This report has been generated from the ESG Reporting Portal.",
            "Data should be verified before regulatory submission.",
            "",
            "=" * 60,
        ])

        report_text = "\n".join(report_lines)

        report_filename = f"ESG_Government_Report_{selected_org}_{selected_year}.txt".replace(" ", "_")

        st.download_button(
            label="📋 Download Government Report",
            data=report_text.encode("utf-8"),
            file_name=report_filename,
            mime="text/plain",
            use_container_width=True
        )

# Report history info
st.markdown("---")
st.markdown("### Report Information")
st.info("""
**Included Data Fields:**
- Organization details and reporting period
- Environmental metrics (GHG emissions, energy, water, waste)
- Social metrics (employees, diversity, safety, training)
- Governance metrics (board composition, policies)

**Report Formats:**
- **CSV**: Raw data for analysis in Excel or other tools
- **Government Report**: Formatted summary for regulatory submission
""")
