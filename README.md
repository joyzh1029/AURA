# AURA

AI 감성 자동 뮤직비디오 생성기

🧩 주요 기능 구성

1. 입력 비디오 업로드 (FastAPI)
   - 클라이언트에서 비디오를 업로드하면 `/upload-video/` API가 이를 수신함
   - 용량 제한: 100MB 이하

2. [1단계] 프레임 추출
   - 모듈: frame_extractor.py
   - 클래스: FrameExtractor
   - OpenCV로 비디오를 1초 간격으로 추출 → PIL.Image로 변환

3. [2단계] 감성 분석 (BLIP 기반 자막 생성)
   - 모듈: blip_emotion_analyzer.py
   - 클래스: BLIPEmotionAnalyzer
   - HuggingFace의 Salesforce/blip-image-captioning-base 사용
   - 프레임 별 자막 생성 후 가장 자주 등장하는 문장을 top_caption으로 추출
   - 자주 등장하는 상위 5개 문장을 top_captions로 반환

4. [3단계] 감성 기반 프롬프트 생성 (Gemini 1.5 Pro)
   - 모듈: llm_prompt_refiner.py
   - 클래스: LLMPromptRefiner
   - .env 파일에 있는 GOOGLE_API_KEY 필요
   - Gemini 모델이 감성적 음악 프롬프트를 영어로 생성함
   - 예시 출력: "A soft classical piano melody echoing through a tranquil library..."

5. [4단계] 음악 생성 (audiocraft MusicGen)
   - 모듈: music_generator.py
   - 클래스: MusicGenerator
   - facebook/musicgen-small 모델 사용
   - 프롬프트 기반 음악 생성 → WAV 파일로 저장
   - Stereo → Mono 변환 및 WAV 클립 저장

6. [5단계] 비디오 + 음악 합성
   - 모듈: runner.py 내부 함수 combine_video_audio
   - moviepy를 사용해 오디오를 비디오에 삽입하여 .mp4로 출력

7. [6단계] 최종 결과 전송
   - /upload-video/ API가 최종 .mp4 파일을 StreamingResponse로 반환

🔧 사용 라이브러리
torch
transformers
google-generativeai
audiocraft
moviepy
opencv-python
Pillow
numpy
scipy
fastapi
python-dotenv

⚠️ 사용 전 준비 사항

1. CUDA 버전 Torch 설치 (cu118 기준):
pip install torch==2.1.0+cu118 torchvision==0.16.0+cu118 torchaudio==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118

2. 환경 변수 설정 (.env):
GOOGLE_API_KEY=your_actual_gemini_key

📁 폴더 구조 예시
project_root/
├── main.py
├── runner.py
├── logic/
│   ├── frame_extractor.py
│   ├── blip_emotion_analyzer.py
│   ├── llm_prompt_refiner.py
│   └── music_generator.py
├── uploads/
├── frontend/public/
├── .env
