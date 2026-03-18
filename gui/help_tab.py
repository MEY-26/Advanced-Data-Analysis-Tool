"""
Analiz parametreleri aciklama sekmesi - TR/EN.
Detaylı açıklamalar: analizlerin ne olduğu, nasıl çalıştığı, tüm parametreler.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextBrowser,
    QPushButton,
)
from PySide6.QtCore import Qt


HELP_TR = """
<h1>Parametre Açıklamaları — Kapsamlı Rehber</h1>
<p>Bu sekme, uygulamadaki tüm analiz yöntemlerini, parametreleri, kısaltmaları ve kavramları detaylıca açıklar. Her bölüm hem Türkçe hem İngilizce kaynaklara uygun, hatasız ve ayrıntılı bilgi içerir.</p>

<hr><h2>1. Veri Sayfası ve Sütun Ataması</h2>
<h3>Veri Sekmesi (Data Tab)</h3>
<p>Excel dosyanızdan yüklenen ham veriyi tablo halinde gösterir. Sütun başlıkları ve satır numaraları görünür. Veri Kalitesi bölümünde satır sayısı, eksik değerler ve dönüştürülemeyen hücreler raporlanır.</p>

<h3>Sütun Ataması Diyalogu (Column Assignment Dialog)</h3>
<p>Dosya yüklediğinizde açılır. Excel sütunlarınızı analiz rollerine atamanızı sağlar. <b>Mevcut Sütunlar</b> sol tarafta listelenir; her sütunun yanında (numeric) veya (categorical) tipi gösterilir.</p>
<ul>
<li><b>Response (bağımlı değişken)</b>: Ölçülen sonuç değişkeni. Birden fazla eklenebilir (MANOVA için 2+, Delta için Öncesi+Sonrası gerekir).</li>
<li><b>Numerik Faktörler</b>: Sayısal bağımsız değişkenler (devir, feed, paso vb.).</li>
<li><b>Kategorik Faktörler</b>: Metin/kategori değişkenleri (delik, ölçüm vb.). "kafa", "oval" gibi değerler burada olmalı.</li>
<li><b>Kovaryatlar</b>: Kontrol edilecek sürekli değişkenler (ANCOVA için).</li>
<li><b>Blok Değişkenleri</b>: Deney bloklarını temsil eden sütunlar (numune vb.).</li>
</ul>
<p><b>Kullanım:</b> Önce hedef rol kutusuna tıklayın, sonra sol listeden sütuna çift tıklayın veya "Seçileni ata" butonunu kullanın.</p>

<h3>Sütunları Düzenle Butonu</h3>
<p>Veri yüklendikten sonra sol panelde "Sütunları Düzenle" butonu aktif olur. Yeni dosya eklemeden mevcut verinin sütun rollerini değiştirmenizi sağlar. Örneğin Response olarak atadığınız bir kolonu sonradan başka bir role taşıyabilir; diğer atamalar korunur.</p>

<h3>Filtreler</h3>
<p>Sol paneldeki Filtreler bölümü, analiz öncesi veriyi sınırlamanızı sağlar. Kategorik sütunlar için "Tümü" veya belirli bir değer, sayısal sütunlar için Min/Max aralığı seçebilirsiniz. "Filtrele" butonu seçimleri uygular.</p>

<hr><h2>2. One-Way ANOVA (Tek Yönlü Varyans Analizi)</h2>
<h3>Ne Nedir?</h3>
<p>Tek bir kategorik faktörün (örn. delik tipi) bağımlı değişken (örn. ölçüm sonucu) üzerindeki etkisini test eder. Grupların ortalamaları arasında istatistiksel olarak anlamlı fark var mı sorusuna yanıt verir.</p>

<h3>Nasıl Çalışır?</h3>
<p>Veriyi faktör seviyelerine göre gruplara ayırır. Gruplar arası varyansı (faktör etkisi) gruplar içi varyansa (hata) oranlar. Bu oran F-istatistiğidir: <b>F = MS<sub>effect</sub> / MS<sub>error</sub></b>. F büyükse ve p-değeri küçükse (&lt;0.05), gruplar arasında anlamlı fark vardır.</p>

<h3>Parametreler</h3>
<ul>
<li><b>Response</b>: Bağımlı değişken (ölçülen sonuç). Açılır listeden seçilir.</li>
<li><b>Faktör</b>: Grupları oluşturan kategorik değişken (örn. delik, ölçüm).</li>
<li><b>Tukey HSD</b>: Post-hoc test. Hangi grup çiftleri arasında anlamlı fark olduğunu ikili karşılaştırmalarla bulur.</li>
<li><b>Levene (varyans homojenliği)</b>: Grupların varyanslarının eşit olup olmadığını test eder. ANOVA varsayımlarından biridir.</li>
</ul>

<h3>Sonuç Sekmeleri</h3>
<ul>
<li><b>Özet</b>: F, p-değeri, grup ortalamaları, eta-squared (η²).</li>
<li><b>ANOVA</b>: Varyans analizi tablosu (SS, df, MS, F, p).</li>
<li><b>Post-Hoc</b>: Tukey ve Levene sonuçları.</li>
<li><b>Dağılım</b>: Histogram ve kutu grafiği.</li>
<li><b>Uyarılar</b>: Varsayım ihlalleri, düşük serbestlik derecesi vb.</li>
</ul>

<hr><h2>3. Two-Way ANOVA (İki Yönlü Varyans Analizi)</h2>
<h3>Ne Nedir?</h3>
<p>İki faktörün (örn. devir ve feed) bağımlı değişken üzerindeki ana etkilerini ve bu iki faktörün birbirleriyle etkileşimini inceler.</p>

<h3>Nasıl Çalışır?</h3>
<p>Her faktörün ayrı ayrı etkisi (ana etki) ve iki faktörün birlikte etkisi (etkileşim) hesaplanır. Etkileşim anlamlıysa, bir faktörün etkisi diğer faktörün seviyesine göre değişir.</p>

<h3>Parametreler</h3>
<ul>
<li><b>Response</b>: Bağımlı değişken.</li>
<li><b>Faktör 1, Faktör 2</b>: İki kategorik veya sayısal faktör. Sayısal seçilirse C(faktör) ile kategorik gibi işlenir.</li>
<li><b>Etkileşim</b>: Faktör 1 × Faktör 2 etkileşim terimini modele ekler.</li>
<li><b>Tukey HSD, Levene</b>: Post-hoc ve varyans homojenliği testleri.</li>
</ul>

<h3>Sonuç Sekmeleri</h3>
<ul>
<li><b>ANOVA</b>: Ana etkiler ve etkileşim tablosu.</li>
<li><b>Post-Hoc</b>: Tukey ve Levene sonuçları.</li>
<li><b>Main Effects</b>: Ana etki grafikleri.</li>
<li><b>Dağılım</b>: Histogram ve kutu grafiği.</li>
<li><b>Uyarılar</b>: Varsayım ihlalleri.</li>
</ul>

