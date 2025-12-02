"""
ESG Reporting Portal - Main Application
"""

import streamlit as st

# Page configuration - only call this once in the main app
st.set_page_config(
    page_title="ESG Reporting Portal",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 ESG Reporting Portal")
st.markdown("Manage your Environmental, Social, and Governance reporting data")

st.markdown("---")

# Test database connection
try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()

    # Simple query to test
    result = session.sql("SELECT CURRENT_USER() as user, CURRENT_DATABASE() as db").collect()

    st.success("✅ Connected to Snowflake!")
    st.write(f"**User:** {result[0]['USER']}")
    st.write(f"**Database:** {result[0]['DB']}")

    # Test table access
    count_result = session.sql("SELECT COUNT(*) as cnt FROM ESG_METRICS").collect()
    st.write(f"**ESG Records:** {count_result[0]['CNT']}")

except Exception as e:
    st.error(f"Connection error: {e}")

st.markdown("---")
st.info("👈 Use the sidebar to navigate between pages")
