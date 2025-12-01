"""
Test script to verify duplicate launcher blocking at login screen.

Expected behavior:
1. First launcher validates with check_only=True -> No session created, proceeds to screen 2
2. Second launcher (same key, same machine) validates with check_only=True -> Should be BLOCKED
3. After killing first launcher and waiting 5 seconds -> Second launcher should succeed
"""

import requests
import json
import time
import os
import platform

# Same device fingerprint logic as launcher
def get_device_fingerprint():
    """Generate device fingerprint matching launcher logic"""
    machine_id = f"{platform.node()}-{os.getenv('COMPUTERNAME', 'unknown')}"
    username = os.getenv('USERNAME', 'unknown')
    platform_name = platform.system()
    pid = os.getpid()
    return f"{machine_id}:{username}:{platform_name}:{pid}"

API_URL = "https://quotrading-flask-api.azurewebsites.net/api/validate-license"
LICENSE_KEY = "C63W-L241-FVJ9-LGIR"

print("=" * 80)
print("TESTING DUPLICATE LAUNCHER BLOCKING AT LOGIN SCREEN")
print("=" * 80)

# Simulate First Launcher Login
print("\n[TEST 1] First launcher login (check_only=True)")
fingerprint1 = get_device_fingerprint()
print(f"Device Fingerprint: {fingerprint1}")

response1 = requests.post(API_URL, json={
    "license_key": LICENSE_KEY,
    "device_fingerprint": fingerprint1,
    "check_only": True
})
result1 = response1.json()
print(f"Response: {result1.get('message')}")
print(f"License Valid: {result1.get('license_valid')}")

if result1.get('license_valid'):
    print("✅ First launcher can proceed to screen 2")
else:
    print("❌ FAILED: First launcher was blocked!")
    exit(1)

# Simulate Second Launcher Login (different PID, same machine)
print("\n[TEST 2] Bot starts and creates session (check_only=False)")
# Simulate bot starting with different PID
bot_fingerprint = fingerprint1.rsplit(':', 1)[0] + ":22222"
print(f"Device Fingerprint: {bot_fingerprint}")

response2 = requests.post(API_URL, json={
    "license_key": LICENSE_KEY,
    "device_fingerprint": bot_fingerprint,
    "check_only": False  # Bot creates session
})
result2 = response2.json()
print(f"Response: {result2.get('message')}")
print(f"License Valid: {result2.get('license_valid')}")

if result2.get('license_valid'):
    print("✅ Bot session created successfully")
else:
    print("❌ FAILED: Bot couldn't create session!")
    exit(1)

print("\n[TEST 3] Second launcher tries to login while bot is running")
launcher2_fingerprint = fingerprint1.rsplit(':', 1)[0] + ":33333"
print(f"Device Fingerprint: {launcher2_fingerprint}")

response3 = requests.post(API_URL, json={
    "license_key": LICENSE_KEY,
    "device_fingerprint": launcher2_fingerprint,
    "check_only": True
})
result3 = response3.json()
print(f"Response: {result3.get('message')}")
print(f"License Valid: {result3.get('license_valid')}")
print(f"Session Conflict: {result3.get('session_conflict', False)}")

if not result3.get('license_valid') or result3.get('session_conflict'):
    print("✅ Second launcher CORRECTLY BLOCKED (bot is running)!")
else:
    print("❌ FAILED: Second launcher was NOT blocked even though bot is running!")
    print(f"Full response: {json.dumps(result3, indent=2)}")

# Wait for session timeout
print("\n[TEST 4] Waiting 6 seconds for bot session to expire...")
time.sleep(6)

# Simulate Third Launcher Login (after timeout)
print("\n[TEST 5] Second launcher tries again after bot closed")
fingerprint3 = fingerprint1.rsplit(':', 1)[0] + ":88888"  # Another different PID
print(f"Device Fingerprint: {fingerprint3}")

response3 = requests.post(API_URL, json={
    "license_key": LICENSE_KEY,
    "device_fingerprint": fingerprint3,
    "check_only": True
})
result3 = response3.json()
print(f"Response: {result3.get('message')}")
print(f"License Valid: {result3.get('license_valid')}")

if result3.get('license_valid'):
    print("✅ Third launcher can proceed after timeout expired")
else:
    print("❌ FAILED: Third launcher blocked even after timeout!")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
