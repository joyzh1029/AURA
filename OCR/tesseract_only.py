import pytesseract
from PIL import Image
import os

# https://github.com/UB-Mannheim/tesseract/wiki 에서 설치
# (이때 설치 과정에서 'korean'이나 영어 이외의 사용할 언어 꼭 추가해야 함)
# 환경변수 (시스템 속성 - 환경 변수 - 시스템 변수의 Path - tesseract 설치한 경로 추가)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# image_path = "" # 이미지 경로(1개)

def ocr_with_options(image_path, lang='eng+kor', config=''):
    """
    언어 및 구성 옵션을 지정하여 OCR 수행
    
    Args:
        image_path (str): 처리할 이미지 파일 경로
        lang (str): 언어 코드 (예: 'eng', 'kor', 'eng+kor')
        config (str): Tesseract 구성 옵션
        
    Returns:
        str: 추출된 텍스트
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=lang, config=config)
        return text
    except Exception as e:
        return f"오류 발생: {str(e)}"

# 신뢰도도 같이 나오는 함수
def ocr_with_boxes(image_path, lang='eng+kor'):
    """
    텍스트 상자 정보와 함께 OCR 수행
    
    Args:
        image_path (str): 처리할 이미지 파일 경로
        lang (str): 언어 코드
        
    Returns:
        list: 텍스트 상자 정보와 인식된 텍스트
    """
    try:
        img = Image.open(image_path)
        
        # 텍스트 상자 및 텍스트 추출
        boxes = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
        
        # 결과 처리
        results = []
        n_boxes = len(boxes['level'])
        for i in range(n_boxes):
            # 신뢰도 점수가 있고 텍스트가 비어있지 않은 경우만 처리
            if boxes['conf'][i] > 0 and boxes['text'][i].strip() != '':
                box_info = {
                    'text': boxes['text'][i],
                    'confidence': boxes['conf'][i],
                }
                results.append(box_info) # 딕셔너리 형태로 저장
        
        return results
        # text = results['text'], confidence = results['confidence'] 형태로 불러와야 함
    except Exception as e:
        return f"오류 발생: {str(e)}"

