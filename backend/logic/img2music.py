"""
img2audio.py - AI를 사용하여 이미지를 오디오로 변환
이미지에서 키워드와 텍스트를 추출하고, 설명을 생성하고, 음악을 생성합니다
"""

import os
import torch
import numpy as np
from PIL import Image
import tempfile
import logging
from pathlib import Path
from typing import Tuple, Dict, List, Optional, Union
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenMP 충돌 방지를 위한 환경 변수
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# CUDA 사용 가능 여부 확인
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device: {DEVICE}")

# VRAM 사용량 추적
def log_gpu_memory():
    if torch.cuda.is_available():
        logger.info(f"GPU Memory allocated: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
        logger.info(f"GPU Memory cached: {torch.cuda.memory_cached(0) / 1024**2:.2f} MB")

# ===== 이미지 분석 모듈 =====

def load_blip_model():
    """가볍게 최적화된 BLIP 이미지 캐프션 모델 로드"""
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        
        # VRAM 절약을 위해 더 작은 BLIP 모델 사용
        model_name = "Salesforce/blip-image-captioning-base"
        
        # 프로세서와 모델 로드
        processor = BlipProcessor.from_pretrained(model_name)
        model = BlipForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.float16)
        
        # 모델을 적절한 장치로 이동
        model = model.to(DEVICE)
        
        log_gpu_memory()
        return processor, model
    except Exception as e:
        logger.error(f"Error loading BLIP model: {e}")
        return None, None

def extract_image_keywords(image_path: str) -> str:
    """BLIP를 사용하여 이미지에서 키워드와 설명 추출"""
    try:
        # 이미지 로드
        raw_image = Image.open(image_path).convert('RGB')
        
        # BLIP 모델 로드
        processor, model = load_blip_model()
        if processor is None or model is None:
            return "Error loading image analysis model"
            
        # 이미지 처리
        inputs = processor(raw_image, return_tensors="pt").to(DEVICE, torch.float16)
        
        # 캐프션 생성
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=50)
            caption = processor.decode(outputs[0], skip_special_tokens=True)
        
        # 처리 후 CUDA 캐시 정리
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info(f"Image caption: {caption}")
        return caption
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return "Failed to analyze image"

# ===== OCR 모듈 =====

def perform_ocr(image_path: str) -> str:
    """OCR을 사용하여 이미지에서 텍스트 추출"""
    try:
        # 필요하지 않을 때 로딩을 피하기 위해 여기서 가져오기
        import pytesseract
        from PIL import Image
        
        # 이미지 열기
        image = Image.open(image_path)
        
        # OCR 수행
        text = pytesseract.image_to_string(image)
        
        # 텍스트 정리 및 반환
        cleaned_text = text.strip()
        logger.info(f"OCR extracted text: {cleaned_text}")
        return cleaned_text
    except ImportError:
        logger.warning("Pytesseract not installed. Installing...")
        import subprocess
        try:
            subprocess.check_call(["pip", "install", "pytesseract"])
            # 설치 후 다시 시도
            import pytesseract
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"Could not install or use pytesseract: {e}")
            return ""
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""

# ===== 텍스트 처리 모듈 =====

def generate_description(image_caption: str, ocr_text: str) -> str:
    """이미지 분석과 OCR 텍스트를 통합하여 일관된 설명 생성"""
    
    # Import here to reduce initial memory footprint
    try:
        from transformers import pipeline
        
        # 의미 있는 입력이 없는 경우 빈 값 반환
        if not image_caption and not ocr_text:
            return ""
            
        # 입력이 하나만 있는 경우 그대로 반환
        if not ocr_text:
            return image_caption
        if not image_caption:
            return ocr_text
            
        # 텍스트 생성을 위한 입력 생성
        input_text = f"Image shows: {image_caption}. Text in the image: {ocr_text}."
        
        # 가볍게 텍스트 생성기 사용
        generator = pipeline('text-generation', 
                            model='distilgpt2',
                            device=0 if torch.cuda.is_available() else -1)
        
        # 일관된 설명 생성
        result = generator(input_text, 
                          max_length=100, 
                          num_return_sequences=1, 
                          temperature=0.7)
        
        # 생성된 텍스트 추출 및 정리
        generated_text = result[0]['generated_text']
        
        # CUDA 캐시 정리
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info(f"Generated description: {generated_text}")
        return generated_text
    except Exception as e:
        logger.error(f"Error generating description: {e}")
        # 단순 묶기로 대체
        if ocr_text:
            return f"{image_caption}. The image contains text that reads: {ocr_text}"
        return image_caption

