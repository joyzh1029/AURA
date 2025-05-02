from .llm_prompt_refiner import LLMPromptRefiner
from .image_analyzer import ImageAnalyzer
from .ocr_processor import OCRProcessor

class ImageToPrompt:
    def __init__(self, api_key=None):
        """
        이미지 분석과 OCR 결과를 기반으로 음악 생성 프롬프트를 생성하는 클래스
        
        Args:
            api_key: Gemini API 키 (없으면 환경 변수에서 읽음)
        """
        self.image_analyzer = ImageAnalyzer()
        self.ocr_processor = OCRProcessor()
        self.prompt_refiner = LLMPromptRefiner(api_key)
        
    def create_prompt_from_image(self, image):
        """
        이미지를 분석하여 음악 생성 프롬프트 생성
        
        Args:
            image: PIL.Image 객체
            
        Returns:
            음악 생성용 프롬프트 문자열
        """
        # 1. 이미지 분석하여 키워드 추출
        keywords = self.image_analyzer.analyze_image(image)
        
        # 2. OCR로 텍스트 추출
        text = self.ocr_processor.extract_text(image)
        
        # 3. 분석 결과를 기반으로 기본 설명 구성
        description = self._create_description(keywords, text)
        
        # 4. LLM으로 최종 프롬프트 생성
        prompt = self.prompt_refiner.refine_prompt(description)
        
        return prompt
    
    def _create_description(self, keywords, text):
        """
        키워드와 OCR 텍스트로부터 기본 설명 생성
        
        Args:
            keywords: {'objects': [...], 'scene': [...]} 형태의 키워드 사전
            text: OCR로 추출한 텍스트
            
        Returns:
            기본 설명 문자열
        """
        description_parts = []
        
        # 객체 정보 추가
        if keywords["objects"]:
            objects_str = ", ".join(keywords["objects"])
            description_parts.append(f"객체: {objects_str}")
        
        # 장면/분위기 정보 추가
        if keywords["scene"]:
            scene_str = ", ".join(keywords["scene"])
            description_parts.append(f"장면: {scene_str}")
        
        # OCR 텍스트 추가 (있는 경우에만)
        if text and len(text.strip()) > 0:
            description_parts.append(f"텍스트: {text}")
        
        # 최종 설명 조합
        description = ". ".join(description_parts)
        
        return description