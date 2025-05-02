"""
img2audio.py - Convert images to audio using AI
Extracts keywords and text from images, creates descriptions, and generates music
"""

import os
import torch
import numpy as np
from PIL import Image
import tempfile
import logging
from pathlib import Path
from typing import Tuple, Dict, List, Optional, Union
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variable to prevent OpenMP conflicts
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Check CUDA availability
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Using device: {DEVICE}")

# Track VRAM usage
def log_gpu_memory():
    if torch.cuda.is_available():
        logger.info(f"GPU Memory allocated: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
        logger.info(f"GPU Memory cached: {torch.cuda.memory_cached(0) / 1024**2:.2f} MB")

# ===== IMAGE ANALYSIS MODULE =====

def load_blip_model():
    """Load BLIP image captioning model (lightweight version)"""
    try:
        from transformers import BlipProcessor, BlipForConditionalGeneration
        
        # Use the smaller BLIP model to conserve VRAM
        model_name = "Salesforce/blip-image-captioning-base"
        
        # Load processor and model
        processor = BlipProcessor.from_pretrained(model_name)
        model = BlipForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.float16)
        
        # Move model to appropriate device
        model = model.to(DEVICE)
        
        log_gpu_memory()
        return processor, model
    except Exception as e:
        logger.error(f"Error loading BLIP model: {e}")
        return None, None

def extract_image_keywords(image_path: str) -> str:
    """Extract keywords and description from image using BLIP"""
    try:
        # Load image
        raw_image = Image.open(image_path).convert('RGB')
        
        # Load BLIP model
        processor, model = load_blip_model()
        if processor is None or model is None:
            return "Error loading image analysis model"
            
        # Process image
        inputs = processor(raw_image, return_tensors="pt").to(DEVICE, torch.float16)
        
        # Generate caption
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=50)
            caption = processor.decode(outputs[0], skip_special_tokens=True)
        
        # Clear CUDA cache after processing
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info(f"Image caption: {caption}")
        return caption
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return "Failed to analyze image"

# ===== OCR MODULE =====

def perform_ocr(image_path: str) -> str:
    """Extract text from images using OCR"""
    try:
        # Import here to avoid loading if not needed
        import pytesseract
        from PIL import Image
        
        # Open image
        image = Image.open(image_path)
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        # Clean and return text
        cleaned_text = text.strip()
        logger.info(f"OCR extracted text: {cleaned_text}")
        return cleaned_text
    except ImportError:
        logger.warning("Pytesseract not installed. Installing...")
        import subprocess
        try:
            subprocess.check_call(["pip", "install", "pytesseract"])
            # Try again after installation
            import pytesseract
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"Could not install or use pytesseract: {e}")
            return ""
    except Exception as e:
        logger.error(f"OCR error: {e}")
        return ""

# ===== TEXT PROCESSING MODULE =====

def generate_description(image_caption: str, ocr_text: str) -> str:
    """Combine image analysis and OCR text into a coherent description"""
    
    # Import here to reduce initial memory footprint
    try:
        from transformers import pipeline
        
        # If we don't have meaningful inputs, return empty
        if not image_caption and not ocr_text:
            return ""
            
        # If we only have one input, return it
        if not ocr_text:
            return image_caption
        if not image_caption:
            return ocr_text
            
        # Create input for text generation
        input_text = f"Image shows: {image_caption}. Text in the image: {ocr_text}."
        
        # Use a lightweight text generator
        generator = pipeline('text-generation', 
                            model='distilgpt2',
                            device=0 if torch.cuda.is_available() else -1)
        
        # Generate a coherent description
        result = generator(input_text, 
                          max_length=100, 
                          num_return_sequences=1, 
                          temperature=0.7)
        
        # Extract and clean generated text
        generated_text = result[0]['generated_text']
        
        # Clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info(f"Generated description: {generated_text}")
        return generated_text
    except Exception as e:
        logger.error(f"Error generating description: {e}")
        # Fallback to simple concatenation
        if ocr_text:
            return f"{image_caption}. The image contains text that reads: {ocr_text}"
        return image_caption

