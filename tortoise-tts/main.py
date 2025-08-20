import sys
import os
import shlex
import subprocess
from datetime import datetime
from moviepy.editor import AudioFileClip, ColorClip
from youtube_upload import upload_video  #import custom upload function for YouTube

#function to generate a new bedtime story video
def generate_new_video():

    #load the story text from file
    with open("story.txt", "r", encoding="utf-8") as f:
        story_text = f.read().strip()

    #generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_name = f"story_{timestamp}"
    audio_path = f"audio_results/{audio_name}.wav"
    video_path = f"results/{audio_name}.mp4"

    #delete old files to keep only recent outputs
    def clean_up_old_files(folder, keep=3, extension=".wav"):
        files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(extension)]
        files.sort(key=os.path.getmtime, reverse=True)
        for f in files[keep:]:
            os.remove(f)
            print(f"🗑️ Deleted old file: {f}")

    #clean audio and video folders
    clean_up_old_files("audio_results", keep=3, extension=".wav")
    clean_up_old_files("results", keep=3, extension=".mp4")

    #create output folders if not already there
    os.makedirs("audio_results", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    #generate audio using tortoise_tts script via subprocess
    print(f"🔊 Generating audio to: {audio_path}")
    venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")  #path to venv python
    subprocess.run([
        venv_python, "scripts/tortoise_tts.py",  #tts script path
        "-o", audio_path,                        #output file path
        "-v", "emma",                            #voice selection
        "-p", "ultra_fast",                      #preset speed
        story_text                               #input text for tts
    ], check=True)

    #create a black screen video with the generated audio
    print(f"🎥 Generating video to: {video_path}")
    audio_clip = AudioFileClip(audio_path)                             #load the generated audio
    duration = audio_clip.duration                                     #get audio duration
    video_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=duration)  #create black screen video
    video_clip = video_clip.set_audio(audio_clip)                      #combine audio with video
    video_clip.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac")  #export final video

    return video_path  #return video file path for optional upload

#function to upload an existing video from results/
def upload_existing_video():
    filename = input("Enter the filename of the video in 'results/' folder (e.g., story_20250710_213615.mp4): ").strip()
    video_path = os.path.join("results", filename)  #build full path
    if not os.path.isfile(video_path):              #check if file exists
        print("❌ File not found. Please check the filename and try again.")
        return
    title = "Black Screen Bedtime Story for Deep Sleep | Calm, Soothing Narration to Help You Fall Asleep Fast"
    description = "Relax with this calm, soothing bedtime story.\n\nSubscribe for more sleep stories every night."
    thumbnail = "thumbnail.jpg"  #default thumbnail
    upload_video(video_path, title, description, thumbnail_file=thumbnail)  #call upload function

#main program logic
print("Choose an option:")
print("1. Generate new bedtime story video")
print("2. Upload an existing video to YouTube")
choice = input("Enter 1 or 2: ").strip()

#if user chooses to generate new video
if choice == "1":
    video_path = generate_new_video()  #generate video and get the path
    upload = input("Do you want to upload this video to YouTube? (y/n): ").strip().lower()
    if upload == "y":
        #define title, description, and thumbnail
        title = "Black Screen Bedtime Story for Deep Sleep | Calm, Soothing Narration to Help You Fall Asleep Fast"
        description = (
            "🌙 Welcome to your nightly escape into calm. This black screen bedtime story is crafted to help you relax, unwind, "
            "and gently drift off into deep, peaceful sleep.\n\n"
            "🖤 Featuring a soothing voice narration over a completely black screen, this video is perfect for:\n"
            "• Falling asleep faster\n"
            "• Reducing anxiety and overthinking\n"
            "• Background storytelling during rest or meditation\n\n"
            "🎧 Best enjoyed with headphones in a quiet room.\n\n"
            "✨ New calming stories every night. Subscribe and turn on the bell so you never miss a moment of peace.\n\n"
            "🛌 Let the words carry you into dreamland. Sleep well.\n\n"
            "#BlackScreenStory #BedtimeStory #FallAsleepFast #SleepNarration "
            "#SoothingVoice #InsomniaRelief #SleepBetter #CalmNarration"
        )
        thumbnail = "thumbnail.jpg"
        upload_video(video_path, title, description, thumbnail_file=thumbnail)  #upload the video

#elif user chooses to upload existing video
elif choice == "2":
    upload_existing_video()

#else invalid input
else:
    print("Invalid choice. Please run again and enter 1 or 2.")

#note: activate the virtual environment before running using "cd tortoise-tts" then ".\.venv\Scripts\activate"
