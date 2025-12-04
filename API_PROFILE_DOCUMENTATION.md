# User Profile API Endpoint Documentation

## Overview
The `/api/profile` endpoint allows users to retrieve their own account information, trading statistics, and recent activity. This is a self-service endpoint that requires authentication via license key.

---

## Endpoint Details

**URL:** `/api/profile`  
**Method:** `GET`  
**Authentication:** Required (License Key)  
**Rate Limit:** 100 requests per minute per license key

---

## Authentication

The endpoint accepts license key authentication in two ways:

### Method 1: Query Parameter
```
GET /api/profile?license_key=YOUR-LICENSE-KEY
```

### Method 2: Authorization Header
```
GET /api/profile
Authorization: Bearer YOUR-LICENSE-KEY
```

---

## Response Format

### Success Response (200 OK)

```json
{
  "status": "success",
  "profile": {
    "account_id": "ACC123",
    "email": "us***@example.com",
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
    "current_device": "abc123...",
    "symbols_traded": ["ES", "NQ", "YM"]
  }
}
```

### Error Responses

#### 400 Bad Request - Missing License Key
```json
{
  "error": "License key required. Use ?license_key=KEY or Authorization: Bearer KEY"
}
```

#### 401 Unauthorized - Invalid License Key
```json
{
  "error": "Invalid license key"
}
```

#### 403 Forbidden - Account Suspended
```json
{
  "error": "Account suspended. Contact support."
}
```

#### 404 Not Found - User Not Found
```json
{
  "error": "User not found"
}
```

#### 429 Too Many Requests - Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded. Try again later."
}
```

#### 500 Internal Server Error - Database Error
```json
{
  "error": "Database connection failed"
}
```
or
```json
{
  "error": "Failed to retrieve profile data"
}
```

---

## Response Fields

### Profile Section

| Field | Type | Description |
|-------|------|-------------|
| `account_id` | string | Unique account identifier |
| `email` | string | Masked email address (e.g., "us***@domain.com") |
| `license_type` | string | License plan (e.g., "Monthly", "Annual") |
| `license_status` | string | Account status (e.g., "active", "suspended") |
| `license_expiration` | string (ISO 8601) | License expiration date/time |
| `days_until_expiration` | integer | Days remaining until license expires |
| `created_at` | string (ISO 8601) | Account creation date/time |
| `account_age_days` | integer | Number of days since account creation |
| `last_active` | string (ISO 8601) | Last API activity timestamp |
| `is_online` | boolean | True if bot sent heartbeat in last 2 minutes |

### Trading Stats Section

| Field | Type | Description |
|-------|------|-------------|
| `total_trades` | integer | Total number of trades executed |
| `total_pnl` | float | Cumulative profit/loss in dollars |
| `avg_pnl_per_trade` | float | Average PnL per trade |
| `winning_trades` | integer | Number of profitable trades |
| `losing_trades` | integer | Number of losing trades |
| `win_rate_percent` | float | Win rate as percentage (0-100) |
| `best_trade` | float | Largest profitable trade |
| `worst_trade` | float | Largest losing trade |

### Recent Activity Section

| Field | Type | Description |
|-------|------|-------------|
| `api_calls_today` | integer | Number of API calls made today |
| `api_calls_total` | integer | Total API calls since account creation |
| `last_heartbeat` | string (ISO 8601) | Last bot heartbeat timestamp |
| `current_device` | string | Partial device fingerprint (first 8 chars) |
| `symbols_traded` | array[string] | List of symbols traded (e.g., ["ES", "NQ"]) |

---

## Security Features

### Data Privacy
- **Email Masking:** Email addresses are masked (e.g., "user@domain.com" → "us***@domain.com")
- **Device Fingerprint:** Only first 8 characters shown
- **License Key:** Never returned in response
- **No Cross-User Access:** Users can only view their own data

### Rate Limiting
- **Limit:** 100 requests per minute per license key
- **Response:** 429 status code when exceeded
- **Logged:** Rate limit violations are logged for security monitoring

### Access Control
- **Authentication Required:** Valid license key must be provided
- **Suspended Accounts:** Return 403 Forbidden
- **Invalid Keys:** Return 401 Unauthorized

---

## Example Usage

### cURL Example (Query Parameter)
```bash
curl "https://quotrading-flask-api.azurewebsites.net/api/profile?license_key=YOUR-LICENSE-KEY"
```

### cURL Example (Authorization Header)
```bash
curl -H "Authorization: Bearer YOUR-LICENSE-KEY" \
     "https://quotrading-flask-api.azurewebsites.net/api/profile"
