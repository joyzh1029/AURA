import torch
from PIL import Image
import pytesseract
from transformers import BlipProcessor, BlipForConditionalGeneration
from logic.llm_prompt_refiner import LLMPromptRefiner
from logic.music_generator import MusicGenerator
import uuid
import os

class ImageMusicGenerator:
    def __init__(self, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[INFO] ImageMusicGenerator initialized with device: {self.device}")
        
        # BLIP 모델 로드
        try:
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
            print("[INFO] BLIP model loaded successfully")
        except Exception as e:
            print(f"[ERROR] Failed to load BLIP model: {e}")
            raise

    def generate_music_from_image(self, image_path: str, output_dir: str) -> str:
        """
        이미지로부터 음악을 생성하고 저장 경로를 반환합니다.
        
        Args:
            image_path: 입력 이미지 경로
            output_dir: 출력 음악 파일이 저장될 디렉토리
            
        Returns:
            생성된 음악 파일의 경로
        """
        print(f"[INFO] Processing image: {image_path}")
        
        # 이미지 열기
        try:
            image = Image.open(image_path).convert("RGB")
            print(f"[INFO] Image opened successfully: {image.size}")
        except Exception as e:
            print(f"[ERROR] Failed to open image: {e}")
            raise

        # 1. 이미지 캡셔닝 (BLIP)
        try:
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                output = self.model.generate(**inputs, max_length=50)
            caption = self.processor.decode(output[0], skip_special_tokens=True).strip()
            print(f"[INFO] Generated caption: {caption}")
        except Exception as e:
            print(f"[ERROR] Caption generation failed: {e}")
            # 캡션 생성 실패 시 기본 텍스트 사용
            caption = "An interesting image"
            print(f"[INFO] Using default caption: {caption}")

        # 2. OCR 텍스트 추출
        try:
            ocr_text = pytesseract.image_to_string(image, lang="eng+kor").strip()
            if ocr_text:
                print(f"[INFO] OCR text extracted: {ocr_text[:100]}...")
            else:
                print("[INFO] No OCR text found in image")
        except Exception as e:
            print(f"[WARNING] OCR extraction failed: {e}")
            ocr_text = ""

        # 3. 프롬프트 생성
        try:
            refiner = LLMPromptRefiner()
            if ocr_text:
                prompt = refiner.refine_prompt(caption, [ocr_text])
            else:
                prompt = refiner.refine_prompt(caption)
            print(f"[INFO] Refined prompt: {prompt}")
        except Exception as e:
            print(f"[WARNING] Prompt refinement failed: {e}")
            # 프롬프트 리파이너 실패 시 캡션만 사용
            prompt = f"Create music that captures the mood of: {caption}"
            print(f"[INFO] Using fallback prompt: {prompt}")

        # 4. 음악 생성
        try:
            # 출력 디렉토리 생성 (없는 경우)
            os.makedirs(output_dir, exist_ok=True)
            
            # 고유한 파일명 생성
            output_path = os.path.join(output_dir, f"imagemusic_{uuid.uuid4()}.wav")
            print(f"[INFO] Output music will be saved to: {output_path}")
            
            # 음악 생성기 초기화 및 음악 생성
            generator = MusicGenerator()
            result = generator.generate_music(prompt, duration=10.0)
            
            # 음악 파일 저장
            from scipy.io import wavfile
            wavfile.write(output_path, result['sampling_rate'], result['audio'])
            
            # 파일 존재 확인
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"[INFO] Music file created successfully: {output_path} ({file_size} bytes)")
            else:
                raise FileNotFoundError(f"Expected music file was not created: {output_path}")
                
            return output_path
        except Exception as e:
            print(f"[ERROR] Music generation failed: {e}")
            raise