import json
from pathlib import Path

# Load exit experiences
exit_file = Path('data/local_experiences/exit_experiences_v2.json')
with open(exit_file) as f:
    exit_data = json.load(f)

print("=" * 80)
print("EXIT EXPERIENCES STRUCTURE")
print("=" * 80)

print(f"\nTop-level keys: {list(exit_data.keys())}")
print(f"Total experiences: {exit_data.get('count', 'N/A')}")
print(f"Version: {exit_data.get('version', 'N/A')}")
print(f"Last updated: {exit_data.get('last_updated', 'N/A')}")

experiences = exit_data.get('experiences', [])
print(f"\nActual experiences in list: {len(experiences)}")

if len(experiences) > 0:
    last_exp = experiences[-1]
    
    print(f"\n{'='*80}")
    print("LAST EXIT EXPERIENCE STRUCTURE")
    print(f"{'='*80}")
    
    print(f"\nTop-level keys: {list(last_exp.keys())}")
    
    if 'outcome' in last_exp:
        print(f"\nOUTCOME fields ({len(last_exp['outcome'])} total):")
        for i, key in enumerate(last_exp['outcome'].keys(), 1):
            print(f"  {i:2}. {key}")
    
    if 'market_state' in last_exp:
        print(f"\nMARKET_STATE fields ({len(last_exp['market_state'])} total):")
        for i, key in enumerate(last_exp['market_state'].keys(), 1):
            print(f"  {i:2}. {key}")
    
    if 'exit_params' in last_exp:
        print(f"\nEXIT_PARAMS ({len(last_exp['exit_params'])} total):")
        for i, key in enumerate(sorted(last_exp['exit_params'].keys())[:20], 1):
            value = last_exp['exit_params'][key]
            print(f"  {i:2}. {key}: {value}")
        print(f"  ... and {len(last_exp['exit_params']) - 20} more parameters")
    
    # Show a complete sample
    print(f"\n{'='*80}")
    print("SAMPLE EXIT EXPERIENCE (LAST TRADE)")
    print(f"{'='*80}")
    print(json.dumps(last_exp, indent=2)[:2000])
    print("\n... (truncated)")
