# User Profile System Audit Report

**Date:** December 4, 2025  
**Auditor:** GitHub Copilot Coding Agent  
**Repository:** QuoTradingai/simple-bot  
**Purpose:** Comprehensive audit of user profile functionality

---

## Executive Summary

This audit examines the current state of user profile functionality in the QuoTrading AI system. The system currently has **NO user-facing profile endpoint** - only admin endpoints exist for viewing user information.

### Key Findings:
- ✅ **Database Schema:** Well-designed with comprehensive user information storage
- ⚠️ **API Endpoints:** No user-facing profile endpoint exists
- ✅ **Admin Endpoints:** Comprehensive admin-only user management endpoints exist
- ⚠️ **User Access:** Users cannot view their own profile, statistics, or account information
- ✅ **Security:** Current admin endpoints properly secured with API key authentication

---

## 1. Current Database Schema

### 1.1 Users Table Structure
Located in: `cloud-api/init_complete_db.py`

The `users` table stores the following information:

```sql
CREATE TABLE users (
    account_id VARCHAR(100) PRIMARY KEY,
    license_key VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    whop_user_id VARCHAR(100),
    whop_membership_id VARCHAR(100),
    license_type VARCHAR(50) NOT NULL DEFAULT 'Monthly',
    license_status VARCHAR(20) NOT NULL DEFAULT 'active',
    license_expiration TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_heartbeat TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    device_fingerprint VARCHAR(255)  -- Added via migration
)
```

**Indexes:**
- `idx_users_license_key` - License key lookup
- `idx_users_email` - Email lookup
- `idx_users_status` - Status filtering
- `idx_users_expiration` - Expiration date queries
- `idx_users_device_fingerprint` - Session locking
- `idx_users_last_heartbeat` - Online status

### 1.2 Related Tables

**RL Experiences Table:**
Stores trading history and machine learning data
- Total trades per user
- PnL statistics
- Win/loss ratios
- Trade outcomes

**API Logs Table:**
Stores API interaction history
- API call count
- Last active timestamp
- Endpoint usage patterns

**Heartbeats Table:**
Stores real-time bot status
- Online/offline status
- Bot version information
- Session activity

---

## 2. Current API Endpoints

### 2.1 User-Facing Endpoints (Non-Admin)

**Available Endpoints:**
1. `/api/hello` - Health check (GET)
2. `/api/validate-license` - License validation (POST)
3. `/api/heartbeat` - Bot heartbeat (POST)
4. `/api/session/release` - Release session (POST)
5. `/api/session/clear` - Clear session (POST)
6. `/api/main` - Main validation (POST) - Used by launcher
7. `/api/rl/submit-outcome` - Submit trade outcome (POST)
8. `/api/health` - System health (GET)

**❌ MISSING:** No `/api/profile` or `/api/user/me` endpoint exists!

Users currently have **NO WAY** to:
- View their own account information
- Check license expiration date
- See total trades executed
- Review PnL statistics
- Check win/loss ratio
- View account creation date
- See last active timestamp

### 2.2 Admin-Only Endpoints

**User Management Endpoints:**
1. `/api/admin/users` - List all users (GET)
2. `/api/admin/user/<account_id>` - Get user details (GET)
3. `/api/admin/online-users` - Get online users (GET)
4. `/api/admin/suspend-user/<account_id>` - Suspend user (POST/PUT)
5. `/api/admin/activate-user/<account_id>` - Activate user (POST/PUT)
6. `/api/admin/delete-user/<account_id>` - Delete user (DELETE)
7. `/api/admin/add-user` - Add new user (POST)
8. `/api/admin/extend-license/<account_id>` - Extend license (POST/PUT)

**Admin User Detail Response (Example):**
```json
{
  "user": {
    "account_id": "ACC123",
    "email": "user@example.com",
    "license_key": "LIC-KEY-123",
    "license_type": "Monthly",
    "license_status": "active",
    "license_expiration": "2025-12-31T23:59:59",
    "created_at": "2025-01-01T00:00:00",
    "last_active": "2025-12-04T20:00:00"
  },
  "recent_api_calls": 1234,
  "trade_stats": {
    "total_trades": 150,
    "total_pnl": 5420.50,
    "avg_pnl": 36.14,
    "winning_trades": 95
  }
}
```

**Security:**
- All admin endpoints require `ADMIN_API_KEY`
- Admin key passed via query parameter or header
- Returns 401 Unauthorized if key missing/invalid

---

## 3. Current User Experience Gaps

### 3.1 What Users Cannot Do

**Account Information:**
- ❌ Cannot view their own email address
- ❌ Cannot check license expiration date
- ❌ Cannot see account creation date
- ❌ Cannot see last login/active time
- ❌ Cannot view license type (Monthly/Annual)
- ❌ Cannot check license status (active/suspended)

