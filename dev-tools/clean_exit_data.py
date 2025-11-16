"""Clean exit experiences - remove old incomplete data"""
import json
from datetime import datetime

with open('data/local_experiences/exit_experiences_v2.json', 'r') as f:
    raw = json.load(f)
    data = raw if isinstance(raw, list) else raw.get('experiences', raw)

print(f"Current exit experiences: {len(data)}")

# Keep only experiences that have the new fields
clean_data = []
for exp in data:
    outcome = exp.get('outcome', {})
    # Check if it has the new fields we added
    if outcome.get('profit_ticks', 0) != 0 or outcome.get('initial_risk_ticks', 0) != 0:
        clean_data.append(exp)

print(f"Experiences with complete data: {len(clean_data)}")
print(f"Removing {len(data) - len(clean_data)} incomplete experiences")

# Save cleaned data
with open('data/local_experiences/exit_experiences_v2.json', 'w') as f:
    json.dump(clean_data, f, indent=2)

print(f"\n✅ Cleaned! Now have {len(clean_data)} complete exit experiences")
print(f"   Run more backtests to collect fresh data with all fields")
