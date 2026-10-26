@echo off
setlocal
cd /d "%~dp0"

py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name AutoInstaller --distpath dist --workpath build main.py
if errorlevel 1 (
    echo.
    echo Build failed. Ensure dependencies and PyInstaller are installed:
    echo   py -3 -m pip install -r requirements.txt
    echo   py -3 -m pip install pyinstaller
    exit /b 1
)

copy /Y ".env.example" "dist\.env.example" >nul
echo.
echo Build complete: %~dp0dist\AutoInstaller.exe
echo Copy your local .env beside AutoInstaller.exe before launching it.
