# 🔍 Script de Vérification de l'État des Services Backend
# =========================================================

$ErrorActionPreference = "Continue"

$services = @(
    @{ Name = "Discovery Service (Eureka)"; Port = 8761; Path = "/"; ExpectedCode = 200 },
    @{ Name = "API Gateway"; Port = 8080; Path = "/actuator/health"; ExpectedCode = 200 },
    @{ Name = "User Management Service"; Port = 8081; Path = "/actuator/health"; ExpectedCode = 200 },
    @{ Name = "AI Prediction Service"; Port = 8082; Path = "/actuator/health"; ExpectedCode = 200 },
    @{ Name = "Notification Service"; Port = 8083; Path = "/actuator/health"; ExpectedCode = 200 },
    @{ Name = "Time Tracking Service"; Port = 8084; Path = "/actuator/health"; ExpectedCode = 200 }
)

Write-Host ""
Write-Host "🕵️ Analyse de l'état des servicesbackend..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$allUp = $true

foreach ($service in $services) {
    Write-Host "- Vérification de $($service.Name) (Port $($service.Port))..." -NoNewline
    
    try {
        $url = "http://localhost:$($service.Port)$($service.Path)"
        $response = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        
        if ($response.StatusCode -eq 200) {
            Write-Host " [EN LIGNE ✅]" -ForegroundColor Green
        }
        else {
            Write-Host " [ERREUR $($response.StatusCode) ⚠️]" -ForegroundColor Yellow
            $allUp = $false
        }
    }
    catch {
        Write-Host " [HORS LIGNE ❌]" -ForegroundColor Red
        $allUp = $false
    }
}

Write-Host ""
if ($allUp) {
    Write-Host "✨ Tous les services backend fonctionnent correctement !" -ForegroundColor Green
}
else {
    Write-Host "⚠️ Certains services sont hors ligne. Ils sont peut-être encore en cours de démarrage." -ForegroundColor Yellow
    Write-Host "💡 Note: Les services Spring Boot peuvent prendre jusqu'à 2-3 minutes pour démarrer." -ForegroundColor Gray
}

Write-Host ""
Write-Host "📊 Rappel des accès :" -ForegroundColor Cyan
Write-Host "Eureka Dashboard: http://localhost:8761"
Write-Host "API Gateway:      http://localhost:8080"
Write-Host ""
