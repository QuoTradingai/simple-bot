# Azure Setup Guide - Redis + Database for QuoTrading

## Overview
This guide walks you through setting up Redis and PostgreSQL on Azure for the QuoTrading Cloud API.

**Estimated Setup Time:** 15-20 minutes  
**Estimated Monthly Cost:** $20-40 (Basic tier for both services)

---

## Prerequisites

✅ Azure CLI installed and logged in  
✅ QuoTrading resource group (`quotrading-rg`)  
✅ Location: `eastus` (or your preferred region)

---

## Step 1: Create Azure Database for PostgreSQL

### 1.1 Create PostgreSQL Server

```powershell
# Create PostgreSQL Flexible Server
az postgres flexible-server create `
  --name quotrading-db `
  --resource-group quotrading-rg `
  --location eastus `
  --admin-user quotadmin `
  --admin-password "YourSecurePassword123!" `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --storage-size 32 `
  --version 15 `
  --public-access 0.0.0.0-255.255.255.255
```

**Parameters explained:**
- `--name`: Unique server name (must be globally unique)
- `--admin-password`: **CHANGE THIS** to a secure password (save it!)
- `--sku-name`: B1ms = Basic tier, 1 vCore, 2GB RAM (~$15/month)
- `--storage-size`: 32 GB storage
- `--public-access`: Allow all IPs (can restrict later)

**Expected output:**
```json
{
  "fullyQualifiedDomainName": "quotrading-db.postgres.database.azure.com",
  "id": "...",
  "name": "quotrading-db",
  "state": "Ready"
}
```

### 1.2 Create Database

```powershell
# Create the actual database
az postgres flexible-server db create `
  --resource-group quotrading-rg `
  --server-name quotrading-db `
  --database-name quotrading
```

### 1.3 Get Connection String

```powershell
# Show connection info
az postgres flexible-server show-connection-string `
  --server-name quotrading-db `
  --admin-user quotadmin `
  --admin-password "YourSecurePassword123!" `
  --database-name quotrading
```

**Copy the PostgreSQL connection string - you'll need it later:**
```
postgresql://quotadmin:YourSecurePassword123!@quotrading-db.postgres.database.azure.com/quotrading?sslmode=require
```

---

## Step 2: Create Azure Cache for Redis

### 2.1 Create Redis Cache

```powershell
# Create Redis Cache (Basic tier)
az redis create `
  --name quotrading-redis `
  --resource-group quotrading-rg `
  --location eastus `
  --sku Basic `
  --vm-size c0 `
  --enable-non-ssl-port false
```

**Parameters explained:**
- `--name`: Unique Redis cache name
- `--sku`: Basic = No replication (~$15/month)
- `--vm-size`: c0 = 250MB cache (sufficient for rate limiting)

**This takes ~10-15 minutes to provision. You'll see:**
```
Running... (takes 10-15 minutes)
```

### 2.2 Get Redis Connection Info

```powershell
# Get Redis host and primary key
az redis show `
  --name quotrading-redis `
  --resource-group quotrading-rg `
  --query "{hostName:hostName, sslPort:sslPort, primaryKey:accessKeys.primaryKey}"
```

**Expected output:**
```json
{
  "hostName": "quotrading-redis.redis.cache.windows.net",
  "sslPort": 6380,
  "primaryKey": "very-long-key-here..."
}
```

**Build your Redis connection string:**
```
rediss://:YOUR_PRIMARY_KEY@quotrading-redis.redis.cache.windows.net:6380/0
```

Replace `YOUR_PRIMARY_KEY` with the actual primary key from above.

---

## Step 3: Initialize Database (Local Testing)

### 3.1 Test Connection Locally

```powershell
# Set environment variable for local testing
$env:DATABASE_URL = "postgresql://quotadmin:YourSecurePassword123!@quotrading-db.postgres.database.azure.com/quotrading?sslmode=require"

# Run initialization script
cd cloud-api
python init_database.py
```

**Expected output:**
```
============================================================
QuoTrading Database Initialization
============================================================

📊 Database: postgresql://quotadmin:***@quotrading-db.postgres.database.azure.com/quotrading

🔨 Creating database tables...
✅ Database tables created successfully

👤 Creating admin user...
✅ Admin user created successfully!
   Account ID: ADMIN
   License Key: QT-XXXX-XXXX-XXXX-XXXX
   Email: admin@quotrading.com

   🔑 Save this license key - you'll need it for admin API access!
```

**🔑 SAVE THE ADMIN LICENSE KEY!** You'll use this to access admin endpoints.

### 3.2 Create Test Users (Optional)

```powershell
# Create 3 test users for beta testing
python init_database.py --test-users 3
```

---

## Step 4: Configure Azure Container App

### 4.1 Add Environment Variables

