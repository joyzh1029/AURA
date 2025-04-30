import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import cv2
from paddleocr import PaddleOCR, draw_ocr
import matplotlib.pyplot as plt

# PaddleOCR 초기화
ocr = PaddleOCR(
    use_angle_cls=True,      # 글자 방향 감지
    lang='korean',           # 한국어 (한글 + 영문 포함)
    det_db_box_thresh=0.3,   # 박스 감지 임계값 (기본값: 0.5)
    det_db_unclip_ratio=2.0, # 박스 확대 비율
    use_gpu=False,
    show_log=False 
)

# backend\uploads\image
def detect_ocr () :
    # 들어온 이미지, 경로 설정
    image_paths = [ ]

    for index, image_path in enumerate(image_paths):
        # 이미지 로드 및 대비 향상
        image = cv2.imread(image_path)
        image = cv2.convertScaleAbs(image, alpha=1.5, beta=0)

        # PaddleOCR 실행
        result = ocr.ocr(image_path, cls=True)

        # 결과 파싱
        # boxes = [line[0] for line in result[0]]           # 텍스트 영역 박스
        txts = [line[1][0] for line in result[0]]         # 인식된 텍스트
        scores = [line[1][1] for line in result[0]]       # 신뢰도 점수

    # 텍스트 인식 결과 출력
    # print("\n--- 인식된 텍스트 목록 ---")
    # for i, (text, score) in enumerate(zip(txts, scores)):
    #     print(f"텍스트 {i+1}: {text} (신뢰도: {score:.2f})")

    return txts, scores

