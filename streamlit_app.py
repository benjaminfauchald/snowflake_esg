"""
SET ESG One Report (Form 56-1) Management System
For Thai listed companies submitting to Stock Exchange of Thailand
"""
import streamlit as st
from datetime import date
import pandas as pd

# Global helper functions for NaN handling
def safe_int(val, default=0):
    if pd.isna(val):
        return default
    try:
        return int(val)
    except:
        return default

def safe_float(val, default=0.0):
    if pd.isna(val):
        return default
    try:
        return float(val)
    except:
        return default

st.title("SET ESG One Report")
st.caption("ระบบจัดการข้อมูล ESG สำหรับ One Report (แบบ 56-1)")

# Persistent messages
if "message" in st.session_state:
    msg_type, msg_text = st.session_state.message
    if msg_type == "success":
        st.success(msg_text)
    del st.session_state.message

try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()

    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "E - Environmental", "S - Social", "G - Governance"])

    # Load data
    df = session.table("ESG_METRICS").to_pandas()

    # === DASHBOARD ===
    with tab1:
        if df.empty:
            st.info("ยังไม่มีข้อมูล One Report กรุณาเพิ่มข้อมูลในแต่ละหมวด E, S, G")
        else:
            latest = df.loc[df["REPORT_YEAR"].idxmax()]

            # Status
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Report Year", int(latest["REPORT_YEAR"]))
            with col2:
                st.metric("Status", latest["REPORT_STATUS"])
            with col3:
                st.metric("Sector", latest["SECTOR"] or "N/A")
            with col4:
                cgr = latest["CGR_SCORE"] or "N/A"
                st.metric("CGR Score", cgr)

            st.markdown("---")

            # E S G Summary
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### 🌱 Environmental")
                total_ghg = safe_float(latest["GHG_SCOPE1_TCO2E"]) + safe_float(latest["GHG_SCOPE2_TCO2E"])
                energy_total = safe_float(latest["ENERGY_TOTAL_MWH"], 1)
                renewable = (safe_float(latest["ENERGY_RENEWABLE_MWH"]) / energy_total) * 100
                st.metric("GHG Emissions", f"{total_ghg:,.0f} tCO2e")
                st.metric("Renewable Energy", f"{renewable:.0f}%")
                st.metric("Waste Recycled", f"{safe_float(latest['WASTE_RECYCLED_PCT']):.0f}%")
                if latest["ISO14001_CERTIFIED"]:
                    st.success("ISO 14001 ✓")

            with col2:
                st.markdown("### 👥 Social")
                st.metric("Employees", f"{safe_int(latest['EMPLOYEES_TOTAL']):,}")
                st.metric("Women in Management", f"{safe_float(latest['WOMEN_MANAGEMENT_PCT']):.0f}%")
                st.metric("Training Hours/Person", f"{safe_float(latest['TRAINING_HOURS_AVG']):.0f}")
                if latest["ISO45001_CERTIFIED"]:
                    st.success("ISO 45001 ✓")

            with col3:
                st.markdown("### 🏛️ Governance")
                st.metric("Board Independence", f"{safe_float(latest['BOARD_INDEPENDENT_PCT']):.0f}%")
                st.metric("Women on Board", f"{safe_float(latest['BOARD_WOMEN_PCT']):.0f}%")
                st.metric("Ethics Training", f"{safe_float(latest['ETHICS_TRAINING_PCT']):.0f}%")
                if latest["SET_ESG_RATING"]:
                    st.success("SET ESG Rating ✓")

            st.markdown("---")

            # Certifications & Ratings
            st.subheader("Certifications & Recognitions")
            certs = []
            if latest["ISO14001_CERTIFIED"]: certs.append("ISO 14001")
            if latest["ISO45001_CERTIFIED"]: certs.append("ISO 45001")
            if latest["SET_ESG_RATING"]: certs.append("SET ESG Rating")
            if latest["THSI_MEMBER"]: certs.append("THSI Member")
            if latest["EXTERNAL_ASSURANCE"]: certs.append(f"Assured by {latest['ASSURANCE_PROVIDER']}")

            if certs:
                st.write(" | ".join(certs))
            else:
                st.info("No certifications recorded")

            # All reports
            st.markdown("---")
            st.subheader("All One Reports")
            display_cols = ["REPORT_YEAR", "REPORT_STATUS", "SECTOR", "CGR_SCORE", "SET_ESG_RATING", "CREATED_AT"]
            st.dataframe(df[display_cols], use_container_width=True)

    # === ENVIRONMENTAL ===
    with tab2:
        st.subheader("Environmental Data (ด้านสิ่งแวดล้อม)")

        # Select year or create new
        years = df["REPORT_YEAR"].tolist() if not df.empty else []
        year_options = ["Create New Report"] + [f"Edit FY{y}" for y in years]
        action = st.selectbox("Select Action", year_options, key="env_action")

        if action == "Create New Report":
            report_year = st.number_input("Report Year", value=2024, min_value=2020, max_value=2030, key="env_year")
            r = {}  # Empty defaults
        else:
            report_year = int(action.replace("Edit FY", ""))
            r = df[df["REPORT_YEAR"] == report_year].iloc[0].to_dict()

        with st.form("env_form"):
            col1, col2 = st.columns(2)
            with col1:
                sector = st.selectbox("SET Sector", ["Technology", "Services", "Industrial", "Property & Construction",
                                                     "Resources", "Consumer Products", "Agro & Food", "Financials"],
                                     index=0)
                status = st.selectbox("Status", ["Draft", "In Review", "Submitted to SET", "Approved"],
                                     index=["Draft", "In Review", "Submitted to SET", "Approved"].index(r.get("REPORT_STATUS", "Draft")) if r else 0)

            st.markdown("---")
            st.markdown("### Climate & GHG Emissions (การปล่อยก๊าซเรือนกระจก)")
            col1, col2, col3 = st.columns(3)
            with col1:
                scope1 = st.number_input("Scope 1 (tCO2e)", value=float(r.get("GHG_SCOPE1_TCO2E") or 8500), help="Direct emissions")
                scope2 = st.number_input("Scope 2 (tCO2e)", value=float(r.get("GHG_SCOPE2_TCO2E") or 4200), help="Electricity")
            with col2:
                scope3 = st.number_input("Scope 3 (tCO2e)", value=float(r.get("GHG_SCOPE3_TCO2E") or 45000), help="Value chain")
                ghg_target = st.number_input("GHG Reduction Target %", value=float(r.get("GHG_REDUCTION_TARGET_PCT") or 15))
            with col3:
                ghg_achieved = st.number_input("GHG Reduction Achieved %", value=float(r.get("GHG_REDUCTION_ACHIEVED_PCT") or 12))

            st.markdown("### Energy (พลังงาน)")
            col1, col2, col3 = st.columns(3)
            with col1:
                energy_total = st.number_input("Total Energy (MWh)", value=float(r.get("ENERGY_TOTAL_MWH") or 25000))
            with col2:
                energy_renewable = st.number_input("Renewable Energy (MWh)", value=float(r.get("ENERGY_RENEWABLE_MWH") or 8750))
            with col3:
                solar_kw = st.number_input("Solar Installed (kW)", value=float(r.get("SOLAR_INSTALLED_KW") or 500))

            st.markdown("### Water & Waste (น้ำและของเสีย)")
            col1, col2, col3 = st.columns(3)
            with col1:
                water = st.number_input("Water (m³)", value=float(r.get("WATER_CONSUMPTION_M3") or 180000))
                water_recycled = st.number_input("Water Recycled %", value=float(r.get("WATER_RECYCLED_PCT") or 35))
            with col2:
                waste = st.number_input("Waste (tons)", value=float(r.get("WASTE_TOTAL_TONS") or 450))
                waste_recycled = st.number_input("Waste Recycled %", value=float(r.get("WASTE_RECYCLED_PCT") or 75))
            with col3:
                hazardous = st.number_input("Hazardous Waste (tons)", value=float(r.get("HAZARDOUS_WASTE_TONS") or 12))
                zero_waste = st.checkbox("Zero Waste to Landfill Target", value=bool(r.get("ZERO_WASTE_TO_LANDFILL")))

            st.markdown("### Compliance")
            col1, col2, col3 = st.columns(3)
            with col1:
                violations = st.number_input("Environmental Violations", value=int(r.get("ENV_VIOLATIONS") or 0), min_value=0)
            with col2:
                fines = st.number_input("Fines (THB)", value=float(r.get("ENV_FINES_THB") or 0))
            with col3:
                iso14001 = st.checkbox("ISO 14001 Certified", value=bool(r.get("ISO14001_CERTIFIED")))

            if st.form_submit_button("Save Environmental Data"):
                if action == "Create New Report":
                    sql = f"""INSERT INTO ESG_METRICS (REPORT_YEAR, REPORT_STATUS, SECTOR,
                        GHG_SCOPE1_TCO2E, GHG_SCOPE2_TCO2E, GHG_SCOPE3_TCO2E, GHG_REDUCTION_TARGET_PCT, GHG_REDUCTION_ACHIEVED_PCT,
                        ENERGY_TOTAL_MWH, ENERGY_RENEWABLE_MWH, SOLAR_INSTALLED_KW,
                        WATER_CONSUMPTION_M3, WATER_RECYCLED_PCT, WASTE_TOTAL_TONS, WASTE_RECYCLED_PCT, HAZARDOUS_WASTE_TONS, ZERO_WASTE_TO_LANDFILL,
                        ENV_VIOLATIONS, ENV_FINES_THB, ISO14001_CERTIFIED)
                    VALUES ({report_year}, '{status}', '{sector}',
                        {scope1}, {scope2}, {scope3}, {ghg_target}, {ghg_achieved},
                        {energy_total}, {energy_renewable}, {solar_kw},
                        {water}, {water_recycled}, {waste}, {waste_recycled}, {hazardous}, {zero_waste},
                        {violations}, {fines}, {iso14001})"""
                else:
                    sql = f"""UPDATE ESG_METRICS SET
                        REPORT_STATUS = '{status}', SECTOR = '{sector}',
                        GHG_SCOPE1_TCO2E = {scope1}, GHG_SCOPE2_TCO2E = {scope2}, GHG_SCOPE3_TCO2E = {scope3},
                        GHG_REDUCTION_TARGET_PCT = {ghg_target}, GHG_REDUCTION_ACHIEVED_PCT = {ghg_achieved},
                        ENERGY_TOTAL_MWH = {energy_total}, ENERGY_RENEWABLE_MWH = {energy_renewable}, SOLAR_INSTALLED_KW = {solar_kw},
                        WATER_CONSUMPTION_M3 = {water}, WATER_RECYCLED_PCT = {water_recycled},
                        WASTE_TOTAL_TONS = {waste}, WASTE_RECYCLED_PCT = {waste_recycled}, HAZARDOUS_WASTE_TONS = {hazardous},
                        ZERO_WASTE_TO_LANDFILL = {zero_waste}, ENV_VIOLATIONS = {violations}, ENV_FINES_THB = {fines},
                        ISO14001_CERTIFIED = {iso14001}, UPDATED_BY = CURRENT_USER(), UPDATED_AT = CURRENT_TIMESTAMP()
                    WHERE REPORT_YEAR = {report_year}"""
                try:
                    session.sql(sql).collect()
                    st.session_state.message = ("success", f"Environmental data saved for FY{report_year}!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    # === SOCIAL ===
    with tab3:
        st.subheader("Social Data (ด้านสังคม)")

        if df.empty:
            st.warning("Please create a report in Environmental tab first")
        else:
            year = st.selectbox("Select Report Year", df["REPORT_YEAR"].tolist(), key="social_year")
            r = df[df["REPORT_YEAR"] == year].iloc[0].to_dict()

            with st.form("social_form"):
                st.markdown("### Workforce (พนักงาน)")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    emp_total = st.number_input("Total Employees", value=safe_int(r.get("EMPLOYEES_TOTAL"), 1850))
                with col2:
                    emp_perm = st.number_input("Permanent", value=safe_int(r.get("EMPLOYEES_PERMANENT"), 1650))
                with col3:
                    new_hires = st.number_input("New Hires", value=safe_int(r.get("NEW_HIRES"), 280))
                with col4:
                    turnover = st.number_input("Turnover %", value=safe_float(r.get("TURNOVER_RATE_PCT"), 8.5))

                st.markdown("### Diversity (ความหลากหลาย)")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    women_total = st.number_input("Women Total %", value=safe_float(r.get("WOMEN_WORKFORCE_PCT"), 45.0))
                with col2:
                    women_mgmt = st.number_input("Women Management %", value=safe_float(r.get("WOMEN_MANAGEMENT_PCT"), 38.0))
                with col3:
                    women_exec = st.number_input("Women Executive %", value=safe_float(r.get("WOMEN_EXECUTIVE_PCT"), 25.0))
                with col4:
                    disabled = st.number_input("Disabled Employees", value=safe_int(r.get("DISABLED_EMPLOYEES"), 28))

                st.markdown("### Health & Safety (ความปลอดภัย)")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    lti = st.number_input("Lost Time Injuries", value=safe_int(r.get("LOST_TIME_INJURIES"), 3))
                with col2:
                    injury_rate = st.number_input("Injury Rate", value=safe_float(r.get("INJURY_RATE"), 0.42))
                with col3:
                    fatalities = st.number_input("Fatalities", value=safe_int(r.get("FATALITIES"), 0))
                with col4:
                    iso45001 = st.checkbox("ISO 45001 Certified", value=bool(r.get("ISO45001_CERTIFIED")))

                st.markdown("### Training (การฝึกอบรม)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    training_hrs = st.number_input("Avg Training Hours", value=safe_float(r.get("TRAINING_HOURS_AVG"), 28.0))
                with col2:
                    training_budget = st.number_input("Training Budget (THB)", value=safe_float(r.get("TRAINING_BUDGET_THB"), 2800000.0))
                with col3:
                    career_dev = st.checkbox("Career Development Program", value=bool(r.get("CAREER_DEVELOPMENT_PROGRAM")))

                st.markdown("### Community & Supply Chain")
                col1, col2, col3 = st.columns(3)
                with col1:
                    csr_budget = st.number_input("CSR Budget (THB)", value=safe_float(r.get("CSR_BUDGET_THB"), 5500000.0))
                with col2:
                    local_supplier = st.number_input("Local Supplier %", value=safe_float(r.get("LOCAL_SUPPLIER_PCT"), 72.0))
                with col3:
                    supplier_code = st.checkbox("Supplier Code of Conduct", value=bool(r.get("SUPPLIER_CODE_OF_CONDUCT")))

                if st.form_submit_button("Save Social Data"):
                    sql = f"""UPDATE ESG_METRICS SET
                        EMPLOYEES_TOTAL = {emp_total}, EMPLOYEES_PERMANENT = {emp_perm}, NEW_HIRES = {new_hires}, TURNOVER_RATE_PCT = {turnover},
                        WOMEN_WORKFORCE_PCT = {women_total}, WOMEN_MANAGEMENT_PCT = {women_mgmt}, WOMEN_EXECUTIVE_PCT = {women_exec}, DISABLED_EMPLOYEES = {disabled},
                        LOST_TIME_INJURIES = {lti}, INJURY_RATE = {injury_rate}, FATALITIES = {fatalities}, ISO45001_CERTIFIED = {iso45001},
                        TRAINING_HOURS_AVG = {training_hrs}, TRAINING_BUDGET_THB = {training_budget}, CAREER_DEVELOPMENT_PROGRAM = {career_dev},
                        CSR_BUDGET_THB = {csr_budget}, LOCAL_SUPPLIER_PCT = {local_supplier}, SUPPLIER_CODE_OF_CONDUCT = {supplier_code},
                        UPDATED_BY = CURRENT_USER(), UPDATED_AT = CURRENT_TIMESTAMP()
                    WHERE REPORT_YEAR = {year}"""
                    try:
                        session.sql(sql).collect()
                        st.session_state.message = ("success", f"Social data saved for FY{year}!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # === GOVERNANCE ===
    with tab4:
        st.subheader("Governance Data (ด้านธรรมาภิบาล)")

        if df.empty:
            st.warning("Please create a report in Environmental tab first")
        else:
            year = st.selectbox("Select Report Year", df["REPORT_YEAR"].tolist(), key="gov_year")
            r = df[df["REPORT_YEAR"] == year].iloc[0].to_dict()

            with st.form("gov_form"):
                st.markdown("### Board Composition (คณะกรรมการ)")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    board_total = st.number_input("Board Members", value=safe_int(r.get("BOARD_TOTAL"), 11))
                with col2:
                    board_ind = st.number_input("Independent %", value=safe_float(r.get("BOARD_INDEPENDENT_PCT"), 45.0))
                with col3:
                    board_women = st.number_input("Women on Board %", value=safe_float(r.get("BOARD_WOMEN_PCT"), 27.0))
                with col4:
                    board_meetings = st.number_input("Meetings/Year", value=safe_int(r.get("BOARD_MEETINGS_YEAR"), 12))

                st.markdown("### Committees")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    audit_comm = st.checkbox("Audit Committee", value=bool(r.get("HAS_AUDIT_COMMITTEE", True)))
                with col2:
                    risk_comm = st.checkbox("Risk Committee", value=bool(r.get("HAS_RISK_COMMITTEE")))
                with col3:
                    cg_comm = st.checkbox("CG/Nomination Committee", value=bool(r.get("HAS_CG_COMMITTEE")))
                with col4:
                    sustain_comm = st.checkbox("Sustainability Committee", value=bool(r.get("HAS_SUSTAINABILITY_COMMITTEE")))

                st.markdown("### Ethics & Anti-Corruption")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    code_conduct = st.checkbox("Code of Conduct", value=bool(r.get("CODE_OF_CONDUCT", True)))
                with col2:
                    anti_corrupt = st.checkbox("Anti-Corruption Policy", value=bool(r.get("ANTI_CORRUPTION_POLICY", True)))
                with col3:
                    whistleblower = st.checkbox("Whistleblower Policy", value=bool(r.get("WHISTLEBLOWER_POLICY", True)))
                with col4:
                    ethics_pct = st.number_input("Ethics Training %", value=safe_float(r.get("ETHICS_TRAINING_PCT"), 98.0))

                st.markdown("### Ratings & Certifications")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    cgr = st.selectbox("CGR Score (IOD)", ["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"],
                                      index=["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"].index(r.get("CGR_SCORE", "4 Stars")) if r.get("CGR_SCORE") else 3)
                with col2:
                    set_esg = st.checkbox("SET ESG Rating", value=bool(r.get("SET_ESG_RATING")))
                with col3:
                    thsi = st.checkbox("THSI Member", value=bool(r.get("THSI_MEMBER")))
                with col4:
                    external_assure = st.checkbox("External Assurance", value=bool(r.get("EXTERNAL_ASSURANCE")))

                assurance_provider = st.text_input("Assurance Provider", value=str(r.get("ASSURANCE_PROVIDER") or ""))
                notes = st.text_area("Notes for SET Submission", value=str(r.get("NOTES") or ""))

                if st.form_submit_button("Save Governance Data"):
                    sql = f"""UPDATE ESG_METRICS SET
                        BOARD_TOTAL = {board_total}, BOARD_INDEPENDENT_PCT = {board_ind}, BOARD_WOMEN_PCT = {board_women}, BOARD_MEETINGS_YEAR = {board_meetings},
                        HAS_AUDIT_COMMITTEE = {audit_comm}, HAS_RISK_COMMITTEE = {risk_comm}, HAS_CG_COMMITTEE = {cg_comm}, HAS_SUSTAINABILITY_COMMITTEE = {sustain_comm},
                        CODE_OF_CONDUCT = {code_conduct}, ANTI_CORRUPTION_POLICY = {anti_corrupt}, WHISTLEBLOWER_POLICY = {whistleblower}, ETHICS_TRAINING_PCT = {ethics_pct},
                        CGR_SCORE = '{cgr}', SET_ESG_RATING = {set_esg}, THSI_MEMBER = {thsi},
                        EXTERNAL_ASSURANCE = {external_assure}, ASSURANCE_PROVIDER = '{assurance_provider}', NOTES = '{notes.replace("'", "''")}',
                        UPDATED_BY = CURRENT_USER(), UPDATED_AT = CURRENT_TIMESTAMP()
                    WHERE REPORT_YEAR = {year}"""
                    try:
                        session.sql(sql).collect()
                        st.session_state.message = ("success", f"Governance data saved for FY{year}!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

            st.markdown("---")
            st.subheader("Export for SET Submission")
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download One Report Data (CSV)",
                data=csv,
                file_name=f"one_report_56-1_{date.today().isoformat()}.csv",
                mime="text/csv"
            )

except Exception as e:
    st.error(f"Error: {e}")
