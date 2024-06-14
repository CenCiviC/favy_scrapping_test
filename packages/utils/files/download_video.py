from pytube import YouTube
from moviepy.editor import VideoFileClip, concatenate_videoclips
from typing import List, Tuple

from .file_path import public_video_abspath

def download_video_by_url(url, path:str):
    yt = YouTube(url)
    try:
        #최고 해상도 선택
        video = yt.streams.filter(adaptive=True, file_extension='mp4').first()
        if video:
            video.download(filename=path)
            print(f"Downloaded video: {path}")
            return path
        else:
            return None
    except:
        return None


def clip_video(input_video_name: str, timelines :List[Tuple[float, float]],filName:str):
    clips = []
    
    video = VideoFileClip(public_video_abspath(input_video_name))
    
    for startTime, endTime in timelines:    
        clip =video.subclip(startTime, endTime) 
        clips.append(clip)
    final_clip = concatenate_videoclips(clips)
    video_path = public_video_abspath(filName + ".mp4")
    final_clip.write_videofile(video_path, codec="libx264", audio_codec="aac", ffmpeg_params=["-crf", "18", "-preset", "slow", "-b:v", "5000k"])