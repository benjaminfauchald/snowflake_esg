-- Sample ESG Data for Demo
-- Realistic data based on typical corporate ESG disclosures

USE DATABASE ESG_REPORTING;
USE SCHEMA PROD;

-- Clear existing sample data (optional - comment out if you want to keep existing data)
-- TRUNCATE TABLE ESG_METRICS;

-- Insert sample ESG records for demo organization
INSERT INTO ESG_METRICS (
    organization_name, reporting_year, reporting_date,
    -- Environmental
    ghg_scope1_mtco2e, ghg_scope2_mtco2e, energy_consumption_mwh,
    renewable_energy_pct, water_consumption_m3, waste_generated_tons, waste_recycled_pct,
    -- Social
    total_employees, female_employees_pct, employee_turnover_pct,
    safety_incidents, training_hours_per_employee,
    -- Governance
    board_size, board_independence_pct, board_female_pct,
    has_ethics_policy, has_whistleblower_policy,
    notes
) VALUES
-- 2024 Data (most recent)
(
    'Acme Corporation', 2024, '2024-03-31',
    12500.00, 8200.00, 45000.00,
    35.00, 125000.00, 2800.00, 62.00,
    1250, 42.00, 12.50,
    3, 24.00,
    9, 78.00, 33.00,
    TRUE, TRUE,
    'Significant progress on renewable energy transition. New solar installation completed Q2.'
),
-- 2023 Data
(
    'Acme Corporation', 2023, '2023-03-31',
    14200.00, 9100.00, 48500.00,
    28.00, 132000.00, 3100.00, 55.00,
    1180, 40.00, 14.20,
    5, 22.00,
    9, 67.00, 22.00,
    TRUE, TRUE,
    'Launched sustainability program. Baseline year for many metrics.'
),
-- 2022 Data
(
    'Acme Corporation', 2022, '2022-03-31',
    15800.00, 10200.00, 52000.00,
    18.00, 145000.00, 3500.00, 48.00,
    1150, 38.00, 15.80,
    7, 18.00,
    8, 62.50, 12.50,
    TRUE, FALSE,
    'Pre-sustainability initiative baseline.'
),
-- 2021 Data (historical)
(
    'Acme Corporation', 2021, '2021-03-31',
    16500.00, 11000.00, 54000.00,
    12.00, 152000.00, 3800.00, 42.00,
    1100, 36.00, 16.50,
    9, 16.00,
    8, 62.50, 12.50,
    TRUE, FALSE,
    'COVID-19 impact year. Reduced office operations.'
),
-- Additional company for comparison
(
    'GreenTech Industries', 2024, '2024-03-31',
    5200.00, 3100.00, 28000.00,
    65.00, 45000.00, 1200.00, 78.00,
    620, 48.00, 8.50,
    1, 32.00,
    7, 86.00, 43.00,
    TRUE, TRUE,
    'Industry leader in sustainability. Carbon neutral target 2030.'
),
(
    'GreenTech Industries', 2023, '2023-03-31',
    6100.00, 3800.00, 31000.00,
    55.00, 52000.00, 1450.00, 72.00,
    580, 46.00, 9.20,
    2, 28.00,
    7, 86.00, 43.00,
    TRUE, TRUE,
    'Major renewable energy contract signed.'
);

-- Verify data
SELECT
    organization_name,
    reporting_year,
    ghg_scope1_mtco2e + ghg_scope2_mtco2e AS total_emissions,
    renewable_energy_pct,
    total_employees
FROM ESG_METRICS
ORDER BY organization_name, reporting_year DESC;
