# QuoTrading Cloud API - Azure Deployment Script (PowerShell)
$ErrorActionPreference = "Stop"

# Add Azure CLI to PATH
$env:PATH += ";C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin"

Write-Host "[INFO] Checking Azure login..." -ForegroundColor Green
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "[ERROR] Not logged in. Run: az login" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Using subscription: $($account.name)" -ForegroundColor Green

# Configuration
$RESOURCE_GROUP = "quotrading-rg"
$LOCATION = "eastus"
$APP_NAME = "quotrading-api-$(Get-Date -Format 'yyyyMMddHHmmss')"
$DB_SERVER_NAME = "quotrading-db-$(Get-Date -Format 'yyyyMMddHHmmss')"
$DB_NAME = "quotrading_db"
$DB_ADMIN_USER = "quotradingadmin"
$PLAN_NAME = "quotrading-plan"
$SKU = "B1"

Write-Host ""
Write-Host "[INFO] Deployment Configuration:" -ForegroundColor Green
Write-Host "  Resource Group: $RESOURCE_GROUP"
Write-Host "  Location: $LOCATION"
Write-Host "  App Name: $APP_NAME"
Write-Host "  Database Server: $DB_SERVER_NAME"
Write-Host "  SKU: $SKU"
Write-Host ""

# Prompt for database password
$DB_ADMIN_PASSWORD = Read-Host "Enter database admin password (min 8 chars, must include upper, lower, number)" -AsSecureString
$DB_ADMIN_PASSWORD_TEXT = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_ADMIN_PASSWORD)
)

if ($DB_ADMIN_PASSWORD_TEXT.Length -lt 8) {
    Write-Host "[ERROR] Password must be at least 8 characters" -ForegroundColor Red
    exit 1
}

# Prompt for Stripe keys
$STRIPE_SECRET_KEY = Read-Host "Enter Stripe Secret Key (or press Enter to set later)"
if ([string]::IsNullOrEmpty($STRIPE_SECRET_KEY)) { $STRIPE_SECRET_KEY = "sk_test_CHANGEME" }

$STRIPE_WEBHOOK_SECRET = Read-Host "Enter Stripe Webhook Secret (or press Enter to set later)"
if ([string]::IsNullOrEmpty($STRIPE_WEBHOOK_SECRET)) { $STRIPE_WEBHOOK_SECRET = "whsec_CHANGEME" }

# Generate API secret
$API_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

Write-Host ""
$confirm = Read-Host "Continue with deployment? (y/n)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "[INFO] Deployment cancelled" -ForegroundColor Yellow
    exit 0
}

# Step 1: Create Resource Group
Write-Host ""
Write-Host "[INFO] Step 1/8: Creating resource group..." -ForegroundColor Green
$rgExists = az group exists --name $RESOURCE_GROUP
if ($rgExists -eq 'true') {
    Write-Host "[WARNING] Resource group already exists, skipping" -ForegroundColor Yellow
} else {
    az group create --name $RESOURCE_GROUP --location $LOCATION --output none
    Write-Host "[INFO] ✓ Resource group created" -ForegroundColor Green
}

# Step 2: Create PostgreSQL Server  
Write-Host ""
Write-Host "[INFO] Step 2/8: Creating PostgreSQL server (5-10 minutes)..." -ForegroundColor Green
try {
    az postgres flexible-server create `
      --resource-group $RESOURCE_GROUP `
      --name $DB_SERVER_NAME `
      --location $LOCATION `
      --admin-user $DB_ADMIN_USER `
      --admin-password $DB_ADMIN_PASSWORD_TEXT `
      --sku-name Standard_B1ms `
      --tier Burstable `
      --version 14 `
      --storage-size 32 `
      --public-access 0.0.0.0 `
      --yes `
      --output none
    Write-Host "[INFO] ✓ PostgreSQL server created" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] PostgreSQL creation may have failed or already exists" -ForegroundColor Yellow
}

# Step 3: Create Database
Write-Host ""
Write-Host "[INFO] Step 3/8: Creating database..." -ForegroundColor Green
try {
    az postgres flexible-server db create `
      --resource-group $RESOURCE_GROUP `
      --server-name $DB_SERVER_NAME `
      --database-name $DB_NAME `
      --output none
    Write-Host "[INFO] ✓ Database created" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Database may already exist" -ForegroundColor Yellow
}

