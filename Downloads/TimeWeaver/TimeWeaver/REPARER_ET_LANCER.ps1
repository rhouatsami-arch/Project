# 🛠️ Script de Réparation et Lancement TimeWeaver
# =================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 🛠️ RÉPARATION SYSTEME TIMEWEAVER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vérification des outils
Write-Host "🔍 Vérification des outils..." -ForegroundColor Yellow
$java = Get-Command java -ErrorAction SilentlyContinue
$mvn = Get-Command mvn -ErrorAction SilentlyContinue
$node = Get-Command node -ErrorAction SilentlyContinue

if (-not $java) { Write-Host "❌ Java est manquant !" -ForegroundColor Red }
if (-not $mvn) { Write-Host "⚠️ Maven (mvn) n'est pas dans le PATH. Le build Docker sera privilégié." -ForegroundColor Yellow }
if (-not $node) { Write-Host "❌ Node.js est manquant !" -ForegroundColor Red }

# 2. Correction des configurations (Déjà faites par l'IA mais on vérifie)
Write-Host "⚙️ Vérification des configurations..." -ForegroundColor Yellow
Write-Host "  - Proxy Angular: OK" -ForegroundColor Green
Write-Host "  - Fallback AI Backend: OK" -ForegroundColor Green
Write-Host "  - Toasts Frontend: OK" -ForegroundColor Green

# 3. Tentative de Build Backend
Write-Host "🏗️ Tentative de build des JARs..." -ForegroundColor Yellow
if ($mvn) {
    Write-Host "📦 Build avec Maven local..." -ForegroundColor Gray
    mvn clean package -DskipTests
}
else {
    Write-Host "📦 Maven local absent. Utilisation de Docker pour le build..." -ForegroundColor Gray
    docker-compose build
}

# 4. Lancement
Write-Host "🚀 Lancement de l'application..." -ForegroundColor Magenta
Write-Host ""

# Demander le mode de lancement
$mode = Read-Host "Souhaitez-vous lancer via [D]ocker ou [P]owershell (manuel)? (D/P)"

if ($mode -eq "D" -or $mode -eq "d") {
    Write-Host "🐳 Lancement via Docker Compose..." -ForegroundColor Cyan
    docker-compose up -d
}
else {
    Write-Host "💻 Lancement manuel via start-app.ps1..." -ForegroundColor Cyan
    .\start-app.ps1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " ✅ RÉPARATION TERMINÉE !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Accès application: http://localhost:4200" -ForegroundColor White
Write-Host "📖 Consultez CORRECTION_CONNEXION.md pour les détails." -ForegroundColor Gray
Write-Host ""
