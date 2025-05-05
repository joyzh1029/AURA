import torch

class ProcessingTimeEstimator:
    def __init__(self):
        self.base_time = 5  # 基础处理时间（图片加载、保存等）
        
    def estimate_processing_time(self, image_size, has_cuda=None):
        """
        基于图片大小和硬件条件估算处理时间
        
        Args:
            image_size: tuple, 图片尺寸 (width, height)
            has_cuda: bool, 是否有CUDA支持（如果为None则自动检测）
            
        Returns:
            dict: 包含总预计时间和各步骤预计时间
        """
        if has_cuda is None:
            has_cuda = torch.cuda.is_available()
            
        # 计算图片大小因子（越大的图片处理越慢）
        image_pixels = image_size[0] * image_size[1]
        size_factor = image_pixels / (1024 * 1024)  # 相对于1MP的因子
        
        # 基于硬件和图片大小估算各步骤时间
        blip_time = 3 * size_factor * (0.5 if has_cuda else 2.0)
        ocr_time = 2 * size_factor
        prompt_time = 2
        music_gen_time = 15 * (0.7 if has_cuda else 2.0)  # 音乐生成时间主要取决于硬件
        
        # 总时间
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