# Step 4: Configure Firewall
Write-Host ""
Write-Host "[INFO] Step 4/8: Configuring database firewall..." -ForegroundColor Green
az postgres flexible-server firewall-rule create `
  --resource-group $RESOURCE_GROUP `
  --name $DB_SERVER_NAME `
  --rule-name AllowAzureServices `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0 `
  --output none 2>$null
Write-Host "[INFO] ✓ Firewall configured" -ForegroundColor Green

# Build connection string
$DB_CONNECTION_STRING = "postgresql://${DB_ADMIN_USER}:${DB_ADMIN_PASSWORD_TEXT}@${DB_SERVER_NAME}.postgres.database.azure.com:5432/${DB_NAME}?sslmode=require"

# Step 5: Create App Service Plan
Write-Host ""
Write-Host "[INFO] Step 5/8: Creating App Service plan..." -ForegroundColor Green
$planExists = az appservice plan show --name $PLAN_NAME --resource-group $RESOURCE_GROUP 2>$null
if ($planExists) {
    Write-Host "[WARNING] App Service plan already exists, skipping" -ForegroundColor Yellow
} else {
    az appservice plan create `
      --resource-group $RESOURCE_GROUP `
      --name $PLAN_NAME `
      --location $LOCATION `
      --sku $SKU `
      --is-linux `
      --output none
    Write-Host "[INFO] ✓ App Service plan created" -ForegroundColor Green
}

# Step 6: Create Web App
Write-Host ""
Write-Host "[INFO] Step 6/8: Creating web app..." -ForegroundColor Green
az webapp create `
  --resource-group $RESOURCE_GROUP `
  --plan $PLAN_NAME `
  --name $APP_NAME `
  --runtime "PYTHON:3.11" `
  --output none
Write-Host "[INFO] ✓ Web app created" -ForegroundColor Green

# Step 7: Configure App Settings
Write-Host ""
Write-Host "[INFO] Step 7/8: Configuring application settings..." -ForegroundColor Green
az webapp config appsettings set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --settings `
    "DATABASE_URL=$DB_CONNECTION_STRING" `
    "STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY" `
    "STRIPE_WEBHOOK_SECRET=$STRIPE_WEBHOOK_SECRET" `
    "API_SECRET_KEY=$API_SECRET" `
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
    "WEBSITES_PORT=8000" `
  --output none
Write-Host "[INFO] ✓ Application settings configured" -ForegroundColor Green

# Step 8: Configure Startup Command
Write-Host ""
Write-Host "[INFO] Step 8/8: Configuring startup command..." -ForegroundColor Green
az webapp config set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --startup-file "gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000" `
  --output none
Write-Host "[INFO] ✓ Startup command configured" -ForegroundColor Green

# Enable HTTPS only
az webapp update `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --https-only true `
  --output none

# Get app URL
$APP_URL_JSON = az webapp show `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --query defaultHostName `
  --output json
$APP_URL = $APP_URL_JSON.Trim('"')

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Deployment Complete! 🎉" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your API will be available at: https://$APP_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Next steps:" -ForegroundColor Yellow
Write-Host "  1. Deploy your code:"
Write-Host "     cd cloud-api"
Write-Host "     az webapp up --resource-group $RESOURCE_GROUP --name $APP_NAME --runtime PYTHON:3.11"
Write-Host ""
Write-Host "  2. Test your API:"
Write-Host "     curl https://$APP_URL/"
Write-Host ""
Write-Host "[WARNING] Update Stripe webhook URL to: https://$APP_URL/api/v1/webhooks/stripe" -ForegroundColor Yellow
Write-Host ""

# Save deployment info
$deploymentInfo = @"
QuoTrading Azure Deployment Information
Generated: $(Get-Date)

Resource Group: $RESOURCE_GROUP
Location: $LOCATION
App Name: $APP_NAME
App URL: https://$APP_URL
Database Server: $DB_SERVER_NAME.postgres.database.azure.com
Database Name: $DB_NAME
Database User: $DB_ADMIN_USER

Stripe Webhook URL: https://$APP_URL/api/v1/webhooks/stripe

To update bot launcher, set:
QUOTRADING_API_URL=https://$APP_URL
"@

$deploymentInfo | Out-File -FilePath "deployment-info.txt" -Encoding UTF8
Write-Host "[INFO] Deployment info saved to deployment-info.txt" -ForegroundColor Green
Write-Host ""
