import torch

class ProcessingTimeEstimator:
    def __init__(self):
        self.base_time = 5  # 기본 처리 시간 (이미지 로딩, 저장 등)
        
    def estimate_processing_time(self, image_size, has_cuda=None):
        """
        이는 이미지 크기와 하드웨어 조건을 기반으로 처리 시간을 추정합니다.
        
        Args:
            image_size: tuple, 이미지크기 (width, height)
            has_cuda: bool, CUDA 지원 여부 (None인 경우 자동 검사)
            
        Returns:
            dict: 총 시간과 각 단계의 예상 시간
        """
        if has_cuda is None:
            has_cuda = torch.cuda.is_available()
            
        # 이미지 크기 요소 계산 (큰 이미지일수록 처리가 느림)
        image_pixels = image_size[0] * image_size[1]
        size_factor = image_pixels / (1024 * 1024)  # 1MP 대비 요소
        
        # 하드웨어와 이미지 크기를 기반으로 각 단계 시간 추정
        blip_time = 3 * size_factor * (0.5 if has_cuda else 2.0)
        ocr_time = 2 * size_factor
        prompt_time = 2
        music_gen_time = 15 * (0.7 if has_cuda else 2.0)  # 음악 생성 시간은 주로 하드웨어에 따라 달라짐
        
        # 총 시간
        total_time = self.base_time + blip_time + ocr_time + prompt_time + music_gen_time
        
        return {
            "total_seconds": round(total_time),
            "steps": {
                "image_processing": round(self.base_time),
                "caption_generation": round(blip_time),
                "ocr_extraction": round(ocr_time),
                "prompt_refinement": round(prompt_time),
                "music_generation": round(music_gen_time)
            }
        }
