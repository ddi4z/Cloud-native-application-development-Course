# build-all.ps1
# Ejecuta los docker build de cada microservicio

$root = Get-Location

# Lista de apps
$apps = @("scores_app", "users_app", "offers_app", "routes_app", "posts_app" , "rf003_app", "rf004_app", "rf005_app", "credit_card_app")
#$apps = @("users_app")

foreach ($app in $apps) {
    Write-Host "🚀 Construyendo $app ..."
    Set-Location "$root\$app"
    $imageName = ($app -replace '_','-') -replace '-app',''
    $imageTag = "$imageName-app:v1.0.0"

    docker build --no-cache  -t $imageTag .
    Set-Location $root
}
# .\build-all.ps1

# kubectl apply -f k8s/local/
