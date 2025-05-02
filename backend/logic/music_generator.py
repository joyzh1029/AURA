from transformers import AutoProcessor, MusicgenForConditionalGeneration
import torch
import numpy as np

class MusicGenerator:
    def __init__(self, model_name="facebook/musicgen-small"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = MusicgenForConditionalGeneration.from_pretrained(model_name)
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model.to(self.device)
        print(f"[MusicGen] Device: {self.device}")

    def generate_music(self, prompt: str, duration: float):
        try:
            print(f"[MusicGen] 생성 프롬프트: {prompt}")
            inputs = self.processor(
                text=[prompt],
                padding=True,
                return_tensors="pt",
            ).to(self.device)

            # duration * 50: 초당 50 프레임 기준
            max_len = int(duration * 50)
            audio_values = self.model.generate(
                **inputs,
                max_length=max_len,
                do_sample=True,
            )

            audio_data = audio_values.cpu().numpy().squeeze()
            audio_data = audio_data / np.abs(audio_data).max()
            audio_data = audio_data.astype(np.float32)

            return {
                'audio': audio_data,
                'sampling_rate': self.model.config.audio_encoder.sampling_rate
            }

        except Exception as e:
            print(f"[MusicGen 오류] 음악 생성 실패: {str(e)}")
            raise
            
    # *변경됨: 이미지 기반 음악 생성 헬퍼 메소드 추가 (hwaseop)
    def generate_from_image_prompt(self, image_prompt: str, duration: float = 15.0):
        """
        이미지 분석 결과로부터 음악 생성
        
        Args:
            image_prompt: 이미지 분석 결과로 생성된 음악 생성 프롬프트
            duration: 생성할 음악 길이(초)
            
        Returns:
            오디오 데이터와 샘플링 레이트
        """
        # 이미지 분석 결과에 음악 스타일 힌트 추가
        enhanced_prompt = f"Create music that reflects the mood and elements in this scene: {image_prompt}"
        
        return self.generate_music(enhanced_prompt, duration)