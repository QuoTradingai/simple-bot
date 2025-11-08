# Alert & Notification System - Complete Integration Guide

## Overview
Comprehensive email and SMS notification system integrated throughout the trading bot to alert users of all critical events in real-time.

## Configuration
Alerts are configured via the GUI launcher:
1. Click "🔔 Enable Trade Alerts" checkbox
2. Enter configuration in popup dialog:
   - **Email Address**: Your email for detailed alerts
   - **Gmail App Password**: 16-character app password from Google
   - **Phone Number**: 10-digit mobile number
   - **Carrier**: Select your carrier (Verizon/AT&T/T-Mobile/Sprint)

### Getting Gmail App Password
1. Go to Google Account settings
2. Security → 2-Step Verification (must be enabled)
3. App passwords → Select "Mail" and "Other device"
4. Copy the 16-character password

## Alert Types Implemented

### 🟢 Bot Lifecycle Alerts
| Alert Type | Trigger | Location | Description |
|------------|---------|----------|-------------|
| **Bot Started** | Successful broker connection | Line ~213 | Confirms bot is online and ready to trade |
| **Bot Shutdown** | Cleanup on exit | Line ~6320 | Notifies when bot is shutting down (before disconnect) |
| **Bot Crash** | Unhandled exceptions | Signal handlers | Critical failure notification |

### 💰 Trading Activity Alerts
| Alert Type | Trigger | Location | Description |
|------------|---------|----------|-------------|
| **Trade Entry** | Position opened (filled) | Line ~2805 | Entry confirmation with price, contracts, side |
| **Trade Exit** | Position closed | Line ~4378 | Exit notification with P&L, duration, reason |
| **Daily Summary** | End of trading day | Line ~5537 | Full session stats: trades, P&L, win rate, drawdown |

### ⚠️ Error & Warning Alerts
| Alert Type | Trigger | Location | Description |
|------------|---------|----------|-------------|
| **Connection Error** | Broker disconnect | Line ~237 | Connection lost alert with reconnect attempt |
| **Order Error** | Order placement fails | Line ~350 | Order rejection or placement failure |
| **Position Stuck** | Position > 2 hours | Line ~3602 | Alert for positions held longer than normal |
| **High Slippage** | Stop loss slippage > threshold | Line ~4186 | Fast market/poor liquidity warning |
| **Flatten Failed** | Emergency flatten fails | Line ~4328 | 🆘 CRITICAL: Manual intervention required |

### 🛡️ Risk Management Alerts
| Alert Type | Trigger | Location | Description |
|------------|---------|----------|-------------|
| **Daily Loss Warning** | 80% of loss limit | Line ~4963 | Early warning approaching daily limit |
| **Daily Loss Limit HIT** | 100% loss limit breach | Line ~4945 | Trading stopped due to loss limit |
| **Max Trades Reached** | Daily trade count = limit | Line ~1538 | No more trades allowed today |
| **Recovery Mode** | Approaching limits | Line ~5183 | Scaled-down trading activated |
| **Confidence Trading** | Risk scaling active | Line ~5183 | High-confidence only mode |

### 🕐 Time-Based Alerts
| Alert Type | Trigger | Location | Description |
|------------|---------|----------|-------------|
| **Flatten Mode** | 4:45 PM ET | Line ~3943 | 15-min warning before maintenance |
| **Trading Resumed** | After maintenance | Line ~3910 | Bot back to normal trading |

## Alert Format

### Email Format
```
Subject: [Bot Alert] {Alert Type}

{Detailed message with full context}
- Symbol, price, contracts
- P&L calculations
- Timestamps
- Error details
```

### SMS Format (160 char max)
```
{Alert Type}: {Concise summary}
{Critical data points only}
```

## Implementation Details

### Email Delivery
- **Protocol**: Gmail SMTP over TLS (smtp.gmail.com:587)
- **Daily Limit**: 500 emails/day (Gmail free tier)
- **Delivery Time**: ~1-5 seconds

