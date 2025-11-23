#!/usr/bin/env python3
"""
Validate RL Execution Data for Live Trading
==========================================
Ensures that execution data is being captured and sent to cloud RL
for proper learning during live trading.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_execution_data_in_cloud_api():
    """Check that cloud_api.py sends execution_data"""
    print("\n[1/3] Checking cloud API client...")
    
    cloud_api_path = Path(__file__).parent.parent / 'src' / 'cloud_api.py'
    with open(cloud_api_path, 'r') as f:
        content = f.read()
    
    checks = [
        ('execution_data parameter in signature', 'execution_data: Dict = None' in content),
        ('execution_data in docstring', 'execution_data:' in content and 'Execution quality metrics' in content),
        ('execution_data added to payload', 'payload["execution_data"]' in content),
        ('order_type_used documented', 'order_type_used' in content),
        ('entry_slippage_ticks documented', 'entry_slippage_ticks' in content),
        ('exit_reason documented', 'exit_reason' in content),
    ]
    
    all_ok = True
    for check_name, check_result in checks:
        if check_result:
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name}")
            all_ok = False
    
    return all_ok


def check_execution_data_in_engine():
    """Check that quotrading_engine.py passes execution_data"""
    print("\n[2/3] Checking trading engine...")
    
    engine_path = Path(__file__).parent.parent / 'src' / 'quotrading_engine.py'
    with open(engine_path, 'r') as f:
        content = f.read()
    
    checks = [
        ('execution_data parameter in function', 'execution_data: Dict[str, Any]' in content),
        ('execution_data passed to cloud', 'execution_data  # Pass execution data' in content or 'execution_data)' in content),
        ('execution_data passed to local RL', 'rl_brain.record_outcome' in content and 'execution_data' in content),
    ]
    
    all_ok = True
    for check_name, check_result in checks:
        if check_result:
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name}")
            all_ok = False
    
    return all_ok


def check_execution_data_in_flask_api():
    """Check that Flask API stores execution_data"""
    print("\n[3/3] Checking Flask API...")
    
    flask_api_path = Path(__file__).parent.parent / 'cloud-api' / 'flask-api' / 'app.py'
    with open(flask_api_path, 'r') as f:
        content = f.read()
    
    checks = [
        ('execution_data extracted from request', 'execution_data = data.get(\'execution_data\'' in content),
        ('order_type_used stored in database', 'order_type_used' in content),
        ('entry_slippage_ticks stored in database', 'entry_slippage_ticks' in content),
        ('exit_reason stored in database', 'exit_reason' in content),
        ('execution_data documented in docstring', 'execution_data' in content and 'execution quality metrics' in content),
    ]
    
    all_ok = True
    for check_name, check_result in checks:
        if check_result:
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name}")
            all_ok = False
    
    return all_ok


def check_migration_exists():
    """Check that database migration exists"""
    print("\n[BONUS] Checking database migration...")
    
    migration_path = Path(__file__).parent.parent / 'cloud-api' / 'flask-api' / 'migrations' / 'add_execution_data_to_rl_experiences.sql'
    
    if migration_path.exists():
        print(f"   ✅ Migration file exists: {migration_path.name}")
        
        with open(migration_path, 'r') as f:
            content = f.read()
        
        if 'order_type_used' in content and 'entry_slippage_ticks' in content and 'exit_reason' in content:
            print(f"   ✅ Migration includes all execution data columns")
            return True
        else:
            print(f"   ⚠️  Migration may be incomplete")
            return False
    else:
        print(f"   ❌ Migration file not found")
        return False


def main():
    """Main entry point"""
    print("=" * 80)
    print("RL EXECUTION DATA VALIDATION FOR LIVE TRADING")
    print("=" * 80)
    
    results = {
        'cloud_api': check_execution_data_in_cloud_api(),
        'engine': check_execution_data_in_engine(),
        'flask_api': check_execution_data_in_flask_api(),
        'migration': check_migration_exists(),
    }
    
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    passed = sum(results.values())
    total = len(results)
    
    for component, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {component.upper().replace('_', ' ')}")
    
    print("\n" + "=" * 80)
    
    if passed == total:
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("\nExecution data will be captured and sent to cloud RL for learning!")
        print("\nNext steps:")
        print("  1. Run database migration: add_execution_data_to_rl_experiences.sql")
        print("  2. Restart Flask API to load new code")
        print("  3. Test with live trading to verify data is being saved")
    else:
        print(f"❌ VALIDATION FAILED ({passed}/{total})")
        print("\nFix the issues above before deploying to live trading.")
    
    print("=" * 80)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
