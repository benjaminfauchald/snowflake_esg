"""
ESG Dashboard - Overview and Visualizations

Displays key ESG metrics, trends, and summary statistics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import get_all_records, get_summary_stats, get_years

st.title("📊 ESG Dashboard")
st.markdown("Overview of Environmental, Social, and Governance metrics")

# Load data
try:
    df = get_all_records()
    stats = get_summary_stats()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please ensure the database tables are set up correctly.")
    st.stop()

if df.empty:
    st.warning("No ESG data available. Please add records in the Data Entry section.")
    st.stop()

# Summary metrics row
st.markdown("### Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Records",
        value=stats.get("TOTAL_RECORDS", 0)
    )

with col2:
    st.metric(
        label="Organizations",
        value=stats.get("TOTAL_ORGS", 0)
    )

with col3:
    st.metric(
        label="Latest Year",
        value=stats.get("LATEST_YEAR", "N/A")
    )

with col4:
    avg_renewable = stats.get("AVG_RENEWABLE_PCT", 0)
    st.metric(
        label="Avg Renewable Energy",
        value=f"{avg_renewable:.1f}%" if avg_renewable else "N/A"
    )

st.markdown("---")

# Charts section
st.markdown("### Trends & Analysis")

tab1, tab2, tab3 = st.tabs(["Environmental", "Social", "Governance"])

with tab1:
    st.markdown("#### Environmental Metrics")

    # GHG Emissions over time
    if "GHG_SCOPE1_MTCO2E" in df.columns and "GHG_SCOPE2_MTCO2E" in df.columns:
        emissions_df = df.groupby("REPORTING_YEAR").agg({
            "GHG_SCOPE1_MTCO2E": "sum",
            "GHG_SCOPE2_MTCO2E": "sum"
        }).reset_index()

        emissions_df["Total Emissions"] = (
            emissions_df["GHG_SCOPE1_MTCO2E"] +
            emissions_df["GHG_SCOPE2_MTCO2E"].fillna(0)
        )

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                emissions_df,
                x="REPORTING_YEAR",
                y=["GHG_SCOPE1_MTCO2E", "GHG_SCOPE2_MTCO2E"],
                title="GHG Emissions by Scope (mtCO2e)",
                labels={"value": "Emissions (mtCO2e)", "REPORTING_YEAR": "Year"},
                barmode="stack"
            )
            fig.update_layout(legend_title_text="Scope")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            renewable_df = df.groupby("REPORTING_YEAR").agg({
                "RENEWABLE_ENERGY_PCT": "mean"
            }).reset_index()

            fig = px.line(
                renewable_df,
                x="REPORTING_YEAR",
                y="RENEWABLE_ENERGY_PCT",
                title="Renewable Energy Adoption (%)",
                markers=True
            )
            fig.update_traces(line_color="#10B981")
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.markdown("#### Social Metrics")

    col1, col2 = st.columns(2)

    with col1:
        if "FEMALE_EMPLOYEES_PCT" in df.columns:
            diversity_df = df.groupby("REPORTING_YEAR").agg({
                "FEMALE_EMPLOYEES_PCT": "mean",
                "TOTAL_EMPLOYEES": "sum"
            }).reset_index()

            fig = px.bar(
                diversity_df,
                x="REPORTING_YEAR",
                y="FEMALE_EMPLOYEES_PCT",
                title="Gender Diversity (% Female)",
                color="FEMALE_EMPLOYEES_PCT",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "SAFETY_INCIDENTS" in df.columns:
            safety_df = df.groupby("REPORTING_YEAR").agg({
                "SAFETY_INCIDENTS": "sum"
            }).reset_index()

            fig = px.line(
                safety_df,
                x="REPORTING_YEAR",
                y="SAFETY_INCIDENTS",
                title="Safety Incidents Over Time",
                markers=True
            )
            fig.update_traces(line_color="#EF4444")
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown("#### Governance Metrics")

    col1, col2 = st.columns(2)

    with col1:
        if "BOARD_INDEPENDENCE_PCT" in df.columns:
            gov_df = df.groupby("REPORTING_YEAR").agg({
                "BOARD_INDEPENDENCE_PCT": "mean",
                "BOARD_FEMALE_PCT": "mean"
            }).reset_index()

            fig = px.line(
                gov_df,
                x="REPORTING_YEAR",
                y=["BOARD_INDEPENDENCE_PCT", "BOARD_FEMALE_PCT"],
                title="Board Composition (%)",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "HAS_ETHICS_POLICY" in df.columns:
            latest_year = df["REPORTING_YEAR"].max()
            latest_df = df[df["REPORTING_YEAR"] == latest_year]

            policies = {
                "Ethics Policy": latest_df["HAS_ETHICS_POLICY"].sum(),
                "Whistleblower Policy": latest_df["HAS_WHISTLEBLOWER_POLICY"].sum()
            }

            fig = go.Figure(data=[
                go.Bar(
                    x=list(policies.keys()),
                    y=list(policies.values()),
                    marker_color=["#3B82F6", "#8B5CF6"]
                )
            ])
            fig.update_layout(title=f"Policy Adoption ({latest_year})")
            st.plotly_chart(fig, use_container_width=True)

# Data table
st.markdown("---")
st.markdown("### Recent Records")
st.dataframe(
    df.head(10),
    use_container_width=True,
    hide_index=True
)
