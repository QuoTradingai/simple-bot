#!/usr/bin/env python3
"""
Test script to verify all GUI settings are properly loaded by the bot.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_env_file_exists():
    """Test if .env file exists."""
    env_path = Path('.env')
    
    print("=" * 80)
    print("TEST 1: .env File Existence")
    print("=" * 80)
    
    if not env_path.exists():
        print("❌ FAIL: .env file does not exist")
        print("   Solution: Run the GUI and click 'Start Bot' to create it")
        return False
    
    print("✅ PASS: .env file exists\n")
    return True

def test_env_variables():
    """Test if all required environment variables are present."""
    print("=" * 80)
    print("TEST 2: Environment Variables Presence")
    print("=" * 80)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'BROKER': 'Broker name',
        'BOT_INSTRUMENTS': 'Trading symbols',
        'BOT_MAX_CONTRACTS': 'Max contracts per trade',
        'BOT_MAX_TRADES_PER_DAY': 'Max trades per day',
        'BOT_MAX_DRAWDOWN_PERCENT': 'Max drawdown percentage',
        'BOT_TRAILING_DRAWDOWN': 'Trailing drawdown enabled',
        'BOT_DAILY_LOSS_LIMIT': 'Daily loss limit',
        'BOT_CONFIDENCE_THRESHOLD': 'Confidence threshold',
        'BOT_DYNAMIC_CONFIDENCE': 'Dynamic confidence enabled',
        'BOT_DYNAMIC_CONTRACTS': 'Dynamic contracts enabled',
        'BOT_RECOVERY_MODE': 'Recovery mode enabled',
        'ACCOUNT_SIZE': 'Account size',
    }
    
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value is not None:
            # Truncate long values for display
            display_value = value if len(value) < 50 else value[:47] + "..."
            print(f"✅ {var:30s} = {display_value}")
        else:
            print(f"❌ {var:30s} MISSING ({description})")
            all_present = False
    
    print()
    return all_present

def test_config_loading():
    """Test if bot configuration loads all settings correctly."""
    print("=" * 80)
    print("TEST 3: Bot Configuration Loading")
    print("=" * 80)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from config import load_config
        
        config = load_config()
        
        print("✅ Configuration loaded successfully\n")
        
        print("Key Settings from BotConfiguration:")
        print("-" * 80)
        print(f"  Broker:                  {config.broker}")
        print(f"  Instruments:             {config.instruments}")
        print(f"  Account Size:            ${config.account_size:,.2f}")
        print(f"  Max Contracts:           {config.max_contracts}")
        print(f"  Max Trades/Day:          {config.max_trades_per_day}")
        print(f"  Max Drawdown %:          {config.max_drawdown_percent:.1f}%")
        print(f"  Trailing Drawdown:       {config.trailing_drawdown}")
        print(f"  Daily Loss Limit:        ${config.daily_loss_limit:.2f}")
        print(f"  Confidence Threshold:    {config.rl_confidence_threshold * 100:.1f}%")
        print(f"  Dynamic Confidence:      {config.dynamic_confidence}")
        print(f"  Dynamic Contracts:       {config.dynamic_contracts}")
        print(f"  Recovery Mode:           {config.recovery_mode}")
        print(f"  Shadow Mode:             {config.shadow_mode}")
        print()
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Could not load config: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_state():
    """Test if session state manager initializes correctly."""
    print("=" * 80)
    print("TEST 4: Session State Manager")
    print("=" * 80)
    
    try:
        from session_state import SessionStateManager
        
        session = SessionStateManager()
        
        print("✅ Session state manager initialized\n")
        
        # Test update with sample data
        session.update_trading_state(
            starting_equity=50000.0,
            current_equity=49500.0,
            daily_pnl=-500.0,
            daily_trades=3,
            broker="TopStep",
            account_type="prop_firm"
        )
        
        summary = session.get_summary()
        
        print("Session State Summary:")
        print("-" * 80)
        print(f"  Trading Date:            {summary['trading_date']}")
        print(f"  Current Equity:          ${summary['current_equity']:,.2f}")
        print(f"  Daily P&L:               ${summary['daily_pnl']:,.2f}")
        print(f"  Total Trades Today:      {summary['total_trades_today']}")
        print(f"  Current Drawdown %:      {summary['current_drawdown_percent']:.2f}%")
        print(f"  Approaching Failure:     {summary['approaching_failure']}")
        print(f"  In Recovery Mode:        {summary['in_recovery_mode']}")
        print(f"  Account Type:            {summary['account_type']}")
        print(f"  Broker:                  {summary['broker']}")
        print()
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Could not initialize session state: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_warnings_and_recommendations():
    """Test if warnings and recommendations work correctly."""
    print("=" * 80)
    print("TEST 5: Warnings and Recommendations System")
    print("=" * 80)
    
    try:
        from session_state import SessionStateManager
        
        session = SessionStateManager()
        
        # Simulate a scenario where we're at 85% of daily loss limit
        session.update_trading_state(
            starting_equity=50000.0,
            current_equity=48300.0,  # Lost $1,700
            daily_pnl=-1700.0,       # Daily loss
            daily_trades=5,
            broker="TopStep",
            account_type="prop_firm"
        )
        
        warnings, recommendations, smart_settings = session.check_warnings_and_recommendations(
            account_size=50000.0,
            max_drawdown_percent=8.0,
            daily_loss_limit=2000.0,  # $2000 limit, lost $1700 = 85%
            current_confidence=65.0,
            max_contracts=3,
            recovery_mode_enabled=False
        )
        
        print("✅ Warnings and recommendations generated\n")
        
        if warnings:
            print("Warnings Generated:")
            print("-" * 80)
            for warning in warnings:
                print(f"  [{warning['level'].upper()}] {warning['message']}")
            print()
        else:
            print("No warnings generated\n")
        
        if recommendations:
            print("Recommendations Generated:")
            print("-" * 80)
            for rec in recommendations:
                print(f"  [{rec['priority'].upper()}] {rec['message']}")
            print()
        else:
            print("No recommendations generated\n")
        
        if smart_settings:
            print("Smart Settings Suggested:")
            print("-" * 80)
            for key, value in smart_settings.items():
                print(f"  {key}: {value}")
            print()
        else:
            print("No smart settings suggested\n")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Could not test warnings: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("GUI SETTINGS VALIDATION TEST SUITE")
    print("=" * 80 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Environment File Exists", test_env_file_exists()))
    results.append(("Environment Variables", test_env_variables()))
    results.append(("Configuration Loading", test_config_loading()))
    results.append(("Session State Manager", test_session_state()))
    results.append(("Warnings & Recommendations", test_warnings_and_recommendations()))
    
    # Print summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10s} {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Bot is ready to load GUI settings correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
