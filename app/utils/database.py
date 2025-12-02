"""
Database utilities for ESG Reporting application.
Handles all Snowflake database operations.
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, current_user, current_timestamp
import pandas as pd
from typing import Optional, Dict, Any, List


def get_session():
    """Get the active Snowpark session."""
    return get_active_session()


@st.cache_data(ttl=60)
def get_all_records() -> pd.DataFrame:
    """Fetch all ESG records from the database."""
    session = get_session()
    df = session.table("ESG_METRICS").order_by(
        col("REPORTING_YEAR").desc(),
        col("ORGANIZATION_NAME")
    ).to_pandas()
    return df


def get_record_by_id(record_id: int) -> Optional[pd.DataFrame]:
    """Fetch a single record by ID."""
    session = get_session()
    df = session.table("ESG_METRICS").filter(
        col("ID") == record_id
    ).to_pandas()
    return df if not df.empty else None


def create_record(data: Dict[str, Any]) -> bool:
    """Create a new ESG record."""
    session = get_session()

    columns = ", ".join(data.keys())
    placeholders = ", ".join([f"'{v}'" if isinstance(v, str) else
                              f"'{v}'" if isinstance(v, bool) else
                              str(v) if v is not None else "NULL"
                              for v in data.values()])

    sql = f"""
    INSERT INTO ESG_METRICS ({columns}, CREATED_BY, CREATED_AT)
    VALUES ({placeholders}, CURRENT_USER(), CURRENT_TIMESTAMP())
    """

    try:
        session.sql(sql).collect()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error creating record: {e}")
        return False


def update_record(record_id: int, data: Dict[str, Any]) -> bool:
    """Update an existing ESG record."""
    session = get_session()

    set_clauses = []
    for key, value in data.items():
        if value is None:
            set_clauses.append(f"{key} = NULL")
        elif isinstance(value, bool):
            set_clauses.append(f"{key} = {str(value).upper()}")
        elif isinstance(value, str):
            escaped_value = value.replace("'", "''")
            set_clauses.append(f"{key} = '{escaped_value}'")
        else:
            set_clauses.append(f"{key} = {value}")

    set_clause = ", ".join(set_clauses)

    sql = f"""
    UPDATE ESG_METRICS
    SET {set_clause},
        UPDATED_BY = CURRENT_USER(),
        UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE ID = {record_id}
    """

    try:
        session.sql(sql).collect()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error updating record: {e}")
        return False


def delete_record(record_id: int) -> bool:
    """Delete an ESG record by ID."""
    session = get_session()

    sql = f"DELETE FROM ESG_METRICS WHERE ID = {record_id}"

    try:
        session.sql(sql).collect()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error deleting record: {e}")
        return False


def get_years() -> List[int]:
    """Get list of available reporting years."""
    session = get_session()
    result = session.sql("""
        SELECT DISTINCT REPORTING_YEAR
        FROM ESG_METRICS
        ORDER BY REPORTING_YEAR DESC
    """).to_pandas()
    return result["REPORTING_YEAR"].tolist()


def get_organizations() -> List[str]:
    """Get list of organizations."""
    session = get_session()
    result = session.sql("""
        SELECT DISTINCT ORGANIZATION_NAME
        FROM ESG_METRICS
        ORDER BY ORGANIZATION_NAME
    """).to_pandas()
    return result["ORGANIZATION_NAME"].tolist()


def get_summary_stats() -> Dict[str, Any]:
    """Get summary statistics for dashboard."""
    session = get_session()

    result = session.sql("""
        SELECT
            COUNT(*) as total_records,
            COUNT(DISTINCT ORGANIZATION_NAME) as total_orgs,
            COUNT(DISTINCT REPORTING_YEAR) as total_years,
            MAX(REPORTING_YEAR) as latest_year,
            SUM(CASE WHEN REPORTING_YEAR = (SELECT MAX(REPORTING_YEAR) FROM ESG_METRICS)
                THEN GHG_SCOPE1_MTCO2E + COALESCE(GHG_SCOPE2_MTCO2E, 0) ELSE 0 END) as latest_emissions,
            AVG(CASE WHEN REPORTING_YEAR = (SELECT MAX(REPORTING_YEAR) FROM ESG_METRICS)
                THEN RENEWABLE_ENERGY_PCT ELSE NULL END) as avg_renewable_pct
        FROM ESG_METRICS
    """).to_pandas()

    return result.iloc[0].to_dict() if not result.empty else {}
