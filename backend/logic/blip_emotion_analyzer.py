from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from collections import Counter

class BLIPEmotionAnalyzer:
    def __init__(self, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)

    def analyze_frames(self, frames):
        """
        프레임 리스트를 받아, 각 프레임을 BLIP으로 문장으로 해석한다.
        가장 많이 등장한 대표 문장을 반환한다.
        """
        captions = []

        for frame in frames:
            inputs = self.processor(images=frame, return_tensors="pt").to(self.device)
            with torch.no_grad():
                output = self.model.generate(**inputs, max_length=50)
                caption = self.processor.decode(output[0], skip_special_tokens=True)
                captions.append(caption.strip())

        # 다수결 방식으로 가장 자주 등장한 문장 뽑기
        if not captions:
            raise ValueError("프레임에서 문장을 생성할 수 없습니다.")

        counter = Counter(captions)
        top_caption = counter.most_common(1)[0][0]

        return top_caption