# ===== 음악 생성 모듈 =====

def setup_musicgen():
    """낮은 VRAM 사용을 위해 최적화된 MusicGen 모델 설정"""
    try:
        # 라이브러리 가져오기
        from audiocraft.models import MusicGen
        import torch
        
        # VRAM 절약을 위해 사용 가능한 가장 작은 모델 사용
        model = MusicGen.get_pretrained("facebook/musicgen-small", device=DEVICE)
        
        # 추론을 위한 모델 최적화
        model.set_generation_params(
            duration=5,  # 더 짧은 클립 생성 (5초)
            temperature=1.0,
            top_k=250,
            top_p=0.0,
        )
        
        log_gpu_memory()
        return model
    except ImportError:
        logger.warning("AudioCraft not installed. Installing...")
        import subprocess
        try:
            # AudioCraft 설치
            subprocess.check_call(["pip", "install", "audiocraft"])
            # Try again
            from audiocraft.models import MusicGen
            model = MusicGen.get_pretrained("facebook/musicgen-small", device=DEVICE)
            model.set_generation_params(duration=5, temperature=1.0)
            return model
        except Exception as e:
            logger.error(f"Could not install or use AudioCraft: {e}")
            return None
    except Exception as e:
        logger.error(f"Error setting up MusicGen: {e}")
        return None

def generate_music(description: str, output_dir: str) -> Optional[str]:
    """텍스트 설명을 기반으로 음악 생성"""
    try:
        # 음악 생성 모델 설정
        model = setup_musicgen()
        if model is None:
            return None
            
        # 음악 생성을 위한 프롬프트 생성
        prompt = f"Create music that captures the essence of: {description}"
        logger.info(f"Music generation prompt: {prompt}")
        
        # 음악 생성
        wav = model.generate([prompt], progress=True)
        
        # 생성된 오디오 저장
        output_path = os.path.join(output_dir, f"generated_{int(time.time())}.wav")
        
        # numpy로 변환하고 저장
        audio_data = wav[0].cpu().numpy()
        
        # SoundFile를 사용하여 저장
        import soundfile as sf
        sf.write(output_path, audio_data, samplerate=32000)
        
        # CUDA 캐시 정리
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info(f"Music saved to {output_path}")
        return output_path
    except ImportError:
        logger.warning("SoundFile not installed. Installing...")
        import subprocess
        try:
            subprocess.check_call(["pip", "install", "soundfile"])
            # Try again
            import soundfile as sf
            # (continue the function)
            return None  # For simplicity in this error handler
        except Exception as e:
            logger.error(f"Could not install or use SoundFile: {e}")
            return None
    except Exception as e:
        logger.error(f"Music generation error: {e}")
        return None

# ===== 메인 처리 파이프라인 =====

def process_image(image_path: str, output_dir: str = "outputs") -> Dict[str, str]:
    """
    이미지를 처리하여 오디오 생성:
    1. 이미지에서 키워드/캐프션 추출
    2. 텍스트가 있는 경우 OCR 수행
    3. 일관된 설명 생성
    4. 설명을 기반으로 음악 생성
    """
    os.makedirs(output_dir, exist_ok=True)
    
    results = {
        "image_path": image_path,
        "caption": "",
        "ocr_text": "",
        "description": "",
        "audio_path": None,
        "error": None
    }
    
    try:
        # Step 1: Extract image information using BLIP
        logger.info(f"Analyzing image: {image_path}")
        image_caption = extract_image_keywords(image_path)
        results["caption"] = image_caption
        
        # Step 2: Perform OCR
        logger.info("Performing OCR on image")
        ocr_text = perform_ocr(image_path)
        results["ocr_text"] = ocr_text
        
        # Step 3: Generate a coherent description
        logger.info("Generating description")
        description = generate_description(image_caption, ocr_text)
        results["description"] = description
        
        # Step 4: Generate music
        logger.info("Generating music based on description")
        audio_path = generate_music(description, output_dir)
        results["audio_path"] = audio_path
        
        logger.info("Processing complete")
        return results
    
    except Exception as e:
        logger.error(f"Error in processing pipeline: {e}")
        results["error"] = str(e)
        return results

# 직접 실행하는 경우
if __name__ == "__main__":
    # 인자로 제공된 경우 샘플 이미지로 테스트
    import sys
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Processing image: {image_path}")
        result = process_image(image_path)
        print(f"Results: {result}")
    else:
        print("인자로 이미지 경로를 제공해주세요")