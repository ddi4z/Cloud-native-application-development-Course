# build-all.ps1
# Ejecuta los docker build de cada microservicio

$root = Get-Location

# Lista de apps
$apps = @("scores_app", "users_app", "offers_app", "routes_app", "rf003_app", "rf004_app", "rf005_app")

foreach ($app in $apps) {
    Write-Host "🚀 Construyendo $app ..."
    Set-Location "$root\$app"
    docker build -t "$($app -replace '_app','')-app:v1.0.0" .
    Set-Location $root
}
# .\build-all.ps1

# kubectl apply -f k8s/local/
# C:\Windows\System32\drivers\etc\hosts