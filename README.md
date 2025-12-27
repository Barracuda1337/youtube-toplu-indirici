# 🎵 YouTube Toplu İndirici v3.0

Modern ve kullanıcı dostu arayüz ile YouTube videolarını toplu olarak indiren gelişmiş bir Python uygulaması.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## ✨ Özellikler

- 🎨 **Modern GUI Arayüzü**: Kullanıcı dostu, modern ve sezgisel arayüz
- 📋 **Toplu İndirme**: Birden fazla video/playlist'i aynı anda indirme
- 🎵 **Ses ve Video Desteği**: MP3 (ses) ve MP4 (video) formatlarında indirme
- 🎯 **Kalite Seçenekleri**: Farklı kalite seviyelerinde indirme (4K, 1080p, 720p, vb.)
- ⚡ **Paralel İndirme**: Aynı anda birden fazla video indirme (1-10 arası)
- 🎬 **Playlist Desteği**: Tüm playlist'i tek seferde ekleme
- 🔄 **Otomatik Yeniden Deneme**: Başarısız indirmeleri otomatik olarak yeniden deneme
- 🚦 **Hız Sınırı**: İndirme hızını sınırlama özelliği
- 📊 **Detaylı Log Sistemi**: Gerçek zamanlı indirme logları
- 🎯 **Akıllı Link Yönetimi**: Duplicate kontrolü ve otomatik temizleme
- 📝 **Altyazı Desteği**: Video altyazılarını da indirme seçeneği

## 📋 Gereksinimler

- Python 3.7 veya üzeri
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (otomatik kontrol edilir)
- tkinter (genellikle Python ile birlikte gelir)

## 🚀 Kurulum

### 1. Repository'yi Klonlayın

```bash
git clone https://github.com/Barracuda1337/youtube-toplu-indirici.git
cd youtube-toplu-indirici
```

### 2. yt-dlp'yi Yükleyin

#### Windows (PowerShell):
```powershell
python -m pip install yt-dlp
```

#### Linux/Mac:
```bash
pip3 install yt-dlp
```

Veya [yt-dlp GitHub sayfasından](https://github.com/yt-dlp/yt-dlp) manuel olarak indirebilirsiniz.

### 3. Uygulamayı Çalıştırın

```bash
python youtube_indirici_modern.py
```

## 📖 Kullanım

### Temel Kullanım

1. **Link Ekleme**:
   - YouTube linkini girin ve "➕ Ekle" butonuna tıklayın
   - Veya "📁 Dosyadan Yükle" ile toplu link ekleyin
   - "🎵 Playlist Ekle" ile tüm playlist'i ekleyin

2. **Format Seçimi**:
   - 🎵 **Ses (MP3)**: Sadece ses dosyası
   - 🎬 **Video (MP4)**: Video + ses dosyası

3. **Kalite Ayarları**:
   - Video kalitesi: best, 4K, 1440p, 1080p, 720p, 480p, 360p
   - Ses kalitesi: best, 320k, 192k, 128k

4. **Gelişmiş Ayarlar**:
   - **Paralel İndirme**: Aynı anda kaç video indirileceği (1-10)
   - **Hız Sınırı**: İndirme hızı sınırı (KB/s)
   - **Yeniden Deneme**: Başarısız indirmeler için maksimum deneme sayısı

5. **İndirmeyi Başlat**:
   - "🚀 İndirmeyi Başlat" butonuna tıklayın
   - İlerlemeyi log ekranından takip edin

### Özellikler

#### Playlist İndirme
```
https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID
```
Linki yazdığınızda otomatik olarak playlist tespit edilir ve tüm videolar eklenir.

#### Dosyadan Link Yükleme
`linkler.txt` dosyasına her satıra bir link yazın:
```
https://www.youtube.com/watch?v=VIDEO1
https://www.youtube.com/watch?v=VIDEO2
# Yorum satırları # ile başlar
```

#### Link Kontrolü
"🔍 Link Kontrolü" butonu ile linklerin geçerliliğini kontrol edebilirsiniz.

## 📁 Proje Yapısı

```
youtube-indirici/
├── youtube_indirici_modern.py  # Ana uygulama
├── README.md                   # Bu dosya
├── .gitignore                 # Git ignore dosyası
├── archive/                    # Eski dosyalar
│   ├── youtube_indirici_gui.py
│   ├── toplu_indirici.py
│   └── ...
└── Ses/                       # İndirilen ses dosyaları (gitignore)
└── Video/                     # İndirilen video dosyaları (gitignore)
```

## 🔧 Sorun Giderme

### yt-dlp Bulunamadı
```bash
python -m pip install --upgrade yt-dlp
```

### İndirme Hataları
- Linklerin geçerli olduğundan emin olun
- İnternet bağlantınızı kontrol edin
- VPN veya proxy deneyin (bölgesel kısıtlamalar için)
- yt-dlp'yi güncelleyin: `python -m pip install --upgrade yt-dlp`

### Playlist İndirme Sorunları
- Playlist linkinin doğru formatta olduğundan emin olun
- Özel playlist'ler için erişim izni gerekebilir
- Büyük playlist'ler için daha fazla zaman gerekebilir

## 🎯 Özellikler Detayı

### Paralel İndirme
Aynı anda birden fazla video indirerek toplam süreyi kısaltır. Sistem kaynaklarınıza göre 1-10 arası değer seçebilirsiniz.

### Otomatik Yeniden Deneme
Başarısız indirmeler otomatik olarak yeniden denenir. Maksimum deneme sayısı ve bekleme süresi ayarlanabilir.

### Akıllı Link Yönetimi
- Duplicate kontrolü: Aynı video birden fazla eklenmez
- URL temizleme: Gereksiz parametreler otomatik temizlenir
- YouTube Music desteği: Music linkleri otomatik dönüştürülür

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:
1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📧 İletişim

Sorularınız veya önerileriniz için issue açabilirsiniz.

## 🙏 Teşekkürler

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Güçlü YouTube indirme aracı
- [tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework

## 📊 Ekran Görüntüleri

*Ekran görüntüleri eklenecek*

## 🔄 Sürüm Geçmişi

### v3.0 (Mevcut)
- ✅ Modern GUI arayüzü
- ✅ Paralel indirme desteği
- ✅ Gelişmiş hata yönetimi
- ✅ Thread-safe ilerleme takibi
- ✅ Playlist desteği iyileştirildi
- ✅ Akıllı link yönetimi

### v2.0
- GUI versiyonu

### v1.0
- İlk sürüm (komut satırı)

---

⭐ Beğendiyseniz yıldız vermeyi unutmayın!

