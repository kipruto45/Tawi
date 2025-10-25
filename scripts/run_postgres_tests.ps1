param(
    [string]$ContainerName = 'tawi-postgres'
)

Write-Host "Starting Postgres (if not already)..."
Write-Host "Starting Postgres (if not already)..."
# start_postgres.ps1 will read POSTGRES_PASSWORD/POSTGRES_DB from environment
& "$PSScriptRoot\start_postgres.ps1" -ContainerName $ContainerName

Write-Host "Setting environment variables for Postgres + 2FA tests..."
$env:USE_POSTGRES = '1'
$env:POSTGRES_DB = ${env:POSTGRES_DB} -or 'tawi_db'
$env:POSTGRES_USER = ${env:POSTGRES_USER} -or 'postgres'
# Do not hardcode POSTGRES_PASSWORD here; prefer reading from environment or CI secret
if (-not $env:POSTGRES_PASSWORD) {
    Write-Host "Warning: POSTGRES_PASSWORD not set; ensure you set it in your environment before running tests."
}
$env:POSTGRES_HOST = ${env:POSTGRES_HOST} -or '127.0.0.1'
$env:POSTGRES_PORT = ${env:POSTGRES_PORT} -or '5432'
$env:USE_2FA = ${env:USE_2FA} -or '1'

Write-Host "Installing Python deps (ensure venv is active)..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt psycopg2-binary dj-database-url

Write-Host "Running migrations..."
python manage.py migrate --noinput

Write-Host "Running real two-factor E2E tests..."
python manage.py test accounts.tests.test_2fa_wizard_e2e_real -v 2
python manage.py test accounts.tests.test_2fa_integration_real_strict -v 2
