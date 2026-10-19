# Script para probar la extraccion del paquete limpio y verificar su integridad
param(
    [string]$ZipPath
)

if (-not $ZipPath) {
    $latestZip = Get-ChildItem -Path . -Filter "GD_TI_Fase6_Despliegue_Trazable_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $latestZip) {
        Write-Error "No se encontro ningun archivo zip de entrega."
        exit 1
    }
    $ZipPath = $latestZip.FullName
}

Write-Host "Probando extraccion limpia de: $ZipPath" -ForegroundColor Cyan

$TestDir = Join-Path (Get-Item .).FullName "clean_extraction_test"
if (Test-Path $TestDir) {
    Remove-Item -Recurse -Force $TestDir
}
New-Item -ItemType Directory -Force -Path $TestDir | Out-Null

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($ZipPath, $TestDir)

Write-Host "Verificando contenidos del paquete extraido..." -ForegroundColor Yellow

$Checklist = @(
    "walkthrough.md",
    ".env.example",
    "README.md",
    "backend/requirements.txt",
    "backend/app/main.py",
    "backend/app/api/v1/endpoints/predictions.py",
    "backend/app/api/v1/endpoints/langchain_agent.py",
    "data/raw/owid_covid_kenya_raw.csv",
    "data/raw/pone.0236308.s001.docx",
    "data/raw/barasa_2020_surge_capacity_s1_table.csv",
    "data/processed/kenya_covid_weekly_train.csv",
    "data/processed/kenya_covid_weekly_val.csv",
    "data/processed/kenya_covid_weekly_test.csv",
    "models/champion_covid_model_v1.0.joblib",
    "models/champion_covid_model_v1.0.json",
    "docs/walkthrough.md",
    "docs/ARTICULO_CIENTIFICO_PROYECTO.md",
    "docs/AUDITORIA_PROCEDENCIA_DATOS_CONDALES.md",
    "docs/flujo_traductor_langflow_exportado.json",
    "docs/auditoria_ejecucion_langflow.json",
    "docs/evidencias/langchain_agent_kiambu_2022_12_18_1790367690729.png",
    "docs/evidencias/playground_results_1790352761335.png",
    "scripts/seed_observations_to_db.py",
    "scripts/test_reproducible_ingestion.py",
    "tests/test_weekly_prediction_alignment.py"
)

$AllOk = $true
foreach ($item in $Checklist) {
    $full = Join-Path $TestDir $item
    if (Test-Path $full) {
        Write-Host "  [OK] $item" -ForegroundColor Green
    } else {
        Write-Host "  [FALTA] $item" -ForegroundColor Red
        $AllOk = $false
    }
}

# Verificar exclusiones estrictas
$MustNotExist = @(
    ".env",
    ".venv",
    "node_modules",
    ".git",
    "dist"
)

foreach ($item in $MustNotExist) {
    $full = Join-Path $TestDir $item
    if (Test-Path $full) {
        Write-Host "  [ERROR: EXCLUSION FALLIDA] Existe $item en el paquete!" -ForegroundColor Red
        $AllOk = $false
    } else {
        Write-Host "  [OK EXCLUIDO] $item" -ForegroundColor Green
    }
}

# Comprobar hashes criptográficos en la extracción
$RawCsv = Join-Path $TestDir "data/raw/owid_covid_kenya_raw.csv"
$ModelJson = Join-Path $TestDir "models/champion_covid_model_v1.0.json"
$S1Docx = Join-Path $TestDir "data/raw/pone.0236308.s001.docx"

$shaRaw = (Get-FileHash -Path $RawCsv -Algorithm SHA256).Hash.ToLower()
$shaModel = (Get-FileHash -Path $ModelJson -Algorithm SHA256).Hash.ToLower()
$shaS1 = (Get-FileHash -Path $S1Docx -Algorithm SHA256).Hash.ToLower()

Write-Host "Hash SHA-256 data cruda extraida: $shaRaw" -ForegroundColor White
Write-Host "Hash SHA-256 metadata modelo:     $shaModel" -ForegroundColor White
Write-Host "Hash SHA-256 Barasa S1 docx:      $shaS1" -ForegroundColor White

if ($shaRaw -eq "c82f3cfc5899b25557f3bf69de987dc9628bfa6fbbee55cd77b649c9d34cd2ba") {
    Write-Host "  [HASH VERIFICADO] CSV crudo intacto." -ForegroundColor Green
} else {
    Write-Host "  [HASH ERROR] Discrepancia en CSV crudo." -ForegroundColor Red
    $AllOk = $false
}

Write-Host "`nEjecutando prueba de ingesta reproducible (0 -> 1.606) en carpeta extraida..." -ForegroundColor Cyan
$PyExe = (Get-Item ".\.venv\Scripts\python.exe").FullName

Push-Location $TestDir
try {
    & $PyExe scripts/test_reproducible_ingestion.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] Fallo scripts/test_reproducible_ingestion.py" -ForegroundColor Red
        $AllOk = $false
    } else {
        Write-Host "  [OK] Ingesta reproducible exitosa (0 -> 1.606 y Barasa S1 verificado)." -ForegroundColor Green
    }

    Write-Host "`nEjecutando suite completa de pruebas pytest en carpeta extraida..." -ForegroundColor Cyan
    & $PyExe -m pytest tests/ -v
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] Fallaron pruebas en pytest." -ForegroundColor Red
        $AllOk = $false
    } else {
        Write-Host "  [OK] Todas las pruebas pytest pasaron exitosamente." -ForegroundColor Green
    }
} finally {
    Pop-Location
}

if ($AllOk) {
    Write-Host "`n=== TODAS LAS COMPROBACIONES DEL PAQUETE EXTRAIDO PASARON EXITOSAMENTE ===" -ForegroundColor Cyan
} else {
    Write-Error "Fallo la verificacion de algunos elementos en la extraccion limpia."
}
