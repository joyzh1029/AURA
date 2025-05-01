import torch
from PIL import Image
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
    AutoProcessor,
    MusicgenForConditionalGeneration,
)
import torchaudio
import os
import random
import tkinter as tk
from tkinter import filedialog, simpledialog
import scipy.io.wavfile as wav
from pydub import AudioSegment
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy

# NLTK 리소스 다운로드
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# spaCy 모델 로드 (처음 실행 시 다운로드 필요)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy 모델 다운로드 중...")
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# 디바이스 설정
device = "cuda" if torch.cuda.is_available() else "cpu"

# 1. BLIP 로드 (이미지 캡션 생성기)
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(device)

# 2. MusicGen 로드 (음악 생성기)
musicgen = MusicgenForConditionalGeneration.from_pretrained(
    "facebook/musicgen-small",
    attn_implementation="eager"  # 느려짐 방지
).to(device)

musicgen_processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
