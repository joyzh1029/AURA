import cv2
from PIL import Image
import numpy as np

class FrameExtractor:
    def __init__(self, interval_sec=1):
        """
        interval_sec: 몇 초마다 프레임을 추출할지 (기본 1초)
        """
        self.interval_sec = interval_sec

    def extract_frames(self, video_path):
        """
        비디오에서 일정 간격으로 프레임 추출 (PIL.Image 리스트 반환)
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise IOError(f"비디오를 열 수 없습니다: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        interval_frames = int(fps * self.interval_sec)

        frames = []
        frame_idx = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % interval_frames == 0:
                # BGR(OpenCV) -> RGB(PIL)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                frames.append(pil_image)

            frame_idx += 1

        cap.release()
        return frames