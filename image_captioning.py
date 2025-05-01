from setup import blip_processor, blip_model, device
from PIL import Image

# 3. 이미지 → 문장 설명 생성 (개선된 버전)
def generate_caption(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = blip_processor(images=image, return_tensors="pt").to(device)
    
    # 더 세부적인 설명을 위해 다양한 생성 옵션 시도
    output = blip_model.generate(
        **inputs, 
        max_length=50,  # 더 긴 설명 허용
        num_beams=5,    # 더 나은 샘플링을 위한 빔 서치
        top_p=0.95,     # 다양성을 위한 top-p 샘플링
    )
    
    caption = blip_processor.decode(output[0], skip_special_tokens=True)
    return caption
