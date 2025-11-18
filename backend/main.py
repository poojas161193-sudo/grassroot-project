from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
from decouple import config
from datetime import datetime

from models import Video, ChatHistory, get_db, create_tables, SessionLocal
from video_processor import VideoProcessor
from language_config import get_enabled_languages

app = FastAPI(title="Video Analyzer API", description="AI-powered video analysis and Q&A system with multi-language support")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = config('UPLOAD_DIR', default='./uploads')
processor = VideoProcessor()

create_tables()


class QuestionRequest(BaseModel):
    video_id: int
    question: str


class VideoResponse(BaseModel):
    id: int
    filename: str
    transcription: str
    summary: str


class ChatResponse(BaseModel):
    question: str
    answer: str


async def process_video_background(
    video_id: int,
    file_path: str,
    language: str = None,
    ui_language: str = 'en'
):
    """Background task to process video with multi-language support"""
    db = SessionLocal()
    try:
        # Update status to processing
        video = db.query(Video).filter(Video.id == video_id).first()
        video.processing_status = "processing"
        db.commit()

        # Process video with language parameters
        result = processor.process_video(file_path, language, ui_language)

        # Update video with results including language info
        video.transcription = result["transcription"]
        video.summary = result["summary"]
        video.detected_language = result["detected_language"]
        video.transcription_method = result["transcription_method"]
        video.processing_status = "completed"
        video.processed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        # Update status to failed
        video = db.query(Video).filter(Video.id == video_id).first()
        video.processing_status = "failed"
        video.error_message = str(e)
        db.commit()
    finally:
        db.close()


@app.get("/supported-languages/")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": get_enabled_languages(),
        "default": "en"
    }


@app.post("/upload-video/")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Query(None, description="Video language (ISO 639-1 code: 'en', 'ja', or 'auto' for auto-detect)"),
    ui_language: str = Query('en', description="UI language for responses (ISO 639-1 code: 'en' or 'ja')"),
    db: Session = Depends(get_db)
):
    """Upload video file with language specification and process in background"""
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")

    try:
        # Save uploaded file in chunks for better performance
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        # Use chunked writing for large files
        CHUNK_SIZE = 1024 * 1024  # 1MB chunks
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(CHUNK_SIZE):
                buffer.write(chunk)

        # Create database entry immediately with language info
        db_video = Video(
            filename=file.filename,
            file_path=file_path,
            processing_status="pending",
            user_selected_language=language if language and language != 'auto' else None,
            ui_language=ui_language
        )
        db.add(db_video)
        db.commit()
        db.refresh(db_video)

        # Add background processing task with language parameters
        background_tasks.add_task(
            process_video_background,
            db_video.id,
            file_path,
            language,
            ui_language
        )

        return {
            "message": "Video uploaded successfully. Processing started in background.",
            "video_id": db_video.id,
            "filename": db_video.filename,
            "processing_status": "pending",
            "language": language,
            "ui_language": ui_language
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {str(e)}")


@app.post("/ask-question/")
async def ask_question(
    request: QuestionRequest,
    ui_language: str = Query(None, description="Response language (ISO 639-1 code: 'en' or 'ja')"),
    db: Session = Depends(get_db)
):
    """Ask question about a specific video with language specification"""
    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        # Use specified language or video's UI language
        response_language = ui_language or video.ui_language or 'en'

        # Get answer from processor in specified language
        answer = processor.answer_question(
            video.transcription,
            request.question,
            response_language
        )

        # Save chat history with language
        chat_entry = ChatHistory(
            video_id=request.video_id,
            question=request.question,
            answer=answer,
            language=response_language
        )
        db.add(chat_entry)
        db.commit()

        return {
            "question": request.question,
            "answer": answer,
            "video_id": request.video_id,
            "language": response_language
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")


@app.get("/videos/")
async def get_videos(db: Session = Depends(get_db)):
    """Get list of all uploaded videos"""
    videos = db.query(Video).all()
    return [
        {
            "id": video.id,
            "filename": video.filename,
            "summary": video.summary,
            "uploaded_at": video.uploaded_at,
            "detected_language": video.detected_language,
            "ui_language": video.ui_language,
            "processing_status": video.processing_status
        }
        for video in videos
    ]


@app.get("/video/{video_id}")
async def get_video(video_id: int, db: Session = Depends(get_db)):
    """Get specific video details with language information"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return {
        "id": video.id,
        "filename": video.filename,
        "transcription": video.transcription,
        "summary": video.summary,
        "processing_status": video.processing_status,
        "error_message": video.error_message,
        "uploaded_at": video.uploaded_at,
        "processed_at": video.processed_at,
        "detected_language": video.detected_language,
        "user_selected_language": video.user_selected_language,
        "ui_language": video.ui_language,
        "transcription_method": video.transcription_method
    }


@app.get("/video-status/{video_id}")
async def get_video_status(video_id: int, db: Session = Depends(get_db)):
    """Check processing status of a video with language information"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    return {
        "video_id": video.id,
        "filename": video.filename,
        "processing_status": video.processing_status,
        "error_message": video.error_message,
        "detected_language": video.detected_language,
        "ui_language": video.ui_language,
        "transcription_method": video.transcription_method,
        "transcription": video.transcription if video.processing_status == "completed" else None,
        "summary": video.summary if video.processing_status == "completed" else None
    }


@app.get("/chat-history/{video_id}")
async def get_chat_history(video_id: int, db: Session = Depends(get_db)):
    """Get chat history for a specific video with language information"""
    history = db.query(ChatHistory).filter(ChatHistory.video_id == video_id).all()
    return [
        {
            "question": chat.question,
            "answer": chat.answer,
            "timestamp": chat.timestamp,
            "language": chat.language
        }
        for chat in history
    ]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Video Analyzer API is running",
        "multi_language_support": True,
        "supported_languages": ["en", "ja"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
