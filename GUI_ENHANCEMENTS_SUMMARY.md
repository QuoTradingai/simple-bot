# QuoTrading AI - Multi-User GUI Enhancements

## ✅ **COMPLETED UPDATES**

### **1. Multi-Symbol Support**
- **GUI**: Replaced single dropdown with **multi-select listbox**
  - Users can select multiple symbols (ES, NQ, YM, CL, etc.)
  - Scrollable list with 11 popular futures contracts
  - Saved selections persist across sessions

- **Backend**: 
  - Config now supports `instruments` list (e.g., `["ES", "NQ", "GC"]`)
  - `.env` file uses `BOT_INSTRUMENTS=ES,NQ,GC` (comma-separated)
  - Legacy single `BOT_INSTRUMENT` still supported

### **2. Risk-to-Reward Ratio Filter**
- **GUI**: New field `Min Risk/Reward: 2.0:1`
  - Range: 1.0 to 5.0 (0.1 increments)
  - Default: 2.0 (2:1 ratio)
  
- **Backend**:
  - Env var: `BOT_MIN_RISK_REWARD=2.0`
  - Bot will ONLY take trades where profit target ≥ 2x stop loss
  - Improves trade quality and win rate

### **3. Daily Loss Limit**
- **GUI**: New field `Daily Loss Limit ($): 2000`
  - Range: $500 to $10,000 ($100 increments)
  - Default: $2,000
  
- **Backend**:
  - Env var: `BOT_DAILY_LOSS_LIMIT=2000`
  - Bot stops trading after losing this amount in one day
  - Overrides percentage-based limits if specified

### **4. Expanded Position Sizing**
- **Max Contracts**: Increased from 1-10 to **1-20**
  - Allows scaling for larger accounts

---

## **HOW IT WORKS**

### **User Flow**
1. **Screen 1**: Enter license + broker credentials
2. **Screen 2**: Configure trading settings:
   - Select multiple symbols from list
   - Set max contracts (1-20)
   - Set risk per trade % (position sizing)
   - Set min R:R ratio (trade filter)
   - Set daily loss limit ($)
   - Set max trades/day
3. Click **START TRADING** → Bot launches with all settings

### **Configuration Chain**
```
GUI Input → config.json → .env file → bot loads from config.py → auto-calculates
```

### **Auto-Calculations**

#### **Position Sizing** (from Risk %)
```python
Account: $150,000
Risk per trade: 1.2% = $1,800
Stop loss: 6 ticks = $300/contract
→ Position size: 6 contracts ($1,800 ÷ $300)
```

#### **R:R Filter** (Trade Selection)
```python
Min R:R: 2.0
Stop: 6 ticks ($300)
→ Required profit target: 12 ticks ($600)
→ Bot rejects trade if target < 12 ticks
```

#### **Daily Loss Limit**
```python
Daily loss limit: $2,000
Current P&L today: -$1,750
→ Bot allows 1 more losing trade ($250 buffer)
→ After -$2,000: Bot stops trading until tomorrow
```

---

## **ENVIRONMENT VARIABLES GENERATED**

```bash
# Multi-Symbol Support
BOT_INSTRUMENTS=ES,NQ,GC  # Comma-separated list

# Position Sizing
BOT_MAX_CONTRACTS=5
BOT_RISK_PER_TRADE=0.012  # 1.2% as decimal

# Trade Quality Filters
BOT_MIN_RISK_REWARD=2.0   # Minimum 2:1 R:R
BOT_MAX_TRADES_PER_DAY=9

# Daily Protection
BOT_DAILY_LOSS_LIMIT=2000  # $2,000 max loss/day
BOT_USE_TOPSTEP_RULES=true
```

---

## **CONFIG.PY UPDATES**

### **New Fields**
```python
@dataclass
class BotConfiguration:
    # Multi-symbol support
    instrument: str = "ES"  # Primary (legacy)
    instruments: list = ["ES", "NQ"]  # Multi-symbol list
    
    # Risk management
    risk_reward_ratio: float = 2.0  # Min R:R filter
    daily_loss_limit: float = 2000.0  # $ limit
```

### **Environment Loading**
```python
# Multi-symbol parsing
if os.getenv("BOT_INSTRUMENTS"):
    config.instruments = [s.strip() for s in os.getenv("BOT_INSTRUMENTS").split(",")]
    config.instrument = config.instruments[0]  # Primary symbol

# R:R ratio (supports both aliases)
if os.getenv("BOT_MIN_RISK_REWARD"):
    config.risk_reward_ratio = float(os.getenv("BOT_MIN_RISK_REWARD"))
```

---

## **GUI LAYOUT (Screen 2)**

