# Deploy QuoTrading Cloud API to Azure Container Apps
# This script builds and deploys the updated API with ml_experiences support

param(
    [string]$ResourceGroup = "quotrading-rg",
    [string]$ContainerAppName = "quotrading-signals",
    [string]$Location = "eastus"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYING QUOTRADING CLOUD API TO AZURE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if logged in to Azure
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
$loginStatus = az account show 2>$null
if (-not $loginStatus) {
    Write-Host "Not logged in to Azure. Logging in..." -ForegroundColor Yellow
    az login
}

$account = az account show | ConvertFrom-Json
Write-Host "✅ Logged in as: $($account.user.name)" -ForegroundColor Green
Write-Host "   Subscription: $($account.name)" -ForegroundColor Gray
Write-Host ""

# Get current directory
$cloudApiPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# Build container image using Azure Container Registry
Write-Host "Building container image in Azure..." -ForegroundColor Yellow
$acrName = "quotradingacr"  # Your ACR name
$imageName = "quotrading-api"
$imageTag = (Get-Date -Format "yyyyMMdd-HHmmss")
$fullImageName = "${acrName}.azurecr.io/${imageName}:${imageTag}"

Write-Host "   Image: $fullImageName" -ForegroundColor Gray

# Build and push using az acr build (builds in cloud)
Set-Location $cloudApiPath
az acr build --registry $acrName --image "${imageName}:${imageTag}" --image "${imageName}:latest" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Image build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Image built and pushed successfully" -ForegroundColor Green
Write-Host ""

# Update Container App with new image
Write-Host "Updating Container App..." -ForegroundColor Yellow
az containerapp update `
    --name $ContainerAppName `
    --resource-group $ResourceGroup `
    --image "${acrName}.azurecr.io/${imageName}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Container App update failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Container App updated successfully" -ForegroundColor Green
Write-Host ""

# Get the app URL
Write-Host "Getting app URL..." -ForegroundColor Yellow
$appDetails = az containerapp show `
    --name $ContainerAppName `
    --resource-group $ResourceGroup `
    --query properties.configuration.ingress.fqdn `
    --output tsv

$appUrl = "https://$appDetails"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "App URL: $appUrl" -ForegroundColor White
Write-Host ""
Write-Host "Test endpoints:" -ForegroundColor Yellow
Write-Host "  Health: $appUrl/health" -ForegroundColor Gray
Write-Host "  API: $appUrl/api/ml/save_experience" -ForegroundColor Gray
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  az containerapp logs show --name $ContainerAppName --resource-group $ResourceGroup --follow" -ForegroundColor Gray
Write-Host ""
