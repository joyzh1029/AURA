from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import os
import shutil
from typing import List
import uuid
import pathlib
from tempfile import NamedTemporaryFile, TemporaryDirectory
import tempfile
import moviepy.editor as mp
from runner import run_pipeline

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
    return {"message": "Image Upload API is running"}

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

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
        "file_path": file_path
    }

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
                "file_path": file_path
            })
        except Exception:
            pass
        finally:
            file.file.close()

    return result

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
        "file_path": file_path
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
