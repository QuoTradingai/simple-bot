import pandas as pd
from datetime import datetime

# Load backtest trades
df = pd.read_csv('data/backtest_trades.csv')

# Filter forced_flatten trades
flatten_trades = df[df['exit_reason'] == 'forced_flatten']

print(f"Total forced_flatten trades: {len(flatten_trades)}")
print(f"1-minute trades: {len(flatten_trades[flatten_trades['duration_min'] == 1])}")
print(f"\n{'='*80}")
print("FORCED FLATTEN TRADES (1 minute duration):")
print(f"{'='*80}\n")

# Show 1-minute forced_flatten trades
one_min = flatten_trades[flatten_trades['duration_min'] == 1]
for idx, trade in one_min.iterrows():
    entry_time = datetime.fromisoformat(trade['entry_time'])
    exit_time = datetime.fromisoformat(trade['exit_time'])
    print(f"Entry: {entry_time.strftime('%m/%d %H:%M')} → Exit: {exit_time.strftime('%H:%M')} | "
          f"{trade['side']} | P&L: ${trade['pnl']:+.2f} | Entry: {entry_time.hour}:{entry_time.minute:02d}")

print(f"\n{'='*80}")
print("DURATION DISTRIBUTION OF FORCED_FLATTEN:")
print(f"{'='*80}\n")
print(flatten_trades['duration_min'].value_counts().sort_index().head(10))
