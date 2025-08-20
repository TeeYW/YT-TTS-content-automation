import os
import tkinter as tk
import ttkbootstrap as tb
from tkinter import filedialog, messagebox
from ttkbootstrap.constants import *
from datetime import datetime
from threading import Thread
import subprocess
from moviepy.editor import AudioFileClip, ColorClip

#set available voice and quality options
VOICE_OPTIONS = ["emma", "random", "tom"]
QUALITY_OPTIONS = ["ultra_fast", "fast", "standard", "high_quality"]

#create main application class
class BedtimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Txt to TTS to YT")
        self.root.geometry("750x750")
        self.thumbnail_file = None
        self.story_file = None

        self.build_ui()

    #build the full GUI layout
    def build_ui(self):
        self.style = tb.Style("darkly")
        pad = {"padx": 10, "pady": 10}

        tb.Label(self.root, text="YT automation", font=("Helvetica", 18, "bold")).pack(**pad)

        #mode selection (file or text)
        self.input_mode = tk.StringVar(value="text")
        mode_frame = tb.Frame(self.root)
        mode_frame.pack(**pad)
        tb.Radiobutton(mode_frame, text="📄 Upload .txt File", variable=self.input_mode, value="file").pack(side="left", padx=15)
        tb.Radiobutton(mode_frame, text="✍️ Type in Story", variable=self.input_mode, value="text").pack(side="left", padx=15)

        #text input box
        self.text_box = tk.Text(self.root, height=10, width=85, font=("Consolas", 10))
        self.text_box.pack(**pad)

        #file selection row
        file_frame = tb.Frame(self.root)
        file_frame.pack(**pad)
        self.file_entry = tb.Entry(file_frame, width=60)
        self.file_entry.pack(side="left", padx=(0, 10))
        tb.Button(file_frame, text="📁 Browse .txt", command=self.load_story_file).pack(side="left")

        #voice and quality dropdowns
        settings_frame = tb.Frame(self.root)
        settings_frame.pack(**pad)
        tb.Label(settings_frame, text="Voice:").grid(row=0, column=0, padx=10)
        self.voice_combo = tb.Combobox(settings_frame, values=VOICE_OPTIONS, state="readonly", width=15)
        self.voice_combo.set("emma")
        self.voice_combo.grid(row=0, column=1, padx=10)
        tb.Label(settings_frame, text="Quality:").grid(row=0, column=2, padx=10)
        self.quality_combo = tb.Combobox(settings_frame, values=QUALITY_OPTIONS, state="readonly", width=15)
        self.quality_combo.set("fast")
        self.quality_combo.grid(row=0, column=3, padx=10)

        #thumbnail selection
        thumb_frame = tb.Frame(self.root)
        thumb_frame.pack(**pad)
        self.thumb_entry = tb.Entry(thumb_frame, width=60)
        self.thumb_entry.pack(side="left", padx=(0, 10))
        tb.Button(thumb_frame, text="🖼️ Browse Thumbnail", command=self.load_thumbnail).pack(side="left")

        #generate and upload button
        tb.Button(self.root, text="🎬 Generate & Upload to YouTube", bootstyle="success", command=self.run_thread).pack(**pad)

        #progress bar
        self.progress = tb.Progressbar(self.root, length=600, mode="determinate")
        self.progress.pack(**pad)

        #status label
        self.status = tb.Label(self.root, text="Waiting...", font=("Helvetica", 10, "italic"))
        self.status.pack()

        #log area
        self.log = tk.Text(self.root, height=10, width=90, font=("Consolas", 10), bg="#1e1e2e", fg="#c7c7c7")
        self.log.pack(pady=15)

    #load story file (.txt) from file dialog
    def load_story_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file:
            self.story_file = file
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file)

    #load thumbnail image from file dialog
    def load_thumbnail(self):
        file = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png")])
        if file:
            self.thumbnail_file = file
            self.thumb_entry.delete(0, tk.END)
            self.thumb_entry.insert(0, file)

    #add a line to the log output
    def log_msg(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    #update the status text and optionally the progress bar
    def update_status(self, msg, progress=None):
        self.status.config(text=msg)
        if progress is not None:
            self.progress["value"] = progress
        self.root.update_idletasks()

    #run main process in separate thread
    def run_thread(self):
        Thread(target=self.run_process).start()

    #main processing flow: read input, generate audio, render video, upload to YouTube
    def run_process(self):
        try:
            self.clean_old_files()
            self.update_status("📝 Reading input...", 5)

            #get story text from file or textbox
            if self.input_mode.get() == "file":
                if not self.story_file:
                    self.log_msg("❌ No file selected.")
                    return
                with open(self.story_file, "r", encoding="utf-8") as f:
                    story_text = f.read().strip()
            else:
                story_text = self.text_box.get("1.0", tk.END).strip()
                if not story_text:
                    self.log_msg("❌ Please type something.")
                    return

            #build file paths using timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = f"audio_results/story_{timestamp}.wav"
            video_path = f"results/story_{timestamp}.mp4"
            os.makedirs("audio_results", exist_ok=True)
            os.makedirs("results", exist_ok=True)

            #tts generation using subprocess
            voice = self.voice_combo.get()
            quality = self.quality_combo.get()
            venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")

            self.update_status("🔊 Generating audio...", 20)
            self.log_msg(f"🎤 Using voice='{voice}', quality='{quality}'")

            subprocess.run([
                venv_python, "scripts/tortoise_tts.py",
                "-o", audio_path,
                "-v", voice,
                "-p", quality,
                story_text
            ], check=True)

            #generate black screen video
            self.update_status("🎥 Rendering video...", 60)
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            self.log_msg(f"⏱ Estimated duration: {int(duration)}s")

            video_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=duration)
            video_clip = video_clip.set_audio(audio_clip)
            video_clip.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac")

            #upload to YouTube
            self.update_status("☁️ Uploading to YouTube...", 85)
            from youtube_upload import upload_video
            title = "Black Screen Bedtime Story for Deep Sleep | Calm, Soothing Narration"
            description = (
                "🌙 Drift into sleep with this calm black screen bedtime story.\n\n"
                "🎧 Best with headphones in a dark room.\n"
                "#BedtimeStory #BlackScreen #SleepNarration"
            )
            link = upload_video(video_path, title, description, thumbnail_file=self.thumbnail_file)
            if link:
                self.log_msg(f"✅ Upload complete!\n🔗 YouTube Link: {link}")
            else:
                self.log_msg("⚠️ Upload completed, but link was not retrieved.")

            self.update_status("✅ All Done!", 100)

        except Exception as e:
            self.log_msg(f"❌ Error: {str(e)}")
            self.update_status("⚠️ Failed", 0)

    #delete all but the 3 latest audio/video files
    def clean_old_files(self):
        self.log_msg("🧹 Cleaning previous files (keeping latest 3)...")
        folders = ["audio_results", "results"]

        for folder in folders:
            if not os.path.exists(folder):
                continue

            #sort files by last modified time
            files = sorted(
                [os.path.join(folder, f) for f in os.listdir(folder)],
                key=lambda x: os.path.getmtime(x),
                reverse=True
            )

            #remove all but the 3 most recent
            for file_path in files[3:]:
                try:
                    os.remove(file_path)
                    self.log_msg(f"🗑 Removed old file: {os.path.basename(file_path)}")
                except Exception as e:
                    self.log_msg(f"⚠️ Could not delete {file_path}: {e}")

#run the application
if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = BedtimeApp(root)
    root.mainloop()
