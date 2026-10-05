@echo off
setlocal
title NERV-BREAK Antigravity MITM Launcher
set HTTPS_PROXY=http://127.0.0.1:8089
set HTTP_PROXY=http://127.0.0.1:8089
set SSL_CERT_FILE=C:\Users\tavan\.mitmproxy\mitmproxy-ca-cert.pem
set REQUESTS_CA_BUNDLE=C:\Users\tavan\.mitmproxy\mitmproxy-ca-cert.pem
set NODE_TLS_REJECT_UNAUTHORIZED=0
set NODE_OPTIONS=--use-system-ca
echo [NERV-BREAK] HTTPS_PROXY=%HTTPS_PROXY%
echo [NERV-BREAK] Starting Antigravity IDE with MITM routing...
start "" "C:\Users\tavan\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe"
endlocal