<hr><h2>4. MANOVA (Çok Değişkenli Varyans Analizi)</h2>
<h3>Ne Nedir?</h3>
<p>Birden fazla bağımlı değişkeni aynı anda analiz eder. ANOVA'nın çok değişkenli uzantısıdır. Örn. "oncesi" ve "sonrasi" birlikte incelenebilir.</p>

<h3>Nasıl Çalışır?</h3>
<p>Wilks' Lambda, Pillai izi, Hotelling-Lawley ve Roy test istatistikleri hesaplanır. Bu testler, faktörlerin birden fazla yanıt üzerinde birlikte anlamlı etkisi olup olmadığını değerlendirir.</p>

<h3>Parametreler</h3>
<ul>
<li><b>Response (2+ seçin)</b>: En az 2 bağımlı değişken seçilmelidir. Çoklu seçim listesinden Ctrl ile birden fazla seçin.</li>
<li><b>Faktörler</b>: Bağımsız değişkenler. En az 1 faktör gerekir.</li>
</ul>

<h3>Sonuç Sekmeleri</h3>
<ul>
<li><b>Sonuç</b>: Wilks' Lambda, Pillai, Hotelling-Lawley, Roy test sonuçları.</li>
<li><b>Main Effects</b>: Ana etki grafikleri.</li>
<li><b>Dağılım</b>: Yanıt dağılımları.</li>
<li><b>Uyarılar</b>: Varsayım ihlalleri.</li>
</ul>

<hr><h2>5. ANCOVA (Kovaryans Analizi)</h2>
<h3>Ne Nedir?</h3>
<p>Kategorik faktörlerin etkisini, sürekli kovaryatları (confounding variables) kontrol ederek inceler. Örn. yaş veya başlangıç değeri gibi değişkenlerin etkisini çıkarıp, sadece faktör etkisini test eder.</p>

<h3>Nasıl Çalışır?</h3>
<p>Kovaryatlar regresyonla modele eklenir; faktör etkileri bu kovaryatlar "sabit tutulduğunda" hesaplanır.</p>

<h3>Parametreler</h3>
<ul>
<li><b>Response</b>: Bağımlı değişken (tek seçim).</li>
<li><b>Faktörler</b>: Kategorik bağımsız değişkenler (çoklu seçim).</li>
<li><b>Kovaryatlar</b>: Kontrol edilecek sürekli değişkenler (çoklu seçim). En az 1 kovaryat gerekir.</li>
<li><b>Tukey HSD, Levene</b>: Post-hoc ve varyans homojenliği testleri.</li>
</ul>

<h3>Sonuç Sekmeleri</h3>
<ul>
<li><b>ANOVA</b>: Kovaryat ve faktör etkileri tablosu.</li>
<li><b>Post-Hoc</b>: Tukey ve Levene sonuçları.</li>
<li><b>Main Effects</b>: Ana etki grafikleri.</li>
<li><b>Dağılım</b>: Yanıt dağılımı.</li>
<li><b>Uyarılar</b>: Varsayım ihlalleri.</li>
</ul>

<hr><h2>6. GRA (Gray Relational Analysis — Gri İlişkisel Analiz)</h2>
<h3>Ne Nedir?</h3>
<p>Referans seriye (ideal veya hedef profil) en yakın alternatifleri sıralayan bir karar destek yöntemidir. Çok kriterli karar vermede kullanılır.</p>

<h3>Nasıl Çalışır?</h3>
<p>1) Referans ve karşılaştırma serileri seçilir. 2) Veriler 0–1 aralığına normalize edilir. <b>Büyük daha iyi:</b> x' = (x − min) / (max − min). <b>Küçük daha iyi:</b> x' = (max − x) / (max − min). 3) Gray relational coefficient hesaplanır: <b>ξ<sub>i</sub>(k) = (Δ<sub>min</sub> + ρ·Δ<sub>max</sub>) / (Δ<sub>0i</sub>(k) + ρ·Δ<sub>max</sub>)</b>, burada Δ<sub>0i</sub>(k) referans ile i. serinin k. gözlemindeki mutlak farktır. 4) Grade (ortalama katsayı) hesaplanır. 5) Alternatifler grade'e göre sıralanır.</p>

<h3>Parametreler</h3>
<ul>
<li><b>Referans seri</b>: İdeal veya hedef olarak alınacak sütun. Tek seçim.</li>
<li><b>Karşılaştırma serileri</b>: Referansla karşılaştırılacak sütunlar. Çoklu seçim; referans hariç.</li>
<li><b>Büyük daha iyi / Küçük daha iyi</b>: Normalizasyon yönü. "Büyük daha iyi" seçilirse yüksek değerler tercih edilir.</li>
<li><b>Distinguishing coefficient (ρ)</b>: 0.01–1.0 arası. Gray relational coefficient formülünde kullanılır. Düşük ρ daha fazla ayırt etme sağlar. Varsayılan 0.5.</li>
</ul>

<h3>Sonuç Sekmeleri</h3>
<ul>
<li><b>Sıralama</b>: Grade değerine göre sıralanmış alternatifler.</li>
<li><b>Grade Grafiği</b>: Grade değerlerinin görselleştirmesi.</li>
<li><b>Normalize Veri</b>: 0–1 aralığına normalize edilmiş veri tablosu.</li>
<li><b>Katsayı Matrisi</b>: Gray relational coefficient matrisi.</li>
</ul>

<hr><h2>7. DFA (Discriminant Function Analysis — Ayırıcı Fonksiyon Analizi)</h2>
<h3>Ne Nedir?</h3>
<p>Kategorik grupları (sınıfları) ayırt etmek için numerik özellikleri kullanan bir sınıflandırma yöntemidir. Linear Discriminant Analysis (LDA) ile gruplar arasındaki farkı maksimize eden doğrusal birleşimler bulunur.</p>

<h3>Nasıl Çalışır?</h3>
<p>sklearn LinearDiscriminantAnalysis kullanılır. Özellik uzayında gruplar arası varyansı maksimize, gruplar içi varyansı minimize eden discriminant fonksiyonları hesaplanır. Wilks' Lambda (1 − açıklanan varyans oranı toplamı) gruplar arası ayrımın gücünü ölçer.</p>

<h3>Parametreler</h3>
<ul>
<li><b>Grup değişkeni</b>: Sınıfları tanımlayan kategorik sütun (örn. delik tipi). Az sayıda benzersiz değer içermeli; gözlem sayısı sınıf sayısından fazla olmalıdır.</li>
<li><b>Özellik değişkenleri</b>: Sınıflandırmada kullanılacak numerik sütunlar (çoklu seçim). Grup değişkeni özellik olarak seçilemez.</li>
</ul>

<h3>Sonuç Sekmeleri</h3>
<ul>
<li><b>Özet</b>: Doğruluk, Wilks Lambda, eigenvalue (açıklanan varyans oranı), sınıflandırma raporu.</li>
<li><b>Sınıflandırma</b>: Confusion matrix (gerçek vs tahmin edilen sınıflar).</li>
<li><b>Katsayılar</b>: Discriminant fonksiyon katsayıları (LD1, LD2, ...) ve intercept.</li>
<li><b>Skor Grafiği</b>: Discriminant skorlarının 2D dağılımı.</li>
<li><b>Uyarılar</b>: Düşük gözlem sayısı vb.</li>
</ul>