**Trading Statistics:**
- ❌ Cannot see total number of trades
- ❌ Cannot view cumulative PnL
- ❌ Cannot check average PnL per trade
- ❌ Cannot see win rate percentage
- ❌ Cannot review recent trading activity
- ❌ Cannot see API call usage

**Session Information:**
- ❌ Cannot see current device fingerprint
- ❌ Cannot view active sessions
- ❌ Cannot see last heartbeat timestamp

### 3.2 Current Workarounds

Users currently rely on:
1. **Email notifications** from Whop for license expiration
2. **Local bot logs** for trading statistics
3. **Broker statements** for PnL tracking
4. **Admin support** for account information

This creates unnecessary support burden and poor user experience.

---

## 4. Proposed Solution: User Profile Endpoint

### 4.1 Recommended Endpoint Design

**Endpoint:** `GET /api/profile`

**Authentication:** 
- License key via query parameter or header
- `?license_key=LIC-KEY-123` or `Authorization: Bearer LIC-KEY-123`

**Response Schema:**
```json
{
  "status": "success",
  "profile": {
    "account_id": "ACC123",
    "email": "us***@example.com",  // Masked for security
    "license_type": "Monthly",
    "license_status": "active",
    "license_expiration": "2025-12-31T23:59:59",
    "days_until_expiration": 27,
    "created_at": "2025-01-01T00:00:00",
    "account_age_days": 337,
    "last_active": "2025-12-04T20:00:00",
    "is_online": true
  },
  "trading_stats": {
    "total_trades": 150,
    "total_pnl": 5420.50,
    "avg_pnl_per_trade": 36.14,
    "winning_trades": 95,
    "losing_trades": 55,
    "win_rate_percent": 63.33,
    "best_trade": 250.00,
    "worst_trade": -180.00
  },
  "recent_activity": {
    "api_calls_today": 45,
    "api_calls_total": 1234,
    "last_heartbeat": "2025-12-04T20:30:00",
    "current_device": "abc123...",  // Fingerprint (partial)
    "symbols_traded": ["ES", "NQ", "YM"]
  }
}
```

### 4.2 Implementation Requirements

**File to Modify:** `cloud-api/flask-api/app.py`

**Code Location:** After line ~3175 (after `/api/rl/submit-outcome`)

**Required Features:**
1. ✅ License key validation
2. ✅ Rate limiting (use existing `check_rate_limit()`)
3. ✅ Email masking (use existing `mask_email()`)
4. ✅ Sensitive data protection
5. ✅ Database query optimization
6. ✅ Error handling
7. ✅ Logging with masked data

**Database Queries Needed:**
```python
# 1. Get user details
SELECT u.account_id, u.email, u.license_type, u.license_status,
       u.license_expiration, u.created_at, u.last_heartbeat,
       u.device_fingerprint
FROM users u
WHERE u.license_key = %s

# 2. Get trading statistics
SELECT 
    COUNT(*) as total_trades,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl,
    COUNT(*) FILTER (WHERE pnl > 0) as winning_trades,
    COUNT(*) FILTER (WHERE pnl < 0) as losing_trades,
    MAX(pnl) as best_trade,
    MIN(pnl) as worst_trade
FROM rl_experiences
WHERE license_key = %s AND took_trade = TRUE

# 3. Get recent activity
SELECT COUNT(*) as api_calls_total
FROM api_logs
WHERE license_key = %s

# 4. Get today's API calls
SELECT COUNT(*) as api_calls_today
FROM api_logs
WHERE license_key = %s 
  AND created_at >= CURRENT_DATE

# 5. Get symbols traded
SELECT DISTINCT symbol
FROM rl_experiences
WHERE license_key = %s AND took_trade = TRUE
ORDER BY symbol
```

### 4.3 Security Considerations

**Data Protection:**
- ✅ Mask email addresses (show `us***@domain.com`)
- ✅ Show partial device fingerprint only (first 8 chars)
- ✅ Don't expose full license key in response
- ✅ Rate limit to prevent abuse (max 60 calls/minute)
- ✅ Log access with masked data

**Access Control:**
- ✅ Users can only access their own profile
- ✅ No cross-user data leakage
- ✅ Validate license key before returning data
- ✅ Return 403 if license is suspended
- ✅ Return 401 if license key is invalid

**Privacy:**
- ❌ Don't expose other users' information
- ❌ Don't show internal IDs or admin fields
- ❌ Don't reveal Whop membership details
- ❌ Don't expose metadata JSONB field

---

## 5. Testing Requirements

### 5.1 Unit Tests Needed

**Test File:** `cloud-api/flask-api/test_profile_endpoint.py`

