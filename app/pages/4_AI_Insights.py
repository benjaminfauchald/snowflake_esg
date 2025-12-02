"""
AI Insights - Cortex AI Integration

Use Snowflake Cortex AI to analyze ESG data and get intelligent insights.
"""

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
from utils.database import get_all_records

st.set_page_config(page_title="AI Insights", page_icon="🤖", layout="wide")

st.title("🤖 AI Insights")
st.markdown("Get AI-powered analysis of your ESG data using Snowflake Cortex")


def get_session():
    """Get the active Snowpark session."""
    return get_active_session()


def query_cortex(prompt: str, model: str = "claude-3-5-sonnet") -> str:
    """Query Snowflake Cortex AI with a prompt."""
    session = get_session()

    # Escape single quotes in prompt
    escaped_prompt = prompt.replace("'", "''")

    sql = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        '{model}',
        '{escaped_prompt}'
    ) as response
    """

    try:
        result = session.sql(sql).collect()
        return result[0]["RESPONSE"] if result else "No response received."
    except Exception as e:
        return f"Error querying Cortex: {str(e)}"


def get_data_summary() -> str:
    """Create a text summary of the ESG data for AI context."""
    try:
        df = get_all_records()
        if df.empty:
            return "No ESG data available."

        summary_parts = [
            f"ESG Data Summary:",
            f"- Total records: {len(df)}",
            f"- Organizations: {df['ORGANIZATION_NAME'].nunique()}",
            f"- Years covered: {df['REPORTING_YEAR'].min()} to {df['REPORTING_YEAR'].max()}",
        ]

        # Latest year stats
        latest_year = df["REPORTING_YEAR"].max()
        latest_df = df[df["REPORTING_YEAR"] == latest_year]

        if "GHG_SCOPE1_MTCO2E" in df.columns:
            total_emissions = latest_df["GHG_SCOPE1_MTCO2E"].sum() + latest_df["GHG_SCOPE2_MTCO2E"].fillna(0).sum()
            summary_parts.append(f"- Latest year total GHG emissions: {total_emissions:,.0f} mtCO2e")

        if "RENEWABLE_ENERGY_PCT" in df.columns:
            avg_renewable = latest_df["RENEWABLE_ENERGY_PCT"].mean()
            summary_parts.append(f"- Latest year avg renewable energy: {avg_renewable:.1f}%")

        if "TOTAL_EMPLOYEES" in df.columns:
            total_emp = latest_df["TOTAL_EMPLOYEES"].sum()
            summary_parts.append(f"- Latest year total employees: {total_emp:,}")

        if "FEMALE_EMPLOYEES_PCT" in df.columns:
            avg_female = latest_df["FEMALE_EMPLOYEES_PCT"].mean()
            summary_parts.append(f"- Latest year avg female representation: {avg_female:.1f}%")

        # Trends
        if len(df["REPORTING_YEAR"].unique()) > 1:
            years = sorted(df["REPORTING_YEAR"].unique())
            if len(years) >= 2:
                first_year = df[df["REPORTING_YEAR"] == years[0]]
                last_year = df[df["REPORTING_YEAR"] == years[-1]]

                if "GHG_SCOPE1_MTCO2E" in df.columns:
                    first_emissions = first_year["GHG_SCOPE1_MTCO2E"].sum()
                    last_emissions = last_year["GHG_SCOPE1_MTCO2E"].sum()
                    change = ((last_emissions - first_emissions) / first_emissions * 100) if first_emissions > 0 else 0
                    summary_parts.append(f"- Emissions trend ({years[0]} to {years[-1]}): {change:+.1f}%")

        return "\n".join(summary_parts)
    except Exception as e:
        return f"Error generating summary: {str(e)}"


# Tabs for different AI features
tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "📊 Data Validation", "📝 Report Summary"])

with tab1:
    st.markdown("### Ask Questions About Your ESG Data")
    st.markdown("Use natural language to query and analyze your ESG metrics.")

    # Show data context
    with st.expander("View Data Context"):
        st.code(get_data_summary())

    # Preset questions
    st.markdown("#### Quick Questions")
    preset_questions = [
        "What are the key trends in our ESG performance?",
        "How can we improve our environmental metrics?",
        "What are our strengths and weaknesses in governance?",
        "Compare our social metrics to industry best practices.",
    ]

    cols = st.columns(2)
    for i, question in enumerate(preset_questions):
        with cols[i % 2]:
            if st.button(question, key=f"preset_{i}", use_container_width=True):
                st.session_state["user_question"] = question

    # Custom question input
    st.markdown("#### Ask Your Own Question")
    user_question = st.text_input(
        "Enter your question:",
        value=st.session_state.get("user_question", ""),
        placeholder="e.g., What was our biggest environmental improvement?"
    )

    if st.button("Get AI Answer", type="primary", disabled=not user_question):
        with st.spinner("Analyzing your data with Cortex AI..."):
            data_context = get_data_summary()

            prompt = f"""You are an ESG (Environmental, Social, Governance) analyst.
