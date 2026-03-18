@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Data Analysis - EXE Olusturma
echo.
python build_exe.py
echo.
pause