```powershell
# Add DATABASE_URL to Container App
az containerapp update `
  --name quotrading-signals `
  --resource-group quotrading-rg `
  --set-env-vars `
    "DATABASE_URL=postgresql://quotadmin:YourSecurePassword123!@quotrading-db.postgres.database.azure.com/quotrading?sslmode=require" `
    "REDIS_URL=rediss://:YOUR_PRIMARY_KEY@quotrading-redis.redis.cache.windows.net:6380/0"
```

**Replace:**
- `YourSecurePassword123!` with your actual database password
- `YOUR_PRIMARY_KEY` with your actual Redis primary key

### 4.2 Verify Environment Variables

```powershell
# Check that variables are set
az containerapp show `
  --name quotrading-signals `
  --resource-group quotrading-rg `
  --query "properties.template.containers[0].env"
```

---

## Step 5: Deploy Updated Code

### 5.1 Build New Docker Image

```powershell
# From project root (simple-bot-1)
cd c:\Users\kevin\Downloads\simple-bot-1

# Build with new dependencies
docker build -t quotradingsignals.azurecr.io/quotrading-signals:v11-database -f cloud-api/Dockerfile .
```

### 5.2 Push to Azure Container Registry

```powershell
# Login to ACR
az acr login --name quotradingsignals

# Push image
docker push quotradingsignals.azurecr.io/quotrading-signals:v11-database
```

### 5.3 Deploy to Container Apps

```powershell
# Update container app with new image
az containerapp update `
  --name quotrading-signals `
  --resource-group quotrading-rg `
  --image quotradingsignals.azurecr.io/quotrading-signals:v11-database
```

**Wait ~30-60 seconds for deployment...**

---

## Step 6: Verify Deployment

### 6.1 Test Health Endpoint

```powershell
# Check API is running
Invoke-WebRequest -Uri "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io/health" | Select-Object StatusCode, Content
```

**Expected:** `StatusCode: 200`

### 6.2 Test Admin Endpoints

```powershell
# Get all users (use your admin license key)
$adminKey = "QT-XXXX-XXXX-XXXX-XXXX"  # Replace with your actual admin key
Invoke-RestMethod -Uri "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io/api/admin/users?license_key=$adminKey"
```

**Expected:** JSON array with user list including ADMIN

### 6.3 Test License Validation

```powershell
# Validate admin license
Invoke-RestMethod -Uri "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io/api/license/validate?license_key=$adminKey"
```

**Expected:**
```json
{
  "valid": true,
  "license_type": "ADMIN",
  "account_id": "ADMIN",
  "message": "License is valid"
}
```

---

## What You Just Built

✅ **PostgreSQL Database** - Stores users, licenses, trades  
✅ **Redis Cache** - Handles rate limiting across restarts  
✅ **Admin Account** - Full access to manage users  
✅ **User Management** - Add/remove/extend licenses via API  
✅ **Activity Tracking** - See who's using the API  
✅ **Trade History** - Store user performance data  

---

## Quick Reference - Connection Strings

### PostgreSQL
```
postgresql://quotadmin:PASSWORD@quotrading-db.postgres.database.azure.com/quotrading?sslmode=require
```

### Redis
```
rediss://:PRIMARY_KEY@quotrading-redis.redis.cache.windows.net:6380/0
```

---

## Troubleshooting

### Can't Connect to Database

**Error:** `connection refused` or `timeout`

**Fix:**
```powershell
# Check firewall rules
az postgres flexible-server firewall-rule list `
  --resource-group quotrading-rg `
  --name quotrading-db

# Add your IP if missing
az postgres flexible-server firewall-rule create `
  --resource-group quotrading-rg `
  --name quotrading-db `
  --rule-name AllowAll `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 255.255.255.255
```

### Redis Connection Timeout

**Error:** `Redis connection failed`

**Fix:**
```powershell
# Check Redis status
az redis show --name quotrading-redis --resource-group quotrading-rg --query "provisioningState"

# Should show "Succeeded"
```

### Environment Variables Not Set

**Error:** `DATABASE_URL not found`

**Fix:**
```powershell
# Re-add environment variables
az containerapp update `
  --name quotrading-signals `
  --resource-group quotrading-rg `
  --set-env-vars `
    "DATABASE_URL=your-connection-string" `
    "REDIS_URL=your-redis-string"
```

---

## Next Steps

1. **Test the system** with admin API endpoints
2. **Create beta users** with `init_database.py --test-users N`
3. **Monitor Azure costs** in the portal
4. **Add your first customer** through admin API
5. **Track usage** with admin stats endpoints

---

## Cost Optimization

**Current setup (~$30/month):**
- PostgreSQL B1ms: ~$15/month
- Redis Basic C0: ~$15/month

**To reduce costs (development):**
- Use SQLite locally (free) - just omit DATABASE_URL
- Skip Redis (use in-memory fallback) - omit REDIS_URL
- Only deploy to Azure when testing production features

**To scale up (100+ users):**
- PostgreSQL GP_Standard_D2s_v3: ~$200/month (2 vCores, 8GB RAM)
- Redis Standard C1: ~$75/month (1GB cache with replication)

---

Ready to proceed? Run the commands in order and let me know if you hit any issues!
