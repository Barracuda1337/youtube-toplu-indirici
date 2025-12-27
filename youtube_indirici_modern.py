#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Toplu İndirici - Modern GUI Versiyonu
Gelişmiş arayüz ile YouTube videolarını toplu olarak indirir.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import subprocess
import os
import time
from pathlib import Path
import queue
import webbrowser

class ModernYouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 YouTube Toplu İndirici v3.0 - Modern")
        
        # Pencere boyutunu büyüt ve minimum boyut ayarla
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)  # Minimum boyut
        self.root.maxsize(1920, 1080)  # Maksimum boyut
        
        # Pencereyi ekranın ortasında aç
        self.center_window()
        
        self.root.configure(bg='#2b2b2b')
        
        # Modern tema ayarları
        self.setup_modern_theme()
        
        # Değişkenler
        self.links = []
        self.download_queue = queue.Queue()
        self.is_downloading = False
        self.current_download = None
        
        # Gelişmiş indirme ayarları
        self.max_concurrent_downloads = 3  # Paralel indirme sayısı
        self.download_speed_limit = None  # Hız sınırı (KB/s)
        self.max_retries = 3  # Maksimum yeniden deneme sayısı
        self.retry_delay = 5  # Yeniden deneme aralığı (saniye)
        self.active_downloads = 0  # Aktif indirme sayısı
        self.download_threads = []  # İndirme thread'leri
        self.failed_downloads = []  # Başarısız indirmeler
        
        # Thread-safe sayaçlar
        self.completed_count = 0  # Tamamlanan indirme sayısı
        self.successful_count = 0  # Başarılı indirme sayısı
        self.failed_count = 0  # Başarısız indirme sayısı
        self.completed_lock = threading.Lock()  # Thread-safe lock
        self.completed_status = {}  # Her link için tamamlanma durumu
        self.active_downloads_lock = threading.Lock()  # active_downloads için lock
        
        # Ana dizin
        self.base_dir = Path(r"C:\Users\Korsan-PC\Desktop\indir")
        self.audio_dir = self.base_dir / "Ses"
        self.video_dir = self.base_dir / "Video"
        
        # Dizinleri oluştur
        self.audio_dir.mkdir(exist_ok=True)
        self.video_dir.mkdir(exist_ok=True)
        
        self.setup_ui()
        self.check_yt_dlp()
    
    def center_window(self):
        """Pencereyi ekranın ortasında konumlandırır"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_modern_theme(self):
        """Modern tema ayarları"""
        style = ttk.Style()
        
        # Modern renk paleti
        colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'accent': '#007acc',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'secondary': '#6c757d'
        }
        
        # Tema ayarları
        style.theme_use('clam')
        
        # Frame stilleri
        style.configure('Modern.TFrame', background=colors['bg'])
        style.configure('Card.TFrame', background='#3c3c3c', relief='flat')
        
        # Label stilleri
        style.configure('Title.TLabel', 
                       background=colors['bg'], 
                       foreground=colors['fg'],
                       font=('Segoe UI', 18, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background=colors['bg'],
                       foreground=colors['accent'],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Status.TLabel',
                       background=colors['bg'],
                       foreground=colors['success'],
                       font=('Segoe UI', 10))
        
        # Button stilleri
        style.configure('Primary.TButton',
                       background=colors['accent'],
                       foreground=colors['fg'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 8))
        
        style.configure('Success.TButton',
                       background=colors['success'],
                       foreground=colors['fg'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 8))
        
        style.configure('Danger.TButton',
                       background=colors['danger'],
                       foreground=colors['fg'],
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 8))
        
        # Progress bar stili
        style.configure('Modern.Horizontal.TProgressbar',
                       background=colors['accent'],
                       troughcolor='#3c3c3c',
                       borderwidth=0,
                       lightcolor=colors['accent'],
                       darkcolor=colors['accent'])
    
    def setup_ui(self):
        """Arayüzü oluşturur"""
        # Ana container
        main_container = ttk.Frame(self.root, style='Modern.TFrame', padding="15")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Başlık bölümü
        header_frame = ttk.Frame(main_container, style='Card.TFrame', padding="20")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(header_frame, 
                               text="🎵 YouTube Toplu İndirici v3.0", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame,
                                  text="Modern arayüz ile hızlı ve kolay indirme",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
        # Ana içerik frame
        content_frame = ttk.Frame(main_container, style='Modern.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sol panel - Link yönetimi
        left_panel = ttk.Frame(content_frame, style='Card.TFrame', padding="15", width=600)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 10))
        left_panel.pack_propagate(False)  # Boyutu sabit tut
        
        # Link girişi
        link_input_frame = ttk.LabelFrame(left_panel, text="📝 Link Ekle", padding="10")
        link_input_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(link_input_frame, text="YouTube Linki:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.link_entry = ttk.Entry(link_input_frame, font=('Segoe UI', 10), width=50)
        self.link_entry.pack(fill=tk.X, pady=(5, 10))
        
                # Akıllı link yönetimi butonları - İlk satır
        button_frame1 = ttk.Frame(link_input_frame)
        button_frame1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(button_frame1, text="➕ Ekle", 
                   style='Success.TButton',
                   command=self.add_link).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame1, text="📁 Dosyadan Yükle", 
                   style='Primary.TButton',
                   command=self.load_from_file).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame1, text="🎵 Playlist Ekle", 
                   style='Primary.TButton',
                   command=self.add_playlist).pack(side=tk.LEFT, padx=(0, 5))
        
        # İkinci satır
        button_frame2 = ttk.Frame(link_input_frame)
        button_frame2.pack(fill=tk.X)
        
        ttk.Button(button_frame2, text="🔍 Link Kontrolü", 
                   style='Primary.TButton',
                   command=self.check_links).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame2, text="🗑️ Temizle", 
                   style='Danger.TButton',
                   command=self.clear_list).pack(side=tk.LEFT)
        
        # Link listesi
        list_frame = ttk.LabelFrame(left_panel, text="📋 Link Listesi", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        columns = ('No', 'Link', 'Durum')
        self.link_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        self.link_tree.heading('No', text='No')
        self.link_tree.heading('Link', text='YouTube Linki')
        self.link_tree.heading('Durum', text='Durum')
        
        self.link_tree.column('No', width=60, anchor='center')
        self.link_tree.column('Link', width=350)
        self.link_tree.column('Durum', width=120, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.link_tree.yview)
        self.link_tree.configure(yscrollcommand=scrollbar.set)
        
        self.link_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sağ panel - Kontroller ve log
        right_panel = ttk.Frame(content_frame, style='Card.TFrame', padding="15")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # İndirme seçenekleri
        options_frame = ttk.LabelFrame(right_panel, text="⚙️ İndirme Seçenekleri", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Format seçimi
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(format_frame, text="Format:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.format_var = tk.StringVar(value="audio")
        format_radio_frame = ttk.Frame(format_frame)
        format_radio_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Radiobutton(format_radio_frame, text="🎵 Ses (MP3)", 
                       variable=self.format_var, value="audio",
                       style='Subtitle.TLabel').pack(anchor=tk.W)
        ttk.Radiobutton(format_radio_frame, text="🎬 Video (MP4)", 
                       variable=self.format_var, value="video",
                       style='Subtitle.TLabel').pack(anchor=tk.W)
        
        # Gelişmiş format seçenekleri
        format_options_frame = ttk.Frame(options_frame)
        format_options_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Video kalite seçimi
        quality_frame = ttk.Frame(format_options_frame)
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(quality_frame, text="🎬 Video Kalitesi:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.quality_var = tk.StringVar(value="best")
        quality_combo = ttk.Combobox(quality_frame, 
                                    textvariable=self.quality_var,
                                    values=["best", "worst", "4K", "1440p", "1080p", "720p", "480p", "360p"],
                                    state="readonly",
                                    font=('Segoe UI', 10))
        quality_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Ses kalite seçimi
        audio_quality_frame = ttk.Frame(format_options_frame)
        audio_quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(audio_quality_frame, text="🎵 Ses Kalitesi:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.audio_quality_var = tk.StringVar(value="best")
        audio_quality_combo = ttk.Combobox(audio_quality_frame, 
                                          textvariable=self.audio_quality_var,
                                          values=["best", "worst", "320k", "192k", "128k"],
                                          state="readonly",
                                          font=('Segoe UI', 10))
        audio_quality_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Video format seçimi
        video_format_frame = ttk.Frame(format_options_frame)
        video_format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(video_format_frame, text="📹 Video Formatı:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.video_format_var = tk.StringVar(value="mp4")
        video_format_combo = ttk.Combobox(video_format_frame, 
                                         textvariable=self.video_format_var,
                                         values=["mp4", "webm", "mkv", "avi"],
                                         state="readonly",
                                         font=('Segoe UI', 10))
        video_format_combo.pack(fill=tk.X, pady=(5, 0))
        
        # Altyazı seçeneği
        subtitle_frame = ttk.Frame(format_options_frame)
        subtitle_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.subtitle_var = tk.BooleanVar(value=False)
        subtitle_check = ttk.Checkbutton(subtitle_frame, 
                                        text="📝 Altyazıları da indir",
                                        variable=self.subtitle_var,
                                        style='Subtitle.TLabel')
        subtitle_check.pack(anchor=tk.W)
        
        # Gelişmiş indirme ayarları
        advanced_frame = ttk.LabelFrame(right_panel, text="⚡ Gelişmiş İndirme Ayarları", padding="10")
        advanced_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Paralel indirme ayarı
        parallel_frame = ttk.Frame(advanced_frame)
        parallel_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(parallel_frame, text="🔄 Paralel İndirme:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        parallel_control_frame = ttk.Frame(parallel_frame)
        parallel_control_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(parallel_control_frame, text="Eşzamanlı indirme sayısı:").pack(side=tk.LEFT)
        
        self.parallel_var = tk.StringVar(value="3")
        parallel_spinbox = ttk.Spinbox(parallel_control_frame, 
                                      from_=1, to=10, width=5,
                                      textvariable=self.parallel_var,
                                      font=('Segoe UI', 10))
        parallel_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # Hız sınırı ayarı
        speed_frame = ttk.Frame(advanced_frame)
        speed_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(speed_frame, text="🚦 İndirme Hızı Sınırı:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        speed_control_frame = ttk.Frame(speed_frame)
        speed_control_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.speed_limit_var = tk.StringVar(value="")
        speed_spinbox = ttk.Spinbox(speed_control_frame, 
                                   from_=0, to=100000, width=10,
                                   textvariable=self.speed_limit_var,
                                   increment=1024,
                                   font=('Segoe UI', 10))
        speed_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(speed_control_frame, text="KB/s (boş = sınırsız)").pack(side=tk.LEFT, padx=(5, 0))
        
        # Yeniden deneme ayarları
        retry_frame = ttk.Frame(advanced_frame)
        retry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(retry_frame, text="🔄 Otomatik Yeniden Deneme:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        retry_control_frame = ttk.Frame(retry_frame)
        retry_control_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(retry_control_frame, text="Maksimum deneme:").pack(side=tk.LEFT)
        
        self.retry_count_var = tk.StringVar(value="3")
        retry_spinbox = ttk.Spinbox(retry_control_frame, 
                                   from_=0, to=10, width=5,
                                   textvariable=self.retry_count_var,
                                   font=('Segoe UI', 10))
        retry_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(retry_control_frame, text="Bekleme süresi:").pack(side=tk.LEFT)
        
        self.retry_delay_var = tk.StringVar(value="5")
        delay_spinbox = ttk.Spinbox(retry_control_frame, 
                                   from_=1, to=60, width=5,
                                   textvariable=self.retry_delay_var,
                                   font=('Segoe UI', 10))
        delay_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(retry_control_frame, text="saniye").pack(side=tk.LEFT, padx=(5, 0))
        
        # İndirme butonu
        self.download_button = ttk.Button(options_frame, 
                                         text="🚀 İndirmeyi Başlat", 
                                         style='Primary.TButton',
                                         command=self.start_download)
        self.download_button.pack(fill=tk.X, pady=(15, 0))
        
        # İptal butonu
        self.cancel_button = ttk.Button(options_frame,
                                       text="⏹️ İptal Et",
                                       style='Danger.TButton',
                                       command=self.cancel_download,
                                       state='disabled')
        self.cancel_button.pack(fill=tk.X, pady=(5, 0))
        
        # İlerleme çubuğu
        progress_frame = ttk.Frame(right_panel)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(progress_frame, text="İlerleme:", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        self.progress = ttk.Progressbar(progress_frame, 
                                       style='Modern.Horizontal.TProgressbar',
                                       mode='determinate')
        self.progress.pack(fill=tk.X, pady=(5, 0))
        
        # Durum etiketi
        self.status_label = ttk.Label(progress_frame, 
                                     text="Hazır", 
                                     style='Status.TLabel')
        self.status_label.pack(pady=(5, 0))
        
        # Log bölümü
        log_frame = ttk.LabelFrame(right_panel, text="📊 İndirme Logu", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 height=30, 
                                                 width=80,
                                                 font=('Consolas', 9),
                                                 bg='#1e1e1e',
                                                 fg='#ffffff',
                                                 insertbackground='#ffffff')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Alt bilgi çubuğu
        footer_frame = ttk.Frame(main_container, style='Card.TFrame', padding="10")
        footer_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(footer_frame, text="📁 Klasörü Aç", 
                  style='Primary.TButton',
                  command=self.open_folder).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(footer_frame, text="🌐 yt-dlp İndir", 
                  style='Primary.TButton',
                  command=self.open_yt_dlp).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(footer_frame, text="🔄 Başarısızları Yeniden Dene", 
                  style='Primary.TButton',
                  command=self.retry_failed).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(footer_frame, text="❓ Yardım", 
                  style='Primary.TButton',
                  command=self.show_help).pack(side=tk.LEFT)
        
        # Enter tuşu ile link ekleme
        self.link_entry.bind('<Return>', lambda e: self.add_link())
    
    def log(self, message, level="INFO"):
        """Log mesajı ekler"""
        timestamp = time.strftime("%H:%M:%S")
        colors = {
            "INFO": "#ffffff",
            "SUCCESS": "#28a745",
            "WARNING": "#ffc107",
            "ERROR": "#dc3545"
        }
        
        color = colors.get(level, "#ffffff")
        
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Son satırı renklendir
        last_line_start = self.log_text.index("end-2c linestart")
        last_line_end = self.log_text.index("end-1c")
        
        self.log_text.tag_add(f"color_{level}", last_line_start, last_line_end)
        self.log_text.tag_config(f"color_{level}", foreground=color)
        
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_yt_dlp(self):
        """yt-dlp'nin yüklü olup olmadığını kontrol eder"""
        try:
            # Önce Python modülü olarak dene
            result = subprocess.run(['python', '-m', 'yt_dlp', '--version'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log(f"✅ yt-dlp bulundu ve hazır (v{version})", "SUCCESS")
            else:
                # Sistem yt-dlp'sini dene
                result = subprocess.run(['yt-dlp', '--version'], 
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.log(f"✅ yt-dlp bulundu ve hazır (v{version})", "SUCCESS")
                else:
                    self.log("❌ yt-dlp bulunamadı!", "ERROR")
                    messagebox.showerror("Hata", "yt-dlp bulunamadı! Lütfen yt-dlp'yi yükleyin.")
        except:
            self.log("❌ yt-dlp bulunamadı!", "ERROR")
            messagebox.showerror("Hata", "yt-dlp bulunamadı! Lütfen yt-dlp'yi yükleyin.")
    
    def add_link(self):
        """Link listesine yeni link ekler"""
        link = self.link_entry.get().strip()
        if not link:
            messagebox.showwarning("Uyarı", "Lütfen bir YouTube linki girin!")
            return
        
        # YouTube link kontrolü (daha kapsamlı)
        youtube_patterns = [
            'http://', 'https://', 'www.youtube.com', 'youtube.com',
            'youtu.be', 'm.youtube.com', 'music.youtube.com'
        ]
        
        # YouTube Music linkini normal YouTube linkine çevir
        if "music.youtube.com" in link:
            # music.youtube.com/watch?v=... -> youtube.com/watch?v=...
            link = link.replace("music.youtube.com", "youtube.com")
            self.log(f"🔄 YouTube Music linki dönüştürüldü: {link}", "INFO")
        
        # URL'den gereksiz parametreleri temizle (&si=... gibi)
        import re
        link = re.sub(r'&si=[^&]*', '', link)
        self.log(f"🧹 URL temizlendi: {link}", "INFO")
        
        if not any(pattern in link for pattern in youtube_patterns):
            messagebox.showwarning("Uyarı", "Geçerli bir YouTube linki girin!")
            return

        # Playlist kontrolü
        if "list=" in link:
            if messagebox.askyesno("Playlist Tespit Edildi", 
                                 "Bu link bir playlist içeriyor. Tüm playlist'i eklemek ister misiniz?\n\nEvet: Playlist'teki tüm videoları ekler\nHayır: Sadece bu videoyu ekler"):
                self.add_playlist(link)
                return
        
        # Link zaten var mı kontrol et (daha akıllı)
        # Video ID'lerini karşılaştır
        video_id = self.extract_video_id(link)
        existing_ids = [self.extract_video_id(existing_link) for existing_link in self.links]
        
        if video_id and video_id in existing_ids:
            self.log(f"⚠️ Bu video zaten listede var: {link}", "WARNING")
            messagebox.showwarning("Uyarı", "Bu video zaten listede var!")
            return
        
        self.links.append(link)
        self.update_link_list()
        self.link_entry.delete(0, tk.END)
        self.log(f"✅ Link eklendi: {link}", "SUCCESS")
    
    def extract_video_id(self, url):
        """URL'den video ID'sini çıkarır"""
        import re
        
        # YouTube video ID pattern'leri
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def extract_playlist_id(self, url):
        """URL'den playlist ID'sini çıkarır"""
        import re
        
        # Playlist ID pattern'leri
        patterns = [
            r'[?&]list=([^&\n?#]+)',
            r'playlist\?list=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def normalize_playlist_url(self, url):
        """Playlist URL'sini normalize eder (watch?v=...&list=... -> playlist?list=...)"""
        import re
        
        playlist_id = self.extract_playlist_id(url)
        if not playlist_id:
            return url
        
        # Eğer zaten playlist?list= formatındaysa, olduğu gibi döndür
        if 'playlist?list=' in url or '/playlist?' in url:
            # Sadece gereksiz parametreleri temizle
            url = re.sub(r'&si=[^&]*', '', url)
            url = re.sub(r'&index=[^&]*', '', url)
            url = re.sub(r'&v=[^&]*', '', url)  # Video ID'yi kaldır
            return url
        
        # watch?v=...&list=... formatındaysa, playlist?list=... formatına çevir
        base_url = 'https://www.youtube.com'
        if 'youtube.com' in url:
            if 'www.' in url:
                base_url = 'https://www.youtube.com'
            else:
                base_url = 'https://youtube.com'
        
        normalized_url = f"{base_url}/playlist?list={playlist_id}"
        return normalized_url
    
    def load_from_file(self):
        """Dosyadan link yükler"""
        file_path = filedialog.askopenfilename(
            title="Link dosyasını seçin",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_links = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if line.startswith(('http://', 'https://', 'www.youtube.com', 'youtube.com')):
                            raw_links.append(line)
                
                if not raw_links:
                    messagebox.showwarning("Uyarı", "Dosyada geçerli link bulunamadı!")
                    return
                
                # Gelişmiş duplicate kontrolü
                new_links = []
                existing_ids = [self.extract_video_id(existing_link) for existing_link in self.links]
                duplicate_count = 0
                
                for link in raw_links:
                    # YouTube Music linkini normal YouTube linkine çevir
                    if "music.youtube.com" in link:
                        link = link.replace("music.youtube.com", "youtube.com")
                        self.log(f"🔄 YouTube Music linki dönüştürüldü: {link}", "INFO")
                    
                    # URL'den gereksiz parametreleri temizle (&si=... gibi)
                    import re
                    link = re.sub(r'&si=[^&]*', '', link)
                    
                    # Video ID kontrolü
                    video_id = self.extract_video_id(link)
                    if video_id and video_id not in existing_ids:
                        new_links.append(link)
                        existing_ids.append(video_id)  # Gelecek kontroller için ekle
                    else:
                        duplicate_count += 1
                
                if new_links:
                    self.links.extend(new_links)
                    self.update_link_list()
                    self.log(f"✅ {len(new_links)} link dosyadan yüklendi", "SUCCESS")
                    
                    if duplicate_count > 0:
                        self.log(f"⚠️ {duplicate_count} link zaten listede vardı", "WARNING")
                    
                    # Dosya yükleme istatistikleri
                    self.log(f"📊 Dosya yükleme tamamlandı:", "INFO")
                    self.log(f"   📋 Dosyadaki toplam link: {len(raw_links)}", "INFO")
                    self.log(f"   ✅ Eklenen: {len(new_links)}", "SUCCESS")
                    self.log(f"   ⚠️ Zaten var: {duplicate_count}", "WARNING")
                else:
                    self.log("⚠️ Dosyadaki tüm linkler zaten listede var", "WARNING")
                    messagebox.showwarning("Uyarı", "Dosyadaki tüm linkler zaten listede var!")
                    
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okuma hatası: {str(e)}")
    
    def add_playlist(self, playlist_url=None):
        """Playlist linkini ekler ve tüm videoları listeye ekler"""
        # Playlist linkini al (parametreden veya inputtan)
        if isinstance(playlist_url, str) and not playlist_url: # Eğer parametre boşsa inputtan al
             playlist_url = self.link_entry.get().strip()
        elif not isinstance(playlist_url, str): # Parametre yoksa inputtan al
             playlist_url = self.link_entry.get().strip()

        if not playlist_url:
            messagebox.showwarning("Uyarı", "Lütfen bir playlist linki girin!")
            return
        
        # YouTube Music ve normal YouTube playlist kontrolü
        if not any(keyword in playlist_url for keyword in ["playlist", "list=", "music.youtube.com"]):
            messagebox.showwarning("Uyarı", "Geçerli bir YouTube playlist linki girin!")
            return
        
        try:
            self.log(f"🎵 Playlist analiz ediliyor: {playlist_url}", "INFO")
            
            # YouTube Music linkini normal YouTube linkine çevir
            if "music.youtube.com" in playlist_url:
                # music.youtube.com/playlist?list=... -> youtube.com/playlist?list=...
                playlist_url = playlist_url.replace("music.youtube.com", "youtube.com")
                self.log(f"🔄 YouTube Music linki dönüştürüldü: {playlist_url}", "INFO")
            
            # URL'den gereksiz parametreleri temizle (&si=... gibi)
            import re
            playlist_url = re.sub(r'&si=[^&]*', '', playlist_url)
            
            # Playlist URL'sini normalize et (watch?v=...&list=... -> playlist?list=...)
            normalized_url = self.normalize_playlist_url(playlist_url)
            if normalized_url != playlist_url:
                self.log(f"🔄 Playlist URL normalize edildi: {normalized_url}", "INFO")
            playlist_url = normalized_url
            
            self.log(f"🧹 URL temizlendi: {playlist_url}", "INFO")
            
            # Playlist'teki videoları al - Geliştirilmiş yt-dlp komutu
            # Önce Python modülü olarak dene
            cmd = [
                'python', '-m', 'yt_dlp',
                '--flat-playlist',
                '--yes-playlist',
                '--get-id',
                '--no-warnings',
                '--quiet',
                '--extractor-args', 'youtube:player_client=android',
                playlist_url
            ]
            
            self.log(f"🔍 yt-dlp komutu çalıştırılıyor...", "INFO")
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=60)
            
            # Eğer Python modülü başarısız olursa, sistem yt-dlp'sini dene
            if result.returncode != 0:
                self.log(f"⚠️ Python modülü başarısız, sistem yt-dlp deneniyor...", "WARNING")
                cmd = [
                    'yt-dlp',
                    '--flat-playlist',
                    '--yes-playlist',
                    '--get-id',
                    '--no-warnings',
                    '--quiet',
                    '--extractor-args', 'youtube:player_client=android',
                    playlist_url
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=60)
            
            if result.returncode == 0:
                video_ids = result.stdout.strip().split('\n')
                video_ids = [vid.strip() for vid in video_ids if vid.strip()]  # Boş satırları temizle
                
                if video_ids:
                    self.log(f"📋 Playlist'te {len(video_ids)} video bulundu", "SUCCESS")
                    
                    # Video ID'lerini tam URL'lere çevir
                    playlist_links = [f"https://www.youtube.com/watch?v={vid_id}" for vid_id in video_ids]
                    
                    # Gelişmiş duplicate kontrolü
                    new_links = []
                    existing_ids = [self.extract_video_id(existing_link) for existing_link in self.links]
                    
                    for link in playlist_links:
                        video_id = self.extract_video_id(link)
                        if video_id and video_id not in existing_ids:
                            new_links.append(link)
                            existing_ids.append(video_id)  # Gelecek kontroller için ekle
                    
                    if new_links:
                        self.links.extend(new_links)
                        self.update_link_list()
                        self.link_entry.delete(0, tk.END)
                        self.log(f"✅ Playlist'ten {len(new_links)} video eklendi", "SUCCESS")
                        
                        if len(new_links) < len(playlist_links):
                            self.log(f"⚠️ {len(playlist_links) - len(new_links)} video zaten listede vardı", "WARNING")
                        
                        # Playlist istatistikleri
                        self.log(f"📊 Playlist analizi tamamlandı:", "INFO")
                        self.log(f"   📋 Toplam video: {len(playlist_links)}", "INFO")
                        self.log(f"   ✅ Eklenen: {len(new_links)}", "SUCCESS")
                        self.log(f"   ⚠️ Zaten var: {len(playlist_links) - len(new_links)}", "WARNING")
                        
                        messagebox.showinfo("Başarılı", 
                                          f"Playlist başarıyla eklendi!\n\n"
                                          f"📋 Toplam video: {len(playlist_links)}\n"
                                          f"✅ Eklenen: {len(new_links)}\n"
                                          f"⚠️ Zaten var: {len(playlist_links) - len(new_links)}")
                    else:
                        self.log("⚠️ Playlist'teki tüm videolar zaten listede var", "WARNING")
                        messagebox.showinfo("Bilgi", "Playlist'teki tüm videolar zaten listede var!")
                else:
                    error_msg = result.stderr if result.stderr else "Video bulunamadı"
                    self.log(f"❌ Playlist'te video bulunamadı: {error_msg}", "ERROR")
                    messagebox.showerror("Hata", f"Playlist'te video bulunamadı!\n\nHata: {error_msg}")
            else:
                error_msg = result.stderr if result.stderr else result.stdout
                self.log(f"❌ Playlist analiz hatası: {error_msg}", "ERROR")
                self.log(f"   Komut: {' '.join(cmd)}", "ERROR")
                self.log(f"   URL: {playlist_url}", "ERROR")
                
                # Daha açıklayıcı hata mesajı
                if "HTTP Error 403" in error_msg or "HTTP Error 429" in error_msg:
                    error_detail = "Erişim engellendi. VPN veya proxy deneyin veya bir süre bekleyin."
                elif "Video unavailable" in error_msg or "Private" in error_msg:
                    error_detail = "Playlist özel veya bölgesel kısıtlı olabilir."
                elif "extractor" in error_msg.lower() or "signature" in error_msg.lower():
                    error_detail = "yt-dlp güncellemesi gerekebilir. Lütfen yt-dlp'yi güncelleyin."
                else:
                    error_detail = "Bilinmeyen bir hata oluştu."
                
                messagebox.showerror("Hata", 
                                    f"Playlist analiz edilemedi!\n\n"
                                    f"Hata: {error_detail}\n\n"
                                    f"Detay: {error_msg[:200]}")
                
        except subprocess.TimeoutExpired:
            self.log("⏰ Playlist analizi zaman aşımına uğradı (60 saniye)", "ERROR")
            messagebox.showerror("Hata", 
                               "Playlist analizi zaman aşımına uğradı!\n\n"
                               "Büyük playlist'ler için daha fazla zaman gerekebilir.\n"
                               "Lütfen tekrar deneyin.")
        except Exception as e:
            self.log(f"❌ Playlist ekleme hatası: {str(e)}", "ERROR")
            import traceback
            self.log(f"   Detay: {traceback.format_exc()}", "ERROR")
            messagebox.showerror("Hata", f"Playlist ekleme hatası:\n\n{str(e)}")
    
    def check_links(self):
        """Linklerin geçerliliğini kontrol eder"""
        if not self.links:
            messagebox.showwarning("Uyarı", "Kontrol edilecek link bulunamadı!")
            return
        
        self.log("🔍 Link geçerlilik kontrolü başlatılıyor...", "INFO")
        
        valid_links = []
        invalid_links = []
        
        for i, link in enumerate(self.links, 1):
            self.log(f"🔍 Kontrol ediliyor ({i}/{len(self.links)}): {link}", "INFO")
            
            try:
                # Video bilgilerini al
                cmd = [
                    'python', '-m', 'yt_dlp',
                    '--get-title',
                    '--no-warnings',
                    '--quiet',
                    link
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    valid_links.append(link)
                    self.log(f"✅ Geçerli: {result.stdout.strip()[:50]}...", "SUCCESS")
                else:
                    invalid_links.append(link)
                    self.log(f"❌ Geçersiz: {link}", "ERROR")
                    
            except subprocess.TimeoutExpired:
                invalid_links.append(link)
                self.log(f"⏰ Zaman aşımı: {link}", "ERROR")
            except Exception as e:
                invalid_links.append(link)
                self.log(f"❌ Hata: {link} - {str(e)}", "ERROR")
        
        # Sonuçları göster
        self.log("-" * 50, "INFO")
        self.log(f"📊 KONTROL SONUÇLARI:", "INFO")
        self.log(f"✅ Geçerli: {len(valid_links)}", "SUCCESS")
        self.log(f"❌ Geçersiz: {len(invalid_links)}", "ERROR")
        
        if invalid_links:
            if messagebox.askyesno("Geçersiz Linkler", 
                                 f"{len(invalid_links)} geçersiz link bulundu. Bunları listeden kaldırmak ister misiniz?"):
                self.links = valid_links
                self.update_link_list()
                self.log("🗑️ Geçersiz linkler kaldırıldı", "WARNING")
    
    def clear_list(self):
        """Link listesini temizler"""
        if messagebox.askyesno("Onay", "Tüm linkleri silmek istediğinizden emin misiniz?"):
            self.links.clear()
            self.update_link_list()
            self.log("🗑️ Link listesi temizlendi", "WARNING")
    
    def update_link_list(self):
        """Link listesini günceller"""
        # Mevcut öğeleri temizle
        for item in self.link_tree.get_children():
            self.link_tree.delete(item)
        
        # Yeni öğeleri ekle
        for i, link in enumerate(self.links, 1):
            self.link_tree.insert('', 'end', values=(i, link, "Bekliyor"))
    
    def start_download(self):
        """İndirme işlemini başlatır"""
        if not self.links:
            messagebox.showwarning("Uyarı", "İndirilecek link bulunamadı!")
            return
        
        if self.is_downloading:
            messagebox.showwarning("Uyarı", "İndirme işlemi zaten devam ediyor!")
            return
        
        # Ayarları güncelle
        try:
            self.max_concurrent_downloads = int(self.parallel_var.get())
            self.max_retries = int(self.retry_count_var.get())
            self.retry_delay = int(self.retry_delay_var.get())
            
            speed_limit = self.speed_limit_var.get().strip()
            self.download_speed_limit = int(speed_limit) if speed_limit else None
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")
            return
        
        # Onay al
        format_text = "Ses (MP3)" if self.format_var.get() == "audio" else "Video (MP4)"
        parallel_text = f" ({self.max_concurrent_downloads} paralel)" if self.max_concurrent_downloads > 1 else ""
        
        if not messagebox.askyesno("Onay", 
                                 f"{len(self.links)} linki {format_text} olarak{parallel_text} indirmek istediğinizden emin misiniz?"):
            return
        
        # İndirme thread'ini başlat
        self.is_downloading = True
        self.active_downloads = 0
        self.failed_downloads = []
        self.download_threads = []
        
        # Sayaçları sıfırla
        self.completed_count = 0
        self.successful_count = 0
        self.failed_count = 0
        self.completed_status = {}  # Her link için durum: None, 'success', 'failed'
        
        self.download_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        self.progress['maximum'] = len(self.links)
        self.progress['value'] = 0
        
        download_thread = threading.Thread(target=self.download_all_parallel)
        download_thread.daemon = True
        download_thread.start()
    
    def cancel_download(self):
        """İndirme işlemini iptal eder"""
        if self.is_downloading:
            self.is_downloading = False
            self.log("⏹️ İndirme iptal edildi", "WARNING")
            self.download_finished(0, 0, cancelled=True)
    
    def download_all_parallel(self):
        """Tüm linkleri paralel olarak indirir"""
        format_type = self.format_var.get()
        quality = self.quality_var.get()
        output_dir = str(self.audio_dir) if format_type == "audio" else str(self.video_dir)
        
        self.log(f"🚀 {len(self.links)} link paralel indiriliyor...", "INFO")
        self.log(f"📁 Hedef: {output_dir}", "INFO")
        self.log(f"🎵 Format: {'Ses (MP3)' if format_type == 'audio' else 'Video (MP4)'}", "INFO")
        self.log(f"🎯 Kalite: {quality}", "INFO")
        self.log(f"⚡ Paralel indirme: {self.max_concurrent_downloads}", "INFO")
        if self.download_speed_limit:
            self.log(f"🚦 Hız sınırı: {self.download_speed_limit} KB/s", "INFO")
        self.log(f"🔄 Maksimum deneme: {self.max_retries}", "INFO")
        self.log("-" * 50, "INFO")
        
        # İndirme kuyruğunu oluştur
        download_queue = queue.Queue()
        for i, link in enumerate(self.links):
            download_queue.put((i+1, link))
            # Başlangıç durumunu ayarla
            self.completed_status[i+1] = None
        
        # Worker thread'leri başlat
        for _ in range(self.max_concurrent_downloads):
            worker = threading.Thread(target=self.download_worker, 
                                    args=(download_queue, output_dir, format_type, quality))
            worker.daemon = True
            worker.start()
            self.download_threads.append(worker)
        
        # Ana thread'de ilerlemeyi takip et
        last_completed = 0
        
        while self.completed_count < len(self.links) and self.is_downloading:
            time.sleep(0.5)
            
            # Thread-safe olarak tamamlanan sayısını al
            with self.completed_lock:
                current_completed = self.completed_count
                current_successful = self.successful_count
                current_failed = self.failed_count
            
            # İlerleme güncellendi mi kontrol et
            if current_completed != last_completed:
                last_completed = current_completed
                # UI'ı güncelle
                self.root.after(0, lambda c=current_completed: self.progress.config(value=c))
            
            # Durum güncelle (active_downloads thread-safe okuma)
            with self.active_downloads_lock:
                current_active = self.active_downloads
            self.root.after(0, lambda c=current_completed, a=current_active: 
                          self.status_label.config(
                              text=f"İndiriliyor: {c}/{len(self.links)} (Aktif: {a})"))
        
        # Worker thread'lerin bitmesini bekle (daha uzun timeout)
        self.log("⏳ Worker thread'lerin bitmesi bekleniyor...", "INFO")
        for worker in self.download_threads:
            worker.join(timeout=30)  # 30 saniye bekle
        
        # Final sayıları al
        with self.completed_lock:
            final_successful = self.successful_count
            final_failed = self.failed_count
        
        # Sonuçları göster
        self.root.after(0, lambda: self.download_finished(final_successful, final_failed))
    
    def download_worker(self, download_queue, output_dir, format_type, quality):
        """Worker thread - kuyruktan link alıp indirir"""
        while self.is_downloading:
            try:
                # Timeout ile kuyruktan al (1 saniye bekle)
                try:
                    index, link = download_queue.get(timeout=1)
                except queue.Empty:
                    # Kuyruk boşsa, başka thread'lerin işi bitmesini bekle
                    # Eğer aktif indirme yoksa ve kuyruk boşsa çık
                    with self.active_downloads_lock:
                        if self.active_downloads == 0 and download_queue.empty():
                            break
                    continue
                
                # Bu link zaten işlenmiş mi kontrol et
                with self.completed_lock:
                    if self.completed_status.get(index) is not None:
                        download_queue.task_done()
                        continue
                
                with self.active_downloads_lock:
                    self.active_downloads += 1
                
                # Durumu güncelle
                self.root.after(0, lambda idx=index: self.update_link_status(idx, "İndiriliyor..."))
                
                # İndirmeyi dene
                success = self.download_with_retry(link, output_dir, format_type, quality, index)
                
                # Thread-safe olarak durumu güncelle
                with self.completed_lock:
                    if self.completed_status.get(index) is None:  # Henüz işlenmemişse
                        if success:
                            self.completed_status[index] = 'success'
                            self.successful_count += 1
                            self.root.after(0, lambda idx=index: self.update_link_status(idx, "✅ Tamamlandı"))
                        else:
                            self.completed_status[index] = 'failed'
                            self.failed_count += 1
                            self.failed_downloads.append((index, link))
                            self.root.after(0, lambda idx=index: self.update_link_status(idx, "❌ Hata"))
                        
                        self.completed_count += 1
                
                with self.active_downloads_lock:
                    self.active_downloads -= 1
                download_queue.task_done()
                
            except Exception as e:
                self.log(f"❌ Worker hatası: {str(e)}", "ERROR")
                import traceback
                self.log(f"   Detay: {traceback.format_exc()}", "ERROR")
                
                # Hata durumunda da sayaçları güncelle
                try:
                    with self.completed_lock:
                        if 'index' in locals() and self.completed_status.get(index) is None:
                            self.completed_status[index] = 'failed'
                            self.failed_count += 1
                            self.completed_count += 1
                            if 'link' in locals():
                                self.failed_downloads.append((index, link))
                            self.root.after(0, lambda idx=index: self.update_link_status(idx, "❌ Hata"))
                except:
                    pass
                
                if 'active_downloads' in locals():
                    with self.active_downloads_lock:
                        self.active_downloads -= 1
                
                # Hata olsa bile devam et (diğer linkleri indirmeye devam et)
                try:
                    download_queue.task_done()
                except:
                    pass
                
                # Kısa bir bekleme sonra devam et
                time.sleep(0.5)
                continue
    
    def download_with_retry(self, url, output_dir, format_type, quality, index):
        """Yeniden deneme ile indirme"""
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    self.log(f"🔄 {index}. deneme: {url}", "WARNING")
                    time.sleep(self.retry_delay)
                
                if self.download_single(url, output_dir, format_type, quality):
                    return True
                    
            except Exception as e:
                self.log(f"❌ Deneme {attempt + 1} hatası: {url} - {str(e)}", "ERROR")
        
        self.log(f"❌ Tüm denemeler başarısız: {url}", "ERROR")
        return False
    
    def download_single(self, url, output_dir, format_type, quality):
        """Tek bir video indirir"""
        try:
            # Temel yt-dlp parametreleri (Python modülü olarak)
            base_cmd = [
                'python', '-m', 'yt_dlp',
                '--no-warnings',  # Uyarıları gizle
                '--ignore-errors',  # Hataları görmezden gel
                '--no-check-certificates',  # Sertifika kontrolünü atla
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--extractor-args', 'youtube:player_client=android',
                '-P', output_dir,
                '-o', '%(title)s.%(ext)s'
            ]
            
            # Hız sınırı ekle
            if self.download_speed_limit:
                base_cmd.extend(['--limit-rate', f'{self.download_speed_limit}K'])
            
            # Altyazı indirme seçeneği
            if self.subtitle_var.get():
                base_cmd.extend(['--write-sub', '--write-auto-sub'])
            
            if format_type == "audio":
                # Ses kalitesi ayarları
                audio_quality = self.audio_quality_var.get()
                if audio_quality == "best":
                    audio_format = "ba/b"
                elif audio_quality == "worst":
                    audio_format = "wa/w"
                elif audio_quality in ["320k", "192k", "128k"]:
                    audio_format = f"ba[abr<={audio_quality}]/b"
                else:
                    audio_format = "ba/b"
                
                cmd = base_cmd + [
                    '-x',
                    '-f', audio_format,
                    '--audio-format', 'mp3',
                    '--audio-quality', '0',  # En iyi kalite
                    '--extract-audio',
                    url
                ]
            else:  # video
                # Video kalitesi ayarları
                if quality == "best":
                    format_spec = "bv+ba/b"
                elif quality == "worst":
                    format_spec = "wv+wa/w"
                elif quality in ["4K", "1440p", "1080p", "720p", "480p", "360p"]:
                    height = quality[:-1] if quality != "4K" else "2160"
                    format_spec = f"bv[height<={height}]+ba/b"
                else:
                    format_spec = "bv+ba/b"
                
                # Video format ayarları
                video_format = self.video_format_var.get()
                if video_format == "mp4":
                    format_preference = "ext:mp4:m4a"
                elif video_format == "webm":
                    format_preference = "ext:webm"
                elif video_format == "mkv":
                    format_preference = "ext:mkv"
                elif video_format == "avi":
                    format_preference = "ext:avi"
                else:
                    format_preference = "ext:mp4:m4a"
                
                cmd = base_cmd + [
                    '-f', format_spec,
                    '-S', format_preference,
                    url
                ]
            
            self.log(f"📥 İndiriliyor: {url}", "INFO")
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                self.log(f"✅ Başarılı: {url}", "SUCCESS")
                return True
            else:
                # Gelişmiş hata yakalama
                error_msg = result.stderr
                self.handle_download_error(url, error_msg)
                
                # İkinci deneme - daha basit format ile
                self.log(f"🔄 İkinci deneme yapılıyor: {url}", "WARNING")
                retry_cmd = base_cmd + [
                    '-f', 'best[ext=mp4]/best[ext=webm]/best',
                    url
                ] if format_type == "video" else base_cmd + [
                    '-x',
                    '-f', 'bestaudio/best',
                    '--audio-format', 'mp3',
                    url
                ]
                
                retry_result = subprocess.run(retry_cmd, capture_output=True, text=True, shell=True)
                
                if retry_result.returncode == 0:
                    self.log(f"✅ İkinci deneme başarılı: {url}", "SUCCESS")
                    return True
                else:
                    self.handle_download_error(url, retry_result.stderr, 2)
                    return False
                
        except Exception as e:
            self.log(f"❌ Hata: {url} - {str(e)}", "ERROR")
            return False
    
    def update_link_status(self, index, status):
        """Link durumunu günceller"""
        for item in self.link_tree.get_children():
            if self.link_tree.item(item)['values'][0] == index:
                values = list(self.link_tree.item(item)['values'])
                values[2] = status
                self.link_tree.item(item, values=values)
                break
    
    def get_link_status(self, index):
        """Link durumunu alır"""
        for item in self.link_tree.get_children():
            if self.link_tree.item(item)['values'][0] == index:
                return self.link_tree.item(item)['values'][2]
        return "Bekliyor"
    
    def handle_download_error(self, url, error_msg, attempt=1):
        """İndirme hatalarını işler"""
        error_types = {
            "HTTP Error 403": "Erişim engellendi - VPN veya proxy deneyin",
            "HTTP Error 429": "Çok fazla istek - Biraz bekleyin",
            "HTTP Error 500": "Sunucu hatası - Daha sonra tekrar deneyin",
            "Signature extraction failed": "YouTube güncellemesi - yt-dlp'yi güncelleyin",
            "Video unavailable": "Video mevcut değil veya bölgesel kısıtlı",
            "Private video": "Özel video - Erişim izni gerekli",
            "Video is private": "Özel video - Erişim izni gerekli",
            "This video is not available": "Video mevcut değil",
            "Video unavailable in your country": "Bölgesel kısıtlı video"
        }
        
        # Hata tipini belirle
        error_suggestion = "Bilinmeyen hata"
        for error_type, suggestion in error_types.items():
            if error_type.lower() in error_msg.lower():
                error_suggestion = suggestion
                break
        
        self.log(f"❌ Hata ({attempt}): {error_suggestion}", "ERROR")
        self.log(f"   URL: {url}", "ERROR")
        self.log(f"   Detay: {error_msg[:100]}...", "ERROR")
        
        return error_suggestion
    
    def download_finished(self, successful, failed, cancelled=False):
        """İndirme tamamlandığında çağrılır"""
        self.is_downloading = False
        self.download_button.config(state='normal')
        self.cancel_button.config(state='disabled')
        self.status_label.config(text="Tamamlandı")
        
        if cancelled:
            self.log("-" * 50, "WARNING")
            self.log("⏹️ İNDİRME İPTAL EDİLDİ", "WARNING")
        else:
            self.log("-" * 50, "INFO")
            self.log("🎉 İNDİRME TAMAMLANDI!", "SUCCESS")
            self.log(f"✅ Başarılı: {successful}", "SUCCESS")
            self.log(f"❌ Başarısız: {failed}", "ERROR")
            self.log(f"📊 Toplam: {len(self.links)}", "INFO")
            
            if successful > 0:
                output_dir = str(self.audio_dir) if self.format_var.get() == "audio" else str(self.video_dir)
                self.log(f"📁 Dosyalar: {output_dir}", "INFO")
            
            messagebox.showinfo("Tamamlandı", 
                              f"İndirme tamamlandı!\n✅ Başarılı: {successful}\n❌ Başarısız: {failed}")
    
    def open_folder(self):
        """İndirme klasörünü açar"""
        format_type = self.format_var.get()
        folder_path = str(self.audio_dir) if format_type == "audio" else str(self.video_dir)
        os.startfile(folder_path)
    
    def open_yt_dlp(self):
        """yt-dlp indirme sayfasını açar"""
        webbrowser.open("https://github.com/yt-dlp/yt-dlp")
    
    def retry_failed(self):
        """Başarısız indirmeleri yeniden dener"""
        if not self.failed_downloads:
            messagebox.showinfo("Bilgi", "Yeniden denenecek başarısız indirme bulunamadı!")
            return
        
        if self.is_downloading:
            messagebox.showwarning("Uyarı", "İndirme işlemi devam ediyor! Lütfen bekleyin.")
            return
        
        failed_count = len(self.failed_downloads)
        if not messagebox.askyesno("Onay", 
                                 f"{failed_count} başarısız indirmeyi yeniden denemek istediğinizden emin misiniz?"):
            return
        
        # Başarısız linkleri listeye ekle
        failed_links = [link for _, link in self.failed_downloads]
        self.links.extend(failed_links)
        self.update_link_list()
        
        # Başarısız listesini temizle
        self.failed_downloads = []
        
        self.log(f"🔄 {failed_count} başarısız indirme yeniden deneme kuyruğuna eklendi", "INFO")
        messagebox.showinfo("Bilgi", f"{failed_count} başarısız indirme yeniden deneme kuyruğuna eklendi!")
    
    def show_help(self):
        """Yardım penceresi gösterir"""
        help_text = """
🎵 YouTube Toplu İndirici v3.0 - Yardım

📝 NASIL KULLANILIR:
1. YouTube linkini girin ve "Ekle" butonuna tıklayın
2. Veya "Dosyadan Yükle" ile toplu link ekleyin
3. Format seçin (Ses/Video)
4. Kalite seçin
5. "İndirmeyi Başlat" butonuna tıklayın

📋 ÖZELLİKLER:
• Modern ve kullanıcı dostu arayüz
• Toplu indirme desteği
• Gerçek zamanlı ilerleme takibi
• Detaylı log sistemi
• Kalite seçenekleri
• İptal etme özelliği

⚠️ NOTLAR:
• yt-dlp yüklü olmalı
• İnternet bağlantısı gerekli
• Yeterli disk alanı olmalı
• YouTube linkleri geçerli olmalı

🔧 SORUN GİDERME:
• yt-dlp bulunamadı hatası: yt-dlp'yi yükleyin
• İndirme hataları: Linkleri kontrol edin
• Disk alanı: Yeterli alan olduğundan emin olun
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Yardım")
        help_window.geometry("500x600")
        help_window.configure(bg='#2b2b2b')
        
        text_widget = scrolledtext.ScrolledText(help_window, 
                                              font=('Segoe UI', 10),
                                              bg='#1e1e1e',
                                              fg='#ffffff',
                                              wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = ModernYouTubeDownloader(root)
    
    # Pencereyi kapatma olayı
    def on_closing():
        if app.is_downloading:
            if messagebox.askokcancel("Çıkış", "İndirme devam ediyor. Çıkmak istediğinizden emin misiniz?"):
                app.is_downloading = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 