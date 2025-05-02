# 환경변수 설정 - OpenMP 충돌 해결
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
<<<<<<< HEAD
=======
import os
>>>>>>> origin/jaehoon
import shutil
from typing import List, Dict, Any, Optional
import uuid
import pathlib
from tempfile import NamedTemporaryFile, TemporaryDirectory
import tempfile
import moviepy.editor as mp
<<<<<<< HEAD
from tempfile import NamedTemporaryFile, TemporaryDirectory
import tempfile
from pydantic import BaseModel
from runner import run_pipeline

# Import chatbot functionality
from chatbot import get_chatbot, process_message
=======
from runner import run_pipeline
from dotenv import load_dotenv

load_dotenv()
>>>>>>> origin/jaehoon

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://192.168.0.142:8080", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

BASE_DIR = pathlib.Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "public"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    return {"message": "AURA API is running"}

<<<<<<< HEAD
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
=======
@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

>>>>>>> origin/jaehoon
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
<<<<<<< HEAD
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

# Utility function to get the full URL for a file
def get_file_url(filename: str) -> str:
    base_url = "http://localhost:8001"
    return f"{base_url}/uploads/{filename}"
=======
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    finally:
        file.file.close()

    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "content_type": file.content_type,
        "file_path": file_path
    }
>>>>>>> origin/jaehoon

@app.post("/upload-multiple/")
async def upload_multiple_images(files: List[UploadFile] = File(...)):
    result = []

    for file in files:
        if not file.content_type.startswith("image/"):
            continue

        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

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

<<<<<<< HEAD





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
=======
@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")

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
            result_path = run_pipeline(temp_video_path, tmp_output_dir)

            final_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            with open(result_path, "rb") as src, open(final_temp.name, "wb") as dst:
                shutil.copyfileobj(src, dst)

        return StreamingResponse(
            open(final_temp.name, "rb"),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename=generated_{uuid.uuid4()}.mp4"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    finally:
        file.file.close()
        if os.path.exists(temp_video_path):
            os.unlink(temp_video_path)

@app.post("/upload-audio/")
>>>>>>> origin/jaehoon
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
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)