<hr><h2>8. MRA (Multiple Regression Analysis — Çoklu Regresyon Analizi)</h2>
<h3>Ne Nedir?</h3>
<p>Bir bağımlı değişkeni birden fazla bağımsız değişkene (predictor) OLS (En Küçük Kareler) regresyonu ile bağlayan yöntemdir. Y = β<sub>0</sub> + β<sub>1</sub>X<sub>1</sub> + ... + β<sub>p</sub>X<sub>p</sub> + ε modeli kurulur.</p>

<h3>Nasıl Çalışır?</h3>
<p>statsmodels OLS ile model tahmin edilir. R² = 1 − SS<sub>res</sub>/SS<sub>total</sub>, Adj. R² = 1 − (1−R²)(n−1)/(n−p−1). ANOVA ile model anlamlılığı, VIF ile çoklu doğrusal bağımlılık kontrol edilir.</p>

<h3>Parametreler</h3>
<ul>
<li><b>Response</b>: Bağımlı değişken. Tek seçim.</li>
<li><b>Predictor'lar</b>: Bağımsız değişkenler (çoklu seçim). Response hariç en az 1 predictor gerekir.</li>
<li><b>Etkileşimler</b>: İkili etkileşim terimlerini (X<sub>1</sub>×X<sub>2</sub> vb.) modele ekler. Varsayılan: kapalı.</li>
</ul>

<h3>Sonuç Sekmeleri</h3>
<ul>
<li><b>Model Özeti</b>: OLS sonuçları, R², Adj. R², katsayılar, t, p.</li>
<li><b>ANOVA</b>: Model anlamlılık tablosu.</li>
<li><b>Katsayılar</b>: Regresyon katsayıları tablosu.</li>
<li><b>VIF</b>: Variance Inflation Factor. Çoklu doğrusal bağımlılık.</li>
<li><b>Residual Plots</b>: Artıklar vs fitted, Q-Q plot.</li>
<li><b>Dağılım</b>: Response dağılımı.</li>
<li><b>Uyarılar</b>: Varsayım ihlalleri.</li>
</ul>

<hr><h2>9. RSM (Response Surface Methodology — Yanıt Yüzeyi Metodolojisi)</h2>
<h3>Ne Nedir?</h3>
<p>Faktörler ile yanıt arasındaki ilişkiyi ikinci derece polinomla modelleyen bir optimizasyon yöntemidir. En iyi faktör ayarlarını bulmak için kullanılır.</p>

<h3>Nasıl Çalışır?</h3>
<p>OLS regresyonu ile yanıt = f(faktörler) modeli kurulur. Ana etkiler, ikili etkileşimler ve karesel terimler eklenebilir. ANOVA ile terimlerin anlamlılığı test edilir. 3D yüzey ve kontur grafikleri ile optimum bölge görselleştirilir.</p>

<h3>Parametreler</h3>
<ul>
<li><b>Response</b>: Modelenecek bağımlı değişken.</li>
<li><b>Faktörler (numerik)</b>: Ana etkiler için numerik faktörler (çoklu seçim).</li>
<li><b>Ana etkiler</b>: Faktörlerin doğrusal terimleri.</li>
<li><b>İkili etkileşimler</b>: devir×feed, devir×paso, feed×paso gibi çapraz terimler.</li>
<li><b>Karesel terimler</b>: devir², feed², paso². Eğriliği yakalar.</li>
<li><b>Coded Values Kullan</b>: Evrensel kodlama. Formül: <b>X<sub>kodlu</sub> = (X<sub>gerçek</sub> − X<sub>orta</sub>) / ((X<sub>max</sub> − X<sub>min</sub>)/2)</b>, X<sub>orta</sub> = (X<sub>max</sub> + X<sub>min</sub>)/2. Faktörler [-1, +1] aralığına ölçeklenir.</li>
<li><b>Delik, Ölçüm, Numune (block)</b>: Kategorik blok değişkenleri.</li>
<li><b>Aykırı değerleri analiz dışında bırak</b>: IQR veya Z-score ile tespit edilen aykırıları çıkarır.</li>
<li><b>Yöntem (IQR / Z-score)</b>: Aykırı tespit yöntemi.</li>
<li><b>Type II / Type III</b>: ANOVA tipi.</li>
<li><b>Faktör 1, Faktör 2, Sabit faktör (3.)</b>: 3D yüzey grafiği için eksenler ve sabitlenen faktör değeri.</li>
</ul>

<h3>Sonuç Sekmeleri</h3>
<ul>
<li><b>Model Özeti</b>: OLS sonuçları, R², katsayılar.</li>
<li><b>ANOVA</b>: Terim bazlı F ve p-değerleri.</li>
<li><b>VIF</b>: Çoklu doğrusal bağımlılık.</li>
<li><b>Residual Plots</b>: Artıklar vs fitted, Q-Q plot.</li>
<li><b>Surface/Contour</b>: 3D yüzey ve kontur grafikleri.</li>
<li><b>Korelasyon</b>: Faktörler arası Pearson korelasyon matrisi.</li>
<li><b>Main Effects</b>: Ana etki grafikleri.</li>
<li><b>Dağılım</b>: Histogram ve dağılım grafikleri.</li>
<li><b>Coded/Real</b>: Kodlanmış ve gerçek değer tabloları.</li>
</ul>

<hr><h2>10. DOE (Design of Experiments — Deney Tasarımı)</h2>
<h3>Ne Nedir?</h3>
<p>Faktöriyel deney tasarımları oluşturur. Full Factorial, Fractional Factorial, CCD, Box-Behnken, D-Optimal ve I-Optimal tasarımlar desteklenir.</p>