# ===== MUSIC GENERATION MODULE =====

def setup_musicgen():
    """Set up the MusicGen model with optimizations for low VRAM"""
    try:
        # Import the library
        from audiocraft.models import MusicGen
        import torch
        
        # Use the smallest available model to conserve VRAM
        model = MusicGen.get_pretrained("facebook/musicgen-small", device=DEVICE)
        
        # Optimize model for inference
        model.set_generation_params(
            duration=5,  # Generate shorter clips (5 seconds)
            temperature=1.0,
            top_k=250,
            top_p=0.0,
        )
        
        log_gpu_memory()
        return model
    except ImportError:
        logger.warning("AudioCraft not installed. Installing...")
        import subprocess
        try:
            # Install AudioCraft
            subprocess.check_call(["pip", "install", "audiocraft"])
            # Try again
            from audiocraft.models import MusicGen
            model = MusicGen.get_pretrained("facebook/musicgen-small", device=DEVICE)
            model.set_generation_params(duration=5, temperature=1.0)
            return model
        except Exception as e:
            logger.error(f"Could not install or use AudioCraft: {e}")
            return None
    except Exception as e:
        logger.error(f"Error setting up MusicGen: {e}")
        return None

def generate_music(description: str, output_dir: str) -> Optional[str]:
    """Generate music based on text description"""
    try:
        # Setup music generation model
        model = setup_musicgen()
        if model is None:
            return None
            
        # Create prompt for music generation
        prompt = f"Create music that captures the essence of: {description}"
        logger.info(f"Music generation prompt: {prompt}")
        
        # Generate music
        wav = model.generate([prompt], progress=True)
        
        # Save the generated audio
        output_path = os.path.join(output_dir, f"generated_{int(time.time())}.wav")
        
        # Convert to numpy and save
        audio_data = wav[0].cpu().numpy()
        
        # Import here to reduce initial memory footprint
        import soundfile as sf
        sf.write(output_path, audio_data, samplerate=32000)
        
        # Clear CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info(f"Music saved to {output_path}")
        return output_path
    except ImportError:
        logger.warning("SoundFile not installed. Installing...")
        import subprocess
        try:
            subprocess.check_call(["pip", "install", "soundfile"])
            # Try again
            import soundfile as sf
            # (continue the function)
            return None  # For simplicity in this error handler
        except Exception as e:
            logger.error(f"Could not install or use SoundFile: {e}")
            return None
    except Exception as e:
        logger.error(f"Music generation error: {e}")
        return None

# ===== MAIN PROCESSING PIPELINE =====

def process_image(image_path: str, output_dir: str = "outputs") -> Dict[str, str]:
    """
    Process an image to generate audio:
    1. Extract keywords/caption from image
    2. Perform OCR if text is present
    3. Generate a coherent description
    4. Create music based on the description
    """
    os.makedirs(output_dir, exist_ok=True)
    
    results = {
        "image_path": image_path,
        "caption": "",
        "ocr_text": "",
        "description": "",
        "audio_path": None,
        "error": None
    }
    
    try:
        # Step 1: Extract image information using BLIP
        logger.info(f"Analyzing image: {image_path}")
        image_caption = extract_image_keywords(image_path)
        results["caption"] = image_caption
        
        # Step 2: Perform OCR
        logger.info("Performing OCR on image")
        ocr_text = perform_ocr(image_path)
        results["ocr_text"] = ocr_text
        
        # Step 3: Generate a coherent description
        logger.info("Generating description")
        description = generate_description(image_caption, ocr_text)
        results["description"] = description
        
        # Step 4: Generate music
        logger.info("Generating music based on description")
        audio_path = generate_music(description, output_dir)
        results["audio_path"] = audio_path
        
        logger.info("Processing complete")
        return results
    
    except Exception as e:
        logger.error(f"Error in processing pipeline: {e}")
        results["error"] = str(e)
        return results

# If run directly
if __name__ == "__main__":
    # Test with a sample image if provided as argument
    import sys
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Processing image: {image_path}")
        result = process_image(image_path)
        print(f"Results: {result}")
    else:
        print("Please provide an image path as argument")