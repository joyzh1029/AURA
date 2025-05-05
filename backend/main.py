# 환경 변수 설정 - OpenMP 충돌 해결
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
from moviepy.editor import VideoFileClip, AudioFileClip
from tempfile import NamedTemporaryFile, TemporaryDirectory
import tempfile
from pydantic import BaseModel
from runner import run_pipeline

# 챗봇 기능 가져오기
from chatbot import get_chatbot, process_message

# 이미지 기반 음악 생성 모듈 가져오기
from logic.image_music_generator import ImageMusicGenerator
from logic.time_estimator import ProcessingTimeEstimator
from PIL import Image

app = FastAPI()

# 시간 추정기 초기화
time_estimator = ProcessingTimeEstimator()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# 업로드 및 결과 디렉토리 설정
BACKEND_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BACKEND_DIR / "uploads"
OUTPUT_DIR = BACKEND_DIR / "results"

# 디렉토리 존재 확인
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_DIR = pathlib.Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "public"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    return {"message": "AURA API is running"}

# 채팅 메시지 모델
class ChatMessage(BaseModel):
    message: str
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None

# 챗봇 및 RAG QA 체인 초기화
chatbot, qa_chain = get_chatbot()

@app.post("/chat/")
async def chat(message: ChatMessage):
    """
    Process a chat message using LangChain with Google Gemini
    """
    try:
        # LangChain과 RAG로 메시지 처리
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

# 파일의 전체 URL을 가져오는 유틸리티 함수
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






# 전체 URL을 반환하도록 업로드 엔드포인트 업데이트
@app.post("/upload/", response_model=Dict[str, Any])
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a single image file
    """
    # 파일이 이미지인지 검증
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # 고유한 파일명 생성
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # 파일 저장
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

# 전체 URL을 반환하도록 오디오 업로드 엔드포인트 업데이트
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

# 전체 URL을 반환하도록 비디오 업로드 엔드포인트 업데이트
@app.post("/estimate-video-time/")
async def estimate_video_processing_time(file: UploadFile = File(...)):
    """
    预测视频处理时间的端点
    """
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="비디오 파일만 가능합니다.")

    try:
        print(f"[INFO] 开始视频处理时间预测请求")
        # 비디오 파일 크기 가져오기
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)

        # 처리 시간 예측 - 비디오 크기 기반 추정
        # MB당 2초의 처리 시간 가정
        time_estimate = int((size / (1024 * 1024)) * 2)
        # 최소 처리 시간 10초 보장
        time_estimate = max(10, time_estimate)
        print(f"[INFO] 视频处理时间预测结果: {time_estimate}秒")
        
        return {"estimated_time": time_estimate}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file, process it through the AURA pipeline
    """
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # 파일 크기 확인
    content = await file.read()
    if len(content) > 100 * 1024 * 1024:  # 100MB 제한
        raise HTTPException(status_code=400, detail="Video file size must be 100MB or smaller")

    temp_video_path = None
    temp_result = None
    final_result = None

    try:
        # 업로드된 파일 저장
        temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        with open(temp_video_path, "wb") as buffer:
            buffer.write(content)

        print(f"[INFO] Video saved to temp path: {temp_video_path}")

        # Create temporary directory for processing
        with TemporaryDirectory() as tmp_dir:
            # Process video through AURA pipeline
            temp_result, final_result = run_pipeline(temp_video_path, tmp_dir)
            print(f"[INFO] Video processing complete. Result at: {final_result}")

            # Return the final processed video with audio
            if os.path.exists(final_result):
                return StreamingResponse(
                    open(final_result, "rb"),
                    media_type="video/mp4",
                    headers={
                        "Content-Type": "video/mp4",
                        "Accept-Ranges": "bytes",
                        "Cache-Control": "no-cache",
                        "Access-Control-Allow-Origin": "*"
                    }
                )
            else:
                raise FileNotFoundError(f"Processed video file not found: {final_result}")

    except Exception as e:
        print(f"[ERROR] Video processing failed: {str(e)}")
        print(traceback.format_exc())
        
        # Cleanup on error
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.unlink(temp_video_path)
            except:
                pass
                
        if temp_result and os.path.exists(temp_result):
            try:
                os.unlink(temp_result)
            except:
                pass
                
        if final_result and os.path.exists(final_result):
            try:
                os.unlink(final_result)
            except:
                pass
                
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")

            
# Make uploads directory accessible via HTTP
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# 이미지 업로드 → 음악 생성 → wav 다운로드 API (개선됨)
@app.post("/estimate-processing-time/")
async def estimate_processing_time(file: UploadFile = File(...)):
    """
    预测处理时间的端点
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 가능합니다.")

    try:
        print(f"[INFO] 开始处理时间预测请求")
        # 创建临时文件来获取图片尺寸
        with NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            print(f"[INFO] 临时文件已创建: {temp_file_path}")

        try:
            with Image.open(temp_file_path) as img:
                image_size = img.size
                print(f"[INFO] 图片尺寸: {image_size}")
        finally:
            os.unlink(temp_file_path)

        # 预测处理时间
        time_estimate = time_estimator.estimate_processing_time(image_size)
        print(f"[INFO] 时间预测结果: {time_estimate}")
        return time_estimate

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.seek(0)  # 重置文件指针，以便后续处理

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