<h3>Tasarım Tipleri</h3>
<ul>
<li><b>Full Factorial</b>: Tüm faktör seviyelerinin tüm kombinasyonları. Seviye sayısı her faktör için ayrı belirtilir (2, 3, 4 vb.).</li>
<li><b>Fractional Factorial</b>: 2 seviyeli kesirli tasarım. Ana etkilerin bir kısmı etkileşimlerle karışır (confounding); deney sayısı azalır.</li>
<li><b>CCD (Central Composite Design)</b>: Faktöriyel blok + yıldız noktaları + merkez. <b>Alpha</b>: orthogonal (faktöriyel blok ile yıldız noktaları ilişkisiz) veya rotatable (tahmin varyansı açıdan eşit). <b>Face</b>: circumscribed (yıldızlar faktör uzayı dışında), inscribed, faced. <b>Merkez factorial, Merkez star</b>: Merkez nokta sayıları (varsayılan 4, 4).</li>
<li><b>Box-Behnken</b>: 3 seviyeli (-1, 0, +1) yanıt yüzeyi tasarımı. En az 3 faktör gerekir. Köşe noktaları kullanmaz.</li>
<li><b>D-Optimal</b>: det(X'X) maksimize edilir. Verilen deney sayısında en iyi bilgi sağlayan nokta seti. <b>Deney sayısı</b> kullanıcı tarafından belirtilir.</li>
<li><b>I-Optimal</b>: Tahminin ortalama varyansını minimize eder. Ön tahmin odaklı tasarım.</li>
</ul>

<h3>Faktör Tanım Tablosu</h3>
<p><b>Faktör Adı</b>: Faktör sütun adı. Veri yüklendiğinde numeric_factors otomatik doldurulur.</p>
<p><b>Min, Max</b>: Gerçek ölçekte faktör aralığı. Kodlanmış tasarım bu aralığa decode edilir.</p>
<p><b>Seviye</b>: Full Factorial için her faktörün seviye sayısı. Diğer tasarımlar için 2 veya 3 seviyeli.</p>
<p><b>Faktör Ekle / Faktör Sil</b>: Tabloya yeni faktör ekler veya seçili satırı siler.</p>

<h3>Sonuç Sekmeleri</h3>
<ul>
<li><b>Tasarım Matrisi (Kodlanmış)</b>: -1, 0, +1 kodlu tasarım tablosu.</li>
<li><b>Tasarım Matrisi (Gerçek)</b>: Min/Max aralığına çevrilmiş gerçek değerler.</li>
<li><b>Tasarım Özeti</b>: Deney sayısı, faktör bilgileri. Excel'e Aktar butonu ile tasarımı Excel'e kaydedebilirsiniz.</li>
</ul>

<hr><h2>11. Delta (Değişim Analizi)</h2>
<h3>Ne Nedir?</h3>
<p>Öncesi–Sonrası ölçümler arasındaki farkı hesaplayan ve bu farkı (Delta) yanıt olarak RSM ile modelleyen analizdir. İyileştirme veya değişim miktarını faktörlere göre inceler.</p>

<h3>Nasıl Çalışır?</h3>
<p>1) Öncesi ve Sonrası kolonlarından Delta hesaplanır (metrik seçimine göre). 2) İsteğe bağlı duplikat birleştirme. 3) Delta, RSM modelinde yanıt olarak kullanılır. 4) Grup özetleri, ANOVA, yüzey grafikleri üretilir.</p>

<h3>Parametreler</h3>
<ul>
<li><b>Öncesi (Before), Sonrası (After)</b>: Karşılaştırılacak ölçüm kolonları.</li>
<li><b>Metrik</b>: <b>absolute</b> = Sonrası − Öncesi. <b>percent</b> = ((Sonrası−Öncesi)/Öncesi)×100. <b>improvement</b> = İyileşme yönüne göre fark.</li>
<li><b>Küçük daha iyi / Büyük daha iyi</b>: İyileşme yönü. "Küçük daha iyi" seçilirse Delta = Öncesi − Sonrası.</li>
<li><b>Öncesi=0 İşlemi</b>: <b>nan</b> = NaN atanır. <b>0</b> = 0 kabul edilir.</li>
<li><b>Hepsini tut / Ortalama ile birleştir</b>: Duplikat işleme.</li>
<li><b>Faktörler (numerik)</b>: RSM'de kullanılacak faktörler.</li>
<li><b>Etkileşimler, Karesel, Delik, Ölçüm</b>: RSM model terimleri.</li>
<li><b>Faktör 1, Faktör 2</b>: Yüzey grafiği eksenleri.</li>
</ul>

<h3>Sonuç Sekmeleri</h3>
<ul>
<li><b>Model Özeti</b>: RSM model sonuçları.</li>
<li><b>ANOVA</b>: Delta modeli ANOVA tablosu.</li>
<li><b>Grup Özeti</b>: Faktör gruplarına göre Delta ortalaması, std, n.</li>
<li><b>Delta Dağılımı</b>: Delta histogramı.</li>
<li><b>Surface</b>: 3D yüzey grafiği.</li>
<li><b>Main Effects</b>: Ana etki grafikleri.</li>
</ul>

<hr><h2>12. Lack of Fit (Uyum Eksikliği)</h2>
<p>One-Way ANOVA ve RSM'de, artıkların kareler toplamı (SS<sub>res</sub>) iki bileşene ayrılır: <b>SS<sub>pure error</sub></b> (tekrarlı noktalardan gelen saf hata) ve <b>SS<sub>lack of fit</sub></b> (model uyum eksikliği). F = MS<sub>lof</sub> / MS<sub>pe</sub> ile test edilir. p&lt;0.05 ise model yetersiz (lack of fit anlamlı).</p>

<hr><h2>13. Post-Hoc Testler</h2>
<ul>
<li><b>Tukey HSD (Honestly Significant Difference)</b>: Grup ortalamaları arasındaki tüm ikili karşılaştırmaları yapar. Hangi çiftler arasında anlamlı fark olduğunu belirler. Aile-bazlı hata oranını (family-wise error rate) kontrol eder. q = (ȳ<sub>i</sub> − ȳ<sub>j</sub>) / √(MS<sub>error</sub>/n).</li>
<li><b>Levene Testi</b>: Varyans homojenliği testi. Grupların varyanslarının eşit olup olmadığını test eder. p&gt;0.05 ise varyanslar homojen kabul edilir. ANOVA varsayımlarından biridir.</li>
</ul>

<hr><h2>14. Aykırı Değer (Outlier) Yöntemleri</h2>
<ul>
<li><b>IQR (Interquartile Range)</b>: Q1 ve Q3 (1. ve 3. çeyrek) hesaplanır. IQR = Q3−Q1. <b>Alt sınır:</b> Q1 − 1.5×IQR. <b>Üst sınır:</b> Q3 + 1.5×IQR. Bu aralık dışındaki değerler aykırı kabul edilir.</li>
<li><b>Z-score</b>: Her değer için <b>z = (x − μ) / σ</b> hesaplanır. |z|&gt;3 ise aykırı (ortalama ± 3 standart sapma dışı).</li>
</ul>

<hr><h2>15. Main Effects Plots (Ana Etki Grafikleri)</h2>
<p>Her faktörün seviyeleri (x ekseni) ile yanıt ortalaması (y ekseni) gösterilir. Faktörün yanıt üzerindeki etkisinin yönü ve büyüklüğü görselleştirilir. Düz çizgi = etki yok; eğimli çizgi = etki var.</p>

<hr><h2>16. Residual Plots (Artık Grafikleri)</h2>
<ul>
<li><b>Artıklar vs Fitted</b>: Tahmin edilen değerler (x) ile artıklar (y). Rastgele dağılım beklenir; huni şekli heteroscedasticity gösterir.</li>
<li><b>Q-Q Plot</b>: Artıkların teorik normal dağılıma uyumu. Çizgi üzerinde noktalar = normal dağılım.</li>
</ul>

<hr><h2>17. Korelasyon Matrisi</h2>
<p>Faktörler (ve isteğe bağlı response) arasındaki Pearson korelasyon katsayıları (r). r ∈ [-1, 1]. |r|&gt;0.7 yüksek korelasyon; çoklu doğrusal bağımlılık riski.</p>

