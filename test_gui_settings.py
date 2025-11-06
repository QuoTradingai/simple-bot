"""
Test GUI Settings Flow
======================
Validates that GUI settings are properly saved and loaded.
"""

from pathlib import Path
import os

def test_env_file_creation():
    """Test if .env file exists and has correct format."""
    env_path = Path('.env')
    
    print("=" * 60)
    print("TEST 1: .env File Existence")
    print("=" * 60)
    
    if not env_path.exists():
        print("❌ FAIL: .env file does not exist")
        print("   Run the GUI and click 'Start Bot' to create it")
        return False
    
    print("✅ PASS: .env file exists")
    
    # Read and display content
    with open(env_path, 'r') as f:
        content = f.read()
    
    print("\n" + "=" * 60)
    print("TEST 2: .env File Content")
    print("=" * 60)
    print(content)
    
    # Check for required fields
    required_fields = [
        'QUOTRADING_LICENSE_KEY',
        'BROKER',
        'BROKER_API_TOKEN',
        'BROKER_USERNAME',
        'BOT_INSTRUMENTS',
        'BOT_MAX_CONTRACTS',
        'BOT_MAX_TRADES_PER_DAY',
        'BOT_RISK_PER_TRADE',
        'BOT_DAILY_LOSS_LIMIT'
    ]
    
    print("\n" + "=" * 60)
    print("TEST 3: Required Fields")
    print("=" * 60)
    
    all_present = True
    for field in required_fields:
        if field in content:
            # Extract value
            for line in content.split('\n'):
                if line.startswith(field):
                    value = line.split('=', 1)[1] if '=' in line else ''
                    print(f"✅ {field:30s} = {value}")
                    break
        else:
            print(f"❌ {field:30s} MISSING")
            all_present = False
    
    return all_present

def test_bot_config_loading():
    """Test if bot correctly loads .env settings."""
    print("\n" + "=" * 60)
    print("TEST 4: Bot Configuration Loading")
    print("=" * 60)
    
    try:
        from src.config import load_config
        
        config = load_config()
        
        print(f"✅ Config loaded successfully")
        print(f"\nKey Settings:")
        print(f"  Broker:           {config.broker}")
        print(f"  Instruments:      {config.instruments}")
        print(f"  Max Contracts:    {config.max_contracts}")
        print(f"  Max Trades/Day:   {config.max_trades_per_day}")
        print(f"  Risk Per Trade:   {config.risk_per_trade * 100}%")
        print(f"  Daily Loss Limit: ${config.daily_loss_limit}")
        print(f"  Shadow Mode:      {config.shadow_mode}")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Could not load config: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("GUI SETTINGS VALIDATION TEST")
    print("=" * 60)
    
    print("\nInstructions:")
    print("1. Open the GUI: python customer/QuoTrading_Launcher.py")
    print("2. Enter test credentials and settings")
    print("3. Click 'Start Bot' (it will create .env file)")
    print("4. Stop the bot")
    print("5. Run this test script")
    
    input("\nPress Enter when you've completed steps 1-4...")
    
    # Run tests
    test1_pass = test_env_file_creation()
    test2_pass = test_bot_config_loading()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if test1_pass and test2_pass:
        print("✅ ALL TESTS PASSED - GUI settings work correctly!")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")

if __name__ == "__main__":
    main()
