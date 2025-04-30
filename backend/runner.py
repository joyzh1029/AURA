import os
from logic.frame_extractor import FrameExtractor
from logic.blip_emotion_analyzer import BLIPEmotionAnalyzer
from logic.llm_prompt_refiner import LLMPromptRefiner
from logic.music_generator import MusicGenerator
from moviepy.editor import VideoFileClip, AudioFileClip
import numpy as np
import soundfile as sf

def combine_video_audio(video_path, audio_path, output_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)

    video_with_audio = video.set_audio(audio)
    video_with_audio.write_videofile(output_path, codec='libx264', audio_codec='aac')

    video.close()
    audio.close()

def run_pipeline(video_path: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    filename_only = os.path.splitext(os.path.basename(video_path))[0]
    music_path = os.path.join(output_dir, f"music_{filename_only}.wav")
    result_path = os.path.join(output_dir, f"result_{filename_only}.mp4")

    # [1단계] 프레임 추출
    extractor = FrameExtractor()
    frames = extractor.extract_frames(video_path)

    # [2단계] 감성 문장 생성
    analyzer = BLIPEmotionAnalyzer()
    raw_caption = analyzer.analyze_frames(frames)

    # [3단계] 프롬프트 정제
    refiner = LLMPromptRefiner()
    refined_prompt = refiner.refine_prompt(raw_caption)

    # [4단계] 음악 생성
    clip = VideoFileClip(video_path)
    generator = MusicGenerator()
    music = generator.generate_music(refined_prompt, clip.duration)
    clip.close()

    # [5단계] 음악 저장
    sf.write(music_path, music['audio'], music['sampling_rate'], format='WAV', subtype='FLOAT')

    # [6단계] 비디오+음악 합성
    combine_video_audio(video_path, music_path, result_path)

    return result_path