import json

# Load signal experiences
with open('cloud-api/signal_experience.json') as f:
    signal_data = json.load(f)

experiences = signal_data['experiences']

wins = [e for e in experiences if e['reward'] > 0]
losses = [e for e in experiences if e['reward'] < 0]
breakeven = [e for e in experiences if e['reward'] == 0]

total = len(experiences)
win_count = len(wins)
loss_count = len(losses)

avg_win = sum([e['reward'] for e in wins]) / len(wins) if wins else 0
avg_loss = sum([e['reward'] for e in losses]) / len(losses) if losses else 0
total_pnl = sum([e['reward'] for e in experiences])

print(f"\n{'='*60}")
print(f"CLOUD RL EXPERIENCES ANALYSIS (signal_experience.json)")
print(f"{'='*60}")
print(f"Total Experiences: {total:,}")
print(f"Wins: {win_count:,} ({win_count/total*100:.1f}%)")
print(f"Losses: {loss_count:,} ({loss_count/total*100:.1f}%)")
print(f"Breakeven: {len(breakeven):,} ({len(breakeven)/total*100:.1f}%)")
print(f"\nAvg Win: ${avg_win:.2f}")
print(f"Avg Loss: ${avg_loss:.2f}")
print(f"Total P&L: ${total_pnl:,.2f}")
print(f"Profit Factor: {abs(sum([e['reward'] for e in wins]) / sum([e['reward'] for e in losses])):.2f}")
print(f"{'='*60}\n")

# Show sample winning trade
print("Sample WINNING trade:")
print(json.dumps(wins[0], indent=2))

print("\nSample LOSING trade:")
print(json.dumps(losses[0], indent=2))
