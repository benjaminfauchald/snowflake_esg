"""
ESG Reporting Portal - Main Application

A Streamlit application for managing ESG (Environmental, Social, Governance)
reporting data with CRUD operations and AI-powered insights.
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="ESG Reporting Portal",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #10B981;
    }
    .stMetric {
        background-color: #F8FAFC;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation info
st.sidebar.markdown("### Navigation")
st.sidebar.info("""
Use the pages in the sidebar to:
- **Dashboard**: View ESG metrics overview
- **Data Entry**: Add, edit, or delete records
- **Reports**: Download ESG reports
- **AI Insights**: Get AI-powered analysis
""")

# Main page content
st.markdown('<p class="main-header">ESG Reporting Portal</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Manage your Environmental, Social, and Governance reporting data</p>',
    unsafe_allow_html=True
)

# Welcome section
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Welcome")
    st.markdown("""
    This portal allows you to manage your organization's ESG reporting data.
    Use the sidebar to navigate between different sections:

    - **Dashboard** - View metrics and trends
    - **Data Entry** - Create, update, and delete ESG records
    - **Reports** - Download data for government reporting
    - **AI Insights** - Get AI-powered analysis of your ESG data
    """)

with col2:
    st.markdown("### Quick Actions")
    st.info("👈 Use the sidebar to navigate between pages")
    st.markdown("""
    - **Dashboard** - View metrics and charts
    - **Data Entry** - Add or edit records
    - **Reports** - Download ESG reports
    - **AI Insights** - Get AI analysis
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6B7280;'>"
    "ESG Reporting Portal | Powered by Snowflake & Streamlit"
    "</div>",
    unsafe_allow_html=True
)
