# License Expiration Grace Period - Flow Diagram

## Overview
This document illustrates the license expiration handling with grace period for active positions.

## Flow Chart

```
┌─────────────────────────────────────────────────────────────┐
│         License Validation Check (Every 5 Minutes)          │
└─────────────────────────────────────┬───────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │  License Still Valid?   │
                        └──────────┬──────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                   YES                           NO
                    │                             │
                    ▼                             ▼
        ┌──────────────────────┐    ┌────────────────────────┐
        │  Continue Trading    │    │  License Expired!      │
        │  (No Action)         │    │  Check Active Position │
        └──────────────────────┘    └──────────┬─────────────┘
                                                │
                                ┌───────────────┴──────────────┐
                                │                              │
                          Has Active                      No Active
                           Position?                       Position
                                │                              │
                                ▼                              ▼
                ┌───────────────────────────┐    ┌────────────────────────┐
                │  GRACE PERIOD ACTIVATED   │    │   IMMEDIATE STOP       │
                │                           │    │                        │
                │  ✓ Block new trades       │    │  ✓ Disable trading     │
                │  ✓ Allow position mgmt    │    │  ✓ Send notification   │
                │  ✓ Send notification      │    │  ✓ Log reason          │
                │  ✓ Continue managing      │    └────────────────────────┘
                └──────────┬────────────────┘
                           │
                           │ (Position managed via
                           │  normal exit rules)
                           │
                           ▼
                ┌──────────────────────────┐
                │  Position Management:    │
                │  • Target hit?           │
                │  • Stop hit?             │
                │  • Time-based exit?      │
                │  • Reversal signal?      │
                └──────────┬───────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │   Position Closes        │
                │   (Normal Exit Logic)    │
                └──────────┬───────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │  GRACE PERIOD ENDS       │
                │                          │
                │  ✓ Disable trading       │
                │  ✓ Set emergency stop    │
                │  ✓ Send final notice     │
                │  ✓ Log final P&L         │
                └──────────────────────────┘
```

## Special Cases - Delayed Stops

In addition to the grace period, there are special timing scenarios:

### Friday Expiration
```
License Expires Friday Before 5pm
        ↓
Set flag: stop_at_market_close
        ↓
Continue trading until 5pm
        ↓
Market closes at 5pm
        ↓
Close any positions + disable trading
```

### Maintenance Window Expiration
```
License Expires During Flatten Mode (4:45-5pm weekday)
        ↓
Set flag: stop_at_maintenance
        ↓
Continue managing positions
        ↓
Maintenance starts at 5pm
        ↓
Close any positions + disable trading
```

## Key Safety Features

### 1. Grace Period Protection
- **Problem**: Immediate stop abandons active positions
- **Solution**: Continue managing until position closes naturally
- **Benefit**: Customer doesn't lose money from forced exits

### 2. Normal Exit Rules
During grace period, positions close via:
- ✅ Target reached
- ✅ Stop loss hit
- ✅ Time-based exit
- ✅ Signal reversal
- ❌ NOT forced market order

### 3. Clear Communication
**Grace Period Notification:**
```
🚨 LICENSE EXPIRED (Grace Period Active)

Your license has expired but you have an active LONG position.
Bot will continue managing the position until it closes.
Position: 1 contracts @ $5000.00

No new trades will be allowed.
Please renew your license.
```

**Final Notification (After Position Closes):**
```
🔒 TRADING STOPPED - Grace Period Ended

Your license expired and the active position has now closed safely.
Final P&L: +$125.50
Exit Reason: Target Reached

Trading is now stopped. Please renew your license to continue.
```

## Code Locations

### Grace Period Logic
- **Safety Check**: `check_safety_conditions()` - Line 6205
  - Checks if license expired
  - If position active: Allow management (grace period)
  - If no position: Block trading

- **Activation**: `handle_license_check_event()` - Line 7359
  - Detects expiration
  - Checks for active position
  - Enters grace period or immediate stop

- **Termination**: `execute_exit()` - Line 5779
  - Detects grace period flag
  - Position closed, ends grace period
  - Disables trading + notification

## Testing

Run tests to validate grace period:
```bash
python tests/test_grace_period.py
```

All scenarios tested:
- ✅ Grace period with active position
- ✅ Immediate stop with no position
- ✅ Grace period ends when position closes
- ✅ Proper notifications sent
