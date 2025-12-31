# Script de Demarrage Full Stack TimeWeaver
# ==========================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " DEMARRAGE TIMEWEAVER FULL STACK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Fonction pour verifier si un port est utilise
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

# Fonction pour demarrer un service Spring Boot
function Start-SpringService {
    param(
        [string]$ServiceName,
        [string]$ServicePath,
        [int]$Port
    )
    
    Write-Host "Demarrage de $ServiceName (port $Port)..." -ForegroundColor Yellow
    
    if (Test-Port $Port) {
        Write-Host "  OK - $ServiceName deja en cours d'execution" -ForegroundColor Green
        return $null
    }
    
    $fullPath = Join-Path $PSScriptRoot $ServicePath
    
    if (-not (Test-Path $fullPath)) {
        Write-Host "  ERREUR: Dossier $ServicePath introuvable" -ForegroundColor Red
        return $null
    }
    
    # Demarrer le service dans une nouvelle fenetre PowerShell
    $cmd = "cd '$fullPath'; Write-Host 'Demarrage de $ServiceName...' -ForegroundColor Cyan; mvn spring-boot:run"
    $process = Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd -PassThru -WindowStyle Normal
    
    Write-Host "  Service demarre (PID: $($process.Id))" -ForegroundColor Gray
    return $process
}

# ETAPE 1: Demarrage des Services Backend
Write-Host "ETAPE 1/3: Demarrage des microservices backend" -ForegroundColor Magenta
Write-Host ""

# Demarrer Discovery Service (Eureka) en premier
$eurekaProcess = Start-SpringService -ServiceName "Discovery Service" -ServicePath "discovery-service" -Port 8761
Start-Sleep -Seconds 15

# Demarrer les autres services
$userProcess = Start-SpringService -ServiceName "User Management" -ServicePath "user-management-service" -Port 8081
Start-Sleep -Seconds 3

$aiProcess = Start-SpringService -ServiceName "AI Prediction" -ServicePath "ai-prediction-service" -Port 8082
Start-Sleep -Seconds 3

$notifProcess = Start-SpringService -ServiceName "Notification" -ServicePath "notification-service" -Port 8083
Start-Sleep -Seconds 3

$trackingProcess = Start-SpringService -ServiceName "Time Tracking" -ServicePath "time-tracking-service" -Port 8084
Start-Sleep -Seconds 3

$gatewayProcess = Start-SpringService -ServiceName "API Gateway" -ServicePath "api-gateway" -Port 8080

Write-Host ""
Write-Host "Attente du demarrage complet des services (45 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 45

# ETAPE 2: Verification des Services
Write-Host ""
Write-Host "ETAPE 2/3: Verification de l'etat des services" -ForegroundColor Magenta
Write-Host ""

$services = @(
    @{Name = "Discovery (Eureka)"; Port = 8761 },
    @{Name = "User Management"; Port = 8081 },
    @{Name = "AI Prediction"; Port = 8082 },
    @{Name = "Notification"; Port = 8083 },
    @{Name = "Time Tracking"; Port = 8084 },
    @{Name = "API Gateway"; Port = 8080 }
)

foreach ($service in $services) {
    if (Test-Port $service.Port) {
        Write-Host "  OK - $($service.Name) (port $($service.Port))" -ForegroundColor Green
    }
    else {
        Write-Host "  KO - $($service.Name) (port $($service.Port))" -ForegroundColor Red
    }
}

# ETAPE 3: Demarrage du Frontend Angular
Write-Host ""
Write-Host "ETAPE 3/3: Demarrage du frontend Angular" -ForegroundColor Magenta
Write-Host ""

$frontendPath = Join-Path $PSScriptRoot "timeweaver-web"

if (Test-Port 4200) {
    Write-Host "  OK - Frontend Angular deja en cours (port 4200)" -ForegroundColor Green
}
elseif (Test-Port 4201) {
    Write-Host "  OK - Frontend Angular deja en cours (port 4201)" -ForegroundColor Green
}
else {
    Write-Host "Demarrage du frontend Angular..." -ForegroundColor Yellow
    
    if (Test-Path $frontendPath) {
        $cmd = "cd '$frontendPath'; Write-Host 'Demarrage du frontend Angular...' -ForegroundColor Cyan; npm start"
        $frontendProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd -PassThru -WindowStyle Normal
        
        Write-Host "  Frontend demarre (PID: $($frontendProcess.Id))" -ForegroundColor Gray
        Write-Host "  Attente de la compilation (30 secondes)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    }
    else {
        Write-Host "  ERREUR: Dossier timeweaver-web introuvable" -ForegroundColor Red
    }
}

# RESUME ET ACCES
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " APPLICATION DEMARREE !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "ACCES A L'APPLICATION:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Frontend (Angular):" -ForegroundColor Yellow
Write-Host "  -> http://localhost:4200" -ForegroundColor White
Write-Host ""
Write-Host "  Backend Services:" -ForegroundColor Yellow
Write-Host "  -> API Gateway:        http://localhost:8080" -ForegroundColor White
Write-Host "  -> Discovery (Eureka): http://localhost:8761" -ForegroundColor White
Write-Host ""
Write-Host "  Bases de Donnees H2:" -ForegroundColor Yellow
Write-Host "  -> User Management:    http://localhost:8081/h2-console" -ForegroundColor White
Write-Host "  -> Time Tracking:      http://localhost:8084/h2-console" -ForegroundColor White
Write-Host ""

Write-Host "INFORMATIONS DE CONNEXION H2:" -ForegroundColor Cyan
Write-Host "  JDBC URL (User):      jdbc:h2:file:./data/userdb" -ForegroundColor Gray
Write-Host "  JDBC URL (Tracking):  jdbc:h2:file:./data/timetrackingdb" -ForegroundColor Gray
Write-Host "  Username: sa" -ForegroundColor Gray
Write-Host "  Password: (vide)" -ForegroundColor Gray
Write-Host ""

# Demander si on veut ouvrir le navigateur
$openBrowser = Read-Host "Voulez-vous ouvrir l'application dans le navigateur? (O/N)"
if ($openBrowser -eq "O" -or $openBrowser -eq "o") {
    Write-Host ""
    Write-Host "Ouverture du navigateur..." -ForegroundColor Cyan
    Start-Process "http://localhost:4200"
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:8761"
}

Write-Host ""
Write-Host "NOTES:" -ForegroundColor Yellow
Write-Host "  - Les services s'executent dans des fenetres PowerShell separees" -ForegroundColor Gray
Write-Host "  - Fermez ces fenetres pour arreter les services" -ForegroundColor Gray
Write-Host "  - Consultez GUIDE_ACCES_BD.md pour plus d'informations" -ForegroundColor Gray
Write-Host ""
Write-Host "Bon developpement avec TimeWeaver!" -ForegroundColor Magenta
Write-Host ""
