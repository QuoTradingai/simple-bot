# QuoTrading Cloud API - Azure Deployment (West US)
$ErrorActionPreference = "Stop"
$env:PATH += ";C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin"

Write-Host "[INFO] Trying West US region (different quota pool)..." -ForegroundColor Green

$RESOURCE_GROUP = "quotrading-rg"
$LOCATION = "westus"  # Changed from eastus
$APP_NAME = "quotrading-api-$(Get-Date -Format 'yyyyMMddHHmmss')"
$PLAN_NAME = "quotrading-plan-westus"
$SKU = "B1"

Write-Host "[INFO] Creating App Service Plan in West US..." -ForegroundColor Green
az appservice plan create `
  --resource-group $RESOURCE_GROUP `
  --name $PLAN_NAME `
  --location $LOCATION `
  --sku $SKU `
  --is-linux `
  --output table

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] West US works! Continuing deployment..." -ForegroundColor Green
} else {
    Write-Host "[FAILED] Same quota issue in West US" -ForegroundColor Red
    exit 1
}
