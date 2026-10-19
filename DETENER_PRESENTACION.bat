@echo off
REM ============================================================================
%~d0
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo ================================================================================
echo  GD_TI - Deteniendo servicios del gemelo digital
echo ================================================================================
echo.

set /a CONTADOR=0

echo [1/2] Deteniendo backend FastAPI (puerto 8002)...
for /f "tokens=5 delims= " %%a in ('netstat -ano ^| findstr ":8002" ^| findstr "LISTENING"') do (
    set PID=%%a
    echo   Deteniendo PID %PID%...
    taskkill /PID %%PID% /F >nul 2>&1
    set /a CONTADOR=1
)
if %CONTADOR%==0 (
    echo   No hay backend corriendo en puerto 8002.
)

echo [2/2] Deteniendo frontend React (puerto 5173)...
for /f "tokens=5 delims= " %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    set PID=%%a
    echo   Deteniendo PID %PID%...
    taskkill /PID %%PID% /F >nul 2>&1
    set /a CONTADOR=1
)
if %CONTADOR%==0 (
    echo   No hay frontend corriendo en puerto 5173.
)

echo.
echo ================================================================================
echo  Servicios detenidos.
echo ================================================================================
pause