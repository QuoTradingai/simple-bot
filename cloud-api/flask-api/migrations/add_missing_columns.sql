-- Add missing columns to users table for full admin dashboard functionality

-- Add account_id column (if not exists) - using license_key as account_id
-- Note: We'll use the existing 'id' column as account_id in queries

-- Add stripe_customer_id for Stripe integration
ALTER TABLE users ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(100);

-- Add last_active for tracking user activity
-- This will be updated from api_logs queries, not stored directly

-- Add notes field for admin notes
ALTER TABLE users ADD COLUMN IF NOT EXISTS notes TEXT;

-- Create index for stripe_customer_id
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer ON users(stripe_customer_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE users TO quotradingadmin;
