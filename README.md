<<<<<<< HEAD
# AURA
<<<<<<< HEAD
이미지랑 음악을 서로 변환하는 RAG 기반 프로그램

-재훈-

AI 감성 자동 뮤직비디오 생성기
- 입력 비디오 → 프레임 추출 (FrameExtractor)
- 프레임 해석 (BLIPEmotionAnalyzer)
- 감성 기반 프롬프트 생성 (LLMPromptRefiner - Gemini 1.5 Pro)
- 음악 생성 (MusicGenerator - MusicGen-small)
- 비디오+음악 합성 및 결과 저장
  
주요 라이브러리: torch, transformers, google-generativeai, moviepy, soundfile, opencv-python, numpy

주요 모델: BLIP, Gemini 1.5 Pro, MusicGen

주의사항: Torch CUDA 버전 필요, Gemini API Key 준비 필요




cuda = pip install torch==2.1.0+cu118 torchvision==0.16.0+cu118 torchaudio==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118
=======
# AURA Chatbot

이미지와 음악을 서로 변환하는 RAG 기반 프로그램

## 프로젝트 소개

AURA는 이미지와 음악을 상호 변환할 수 있는 혁신적인 AI 챗봇입니다. RAG(Retrieval-Augmented Generation) 기술을 기반으로 하여 사용자가 업로드한 이미지나 음악을 분석하고 변환합니다.

## 시스템 요구사항

### 백엔드
- Python 3.10 이상
- FastAPI
- uvicorn
- 기타 필요한 Python 패키지

### 프론트엔드
- Node.js
- React
- Vite
- TypeScript

## 설치 방법

### 백엔드 설치
```bash
cd backend
pip install -r requirements.txt
```

### 프론트엔드 설치
```bash
cd frontend
npm install
```

## 실행 방법

### 백엔드 서버 실행
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
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
AURA2/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── uploads/
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   └── App.tsx
    ├── public/
    └── package.json
```
>>>>>>> origin/zhouying
=======
>>>>>>> 4ff284a17ad7935b100ea0fc0cbb3c6d75ed67ba
