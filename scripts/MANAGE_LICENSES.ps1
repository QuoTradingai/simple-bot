# QuoTrading License Key Manager
# Run this to create/manage license keys

param(
    [Parameter(Mandatory=$false)]
    [string]$Action = "create",
    
    [Parameter(Mandatory=$false)]
    [string]$Email,
    
    [Parameter(Mandatory=$false)]
    [string]$LicenseType = "TRIAL",
    
    [Parameter(Mandatory=$false)]
    [int]$Days = 30
)

$dbPassword = az functionapp config appsettings list --resource-group quotrading-rg --name quotrading-api-v2 --query "[?name=='DB_PASSWORD'].value" --output tsv

if ($Action -eq "create") {
    Write-Host "`n🔑 Creating New License Key" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
    
    if (-not $Email) {
        $Email = Read-Host "Enter customer email"
    }
    
    # Generate license key
    $licenseKey = "QT-" + (-join ((65..90) + (48..57) | Get-Random -Count 12 | ForEach-Object {[char]$_}))
    $accountId = [guid]::NewGuid().ToString().Substring(0, 12)
    $expiration = (Get-Date).AddDays($Days).ToString("yyyy-MM-dd")
    
    # Create SQL
    $sql = @"
INSERT INTO users (account_id, email, license_key, license_type, license_status, license_expiration)
VALUES ('$accountId', '$Email', '$licenseKey', '$LicenseType', 'ACTIVE', '$expiration');
"@
    
    Write-Host "`n✅ License Created:" -ForegroundColor Green
    Write-Host "  Email: $Email" -ForegroundColor White
    Write-Host "  License Key: $licenseKey" -ForegroundColor Yellow
    Write-Host "  Type: $LicenseType" -ForegroundColor White
    Write-Host "  Expires: $expiration" -ForegroundColor White
    Write-Host "`n📝 Save this SQL to database:" -ForegroundColor Cyan
    Write-Host $sql -ForegroundColor Gray
    
    # Save to file
    $sql | Out-File "license_$accountId.sql"
    Write-Host "`n💾 Saved to: license_$accountId.sql" -ForegroundColor Green
    
} elseif ($Action -eq "list") {
    Write-Host "`n📋 Listing all licenses requires database connection" -ForegroundColor Yellow
}
