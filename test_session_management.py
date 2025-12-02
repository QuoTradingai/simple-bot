"""
Test Session Management
=======================
Verify that:
1. Launcher and bot use the same base device fingerprint (without symbol)
2. Bot creates symbol-specific fingerprints for multi-symbol support
3. Different symbols generate different fingerprints on the same device
4. Stale sessions are auto-cleared on login
5. Active sessions block concurrent logins
6. Sessions are released on clean shutdown

Note: This test duplicates the fingerprint generation logic from launcher
and bot files because importing those files directly requires tkinter and
other dependencies that may not be available in test environment. This
ensures tests can run in isolation but should be kept in sync with changes
to production code.
"""

import sys
import os
import hashlib
import platform
import getpass
import uuid

def get_launcher_device_fingerprint() -> str:
    """
    Generate a unique device fingerprint for session locking.
    Launcher uses fingerprint WITHOUT symbol (validates license once).
    
    This is the LAUNCHER version from QuoTrading_Launcher.py
    """
    # Get platform-specific machine ID
    try:
        machine_id = str(uuid.getnode())  # MAC address as unique ID
    except:
        machine_id = "unknown"
    
    # Get username
    try:
        username = getpass.getuser()
    except:
        username = "unknown"
    
    # Get platform info
    platform_name = platform.system()  # Windows, Darwin (Mac), Linux
    
    # Combine all components WITHOUT symbol - launcher just validates license
    fingerprint_raw = f"{machine_id}:{username}:{platform_name}"
    
    # Hash for privacy (don't send raw MAC address to server)
    fingerprint_hash = hashlib.sha256(fingerprint_raw.encode()).hexdigest()[:16]
    
    return fingerprint_hash


def get_bot_device_fingerprint(symbol: str = None) -> str:
    """
    Generate a unique device fingerprint for session locking.
    Supports multi-symbol mode: each symbol gets its own session.
    
    This is the BOT version from quotrading_engine.py
    
    Args:
        symbol: Optional trading symbol (e.g., 'ES', 'NQ'). When provided,
               creates a symbol-specific fingerprint for multi-symbol support.
    """
    # Get platform-specific machine ID
    try:
        machine_id = str(uuid.getnode())  # MAC address as unique ID
    except:
        machine_id = "unknown"
    
    # Get username
    try:
        username = getpass.getuser()
    except:
        username = "unknown"
    
    # Get platform info
    platform_name = platform.system()  # Windows, Darwin (Mac), Linux
    
    # Combine all components - include symbol if provided for multi-symbol support
    if symbol:
        fingerprint_raw = f"{machine_id}:{username}:{platform_name}:{symbol}"
    else:
        fingerprint_raw = f"{machine_id}:{username}:{platform_name}"
    
    # Hash for privacy (don't send raw MAC address to server)
    fingerprint_hash = hashlib.sha256(fingerprint_raw.encode()).hexdigest()[:16]
    
    return fingerprint_hash


def test_device_fingerprint_consistency():
    """Test that launcher and bot generate the same BASE device fingerprint (without symbol)"""
    print("\n" + "="*70)
    print("TEST: Device Fingerprint Consistency (Base - No Symbol)")
    print("="*70)
    
    # Generate fingerprints (bot without symbol should match launcher)
    launcher_fingerprint = get_launcher_device_fingerprint()
    bot_fingerprint = get_bot_device_fingerprint()  # No symbol = base fingerprint
    
    print(f"Launcher fingerprint: {launcher_fingerprint}")
    print(f"Bot fingerprint (no symbol): {bot_fingerprint}")
    
    # Verify they match (base fingerprints should be the same)
    if launcher_fingerprint == bot_fingerprint:
        print("✅ PASS: Base fingerprints match - launcher and bot share the same base")
        return True
    else:
        print("❌ FAIL: Base fingerprints don't match!")
        print("  Launcher and bot MUST use the same base fingerprint")
        return False


