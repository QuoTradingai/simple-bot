# QuoTrading - Database & User Management Implementation

## What We Built

I've implemented a complete **Redis + PostgreSQL** user management system for QuoTrading Cloud API with full admin controls.

---

## 🎯 New Features

### 1. **PostgreSQL Database** 
- User accounts with license management
- Trade history tracking
- API usage logging
- Persistent storage (survives restarts)

### 2. **Redis Cache**
- Distributed rate limiting (works across server restarts)
- Session management
- High-performance caching
- Automatic fallback to in-memory if Redis unavailable

### 3. **User Management**
- Create/manage users via API
- License expiration tracking  
- Suspend/activate accounts
- Track user activity & trades

### 4. **Admin API Endpoints**
All require admin license key:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/admin/users` | GET | List all users |
| `/api/admin/user/{account_id}` | GET | Get specific user details |
| `/api/admin/add-user` | POST | Create new user |
| `/api/admin/extend-license/{account_id}` | PUT | Extend user license |
| `/api/admin/suspend-user/{account_id}` | PUT | Suspend user account |
| `/api/admin/activate-user/{account_id}` | PUT | Activate suspended user |
| `/api/admin/stats` | GET | System-wide statistics |

### 5. **Enhanced License Validation**
- Database-backed validation (real-time)
- Tracks last active timestamp
- Supports multiple license types: ADMIN, BETA, TRIAL, MONTHLY, ANNUAL
- Automatic expiration checking

---

## 📦 New Files Created

### Cloud API
1. **`cloud-api/database.py`** - Database models & connection management
   - User, APILog, TradeHistory models
   - Helper functions for user management
   - SQLAlchemy setup with PostgreSQL/SQLite support

2. **`cloud-api/redis_manager.py`** - Redis connection with fallback
   - Rate limiting (Redis-backed)
   - Key-value operations
   - Automatic in-memory fallback if Redis unavailable

3. **`cloud-api/init_database.py`** - Database initialization script
   - Creates all tables
   - Seeds admin user
   - Can create test users for beta

### Documentation
4. **`docs/AZURE_DATABASE_SETUP.md`** - Complete Azure setup guide
   - Step-by-step Azure PostgreSQL setup
   - Redis Cache creation
   - Environment variable configuration
   - Cost estimates & troubleshooting

### Testing
5. **`test_database_api.py`** - Comprehensive test suite
   - Tests all admin endpoints
   - User creation/validation
   - Rate limiting verification
   - 8 automated tests

---

## 🔄 Modified Files

### `cloud-api/signal_engine_v2.py`
- ✅ Integrated database & Redis managers
- ✅ Added admin endpoints (user management)
- ✅ Updated license validation to use database
- ✅ Redis-backed rate limiting (falls back to in-memory)
- ✅ Database initialization on startup

### `cloud-api/requirements-signal.txt`
Added dependencies:
```
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
alembic==1.13.1
```

---

## 🚀 How to Deploy

### Step 1: Create Azure Resources (~15 minutes)

**PostgreSQL Database:**
```powershell
az postgres flexible-server create `
  --name quotrading-db `
  --resource-group quotrading-rg `
  --location eastus `
  --admin-user quotadmin `
  --admin-password "YourSecurePassword123!" `
  --sku-name Standard_B1ms `
  --storage-size 32

az postgres flexible-server db create `
  --resource-group quotrading-rg `
  --server-name quotrading-db `
  --database-name quotrading
```

**Redis Cache:**
```powershell
az redis create `
  --name quotrading-redis `
  --resource-group quotrading-rg `
  --location eastus `
  --sku Basic `
  --vm-size c0
```

### Step 2: Get Connection Strings

**PostgreSQL:**
```
postgresql://quotadmin:PASSWORD@quotrading-db.postgres.database.azure.com/quotrading?sslmode=require
```

**Redis:**
```powershell
# Get primary key
az redis show-connection-string --name quotrading-redis --resource-group quotrading-rg
```

Format: `rediss://:PRIMARY_KEY@quotrading-redis.redis.cache.windows.net:6380/0`

### Step 3: Initialize Database Locally

```powershell
# Set environment variable
$env:DATABASE_URL = "postgresql://quotadmin:PASSWORD@quotrading-db.postgres.database.azure.com/quotrading?sslmode=require"

# Initialize database & create admin user
cd cloud-api
python init_database.py

# Output will show your ADMIN LICENSE KEY - SAVE IT!
# Example: QT-A1B2-C3D4-E5F6-G7H8
```

### Step 4: Configure Azure Container App

```powershell
az containerapp update `
  --name quotrading-signals `
  --resource-group quotrading-rg `
  --set-env-vars `
    "DATABASE_URL=postgresql://quotadmin:PASSWORD@quotrading-db.postgres.database.azure.com/quotrading?sslmode=require" `
    "REDIS_URL=rediss://:PRIMARY_KEY@quotrading-redis.redis.cache.windows.net:6380/0"
```

### Step 5: Build & Deploy

```powershell
# Build new Docker image
docker build -t quotradingsignals.azurecr.io/quotrading-signals:v11-database -f cloud-api/Dockerfile .

# Push to Azure Container Registry
az acr login --name quotradingsignals
docker push quotradingsignals.azurecr.io/quotrading-signals:v11-database

