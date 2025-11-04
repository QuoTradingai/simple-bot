# Dynamic Position Sizing Guide

## 🎯 How It Works

**USER SETS THE MAX LIMIT → RL Confidence chooses contracts within that limit**

### Configuration (User Controls)

In `src/config.py`:
```python
max_contracts: int = 3  # USER CONFIGURABLE - Set your maximum allowed contracts (1-25)
```

**Safety Limits:**
- ✅ **Recommended**: 1-10 contracts (covers 90% of retail traders)
- ⚠️ **Warning threshold**: 15+ contracts (high position size)
- 🛑 **Hard cap**: 25 contracts maximum (safety limit)

### Dynamic Scaling (RL Confidence)

The bot uses **RL confidence** to dynamically choose contracts **within your max limit**:

| RL Confidence | Multiplier | Contracts (max=3) | Contracts (max=10) | Contracts (max=25) |
|---------------|------------|-------------------|---------------------|---------------------|
| **LOW** (< 40%) | 0.33 | 1 contract | 3 contracts | 8 contracts |
| **MEDIUM** (40-70%) | 0.33-0.67 | 1-2 contracts | 3-7 contracts | 8-17 contracts |
| **HIGH** (70-100%) | 0.67-1.0 | 2-3 contracts | 7-10 contracts | 17-25 contracts |

## 📊 Examples

### Example 1: Conservative Trader ($25,000 account)
```python
max_contracts = 3
risk_per_trade = 0.012  # 1.2%
```

**Positions:**
- 🟡 Low confidence signal → 1 contract ($300 risk)
- 🟢 Medium confidence signal → 2 contracts ($600 risk)
- 🔥 High confidence signal → 3 contracts ($900 risk)

### Example 2: Aggressive Trader ($100,000 account)
```python
max_contracts = 10
risk_per_trade = 0.012  # 1.2%
```

**Positions:**
- 🟡 Low confidence signal → 3 contracts ($1,200 risk)
- 🟢 Medium confidence signal → 6 contracts ($1,200 risk)
- 🔥 High confidence signal → 10 contracts ($1,200 risk)

### Example 3: Small Account Trader ($10,000)
```python
max_contracts = 1
risk_per_trade = 0.010  # 1.0%
```

**Positions:**
- 🟡 Low confidence signal → 1 contract ($100 risk)
- 🟢 Medium confidence signal → 1 contract ($100 risk)
- 🔥 High confidence signal → 1 contract ($100 risk)

## 🔧 User Configuration

Each user can customize their own limits in the bot config:

```python
# src/config.py or environment variables
BOT_MAX_CONTRACTS=5          # Your maximum allowed contracts
BOT_RISK_PER_TRADE=0.015     # 1.5% risk per trade
BOT_MAX_TRADES_PER_DAY=12    # Daily trade limit
```

## 🧠 RL Confidence System

The RL brain analyzes:
- ✅ Signal strength (VWAP distance, RSI, trend alignment)
- ✅ Market conditions (volatility, time of day)
- ✅ Historical win rate in similar setups
- ✅ Recent performance

**Output:** Confidence score 0-100% → Scaled to contracts within YOUR limit!

## 🛡️ Safety Features

1. **User-controlled max** - You set your absolute maximum
2. **Risk-based calculation** - Never exceeds risk_per_trade %
3. **Confidence scaling** - Only takes full size on HIGH confidence
4. **Account size aware** - Risk dollars scale with equity

## 🎓 Best Practices

### For Small Accounts ($5K-$25K)
```python
max_contracts = 1-2
risk_per_trade = 0.008-0.010  # 0.8-1.0%
```

### For Medium Accounts ($25K-$100K)
```python
max_contracts = 3-5
risk_per_trade = 0.010-0.012  # 1.0-1.2%
```

### For Large Accounts ($100K+)
```python
max_contracts = 5-15
risk_per_trade = 0.012-0.015  # 1.2-1.5%
```

### For Very Large Accounts ($250K+)
```python
max_contracts = 15-25
risk_per_trade = 0.015-0.020  # 1.5-2.0%
```

**Note:** Values above 15 contracts will trigger a warning. Values above 25 are blocked.

## 📝 Multi-User Setup

For subscription-based service:

```python
# User A - Conservative
user_a_config = {
    "max_contracts": 2,
    "risk_per_trade": 0.008,
    "account_equity": 15000
}

# User B - Aggressive
user_b_config = {
    "max_contracts": 8,
    "risk_per_trade": 0.015,
    "account_equity": 120000
}

# User C - Small Account
user_c_config = {
    "max_contracts": 1,
    "risk_per_trade": 0.010,
    "account_equity": 8000
}
```

Each user gets the **same signals**, but position sizes scale to **their config**!

## 🚀 Key Advantages

✅ **User Control** - You set your own limits, not the bot
✅ **Confidence-Based** - Only goes full size on best setups
✅ **Scalable** - Works for any account size ($5K to $5M)
✅ **Risk-Aware** - Always respects your risk_per_trade %
✅ **Multi-User Ready** - Each user can have different settings

---

**Bottom Line:** You control the maximum, RL confidence dynamically chooses the best size within your limit! 🎯
