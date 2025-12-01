# Session Locking Test Scenarios

This document outlines test scenarios to verify that session locking works correctly and prevents API key sharing.

## Overview

**Session Timeout**: 90 seconds (3 missed heartbeats)
- Heartbeats are sent every 30 seconds
- A session is considered "active" if last heartbeat < 90 seconds ago
- Stale sessions are automatically cleared before checking for conflicts

## Test Scenarios

### Scenario 1: Normal Single-Device Login
**Expected**: Login succeeds without any session conflict

**Steps**:
1. Start bot on Device A with valid license key
2. Observe login process

**Expected Result**:
- ✅ Bot validates license successfully
- ✅ No session conflict error
- ✅ Bot starts trading normally
- ✅ Heartbeats sent every 30 seconds

---

### Scenario 2: Same Device Restart (Immediate)
**Expected**: Login succeeds, previous session auto-cleared

**Steps**:
1. Start bot on Device A
2. Stop bot on Device A (Ctrl+C or crash)
3. Immediately restart bot on Device A (within 90 seconds)

**Expected Result**:
- ✅ Bot auto-clears the previous session from same device
- ✅ Login succeeds
- ✅ No error message shown to user
- ✅ Bot starts trading normally

---

### Scenario 3: Same Device Restart (After Timeout)
**Expected**: Login succeeds, stale session auto-cleared

**Steps**:
1. Start bot on Device A
2. Stop bot on Device A
3. Wait 95 seconds (longer than SESSION_TIMEOUT_SECONDS)
4. Restart bot on Device A

**Expected Result**:
- ✅ Stale session automatically cleared
- ✅ Login succeeds immediately
- ✅ No error message
- ✅ Bot starts trading normally

---

### Scenario 4: Two Devices - Active Conflict at Login
**Expected**: Second device blocked at login screen with clear error

**Steps**:
1. Start bot on Device A
2. Immediately try to start bot on Device B (same license key)
3. Device A is still running and sending heartbeats

**Expected Result**:
- ✅ Device A: Running normally, sending heartbeats
- ❌ Device B: Login BLOCKED with error message:
  ```
  ⚠️ LICENSE ALREADY IN USE
  Your license key is currently active on another device.
  Please stop the bot on the other device first.
  Contact: support@quotrading.com
  ```
- ✅ Device B: Bot exits, does NOT start
- ✅ Error appears at LOGIN SCREEN, not during runtime

---

### Scenario 5: Two Devices - Sequential Login (Proper Handoff)
**Expected**: Second device succeeds after first device stops

**Steps**:
1. Start bot on Device A
2. Stop bot on Device A (waits for cleanup, session released)
3. Wait 5 seconds
4. Start bot on Device B (same license key)

**Expected Result**:
- ✅ Device A: Shuts down cleanly, releases session
- ✅ Device B: Login succeeds (stale session auto-cleared if needed)
- ✅ Device B: Starts trading normally

---

### Scenario 6: Two Devices - Sequential Login (Device A Crashes)
**Expected**: Second device succeeds after timeout period

**Steps**:
1. Start bot on Device A
2. Force-kill bot on Device A (simulates crash, no cleanup)
3. Immediately try to start bot on Device B (same license key)
4. Wait for timeout and retry

**Expected Result**:
- ✅ Device B (first attempt): Login BLOCKED (Device A session still active)
- ✅ Wait 95 seconds (SESSION_TIMEOUT_SECONDS + buffer)
- ✅ Device B (retry): Login succeeds (stale session auto-cleared)
- ✅ Device B: Starts trading normally

---

### Scenario 7: Runtime Conflict Detection
**Expected**: Running bot detects if another device steals the session

**Steps**:
1. Start bot on Device A
2. Force-kill bot on Device A (no cleanup, session not released)
3. Wait 95 seconds for session to become stale
4. Start bot on Device B (same license key)
5. Bot on Device B starts successfully
6. Somehow Device A comes back online and tries to send heartbeat

**Expected Result**:
- ✅ Device B: Starts successfully after stale session cleared
- ✅ Device B: Sends heartbeats every 30 seconds
- ❌ Device A (if it tries to send heartbeat): Receives session conflict error
- ✅ Device A: Disconnects websocket, enters emergency stop mode
- ✅ Device A: Shows error message:
  ```
  ⚠️ LICENSE ALREADY IN USE
  Your license key is currently active on another device.
  Bot will remain ON but IDLE (no trading)
  ```

---

### Scenario 8: Heartbeat Continuity (No False Positives)
**Expected**: Normal operation with no false session conflicts

**Steps**:
1. Start bot on Device A
2. Let it run for 10 minutes (20 heartbeats)
3. Monitor for any session conflict errors

**Expected Result**:
- ✅ All heartbeats succeed
- ✅ No session conflict errors
- ✅ Bot trades normally throughout

---

## Testing Checklist

Before deploying to production, verify:

- [ ] Scenario 1: Normal single-device login works
- [ ] Scenario 2: Same device restart (immediate) works
- [ ] Scenario 3: Same device restart (after timeout) works
- [ ] Scenario 4: Two devices blocked at login (active conflict)
- [ ] Scenario 5: Sequential login (proper handoff) works
- [ ] Scenario 6: Sequential login (crash recovery) works
- [ ] Scenario 7: Runtime conflict detection works
- [ ] Scenario 8: No false positives during normal operation

## Key Behavioral Requirements

✅ **Session conflicts MUST be detected at LOGIN SCREEN**
- User should see the error before bot starts
- Bot should exit immediately, not proceed to runtime

✅ **Stale sessions MUST be automatically cleared**
- No manual intervention required
- Works at both `/api/main` and `/api/validate-license`

✅ **Consistent 90-second timeout across all endpoints**
- `/api/main`
- `/api/validate-license`
- `/api/heartbeat`
- `/api/session/clear`

✅ **Runtime conflicts handled gracefully**
- Bot disconnects from broker
- Enters emergency stop mode (idle)
- Does NOT crash or exit
- Shows clear error message

## Server Endpoints Behavior

### `/api/main`
- Auto-clears stale sessions (> 90 seconds old)
- Checks for active sessions (< 90 seconds)
- Returns 403 with `session_conflict: true` if another device active

### `/api/validate-license`
- Auto-clears stale sessions (> 90 seconds old)
- Checks for active sessions (< 90 seconds)
- Returns 403 with `session_conflict: true` if another device active

### `/api/heartbeat`
- Checks for active sessions (< 90 seconds)
- Returns 403 with `session_conflict: true` if another device active
- Updates heartbeat timestamp on success

### `/api/session/clear`
- Manually clears sessions older than 90 seconds
- Used by client retry logic (but auto-clear makes this redundant)

### `/api/session/release`
- Releases session when bot shuts down cleanly
- Called during cleanup_on_shutdown()
