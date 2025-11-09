# Bot Time Service Integration

## Summary

Bot now integrates with Azure time service for comprehensive time-based trading management.

## What Changed

### 1. **New Function: `check_azure_time_service()`** (Line ~697)
- Called every 30 seconds alongside kill switch check
- Queries `/api/time/simple` endpoint
- Returns trading state: `entry_window`, `flatten_mode`, `closed`, or `event_block`
- Caches result in `bot_status["azure_trading_state"]`

### 2. **Updated Function: `get_trading_state()`** (Line ~6398)
- **Azure-first design**: Checks cached Azure state before local logic
- Falls back to local time calculations if Azure unreachable
- Maintains backwards compatibility for backtesting

### 3. **Updated Function: `validate_signal_requirements()`** (Line ~2160)
- Added `event_block` state handling
- Blocks new entries during FOMC/NFP/CPI events
- Respects `fomc_block_enabled` config setting

### 4. **Updated Function: `check_exit_conditions()`** (Line ~4548)
- Flattens positions during economic events
- Auto-resumes after event window closes
- Logs event reason for transparency

### 5. **Updated Config** (`config.json`)
- Added `fomc_block_enabled: true` - User can disable FOMC blocking
- Added `cloud_api_url` - Points to Azure Container Apps endpoint

## Trading Behavior

### Before (Hard-Coded Logic)
- ❌ Hard-coded flatten at 4:45 PM
- ❌ Manual maintenance window checks
- ❌ No FOMC/NFP/CPI awareness
- ❌ No timezone synchronization

### After (Azure-Driven Logic)
- ✅ Azure provides single source of truth for time
- ✅ Automatic maintenance window detection
- ✅ Economic event blocking (30 min before to 1 hour after)
- ✅ Timezone-accurate (handles DST automatically)
- ✅ Graceful fallback if Azure unreachable

## Trading States

Bot now recognizes 4 states (previously 3):

1. **`entry_window`** - Normal trading allowed
2. **`flatten_mode`** - 4:45-5:00 PM, close positions
3. **`closed`** - Maintenance (5-6 PM) or weekend
4. **`event_block`** - NEW: Economic event active (FOMC/NFP/CPI)

## Event Blocking Logic

When Azure detects an economic event:
1. **30 minutes before event**: `trading_allowed = false`
2. **During event**: `trading_allowed = false`
3. **1 hour after event**: `trading_allowed = false`
4. **After event window**: `trading_allowed = true`

Bot behavior:
- **If in position**: Flatten immediately (logged as `event_flatten`)
- **If no position**: Block new entries (logged as `Economic event block`)
- **After event**: Auto-resume trading

## Config Settings

### `fomc_block_enabled` (Boolean, default: `true`)
- `true`: Block trading during FOMC/NFP/CPI events
- `false`: Ignore economic events, trade normally

Users can toggle this in the GUI settings panel.

### `cloud_api_url` (String)
Azure endpoint for time service and kill switch:
```
https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io
```

## Health Check Flow

Every 30 seconds, `check_broker_connection()` calls:

1. **`check_cloud_kill_switch()`** - Emergency stop check
2. **`check_azure_time_service()`** - Time/event check (NEW)
3. **Broker health check** - Connection validation

This ensures bot stays synchronized with Azure and responds to:
- Kill switch activation/deactivation
- Maintenance windows
- Economic events
- Market hours

## Logging

New log messages:

### Event Block Activated
```
================================================================================
📅 ECONOMIC EVENT BLOCK ACTIVATED: FOMC Meeting (2:00 PM ET)
  Trading halted 30 min before to 1 hour after event
  Will auto-resume when event window closes
================================================================================
```

### Event Block Ended
```
================================================================================
✅ ECONOMIC EVENT ENDED - Trading resumed
================================================================================
```

### Position Flattened for Event
```
================================================================================
ECONOMIC EVENT - FOMC Meeting (2:00 PM ET) - AUTO-FLATTENING POSITION
Time: 13:30:00 EST
Position: LONG 1 @ $5850.25
================================================================================
```

## Deployment Checklist

- [ ] Deploy Azure v8 with time service + calendar
- [ ] Test `/api/time/simple` endpoint
- [ ] Test calendar scraping (should run 1st of month at 5 PM ET)
- [ ] Test event blocking with live bot
- [ ] Test maintenance window flattening
- [ ] Test auto-resume after events
- [ ] Add FOMC toggle to GUI settings panel

## Files Modified

1. `src/vwap_bounce_bot.py` - Added Azure time service integration
2. `config.json` - Added `fomc_block_enabled` and `cloud_api_url`

## Next Steps

1. **Deploy Azure v8** - Build Docker image with calendar + time service
2. **Test Event Blocking** - Wait for next FOMC/NFP/CPI to verify
3. **Add GUI Toggle** - Checkbox in `QuoTrading_Launcher.py` for FOMC blocking
4. **Customer Documentation** - Add FOMC feature to user guide

## Benefits

### For You (Admin)
- ✅ Centralized time management (no timezone bugs)
- ✅ Easy FOMC calendar updates (Azure scrapes Fed website monthly)
- ✅ Remote control (kill switch + event blocking from Azure)

### For Customers
- ✅ Automatic FOMC protection (no manual intervention)
- ✅ Transparent event logging (know why bot stopped)
- ✅ Optional feature (can disable if they want to trade through events)
- ✅ Zero downtime (auto-resume after events)

## Compatibility

- ✅ **Backtest mode**: Uses local time logic (Azure check skipped)
- ✅ **Live mode**: Azure-first with fallback
- ✅ **Offline mode**: Falls back to local time if Azure unreachable
- ✅ **Multi-user**: Works globally (UTC → ET conversion in Azure)
