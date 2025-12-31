# 🔍 Rapport d'état des services TimeWeaver
$services = @(
    @{ name = "Eureka (Discovery Service)"; port = 8761 },
    @{ name = "API Gateway"; port = 8080 },
    @{ name = "User Management"; port = 8081 },
    @{ name = "AI Prediction"; port = 8082 },
    @{ name = "Notification Service"; port = 8083 },
    @{ name = "Time Tracking"; port = 8084 }
)

Write-Host "VÉRIFICATION DE L'ÉTABLISSEMENT DES SERVICES" -ForegroundColor Cyan
Write-Host "--------------------------------------------"

foreach ($s in $services) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect("127.0.0.1", $s.port)
        Write-Host "✅ $($s.name) (Port $($s.port)) : EN LIGNE" -ForegroundColor Green
        $client.Close()
    }
    catch {
        Write-Host "❌ $($s.name) (Port $($s.port)) : HORS LIGNE" -ForegroundColor Red
    }
}
