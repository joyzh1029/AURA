from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
from typing import List
import uuid
import pathlib

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

# Get the absolute path to the frontend public directory
BASE_DIR = pathlib.Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "public"

# Mount the static files directory
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    return {"message": "Image Upload API is running"}

@app.post("/upload/")
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
        "file_path": file_path
    }

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
                "file_path": file_path
            })
        except Exception:
            pass
        finally:
            file.file.close()
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
