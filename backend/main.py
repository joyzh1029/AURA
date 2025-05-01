# 환경변수 설정 - OpenMP 충돌 해결
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
import shutil
from typing import List, Dict, Any, Optional
import uuid
import pathlib
import moviepy.editor as mp
from tempfile import NamedTemporaryFile, TemporaryDirectory
import tempfile
from pydantic import BaseModel
from runner import run_pipeline

# Import img2audio module
from img2audio import process_image

# Import chatbot functionality
from chatbot import get_chatbot, process_message

app = FastAPI()

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://192.168.0.142:8080", "*"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create directory for audio outputs *hwaseop*
AUDIO_DIR = "audio_outputs"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Get the absolute path to the frontend public directory
BASE_DIR = pathlib.Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "public"

# Mount the static files directory
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

# Utility function to get the full URL for a file *hwaseop*
def get_file_url(filename: str, directory: str = UPLOAD_DIR) -> str:
    base_url = "http://localhost:8001"
    relative_path = directory.replace("\\", "/").split("/")[-1]
    return f"{base_url}/{relative_path}/{filename}"

@app.post("/upload-multiple/")
async def upload_multiple_images(files: List[UploadFile] = File(...)):
    """
    Upload multiple image files
    """
    result = []
    
    for file in files:
        # Validate file is an image
        if not file.content_type.startswith("image/"):
            continue
        
        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save the file
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

@app.post("/image-to-audio/", response_model=Dict[str, Any])
async def convert_image_to_audio(file: UploadFile = File(...)):
    """
    Process an image to generate audio using img2audio
    """
    # Validate file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save the uploaded image
    file_extension = os.path.splitext(file.filename)[1]
    image_filename = f"{uuid.uuid4()}{file_extension}"
    image_path = os.path.join(UPLOAD_DIR, image_filename)
    
    try:
        # Save uploaded file
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the image using img2audio
        result = process_image(image_path, AUDIO_DIR)
        
        if result["error"]:
            raise HTTPException(status_code=500, detail=f"Error processing image: {result['error']}")
        
        if not result["audio_path"]:
            raise HTTPException(status_code=500, detail="Failed to generate audio")
        
        # Get the audio filename
        audio_filename = os.path.basename(result["audio_path"])
        
        # Construct response
        response = {
            "image": {
                "filename": image_filename,
                "url": get_file_url(image_filename)
            },
            "audio": {
                "filename": audio_filename,
                "url": get_file_url(audio_filename, AUDIO_DIR)
            },
            "caption": result["caption"],
            "ocr_text": result["ocr_text"],
            "description": result["description"]
        }
        
        return response
    except Exception as e:
        # Clean up the image if an error occurs
        if os.path.exists(image_path):
            os.unlink(image_path)
        raise HTTPException(status_code=500, detail=f"Error in image-to-audio process: {str(e)}")
    finally:
        file.file.close()

@app.post("/upload-audio/", response_model=Dict[str, Any])
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload an audio file
    """
    # Validate file is an audio
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio")
    
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

# Make audio outputs directory accessible via HTTP *hwaseop*
app.mount("/audio_outputs", StaticFiles(directory=AUDIO_DIR), name="audio_outputs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)