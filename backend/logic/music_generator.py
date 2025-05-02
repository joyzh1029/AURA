import torch
import numpy as np
from audiocraft.models import MusicGen
from scipy.io.wavfile import write as wav_write
import os

class MusicGenerator:
    def __init__(self, model_name="facebook/musicgen-small"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[INFO] Using device: {self.device}")

        self.model = MusicGen.get_pretrained(model_name)

    def generate_music(self, prompt: str, duration: float, save_path: str) -> None:
        self.model.set_generation_params(
            use_sampling=True,
            top_k=250,
            duration=duration
        )

        print(f"[DEBUG] Generating music ({duration}s) for prompt: {prompt}")
        wav = self.model.generate([prompt])
        audio = wav[0].cpu().numpy()

        # 🎯 Stereo → Mono 변환 (scipy wavfile.write 호환)
        if audio.ndim > 1:
            print(f"[INFO] Stereo detected, converting to mono")
            audio = np.mean(audio, axis=0)

        # 🔒 클리핑 및 int16 변환
        audio = np.clip(audio, -1.0, 1.0)
        audio = (audio * 32767).astype(np.int16)

        print(f"[DEBUG] Final audio shape: {audio.shape}, dtype: {audio.dtype}, max: {audio.max()}, min: {audio.min()}")
        wav_write(save_path, 32000, audio)
        print(f"[INFO] WAV 저장 완료: {save_path}")