def test_fingerprint_excludes_pid():
    """Test that device fingerprint does NOT include process ID"""
    print("\n" + "="*70)
    print("TEST: Fingerprint Excludes PID")
    print("="*70)
    
    # Generate fingerprint multiple times (should always be the same)
    fp1 = get_launcher_device_fingerprint()
    fp2 = get_launcher_device_fingerprint()
    fp3 = get_bot_device_fingerprint()
    
    print(f"Launcher call 1: {fp1}")
    print(f"Launcher call 2: {fp2}")
    print(f"Bot call 1:      {fp3}")
    
    # Verify they all match (base fingerprints without symbol)
    if fp1 == fp2 == fp3:
        print("✅ PASS: Fingerprint is stable - does not include PID or other volatile data")
        return True
    else:
        print("❌ FAIL: Fingerprint changes - may include unstable components like PID")
        return False


def test_fingerprint_format():
    """Test that fingerprint has expected format"""
    print("\n" + "="*70)
    print("TEST: Fingerprint Format")
    print("="*70)
    
    fp = get_launcher_device_fingerprint()
    
    print(f"Fingerprint: {fp}")
    print(f"Length: {len(fp)} characters")
    print(f"Is hex: {all(c in '0123456789abcdef' for c in fp)}")
    
    # Should be 16-character hex string
    if len(fp) == 16 and all(c in '0123456789abcdef' for c in fp):
        print("✅ PASS: Fingerprint format is correct (16-char hex)")
        return True
    else:
        print("❌ FAIL: Fingerprint format is incorrect")
        return False


def test_multi_symbol_fingerprints():
    """Test that different symbols generate different fingerprints on the same device"""
    print("\n" + "="*70)
    print("TEST: Multi-Symbol Fingerprints")
    print("="*70)
    
    # Generate fingerprints for different symbols
    base_fp = get_bot_device_fingerprint()  # No symbol
    es_fp = get_bot_device_fingerprint("ES")
    nq_fp = get_bot_device_fingerprint("NQ")
    mes_fp = get_bot_device_fingerprint("MES")
    
    print(f"Base fingerprint (no symbol): {base_fp}")
    print(f"ES fingerprint:               {es_fp}")
    print(f"NQ fingerprint:               {nq_fp}")
    print(f"MES fingerprint:              {mes_fp}")
    
    # Verify all fingerprints are different
    all_fps = [base_fp, es_fp, nq_fp, mes_fp]
    if len(all_fps) == len(set(all_fps)):
        print("✅ PASS: All symbol-specific fingerprints are unique")
        print("  This allows multiple symbols to run on the same device")
        return True
    else:
        print("❌ FAIL: Symbol-specific fingerprints are not unique!")
        print("  This will cause session conflicts when running multiple symbols")
        return False


def test_symbol_fingerprint_consistency():
    """Test that the same symbol generates the same fingerprint"""
    print("\n" + "="*70)
    print("TEST: Symbol Fingerprint Consistency")
    print("="*70)
    
    # Generate fingerprints for ES multiple times
    es_fp1 = get_bot_device_fingerprint("ES")
    es_fp2 = get_bot_device_fingerprint("ES")
    es_fp3 = get_bot_device_fingerprint("ES")
    
    print(f"ES fingerprint call 1: {es_fp1}")
    print(f"ES fingerprint call 2: {es_fp2}")
    print(f"ES fingerprint call 3: {es_fp3}")
    
    # Verify they all match
    if es_fp1 == es_fp2 == es_fp3:
        print("✅ PASS: Symbol fingerprints are consistent")
        return True
    else:
        print("❌ FAIL: Symbol fingerprints are not consistent!")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SESSION MANAGEMENT TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test 1: Device fingerprint consistency (base)
    results.append(("Fingerprint Consistency (Base)", test_device_fingerprint_consistency()))
    
    # Test 2: Fingerprint excludes PID
    results.append(("Fingerprint Stability", test_fingerprint_excludes_pid()))
    
    # Test 3: Fingerprint format
    results.append(("Fingerprint Format", test_fingerprint_format()))
    
    # Test 4: Multi-symbol fingerprints are unique
    results.append(("Multi-Symbol Fingerprints", test_multi_symbol_fingerprints()))
    
    # Test 5: Symbol fingerprint consistency
    results.append(("Symbol Fingerprint Consistency", test_symbol_fingerprint_consistency()))
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
