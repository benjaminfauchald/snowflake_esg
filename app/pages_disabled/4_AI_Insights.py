"""
AI Insights - Cortex AI Integration
"""

import streamlit as st

st.title("🤖 AI Insights")
st.markdown("Get AI-powered analysis using Snowflake Cortex")

try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()

    # Get data summary
    df = session.table("ESG_METRICS").to_pandas()

    if df.empty:
        st.warning("No data available for analysis.")
    else:
        # Data context
        data_summary = f"""
        ESG Data Summary:
        - Total records: {len(df)}
        - Organizations: {df['ORGANIZATION_NAME'].nunique()}
        - Years: {df['REPORTING_YEAR'].min()} to {df['REPORTING_YEAR'].max()}
        - Total GHG Emissions: {df['GHG_SCOPE1_MTCO2E'].sum():,.0f} mtCO2e
        - Avg Renewable Energy: {df['RENEWABLE_ENERGY_PCT'].mean():.1f}%
        """

        st.markdown("### Data Context")
        st.code(data_summary)

        st.markdown("---")
        st.markdown("### Ask a Question")

        user_question = st.text_input(
            "Enter your question:",
            placeholder="e.g., What are the key trends in our ESG performance?"
        )

        if st.button("Get AI Answer", type="primary", disabled=not user_question):
            with st.spinner("Analyzing with Cortex AI..."):
                prompt = f"""You are an ESG analyst. Based on this data summary, answer the question.

{data_summary}

Question: {user_question}

Provide a clear, professional response:"""

                # Escape quotes
                escaped_prompt = prompt.replace("'", "''")

                try:
                    result = session.sql(f"""
                        SELECT SNOWFLAKE.CORTEX.COMPLETE(
                            'claude-3-5-sonnet',
                            '{escaped_prompt}'
                        ) as response
                    """).collect()

                    st.markdown("### AI Response")
                    st.markdown(result[0]["RESPONSE"])
                except Exception as e:
                    st.error(f"Cortex error: {e}")
                    st.info("Make sure Cortex AI is enabled in your Snowflake account.")

except Exception as e:
    st.error(f"Error: {e}")