<hr><h2>18. Tablo Kısaltmaları ve Terimler</h2>
<ul>
<li><b>SS / sum_sq</b>: Kareler toplamı (Sum of Squares).</li>
<li><b>df</b>: Serbestlik derecesi (degrees of freedom).</li>
<li><b>MS</b>: Ortalama kareler (Mean Square) = SS/df.</li>
<li><b>F</b>: F-istatistiği = MS<sub>effect</sub> / MS<sub>error</sub>.</li>
<li><b>p, PR(&gt;F), P&gt;|t|</b>: p-değeri.</li>
<li><b>SE</b>: Standart hata (Standard Error).</li>
<li><b>R²</b>: R² = 1 − SS<sub>res</sub>/SS<sub>total</sub>. Adj. R² = 1 − (1−R²)(n−1)/(n−p−1).</li>
<li><b>AIC, BIC</b>: Model karşılaştırma kriterleri. Düşük değer daha iyi.</li>
<li><b>VIF</b>: VIF<sub>j</sub> = 1 / (1 − R<sub>j</sub>²). R<sub>j</sub>² = j. değişkenin diğerleriyle regresyonundan R².</li>
<li><b>coef</b>: Regresyon katsayısı.</li>
<li><b>t</b>: t-istatistiği = coef / SE.</li>
<li><b>Dep. Variable</b>: Bağımlı değişken.</li>
<li><b>Df Residuals</b>: Hata serbestlik derecesi.</li>
<li><b>Cond. No.</b>: Koşul sayısı. Yüksekse sayısal hassasiyet sorunu.</li>
<li><b>Omnibus, Jarque-Bera</b>: Normallik testleri.</li>
<li><b>Durbin-Watson</b>: Otokorelasyon. 1.5–2.5 aralığı kabul edilir.</li>
<li><b>eta-squared (η²)</b>: Etki büyüklüğü. η² = SS<sub>effect</sub> / SS<sub>total</sub>.</li>
</ul>

<hr><h2>19. Anlamlılık Seviyeleri</h2>
<ul>
<li><b>***</b>: p&lt;0.001 (çok anlamlı)</li>
<li><b>**</b>: p&lt;0.01 (anlamlı)</li>
<li><b>*</b>: p&lt;0.05 (anlamlı)</li>
<li><b>p≥0.05</b>: Anlamlı değil (H0 reddedilemez)</li>
</ul>

<hr><h2>20. VIF Yorumu</h2>
<ul>
<li><b>VIF&lt;5</b>: Kabul edilebilir.</li>
<li><b>VIF 5–10</b>: Orta düzey; dikkat.</li>
<li><b>VIF&gt;10</b>: Yüksek multicollinearity; değişken çıkarımı veya PCA düşünülebilir.</li>
<li><b>VIF=∞</b>: Tam çoklu doğrusal bağımlılık.</li>
</ul>

<hr><h2>21. Dağılım İstatistikleri</h2>
<ul>
<li><b>skewness</b>: Çarpıklık. 0=simetrik, &gt;0 sağa çarpık, &lt;0 sola çarpık.</li>
<li><b>kurtosis</b>: Basıklık. Normal dağılımda ~3.</li>
<li><b>Shapiro-Wilk p</b>: Normallik testi. p&gt;0.05 ise normal kabul edilir.</li>
</ul>

<hr><h2>22. ANOVA Type II vs Type III</h2>
<ul>
<li><b>Type II</b>: Sıralı SS (Sequential). Her terim, kendisinden önce gelenleri kontrol ederek test edilir. Dengeli tasarımlar için uygun.</li>
<li><b>Type III</b>: Kısmi SS (Partial). Her terim diğer tüm terimleri kontrol ederek test edilir. Dengesiz tasarımlar ve etkileşimli modeller için genelde tercih edilir.</li>
</ul>

<hr><h2>23. Dışa Aktarma</h2>
<p>Dosya → Dışa Aktar ile filtrelenmiş veri, analiz sonuçları (ANOVA, VIF, grup özetleri vb.) Excel veya CSV olarak kaydedilebilir. Her analiz türü için ilgili sonuçlar seçilebilir.</p>

<hr><p><i>Bu rehber, uygulamadaki tüm analiz yöntemlerini ve parametreleri kapsar. Kaynak: statsmodels, scikit-learn, Deng (1989) Gray relational analysis, Box &amp; Wilson (1951) RSM.</i></p>
"""

HELP_EN = """
<h1>Parameter Descriptions — Comprehensive Guide</h1>
<p>This tab explains all analysis methods, parameters, abbreviations, and concepts in detail. Each section is accurate, source-based, and comprehensive in both Turkish and English.</p>

<hr><h2>1. Data Page and Column Assignment</h2>
<h3>Data Tab</h3>
<p>Displays the raw data loaded from your Excel file in tabular form. The Data Quality section reports row count, missing values, and cells that could not be converted.</p>

<h3>Column Assignment Dialog</h3>
<p>Opens when you load a file. Lets you assign Excel columns to analysis roles. <b>Available Columns</b> are listed on the left; each shows (numeric) or (categorical) type.</p>
<ul>
<li><b>Response (dependent variable)</b>: The measured outcome. Multiple can be added (MANOVA requires 2+, Delta requires Before+After).</li>
<li><b>Numeric Factors</b>: Numeric independent variables (speed, feed, step, etc.).</li>
<li><b>Categorical Factors</b>: Text/category variables (hole type, measurement, etc.). Values like "head", "oval" belong here.</li>
<li><b>Covariates</b>: Continuous variables to control for (ANCOVA).</li>
<li><b>Block Variables</b>: Columns representing experiment blocks (sample, etc.).</li>
</ul>
<p><b>Usage:</b> Click the target role box first, then double-click a column or use "Assign Selected".</p>

<h3>Edit Columns Button</h3>
<p>After data is loaded, the "Sütunları Düzenle" (Edit Columns) button in the left panel becomes active. It lets you change column roles for the loaded data without loading a new file. For example, you can move a column from Response to another role; other assignments are preserved.</p>

<h3>Filters</h3>
<p>The Filters section limits data before analysis. Choose "All" or specific values for categorical columns, Min/Max ranges for numeric columns. "Filter" applies the selection.</p>

<hr><h2>2. One-Way ANOVA</h2>
<h3>What Is It?</h3>
<p>Tests the effect of a single categorical factor (e.g., hole type) on a dependent variable (e.g., measurement result). Answers whether group means differ significantly.</p>

<h3>How It Works</h3>
<p>Splits data by factor levels. Compares between-group variance (factor effect) to within-group variance (error). This ratio is the F-statistic: <b>F = MS<sub>effect</sub> / MS<sub>error</sub></b>. Large F and small p (&lt;0.05) indicate significant differences.</p>

<h3>Parameters</h3>
<ul>
<li><b>Response</b>: Dependent variable. Selected from dropdown.</li>
<li><b>Factor</b>: Categorical variable defining groups.</li>
<li><b>Tukey HSD</b>: Post-hoc test. Identifies which group pairs differ significantly.</li>
<li><b>Levene (homogeneity of variance)</b>: Tests whether group variances are equal. An ANOVA assumption.</li>
</ul>

