@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo GitHub'a Gonderim - Advanced Data Analysis Tool
echo ========================================
echo.

echo [1/6] Git deposu olusturuluyor...
git init
if errorlevel 1 (
    echo HATA: git init basarisiz. Git kurulu mu?
    pause
    exit /b 1
)
echo.

echo [2/6] Remote ekleniyor...
git remote add origin https://github.com/MEY-26/Advanced-Data-Analysis-Tool.git 2>nul
if errorlevel 1 (
    echo Remote zaten var, guncelleniyor...
    git remote set-url origin https://github.com/MEY-26/Advanced-Data-Analysis-Tool.git
)
echo.

echo [3/6] Dosyalar ekleniyor...
git add -A
echo.

echo [4/6] Commit olusturuluyor...
git commit -m "Initial commit: Advanced Data Analysis Tool - ANOVA, MANOVA, RSM, GRA, DFA, MRA"
if errorlevel 1 (
    echo UYARI: Commit atlandi - belki degisiklik yok.
)
echo.

echo [5/6] Ana dal ayarlaniyor...
git branch -M main
echo.

echo [6/6] GitHub'a gonderiliyor...
git push -u origin main
if errorlevel 1 (
    echo.
    echo HATA: Push basarisiz!
    echo - GitHub hesabiniza giris yaptiginizdan emin olun
    echo - Remote'da mevcut commit varsa su komutu deneyin:
    echo   git pull origin main --allow-unrelated-histories
    echo   git push -u origin main
    pause
    exit /b 1
)

echo.
echo ========================================
echo BASARILI! Kod GitHub'a gonderildi.
echo https://github.com/MEY-26/Advanced-Data-Analysis-Tool
echo ========================================
pause
