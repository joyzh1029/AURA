import os
from frame_extractor import FrameExtractor
from blip_emotion_analyzer import BLIPEmotionAnalyzer
from llm_prompt_refiner import LLMPromptRefiner
from music_generator import MusicGenerator
from moviepy import VideoFileClip, AudioFileClip
import soundfile as sf
import numpy as np

def combine_video_audio(video_path, audio_path, output_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)

    video_with_audio = video.with_audio(audio)
    video_with_audio.write_videofile(output_path, codec='libx264', audio_codec='aac')

    video.close()
    audio.close()

def main(video_filename):
    base_dir = os.path.dirname(__file__)

    os.makedirs(os.path.join(base_dir, "video"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "music"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "mv_result"), exist_ok=True)

    video_path = os.path.join(base_dir, "video", video_filename)
    music_path = os.path.join(base_dir, "music", f"music_{os.path.splitext(video_filename)[0]}.wav")
    result_path = os.path.join(base_dir, "mv_result", f"result_{os.path.splitext(video_filename)[0]}.mp4")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"비디오 파일을 찾을 수 없습니다: {video_path}")

    print("[1단계] 비디오 프레임 추출 중...")
    extractor = FrameExtractor(interval_sec=1)
    frames = extractor.extract_frames(video_path)
    print(f"\t추출된 프레임 수: {len(frames)}")

    print("[2단계] BLIP 감성 문장 생성 중...")
    analyzer = BLIPEmotionAnalyzer()
    raw_caption = analyzer.analyze_frames(frames)

    if not raw_caption:
        raise ValueError("BLIP에서 감성 문장 생성 실패")

    print(f"\tBLIP 생성 문장: {raw_caption}")

    print("[3단계] Gemini를 이용한 프롬프트 다듬기...")
    refiner = LLMPromptRefiner()
    refined_prompt = refiner.refine_prompt(raw_caption)

    print(f"\t최종 프롬프트: {refined_prompt}")

    print("[4단계] 음악 생성 중...")
    clip = VideoFileClip(video_path)
    duration = clip.duration
    generator = MusicGenerator()
    music = generator.generate_music(refined_prompt, duration)
    clip.close()

    print("[5단계] 음악 파일 저장 중...")
    if not isinstance(music['audio'], np.ndarray):
        raise ValueError("오디오 형식 오류")
    sf.write(music_path, music['audio'], music['sampling_rate'], format='WAV', subtype='FLOAT')

    print("[6단계] 비디오와 음악 합성 중...")
    combine_video_audio(video_path, music_path, result_path)

    print("\n🎉 모든 작업 완료!")
    print(f"결과 파일: {result_path}")

if __name__ == "__main__":
    main("knight2.mp4")  # 여기에 입력할 비디오 파일명