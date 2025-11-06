# Environment Variable Configuration Guide

## ✅ Currently Configured in Your `.env`

Your `.env` file now includes:

### Core Settings
- `TOPSTEP_API_TOKEN` - Your broker API key ✅
- `TOPSTEP_USERNAME` - Your broker email ✅
- `BOT_ENVIRONMENT` - Environment mode (production) ✅
- `BOT_DRY_RUN` - Live vs paper trading (false = LIVE) ✅
- `CONFIRM_LIVE_TRADING` - Safety confirmation (1 = enabled) ✅
- `BOT_LOG_LEVEL` - Logging verbosity ✅

### Trading Configuration
- `BOT_INSTRUMENT` - Symbol to trade (ES) ✅
- `BOT_TIMEZONE` - Trading timezone (America/New_York) ✅

### Position Sizing (USER CONFIGURABLE)
- `BOT_MAX_CONTRACTS` - Maximum contracts (3) ✅
- `BOT_MAX_TRADES_PER_DAY` - Daily trade limit (9) ✅
- `BOT_RISK_PER_TRADE` - Risk percentage (0.012 = 1.2%) ✅
- `BOT_RISK_REWARD_RATIO` - Target profit ratio (2.0) ✅

### Risk Management
- `BOT_USE_TOPSTEP_RULES` - Auto risk calculation (true) ✅
- `BOT_TICK_SIZE` - Market tick size (0.25) ✅
- `BOT_TICK_VALUE` - Tick dollar value ($12.50) ✅

---

## 🎯 How Environment Variables Work

### Priority Order
1. **Environment Variable** (from `.env`) - HIGHEST PRIORITY
2. **Code Default** (from `config.py`) - FALLBACK

### Example
```python
# config.py default
max_contracts: int = 3

# .env override
BOT_MAX_CONTRACTS=10

# Result: Bot uses 10 contracts (env var wins)
```

---

## 📋 All Available Environment Variables

See `.env.example` for the complete list of 50+ configurable parameters including:

### Position Sizing
- `BOT_MAX_CONTRACTS` (1-25, cap at 25)
- `BOT_MAX_TRADES_PER_DAY`
- `BOT_RISK_PER_TRADE`
- `BOT_RISK_REWARD_RATIO`

### Risk Management
- `BOT_USE_TOPSTEP_RULES` (true/false)
- `BOT_DAILY_LOSS_PERCENT` (custom % if not using TopStep)
- `BOT_MAX_DRAWDOWN_PERCENT` (custom % if not using TopStep)
- `BOT_DAILY_LOSS_LIMIT` (manual override in dollars)

### VWAP Strategy
- `BOT_VWAP_STD_DEV_1` (warning band)
- `BOT_VWAP_STD_DEV_2` (entry band)
- `BOT_VWAP_STD_DEV_3` (exit/stop band)

### Technical Filters
- `BOT_USE_TREND_FILTER`
- `BOT_USE_RSI_FILTER`
- `BOT_USE_VWAP_DIRECTION_FILTER`
- `BOT_USE_VOLUME_FILTER`
- `BOT_RSI_PERIOD`, `BOT_RSI_OVERSOLD`, `BOT_RSI_OVERBOUGHT`

### Trading Hours
- `BOT_ENTRY_START_TIME` (18:00:00 ET)
- `BOT_ENTRY_END_TIME` (16:55:00 ET)
- `BOT_FLATTEN_TIME` (16:30:00 ET)
- `BOT_VWAP_RESET_TIME` (18:00:00 ET)

### Advanced Features
- `BOT_RL_ENABLED` (reinforcement learning)
- `BOT_RL_EXPLORATION_RATE` (0.0 for live trading)
- `BOT_ADAPTIVE_EXITS_ENABLED` (dynamic exit management)
- `BOT_ADAPTIVE_VOLATILITY_SCALING`
- `BOT_BREAKEVEN_ENABLED`, `BOT_TRAILING_STOP_ENABLED`

---

## 🚀 Quick Start for Different Account Sizes