<h3>Result Tabs</h3>
<ul>
<li><b>Summary</b>: F, p-value, group means, eta-squared (η²).</li>
<li><b>ANOVA</b>: Variance analysis table (SS, df, MS, F, p).</li>
<li><b>Post-Hoc</b>: Tukey and Levene results.</li>
<li><b>Distribution</b>: Histogram and box plot.</li>
<li><b>Warnings</b>: Assumption violations, low degrees of freedom, etc.</li>
</ul>

<hr><h2>3. Two-Way ANOVA</h2>
<h3>What Is It?</h3>
<p>Examines main effects of two factors and their interaction on the dependent variable.</p>

<h3>How It Works</h3>
<p>Computes each factor's effect and the interaction. A significant interaction means one factor's effect depends on the other's level.</p>

<h3>Parameters</h3>
<ul>
<li><b>Response</b>: Dependent variable.</li>
<li><b>Factor 1, Factor 2</b>: Two categorical or numeric factors. Numeric factors are treated as categorical via C(factor).</li>
<li><b>Interaction</b>: Include Factor1×Factor2 in the model.</li>
<li><b>Tukey HSD, Levene</b>: Post-hoc and homogeneity of variance tests.</li>
</ul>

<h3>Result Tabs</h3>
<ul>
<li><b>ANOVA</b>: Main effects and interaction table.</li>
<li><b>Post-Hoc</b>: Tukey and Levene results.</li>
<li><b>Main Effects</b>: Main effect plots.</li>
<li><b>Distribution</b>: Histogram and box plot.</li>
<li><b>Warnings</b>: Assumption violations.</li>
</ul>

<hr><h2>4. MANOVA (Multivariate Analysis of Variance)</h2>
<h3>What Is It?</h3>
<p>Analyzes multiple dependent variables simultaneously. Multivariate extension of ANOVA.</p>

<h3>How It Works</h3>
<p>Computes Wilks' Lambda, Pillai's trace, Hotelling-Lawley, and Roy statistics to test whether factors have a joint effect on the responses.</p>

<h3>Parameters</h3>
<ul>
<li><b>Response (2+ required)</b>: At least 2 dependent variables. Use Ctrl for multi-select.</li>
<li><b>Factors</b>: Independent variables. At least 1 required.</li>
</ul>

<h3>Result Tabs</h3>
<ul>
<li><b>Result</b>: Wilks' Lambda, Pillai, Hotelling-Lawley, Roy test results.</li>
<li><b>Main Effects</b>: Main effect plots.</li>
<li><b>Distribution</b>: Response distributions.</li>
<li><b>Warnings</b>: Assumption violations.</li>
</ul>

<hr><h2>5. ANCOVA (Analysis of Covariance)</h2>
<h3>What Is It?</h3>
<p>Tests categorical factor effects while controlling for continuous covariates (confounding variables).</p>

<h3>How It Works</h3>
<p>Covariates are included in the model; factor effects are estimated with covariates held constant.</p>

<h3>Parameters</h3>
<ul>
<li><b>Response</b>: Single dependent variable.</li>
<li><b>Factors</b>: Categorical independent variables (multi-select).</li>
<li><b>Covariates</b>: Continuous variables to control (multi-select). At least 1 required.</li>
<li><b>Tukey HSD, Levene</b>: Post-hoc and homogeneity tests.</li>
</ul>

<h3>Result Tabs</h3>
<ul>
<li><b>ANOVA</b>: Covariate and factor effects table.</li>
<li><b>Post-Hoc</b>: Tukey and Levene results.</li>
<li><b>Main Effects</b>: Main effect plots.</li>
<li><b>Distribution</b>: Response distribution.</li>
<li><b>Warnings</b>: Assumption violations.</li>
</ul>

<hr><h2>6. GRA (Gray Relational Analysis)</h2>
<h3>What Is It?</h3>
<p>Ranks alternatives by similarity to a reference (ideal) series. Used in multi-criteria decision making.</p>

<h3>How It Works</h3>
<p>1) Select reference and comparison series. 2) Normalize to 0–1. <b>Larger better:</b> x' = (x − min) / (max − min). <b>Smaller better:</b> x' = (max − x) / (max − min). 3) Gray relational coefficient: <b>ξ<sub>i</sub>(k) = (Δ<sub>min</sub> + ρ·Δ<sub>max</sub>) / (Δ<sub>0i</sub>(k) + ρ·Δ<sub>max</sub>)</b>, where Δ<sub>0i</sub>(k) is the absolute difference between reference and series i at observation k. 4) Compute grade (mean coefficient). 5) Rank by grade.</p>

<h3>Parameters</h3>
<ul>
<li><b>Reference series</b>: Ideal/target column. Single selection.</li>
<li><b>Comparison series</b>: Columns to compare (exclude reference). Multi-select.</li>
<li><b>Larger better / Smaller better</b>: Normalization direction.</li>
<li><b>Distinguishing coefficient (ρ)</b>: 0.01–1.0. Lower ρ increases discrimination. Default 0.5.</li>
</ul>

<h3>Result Tabs</h3>
<ul>
<li><b>Ranking</b>: Alternatives ranked by grade.</li>
<li><b>Grade Chart</b>: Grade values visualization.</li>
<li><b>Normalized Data</b>: Data normalized to 0–1 range.</li>
<li><b>Coefficient Matrix</b>: Gray relational coefficient matrix.</li>
</ul>

<hr><h2>7. DFA (Discriminant Function Analysis)</h2>
<h3>What Is It?</h3>
<p>A classification method that uses numeric features to discriminate among categorical groups (classes). Linear Discriminant Analysis (LDA) finds linear combinations that maximize between-group variance and minimize within-group variance.</p>

<h3>How It Works</h3>
<p>Uses sklearn LinearDiscriminantAnalysis. Discriminant functions are computed. Wilks' Lambda (1 − sum of explained variance ratios) measures separation strength. Number of samples must exceed number of classes.</p>

<h3>Parameters</h3>
<ul>
<li><b>Group variable</b>: Categorical column defining classes (e.g., hole type). Should have few unique values; sample count must exceed class count.</li>
<li><b>Feature variables</b>: Numeric columns for classification (multi-select). Group variable cannot be a feature.</li>
</ul>

<h3>Result Tabs</h3>
<ul>
<li><b>Summary</b>: Accuracy, Wilks Lambda, eigenvalue (explained variance ratio), classification report.</li>
<li><b>Classification</b>: Confusion matrix (actual vs predicted classes).</li>
<li><b>Coefficients</b>: Discriminant function coefficients (LD1, LD2, ...) and intercept.</li>
<li><b>Score Plot</b>: 2D distribution of discriminant scores.</li>
<li><b>Warnings</b>: Low sample count, etc.</li>
</ul>

<hr><h2>8. MRA (Multiple Regression Analysis)</h2>
<h3>What Is It?</h3>
<p>Links one dependent variable to multiple independent variables (predictors) via OLS (Ordinary Least Squares) regression. Model: Y = β<sub>0</sub> + β<sub>1</sub>X<sub>1</sub> + ... + β<sub>p</sub>X<sub>p</sub> + ε.</p>

