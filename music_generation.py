from setup import musicgen, musicgen_processor, device
import torchaudio
import os
from pydub import AudioSegment

# 5. 음악 생성 및 저장 (향상된 버전)
def generate_music(prompt, output_path="output_music.mp3", duration_sec=30):
    print(f"음악 생성 중... 프롬프트: {prompt}")
    
    inputs = musicgen_processor(
        text=[prompt], 
        padding=True, 
        return_tensors="pt"
    ).to(device)
    
    # 음악 생성 설정을 더욱 최적화
    audio_values = musicgen.generate(
        **inputs,
        max_new_tokens=1000,  # 더 길고 구조적인 음악 생성
        do_sample=True,       # 샘플링 활성화
        guidance_scale=5.0,   # 프롬프트 반영력 강화
        temperature=0.7,      # 안정적인 음악 생성
    )
    
    sampling_rate = musicgen.config.audio_encoder.sampling_rate
    
    # WAV 파일로 먼저 저장
    temp_wav_path = output_path.replace('.mp3', '_temp.wav')
    torchaudio.save(temp_wav_path, audio_values[0].cpu(), sampling_rate)
    
    # WAV에서 MP3로 변환
    wav_to_mp3(temp_wav_path, output_path)
    
    # 임시 WAV 파일 삭제
    os.remove(temp_wav_path)
    
    print(f"음악 저장 완료: {output_path}")


# WAV를 MP3로 변환하는 함수
def wav_to_mp3(wav_path, mp3_path):
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3", bitrate="192k")
