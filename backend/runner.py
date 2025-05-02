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
    # 처리 파일 저장을 위한 임시 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 영상 결과를 영구적으로 저장할 디렉토리 생성
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # 파일명 생성
    filename_only = os.path.splitext(os.path.basename(video_path))[0]
    timestamp = int(os.path.getmtime(video_path))  # 파일 수정 시간을 TIMESTAMP로 변환
    
    # 임시 처리 파일 경로
    music_path = os.path.join(output_dir, f"music_{filename_only}.wav")
    temp_result_path = os.path.join(output_dir, f"result_{filename_only}.mp4")
    
    # 영상 결과를 영구적으로 저장할 디렉토리 생성
    final_result_path = os.path.join(results_dir, f"aura_video_{filename_only}_{timestamp}.mp4")

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
    combine_video_audio(video_path, music_path, temp_result_path)
    
    # [7단계] 영상 결과를 영구적으로 저장
    import shutil
    shutil.copy2(temp_result_path, final_result_path)
    print(f"영상 결과를 영구적으로 저장: {final_result_path}")
    
    # 반환
    return temp_result_path, final_result_path
