"""
ESG Reports - Download and Export
"""

import streamlit as st
from datetime import date

st.title("📥 ESG Reports")

try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()

    # Get data
    df = session.table("ESG_METRICS").to_pandas()

    if df.empty:
        st.warning("No data available to export.")
    else:
        st.markdown("### Data Preview")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.markdown("### Download")

        # CSV download
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"ESG_Report_{date.today()}.csv",
            mime="text/csv",
            type="primary"
        )

        # Summary stats
        st.markdown("---")
        st.markdown("### Summary Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Records", len(df))
        with col2:
            if "GHG_SCOPE1_MTCO2E" in df.columns:
                st.metric("Total Emissions", f"{df['GHG_SCOPE1_MTCO2E'].sum():,.0f}")
        with col3:
            if "TOTAL_EMPLOYEES" in df.columns:
                st.metric("Total Employees", f"{df['TOTAL_EMPLOYEES'].sum():,}")

except Exception as e:
    st.error(f"Error: {e}")
