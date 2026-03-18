@echo off
cd /d "%~dp0"
REM C:\Python313\python.exe ile baslat (uygulamanin kullandigi Python)
if exist "C:\Python313\python.exe" (
    "C:\Python313\python.exe" main.py
) else (
    py -3 main.py
)
if errorlevel 1 pause