<h3>How It Works</h3>
<p>Model estimated with statsmodels OLS. R² = 1 − SS<sub>res</sub>/SS<sub>total</sub>, Adj. R² = 1 − (1−R²)(n−1)/(n−p−1). ANOVA tests model significance; VIF checks multicollinearity.</p>

<h3>Parameters</h3>
<ul>
<li><b>Response</b>: Dependent variable. Single selection.</li>
<li><b>Predictors</b>: Independent variables (multi-select). At least 1 predictor required (excluding response).</li>
<li><b>Interactions</b>: Include pairwise interaction terms (X<sub>1</sub>×X<sub>2</sub>, etc.). Default: off.</li>
</ul>

<h3>Result Tabs</h3>
<ul>
<li><b>Model Summary</b>: OLS results, R², Adj. R², coefficients, t, p.</li>
<li><b>ANOVA</b>: Model significance table.</li>
<li><b>Coefficients</b>: Regression coefficients table.</li>
<li><b>VIF</b>: Variance Inflation Factor.</li>
<li><b>Residual Plots</b>: Residuals vs fitted, Q-Q plot.</li>
<li><b>Distribution</b>: Response distribution.</li>
<li><b>Warnings</b>: Assumption violations.</li>
</ul>

<hr><h2>9. RSM (Response Surface Methodology)</h2>
<h3>What Is It?</h3>
<p>Models the relationship between factors and response with a second-order polynomial. Used for optimization.</p>

<h3>How It Works</h3>
<p>OLS regression fits response = f(factors). Main effects, interactions, and quadratic terms can be included. ANOVA tests term significance. 3D surface and contour plots visualize the optimum region.</p>

<h3>Parameters</h3>
<ul>
<li><b>Response</b>: Variable to model.</li>
<li><b>Factors (numeric)</b>: Numeric factors for main effects (multi-select).</li>
<li><b>Main effects, Interactions, Quadratic</b>: Model terms.</li>
<li><b>Coded Values</b>: Universal coding. Formula: <b>X<sub>coded</sub> = (X<sub>real</sub> − X<sub>mid</sub>) / ((X<sub>max</sub> − X<sub>min</sub>)/2)</b>, X<sub>mid</sub> = (X<sub>max</sub> + X<sub>min</sub>)/2. Factors scaled to [-1, +1].</li>
<li><b>Hole, Measurement, Sample (block)</b>: Categorical block variables.</li>
<li><b>Exclude outliers</b>: Detect and remove outliers via IQR or Z-score.</li>
<li><b>Method (IQR / Z-score)</b>: Outlier detection method.</li>
<li><b>Type II / Type III</b>: ANOVA type.</li>
<li><b>Factor 1, Factor 2, Fixed factor (3.)</b>: Axes and fixed value for 3D surface plot.</li>
</ul>

<h3>Result Tabs</h3>
<ul>
<li><b>Model Summary</b>: OLS results, R², coefficients.</li>
<li><b>ANOVA</b>: Term-wise F and p-values.</li>
<li><b>VIF</b>: Multicollinearity.</li>
<li><b>Residual Plots</b>: Residuals vs fitted, Q-Q plot.</li>
<li><b>Surface/Contour</b>: 3D surface and contour plots.</li>
<li><b>Correlation</b>: Pearson correlation matrix among factors.</li>
<li><b>Main Effects</b>: Main effect plots.</li>
<li><b>Distribution</b>: Histogram and distribution plots.</li>
<li><b>Coded/Real</b>: Coded and real value tables.</li>
</ul>

<hr><h2>10. DOE (Design of Experiments)</h2>
<h3>What Is It?</h3>
<p>Creates factorial experimental designs: Full Factorial, Fractional Factorial, CCD, Box-Behnken, D-Optimal, I-Optimal.</p>

<h3>Design Types</h3>
<ul>
<li><b>Full Factorial</b>: All combinations of factor levels. Level count specified per factor (2, 3, 4, etc.).</li>
<li><b>Fractional Factorial</b>: 2-level fractional design. Some main effects confounded with interactions; fewer runs.</li>
<li><b>CCD (Central Composite Design)</b>: Factorial block + star points + center. <b>Alpha</b>: orthogonal or rotatable. <b>Face</b>: circumscribed, inscribed, faced. <b>Center factorial, Center star</b>: Center point counts (default 4, 4).</li>
<li><b>Box-Behnken</b>: 3-level (-1, 0, +1) response surface design. Minimum 3 factors. No corner points.</li>
<li><b>D-Optimal</b>: Maximizes det(X'X). Best information for given run count. <b>Run count</b> specified by user.</li>
<li><b>I-Optimal</b>: Minimizes average prediction variance.</li>
</ul>

<h3>Factor Table</h3>
<p><b>Factor Name</b>: Column name. Auto-filled from numeric_factors when data is loaded.</p>
<p><b>Min, Max</b>: Real-scale factor range. Coded design decoded to this range.</p>
<p><b>Levels</b>: For Full Factorial, levels per factor. Other designs use 2 or 3 levels.</p>
<p><b>Add Factor / Remove Factor</b>: Add or remove factor rows.</p>

<h3>Result Tabs</h3>
<ul>
<li><b>Design Matrix (Coded)</b>: -1, 0, +1 coded design table.</li>
<li><b>Design Matrix (Real)</b>: Real values in Min/Max range.</li>
<li><b>Design Summary</b>: Run count, factor info. Export to Excel button.</li>
</ul>

<hr><h2>11. Delta (Change Analysis)</h2>
<h3>What Is It?</h3>
<p>Computes Before–After difference (Delta) and models it with RSM. Analyzes improvement/change by factors.</p>

<h3>How It Works</h3>
<p>1) Compute Delta from Before/After columns. 2) Optional duplicate merging. 3) Delta as response in RSM. 4) Group summaries, ANOVA, surface plots.</p>

<h3>Parameters</h3>
<ul>
<li><b>Before, After</b>: Measurement columns to compare.</li>
<li><b>Metric</b>: <b>absolute</b> = After − Before. <b>percent</b> = ((After−Before)/Before)×100. <b>improvement</b> = Difference by improvement direction.</li>
<li><b>Smaller better / Larger better</b>: Improvement direction.</li>
<li><b>Before=0</b>: <b>nan</b> or <b>0</b> when Before is zero.</li>
<li><b>Keep all / Average and merge</b>: Duplicate handling.</li>
<li><b>Factors (numeric)</b>: Factors for RSM.</li>
<li><b>Interactions, Quadratic, Hole, Measurement</b>: RSM model terms.</li>
<li><b>Factor 1, Factor 2</b>: Surface plot axes.</li>
</ul>

<h3>Result Tabs</h3>
<ul>
<li><b>Model Summary</b>: RSM model results.</li>
<li><b>ANOVA</b>: Delta model ANOVA table.</li>
<li><b>Group Summary</b>: Delta mean, std, n by factor groups.</li>
<li><b>Delta Distribution</b>: Delta histogram.</li>
<li><b>Surface</b>: 3D surface plot.</li>
<li><b>Main Effects</b>: Main effect plots.</li>
</ul>

