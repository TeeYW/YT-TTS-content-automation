from moviepy.editor import AudioFileClip, ColorClip
import os

#create folders if they don't already exist
os.makedirs("results", exist_ok=True)         #create folder to store final video
os.makedirs("audio_results", exist_ok=True)   #create folder to store audio-only .mov file

#load the audio file
audio_path = "output.wav"
audio_clip = AudioFileClip(audio_path)        #load the audio into a MoviePy AudioFileClip object
duration = audio_clip.duration                #get the duration of the audio

#create a black video with the same duration as the audio
video_clip = ColorClip(size=(1920, 1080),     #set video resolution to 1920x1080
                       color=(0, 0, 0),       #set background color to black
                       duration=duration      #match video duration to audio
                      ).set_audio(audio_clip) #add audio to the black video

#export the full video to the results folder
video_clip.write_videofile("results/final_video.mp4", fps=24, codec="libx264", audio_codec="aac")

#export the audio as a .mov file with minimal video track (required for compatibility)
audio_clip.write_videofile("audio_results/final_audio.mov", fps=1, codec="libx264", audio_codec="aac")

