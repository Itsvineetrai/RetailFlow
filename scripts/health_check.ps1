Write-Host "=== RetailFlow Health Check ==="
docker ps
Write-Host ""
Write-Host "Spark Master UI : http://localhost:8081"
Write-Host "Kafka UI        : http://localhost:8080"
Write-Host "MinIO Console   : http://localhost:9001"
Write-Host "MinIO API       : http://localhost:9000"
