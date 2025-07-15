@echo off
setlocal enabledelayedexpansion

:: ====== BEEP TEST FEATURE ======
if /i "%~1"=="beep" (
    echo Testing beep sequence...
    powershell -c "[console]::beep(800,200); Start-Sleep -Milliseconds 100; [console]::beep(1200,200); Start-Sleep -Milliseconds 100; [console]::beep(1000,400)"
    echo Done!
    exit /b 0
)

:: ====== AUTO-DETECT OOBABOOGA AND Z-WAIFU FOLDERS ======
set "ROOTDIR=%~dp0"
set "OOBABAT=start_windows.bat"
set "ZWAIFUBAT=startup.bat"
set "OOBADIR="
set "ZWAIFUDIR="

:: Search for Oobabooga
for /r "%ROOTDIR%" %%d in (%OOBABAT%) do (
    set "OOBADIR=%%~dpd"
    goto :found_ooba
)
:found_ooba

:: Search for Z-Waifu
for /r "%ROOTDIR%" %%d in (%ZWAIFUBAT%) do (
    set "ZWAIFUDIR=%%~dpd"
    goto :found_zwaifu
)
:found_zwaifu

:: Check if both were found
if "%OOBADIR%"=="" (
    echo Could not find Oobabooga folder containing %OOBABAT%. Exiting.
    powershell -c "[console]::beep(400,700)"
    exit /b 1
)
if "%ZWAIFUDIR%"=="" (
    echo Could not find Z-Waifu folder containing %ZWAIFUBAT%. Exiting.
    powershell -c "[console]::beep(400,700)"
    exit /b 1
)

:: ====== CHECK FOR RUNNING PROCESSES ======
tasklist | find /i "cmd.exe" | find /i "Oobabooga" >nul && (
    echo WARNING: Oobabooga may already be running.
    set /p CONTINUE=Continue anyway? (Y/N): 
    if /i "!CONTINUE!" NEQ "Y" exit /b 1
)
tasklist | find /i "cmd.exe" | find /i "ZWaifu" >nul && (
    echo WARNING: Z-Waifu may already be running.
    set /p CONTINUE=Continue anyway? (Y/N): 
    if /i "!CONTINUE!" NEQ "Y" exit /b 1
)

:: ====== CONFIGURATION ======
set "OOBALOG=%ROOTDIR%ooba_log.txt"
set "ZWAIFULOG=%ROOTDIR%zwaifu_log.txt"
set "OOBAPORT=5000"
if not "%~1"=="" if /i not "%~1"=="beep" set "OOBAPORT=%~1"
set /a tries=0
set /a maxtries=40

:: ====== START OOBABOOGA ======
title Launching Oobabooga + Z-Waifu
cd /d "%OOBADIR%"
echo Starting Oobabooga...
start "Oobabooga" /B cmd /c "%OOBABAT% > "%OOBALOG%" 2>&1"

:: ====== WAIT FOR PORT ======
echo Waiting for Oobabooga to be ready on port %OOBAPORT%...
:waitloop
timeout /t 3 >nul
powershell -Command "try { $s = New-Object Net.Sockets.TcpClient('127.0.0.1', %OOBAPORT%); $s.Close(); exit 0 } catch { exit 1 }"
if errorlevel 1 (
    set /a tries+=1
    if !tries! geq !maxtries! (
        echo Timeout waiting for Oobabooga! Exiting.
        powershell -c "[console]::beep(400,700)"
        goto kill_ooba_and_exit
    )
    goto waitloop
)

:: ====== START Z-WAIFU ======
echo Oobabooga is up. Starting Z-Waifu...
powershell -c "[console]::beep(1000,300)"
cd /d "%ZWAIFUDIR%"
start "ZWaifu" /B cmd /c "%ZWAIFUBAT% > "%ZWAIFULOG%" 2>&1"
if errorlevel 1 (
    echo Z-Waifu failed to start! Killing Oobabooga...
    powershell -c "[console]::beep(400,700)"
    goto kill_ooba_and_exit
)

echo Both Oobabooga and Z-Waifu started successfully.

:: ====== SUMMARY ======
echo.
echo =====================
echo Oobabooga log: %OOBALOG%
echo Z-Waifu log:   %ZWAIFULOG%
echo =====================
echo.
powershell -c "[console]::beep(1500,200)"
goto end

:kill_ooba_and_exit
:: Kill Oobabooga process (by window title)
taskkill /FI "WINDOWTITLE eq Oobabooga*" /F >nul 2>&1
echo Oobabooga process killed.
echo See %OOBALOG% for details.
exit /b 1

:end
endlocal
exit /b 0 