# Alert Notifications Integration Guide

## Overview
The notification system is ready to use! It's already configured via the GUI and just needs to be integrated into the bot's trading logic.

## Quick Start

### 1. Import the notifier
```python
from notifications import get_notifier

# Get the notifier instance
notifier = get_notifier()
```

### 2. Send alerts at key points

#### Trade Entry Alert
```python
# When entering a trade
notifier.send_trade_alert(
    trade_type="ENTRY",
    symbol="ES",
    price=4500.00,
    contracts=2,
    side="LONG"  # or "SHORT"
)
```

#### Trade Exit Alert
```python
# When exiting a trade
notifier.send_trade_alert(
    trade_type="EXIT",
    symbol="ES",
    price=4520.00,
    contracts=2,
    side="LONG"
)
```

#### Error Alerts
```python
# When an error occurs
notifier.send_error_alert(
    error_message="Connection lost to broker",
    error_type="Connection Error"
)
```

#### Daily Summary (end of day)
```python
# Send daily performance summary
notifier.send_daily_summary(
    trades=12,
    profit_loss=1250.50,
    win_rate=66.7,
    max_drawdown=-450.00
)
```

#### Loss Limit Warning
```python
# Warn when approaching daily loss limit
notifier.send_daily_limit_warning(
    current_loss=-800.00,
    limit=1000.00
)
```

## Integration Points in Bot

### In `vwap_bounce_bot.py`:

1. **After successful trade entry** (around line 2791):
```python
from notifications import get_notifier

# After trade is filled
logger.info(f"  Final Entry Price: ${actual_fill_price:.2f}")

# Send alert
notifier = get_notifier()
notifier.send_trade_alert(
    trade_type="ENTRY",
    symbol=CONFIG['instrument'],
    price=actual_fill_price,
    contracts=position_size,
    side="LONG" if direction == 1 else "SHORT"
)
```

2. **After trade exit** (around line 4091):
```python
# After exit is filled
logger.info(f"  Expected: ${exit_price:.2f}, Actual: ${actual_exit_price:.2f}")

# Send alert
notifier = get_notifier()
notifier.send_trade_alert(
    trade_type="EXIT",
    symbol=CONFIG['instrument'],
    price=actual_exit_price,
    contracts=exit_size,
    side="LONG" if position_side == 1 else "SHORT"
)
```

3. **On connection errors** (error handling blocks):
```python
except Exception as e:
    logger.error(f"Connection error: {e}")
    
    # Send error alert
    notifier = get_notifier()
    notifier.send_error_alert(
        error_message=str(e),
        error_type="Connection Error"
    )
```

4. **Daily loss limit check** (around loss limit validation):
```python
if abs(daily_loss) >= CONFIG['daily_loss_limit'] * 0.8:  # 80% of limit
    notifier = get_notifier()
    notifier.send_daily_limit_warning(
        current_loss=daily_loss,
        limit=CONFIG['daily_loss_limit']
    )
```

5. **End of day summary** (session close):
```python
# Calculate daily stats
notifier = get_notifier()
notifier.send_daily_summary(
    trades=len(daily_trades),
    profit_loss=daily_pnl,
    win_rate=calculate_win_rate(),
    max_drawdown=calculate_max_drawdown()
)
```

## Testing

Test the notifications from command line:
```bash
python src/notifications.py
```

Or test from within your code:
```python
from notifications import get_notifier

notifier = get_notifier()
if notifier.enabled:
    notifier.send_test_alert()
```

## Configuration

Users configure alerts via the GUI launcher:
1. Click "Enable Trade Alerts" checkbox
2. Enter email, Gmail app password, phone, carrier
3. Alerts are saved to `config.json`

The notification system automatically reads from `config.json` and only sends alerts if:
- `alerts_enabled` is `true`
- Valid email and Gmail password are provided

## Free Limits

- **Gmail SMTP**: 500 emails/day (free)
- **Email-to-SMS**: Unlimited (uses carrier gateway)
- No paid services required!

## Security Notes

- Gmail App Passwords are encrypted/hashed when stored
- Config file should not be committed to git (already in .gitignore)
- Users manage their own Gmail security

## Next Steps

To fully integrate:
1. Add `from notifications import get_notifier` to `vwap_bounce_bot.py`
2. Call appropriate alert methods at trade entry/exit points
3. Add error alerts in exception handlers
4. Implement daily summary calculation and sending
5. Test with real trades!
