-- Aqua-Sense: Software-Based Water Quality Analysis System
-- PostgreSQL Database Initialization Script

-- 1. Create Database (Run this in psql or pgAdmin as superuser)
-- CREATE DATABASE water_quality_db;
-- \c water_quality_db;

-- 2. Water Test Records Table
CREATE TABLE IF NOT EXISTS water_test_records (
    id SERIAL PRIMARY KEY,
    sample_name VARCHAR(120) NOT NULL,
    water_source VARCHAR(100) NOT NULL DEFAULT 'Municipal Tap',
    location VARCHAR(200) NOT NULL DEFAULT 'General Sampling Site',
    tested_by VARCHAR(100) NOT NULL DEFAULT 'Analyst',
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ph DOUBLE PRECISION NOT NULL,
    tds DOUBLE PRECISION NOT NULL,
    turbidity DOUBLE PRECISION NOT NULL,
    hardness DOUBLE PRECISION NOT NULL,
    chlorine DOUBLE PRECISION NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    overall_status VARCHAR(50) NOT NULL,
    wqi_score DOUBLE PRECISION NOT NULL,
    status_summary TEXT,
    evaluations_json TEXT,
    recommendations_json TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_test_records_timestamp ON water_test_records(timestamp);
CREATE INDEX IF NOT EXISTS idx_test_records_status ON water_test_records(overall_status);

-- 3. Reference Limits Table
CREATE TABLE IF NOT EXISTS reference_limits (
    parameter_key VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    min_safe DOUBLE PRECISION,
    max_safe DOUBLE PRECISION,
    ideal_value DOUBLE PRECISION,
    description VARCHAR(255),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Seed Standard WHO / EPA Potability Reference Limits
INSERT INTO reference_limits (parameter_key, display_name, unit, min_safe, max_safe, ideal_value, description)
VALUES
    ('ph', 'pH Level', 'pH', 6.5, 8.5, 7.0, 'Safe acidity range for potable and domestic use.'),
    ('tds', 'Total Dissolved Solids', 'ppm', 50.0, 500.0, 150.0, 'Combined mineral and dissolved organic matter content.'),
    ('turbidity', 'Turbidity', 'NTU', 0.0, 5.0, 0.5, 'Cloudiness caused by suspended particulates and sediments.'),
    ('hardness', 'Total Hardness', 'mg/L as CaCO3', 0.0, 200.0, 100.0, 'Concentration of dissolved calcium and magnesium ions.'),
    ('chlorine', 'Free Residual Chlorine', 'ppm (mg/L)', 0.2, 2.0, 0.5, 'Active disinfectant residual preventing bacterial regrowth.'),
    ('temperature', 'Temperature', '°C', 12.0, 25.0, 20.0, 'Thermal condition affecting gas solubility and kinetics.')
ON CONFLICT (parameter_key) DO NOTHING;
