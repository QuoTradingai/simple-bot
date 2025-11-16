"""
Migrate old experience files to new feature set.

Exit System: 64 features -> 62 features (remove bid_ask_spread_ticks, slippage_ticks, rejected_partial_count)
Signal System: 33 features -> 31 features (remove bid_ask_spread_ticks, entry_slippage_ticks)

This script removes the obsolete features from outcome metadata to keep files clean.
"""

import json
import shutil
from pathlib import Path

def migrate_exit_experiences():
    """Remove slippage_ticks, bid_ask_spread_ticks from exit experience outcomes."""
    
    filepath = Path('../data/local_experiences/exit_experiences_v2.json')
    backup_path = Path('../data/local_experiences/exit_experiences_v2.json.backup')
    
    # Create backup
    shutil.copy2(filepath, backup_path)
    print(f"✓ Backed up to {backup_path}")
    
    # Load data
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    print(f"Processing {len(data['experiences'])} exit experiences...")
    
    # Remove obsolete fields from outcomes
    removed_count = 0
    for exp in data['experiences']:
        if 'outcome' in exp:
            removed = False
            if 'slippage_ticks' in exp['outcome']:
                del exp['outcome']['slippage_ticks']
                removed = True
            if 'bid_ask_spread_ticks' in exp['outcome']:
                del exp['outcome']['bid_ask_spread_ticks']
                removed = True
            if removed:
                removed_count += 1
    
    # Save updated data
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Removed obsolete fields from {removed_count} exit experiences")
    print(f"✓ Saved to {filepath}")
    

def migrate_signal_experiences():
    """Remove entry_slippage_ticks, bid_ask_spread_ticks from signal experiences."""
    
    filepath = Path('../data/local_experiences/signal_experiences_v2.json')
    backup_path = Path('../data/local_experiences/signal_experiences_v2.json.backup')
    
    # Create backup
    shutil.copy2(filepath, backup_path)
    print(f"✓ Backed up to {backup_path}")
    
    # Load data
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    print(f"Processing {len(data['experiences'])} signal experiences...")
    
    # Remove obsolete fields
    removed_count = 0
    for exp in data['experiences']:
        removed = False
        if 'entry_slippage_ticks' in exp:
            del exp['entry_slippage_ticks']
            removed = True
        if 'bid_ask_spread_ticks' in exp:
            del exp['bid_ask_spread_ticks']
            removed = True
        if removed:
            removed_count += 1
    
    # Save updated data
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Removed obsolete fields from {removed_count} signal experiences")
    print(f"✓ Saved to {filepath}")


if __name__ == '__main__':
    print("="*60)
    print("MIGRATING EXPERIENCE FILES TO NEW FEATURE SET")
    print("="*60)
    print()
    
    print("Exit System: 64→62 features")
    print("  Removing: slippage_ticks, bid_ask_spread_ticks")
    print()
    migrate_exit_experiences()
    print()
    
    print("Signal System: 33→31 features")
    print("  Removing: entry_slippage_ticks, bid_ask_spread_ticks")
    print()
    migrate_signal_experiences()
    print()
    
    print("="*60)
    print("MIGRATION COMPLETE!")
    print("="*60)
    print()
    print("Your old experience data has been preserved with obsolete fields removed.")
    print("Backups saved with .backup extension.")
    print()
    print("Training scripts will now extract 62+31 features from this data.")
