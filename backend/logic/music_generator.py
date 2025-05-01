from transformers import AutoProcessor, MusicgenForConditionalGeneration
import torch
import numpy as np

class MusicGenerator:
    def __init__(self, model_name="facebook/musicgen-small"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = MusicgenForConditionalGeneration.from_pretrained(model_name)
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model.to(self.device)

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
