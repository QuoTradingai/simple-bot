#!/usr/bin/env python3
"""Check how many experiences were restored from git"""
import json

# Check signal experiences
with open('cloud-api/signal_experience.json', 'r') as f:
    signal_data = json.load(f)
    signal_count = len(signal_data.get('experiences', []))
    print(f"✅ Signal experiences restored: {signal_count:,}")

# Check exit experiences  
with open('cloud-api/exit_experience.json', 'r') as f:
    exit_data = json.load(f)
    exit_count = len(exit_data.get('exit_experiences', []))
    print(f"✅ Exit experiences restored: {exit_count:,}")

print(f"\n🧠 TOTAL: {signal_count + exit_count:,} experiences ready for cloud!")
