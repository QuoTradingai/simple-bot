# QuoTrading ML/RL Backup - November 8, 2025
# CRITICAL: This contains all learned intelligence and settings

## Configuration Settings (config.json)
```json
{
  "quotrading_license": "QUOTRADING_ADMIN_MASTER_2025",
  "market_type": "Futures",
  "broker": "TopStep",
  "broker_token": "0lqxI8Gt4JRDhbuP9wOoHmdxJE49fIQCxIU+mSbPqGs=",
  "broker_username": "alvarezjose4201@gmail.com",
  "symbols": ["ES"],
  "account_size": 50000.0,
  "max_contracts": 1,
  "max_trades_per_day": 9999,
  "risk_per_trade": 0.012,
  "min_risk_reward": 2.0,
  "daily_loss_limit": 1000.0,
  "auto_calculate_limits": true,
  "rl_confidence_threshold": 0.65,
  "rl_exploration_rate": 0.05,
  "rl_min_exploration_rate": 0.05,
  "rl_exploration_decay": 0.995,
  "username": "hi",
  "quotrading_email": "kevinsuero072897@gmail.com",
  "quotrading_api_key": "QUOTRADING_ADMIN_MASTER_2025",
  "quotrading_validated": true,
  "password": "admin",
  "user_api_key": "QUOTRADING_ADMIN_MASTER_2025",
  "validated": true,
  "user_data": {
    "email": "admin@quotrading.com",
    "account_type": "admin",
    "active": true
  },
  "broker_type": "Prop Firm",
  "account_type": "Trading Combine $50K",
  "broker_validated": true,
  "accounts": [
    {
      "id": "50KTC-V2-398684-33989413",
      "name": "50KTC-V2-398684-33989413",
      "balance": 50000.0,
      "equity": 50000.0,
      "type": "prop_firm"
    }
  ],
  "selected_account": "50KTC-V2-398684-33989413",
  "fetched_account_balance": 50000.0,
  "fetched_account_type": "prop_firm",
  "max_trades": 3,
  "confidence_threshold": 70.0,
  "shadow_mode": false
}
```

## ML/RL Brain Settings

### Signal Confidence RL
- **File**: `data/signal_experience.json`
- **Experiences Loaded**: 6,880 past trades
- **Confidence Threshold**: 70% (LIVE MODE - user setting)
- **Exploration Rate**: 0% in live mode (pure exploitation - NO RANDOM TRADES!)
- **Min Exploration**: 5%
- **Exploration Decay**: 0.995

### Adaptive Exit Manager
- **File**: `data/exit_experience.json`
- **Exit Experiences**: 2,961 past exits
- **Learning**: Enabled with RL learning

## Critical Files to Preserve

1. **Signal Learning Data**
   - Location: `data/signal_experience.json`
   - Size: 6,880 experiences
   - Contains: All learned signal patterns, outcomes, and confidence scores

2. **Exit Learning Data**
   - Location: `data/exit_experience.json`
   - Size: 2,961 experiences
   - Contains: Exit timing patterns, profit-taking strategies

3. **Bot Configuration**
   - Location: `config.json`
   - Contains: All user settings, broker credentials, account setup

4. **Historical Data**
   - Location: `data/historical_data/ES_1min.csv`
   - Location: `data/historical_data/ES_ticks.csv`
   - Contains: Market data for backtesting

## Trading Rules (Programmed)

### Position Sizing
- Risk per trade: 1.2% of account
- Max contracts: 1 (user setting)
- Max trades/day: 3
- Daily loss limit: $1,000

### Entry Conditions
- VWAP bounce (2.0 std dev bands)
- RSI extreme: <25 (long) or >75 (short)
- Volume spike: 1.5x average
- Trend filter: Optional (disabled by default)

### Exit Conditions
- Target: 2:1 reward-risk ratio
- Stop loss: 8 ticks default
- Adaptive exits: Enabled (ML-based)
- Time-based: Flatten at 4:45 PM ET

### Risk Management
- Auto-calculate limits: Enabled
- Prop firm max drawdown: 8%
- TopStep contract limits enforced
- Account mismatch detection: $5,000 threshold

## Recovery Instructions

If you ever need to restore:

1. **Copy this entire backup folder**
2. **Restore files**:
   - `config.json` → root
   - `data/signal_experience.json` → data/
   - `data/exit_experience.json` → data/
   - `data/historical_data/*.csv` → data/historical_data/

3. **Verify settings**:
   ```python
   import json
   with open('config.json') as f:
       config = json.load(f)
   print(f"RL Confidence: {config['rl_confidence_threshold']}")
   print(f"Risk per trade: {config['risk_per_trade']}")
   ```

## GitHub Backup Status
- Repository: https://github.com/Quotraders/simple-bot
- Last commit: "Add cloud signal engine for Azure deployment"
- Commit hash: 3a62513
- All code is backed up to GitHub

## IMPORTANT NOTES

⚠️ **DO NOT LOSE**:
- `data/signal_experience.json` - 6,880 trades of learning
- `data/exit_experience.json` - 2,961 exits of learning
- These files contain MONTHS of ML training data!

✅ **Safe to Recreate**:
- `config.json` - Can reconfigure manually
- Historical CSV files - Can re-download
- Bot state files - Regenerated on each run

## Cloud Deployment Settings

When deploying to Azure, use these settings:

```
DATABASE_URL=postgresql://quotrading_db_user:neSCC1nv8xSKcTRW24CMSygdmvoVTvys@dpg-d47h2hi4d50c7385trl0-a.oregon-postgres.render.com/quotrading_db
API_SECRET_KEY=change-this-in-production
STRIPE_SECRET_KEY=your_stripe_key_here
```

## Backup Date
Created: November 8, 2025 05:50 AM EST
System: Windows
Python: 3.13.7
Bot Version: Hybrid Architecture (Local + Cloud)
