<#
.SYNOPSIS
Sync RL Experience Data to Azure Storage

.DESCRIPTION
Upload your local signal_experience.json to Azure Storage so the cloud RL Brain can use it.
Run this whenever you update your RL training data locally.
#>

$storageAccount = "quotradingrlstorage"
$resourceGroup = "quotrading-rg"
$container = "rl-data"
$localFile = "data/signal_experience.json"

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Sync RL Data to Azure                              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if file exists
if (-not (Test-Path $localFile)) {
    Write-Host "❌ File not found: $localFile" -ForegroundColor Red
    exit 1
}

# Get file info
$fileInfo = Get-Item $localFile
$experiences = (Get-Content $localFile | ConvertFrom-Json).Count
Write-Host "📊 Local file: $($fileInfo.Length) bytes, $experiences experiences" -ForegroundColor White

# Get connection string
Write-Host "🔑 Getting Azure Storage connection..." -ForegroundColor Yellow
$connectionString = az storage account show-connection-string `
    --name $storageAccount `
    --resource-group $resourceGroup `
    --query connectionString `
    --output tsv

if (-not $connectionString) {
    Write-Host "❌ Failed to get storage connection" -ForegroundColor Red
    exit 1
}

# Upload to Azure
Write-Host "☁️  Uploading to Azure Storage..." -ForegroundColor Yellow
az storage blob upload `
    --container-name $container `
    --name signal_experience.json `
    --file $localFile `
    --connection-string $connectionString `
    --overwrite

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Successfully synced $experiences experiences to Azure!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The cloud RL Brain will use this data on next request." -ForegroundColor Cyan
    Write-Host "Your users' bots will get decisions based on this training data." -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Upload failed" -ForegroundColor Red
}
