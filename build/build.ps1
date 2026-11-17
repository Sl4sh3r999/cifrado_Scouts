# Genera el ejecutable portable dist\Codificador.exe
# Requisitos: Python 3.11+ con  py -m pip install --user reportlab pywin32 pyinstaller
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

py -m PyInstaller --noconfirm --clean --onefile --windowed `
    --name Codificador `
    --paths src `
    --hidden-import win32ui --hidden-import win32print --hidden-import win32con `
    --distpath dist --workpath build\work --specpath build `
    src\main.py

Write-Host ""
Write-Host "Listo: $raiz\dist\Codificador.exe"
