# Script de empaquetado para entrega academica limpia
# Excluye estrictamente: .venv, node_modules, .git, dist, .cache, .pytest_cache, .env, backups temporales

$ProjectRoot = (Get-Item .).FullName
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TargetDir = Join-Path $ProjectRoot "delivery_package"
$TargetZip = Join-Path $ProjectRoot "GD_TI_Fase6_Despliegue_Trazable_$Timestamp.zip"

Write-Host "Iniciando empaquetado limpio para entrega academica..." -ForegroundColor Cyan

if (Test-Path $TargetDir) {
    Remove-Item -Recurse -Force $TargetDir
}

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

$ExcludeFolders = @('.venv', 'node_modules', '.git', 'dist', '.pytest_cache', '__pycache__', '.system_generated', '.idea', '.vscode', '.agents', '.gemini', 'delivery_package', 'clean_extraction_test')
$ExcludeFiles = @('*.pyc', '*.bak', '*.tmp', '*.log', '*.db', '*.sqlite', '*.sqlite3', '*.zip')

# Copiar archivos raiz relevantes (incluye .env.example y walkthrough.md; excluye .env secreto)
Get-ChildItem -Path $ProjectRoot -File | Where-Object {
    $name = $_.Name
    if ($name -eq '.env' -or $name -eq '.env.local') { return $false }
    $skip = $false
    foreach ($pat in $ExcludeFiles) {
        if ($name -like $pat) { $skip = $true; break }
    }
    -not $skip
} | ForEach-Object {
    Copy-Item $_.FullName -Destination $TargetDir
}

# Copiar carpetas relevantes asegurando apps, models y data para entrega completa
$SourceFolders = @('backend', 'src', 'public', 'tests', 'docs', 'data', 'scripts', 'apps', 'models')

foreach ($folder in $SourceFolders) {
    $srcPath = Join-Path $ProjectRoot $folder
    if (Test-Path $srcPath) {
        $destPath = Join-Path $TargetDir $folder
        New-Item -ItemType Directory -Force -Path $destPath | Out-Null
        
        Get-ChildItem -Path $srcPath -Recurse | Where-Object {
            $fullName = $_.FullName
            $rel = $fullName.Substring($srcPath.Length)
            
            $skip = $false
            foreach ($exFolder in $ExcludeFolders) {
                if ($rel -like "*\$exFolder*" -or $rel -like "*\$exFolder") { $skip = $true; break }
            }
            foreach ($exFile in $ExcludeFiles) {
                if ($_.Name -like $exFile) { $skip = $true; break }
            }
            -not $skip
        } | ForEach-Object {
            $destItem = $_.FullName.Replace($srcPath, $destPath)
            if ($_.PSIsContainer) {
                if (-not (Test-Path $destItem)) {
                    New-Item -ItemType Directory -Force -Path $destItem | Out-Null
                }
            } else {
                $parent = Split-Path $destItem -Parent
                if (-not (Test-Path $parent)) {
                    New-Item -ItemType Directory -Force -Path $parent | Out-Null
                }
                Copy-Item $_.FullName -Destination $destItem -Force
            }
        }
        Write-Host "Copiado: $folder" -ForegroundColor Green
    }
}

# Comprimir en archivo zip
Write-Host "Generando archivo ZIP: $TargetZip..." -ForegroundColor Yellow
if (Test-Path $TargetZip) { Remove-Item -Force $TargetZip }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($TargetDir, $TargetZip, [System.IO.Compression.CompressionLevel]::Optimal, $false)

# Eliminar carpeta intermedia
Start-Sleep -Milliseconds 500
Remove-Item -Recurse -Force $TargetDir -ErrorAction SilentlyContinue

if (Test-Path $TargetZip) {
    $ZipItem = Get-Item $TargetZip
    $SizeMB = [math]::Round($ZipItem.Length / 1MB, 2)
    Write-Host "Empaquetado exitoso!" -ForegroundColor Cyan
    Write-Host "Ubicacion: $($ZipItem.FullName)" -ForegroundColor White
    Write-Host "Tamano del paquete limpio: $SizeMB MB (sin .venv ni node_modules)" -ForegroundColor White
} else {
    Write-Error "Fallo la creacion del archivo ZIP."
}
