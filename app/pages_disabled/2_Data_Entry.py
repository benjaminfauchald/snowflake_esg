"""
ESG Data Entry - CRUD Operations
"""

import streamlit as st
from datetime import date

st.title("✏️ ESG Data Entry")

try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()

    # Tabs
    tab1, tab2 = st.tabs(["View Records", "Add New"])

    with tab1:
        st.markdown("### Current Records")
        df = session.table("ESG_METRICS").to_pandas()

        if df.empty:
            st.info("No records found.")
        else:
            st.dataframe(
                df[["ID", "ORGANIZATION_NAME", "REPORTING_YEAR", "GHG_SCOPE1_MTCO2E", "TOTAL_EMPLOYEES"]],
                use_container_width=True
            )

            # Delete functionality
            st.markdown("---")
            record_id = st.number_input("Record ID to delete", min_value=1, step=1)
            if st.button("Delete Record", type="secondary"):
                try:
                    session.sql(f"DELETE FROM ESG_METRICS WHERE ID = {record_id}").collect()
                    st.success(f"Record {record_id} deleted!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab2:
        st.markdown("### Add New ESG Record")

        with st.form("add_form"):
            org_name = st.text_input("Organization Name *")
            reporting_year = st.number_input("Reporting Year *", value=date.today().year, min_value=2000, max_value=2100)

            st.markdown("#### Environmental")
            col1, col2 = st.columns(2)
            with col1:
                ghg_scope1 = st.number_input("GHG Scope 1 (mtCO2e)", value=0.0)
            with col2:
                renewable_pct = st.number_input("Renewable Energy %", value=0.0, min_value=0.0, max_value=100.0)

            st.markdown("#### Social")
            col1, col2 = st.columns(2)
            with col1:
                employees = st.number_input("Total Employees", value=0)
            with col2:
                female_pct = st.number_input("Female Employees %", value=0.0, min_value=0.0, max_value=100.0)

            st.markdown("#### Governance")
            col1, col2 = st.columns(2)
            with col1:
                board_size = st.number_input("Board Size", value=0)
            with col2:
                ethics = st.checkbox("Has Ethics Policy")

            submitted = st.form_submit_button("Create Record", type="primary")

            if submitted:
                if not org_name:
                    st.error("Organization name is required!")
                else:
                    sql = f"""
                    INSERT INTO ESG_METRICS (
                        ORGANIZATION_NAME, REPORTING_YEAR, GHG_SCOPE1_MTCO2E,
                        RENEWABLE_ENERGY_PCT, TOTAL_EMPLOYEES, FEMALE_EMPLOYEES_PCT,
                        BOARD_SIZE, HAS_ETHICS_POLICY, CREATED_BY, CREATED_AT
                    ) VALUES (
                        '{org_name}', {reporting_year}, {ghg_scope1},
                        {renewable_pct}, {employees}, {female_pct},
                        {board_size}, {ethics}, CURRENT_USER(), CURRENT_TIMESTAMP()
                    )
                    """
                    try:
                        session.sql(sql).collect()
                        st.success("Record created!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error: {e}")

except Exception as e:
    st.error(f"Error: {e}")