<hr><h2>12. Lack of Fit</h2>
<p>In One-Way ANOVA and RSM, residual sum of squares (SS<sub>res</sub>) is split into <b>SS<sub>pure error</sub></b> (from replicated points) and <b>SS<sub>lack of fit</sub></b> (model inadequacy). Tested via F = MS<sub>lof</sub> / MS<sub>pe</sub>. p&lt;0.05 indicates significant lack of fit (model inadequate).</p>

<hr><h2>13. Post-Hoc Tests</h2>
<ul>
<li><b>Tukey HSD (Honestly Significant Difference)</b>: All pairwise comparisons of group means. Identifies which pairs differ. Controls family-wise error rate. q = (ȳ<sub>i</sub> − ȳ<sub>j</sub>) / √(MS<sub>error</sub>/n).</li>
<li><b>Levene Test</b>: Homogeneity of variance. Tests whether group variances are equal. p&gt;0.05 = homogeneous. An ANOVA assumption.</li>
</ul>

<hr><h2>14. Outlier Methods</h2>
<ul>
<li><b>IQR (Interquartile Range)</b>: Q1 and Q3 computed. IQR = Q3−Q1. <b>Lower bound:</b> Q1 − 1.5×IQR. <b>Upper bound:</b> Q3 + 1.5×IQR. Values outside this range are outliers.</li>
<li><b>Z-score</b>: <b>z = (x − μ) / σ</b> for each value. |z|&gt;3 indicates outlier (outside mean ± 3 standard deviations).</li>
</ul>

<hr><h2>15. Main Effects Plots</h2>
<p>Factor levels (x-axis) vs response mean (y-axis). Visualizes direction and magnitude of each factor's effect. Flat line = no effect; sloped line = effect present.</p>

<hr><h2>16. Residual Plots</h2>
<ul>
<li><b>Residuals vs Fitted</b>: Fitted values (x) vs residuals (y). Random scatter expected; funnel shape indicates heteroscedasticity.</li>
<li><b>Q-Q Plot</b>: Residuals vs theoretical normal. Points on line = normal distribution.</li>
</ul>

<hr><h2>17. Correlation Matrix</h2>
<p>Pearson correlation coefficients (r) among factors (and optionally response). r ∈ [-1, 1]. |r|&gt;0.7 indicates high correlation; multicollinearity risk.</p>

<hr><h2>18. Table Abbreviations and Terms</h2>
<ul>
<li><b>SS / sum_sq</b>: Sum of Squares.</li>
<li><b>df</b>: Degrees of freedom.</li>
<li><b>MS</b>: Mean Square = SS/df.</li>
<li><b>F</b>: F-statistic = MS<sub>effect</sub> / MS<sub>error</sub>.</li>
<li><b>p, PR(&gt;F), P&gt;|t|</b>: p-value.</li>
<li><b>SE</b>: Standard Error.</li>
<li><b>R²</b>: R² = 1 − SS<sub>res</sub>/SS<sub>total</sub>. Adj. R² = 1 − (1−R²)(n−1)/(n−p−1).</li>
<li><b>AIC, BIC</b>: Model comparison criteria. Lower is better.</li>
<li><b>VIF</b>: VIF<sub>j</sub> = 1 / (1 − R<sub>j</sub>²). R<sub>j</sub>² = R² from regressing j on others.</li>
<li><b>coef</b>: Regression coefficient.</li>
<li><b>t</b>: t-statistic = coef / SE.</li>
<li><b>Dep. Variable</b>: Dependent variable.</li>
<li><b>Df Residuals</b>: Residual degrees of freedom.</li>
<li><b>Cond. No.</b>: Condition number. High = numerical precision issues.</li>
<li><b>Omnibus, Jarque-Bera</b>: Normality tests.</li>
<li><b>Durbin-Watson</b>: Autocorrelation. 1.5–2.5 range acceptable.</li>
<li><b>eta-squared (η²)</b>: Effect size. η² = SS<sub>effect</sub> / SS<sub>total</sub>.</li>
</ul>

<hr><h2>19. Significance Levels</h2>
<ul>
<li><b>***</b>: p&lt;0.001 (highly significant)</li>
<li><b>**</b>: p&lt;0.01 (significant)</li>
<li><b>*</b>: p&lt;0.05 (significant)</li>
<li><b>p≥0.05</b>: Not significant (H0 not rejected)</li>
</ul>

<hr><h2>20. VIF Interpretation</h2>
<ul>
<li><b>VIF&lt;5</b>: Acceptable.</li>
<li><b>VIF 5–10</b>: Moderate; caution.</li>
<li><b>VIF&gt;10</b>: High multicollinearity; consider variable removal or PCA.</li>
<li><b>VIF=∞</b>: Perfect multicollinearity.</li>
</ul>

<hr><h2>21. Distribution Statistics</h2>
<ul>
<li><b>skewness</b>: 0=symmetric, &gt;0 right-skewed, &lt;0 left-skewed.</li>
<li><b>kurtosis</b>: Peakedness. Normal ≈ 3.</li>
<li><b>Shapiro-Wilk p</b>: Normality test. p&gt;0.05 = normal.</li>
</ul>

<hr><h2>22. ANOVA Type II vs Type III</h2>
<ul>
<li><b>Type II</b>: Sequential SS. Each term tested controlling for preceding terms. Suitable for balanced designs.</li>
<li><b>Type III</b>: Partial SS. Each term tested controlling for all others. Often preferred for unbalanced designs and models with interactions.</li>
</ul>

<hr><h2>23. Export</h2>
<p>File → Export saves filtered data and analysis results (ANOVA, VIF, group summaries, etc.) to Excel or CSV. Results can be selected per analysis type.</p>

<hr><p><i>This guide covers all analysis methods and parameters in the application. Sources: statsmodels, scikit-learn, Deng (1989) Gray relational analysis, Box &amp; Wilson (1951) RSM.</i></p>
"""


class HelpTab(QWidget):
    """Analiz parametreleri aciklama sekmesi - TR/EN."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        btn_row = QHBoxLayout()
        self.btn_tr = QPushButton("Türkçe")
        self.btn_en = QPushButton("English")
        self.btn_tr.setCheckable(True)
        self.btn_en.setCheckable(True)
        self.btn_tr.setChecked(True)
        self.btn_tr.clicked.connect(lambda: self._set_lang("tr"))
        self.btn_en.clicked.connect(lambda: self._set_lang("en"))
        btn_row.addWidget(self.btn_tr)
        btn_row.addWidget(self.btn_en)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setHtml(HELP_TR)
        layout.addWidget(self.browser)
    
    def _set_lang(self, lang: str) -> None:
        if lang == "tr":
            self.btn_tr.setChecked(True)
            self.btn_en.setChecked(False)
            self.browser.setHtml(HELP_TR)
        else:
            self.btn_tr.setChecked(False)
            self.btn_en.setChecked(True)
            self.browser.setHtml(HELP_EN)
