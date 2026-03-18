#!/usr/bin/env python3
"""
Python ve pyDOE2 kurulum kontrolu.
Bu scripti calistirdiginiz Python, uygulamanin kullandigi Python ile AYNI olmali.
"""
import sys
import subprocess

print("=" * 60)
print("Python Konum Kontrolu")
print("=" * 60)
print(f"Python yolu: {sys.executable}")
print(f"Python versiyonu: {sys.version}")
print()

# pyDOE2 kontrolu
try:
    import pyDOE2
    print("pyDOE2: KURULU")
    print(f"  Konum: {pyDOE2.__file__}")
except ImportError as e:
    print("pyDOE2: KURULU DEGIL")
    print(f"  Hata: {e}")
    print()
    print("Cozum: Asagidaki komutu bu Python ile calistirin:")
    print(f'  "{sys.executable}" -m pip install pyDOE2')
    print()
    print("Veya terminalde:")
    print("  python -m pip install pyDOE2")
    print("  (python = yukaridaki yoldaki ayni Python olmali)")

print()
print("=" * 60)
