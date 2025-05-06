# 🎵 AURA - AI 감성 음악 생성기

## 🔍 프로젝트 개요
AURA는 이미지 또는 비디오의 분위기와 내용을 AI가 분석하여, 음악을 생성하고 감성적인 결과물을 제공하는 시스템입니다. 다양한 파일 형식을 지원하며, 실시간 음악 생성, 다운로드, 그리고 다국어 챗봇을 통한 사용자 친화적 인터랙션을 제공합니다.

## 📑 목차
- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [사용 방법](#-사용-방법)
- [기술 스택](#-기술-스택)
- [설치 방법](#-설치-방법)
- [프로젝트 구조](#-프로젝트-구조)

## 🛠 주요 기능
1. **콘텐츠 업로드 및 분석**
   - 이미지 (JPG, PNG, GIF 등) 및 비디오 (MP4, AVI, MOV 등) 업로드
   - FastAPI 기반 API
   - BLIP 모델을 통한 콘텐츠 분석
   - 다중 감성 자막 추출 (top_caption, top_captions, all_captions)

2. **맞춤형 음악 생성**
   - Gemini 1.5 Pro를 활용한 감성 프롬프트 생성
   - Meta의 audiocraft MusicGen 모델로 고품질 음악 생성
   - 스테레오 → 모노 오디오 변환

3. **결과물 합성 및 출력**
   - moviepy를 통한 비디오-오디오 합성
   - 생성된 음악 또는 뮤직비디오 자동 재생
   - 최적화된 MP4 출력 및 다운로드 지원

4. **다국어 챗봇**
   - LangChain과 Gemini 1.5 Flash를 활용한 대화형 AI
   - 한국어, 영어, 중국어 지원
   - 사용자 의도 분석 (인사말, 변환 요청, 일반 질문)
   - 지식 베이스 기반 RAG(Retrieval-Augmented Generation)로 정확한 답변 제공
   - 사용자 언어에 맞춘 자연스러운 응답 및 번역 기능

## 🎬 사용 방법
### 1. 이미지 변환
- 이미지 파일을 업로드 영역에 드래그하거나 클릭하여 선택
- 시스템이 이미지를 분석하고 적절한 음악을 생성
- 생성된 음악이 자동 재생되며, 다운로드 가능

### 2. 비디오 변환
- 비디오 파일을 업로드 영역에 드래그하거나 클릭하여 선택
- 시스템이 비디오 내용을 분석하여 맞춤형 음악 생성
- 음악이 포함된 새로운 비디오가 자동 재생되며, 다운로드 가능

### 3. 챗봇 상호작용
- AURA 챗봇과의 대화 
- 예: "이미지를 음악으로 변환해 주세요" 또는 "안녕하세요"
- 챗봇이 사용자의 언어를 감지하고 적절한 응답 제공
- 서비스 정보등

## ⚙️ 기술 스택
### 백엔드
- FastAPI
- Python 3.10
- CUDA 지원
- LangChain (GoogleGenerativeAI, FAISS)

### 프론트엔드
- React
- TypeScript
- Vite
- Shadcn UI

## 🚀 설치 방법
### 1. 백엔드 설정
#### (1) Python 환경 설정
- Python 3.10 이상 설치
- 가상환경 생성 및 활성화

#### (2) CUDA 설치 (cu118 기준)
```bash
pip install torch==2.1.0+cu118 torchvision==0.16.0+cu118 torchaudio==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118
```

#### (3) audiocraft 설치
```bash
pip install git+https://github.com/facebookresearch/audiocraft#egg=audiocraft
```

#### (4) 종속성 설치
- `requirements.txt` 파일을 사용하여 필요한 라이브러리 설치:
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

### 2. 프론트엔드 설정및 실행
#### (1) Node.js 설치
- Node.js (버전 16 이상) 설치: [Node.js 공식 사이트](https://nodejs.org/)에서 다운로드 및 설치
- 설치 확인:
  ```bash
  node -v
  npm -v
  ```

#### (2) 프론트엔드 종속성 설치 및 실행
```bash
cd frontend
npm install
npm run dev
```

### 3. 백엔드 실행
```bash
cd backend
python main.py
```

## 📁 프로젝트 구조
```
AURA2/
├── README.md
├── backend/
│   ├── main.py                # FastAPI 백엔드 메인 서버
│   ├── chatbot.py             # 챗봇 구현
│   ├── runner.py              # 비디오-음악 파이프라인 실행기
│   ├── requirements.txt       # Python 의존성
│   ├── knowledge_base/        # 지식 베이스
│   │   ├── greetings.txt
│   │   └── usage_guide.txt
│   ├── logic/                 # 핵심 로직
│   │   ├── blip_emotion_analyzer.py    # 감정 분석
│   │   ├── frame_extractor.py          # 비디오 프레임 추출
│   │   ├── image_music_generator.py    # 이미지-음악 생성기
│   │   ├── img2music.py               # 이미지-음악 변환
│   │   ├── llm_prompt_refiner.py      # LLM 프롬프트 최적화
│   │   ├── music_generator.py         # 음악 생성기
│   │   └── time_estimator.py         # 처리 시간 추정
│   ├── uploads/               # 업로드 파일 임시 저장
│   └── results/               # 생성 결과 저장
│
└── frontend/
    ├── public/                # 정적 리소스
    │   ├── favicon.ico
    │   ├── placeholder.svg
    │   └── robots.txt
    ├── src/
    │   ├── App.tsx           # React 앱 진입점
    │   ├── App.css           # 글로벌 스타일
    │   ├── components/       # React 컴포넌트
    │   │   ├── Chat/         # 채팅 관련 컴포넌트
    │   │   │   ├── ChatContainer.tsx
    │   │   │   ├── ChatInput.tsx
    │   │   │   └── ChatMessage.tsx
    │   │   ├── FileUpload/   # 파일 업로드 컴포넌트
    │   │   │   └── FileUploader.tsx
    │   │   ├── ImagePreview/ # 이미지 미리보기 컴포넌트
    │   │   │   └── ImagePreview.tsx
    │   │   ├── MusicPlayer/  # 음악 플레이어 컴포넌트
    │   │   │   └── MusicPlayer.tsx
    │   │   ├── VoiceInput/   # 음성 입력 컴포넌트
    │   │   └── ui/           # UI 컴포넌트 라이브러리
    │   └── config/           # 설정 파일
    ├── package.json          # npm 패키지 관리
    └── components.json       # 컴포넌트 설정

```

AURA 팀은 사용자의 피드백을 소중히 생각하며, 서비스를 지속적으로 개선하고 있습니다. AURA로 창의적인 음악 변환을 즐겨보세요!

