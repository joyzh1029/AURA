# 🎬 AI 감성 자동 뮤직비디오 생성기

AI가 비디오를 분석하여 감성적인 자막을 추출하고, 이를 바탕으로 음악을 작곡한 뒤 비디오와 합성하여 감성 뮤직비디오를 자동으로 생성하는 프로젝트입니다.

---

## 🧩 주요 기능 구성

1. **입력 비디오 업로드 (FastAPI)**
   - 클라이언트에서 비디오를 업로드하면 `/upload-video/` API가 이를 수신함
   - 용량 제한: **100MB 이하**

2. **[1단계] 프레임 추출**
   - 모듈: `frame_extractor.py`
   - 클래스: `FrameExtractor`
   - OpenCV로 비디오를 1초 간격으로 추출 → `PIL.Image`로 변환

3. **[2단계] 감성 분석 (BLIP 기반 자막 생성)**
   - 모듈: `blip_emotion_analyzer.py`
   - 클래스: `BLIPEmotionAnalyzer`
   - 모델: `Salesforce/blip-image-captioning-base`
   - 프레임 별 자막 생성 후 가장 자주 등장하는 문장을 `top_caption`으로 추출
   - 자주 등장하는 상위 5개 문장은 `top_captions`로 반환

4. **[3단계] 감성 기반 프롬프트 생성 (Gemini 1.5 Pro)**
   - 모듈: `llm_prompt_refiner.py`
   - 클래스: `LLMPromptRefiner`
   - `.env` 파일에 `GOOGLE_API_KEY` 필요
   - Gemini가 감성적인 음악 프롬프트를 영어로 생성  
     예: `"A soft classical piano melody echoing through a tranquil library..."`

5. **[4단계] 음악 생성 (audiocraft MusicGen)**
   - 모듈: `music_generator.py`
   - 클래스: `MusicGenerator`
   - 모델: `facebook/musicgen-small`
   - 프롬프트 기반 음악 생성 → WAV 파일 저장 (Stereo → Mono 변환)

6. **[5단계] 비디오 + 음악 합성**
   - 모듈: `runner.py`
   - 함수: `combine_video_audio`
   - `moviepy`를 사용하여 `.mp4`로 합성 출력

7. **[6단계] 최종 결과 전송**
   - `/upload-video/` API가 최종 `.mp4` 파일을 `StreamingResponse`로 반환

---

## 🔧 사용 라이브러리

```
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
```

---

## ⚠️ 사용 전 준비 사항

### 1. CUDA 버전 Torch 설치 (cu118 기준)

```bash
pip install torch==2.1.0+cu118 torchvision==0.16.0+cu118 torchaudio==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118
```

### 프론트엔드 설치
- Node.js 설치
https://nodejs.org/ko

```bash
cd frontend
npm install
```

---

### 백엔드 서버 실행
```bash
cd backend
python main.py
```

### 프론트엔드 개발 서버 실행
```bash
cd frontend
npm run dev
```

## 주요 기능

1. 이미지 업로드
   - 단일 이미지 업로드
   - 다중 이미지 업로드 지원
   - 이미지 미리보기

2. 음악 변환
   - 이미지에서 음악으로 변환
   - 음악 재생 기능

3. 대화형 인터페이스
   - 직관적인 채팅 인터페이스
   - 실시간 응답

## 기술 스택

### 백엔드
- FastAPI
- Python
- uvicorn

### 프론트엔드
- React
- TypeScript
- Vite
- Shadcn UI
- TanStack Query

## 프로젝트 구조

```
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
```

