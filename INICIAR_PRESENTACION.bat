@echo off
REM ============================================================================
%~d0
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo ================================================================================
echo  GEMelo Digital Epidemiologico - Lanzador de Presentacion (Puerto 5173/8002)
echo ================================================================================
echo.

REM Verificar que estamos en la carpeta correcta
if not exist "backend\main.py" (
    echo [ERROR] No se encontro backend/main.py en el directorio actual.
    echo   Asegurate de ejecutar este archivo desde la carpeta del proyecto.
    pause
    exit /b 1
)

if not exist "src\App.tsx" (
    echo [ERROR] No se encontro src/App.tsx en el directorio actual.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual en .venv\Scripts\python.exe
    pause
    exit /b 1
)

if not exist "node_modules\.package-lock.json" (
    echo [ADVERTENCIA] No se encontro node_modules. Ejecuta 'npm install' primero.
)

echo [1/5] Verificando entorno...
echo   - Backend: Python 3.11.9 (.venv)
echo   - Frontend: Node.js + Vite (puerto 5173)
echo   - Backend puerto: 8002
echo.

REM Verificar si ya estan corriendo los servicios
echo [2/5] Verificando si los servicios ya estan activos...
for /f "tokens=2 delims=:" %%a in ('netstat -ano ^| findstr ":8002"') do set PID_BACKEND=%%a
for /f "tokens=2 delims=:" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do set PID_FRONTEND=%%a

if not "%PID_BACKEND%"=="" (
    echo   Backend ya esta ejecutándose (PID %PID_BACKEND%). No se iniciara de nuevo.
) else (
    echo [3/5] Iniciando Backend FastAPI (puerto 8002)...
    start "" "Backend-GD_TI" .venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --reload
    echo   Esperando a que el backend esté listo...
    set /a CONTADOR=0
    :CHECK_BACKEND
    powershell -Command "try { \$r = Invoke-WebRequest -Uri 'http://127.0.0.1:8001/health' -TimeoutSec 2 -ErrorAction SilentlyContinue; if (\$r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
    if errorlevel 1 (
        set /a CONTADOR=%CONTADOR%+1
        if %CONTADOR% GTR 30 (
            echo   [ADVERTENCIA] Backend no respondió después de 30 segundos.
        ) else (
            timeout /t 1 >nul
            goto CHECK_BACKEND
        )
    ) else (
        echo   Backend OK en puerto 8002.
    )
)

if not "%PID_FRONTEND%"=="" (
    echo   Frontend ya está ejecutándose (puerto 5173). No se iniciará de nuevo.
) else (
    echo [4/5] Iniciando Frontend React (puerto 5173)...
    start "" "Frontend-GD_TI" npm run dev
    echo   Esperando a que el frontend esté listo...
    set /a CONTADOR=0
    :CHECK_FRONTEND
    powershell -Command "try { \$r = Invoke-WebRequest -Uri 'http://127.0.0.1:5173/' -TimeoutSec 2 -ErrorAction SilentlyContinue; if (\$r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
    if errorlevel 1 (
        set /a CONTADOR=%CONTADOR%+1
        if %CONTADOR% GTR 60 (
            echo   [ADVERTENCIA] Frontend no respondió después de 60 segundos.
        ) else (
            timeout /t 1 >nul
            goto CHECK_FRONTEND
        )
    ) else (
        echo   Frontend OK en puerto 5173.
    )
)

echo.
echo [5/5] Abriendo aplicación en el navegador...
start "" "http://127.0.0.1:5173"
echo.
echo ================================================================================
echo  LISTO. El sistema está disponible en:
echo    http://127.0.0.1:5173  (Frontend - inicio de sesión requerido)
echo    http://127.0.0.1:8002/docs  (Backend - documentacion API)
echo ================================================================================
echo.
echo Para detener el sistema, ejecuta: DETENER_PRESENTACION.bat
echo ================================================================================
pause