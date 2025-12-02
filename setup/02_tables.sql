-- ESG Metrics Table
-- Contains Environmental, Social, and Governance reporting data

USE DATABASE ESG_REPORTING;
USE SCHEMA PROD;

CREATE TABLE IF NOT EXISTS ESG_METRICS (
    -- Primary Key
    id INTEGER AUTOINCREMENT PRIMARY KEY,

    -- Organization Info
    organization_name VARCHAR(255) NOT NULL,
    reporting_year INTEGER NOT NULL,
    reporting_date DATE,

    -- Environmental Metrics
    ghg_scope1_mtco2e DECIMAL(15,2) COMMENT 'Direct GHG emissions (metric tons CO2e)',
    ghg_scope2_mtco2e DECIMAL(15,2) COMMENT 'Indirect GHG emissions from energy',
    energy_consumption_mwh DECIMAL(15,2) COMMENT 'Total energy consumption (MWh)',
    renewable_energy_pct DECIMAL(5,2) COMMENT 'Percentage of renewable energy',
    water_consumption_m3 DECIMAL(15,2) COMMENT 'Water consumption (cubic meters)',
    waste_generated_tons DECIMAL(15,2) COMMENT 'Total waste generated (tons)',
    waste_recycled_pct DECIMAL(5,2) COMMENT 'Percentage of waste recycled',

    -- Social Metrics
    total_employees INTEGER COMMENT 'Total employee headcount',
    female_employees_pct DECIMAL(5,2) COMMENT 'Percentage of female employees',
    employee_turnover_pct DECIMAL(5,2) COMMENT 'Annual employee turnover rate',
    safety_incidents INTEGER COMMENT 'Number of recordable safety incidents',
    training_hours_per_employee DECIMAL(8,2) COMMENT 'Average training hours per employee',

    -- Governance Metrics
    board_size INTEGER COMMENT 'Number of board members',
    board_independence_pct DECIMAL(5,2) COMMENT 'Percentage of independent directors',
    board_female_pct DECIMAL(5,2) COMMENT 'Percentage of female board members',
    has_ethics_policy BOOLEAN DEFAULT FALSE COMMENT 'Has formal ethics policy',
    has_whistleblower_policy BOOLEAN DEFAULT FALSE COMMENT 'Has whistleblower protection policy',

    -- Metadata
    notes TEXT COMMENT 'Additional notes or comments',
    created_by VARCHAR(100) DEFAULT CURRENT_USER(),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_by VARCHAR(100),
    updated_at TIMESTAMP_NTZ,

    -- Note: Validation done in application layer (Snowflake doesn't support CHECK constraints)
    UNIQUE (organization_name, reporting_year)
);

-- Create stage for data exports
CREATE STAGE IF NOT EXISTS EXPORT_STAGE
    FILE_FORMAT = (
        TYPE = CSV
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        SKIP_HEADER = 0
    );

-- Create view for easy reporting
CREATE OR REPLACE VIEW ESG_REPORT_VIEW AS
SELECT
    id,
    organization_name,
    reporting_year,
    reporting_date,
    -- Environmental
    ghg_scope1_mtco2e,
    ghg_scope2_mtco2e,
    ghg_scope1_mtco2e + COALESCE(ghg_scope2_mtco2e, 0) AS total_ghg_emissions,
    energy_consumption_mwh,
    renewable_energy_pct,
    water_consumption_m3,
    waste_generated_tons,
    waste_recycled_pct,
    -- Social
    total_employees,
    female_employees_pct,
    employee_turnover_pct,
    safety_incidents,
    training_hours_per_employee,
    -- Governance
    board_size,
    board_independence_pct,
    board_female_pct,
    has_ethics_policy,
    has_whistleblower_policy,
    -- Metadata
    notes,
    created_at,
    updated_at
FROM ESG_METRICS
ORDER BY reporting_year DESC, organization_name;
