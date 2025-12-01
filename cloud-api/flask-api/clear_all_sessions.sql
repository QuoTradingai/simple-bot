-- Clear all existing sessions to migrate from PID-based to machine-based fingerprints
-- Run this once after deploying the new fingerprint logic

UPDATE users 
SET device_fingerprint = NULL,
    last_heartbeat = NULL
WHERE device_fingerprint IS NOT NULL;

-- This allows all users to log in with the new fingerprint format (without PID)