```

### Python Example
```python
import requests

license_key = "YOUR-LICENSE-KEY"
url = f"https://quotrading-flask-api.azurewebsites.net/api/profile?license_key={license_key}"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(f"Total Trades: {data['trading_stats']['total_trades']}")
    print(f"Total PnL: ${data['trading_stats']['total_pnl']:.2f}")
    print(f"Win Rate: {data['trading_stats']['win_rate_percent']:.2f}%")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

### JavaScript Example
```javascript
const licenseKey = 'YOUR-LICENSE-KEY';
const url = `https://quotrading-flask-api.azurewebsites.net/api/profile?license_key=${licenseKey}`;

fetch(url)
  .then(response => response.json())
  .then(data => {
    console.log('Total Trades:', data.trading_stats.total_trades);
    console.log('Total PnL:', data.trading_stats.total_pnl);
    console.log('Win Rate:', data.trading_stats.win_rate_percent + '%');
  })
  .catch(error => console.error('Error:', error));
```

---

## Common Use Cases

### 1. Check License Expiration
```python
response = requests.get(f"{api_url}/api/profile?license_key={key}")
data = response.json()
days_left = data['profile']['days_until_expiration']
if days_left < 7:
    print(f"⚠️ License expires in {days_left} days!")
```

### 2. Display Trading Statistics Dashboard
```python
response = requests.get(f"{api_url}/api/profile?license_key={key}")
data = response.json()
stats = data['trading_stats']

print(f"Trading Performance:")
print(f"  Total Trades: {stats['total_trades']}")
print(f"  Win Rate: {stats['win_rate_percent']:.2f}%")
print(f"  Total PnL: ${stats['total_pnl']:.2f}")
print(f"  Avg PnL: ${stats['avg_pnl_per_trade']:.2f}")
```

### 3. Check Online Status
```python
response = requests.get(f"{api_url}/api/profile?license_key={key}")
data = response.json()
is_online = data['profile']['is_online']
print(f"Bot Status: {'🟢 Online' if is_online else '🔴 Offline'}")
```

---

## Testing

A test script is available at `cloud-api/flask-api/test_profile_endpoint.py`:

```bash
python cloud-api/flask-api/test_profile_endpoint.py
```

This script tests:
- Profile retrieval with query parameter
- Profile retrieval with Authorization header
- Missing license key handling
- Invalid license key handling
- Response format validation

---

## Integration with Launcher

The launcher application can integrate this endpoint to display user information:

```python
# In QuoTrading_Launcher.py
import requests

def fetch_user_profile(license_key):
    """Fetch user profile from cloud API"""
    url = f"{CLOUD_API_BASE_URL}/api/profile?license_key={license_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        logging.error(f"Failed to fetch profile: {e}")
        return None

# Display in GUI
profile_data = fetch_user_profile(api_key)
if profile_data:
    stats = profile_data['trading_stats']
    self.stats_label.config(
        text=f"Total Trades: {stats['total_trades']} | "
             f"Win Rate: {stats['win_rate_percent']:.1f}% | "
             f"PnL: ${stats['total_pnl']:.2f}"
    )
```

---

## Performance Considerations

- **Database Queries:** 5 optimized queries per request
- **Response Time:** Typically < 200ms
- **Caching:** Not implemented (future enhancement)
- **Connection Pooling:** Uses PostgreSQL connection pool

---

## Future Enhancements

Potential improvements for future versions:

1. **Caching:** Cache profile data for 1-5 minutes to reduce database load
2. **More Statistics:** Add per-symbol breakdown, monthly/weekly stats
3. **Historical Data:** Provide time-series data for charting
4. **Customization:** Allow users to specify date ranges
5. **Export:** Add CSV/JSON export functionality
6. **WebSocket:** Real-time updates when trading

---

## Related Endpoints

- `/api/validate-license` - Validate license key
- `/api/heartbeat` - Send bot heartbeat
- `/api/rl/submit-outcome` - Submit trade outcome
- `/api/admin/user/<account_id>` - Admin view of user (requires admin key)

---

*Documentation last updated: December 4, 2025*
