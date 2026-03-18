# RSM/ANOVA ve Degisim Analizi GUI Uygulamasi

Talasli imalat operasyonuna ait olcum verilerini Excel'den okuyup, RSM (Response Surface Methodology) / ANOVA ve Degisim Analizi yapan masaustu GUI uygulamasi.

## Kurulum

```bash
pip install -r requirements.txt
```

## Calistirma

```bash
python main.py
```

## Kullanim Senaryosu

1. **Dosya Yukleme**: "FormTester.xlsx Sec" butonu ile Excel dosyasini secin. Sayfa (sheet) secimi dropdown'dan yapilir.
2. **Filtreleme**: Veri tablosu gorunumunde Numune, Delik, Olcum ve Devir/Feed/Paso araliklarina gore filtre uygulayin.
3. **Analiz 1 (RSM)**: Oncesi olcumunu response olarak kullanarak tezgah parametreleri ile iliskiyi modelleyin. ANOVA, residual grafikleri, surface/contour grafikleri goruntulenir.
4. **Analiz 2 (Degisim)**: Sonrasi-Oncesi degisim metriklerini (mutlak, yuzdesel, iyilesme) analiz edin. Grup bazli ozet tablolar ve en cok iyilestiren parametre kombinasyonlari gosterilir.
5. **Disa Aktarma**: Dosya > Disa Aktar ile filtreli veri, analiz sonuclari ve grafikleri Excel veya CSV olarak kaydedin.

## Export Edilen Dosyalar

- **Excel (xlsx)**: Her veri/analiz ayri bir sheet olarak yazilir (Filtered Data, Model Summary, ANOVA, Grup Ozeti vb.)
- **CSV**: Her veri/analiz ayri bir .csv dosyasi olarak kaydedilir
- **Grafikler**: PNG formatinda (residual, QQ, surface, contour, boxplot vb.)

## Beklenen Veri Yapisi

Excel dosyasinda su kolonlar olmali:

| Kolon   | Tip      | Aciklama                    |
|---------|----------|-----------------------------|
| Numune  | int      | Numune kodu                 |
| Delik   | kategori | kafa / flans                |
| Devir   | numerik  | Tezgah parametresi          |
| Feed    | numerik  | Tezgah parametresi          |
| Paso    | numerik  | Tezgah parametresi          |
| Olcum   | kategori | oval / silindir / konik     |
| Oncesi  | numerik  | Operasyon oncesi olcum      |
| Sonrasi | numerik  | Operasyon sonrasi olcum     |

Kolon adlari buyuk/kucuk harf farkli olabilir; uygulama otomatik eslestirir.