### SMS Delivery
- **Method**: Email-to-SMS via carrier gateways
- **Cost**: FREE (uses email system)
- **Carriers Supported**:
  - Verizon: `{phone}@vtext.com`
  - AT&T: `{phone}@txt.att.net`
  - T-Mobile: `{phone}@tmomail.net`
  - Sprint: `{phone}@messaging.sprintpcs.com`
- **Delivery Time**: ~5-30 seconds

### Error Handling
All alerts are wrapped in try/except blocks:
- **Never crash the bot** if alert fails to send
- **Silent failures** logged at debug level
- **Network errors** handled gracefully
- **Bot continues trading** even if notifications fail

## Code Structure

### Notification Module
**File**: `src/notifications.py`
- `AlertNotifier` class with singleton pattern
- `get_notifier()` for global access
- Methods:
  - `send_trade_alert(type, symbol, price, contracts, side)`
  - `send_error_alert(message, error_type)`
  - `send_daily_summary(trades, pnl, win_rate, drawdown)`
  - `send_daily_limit_warning(current_loss, limit)`
  - `send_test_alert()` for testing

### Integration Pattern
```python
# Import at top of file
from notifications import get_notifier

# Use in code
try:
    notifier = get_notifier()
    notifier.send_error_alert(
        error_message="Critical event occurred",
        error_type="Event Type"
    )
except Exception as e:
    logger.debug(f"Failed to send alert: {e}")
```

## Testing

### Test Alert Button
GUI launcher includes "Send Test Alert" button to verify:
- Email configuration is correct
- SMS delivery works
- Credentials are valid

### Sample Test Alert
```
Subject: [Bot Alert] Test Alert

This is a test alert from QuoTrading Bot.

If you receive this, your alert notifications are working correctly!

Configuration:
- Email: ✓ Working
- SMS: ✓ Working (if you received this via text)

Time: 2025-11-08 14:30:00 ET
```

## Alert Frequency

### Real-Time Alerts (Immediate)
- Trade entry/exit
- Connection errors
- Critical failures
- Flatten failures

### Batch Alerts (Once per event)
- Bot startup (once)
- Daily summary (end of day)
- Mode activations (on change)
- Limit warnings (first occurrence)

### Throttled Alerts (Limited frequency)
- Position stuck (once per position)
- High slippage (per occurrence)
- Max trades (once when hit)

## Security Considerations

1. **Gmail App Password**: Stored in `config.json` (not in repository)
2. **Phone Number**: Private data, not logged
3. **Credentials**: Never sent in alerts or logged
4. **TLS Encryption**: All SMTP traffic encrypted

## Troubleshooting

### Alerts Not Sending
1. Check Gmail App Password is correct (16 chars)
2. Verify 2-Step Verification enabled on Google account
3. Test with "Send Test Alert" button
4. Check bot logs for error messages

### SMS Not Receiving
1. Verify phone number is correct (10 digits, no spaces)
2. Confirm carrier selection matches your provider
3. Some carriers block email-to-SMS - try different carrier
4. Check spam folder or blocked messages

### Too Many Alerts
- Reduce alert types in future update (selective alerts)
- Batch similar alerts
- Increase thresholds (e.g., slippage tolerance)

## Future Enhancements

Potential additions (not yet implemented):
- ⏳ Webhook support (Discord, Slack, etc.)
- ⏳ Push notifications via mobile app
- ⏳ Alert filtering/priority levels
- ⏳ Quiet hours (suppress non-critical alerts)
- ⏳ Alert history/log viewer
- ⏳ Multiple recipient support

## Support

For issues or questions:
1. Check Gmail App Password setup
2. Verify carrier gateway compatibility
3. Review bot logs for error details
4. Test with simple email first, then add SMS

---

**Last Updated**: November 8, 2025
**Integration Status**: ✅ Complete - All critical events covered
**Total Alert Types**: 16 unique alerts
