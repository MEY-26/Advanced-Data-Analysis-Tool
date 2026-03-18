#!/usr/bin/env python3
"""
Data Analysis - EXE oluşturma scripti.
Bu script PyInstaller kullanarak tek dosya .exe üretir.
Kullanım: python build_exe.py
"""

import subprocess
import sys
from pathlib import Path


def create_icon():
    """L2.png'den icon.ico oluşturur (EXE dosyası ikonu için)."""
    png_path = Path("assets/L2.png") if Path("assets/L2.png").exists() else Path("L2.png")
    ico_path = Path("assets/icon.ico")
    if not png_path.exists():
        print("Uyari: L2.png bulunamadi (assets/ veya ana dizin). EXE varsayilan ikonla olusturulacak.")
        return False
    Path("assets").mkdir(exist_ok=True)
    try:
        from PIL import Image
        img = Image.open(png_path)
        img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
        print("Icon.ico olusturuldu.")
        return True
    except ImportError:
        print("Pillow yok. Yukleniyor: pip install Pillow")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image
        img = Image.open(png_path)
        img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
        print("Icon.ico olusturuldu.")
        return True
    except Exception as e:
        print(f"Icon olusturma hatasi: {e}")
        return False


def main():
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller bulunamadi. Yukleniyor: pip install pyinstaller")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    create_icon()

    print("EXE olusturuluyor... (birkaç dakika sürebilir)")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "Data_Analysis.spec", "--noconfirm"],
        cwd=".",
    )
    if result.returncode == 0:
        print("\nTamamlandi! EXE dosyasi: dist/Data_Analysis.exe")
    else:
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
