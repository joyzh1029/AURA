# AURA 비디오 처리 파이프라인 문서

## 개요

AURA 비디오 처리 파이프라인은 사용자가 업로드한 비디오를 분석하고, 비디오의 감정과 분위기에 맞는 음악을 생성하여 원본 비디오와 결합하는 AI 기반 시스템입니다. 이 문서는 전체 처리 과정을 설명합니다.

## 파이프라인 단계

### 1단계: 프레임 추출

```python
# [1단계] 프레임 추출
extractor = FrameExtractor()
frames = extractor.extract_frames(video_path)
```

이 단계에서는 입력 비디오에서 주요 프레임을 추출합니다. 비디오의 시각적 콘텐츠를 분석하기 위해 일정 간격으로 프레임을 샘플링합니다.

### 2단계: 감성 문장 생성

```python
# [2단계] 감성 문장 생성
analyzer = BLIPEmotionAnalyzer()
raw_caption = analyzer.analyze_frames(frames)
```

추출된 프레임은 BLIP(Bootstrapping Language-Image Pre-training) 모델을 통해 분석됩니다. 이 모델은 이미지의 내용을 설명하는 캡션과 감정 분석을 생성합니다.

### 3단계: 프롬프트 정제

```python
# [3단계] 프롬프트 정제
refiner = LLMPromptRefiner()
refined_prompt = refiner.refine_prompt(raw_caption)
```

생성된 캡션은 LLM(Large Language Model)을 통해 정제됩니다. 이 과정에서 음악 생성에 적합한 형태로 프롬프트가 변환됩니다.

### 4단계: 음악 생성

```python
# [4단계] 음악 생성
clip = VideoFileClip(video_path)
generator = MusicGenerator()
music = generator.generate_music(refined_prompt, clip.duration)
clip.close()
```

정제된 프롬프트를 기반으로 비디오 길이에 맞는 음악이 생성됩니다. 음악은 비디오의 감정과 분위기를 반영합니다.

### 5단계: 음악 저장

```python
# [5단계] 음악 저장
sf.write(music_path, music['audio'], music['sampling_rate'], format='WAV', subtype='FLOAT')
```

생성된 음악은 WAV 형식으로 임시 파일에 저장됩니다.

### 6단계: 비디오+음악 합성

```python
# [6단계] 비디오+음악 합성
combine_video_audio(video_path, music_path, temp_result_path)
```

원본 비디오와 생성된 음악이 결합되어 새로운 비디오 파일이 생성됩니다. 이 과정에서 원본 비디오의 시각적 요소와 새로 생성된 음악이 동기화됩니다.

### 7단계: 영상 결과를 영구적으로 저장

```python
# [7단계] 영상 결과를 영구적으로 저장
import shutil
shutil.copy2(temp_result_path, final_result_path)
print(f"영상 결과를 영구적으로 저장: {final_result_path}")
```

처리된 비디오는 임시 디렉토리에서 영구 저장소(results 디렉토리)로 복사됩니다. 이렇게 하면 서버 재시작 후에도 처리된 비디오를 사용할 수 있습니다.

## 반환 값

파이프라인은 두 개의 경로를 반환합니다:
1. `temp_result_path`: 임시 저장 경로 (즉시 스트리밍용)
2. `final_result_path`: 영구 저장 경로 (보관용)

```python
return temp_result_path, final_result_path
```

## 사용 방법

AURA 웹 인터페이스를 통해 15초 이하의 비디오를 업로드하면 자동으로 파이프라인이 실행됩니다. 처리가 완료되면 생성된 비디오가 인터페이스 상단의 보라색 영역에 표시됩니다.

## 기술 스택

- **프레임 추출**: OpenCV
- **감성 분석**: BLIP 모델
- **프롬프트 정제**: Google Gemini
- **음악 생성**: 커스텀 음악 생성 모델
- **비디오 처리**: MoviePy
- **오디오 처리**: SoundFile, NumPy

## 제한 사항

- 비디오 길이는 15초 이하로 제한됩니다.
- 파일 크기는 100MB 이하여야 합니다.
- 지원되는 비디오 형식: MP4, WebM, MOV

---

© 2025 AURA. 이미지, 영상과 음악의 교차점.
