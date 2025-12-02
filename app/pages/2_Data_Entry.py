"""
ESG Data Entry - CRUD Operations

Allows users to create, read, update, and delete ESG records.
"""

import streamlit as st
import pandas as pd
from datetime import date
from utils.database import (
    get_all_records,
    get_record_by_id,
    create_record,
    update_record,
    delete_record
)

st.title("✏️ ESG Data Entry")
st.markdown("Add, edit, or delete ESG reporting records")

# Initialize session state
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "edit_record_id" not in st.session_state:
    st.session_state.edit_record_id = None

# Tabs for different operations
tab1, tab2 = st.tabs(["📋 View & Edit Records", "➕ Add New Record"])

# Tab 1: View and Edit Records
with tab1:
    st.markdown("### Current ESG Records")

    try:
        df = get_all_records()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        df = pd.DataFrame()

    if df.empty:
        st.info("No records found. Add a new record using the 'Add New Record' tab.")
    else:
        # Display records in a data editor
        st.markdown("Click on a row to select it for editing or deletion.")

        # Add selection column
        df_display = df[["ID", "ORGANIZATION_NAME", "REPORTING_YEAR",
                        "GHG_SCOPE1_MTCO2E", "RENEWABLE_ENERGY_PCT",
                        "TOTAL_EMPLOYEES", "BOARD_SIZE", "CREATED_AT"]].copy()

        # Show the data
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Edit/Delete controls
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            record_ids = df["ID"].tolist()
            selected_id = st.selectbox(
                "Select Record ID to Edit/Delete",
                options=record_ids,
                format_func=lambda x: f"ID {x} - {df[df['ID']==x]['ORGANIZATION_NAME'].values[0]} ({df[df['ID']==x]['REPORTING_YEAR'].values[0]})"
            )

        with col2:
            if st.button("Edit Selected", type="primary", use_container_width=True):
                st.session_state.edit_mode = True
                st.session_state.edit_record_id = selected_id
                st.rerun()

        with col3:
            if st.button("Delete Selected", type="secondary", use_container_width=True):
                if st.session_state.get("confirm_delete") == selected_id:
                    if delete_record(selected_id):
                        st.success(f"Record {selected_id} deleted successfully!")
                        st.session_state.confirm_delete = None
                        st.rerun()
                else:
                    st.session_state.confirm_delete = selected_id
                    st.warning(f"Click 'Delete Selected' again to confirm deletion of record {selected_id}")

        # Edit form
        if st.session_state.edit_mode and st.session_state.edit_record_id:
            st.markdown("---")
            st.markdown(f"### Edit Record #{st.session_state.edit_record_id}")

            record_df = get_record_by_id(st.session_state.edit_record_id)
            if record_df is not None:
                record = record_df.iloc[0]

                with st.form("edit_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        org_name = st.text_input("Organization Name", value=record["ORGANIZATION_NAME"])
                        reporting_year = st.number_input("Reporting Year", value=int(record["REPORTING_YEAR"]),
                                                         min_value=2000, max_value=2100)

                    with col2:
                        reporting_date = st.date_input(
                            "Reporting Date",
                            value=pd.to_datetime(record["REPORTING_DATE"]).date() if pd.notna(record["REPORTING_DATE"]) else date.today()
                        )

                    st.markdown("#### Environmental Metrics")
                    env_col1, env_col2, env_col3 = st.columns(3)

                    with env_col1:
                        ghg_scope1 = st.number_input("GHG Scope 1 (mtCO2e)",
                                                     value=float(record["GHG_SCOPE1_MTCO2E"]) if pd.notna(record["GHG_SCOPE1_MTCO2E"]) else 0.0)
                        ghg_scope2 = st.number_input("GHG Scope 2 (mtCO2e)",
                                                     value=float(record["GHG_SCOPE2_MTCO2E"]) if pd.notna(record["GHG_SCOPE2_MTCO2E"]) else 0.0)

                    with env_col2:
                        energy = st.number_input("Energy (MWh)",
                                                 value=float(record["ENERGY_CONSUMPTION_MWH"]) if pd.notna(record["ENERGY_CONSUMPTION_MWH"]) else 0.0)
                        renewable_pct = st.number_input("Renewable %", min_value=0.0, max_value=100.0,
                                                        value=float(record["RENEWABLE_ENERGY_PCT"]) if pd.notna(record["RENEWABLE_ENERGY_PCT"]) else 0.0)

                    with env_col3:
                        water = st.number_input("Water (m³)",
                                                value=float(record["WATER_CONSUMPTION_M3"]) if pd.notna(record["WATER_CONSUMPTION_M3"]) else 0.0)
                        waste = st.number_input("Waste (tons)",
                                                value=float(record["WASTE_GENERATED_TONS"]) if pd.notna(record["WASTE_GENERATED_TONS"]) else 0.0)
                        waste_recycled = st.number_input("Waste Recycled %", min_value=0.0, max_value=100.0,
                                                         value=float(record["WASTE_RECYCLED_PCT"]) if pd.notna(record["WASTE_RECYCLED_PCT"]) else 0.0)

                    st.markdown("#### Social Metrics")
                    soc_col1, soc_col2, soc_col3 = st.columns(3)

                    with soc_col1:
                        employees = st.number_input("Total Employees",
                                                    value=int(record["TOTAL_EMPLOYEES"]) if pd.notna(record["TOTAL_EMPLOYEES"]) else 0)
                        female_pct = st.number_input("Female Employees %", min_value=0.0, max_value=100.0,
                                                     value=float(record["FEMALE_EMPLOYEES_PCT"]) if pd.notna(record["FEMALE_EMPLOYEES_PCT"]) else 0.0)

                    with soc_col2:
                        turnover = st.number_input("Turnover %", min_value=0.0, max_value=100.0,
                                                   value=float(record["EMPLOYEE_TURNOVER_PCT"]) if pd.notna(record["EMPLOYEE_TURNOVER_PCT"]) else 0.0)
                        safety = st.number_input("Safety Incidents",
                                                 value=int(record["SAFETY_INCIDENTS"]) if pd.notna(record["SAFETY_INCIDENTS"]) else 0)

                    with soc_col3:
                        training = st.number_input("Training Hours/Employee",
                                                   value=float(record["TRAINING_HOURS_PER_EMPLOYEE"]) if pd.notna(record["TRAINING_HOURS_PER_EMPLOYEE"]) else 0.0)

                    st.markdown("#### Governance Metrics")
                    gov_col1, gov_col2, gov_col3 = st.columns(3)

                    with gov_col1:
                        board_size = st.number_input("Board Size",
                                                     value=int(record["BOARD_SIZE"]) if pd.notna(record["BOARD_SIZE"]) else 0)
                        board_ind = st.number_input("Board Independence %", min_value=0.0, max_value=100.0,
                                                    value=float(record["BOARD_INDEPENDENCE_PCT"]) if pd.notna(record["BOARD_INDEPENDENCE_PCT"]) else 0.0)

                    with gov_col2:
                        board_female = st.number_input("Board Female %", min_value=0.0, max_value=100.0,
                                                       value=float(record["BOARD_FEMALE_PCT"]) if pd.notna(record["BOARD_FEMALE_PCT"]) else 0.0)

                    with gov_col3:
                        ethics = st.checkbox("Has Ethics Policy",
                                             value=bool(record["HAS_ETHICS_POLICY"]) if pd.notna(record["HAS_ETHICS_POLICY"]) else False)
                        whistleblower = st.checkbox("Has Whistleblower Policy",
                                                    value=bool(record["HAS_WHISTLEBLOWER_POLICY"]) if pd.notna(record["HAS_WHISTLEBLOWER_POLICY"]) else False)

                    notes = st.text_area("Notes", value=str(record["NOTES"]) if pd.notna(record["NOTES"]) else "")

                    col1, col2 = st.columns(2)
                    with col1:
                        submit = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
                    with col2:
                        cancel = st.form_submit_button("Cancel", use_container_width=True)

                    if submit:
                        data = {
                            "ORGANIZATION_NAME": org_name,
                            "REPORTING_YEAR": reporting_year,
                            "REPORTING_DATE": str(reporting_date),
                            "GHG_SCOPE1_MTCO2E": ghg_scope1,
                            "GHG_SCOPE2_MTCO2E": ghg_scope2,
                            "ENERGY_CONSUMPTION_MWH": energy,
                            "RENEWABLE_ENERGY_PCT": renewable_pct,
                            "WATER_CONSUMPTION_M3": water,
                            "WASTE_GENERATED_TONS": waste,
                            "WASTE_RECYCLED_PCT": waste_recycled,
                            "TOTAL_EMPLOYEES": employees,
                            "FEMALE_EMPLOYEES_PCT": female_pct,
                            "EMPLOYEE_TURNOVER_PCT": turnover,
                            "SAFETY_INCIDENTS": safety,
                            "TRAINING_HOURS_PER_EMPLOYEE": training,
                            "BOARD_SIZE": board_size,
                            "BOARD_INDEPENDENCE_PCT": board_ind,
                            "BOARD_FEMALE_PCT": board_female,
                            "HAS_ETHICS_POLICY": ethics,
                            "HAS_WHISTLEBLOWER_POLICY": whistleblower,
                            "NOTES": notes
                        }

                        if update_record(st.session_state.edit_record_id, data):
                            st.success("Record updated successfully!")
                            st.session_state.edit_mode = False
                            st.session_state.edit_record_id = None
                            st.rerun()

                    if cancel:
                        st.session_state.edit_mode = False
                        st.session_state.edit_record_id = None
                        st.rerun()

# Tab 2: Add New Record
with tab2:
    st.markdown("### Add New ESG Record")

    with st.form("add_form"):
        col1, col2 = st.columns(2)

        with col1:
            org_name = st.text_input("Organization Name *", value="")
            reporting_year = st.number_input("Reporting Year *", value=date.today().year,
                                             min_value=2000, max_value=2100)

        with col2:
            reporting_date = st.date_input("Reporting Date", value=date.today())

        st.markdown("#### Environmental Metrics")
        env_col1, env_col2, env_col3 = st.columns(3)

        with env_col1:
            ghg_scope1 = st.number_input("GHG Scope 1 (mtCO2e)", value=0.0, key="new_ghg1")
            ghg_scope2 = st.number_input("GHG Scope 2 (mtCO2e)", value=0.0, key="new_ghg2")

        with env_col2:
            energy = st.number_input("Energy Consumption (MWh)", value=0.0, key="new_energy")
            renewable_pct = st.number_input("Renewable Energy %", min_value=0.0, max_value=100.0, value=0.0, key="new_renewable")

        with env_col3:
            water = st.number_input("Water Consumption (m³)", value=0.0, key="new_water")
            waste = st.number_input("Waste Generated (tons)", value=0.0, key="new_waste")
            waste_recycled = st.number_input("Waste Recycled %", min_value=0.0, max_value=100.0, value=0.0, key="new_waste_recycled")

        st.markdown("#### Social Metrics")
        soc_col1, soc_col2, soc_col3 = st.columns(3)

        with soc_col1:
            employees = st.number_input("Total Employees", value=0, key="new_employees")
            female_pct = st.number_input("Female Employees %", min_value=0.0, max_value=100.0, value=0.0, key="new_female")

        with soc_col2:
            turnover = st.number_input("Employee Turnover %", min_value=0.0, max_value=100.0, value=0.0, key="new_turnover")
            safety = st.number_input("Safety Incidents", value=0, key="new_safety")

        with soc_col3:
            training = st.number_input("Training Hours/Employee", value=0.0, key="new_training")

        st.markdown("#### Governance Metrics")
        gov_col1, gov_col2, gov_col3 = st.columns(3)

        with gov_col1:
            board_size = st.number_input("Board Size", value=0, key="new_board")
            board_ind = st.number_input("Board Independence %", min_value=0.0, max_value=100.0, value=0.0, key="new_board_ind")

        with gov_col2:
            board_female = st.number_input("Board Female %", min_value=0.0, max_value=100.0, value=0.0, key="new_board_female")

        with gov_col3:
            ethics = st.checkbox("Has Ethics Policy", key="new_ethics")
            whistleblower = st.checkbox("Has Whistleblower Policy", key="new_whistle")

        notes = st.text_area("Notes", key="new_notes")

        submitted = st.form_submit_button("Create Record", type="primary", use_container_width=True)

        if submitted:
            if not org_name:
                st.error("Organization name is required!")
            else:
                data = {
                    "ORGANIZATION_NAME": org_name,
                    "REPORTING_YEAR": reporting_year,
                    "REPORTING_DATE": str(reporting_date),
                    "GHG_SCOPE1_MTCO2E": ghg_scope1,
                    "GHG_SCOPE2_MTCO2E": ghg_scope2,
                    "ENERGY_CONSUMPTION_MWH": energy,
                    "RENEWABLE_ENERGY_PCT": renewable_pct,
                    "WATER_CONSUMPTION_M3": water,
                    "WASTE_GENERATED_TONS": waste,
                    "WASTE_RECYCLED_PCT": waste_recycled,
                    "TOTAL_EMPLOYEES": employees,
                    "FEMALE_EMPLOYEES_PCT": female_pct,
                    "EMPLOYEE_TURNOVER_PCT": turnover,
                    "SAFETY_INCIDENTS": safety,
                    "TRAINING_HOURS_PER_EMPLOYEE": training,
                    "BOARD_SIZE": board_size,
                    "BOARD_INDEPENDENCE_PCT": board_ind,
                    "BOARD_FEMALE_PCT": board_female,
                    "HAS_ETHICS_POLICY": ethics,
                    "HAS_WHISTLEBLOWER_POLICY": whistleblower,
                    "NOTES": notes
                }

                if create_record(data):
                    st.success("Record created successfully!")
                    st.balloons()
