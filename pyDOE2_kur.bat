@echo off
echo pyDOE2 kurulumu...
echo.

REM 1. Windows Python Launcher (py) - genelde calisir
py -3 -m pip install pyDOE2 2>nul
if %errorlevel% equ 0 (
    echo Basarili! py -3 ile kuruldu.
    goto :end
)

REM 2. python komutu
python -m pip install pyDOE2 2>nul
if %errorlevel% equ 0 (
    echo Basarili! python ile kuruldu.
    goto :end
)

REM 3. python3 komutu
python3 -m pip install pyDOE2 2>nul
if %errorlevel% equ 0 (
    echo Basarili! python3 ile kuruldu.
    goto :end
)

echo HATA: Python bulunamadi veya pip calismadi.
echo.
echo Manuel cozum:
echo 1. Cursor'da python_kontrol.py dosyasina sag tiklayip "Run Python File" secin
echo 2. Cikti Python yolunu gosterir - o yolu kullanin
echo 3. Veya: Baslat ^> "python" yazin, Python'un nerede oldugunu gorun
pause

:end
pause
