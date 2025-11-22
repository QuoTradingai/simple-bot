-- QuoTrading Production Database Initialization
-- Run this against PostgreSQL: quotrading-db.postgres.database.azure.com

-- Users table for license management
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255),
    license_type VARCHAR(20) NOT NULL DEFAULT 'standard',
    license_status VARCHAR(20) NOT NULL DEFAULT 'active',
    license_expiration TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API usage logs
CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(50) NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    request_data JSONB,
    response_data JSONB,
    status_code INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trade history tracking
CREATE TABLE IF NOT EXISTS trade_history (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,
    entry_price DECIMAL(10, 2),
    exit_price DECIMAL(10, 2),
    pnl DECIMAL(10, 2),
    confidence DECIMAL(5, 2),
    regime VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create admin user
INSERT INTO users (license_key, email, license_type, license_status, license_expiration)
VALUES ('ADMIN-DEV-KEY-2024', 'admin@quotrading.com', 'admin', 'active', '2026-12-31 23:59:59')
ON CONFLICT (license_key) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_license_key ON users(license_key);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(license_status);
CREATE INDEX IF NOT EXISTS idx_api_logs_license_key ON api_logs(license_key);
CREATE INDEX IF NOT EXISTS idx_api_logs_created_at ON api_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_trade_history_license_key ON trade_history(license_key);
CREATE INDEX IF NOT EXISTS idx_trade_history_created_at ON trade_history(created_at);