Based on the following ESG data summary, answer the user's question.
Be specific, cite numbers when available, and provide actionable insights.

{data_context}

User Question: {user_question}

Provide a clear, professional response:"""

            response = query_cortex(prompt)

            st.markdown("#### AI Response")
            st.markdown(response)

with tab2:
    st.markdown("### AI Data Validation")
    st.markdown("Let AI check your ESG data for anomalies and inconsistencies.")

    if st.button("Run Validation Check", type="primary"):
        with st.spinner("Validating data with Cortex AI..."):
            try:
                df = get_all_records()

                if df.empty:
                    st.warning("No data to validate.")
                else:
                    # Create validation context
                    validation_data = []
                    for _, row in df.iterrows():
                        record = {
                            "org": row["ORGANIZATION_NAME"],
                            "year": row["REPORTING_YEAR"],
                            "ghg_scope1": row.get("GHG_SCOPE1_MTCO2E"),
                            "ghg_scope2": row.get("GHG_SCOPE2_MTCO2E"),
                            "renewable_pct": row.get("RENEWABLE_ENERGY_PCT"),
                            "employees": row.get("TOTAL_EMPLOYEES"),
                            "female_pct": row.get("FEMALE_EMPLOYEES_PCT"),
                            "turnover_pct": row.get("EMPLOYEE_TURNOVER_PCT"),
                            "board_size": row.get("BOARD_SIZE"),
                        }
                        validation_data.append(str(record))

                    data_str = "\n".join(validation_data[:10])  # Limit for prompt size

                    prompt = f"""You are an ESG data quality analyst. Review the following ESG records for potential issues:

{data_str}

Identify any:
1. Unusual or outlier values that might be data entry errors
2. Inconsistencies between related metrics
3. Missing critical data points
4. Values outside expected ranges (e.g., percentages > 100)
5. Year-over-year changes that seem unrealistic

Format your response as a list of findings with severity (High/Medium/Low) and recommendations."""

                    response = query_cortex(prompt)

                    st.markdown("#### Validation Results")
                    st.markdown(response)

            except Exception as e:
                st.error(f"Error during validation: {e}")

with tab3:
    st.markdown("### AI Report Summary Generator")
    st.markdown("Generate an executive summary of your ESG performance.")

    col1, col2 = st.columns(2)

    with col1:
        report_year = st.selectbox(
            "Select Year",
            options=["Latest"] + list(range(2024, 2019, -1))
        )

    with col2:
        report_tone = st.selectbox(
            "Report Tone",
            options=["Professional", "Technical", "Simplified"]
        )

    if st.button("Generate Summary", type="primary"):
        with st.spinner("Generating executive summary..."):
            data_context = get_data_summary()

            prompt = f"""You are an ESG communications specialist. Generate an executive summary
for ESG performance based on this data:

{data_context}

Requirements:
- Tone: {report_tone}
- Year focus: {report_year}
- Include: Key achievements, areas for improvement, and strategic recommendations
- Length: 3-4 paragraphs

Generate the executive summary:"""

            response = query_cortex(prompt)

            st.markdown("#### Executive Summary")
            st.markdown(response)

            # Download option
            st.download_button(
                label="Download Summary",
                data=response.encode("utf-8"),
                file_name=f"ESG_Executive_Summary_{report_year}.txt",
                mime="text/plain"
            )

# Info section
st.markdown("---")
st.info("""
**Powered by Snowflake Cortex AI**

This feature uses Snowflake's built-in AI capabilities to analyze your ESG data.
All processing happens securely within your Snowflake environment.

Available AI Models:
- Claude 3.5 Sonnet (default) - Best for analysis and insights
- Mistral Large - Alternative for complex queries
- Snowflake Arctic - Optimized for Snowflake data
""")
