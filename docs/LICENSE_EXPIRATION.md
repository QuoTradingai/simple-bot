# License Expiration Handling

## Overview

The QuoTrading bot now includes automatic license expiration detection and graceful shutdown capabilities. When a customer's API key (license) expires, the bot will intelligently stop trading at the most appropriate time to minimize disruption.

## How It Works

### Periodic License Validation

- The bot checks license validity **every 5 minutes** during trading hours
- Validates against the cloud API to ensure the license is still active
- Does not stop trading on temporary network errors (continues to retry)

### Graceful Shutdown Strategy

When a license expiration is detected, the bot chooses the best time to stop based on current market conditions:

#### 1. **Immediate Stop** (Default)
- **When**: Expires during normal trading hours (Monday-Thursday, 6:00 PM - 4:45 PM ET)
- **Action**: 
  - Immediately flatten all open positions
  - Disable new trade entries
  - Send notification alert
  - Log expiration reason

#### 2. **Friday Market Close**
- **When**: Expires on Friday before market close (before 5:00 PM ET)
- **Action**:
  - Continue trading until Friday market close (5:00 PM ET)
  - Flatten positions at market close
  - Disable trading for the weekend
  - Prevents unnecessary early exit

#### 3. **Maintenance Window**
- **When**: Expires during flatten mode (4:45-5:00 PM ET, Monday-Thursday)
- **Action**:
  - Wait until maintenance window starts (5:00 PM ET)
  - Flatten positions with other daily maintenance activities
  - Minimizes disruption during active trading

#### 4. **Weekend Expiration**
- **When**: Expires on Saturday or Sunday
- **Action**:
  - Should have already stopped on Friday at market close
  - If detected, stops immediately
  - No position flattening needed (market closed)

## Example Scenarios

**Scenario 1: Expires Wednesday at 2 PM**
```
14:00 - License check detects expiration
14:00 - Flatten any open positions immediately
14:00 - Disable trading
14:00 - Send notification
```

**Scenario 2: Expires Friday at 3 PM**
```
15:00 - License check detects expiration
15:00 - Flag set: stop_at_market_close
15:00-17:00 - Continue trading normally
17:00 - Market closes, flatten positions
17:00 - Disable trading
17:00 - Send notification
```

**Scenario 3: Expires Wednesday at 4:50 PM**
```
16:50 - License check detects expiration (flatten mode active)
16:50 - Flag set: stop_at_maintenance
16:50-17:00 - Continue managing open positions
17:00 - Maintenance window, flatten positions
17:00 - Disable trading
17:00 - Send notification
```

## Customer Impact

- **Smart Timing**: Stops at natural market breaks (maintenance, weekend close)
- **Position Safety**: Always flattens positions before stopping
- **Clear Communication**: Logs and alerts explain exactly what's happening
- **Minimal Disruption**: Waits for appropriate times when possible

## Testing

Run the test suite to validate expiration handling:

```bash
python tests/test_expiration_simple.py
```

All timing logic is tested for correctness.
