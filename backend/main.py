# 환경변수 설정 - OpenMP 충돌 해결
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import traceback
from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import shutil
from typing import List, Dict, Any, Optional
import uuid
import pathlib
from tempfile import NamedTemporaryFile, TemporaryDirectory
import tempfile
import moviepy.editor as mp
from tempfile import NamedTemporaryFile, TemporaryDirectory
import tempfile
from pydantic import BaseModel
from runner import run_pipeline

# Import chatbot functionality
from chatbot import get_chatbot, process_message

# 이미지 기반 음악 생성 모듈 import
from logic.image_music_generator import ImageMusicGenerator

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://192.168.0.142:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置上传和结果目录
BACKEND_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BACKEND_DIR / "uploads"
OUTPUT_DIR = BACKEND_DIR / "results"

# 确保目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_DIR = pathlib.Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "public"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    return {"message": "AURA API is running"}

# Chat message model
class ChatMessage(BaseModel):
    message: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None

# Initialize chatbot and RAG QA chain
chatbot, qa_chain = get_chatbot()

@app.post("/chat/")
async def chat(message: ChatMessage):
    """
    Process a chat message using LangChain with Google Gemini
    """
    try:
        # Process the message with LangChain and RAG
        response = process_message(
            conversation=chatbot,
            qa_chain=qa_chain,
            message=message.message,
            image_url=message.image_url,
            video_url=message.video_url,
            audio_url=message.audio_url
        )
        
        return {
            "response": response,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

# Utility function to get the full URL for a file
def get_file_url(filename: str) -> str:
    base_url = "http://localhost:8001"
    return f"{base_url}/uploads/{filename}"

@app.post("/upload-multiple/")
async def upload_multiple_images(files: List[UploadFile] = File(...)):
    result = []

    for file in files:
        if not file.content_type.startswith("image/"):
            continue

        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = str(UPLOAD_DIR / unique_filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            result.append({
                "filename": unique_filename,
                "original_filename": file.filename,
                "content_type": file.content_type,
                "file_path": file_path,
                "url": get_file_url(unique_filename)
            })
        except Exception:
            pass
        finally:
            file.file.close()

    return result






# Update the upload endpoints to return full URLs
@app.post("/upload/", response_model=Dict[str, Any])
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a single image file
    """
    # Validate file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    finally:
        file.file.close()
    
    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "content_type": file.content_type,
        "file_path": file_path,
        "url": get_file_url(unique_filename)
    }

# Update the upload-audio endpoint to return full URLs
@app.post("/upload-audio/", response_model=Dict[str, Any])
async def upload_audio(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio")

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    finally:
        file.file.close()

    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "content_type": file.content_type,
        "file_path": file_path,
        "url": get_file_url(unique_filename)
    }

# Update the upload-video endpoint to return full URLs
@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file, process it through the AURA pipeline and return the transformed video
    """
    # Validate file is a video
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Validate file size (max 100MB)
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Video file size must be 100MB or smaller")

    with NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_in:
        shutil.copyfileobj(file.file, temp_in)
        temp_in.flush()
        temp_video_path = temp_in.name

    try:
        with TemporaryDirectory() as tmp_output_dir:
            # run_pipeline 함수가 반환
            temp_result_path, final_result_path = run_pipeline(temp_video_path, tmp_output_dir)
            
            # 사용자에게 영상 결과를 직접 반환
            final_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            with open(temp_result_path, "rb") as src, open(final_temp.name, "wb") as dst:
                shutil.copyfileobj(src, dst)

        return StreamingResponse(
            open(final_temp.name, "rb"),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename=generated_{uuid.uuid4()}.mp4"
            }
        )
    except Exception as e:
        if os.path.exists(temp_video_path):
            os.unlink(temp_video_path)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        file.file.close()
        if os.path.exists(temp_video_path):
            os.unlink(temp_video_path)

            
# Make uploads directory accessible via HTTP
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 이미지 업로드 → 음악 생성 → wav 다운로드 API (개선됨)
@app.post("/upload-image-music/")
async def upload_image_music(file: UploadFile = File(...)):
    """
    이미지 파일을 업로드 받아 음악으로 변환하여 반환합니다.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 가능합니다.")

    # 파일 확장자 추출
    file_ext = os.path.splitext(file.filename)[1]
    
    # 작업용 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    
    try:
        print(f"[INFO] Processing upload-image-music request")
        print(f"[INFO] Temporary directory: {temp_dir}")
        
        # 1. 이미지 파일 저장
        image_path = os.path.join(temp_dir, f"uploaded{file_ext}")
        with open(image_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        print(f"[INFO] Image saved to: {image_path}")

        # 2. 이미지 → 음악 생성
        print(f"[INFO] Initializing ImageMusicGenerator")
        music_generator = ImageMusicGenerator()
        
        print(f"[INFO] Generating music from image")
        music_path = music_generator.generate_music_from_image(image_path, temp_dir)
        
        print(f"[INFO] Music generated successfully: {music_path}")
        
        # 3. 음악 파일 존재 확인
        if not os.path.exists(music_path):
            raise FileNotFoundError(f"Generated music file not found: {music_path}")
            
        filesize = os.path.getsize(music_path)
        print(f"[INFO] Generated music file size: {filesize} bytes")
        
        if filesize == 0:
            raise ValueError("Generated music file is empty")

        # 4. 영구 저장용 파일 생성
        output_filename = f"generated_music_{uuid.uuid4()}.wav"
        permanent_path = str(OUTPUT_DIR / output_filename)
        
        # 임시 파일을 영구 저장 위치로 복사
        shutil.copy2(music_path, permanent_path)
        print(f"[INFO] Music file copied to permanent location: {permanent_path}")

        # 5. StreamingResponse로 반환 (VideoAPI와 동일한 방식)
        return StreamingResponse(
            open(permanent_path, "rb"),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
        
    except Exception as e:
        print(f"[ERROR] Upload-image-music failed: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"이미지 음악 생성 실패: {str(e)}")
    finally:
        file.file.close()
        
        # 임시 디렉토리는 남겨두어 디버깅에 사용
        print(f"[INFO] Temporary files remain in {temp_dir} for debugging")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)