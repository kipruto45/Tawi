<#
PowerShell helper to create a Postgres database and apply the schema from sql/create_schema_postgres.sql.

Environment variables used (recommended to set securely):
 - PGHOST (default: localhost)
 - PGPORT (default: 5432)
 - PGUSER (required)
 - PGPASSWORD (required)
 - PGDATABASE (database to create)

Usage:
  # export env vars, then run
  .\scripts\create_db_and_schema.ps1

#>

$ErrorActionPreference = 'Stop'

$host = $env:PGHOST -or 'localhost'
$port = $env:PGPORT -or '5432'
$user = $env:PGUSER
$pass = $env:PGPASSWORD
$db   = $env:PGDATABASE -or 'tawi_db'

if (-not $user -or -not $pass) {
    Write-Error "PGUSER and PGPASSWORD must be set in environment"
    exit 1
}

$env:PGPASSWORD = $pass

$createCmd = "psql -h $host -p $port -U $user -c \"CREATE DATABASE $db;\""
Write-Host "Creating database $db on $host:$port as $user"
try {
    cmd.exe /c $createCmd
} catch {
    Write-Warning "CREATE DATABASE may have failed or DB already exists: $_"
}

$schemaFile = Join-Path $PSScriptRoot '..\sql\create_schema_postgres.sql'
if (-not (Test-Path $schemaFile)) {
    Write-Error "Schema file not found: $schemaFile"
    exit 1
}

$applyCmd = "psql -h $host -p $port -U $user -d $db -f \"$schemaFile\""
Write-Host "Applying schema from $schemaFile to $db"
cmd.exe /c $applyCmd

Write-Host "Schema applied. You should now update your DATABASE_URL or Django settings to point at the new Postgres DB."
