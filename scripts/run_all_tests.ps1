# ==============================================================================
# Script Maestro de Pruebas Automatizadas - Gemelo Digital Epidemiologico Kenia
# ==============================================================================

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   GEMELO DIGITAL EPIDEMIOLOGICO - KENIA (47 CONDADOS)" -ForegroundColor Cyan
Write-Host "      Bateria de Pruebas y Control de Calidad (Semana 3)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$TotalStart = Get-Date

# 1. PRUEBAS EN PYTHON
Write-Host "[1/3] Ejecutando Suite de Pruebas en Python (34 Pruebas)..." -ForegroundColor Yellow
$pyStart = Get-Date
python -m unittest discover -s tests -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) {
    Write-Host " -> ERROR en pruebas de Python." -ForegroundColor Red
    exit 1
}
$pyDuration = [math]::Round(((Get-Date) - $pyStart).TotalSeconds, 2)
Write-Host " -> OK: 34 pruebas en Python aprobadas exitosamente en $pyDuration s." -ForegroundColor Green
Write-Host ""

# 2. VERIFICACION DE TIPOS TYPESCRIPT
Write-Host "[2/3] Verificando Tipado Estricto de TypeScript..." -ForegroundColor Yellow
$tsStart = Get-Date
npx tsc --noEmit
if ($LASTEXITCODE -ne 0) {
    Write-Host " -> ERROR en compilacion TypeScript." -ForegroundColor Red
    exit 1
}
$tsDuration = [math]::Round(((Get-Date) - $tsStart).TotalSeconds, 2)
Write-Host " -> OK: TypeScript verificado con 0 errores en $tsDuration s." -ForegroundColor Green
Write-Host ""

# 3. COMPILACION DE PRODUCCION FRONTEND
Write-Host "[3/3] Compilando Bundle de Produccion Frontend (Vite)..." -ForegroundColor Yellow
$buildStart = Get-Date
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host " -> ERROR en compilacion de Vite." -ForegroundColor Red
    exit 1
}
$buildDuration = [math]::Round(((Get-Date) - $buildStart).TotalSeconds, 2)
Write-Host " -> OK: Bundle de produccion generado exitosamente en dist/ en $buildDuration s." -ForegroundColor Green
Write-Host ""

$TotalDuration = [math]::Round(((Get-Date) - $TotalStart).TotalSeconds, 2)
Write-Host "================================================================" -ForegroundColor Green
Write-Host "   TODAS LAS PRUEBAS Y COMPILACIONES SUPERADAS CON EXITO" -ForegroundColor Green
Write-Host "   Tiempo total transcurrido: $TotalDuration segundos" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
