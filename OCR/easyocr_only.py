from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

import easyocr
import cv2
import matplotlib.pyplot as plt

# 이미지 경로 지정
image_paths = []  

# EasyOCR 리더 객체 생성 (한글과 영어 지원)
reader = easyocr.Reader(['ko', 'en'], gpu=False)  # GPU 사용하지 않음

# 이미지에서 텍스트 인식
def detect_text(image_path):
    for image_path in image_paths:
        # 이미지 로드
        image = cv2.imread(image_path)
        
        # 이미지 전처리
        image = cv2.convertScaleAbs(image, alpha=1.5, beta=0)

        # 텍스트 인식
        results = reader.readtext(image_path)

        texts = []
        confidences = []
        
        # 인식된 텍스트와 신뢰도 출력
        # for (bbox, text, confidence) in results:
        #     # 결과 출력
        #     print(f"인식된 텍스트: {text} (신뢰도: {confidence:.2f})")
        #     texts.append(text)
        #     confidences.append(confidence)

    return texts, confidences

# detect_text(image_paths[0])
# 