@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0\.."
title NERV-BREAK-Antigravity Control Panel

:menu
cls
echo.
echo   ====================================================
echo          NERV-BREAK-Antigravity Control Panel
echo   ====================================================
echo.
echo   -- Deployment and Verification ---------------------
echo   [1] deploy-workspace   Deploy to current workspace (.agents)
echo   [2] deploy-global      Deploy globally (~/.gemini/config)
echo   [3] verify             Run Verification Diagnostic Suite
echo   [4] status             Check deployment status
echo.
echo   -- Proxy and Refusal Tampering ---------------------
echo   [5] proxy-start        Start Proxy Relay (:8080) and Web Panel (:8090)
echo   [6] proxy-stop         Stop Proxy Relay
echo.
echo   -- Security Tools and MCP --------------------------
echo   [7] mcp-test           Test MCP Server Stdio loop
echo   [8] kali-wsl           Install WSL Kali Linux (recommended)
echo.
echo   -- Exit --------------------------------------------
echo   [0] quit               Exit Control Panel
echo   ====================================================
echo.
set /p "c=  Choice: "

if "%c%"=="1" goto deploy_ws
if "%c%"=="2" goto deploy_gl
if "%c%"=="3" goto verify
if "%c%"=="4" goto status
if "%c%"=="5" goto proxy_start
if "%c%"=="6" goto proxy_stop
if "%c%"=="7" goto mcp_test
if "%c%"=="8" goto kali_wsl
if "%c%"=="0" goto quit
goto menu

:deploy_ws
cls
python antigravity_deploy.py apply
pause
goto menu

:deploy_gl
cls
python antigravity_deploy.py apply --global
pause
goto menu

:verify
cls
python verify_antigravity.py
pause
goto menu

:status
cls
python antigravity_deploy.py status
pause
goto menu

:proxy_start
cls
echo Starting NERV Proxy Relay...
start "NERV-Proxy-Relay" /MIN python proxy_relay.py
timeout /t 2 /nobreak >nul
echo Proxy running on http://127.0.0.1:8080
echo Dashboard running on http://localhost:8090
pause
goto menu

:proxy_stop
cls
echo Stopping NERV Proxy Relay...
taskkill /FI "WINDOWTITLE eq NERV-Proxy-Relay*" /F 2>nul
echo Proxy stopped.
pause
goto menu

:mcp_test
cls
echo Testing MCP Server...
python mcp_server.py --auto
pause
goto menu

:kali_wsl
cls
echo Installing WSL Kali Linux (~1GB)...
wsl --install -d kali-linux
pause
goto menu

:quit
exit
