import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
from PIL import ImageTk, Image
import requests
from io import BytesIO
import re

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("400x700")

        # Configure styles for macOS height fix
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 10), padding=2)
        self.style.configure('TCombobox', padding=2)
        self.style.configure('TLabel', font=('Arial', 10))

        self.create_widgets()
        self.ydl_opts = {'quiet': True, 'no_warnings': True}
        self.formats = []
        self.thumbnail = None

    def create_widgets(self):
        # URL Entry
        tk.Label(self.root, text="YouTube URL:", font=('Arial', 10)).pack(pady=5)
        self.url_entry = tk.Entry(self.root, width=45)
        self.url_entry.pack(pady=5)

        # Fetch Button
        self.fetch_btn = ttk.Button(
            self.root,
            text="Fetch Video",
            command=self.fetch_video,
            style='TButton'
        )
        self.fetch_btn.pack(pady=5)

        # Progress Bar
        tk.Label(self.root, text="Progress:", font=('Arial', 10)).pack(pady=5)
        self.progress = ttk.Progressbar(
            self.root,
            orient='horizontal',
            length=300,
            mode='determinate'
        )
        self.progress.pack(pady=5)

        # Other UI elements (Thumbnail, Title, Quality, Download Button)
        self.thumbnail_label = tk.Label(self.root)
        self.thumbnail_label.pack(pady=5)
        self.title_label = tk.Label(
            self.root,
            wraplength=380,
            font=('Arial', 10)
        )
        self.title_label.pack(pady=5)
        tk.Label(self.root, text="Select Format:", font=('Arial', 10)).pack(pady=5)
        self.quality_combo = ttk.Combobox(
            self.root,
            state='readonly',
            font=('Arial', 10),
            height=15
        )
        self.quality_combo.pack(pady=5)
        self.quality_combo.bind('<<ComboboxSelected>>', self.update_size)
        self.size_label = tk.Label(self.root, font=('Arial', 10))
        self.size_label.pack(pady=5)
        self.download_btn = ttk.Button(
            self.root,
            text="Download",
            state='disabled',
            command=self.download_video,
            style='TButton'
        )
        self.download_btn.pack(pady=10)

    def download_video(self):
        """Download the selected video format with progress bar."""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        selection = self.quality_combo.current()
        if selection < 0:
            messagebox.showerror("Error", "Please select a format")
            return

        format_id = self.formats[selection][0]
        save_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if not save_path:
            return

        self.ydl_opts.update({
            'format': format_id,
            'outtmpl': save_path,
            'progress_hooks': [self.progress_hook]
        })

        try:
            self.progress['value'] = 0  # Reset progress bar
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Success", "Download complete")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download video: {e}")


    def fetch_video(self):
        """Fetch video details and display them."""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.title_label.config(text=info['title'])
                self.formats = [
                    (f['format_id'], f['format_note'], f['filesize'])
                    for f in info['formats']
                    if f.get('filesize')
                ]
                self.quality_combo['values'] = [
                    f"{fmt[1]} - {fmt[2] / (1024**2):.2f} MB" for fmt in self.formats
                ]
                if self.formats:
                    self.quality_combo.current(0)
                    self.download_btn['state'] = 'normal'

                # Display thumbnail
                response = requests.get(info['thumbnail'])
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img = img.resize((200, 120), Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(img)
                self.thumbnail_label.config(image=photo)
                self.thumbnail_label.image = photo
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch video details: {e}")

    def update_size(self, event):
        """Update file size when format is selected."""
        selection = self.quality_combo.current()
        if selection >= 0:
            size_mb = self.formats[selection][2] / (1024**2)
            self.size_label.config(text=f"Size: {size_mb:.2f} MB")


    def progress_hook(self, d):
        """Update progress bar during download."""
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes', 1)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            progress = int(downloaded_bytes / total_bytes * 100)
            self.progress['value'] = progress
            self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
