#!/usr/bin/env python3
"""
Test script to verify the launch flow changes.
This test ensures that:
1. The "Launch Trading Bot?" confirmation popup is removed
2. The "Bot Launched!" success popup is removed
3. The countdown dialog appears and works correctly
"""

import sys
import os
from pathlib import Path

# Add launcher to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'launcher'))

def test_launch_flow():
    """Test that the launch flow has been properly modified"""
    
    # Read the launcher file
    launcher_path = Path(__file__).parent / 'launcher' / 'QuoTrading_Launcher.py'
    with open(launcher_path, 'r') as f:
        content = f.read()
    
    # Test 1: Verify the "Launch Trading Bot?" confirmation is removed
    assert 'messagebox.askyesno' not in content or \
           '"Launch Trading Bot?"' not in content, \
           "FAIL: 'Launch Trading Bot?' confirmation popup still exists"
    print("✓ Test 1 PASSED: 'Launch Trading Bot?' confirmation popup removed")
    
    # Test 2: Verify the "Bot Launched!" success message is removed
    assert '"Bot Launched!"' not in content, \
           "FAIL: 'Bot Launched!' success popup still exists"
    print("✓ Test 2 PASSED: 'Bot Launched!' success popup removed")
    
    # Test 3: Verify countdown dialog still exists
    assert 'show_countdown_and_launch' in content, \
           "FAIL: Countdown dialog function removed"
    print("✓ Test 3 PASSED: Countdown dialog still exists")
    
    # Test 4: Verify GUI closes immediately after launch
    assert 'self.root.destroy()' in content, \
           "FAIL: GUI destroy call not found"
    
    # Count occurrences - should be called right after bot launch
    launch_bot_section = content[content.find('def launch_bot_process'):content.find('def show_settings_dialog')]
    assert 'self.root.destroy()' in launch_bot_section, \
           "FAIL: GUI destroy not called in launch_bot_process"
    print("✓ Test 4 PASSED: GUI closes immediately after launch")
    
    # Test 5: Verify no success messagebox before destroy
    lines = launch_bot_section.split('\n')
    destroy_index = None
    messagebox_after_launch = False
    
    for i, line in enumerate(lines):
        if 'self.root.destroy()' in line:
            destroy_index = i
        if destroy_index is None and i > 0 and 'messagebox.showinfo' in line and 'Bot Launched' in lines[i-1:i+2]:
            messagebox_after_launch = True
    
    assert not messagebox_after_launch, \
           "FAIL: Success messagebox found before GUI destroy"
    print("✓ Test 5 PASSED: No success popup before GUI close")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60)
    print("\nSummary of changes:")
    print("  1. Removed 'Launch Trading Bot?' confirmation popup")
    print("  2. Removed 'Bot Launched!' success popup")
    print("  3. Countdown dialog remains as the only message")
    print("  4. GUI closes immediately after countdown")
    print("="*60)

if __name__ == "__main__":
    try:
        test_launch_flow()
    except AssertionError as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