# Deploy to Azure
az containerapp update `
  --name quotrading-signals `
  --resource-group quotrading-rg `
  --image quotradingsignals.azurecr.io/quotrading-signals:v11-database
```

### Step 6: Test Deployment

```powershell
# Update test script with your admin key
# Edit test_database_api.py, line 14:
# ADMIN_LICENSE_KEY = "QT-A1B2-C3D4-E5F6-G7H8"  # Your actual key

# Run tests
python test_database_api.py
```

**Expected: 8/8 tests passing ✅**

---

## 💰 Costs

**Monthly Azure Costs:**
- PostgreSQL B1ms (Basic): ~$15/month
- Redis Cache C0 (Basic): ~$15/month
- **Total: ~$30/month**

**Free Alternative (Development):**
- Omit DATABASE_URL → Uses SQLite (local file)
- Omit REDIS_URL → Uses in-memory (resets on restart)
- **Cost: $0**

---

## 📊 Admin Usage Examples

### Get All Users
```powershell
$adminKey = "QT-XXXX-XXXX-XXXX-XXXX"
Invoke-RestMethod -Uri "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io/api/admin/users?license_key=$adminKey"
```

### Add New Beta User
```powershell
Invoke-RestMethod -Method POST -Uri "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io/api/admin/add-user" `
  -Body (@{
    license_key = $adminKey
    account_id = "USER001"
    email = "user@example.com"
    license_type = "BETA"
    license_duration_days = 90
    notes = "Beta tester from Discord"
  } | ConvertTo-Json) `
  -ContentType "application/json"
```

### Get System Stats
```powershell
Invoke-RestMethod -Uri "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io/api/admin/stats?license_key=$adminKey"
```

### Extend User License
```powershell
Invoke-RestMethod -Method PUT -Uri "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io/api/admin/extend-license/USER001?license_key=$adminKey&additional_days=30"
```

---

## 🔍 What You Can Track

### User Information
- ✅ Account ID, email, license type
- ✅ License status (ACTIVE, EXPIRED, SUSPENDED)
- ✅ License expiration date
- ✅ Last active timestamp
- ✅ Created date
- ✅ Admin privileges

### Activity Tracking
- ✅ API calls per user
- ✅ Endpoint usage patterns
- ✅ Response times
- ✅ IP addresses
- ✅ User agents

### Trading Stats (per user)
- ✅ Total trades executed
- ✅ Win/loss record
- ✅ Total P&L
- ✅ Average P&L per trade
- ✅ Entry/exit prices
- ✅ Signal confidence scores

### System-Wide Stats
- ✅ Total users (active vs suspended)
- ✅ License type breakdown
- ✅ API calls (last 24 hours)
- ✅ Total trades across all users
- ✅ Collective P&L

---

## 🎯 Next Steps

### Immediate (After Deployment)
1. ✅ Save admin license key securely
2. ✅ Run test suite (verify 8/8 passing)
3. ✅ Create 2-3 beta test users
4. ✅ Test license validation in launcher GUI

### Short Term (Next Week)
- 📧 Email notifications (license activation/expiration)
- 💳 Stripe payment integration (auto-create users)
- 📊 Simple web dashboard (view stats in browser)
- 🔔 Webhook for trade submissions

### Long Term (Scaling)
- 🗄️ Database backups (Azure automated backups)
- 📈 Analytics dashboard (Grafana/Metabase)
- 🌐 Multi-region deployment
- 🔐 OAuth2 authentication
- 📱 Mobile app integration

---

## 🛠️ Troubleshooting

### Database Connection Fails
```powershell
# Check firewall rules
az postgres flexible-server firewall-rule create `
  --resource-group quotrading-rg `
  --name quotrading-db `
  --rule-name AllowAll `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 255.255.255.255
```

### Redis Connection Timeout
```powershell
# Check Redis status
az redis show --name quotrading-redis --resource-group quotrading-rg --query "provisioningState"
```

### Admin Endpoints Return 403
- ❌ Wrong license key → Check key from init_database.py output
- ❌ Not admin user → Verify `is_admin=True` in database
- ❌ License expired → Check `license_expiration` field

### Rate Limiting Not Working
- ✅ Automatically falls back to in-memory if Redis unavailable
- ✅ Check `/api/rate-limit/status` endpoint
- ✅ Verify REDIS_URL environment variable

---

## 📚 Documentation

- **Full Azure Setup:** `docs/AZURE_DATABASE_SETUP.md`
- **Database Schema:** `cloud-api/database.py` (models at top)
- **API Endpoints:** `cloud-api/signal_engine_v2.py` (admin section ~line 170)
- **Test Suite:** `test_database_api.py`

---

## ✅ Success Checklist

After deployment, verify:

- [ ] PostgreSQL database created on Azure
- [ ] Redis cache created on Azure
- [ ] Database tables initialized (`init_database.py` run successfully)
- [ ] Admin user created (license key saved)
- [ ] Environment variables set in Container App
- [ ] Docker image built with new dependencies
- [ ] Deployed to Azure Container Apps
- [ ] Health endpoint returns 200
- [ ] Admin stats endpoint works (with admin key)
- [ ] Can create new users via API
- [ ] License validation works for new users
- [ ] Rate limiting still operational
- [ ] Calendar endpoints still working
- [ ] All 8 tests passing in `test_database_api.py`

---

**Ready to deploy? Follow the steps above and you'll have a production-ready user management system!** 🚀
