# AURA
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



1차 troubleshooting 영상에 어울리는 음악이 제작이 안됨 --> 영상분석 결과로 나온 키워드를 문장으로 연결하여 구체적으로 변환
2차 troubleshooting 영상에서 뽑아낸 키워드가 단지 수치로만 감정을 나타내어(예 : 사람이 있다없다만 판별, 색이 어둡다 밝다 판별) 감성인식이 정확하지 않음.
 --> 이것을 blip로 대체하여 blip에서 키워드 추출 --> llm의 개입으로 prompt화 --> musicgen

cuda = pip install torch==2.1.0+cu118 torchvision==0.16.0+cu118 torchaudio==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118
