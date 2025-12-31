# Verification simplified
Write-Host "Verification des services backend..." -ForegroundColor Cyan

function Check-Service($name, $port) {
    Write-Host "- $name (Port $port): " -NoNewline
    $tcp = New-Object System.Net.Sockets.TcpClient
    try {
        $tcp.Connect("localhost", $port)
        Write-Host "EN LIGNE [OK]" -ForegroundColor Green
    }
    catch {
        Write-Host "HORS LIGNE [OFF]" -ForegroundColor Red
    }
    finally {
        $tcp.Close()
    }
}

Check-Service "Eureka (Discovery)" 8761
Check-Service "API Gateway" 8080
Check-Service "User Management" 8081
Check-Service "AI Prediction" 8082
Check-Service "Notification" 8083
Check-Service "Time Tracking" 8084

Write-Host ""
Write-Host "Dashboard Eureka: http://localhost:8761"
