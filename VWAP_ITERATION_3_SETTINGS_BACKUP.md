# VWAP ITERATION 3 SETTINGS - BACKUP
# DO NOT LOSE - These are your proven profitable settings!
# Date: November 8, 2025

## 🎯 VWAP STRATEGY - ITERATION 3 (WINNER!)

### VWAP Bands (Standard Deviation Multipliers)
```
vwap_std_dev_1 = 2.5   # Warning zone (potential reversal)
vwap_std_dev_2 = 2.1   # ENTRY ZONE - Iteration 3 ✅
vwap_std_dev_3 = 3.7   # EXIT/STOP ZONE - Iteration 3 ✅
```

**What this means:**
- Entry: Price bounces off 2.1 std dev band
- Exit: 2:1 reward-risk or 3.7 std dev band
- Stop: 3.7 std dev or fixed ticks

---

## 📊 RSI SETTINGS - ITERATION 3

```
rsi_period = 10          # Iteration 3 (faster than standard 14)
rsi_oversold = 35        # LONG entries (selective) ✅
rsi_overbought = 65      # SHORT entries (selective) ✅
```

**Strategy:**
- More selective than extreme 20/80
- Catches better setups
- Reduces false signals

---

## ⚙️ FILTERS - ITERATION 3

```
use_trend_filter = False           # OFF - optimizer found better without ✅
use_rsi_filter = True              # ON - RSI confirmation required
use_vwap_direction_filter = True   # ON - price must be correct side of VWAP ✅
use_volume_filter = False          # OFF - blocks overnight trades
```

**Key Finding:** Trend filter OFF = better performance!

---

## 💰 RISK MANAGEMENT

```
risk_per_trade = 0.012              # 1.2% per trade
max_contracts = 1                   # Current setting (user configurable)
max_trades_per_day = 3              # Daily trade limit
risk_reward_ratio = 2.0             # 2:1 reward-risk
daily_loss_limit = $1,000           # Or 2% of account
auto_calculate_limits = True        # Dynamic based on account size
```

---

## 📈 POSITION SIZING

```
Account Size: $50,000
Risk Per Trade: 1.2% = $600
Stop Loss: 8 ticks default
Tick Value: $12.50
Contracts: Auto-calculated based on stop distance
```

**Example:**
- Entry: $5800
- Stop: $5798 (8 ticks = $100)
- Risk: $600
- Contracts: 6 ($600 / $100 per contract)
- Capped at: max_contracts setting

---

## ⏰ TRADING HOURS (Eastern Time)

```
entry_start_time = 18:00           # 6 PM - ES futures session opens
entry_end_time = 16:55             # 4:55 PM - before maintenance
flatten_time = 16:45               # 4:45 PM - start closing positions
forced_flatten_time = 17:00        # 5:00 PM - maintenance starts
vwap_reset_time = 18:00            # 6 PM - daily VWAP reset
```

**Friday Special:**
```
friday_entry_cutoff = 16:30        # Stop entries 4:30 PM
friday_close_target = 16:45        # Flatten by 4:45 PM
```

---

## 🎲 MACHINE LEARNING SETTINGS

```
rl_confidence_threshold = 0.70     # 70% confidence required (LIVE MODE)
rl_exploration_rate = 0.0          # 0% in live = NO RANDOM TRADES
rl_min_exploration_rate = 0.05     # 5% minimum
rl_exploration_decay = 0.995       # Decay rate
```

**Learning Data:**
- Signal experiences: 6,880 trades
- Exit experiences: 2,961 exits
- Files: `data/signal_experience.json`, `data/exit_experience.json`

---

## 🔧 EXECUTION SETTINGS

```
slippage_ticks = 1.5               # Conservative estimate
commission_per_contract = 2.50     # Round-turn
tick_size = 0.25                   # ES futures
tick_value = 12.50                 # $ per tick
```

---

## 📋 TECHNICAL INDICATORS

### EMA (Trend - DISABLED)
```
trend_ema_period = 21
trend_threshold = 0.0001
```

### MACD (DISABLED)
```
macd_fast = 12
macd_slow = 26
macd_signal = 9
```

### Volume (DISABLED)
```
volume_spike_multiplier = 1.5
volume_lookback = 20
```

---

## 🚨 SAFETY LIMITS

```
daily_loss_limit = $1,000          # Fixed
daily_loss_percent = 2.0%          # Or percentage
proactive_stop_buffer_ticks = 2
flatten_buffer_ticks = 2
recovery_mode = False              # Disabled in production
```

---

## 💡 KEY INSIGHTS FROM ITERATION 3

### What Works:
✅ **2.1 std dev entry** (not too tight, not too wide)
✅ **3.7 std dev stops** (wider stops reduce noise)
✅ **RSI 35/65** (more selective than extreme levels)
✅ **VWAP direction filter ON** (trade correct side only)
✅ **Trend filter OFF** (better without it!)
✅ **1.2% risk per trade** (aggressive but controlled)

### What Doesn't Work:
❌ Volume filter (blocks overnight trades)
❌ Trend filter (optimizer found worse results)
❌ Extreme RSI 20/80 (too many false signals)
❌ Tight std dev (1.5-1.8 = too many whipsaws)

---

## 🔄 HOW TO RESTORE THESE SETTINGS

### Option 1: config.py (Hardcoded)
Edit `src/config.py` lines 43-61:
```python
vwap_std_dev_2: float = 2.1
vwap_std_dev_3: float = 3.7
rsi_period: int = 10
rsi_oversold: int = 35
rsi_overbought: int = 65
use_trend_filter: bool = False
use_vwap_direction_filter: bool = True
```

### Option 2: Environment Variables
Set in `.env` file:
```bash
BOT_VWAP_STD_DEV_2=2.1
BOT_VWAP_STD_DEV_3=3.7
BOT_RSI_PERIOD=10
BOT_RSI_OVERSOLD=35
BOT_RSI_OVERBOUGHT=65
BOT_USE_TREND_FILTER=false
```

### Option 3: config.json
Not all VWAP settings in config.json - use config.py instead

---

## 📁 FILES TO BACKUP

**Critical (DO NOT LOSE):**
- `src/config.py` - All VWAP settings
- `data/signal_experience.json` - 6,880 ML trades
- `data/exit_experience.json` - 2,961 ML exits

**Important:**
- `config.json` - User settings, broker credentials
- `data/historical_data/*.csv` - Backtest data

**Already Backed Up:**
- `backup_ml_data/` - Local backup folder ✅
- GitHub: https://github.com/Quotraders/simple-bot ✅

---

## 🎯 PERFORMANCE EXPECTATIONS

With these settings (Iteration 3):
- Win Rate: ~60-65% (mean reversion)
- Risk/Reward: 2:1 average
- Max Drawdown: <8% (prop firm compliant)
- Daily Trades: 1-5 trades
- Best Sessions: Overnight (18:00-09:30 ET)

---

## 🔐 THIS IS YOUR EDGE - PROTECT IT!

These settings are the result of:
- Months of backtesting
- 6,880+ real trades
- Machine learning optimization
- Live market validation

**DO NOT SHARE** these exact parameters with anyone!

---

Backup created: November 8, 2025 05:52 AM EST
Status: SAFE ✅
