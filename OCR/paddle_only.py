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
    use_gpu=False
)

# 이미지 경로
image_paths = [
        r'D:\student\miniproject\Eng\create-a-luxurious-blue-marble-text-effect-5d7ff.jpg',
        r'D:\student\miniproject\Eng\Deep-love-messages-for-her-to-make-her-cry-3.jpg',
        r'D:\student\miniproject\Eng\Deep-love-messages-for-her-to-make-her-cry-4.jpg',
        r'D:\student\miniproject\Eng\Deep-love-messages-for-her-to-make-her-cry.jpg',
        r'D:\student\miniproject\Eng\fill-text-with-image-photoshop-f-1.jpg',
        r'D:\student\miniproject\Eng\Fill-Text-with-Image-Tutorial-Image.jpg',
        r'D:\student\miniproject\Eng\Heart-touching-love-message-to-make-her-cry-1.jpg',
        r'D:\student\miniproject\Eng\Heart-touching-love-message-to-make-her-cry-3.jpg',
        r'D:\student\miniproject\Eng\Heartfelt-Love-Messages-For-Her-To-Make-Her-Cry.jpg',
        r'D:\student\miniproject\Eng\images.jpg',
        r'D:\student\miniproject\Eng\Love-text-to-make-her-cry.jpg',
        r'D:\student\miniproject\Eng\modern-professional-text-efeect-design-260nw-2282740589.jpg',
        r'D:\student\miniproject\Eng\Setting-Up-The-Slide-Text-1000x563.jpg',
        r'D:\student\miniproject\Eng\simple-3d-editable-text-effect-vector.jpg',
        r'D:\student\miniproject\Eng\Touching-Love-Messages-For-Her-3.jpg',
        r'D:\student\miniproject\Eng\Touching-Love-Messages-For-Her-4.jpg',
        r'D:\student\miniproject\Eng\When-a-man-is-prey-to-his-emotions-he-is-not-his-own-master.-Benedict-de-Spinoza.jpg'
    ]
for index, image_path in enumerate(image_paths):
    # 이미지 로드 및 대비 향상
    image = cv2.imread(image_path)
    image = cv2.convertScaleAbs(image, alpha=1.5, beta=0)

    # PaddleOCR 실행
    result = ocr.ocr(image_path, cls=True)

    # 결과 이미지 시각화용 (OpenCV 이미지는 BGR이므로 RGB로 변환)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 결과 파싱
    boxes = [line[0] for line in result[0]]           # 텍스트 영역 박스
    txts = [line[1][0] for line in result[0]]         # 인식된 텍스트
    scores = [line[1][1] for line in result[0]]       # confidence score

    # 결과 이미지 생성
    image_with_ocr = draw_ocr(image_rgb, boxes, txts, scores, font_path='C:/Windows/Fonts/malgun.ttf')
    
    cv2.imwrite(f"paddleocr_result_{index}.jpg", cv2.cvtColor(image_with_ocr, cv2.COLOR_RGB2BGR))

# 텍스트 인식 결과 출력
print("\n--- 인식된 텍스트 목록 ---")
for i, (text, score) in enumerate(zip(txts, scores)):
    print(f"텍스트 {i+1}: {text} (신뢰도: {score:.2f})")

# 출력
# plt.imshow(image_with_ocr)
# plt.axis('off')
# plt.title("OCR 결과 시각화")
# plt.show()
