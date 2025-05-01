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
        가장 자주 등장한 문장(top_caption), 상위 자막 리스트(top_captions), 전체 자막 리스트(all_captions)를 반환한다.
        """
        captions = []

        for frame in frames:
            inputs = self.processor(images=frame, return_tensors="pt").to(self.device)
            with torch.no_grad():
                output = self.model.generate(**inputs, max_length=50)
                caption = self.processor.decode(output[0], skip_special_tokens=True)
                captions.append(caption.strip())

        if not captions:
            raise ValueError("프레임에서 문장을 생성할 수 없습니다.")

        counter = Counter(captions)
        top_caption = counter.most_common(1)[0][0]
        top_captions = [cap for cap, _ in counter.most_common(5)]

        return {
            "top_caption": top_caption,
            "top_captions": top_captions,
            "all_captions": captions
        }
