# Azure Deployment Guide - QuoTrading Signal API
# Run these commands in PowerShell one at a time

# ============================================
# STEP 1: Check if Azure CLI is installed
# ============================================
az --version
# If this fails, install from: https://aka.ms/installazurecliwindows

# ============================================
# STEP 2: Login to Azure
# ============================================
az login
# This will open browser - login with your Azure account

# ============================================
# STEP 3: Set variables (CUSTOMIZE THESE)
# ============================================
$RESOURCE_GROUP = "quotrading-rg"
$APP_NAME = "quotrading-signals"  # Must be globally unique
$LOCATION = "eastus"  # or "westus2", "centralus" (close to you)
$PLAN_NAME = "quotrading-plan"
$RUNTIME = "PYTHON|3.11"

# ============================================
# STEP 4: Create Resource Group
# ============================================
az group create --name $RESOURCE_GROUP --location $LOCATION

# ============================================
# STEP 5: Create App Service Plan (Free tier)
# ============================================
az appservice plan create `
  --name $PLAN_NAME `
  --resource-group $RESOURCE_GROUP `
  --sku F1 `
  --is-linux

# ============================================
# STEP 6: Create Web App
# ============================================
az webapp create `
  --resource-group $RESOURCE_GROUP `
  --plan $PLAN_NAME `
  --name $APP_NAME `
  --runtime $RUNTIME `
  --deployment-local-git

# ============================================
# STEP 7: Configure Environment Variables
# ============================================
az webapp config appsettings set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --settings `
    DATABASE_URL="postgresql://quotrading_db_user:neSCC1nv8xSKcTRW24CMSygdmvoVTvys@dpg-d47h2hi4d50c7385trl0-a.oregon-postgres.render.com/quotrading_db" `
    STRIPE_SECRET_KEY="your_stripe_key_here" `
    API_SECRET_KEY="change-this-in-production"

# ============================================
# STEP 8: Configure Deployment from GitHub
# ============================================
az webapp deployment source config `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --repo-url https://github.com/Quotraders/simple-bot `
  --branch main `
  --manual-integration

# ============================================
# STEP 9: Set startup command
# ============================================
az webapp config set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker cloud-api.main:app"

# ============================================
# STEP 10: Get App URL
# ============================================
az webapp show `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --query defaultHostName `
  --output tsv

# Your API will be at: https://$APP_NAME.azurewebsites.net

# ============================================
# STEP 11: View logs (if needed)
# ============================================
az webapp log tail `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME

# ============================================
# TROUBLESHOOTING
# ============================================
# Check deployment status:
# az webapp deployment list-publishing-profiles --name $APP_NAME --resource-group $RESOURCE_GROUP

# Restart app:
# az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

# Check app settings:
# az webapp config appsettings list --name $APP_NAME --resource-group $RESOURCE_GROUP
