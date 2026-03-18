# RSM / Değişim Analizi - Kurulum ve Dağıtım Kılavuzu

Bu doküman, uygulamanın başka bir bilgisayarda çalıştırılması için gereken tüm bilgileri içerir.

---

## 1. Gereksinimler (Python ile Çalıştırma)

### Python Sürümü
- **Önerilen:** Python 3.10 veya 3.11
- **Minimum:** Python 3.9
- **Test edilmiş:** Python 3.10, 3.11

### Gerekli Paketler
| Paket | Minimum Sürüm |
|-------|---------------|
| PySide6 | 6.5.0 |
| pandas | 2.0.0 |
| openpyxl | 3.1.0 |
| statsmodels | 0.14.0 |
| scipy | 1.11.0 |
| numpy | 1.24.0 |
| matplotlib | 3.7.0 |

---

## 2. Kurulum Adımları (Python ile)

### Adım 1: Python Kurulumu
1. [python.org](https://www.python.org/downloads/) adresinden Python 3.10 veya 3.11 indirin.
2. Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretleyin.
3. Kurulumu tamamlayın.

### Adım 2: Proje Klasörünü Kopyalayın
Tüm proje dosyalarını (AHGv3 klasörü) hedef bilgisayara kopyalayın.

### Adım 3: Bağımlılıkları Yükleyin
Komut satırında (CMD veya PowerShell) proje klasörüne gidin ve:

```bash
pip install -r requirements.txt
```

### Adım 4: Uygulamayı Çalıştırın
```bash
python main.py
```

---

## 3. EXE Oluşturma (Çift Tıklama ile Çalıştırma)

CMD veya terminal erişimi kısıtlı bilgisayarlarda kullanım için uygulama tek bir `.exe` dosyasına dönüştürülebilir. Bu işlem **geliştirme yapılan bilgisayarda** (Python kurulu olan) yapılır; oluşan `.exe` dosyası başka bilgisayarlara kopyalanabilir.

### Gereksinimler
- Python 3.10 veya 3.11 kurulu
- `requirements.txt` içindeki paketler yüklü
- PyInstaller (build sırasında yüklenecek)

### EXE Oluşturma Adımları

1. Proje klasörüne gidin:
   ```bash
   cd c:\Users\meminyaman\Desktop\AHGv3
   ```

2. PyInstaller'ı yükleyin (bir kez):
   ```bash
   pip install pyinstaller
   ```

3. EXE'yi oluşturun:
   - **Seçenek A:** `EXE_Olustur.bat` dosyasına çift tıklayın (en kolay)
   - **Seçenek B:** Komut satırında `python build_exe.py`
   - **Seçenek C:** `pyinstaller Data_Analysis.spec --noconfirm`

4. Oluşan dosya:
   - **Tek dosya:** `dist/Data_Analysis.exe`
   - Bu `.exe` dosyasını istediğiniz bilgisayara kopyalayıp çift tıklayarak çalıştırabilirsiniz.

### EXE Kullanımı
- `.exe` dosyasına **çift tıklayın** – uygulama açılır.
- CMD, PowerShell veya Python kurulumu **gerekmez**.
- Excel dosyası seçmek için uygulama içindeki "FormTester.xlsx Sec" butonunu kullanın.

---

## 4. Sorun Giderme

### "Python bulunamadı" hatası
- Python kurulumunda "Add to PATH" seçeneğini işaretleyin.
- Bilgisayarı yeniden başlatın.
- Alternatif: `.exe` kullanın (Python gerekmez).

### "Modül bulunamadı" hatası
```bash
pip install -r requirements.txt
```

### EXE açılmıyor veya hata veriyor
- Antivirüs yazılımı `.exe` dosyasını engelliyor olabilir – güvenilir dosya olarak ekleyin.
- `.exe`'yi farklı bir klasöre taşıyıp tekrar deneyin.
- Geliştirme bilgisayarında EXE'yi yeniden oluşturun.

### Excel dosyası açılmıyor
- Dosya `.xlsx` formatında olmalı.
- Beklenen kolonlar: Numune, Delik, Devir, Feed, Paso, Olcum, Oncesi, Sonrasi (büyük/küçük harf farkı kabul edilir).

---

## 5. Dosya Yapısı Özeti

```
AHGv3/
├── main.py              # Ana giriş noktası
├── requirements.txt     # Python bağımlılıkları
├── KURULUM.md           # Bu dosya (kurulum kılavuzu)
├── build_exe.py         # EXE oluşturma scripti
├── RSM_AHG.spec         # PyInstaller yapılandırması
├── EXE_Olustur.bat      # EXE oluşturmak için çift tıklanabilir
├── data_loader.py
├── analysis_rsm.py
├── analysis_delta.py
├── plots.py
├── exporter.py
├── utils.py
└── gui/
    ├── main_window.py
    ├── analysis1_tab.py
    ├── analysis2_tab.py
    ├── data_view.py
    ├── export_dialog.py
    ├── help_tab.py
    └── widgets.py
```

---

## 6. Hızlı Referans

| Senaryo | Komut / İşlem |
|---------|---------------|
| Python ile çalıştırma | `python main.py` |
| EXE oluşturma | `python build_exe.py` |
| EXE ile çalıştırma | `dist/Data_Analysis.exe` dosyasına çift tıklama |
| Bağımlılık kurulumu | `pip install -r requirements.txt` |
