param(
    [string]$ContainerName = 'tawi-postgres',
    [string]$Image = 'postgres:13',
    [string]$PostgresUser = 'postgres',
    [string]$PostgresPassword = $env:POSTGRES_PASSWORD,
    [string]$PostgresDb = $env:POSTGRES_DB,
    [int]$Port = 5432
)

Write-Host "Ensuring Docker is available..."
try {
    docker version > $null 2>&1
} catch {
    Write-Error "Docker does not appear to be available. Please install/start Docker and retry."
    exit 1
}

$running = docker ps --filter "name=$ContainerName" --format "{{.Names}}" | Select-String $ContainerName -Quiet
if (-not $running) {
    if (-not $PostgresPassword) {
        Write-Host "POSTGRES_PASSWORD not provided via env or parameter. Please set POSTGRES_PASSWORD and retry."
        exit 1
    }
    if (-not $PostgresDb) {
        $PostgresDb = 'tawi_db'
    }
    Write-Host "Starting Postgres container $ContainerName (image $Image) on port $Port..."
    docker run --name $ContainerName -e POSTGRES_USER=$PostgresUser -e POSTGRES_PASSWORD=$PostgresPassword -e POSTGRES_DB=$PostgresDb -p ${Port}:5432 -d $Image | Out-Null
} else {
    Write-Host "Container $ContainerName already running."
}

Write-Host "Waiting for Postgres to accept connections..."
for ($i = 0; $i -lt 60; $i++) {
    try {
        docker exec $ContainerName pg_isready -U $PostgresUser > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Postgres is ready."
            exit 0
        }
    } catch {
        # ignore and retry
    }
    Start-Sleep -Seconds 1
}

Write-Error "Timed out waiting for Postgres to become ready. Check container logs with: docker logs $ContainerName"
exit 1
