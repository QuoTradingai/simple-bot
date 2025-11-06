"""
Test script to create sample trade summary files
This simulates what the bot will write when a trade completes
"""

import json
import time
from datetime import datetime

# Create a sample trade summary
trade_summary = {
    'symbol': 'ES',
    'direction': 'LONG',
    'entry_price': 4500.00,
    'exit_price': 4506.25,
    'contracts': 2,
    'pnl': 156.25,
    'pnl_percent': 0.31,
    'timestamp': datetime.now().isoformat(),
    'reason': 'target_hit'
}

print("Writing trade_summary.json...")
with open('trade_summary.json', 'w') as f:
    json.dump(trade_summary, f, indent=2)
print("✓ Trade summary written")

# Wait a moment
time.sleep(1)

# Create a sample daily summary
daily_summary = {
    'total_pnl': 156.25,
    'wins': 1,
    'losses': 0,
    'account_balance': 50156.25,
    'timestamp': datetime.now().isoformat()
}

print("Writing daily_summary.json...")
with open('daily_summary.json', 'w') as f:
    json.dump(daily_summary, f, indent=2)
print("✓ Daily summary written")

print("\nNow launch the GUI and watch the Trade Summary console!")
print("You should see:")
print("  ES LONG @ 4500.00 → EXIT @ 4506.25 | +$156.25 (+0.31%)")
print("  ─────────────────────────────────")
print("  Today: +$156.25 | 1W, 0L | Balance: $50,156.25")