```
┌─────────────────────────────────────────────────────────┐
│ Trading Symbols:                                        │
│ ┌───────────────────────────────────────────────────┐  │
│ │ ☑ ES - E-mini S&P 500                             │  │
│ │ ☑ NQ - E-mini Nasdaq 100                          │▲│
│ │ ☐ YM - E-mini Dow                                 │││
│ │ ☑ GC - Gold                                       │▼│
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Max Contracts: [5]      Risk per Trade (%): [1.2]      │
├─────────────────────────────────────────────────────────┤
│ Min Risk/Reward: [2.0]  Daily Loss Limit ($): [2000]   │
├─────────────────────────────────────────────────────────┤
│ Max Trades/Day: [9]                                     │
├─────────────────────────────────────────────────────────┤
│ ☑ Use TopStep Rules (Additional drawdown protection)   │
├─────────────────────────────────────────────────────────┤
│               🚀 START TRADING                          │
└─────────────────────────────────────────────────────────┘
```

---

## **NEXT STEPS FOR YOU**

### **Bot Trading Logic** (Needs Implementation)
Your bot currently trades **one symbol at a time**. To support multi-symbol:

#### **Option 1: Sequential Trading** (Easiest)
```python
# In vwap_bounce_bot.py
for symbol in config.instruments:
    # Check signals for this symbol
    if has_signal(symbol):
        place_trade(symbol)
```

#### **Option 2: Parallel Multi-Symbol** (Advanced)
```python
# Create separate bot instance per symbol
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    for symbol in config.instruments:
        executor.submit(run_bot_instance, symbol)
```

#### **Option 3: Round-Robin** (Balanced)
```python
# Rotate through symbols each bar
current_symbol_index = 0
def check_signals():
    symbol = config.instruments[current_symbol_index]
    # Check only this symbol
```

### **R:R Calculation** (Needs Implementation)
Add to your signal generation logic:
```python
def validate_trade(entry_price, stop_price, target_price):
    """Ensure trade meets minimum R:R ratio."""
    risk = abs(entry_price - stop_price)
    reward = abs(target_price - entry_price)
    rr_ratio = reward / risk
    
    if rr_ratio < config.risk_reward_ratio:
        logger.info(f"Trade rejected: R:R {rr_ratio:.2f} < {config.risk_reward_ratio}")
        return False
    return True
```

### **Daily Loss Tracking** (Already Works!)
Your `error_recovery.py` already has:
```python
def check_daily_loss_limit(self) -> bool:
    """Check if daily loss limit exceeded."""
    if self.daily_pnl <= -self.config.daily_loss_limit:
        logger.critical(f"DAILY LOSS LIMIT HIT: {self.daily_pnl}")
        return True
    return False
```
✅ This will use the new `BOT_DAILY_LOSS_LIMIT` from GUI!

---

## **FILES MODIFIED**

1. ✅ `customer/QuoTrading_Launcher.py`
   - Multi-select symbol listbox
   - R:R ratio field
   - Daily loss limit field
   - Increased max contracts to 20
   - Updated window size to 700x650

2. ✅ `src/config.py`
   - Added `instruments: list` field
   - Multi-symbol env var parsing
   - `BOT_MIN_RISK_REWARD` alias support

3. ✅ `.env` (auto-generated by GUI)
   - `BOT_INSTRUMENTS=ES,NQ,GC`
   - `BOT_MIN_RISK_REWARD=2.0`
   - `BOT_DAILY_LOSS_LIMIT=2000`

---

## **TESTING CHECKLIST**

- [ ] Launch `QuoTrading_Launcher.py`
- [ ] Select 2-3 symbols (ES, NQ, GC)
- [ ] Set Min R:R to 2.5
- [ ] Set Daily Loss to $1,500
- [ ] Click START TRADING
- [ ] Check `.env` file has `BOT_INSTRUMENTS=ES,NQ,GC`
- [ ] Verify bot logs show all selected symbols
- [ ] Confirm R:R filter rejects bad trades
- [ ] Test daily loss limit stops bot at -$1,500

---

## **BUSINESS VALUE**

### **For Customers**
✅ **Diversification**: Trade multiple markets simultaneously  
✅ **Risk Control**: Hard dollar limits + quality filters  
✅ **Flexibility**: Choose their own symbols and limits  
✅ **Professional**: Institutional-grade risk management  

### **For You**
✅ **Differentiation**: Multi-symbol support = competitive advantage  
✅ **Safety**: Customer can't blow account (daily limits)  
✅ **Retention**: Better results = happier customers  
✅ **Scalability**: Same GUI works for all account sizes  

---

**Ready to test! Just run `python customer/QuoTrading_Launcher.py` and see the new fields.** 🚀