**Test Cases:**
1. ✅ Valid license key returns profile data
2. ✅ Invalid license key returns 401
3. ✅ Suspended license returns 403
4. ✅ Expired license returns appropriate warning
5. ✅ Email is properly masked
6. ✅ Device fingerprint is partial only
7. ✅ Trading stats calculate correctly
8. ✅ Rate limiting works (61st request fails)
9. ✅ Database connection failure handled gracefully
10. ✅ Missing license key returns 400

### 5.2 Integration Tests

**Scenarios:**
1. User with no trades sees zero statistics
2. User with 100 trades sees accurate PnL
3. User online within 2 minutes shows `is_online: true`
4. User offline shows `is_online: false`
5. Multiple symbols traded shown in array

---

## 6. Benefits of Adding Profile Endpoint

### 6.1 User Benefits
- ✅ **Self-Service:** Users can check account status without admin support
- ✅ **Transparency:** Clear view of license expiration and status
- ✅ **Performance Tracking:** See trading statistics in real-time
- ✅ **Engagement:** Users can track their progress
- ✅ **Onboarding:** New users can verify account setup

### 6.2 Business Benefits
- ✅ **Reduced Support Load:** Fewer "when does my license expire?" tickets
- ✅ **Increased Retention:** Users engaged with their statistics stay longer
- ✅ **Better UX:** Professional self-service capability
- ✅ **Data-Driven Users:** Users can optimize based on their stats
- ✅ **Dashboard Foundation:** Enable future web dashboard

### 6.3 Technical Benefits
- ✅ **API Completeness:** Standard REST API practice
- ✅ **Reusability:** Launcher/web frontend can use same endpoint
- ✅ **Scalability:** Reduces admin endpoint load
- ✅ **Logging:** Better audit trail of user self-service

---

## 7. Alternative Approaches Considered

### 7.1 Option A: Keep Admin-Only (Current State)
**Pros:** Simple, no new code  
**Cons:** Poor UX, high support burden, not industry standard

### 7.2 Option B: Add User Profile Endpoint (RECOMMENDED)
**Pros:** Industry standard, better UX, self-service  
**Cons:** Requires new endpoint implementation (~200 lines)

### 7.3 Option C: Build Web Dashboard
**Pros:** Rich UI, advanced features  
**Cons:** Major development effort, requires React/Vue frontend

**Recommendation:** Implement **Option B** as foundation for Option C later.

---

## 8. Implementation Checklist

- [ ] Add `/api/profile` endpoint to `app.py`
- [ ] Implement license key validation
- [ ] Add rate limiting (60 req/min)
- [ ] Mask sensitive data (email, device fingerprint)
- [ ] Query user details from database
- [ ] Query trading statistics
- [ ] Query recent activity
- [ ] Calculate derived fields (days until expiration, win rate)
- [ ] Add error handling
- [ ] Add logging with masked data
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Update API documentation
- [ ] Add to health check endpoint list

---

## 9. Current State Summary

### What Exists ✅
- Well-designed database schema with comprehensive user data
- Admin endpoints for user management
- Security infrastructure (API keys, rate limiting)
- Data masking utilities for logs
- Trading statistics tracking in RL experiences

### What's Missing ❌
- User-facing profile endpoint
- Self-service account information access
- User-accessible trading statistics
- Public API documentation
- User profile tests

### Priority Assessment
**Priority:** **HIGH** ⚡

**Rationale:**
- Industry standard feature (every SaaS has user profiles)
- Low implementation effort (~2-3 hours)
- High user value (self-service)
- Reduces support burden
- Foundation for future web dashboard

---

## 10. Conclusion

The QuoTrading AI system has **excellent infrastructure** for user management but lacks a **user-facing profile endpoint**. This creates an incomplete user experience and unnecessary support burden.

**Recommendation:** Implement `/api/profile` endpoint following the design in Section 4.

**Estimated Effort:** 2-3 hours (implementation + testing)

**Expected Impact:**
- 📈 User satisfaction improvement
- 📉 Support ticket reduction (~20-30%)
- ✅ Industry-standard API completeness
- 🚀 Foundation for web dashboard

---

## Appendix A: Example Implementation

```python
@app.route('/api/profile', methods=['GET'])
def get_user_profile():
    """
    Get user profile information (self-service)
    Users can view their own account details and trading statistics
    """
    # Get license key from query or header
    license_key = request.args.get('license_key') or \
                  request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not license_key:
        return jsonify({"error": "License key required"}), 400
    
    # Rate limiting
    allowed, rate_msg = check_rate_limit(license_key, '/api/profile')
    if not allowed:
        return jsonify({"error": rate_msg}), 429
    
    # Validate license
    valid, user_data = validate_license(license_key)
    if not valid:
        return jsonify({"error": "Invalid license key"}), 401
    
    if user_data.get('license_status', '').upper() == 'SUSPENDED':
        return jsonify({"error": "Account suspended"}), 403
    
    # Implementation continues...
```

---

*Audit completed by GitHub Copilot Coding Agent*  
*Report generated: December 4, 2025*