### Small Account ($50K TopStep)
```bash
BOT_MAX_CONTRACTS=1
BOT_MAX_TRADES_PER_DAY=6
BOT_RISK_PER_TRADE=0.01
BOT_USE_TOPSTEP_RULES=true
```

### Medium Account ($150K TopStep)
```bash
BOT_MAX_CONTRACTS=3
BOT_MAX_TRADES_PER_DAY=9
BOT_RISK_PER_TRADE=0.012
BOT_USE_TOPSTEP_RULES=true
```

### Large Account ($250K TopStep)
```bash
BOT_MAX_CONTRACTS=5
BOT_MAX_TRADES_PER_DAY=12
BOT_RISK_PER_TRADE=0.015
BOT_USE_TOPSTEP_RULES=true
```

### Personal Account (Custom Risk)
```bash
BOT_MAX_CONTRACTS=10
BOT_MAX_TRADES_PER_DAY=15
BOT_RISK_PER_TRADE=0.02
BOT_USE_TOPSTEP_RULES=false
BOT_DAILY_LOSS_PERCENT=3.0
BOT_MAX_DRAWDOWN_PERCENT=5.0
```

---

## ⚠️ Safety Notes

### Hard Caps (Cannot Override)
- `max_contracts > 25` → Bot refuses to start (hard error)
- `max_contracts > 15` → Bot shows warning but allows

### TopStep Rules (Auto-Applied)
When `BOT_USE_TOPSTEP_RULES=true`:
- Daily loss limit = 2% of balance (auto-calculated)
- Max drawdown = 4% from peak (auto-calculated)
- Profit target = 6% for evaluation accounts

### RL Confidence Scaling (Automatic)
Your `BOT_MAX_CONTRACTS` is the MAXIMUM. RL confidence scales within it:
- **LOW confidence** (0-40%): Uses 33% of max (e.g., 3 → 1 contract)
- **MEDIUM confidence** (40-70%): Uses 33-67% of max (e.g., 3 → 2 contracts)  
- **HIGH confidence** (70-100%): Uses 67-100% of max (e.g., 3 → 3 contracts)

---

## 🔧 Troubleshooting

### My env var isn't being read
1. Check the variable name starts with `BOT_` prefix
2. Verify `.env` file is in project root (same folder as `run.py`)
3. Restart the bot (environment variables load on startup)
4. Check for typos in variable names

### Which .env file is active?
The bot reads `.env` in the project root directory:
```
simple-bot-1/
  .env              ← ACTIVE FILE (your settings)
  .env.example      ← TEMPLATE (reference only)
  run.py
  src/
    config.py       ← Default values (fallback)
```

### How to verify what's loaded?
The bot logs configuration on startup:
```
2025-11-04 10:02:40 - vwap_bot - INFO - Max Contracts: 3
2025-11-04 10:02:40 - vwap_bot - INFO - Max Trades per Day: 9
2025-11-04 10:02:40 - vwap_bot - INFO - Risk per Trade: 1.2%
```

---

## 📝 Best Practices

1. **Always keep a backup**: Copy `.env` to `.env.backup` before major changes
2. **Use `.env.example` as reference**: It shows all available options
3. **Test in paper mode first**: Set `BOT_DRY_RUN=true` when testing new settings
4. **Start conservative**: Begin with 1-3 contracts, increase gradually
5. **Document your changes**: Add comments to your `.env` file for custom settings
6. **Never commit .env to git**: Contains your API credentials (already in .gitignore)

---

## 🎓 Multi-User Deployment

For subscription service, each customer gets their own `.env` file:

### customer_1.env
```bash
TOPSTEP_API_TOKEN=customer1_token
BOT_MAX_CONTRACTS=2
BOT_MAX_TRADES_PER_DAY=6
```

### customer_2.env  
```bash
TOPSTEP_API_TOKEN=customer2_token
BOT_MAX_CONTRACTS=10
BOT_MAX_TRADES_PER_DAY=15
```

Then run: `python run.py --env customer_1.env`

(Note: Multi-env support would need to be implemented in `run.py`)
