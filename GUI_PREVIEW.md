# GUI Preview: Prop Firm Safety Mode

## New Section Added to Trading Controls Screen

```
┌─────────────────────────────────────────────────────────────────┐
│                     QuoTrading - Trading Controls                 │
│                  Configure your trading strategy                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Trading Symbols (select at least one):                          │
│  ☑ ES - E-mini S&P 500        ☐ YM - E-mini Dow                 │
│  ☐ NQ - E-mini Nasdaq 100     ☐ CL - Crude Oil                  │
│  ☐ RTY - E-mini Russell 2000  ☐ GC - Gold                       │
└─────────────────────────────────────────────────────────────────┘

[Account Settings, Risk Settings, etc...]

┌─────────────────────────────────────────────────────────────────┐
│  Prop Firm Safety Mode:                                          │
│                                                                   │
│  ☑ Stop Trading When Approaching Failure                         │
│     (Recommended for Prop Firms)                                 │
│                                                                   │
│  ✓ SAFE MODE: Bot will stop making trades (but stay running)    │
│    when approaching 80% of daily loss limit or max drawdown.     │
│    This protects you from account failure. Bot continues         │
│    monitoring and will resume if conditions improve              │
│    significantly.                                                │
│                                                                   │
│  When enabled:                                                   │
│  • Bot stops NEW trades at 80% of daily loss limit              │
│    (e.g., $1600/$2000)                                           │
│  • Bot stops NEW trades at 80% of max drawdown                  │
│    (e.g., 6.4%/8%)                                               │
│  • Existing positions are managed normally (stop losses,         │
│    exits)                                                        │
│  • Bot continues running and monitoring market conditions        │
│  • Bot will NOT attempt recovery trades                          │
│  • Safest option for prop firm accounts                          │
└─────────────────────────────────────────────────────────────────┘

[Other settings continue...]
```

## When User Unchecks the Box (Recovery Mode)

```
┌─────────────────────────────────────────────────────────────────┐
│  Prop Firm Safety Mode:                                          │
│                                                                   │
│  ☐ Stop Trading When Approaching Failure                         │
│     (Recommended for Prop Firms)                                 │
│                                                                   │
│  ⚠️ RECOVERY MODE: Bot will continue trading even when close to  │
│    failure, using ONLY high-confidence signals (automatically    │
│    increases confidence threshold). This gives the bot a chance  │
│    to recover from a bad day, but increases risk of account      │
│    failure. Use with caution!                                    │
│                                                                   │
│  When disabled (Recovery Mode):                                  │
│  • Bot continues trading even close to limits                    │
│  • Auto-increases confidence threshold to 75%+ (only takes       │
│    best signals)                                                 │
│  • Reduces position size when in danger zone                     │
│  • Attempts to recover from drawdown/daily losses                │
│  • Higher risk - could lead to account failure if signals are    │
│    wrong                                                         │
│  • Use only if you're confident in the bot's performance         │
└─────────────────────────────────────────────────────────────────┘
```

## Launch Confirmation Dialog (with Setting Enabled)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Launch Trading Bot?                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Ready to start bot with these settings:                         │
│                                                                   │
│  Broker: TopStep                                                 │
│  Account: TopStep Account 1 - $50,000.00                        │
│  Symbols: ES                                                     │
│  Contracts Per Trade: 3                                          │
│  Max Drawdown: 8.0%                                              │
│  Daily Loss Limit: $2000                                         │
│    → Bot stays on but will NOT execute trades if limit is hit   │
│    → Resets daily after market maintenance                       │
│  Max Trades/Day: 10                                              │
│    → Bot stays on but will NOT execute trades after limit       │
│    → Resets daily after market maintenance                       │
│  Confidence Threshold: 65.0% (Min - dynamic adjustments          │
│    enabled)                                                      │
│    → Bot may auto-increase confidence when needed (never         │
│      below minimum)                                              │
│                                                                   │
│  Prop Firm Safety: STOP when approaching failure (80% of         │
│    limits)                                                       │
│    → Bot stops NEW trades when getting close to account failure │
│    → Continues monitoring but won't trade until safe            │
│                                                                   │
│  This will open a PowerShell terminal with live logs.            │
│  Use the window's close button to stop the bot.                  │
│                                                                   │
│  Continue?                                                       │
│                                                                   │
│                     [ Yes ]    [ No ]                             │
└─────────────────────────────────────────────────────────────────┘
```

## Launch Confirmation Dialog (with Recovery Mode)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Launch Trading Bot?                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Ready to start bot with these settings:                         │
│                                                                   │
│  [... other settings ...]                                        │
│                                                                   │
│  ⚠️ Recovery Mode: Continue trading when close to failure        │
│    → Bot will attempt recovery with high confidence signals      │
│      only                                                        │
│    → Higher risk - use with caution!                             │
│                                                                   │
│  This will open a PowerShell terminal with live logs.            │
│  Use the window's close button to stop the bot.                  │
│                                                                   │
│  Continue?                                                       │
│                                                                   │
│                     [ Yes ]    [ No ]                             │
└─────────────────────────────────────────────────────────────────┘
```

## Visual Characteristics

### Color Coding:
- **Safe Mode (Enabled)**: Green text and checkmark ✓
- **Recovery Mode (Disabled)**: Orange/warning text and warning icon ⚠️
- **Section**: Light blue elevated card with subtle border

### Layout:
- Positioned after "Dynamic Contract Mode" section
- Before "Trailing Drawdown Section"
- Same styling as other advanced settings
- Clear visual separation with card borders
- Comprehensive tooltips that update based on selection

### Interactive Elements:
- Checkbox with hover effects
- Dynamic info label that changes based on checkbox state
- Detailed explanation text that updates in real-time
- Mouse cursor changes to "hand" when hovering over checkbox

### User Experience:
- Default is CHECKED (safe mode) for prop firms
- Default is UNCHECKED for live brokers
- Clear warnings when selecting recovery mode
- Comprehensive explanations prevent user confusion
- Settings are saved and restored on next launch
