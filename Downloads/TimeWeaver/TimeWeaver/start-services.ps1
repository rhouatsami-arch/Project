# Script de démarrage des services TimeWeaver
# Ce script démarre tous les microservices nécessaires

Write-Host "🚀 Démarrage des services TimeWeaver..." -ForegroundColor Cyan
Write-Host ""

# Vérifier si Docker est disponible
$dockerAvailable = Get-Command docker -ErrorAction SilentlyContinue

if ($dockerAvailable) {
    Write-Host "📦 Docker détecté - Démarrage avec Docker Compose..." -ForegroundColor Green
    docker-compose up -d
    
    Write-Host ""
    Write-Host "⏳ Attente du démarrage des services (30 secondes)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    Write-Host ""
    Write-Host "✅ Services démarrés!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Accès aux bases de données H2:" -ForegroundColor Cyan
    Write-Host "   • User Management: http://localhost:8081/h2-console" -ForegroundColor White
    Write-Host "   • Time Tracking:   http://localhost:8084/h2-console" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Autres services:" -ForegroundColor Cyan
    Write-Host "   • Discovery (Eureka): http://localhost:8761" -ForegroundColor White
    Write-Host "   • API Gateway:        http://localhost:8080" -ForegroundColor White
    Write-Host "   • Frontend Angular:   http://localhost:4200" -ForegroundColor White
    Write-Host ""
    
    # Ouvrir les consoles H2 dans le navigateur
    $openConsoles = Read-Host "Voulez-vous ouvrir les consoles H2 dans le navigateur? (O/N)"
    if ($openConsoles -eq "O" -or $openConsoles -eq "o") {
        Start-Process "http://localhost:8081/h2-console"
        Start-Sleep -Seconds 2
        Start-Process "http://localhost:8084/h2-console"
        
        Write-Host ""
        Write-Host "💡 Paramètres de connexion H2:" -ForegroundColor Yellow
        Write-Host "   JDBC URL (User):    jdbc:h2:file:./data/userdb" -ForegroundColor White
        Write-Host "   JDBC URL (Tracking): jdbc:h2:file:./data/timetrackingdb" -ForegroundColor White
        Write-Host "   Username: sa" -ForegroundColor White
        Write-Host "   Password: (laisser vide)" -ForegroundColor White
    }
    
}
else {
    Write-Host "⚠️  Docker non détecté - Démarrage manuel requis" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour démarrer les services manuellement:" -ForegroundColor Cyan
    Write-Host "1. Ouvrez plusieurs terminaux PowerShell" -ForegroundColor White
    Write-Host "2. Dans chaque terminal, naviguez vers un service et exécutez:" -ForegroundColor White
    Write-Host "   cd <nom-du-service>" -ForegroundColor Gray
    Write-Host "   mvn spring-boot:run" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Services à démarrer dans l'ordre:" -ForegroundColor Cyan
    Write-Host "   1. discovery-service (port 8761)" -ForegroundColor White
    Write-Host "   2. user-management-service (port 8081)" -ForegroundColor White
    Write-Host "   3. time-tracking-service (port 8084)" -ForegroundColor White
    Write-Host "   4. ai-prediction-service (port 8082)" -ForegroundColor White
    Write-Host "   5. notification-service (port 8083)" -ForegroundColor White
    Write-Host "   6. api-gateway (port 8080)" -ForegroundColor White
}

Write-Host ""
Write-Host "📖 Pour plus d'informations, consultez GUIDE_ACCES_BD.md" -ForegroundColor Cyan
