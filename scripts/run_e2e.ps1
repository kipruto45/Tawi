# Helper to run Playwright e2e tests locally
# Usage: ./scripts/run_e2e.ps1

# Start Django dev server in background (PowerShell job)
Write-Host "Starting Django dev server on http://localhost:8000"
$python = Join-Path -Path $PSScriptRoot -ChildPath "..\.venv\Scripts\python.exe"
Start-Job -ScriptBlock { param($p) & $p runserver } -ArgumentList $python | Out-Null
Start-Sleep -Seconds 2

# Install Node deps if node_modules missing
if (-Not (Test-Path -Path "node_modules")) {
  Write-Host "Installing Node dependencies..."
  npm install
}

Write-Host "Running Playwright tests..."
npm run test:e2e

# Stop background jobs (Django server)
Get-Job | Stop-Job | Remove-Job
Write-Host "E2E run complete"
