import os
from logic.frame_extractor import FrameExtractor
from logic.blip_emotion_analyzer import BLIPEmotionAnalyzer
from logic.llm_prompt_refiner import LLMPromptRefiner
from logic.music_generator import MusicGenerator
from moviepy.editor import VideoFileClip, AudioFileClip
import numpy as np
import time
import wave


def combine_video_audio(video_path, audio_path, output_path):
    video = VideoFileClip(video_path)

    try:
        with wave.open(audio_path, 'rb') as wf:
            print(f"[INFO] 음악 확인 완료: {audio_path}, 길이={wf.getnframes() / wf.getframerate():.2f}s")
    except wave.Error as e:
        raise ValueError(f"[ERROR] 생성된 음악 WAV 파일이 잘못되었습니다: {e}")

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

    # [2단계] 감성 자막 분석
    analyzer = BLIPEmotionAnalyzer()
    analyzer_result = analyzer.analyze_frames(frames)
    top_caption = analyzer_result["top_caption"]
    top_captions = analyzer_result["top_captions"]

    # [3단계] 프롬프트 정제
    refiner = LLMPromptRefiner()
    refined_prompt = refiner.refine_prompt(top_caption, top_captions)

    # [4단계] 음악 생성 및 바로 저장
    clip = VideoFileClip(video_path)
    generator = MusicGenerator()
    generator.generate_music(refined_prompt, clip.duration, music_path)

    try:
        clip.reader.close()
        if clip.audio:
            clip.audio.reader.close_proc()
    except Exception as e:
        print(f"[WARN] Video clip 해제 중 오류: {str(e)}")
    finally:
        clip.close()
        time.sleep(0.5)

    # [5단계] 비디오+음악 합성
    combine_video_audio(video_path, music_path, result_path)

    return result_path