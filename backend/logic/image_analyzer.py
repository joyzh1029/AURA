from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
import torch
from PIL import Image
import numpy as np

class ImageAnalyzer:
    def __init__(self, device=None):
        """
        이미지에서 객체와 장면 정보를 분석하는 클래스
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[ImageAnalyzer] Device: {self.device}")
        
        # 이미지 객체 감지 모델 로드
        self.object_model = AutoModelForZeroShotObjectDetection.from_pretrained(
            "google/owlvit-base-patch32", torch_dtype=torch.float16
        ).to(self.device)
        
        self.object_processor = AutoProcessor.from_pretrained("google/owlvit-base-patch32")
        
    def analyze_image(self, image, candidate_labels=None):
        """
        이미지를 분석하여 객체, 배경, 분위기 정보를 추출
        
        Args:
            image: PIL.Image 객체
            candidate_labels: 선택적으로 검사할 특정 레이블 목록
            
        Returns:
            키워드 목록 {'objects': [...], 'scene': [...]}
        """
        # 기본 후보 레이블이 제공되지 않은 경우
        if candidate_labels is None:
            candidate_labels = [
                # 일반 객체
                "person", "man", "woman", "child", "group of people", "crowd", 
                "dog", "cat", "bird", "car", "building", "tree", "flower", "book",
                "phone", "computer", "table", "chair", "food", "drink",
                
                # 장면/배경
                "indoor", "outdoor", "nature", "urban", "beach", "mountain", "forest",
                "city", "street", "office", "home", "restaurant", "park", "night",
                "day", "sunset", "sunrise", 
                
                # 분위기/감정
                "happy", "sad", "calm", "energetic", "peaceful", "chaotic",
                "romantic", "mysterious", "scary", "cute", "funny", "serious"
            ]
        
        # 객체 감지
        inputs = self.object_processor(
            images=image, 
            text=candidate_labels,
            return_tensors="pt"
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.object_model(**inputs)
            
        # 결과 처리
        target_sizes = torch.tensor([image.size[::-1]])
        results = self.object_processor.post_process_object_detection(
            outputs=outputs,
            target_sizes=target_sizes,
            threshold=0.1  # 낮은 임계값으로 더 많은 객체 감지
        )[0]
        
        # 감지된 객체와 점수
        detected_objects = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            if score >= 0.3:  # 신뢰도가 높은 객체만 포함
                detected_objects.append({
                    "label": candidate_labels[label],
                    "score": float(score),
                    "box": box.tolist()
                })
        
        # 객체 정보를 장면 정보와 일반 객체로 분류
        scene_keywords = []
        object_keywords = []
        
        scene_categories = ["indoor", "outdoor", "nature", "urban", "beach", "mountain", 
                           "forest", "city", "street", "office", "home", "restaurant", 
                           "park", "night", "day", "sunset", "sunrise"]
        
        mood_categories = ["happy", "sad", "calm", "energetic", "peaceful", "chaotic",
                         "romantic", "mysterious", "scary", "cute", "funny", "serious"]
        
        for obj in detected_objects:
            if obj["label"] in scene_categories:
                scene_keywords.append(obj["label"])
            elif obj["label"] in mood_categories:
                scene_keywords.append(obj["label"])
            else:
                object_keywords.append(obj["label"])
        
        # 중복 제거 및 정렬
        scene_keywords = sorted(list(set(scene_keywords)))
        object_keywords = sorted(list(set(object_keywords)))
        
        return {
            "objects": object_keywords,
            "scene": scene_keywords
        }