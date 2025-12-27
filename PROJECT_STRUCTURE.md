# 📁 Proje Yapısı

```
youtube-indirici/
│
├── 📄 youtube_indirici_modern.py    # Ana uygulama dosyası
│
├── 📚 Dokümantasyon
│   ├── README.md                    # Ana dokümantasyon
│   ├── CONTRIBUTING.md              # Katkıda bulunma rehberi
│   ├── LICENSE                      # MIT Lisansı
│   └── PROJECT_STRUCTURE.md         # Bu dosya
│
├── 🔧 Konfigürasyon
│   ├── .gitignore                   # Git ignore kuralları
│   ├── .gitattributes               # Git attributes
│   └── requirements.txt             # Python bağımlılıkları
│
├── 📦 Archive (Eski Dosyalar)
│   ├── README.md                    # Archive açıklaması
│   ├── youtube_indirici_gui.py     # Eski GUI versiyonu
│   ├── youtube_indirici_gui copy.py # Kopya dosya
│   ├── toplu_indirici.py           # Eski CLI versiyonu
│   ├── gelismis_indirici.bat       # Eski batch script
│   ├── toplu_indir.bat             # Eski batch script
│   ├── KULLANIM_KILAVUZU.txt       # Eski kılavuz
│   ├── formatlar.txt               # Eski format dosyası
│   └── Baslat.lnk                  # Kısayol
│
└── 📂 Kullanıcı Dosyaları (Git'te yok)
    ├── Ses/                         # İndirilen ses dosyaları
    ├── Video/                       # İndirilen video dosyaları
    ├── Indirmeler/                  # Alternatif indirme klasörü
    └── linkler.txt                  # Kullanıcı link dosyası
```

## 📝 Dosya Açıklamaları

### Ana Dosyalar

- **youtube_indirici_modern.py**: Modern GUI arayüzlü ana uygulama
  - Tkinter tabanlı kullanıcı arayüzü
  - Paralel indirme desteği
  - Playlist yönetimi
  - Gelişmiş hata yönetimi

### Dokümantasyon

- **README.md**: Proje hakkında genel bilgiler, kurulum ve kullanım
- **CONTRIBUTING.md**: Katkıda bulunma rehberi
- **LICENSE**: MIT lisansı
- **PROJECT_STRUCTURE.md**: Proje yapısı açıklaması (bu dosya)

### Konfigürasyon

- **.gitignore**: Git'in takip etmeyeceği dosyalar
- **.gitattributes**: Git dosya özellikleri (line ending vb.)
- **requirements.txt**: Python paket bağımlılıkları

### Archive

Eski versiyonlar ve kullanılmayan dosyalar bu klasörde saklanır. Referans amaçlıdır.

### Kullanıcı Dosyaları

Bu klasörler `.gitignore` ile Git'ten hariç tutulmuştur:
- **Ses/**: İndirilen MP3 dosyaları
- **Video/**: İndirilen MP4/WebM dosyaları
- **Indirmeler/**: Alternatif indirme klasörü
- **linkler.txt**: Kullanıcının link listesi

## 🚀 Hızlı Başlangıç

1. Repository'yi klonlayın
2. `requirements.txt` dosyasındaki bağımlılıkları yükleyin
3. `youtube_indirici_modern.py` dosyasını çalıştırın

## 📦 Bağımlılıklar

- Python 3.7+
- yt-dlp
- tkinter (Python ile birlikte gelir)

Detaylar için `requirements.txt` dosyasına bakın.

