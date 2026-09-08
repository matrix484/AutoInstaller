@echo off
title Auto Installer
echo ==========================================
echo          AUTO INSTALLER
echo ==========================================
echo.
echo Installing required applications...
echo.

echo [1/2] Installing Git...
winget install --id Git.Git --silent --accept-package-agreements --accept-source-agreements

if %errorlevel% neq 0 (
    echo Failed to install Git.
    pause
    exit /b 1
)

echo Git installed successfully.
echo.

echo [2/2] Installing Visual Studio Code...
winget install --id Microsoft.VisualStudioCode --silent --accept-package-agreements --accept-source-agreements

if %errorlevel% neq 0 (
    echo Failed to install Visual Studio Code.
    pause
    exit /b 1
)

echo Visual Studio Code installed successfully.
echo.

echo ==========================================
echo       INSTALLATION COMPLETED
echo ==========================================
echo.
echo Your applications are ready to use.
pause