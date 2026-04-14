@echo off
setlocal

powershell -ExecutionPolicy Bypass -File "%~dp0create_desktop_shortcut.ps1"
if errorlevel 1 (
    echo Falha ao criar o atalho no Ambiente de Trabalho.
    pause
    exit /b %errorlevel%
)

echo Atalho criado com sucesso no Ambiente de Trabalho.
pause