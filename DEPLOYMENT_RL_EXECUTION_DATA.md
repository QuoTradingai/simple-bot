# Deploying RL Execution Data Enhancement

## Overview
This update ensures that after every trade, complete execution data is saved to the cloud RL system, allowing the RL brain to learn from execution quality, not just P&L.

## What Was Added

### 1. Execution Data Captured
The following execution quality metrics are now captured and sent to cloud RL:
- **order_type_used**: Whether order was passive (limit), aggressive (market), or mixed
- **entry_slippage_ticks**: Actual slippage in ticks from expected entry price
- **partial_fill**: Whether order was only partially filled
- **fill_ratio**: Ratio of filled contracts to requested (1.0 = fully filled)
- **exit_reason**: How trade closed (target_reached, stop_loss, timeout, etc.)
- **held_full_duration**: Whether trade hit target/stop or exited early

### 2. Code Changes
- **src/cloud_api.py**: Updated `report_trade_outcome()` to accept and send execution_data
- **src/quotrading_engine.py**: Updated to pass execution_data to cloud API
- **cloud-api/flask-api/app.py**: Updated `submit_outcome()` to store execution_data in database

### 3. Database Migration
- **New file**: `cloud-api/flask-api/migrations/add_execution_data_to_rl_experiences.sql`
- Adds 6 new columns to `rl_experiences` table for execution quality metrics

## Deployment Steps

### Step 1: Run Database Migration
Connect to your Azure PostgreSQL database and run the migration:

```bash
# Option A: Using Azure CLI
az login
az postgres flexible-server execute \
  --name quotrading-db \
  --admin-user quotradingadmin \
  --admin-password YOUR_PASSWORD \
  --database-name quotrading \
  --file-path cloud-api/flask-api/migrations/add_execution_data_to_rl_experiences.sql

# Option B: Using psql directly
psql -h quotrading-db.postgres.database.azure.com \
     -U quotradingadmin \
     -d quotrading \
     -f cloud-api/flask-api/migrations/add_execution_data_to_rl_experiences.sql
```

Verify the migration:
```sql
-- Check that new columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'rl_experiences' 
  AND column_name IN ('order_type_used', 'entry_slippage_ticks', 'exit_reason');
```

### Step 2: Deploy Updated Flask API
Deploy the updated Flask API to Azure Container Apps:

```bash
cd cloud-api/flask-api

# Build and deploy
az containerapp up \
  --name quotrading-signals \
  --resource-group quotrading-rg \
  --source .
```

Or if using zip deployment:
```bash
# Create deployment package
zip -r deploy.zip app.py requirements.txt

# Deploy to Azure
az webapp deployment source config-zip \
  --resource-group quotrading-rg \
  --name quotrading-flask-api \
  --src deploy.zip
```

### Step 3: Validate Deployment
Run the validation script to ensure everything is configured correctly:

```bash
python scripts/validate_rl_execution_data.py
```

Expected output:
```
✅ ALL CHECKS PASSED (4/4)
Execution data will be captured and sent to cloud RL for learning!
```

### Step 4: Test with Live Trading
Start a live trading session and verify execution data is being captured:

1. Start the bot in live mode
2. Wait for a trade to execute
3. Check Azure PostgreSQL to verify execution data is saved:

```sql
-- View recent trades with execution data
SELECT 
    symbol,
    side,
    pnl,
    order_type_used,
    entry_slippage_ticks,
    exit_reason,
    partial_fill,
    created_at
FROM rl_experiences
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC
LIMIT 10;
```

## Benefits

### For RL Learning
The RL system can now learn from:
1. **Execution quality**: Whether aggressive or passive orders work better in different market conditions
2. **Slippage patterns**: Which setups have lower slippage
3. **Exit reasons**: Whether targets are being hit or stops are being triggered
4. **Fill quality**: Whether partial fills are affecting performance

### For Trade Analysis
You can now analyze:
- Average slippage by time of day
- Exit reason distribution
- Correlation between order type and P&L
- Impact of partial fills on performance

## Rollback Plan

If you need to rollback:

```sql
-- Rollback database changes (optional - columns can stay as they're nullable)
ALTER TABLE rl_experiences 
DROP COLUMN IF EXISTS order_type_used,
DROP COLUMN IF EXISTS entry_slippage_ticks,
DROP COLUMN IF EXISTS partial_fill,
DROP COLUMN IF EXISTS fill_ratio,
DROP COLUMN IF EXISTS exit_reason,
DROP COLUMN IF EXISTS held_full_duration;
```

Then redeploy the previous version of the Flask API.

## Monitoring

After deployment, monitor:
1. **API logs**: Check for any errors in submit-outcome endpoint
2. **Database queries**: Ensure inserts are completing successfully
3. **Bot logs**: Verify "Outcome reported to cloud" messages appear
4. **Data completeness**: Check that execution_data fields are populated

## Support

If you encounter issues:
1. Check Flask API logs: `az containerapp logs show --name quotrading-signals --resource-group quotrading-rg`
2. Check PostgreSQL logs
3. Run validation script: `python scripts/validate_rl_execution_data.py`
4. Check bot logs for "Outcome reported to cloud" messages

## Summary

✅ Execution data now captured after every trade
✅ Cloud RL can learn from execution quality, not just P&L
✅ Database migration adds execution tracking columns
✅ Backward compatible (execution_data is optional)
✅ Validation script ensures proper configuration
