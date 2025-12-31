# ========================================
# 🚀 Script de Démarrage Full Stack TimeWeaver
# ========================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🚀 DÉMARRAGE APPLICATION TIMEWEAVER FULL STACK 🚀       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Fonction pour vérifier si un port est utilisé
function Test-Port {
    param($Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Fonction pour démarrer un service Spring Boot
function Start-SpringService {
    param(
        [string]$ServiceName,
        [string]$ServicePath,
        [int]$Port,
        [string]$Icon
    )
    
    Write-Host "$Icon Démarrage de $ServiceName (port $Port)..." -ForegroundColor Yellow
    
    if (Test-Port $Port) {
        Write-Host "   ✓ $ServiceName déjà en cours d'exécution sur le port $Port" -ForegroundColor Green
        return $null
    }
    
    $fullPath = Join-Path $PSScriptRoot $ServicePath
    
    if (-not (Test-Path $fullPath)) {
        Write-Host "   ✗ Erreur: Dossier $ServicePath introuvable" -ForegroundColor Red
        return $null
    }
    
    # Démarrer le service dans une nouvelle fenêtre PowerShell
    $process = Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$fullPath'; Write-Host '🚀 Démarrage de $ServiceName...' -ForegroundColor Cyan; mvn spring-boot:run"
    ) -PassThru -WindowStyle Normal
    
    Write-Host "   ⏳ Service démarré (PID: $($process.Id))" -ForegroundColor Gray
    return $process
}

# ========================================
# ÉTAPE 1: Démarrage des Services Backend
# ========================================

Write-Host "📦 ÉTAPE 1/3: Démarrage des microservices backend" -ForegroundColor Magenta
Write-Host ""

# Démarrer Discovery Service (Eureka) en premier
$eurekaProcess = Start-SpringService -ServiceName "Discovery Service (Eureka)" -ServicePath "discovery-service" -Port 8761 -Icon "🔍"
Start-Sleep -Seconds 15

# Démarrer les autres services
$userProcess = Start-SpringService -ServiceName "User Management Service" -ServicePath "user-management-service" -Port 8081 -Icon "👤"
Start-Sleep -Seconds 3

$aiProcess = Start-SpringService -ServiceName "AI Prediction Service" -ServicePath "ai-prediction-service" -Port 8082 -Icon "🤖"
Start-Sleep -Seconds 3

$notifProcess = Start-SpringService -ServiceName "Notification Service" -ServicePath "notification-service" -Port 8083 -Icon "📧"
Start-Sleep -Seconds 3

$trackingProcess = Start-SpringService -ServiceName "Time Tracking Service" -ServicePath "time-tracking-service" -Port 8084 -Icon "⏱️"
Start-Sleep -Seconds 3

$gatewayProcess = Start-SpringService -ServiceName "API Gateway" -ServicePath "api-gateway" -Port 8080 -Icon "🌐"

Write-Host ""
Write-Host "⏳ Attente du démarrage complet des services (45 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# ========================================
# ÉTAPE 2: Vérification des Services
# ========================================

Write-Host ""
Write-Host "📦 ÉTAPE 2/3: Vérification de l'état des services" -ForegroundColor Magenta
Write-Host ""

$services = @(
    @{Name = "Discovery (Eureka)"; Port = 8761; Url = "http://localhost:8761" },
    @{Name = "User Management"; Port = 8081; Url = "http://localhost:8081/actuator/health" },
    @{Name = "AI Prediction"; Port = 8082; Url = "http://localhost:8082/actuator/health" },
    @{Name = "Notification"; Port = 8083; Url = "http://localhost:8083/actuator/health" },
    @{Name = "Time Tracking"; Port = 8084; Url = "http://localhost:8084/actuator/health" },
    @{Name = "API Gateway"; Port = 8080; Url = "http://localhost:8080/actuator/health" }
)

foreach ($service in $services) {
    if (Test-Port $service.Port) {
        Write-Host "   ✓ $($service.Name) - OK (port $($service.Port))" -ForegroundColor Green
    }
    else {
        Write-Host "   ✗ $($service.Name) - Non disponible (port $($service.Port))" -ForegroundColor Red
    }
}

# ========================================
# ÉTAPE 3: Démarrage du Frontend Angular
# ========================================

Write-Host ""
Write-Host "📦 ÉTAPE 3/3: Démarrage du frontend Angular" -ForegroundColor Magenta
Write-Host ""

$frontendPath = Join-Path $PSScriptRoot "timeweaver-web"

if (Test-Port 4200) {
    Write-Host "   ✓ Frontend Angular déjà en cours d'exécution sur le port 4200" -ForegroundColor Green
}
elseif (Test-Port 4201) {
    Write-Host "   ✓ Frontend Angular déjà en cours d'exécution sur le port 4201" -ForegroundColor Green
}
else {
    Write-Host "🌐 Démarrage du frontend Angular..." -ForegroundColor Yellow
    
    if (Test-Path $frontendPath) {
        $frontendProcess = Start-Process powershell -ArgumentList @(
            "-NoExit",
            "-Command",
            "cd '$frontendPath'; Write-Host '🌐 Démarrage du frontend Angular...' -ForegroundColor Cyan; npm start"
        ) -PassThru -WindowStyle Normal
        
        Write-Host "   ⏳ Frontend démarré (PID: $($frontendProcess.Id))" -ForegroundColor Gray
        Write-Host "   ⏳ Attente de la compilation (30 secondes)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    }
    else {
        Write-Host "   ✗ Erreur: Dossier timeweaver-web introuvable" -ForegroundColor Red
    }
}

# ========================================
# RÉSUMÉ ET ACCÈS
# ========================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ APPLICATION DÉMARRÉE !                     ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "🌐 ACCÈS À L'APPLICATION:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Frontend (Angular):" -ForegroundColor Yellow
Write-Host "   → http://localhost:4200" -ForegroundColor White
Write-Host ""
Write-Host "   Backend Services:" -ForegroundColor Yellow
Write-Host "   → API Gateway:        http://localhost:8080" -ForegroundColor White
Write-Host "   → Discovery (Eureka): http://localhost:8761" -ForegroundColor White
Write-Host ""
Write-Host "   Bases de Données H2:" -ForegroundColor Yellow
Write-Host "   → User Management:    http://localhost:8081/h2-console" -ForegroundColor White
Write-Host "   → Time Tracking:      http://localhost:8084/h2-console" -ForegroundColor White
Write-Host ""

Write-Host "💡 INFORMATIONS DE CONNEXION H2:" -ForegroundColor Cyan
Write-Host "   JDBC URL (User):      jdbc:h2:file:./data/userdb" -ForegroundColor Gray
Write-Host "   JDBC URL (Tracking):  jdbc:h2:file:./data/timetrackingdb" -ForegroundColor Gray
Write-Host "   Username: sa" -ForegroundColor Gray
Write-Host "   Password: (vide)" -ForegroundColor Gray
Write-Host ""

# Demander si on veut ouvrir le navigateur
$openBrowser = Read-Host "Voulez-vous ouvrir l'application dans le navigateur? (O/N)"
if ($openBrowser -eq "O" -or $openBrowser -eq "o") {
    Write-Host ""
    Write-Host "🌐 Ouverture du navigateur..." -ForegroundColor Cyan
    Start-Process "http://localhost:4200"
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8761"
}

Write-Host ""
Write-Host "📝 NOTES:" -ForegroundColor Yellow
Write-Host "   • Les services s'exécutent dans des fenêtres PowerShell séparées" -ForegroundColor Gray
Write-Host "   • Fermez ces fenêtres pour arrêter les services" -ForegroundColor Gray
Write-Host "   • Consultez GUIDE_ACCES_BD.md pour plus d'informations" -ForegroundColor Gray
Write-Host ""
Write-Host "✨ Bon développement avec TimeWeaver! ✨" -ForegroundColor Magenta
Write-Host ""
