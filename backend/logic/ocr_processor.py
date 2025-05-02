import pytesseract
from PIL import Image
import numpy as np
import cv2
import os
from pathlib import Path

class OCRProcessor:
    def __init__(self, tesseract_cmd=None, lang="eng+kor"):
        """
        이미지에서 텍스트를 추출하는 OCR 처리기
        
        Args:
            tesseract_cmd: tesseract 실행 파일 경로 (없으면 기본값 사용)
            lang: 언어 설정 (기본: 영어+한국어)
        """
        # Tesseract 경로 설정
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif os.name == 'nt':  # Windows
            default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if Path(default_path).exists():
                pytesseract.pytesseract.tesseract_cmd = default_path
        
        self.lang = lang
        
        # Tesseract가 설치되어 있는지 확인
        try:
            pytesseract.get_tesseract_version()
            print("[OCR] Tesseract 버전:", pytesseract.get_tesseract_version())
        except Exception as e:
            print(f"[OCR 경고] Tesseract가 설치되지 않았거나 경로가 올바르지 않습니다: {e}")
            print("Tesseract OCR 설치 방법:")
            print("- Windows: https://github.com/UB-Mannheim/tesseract/wiki에서 설치")
            print("- macOS: brew install tesseract")
            print("- Linux: sudo apt-get install tesseract-ocr")
            print("설치 후 한국어 언어팩도 설치해 주세요.")
    
    def preprocess_image(self, image):
        """
        OCR 정확도를 높이기 위한 이미지 전처리
        
        Args:
            image: PIL Image 객체 또는 NumPy 배열
            
        Returns:
            전처리된 이미지 (NumPy 배열)
        """
        # PIL Image를 NumPy 배열로 변환
        if isinstance(image, Image.Image):
            img = np.array(image)
        else:
            img = image.copy()
            
        # BGR에서 RGB로 변환 (이미 RGB면 건너뜀)
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 가우시안 블러로 노이즈 제거
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
        # 이미지 대비 향상
        img = cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return img
        
    def extract_text(self, image, preprocess=True):
        """
        이미지에서 텍스트 추출
        
        Args:
            image: PIL.Image 객체 
            preprocess: 전처리 여부 (기본: True)
            
        Returns:
            추출된 텍스트 문자열
        """
        try:
            # 이미지 전처리 
            if preprocess:
                processed_img = self.preprocess_image(image)
                text = pytesseract.image_to_string(processed_img, lang=self.lang)
            else:
                text = pytesseract.image_to_string(image, lang=self.lang)
            
            # 텍스트 정제
            text = ' '.join(text.strip().split())
            
            return text
        except Exception as e:
            print(f"[OCR 오류] 텍스트 추출 실패: {e}")
            return ""