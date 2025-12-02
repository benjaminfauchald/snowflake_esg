"""
ESG Dashboard - Overview
"""

import streamlit as st

st.title("📊 ESG Dashboard")

try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()

    # Get data
    df = session.table("ESG_METRICS").to_pandas()

    if df.empty:
        st.warning("No ESG data available.")
    else:
        st.markdown("### Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Records", len(df))

        with col2:
            st.metric("Organizations", df["ORGANIZATION_NAME"].nunique())

        with col3:
            st.metric("Latest Year", df["REPORTING_YEAR"].max())

        st.markdown("### Recent Records")
        st.dataframe(df.head(10), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
