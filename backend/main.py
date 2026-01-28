from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
from decouple import config
from datetime import datetime

from models import Video, ChatHistory, get_db, create_tables, SessionLocal
from video_processor import VideoProcessor
from language_config import get_enabled_languages

# Q2: Course Generation imports
from course_structurer import CourseStructurer
from slide_generator import SlideGenerator
from quiz_generator import QuizGenerator
from course_assembler import CourseAssembler
from course_models import Course, create_course_tables

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

# Q2: Initialize course generation components
course_structurer = CourseStructurer()
slide_generator = SlideGenerator()
quiz_generator = QuizGenerator()
course_assembler = CourseAssembler()

create_tables()
create_course_tables()  # Create course-related tables


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


# Q2: Course Generation Models
class CourseAnalyzeRequest(BaseModel):
    video_id: int
    language: str = "en"
    theme: str = "light"  # light, dark, corporate
    num_questions: int = 10


class CourseGenerateRequest(BaseModel):
    video_id: int
    language: str = "en"
    theme: str = "light"
    num_questions: int = 10


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

        # Process video with language parameters and video_id for audio summary
        result = processor.process_video(file_path, language, ui_language, video_id)

        # Update video with results including language info and audio summary
        video.transcription = result["transcription"]
        video.summary = result["summary"]
        video.detected_language = result["detected_language"]
        video.transcription_method = result["transcription_method"]
        video.audio_summary_path = result.get("audio_summary_path")
        video.audio_summary_duration = result.get("audio_summary_duration")
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
        "transcription_method": video.transcription_method,
        "audio_summary_path": video.audio_summary_path,
        "audio_summary_duration": video.audio_summary_duration
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
        "summary": video.summary if video.processing_status == "completed" else None,
        "audio_summary_path": video.audio_summary_path if video.processing_status == "completed" else None,
        "audio_summary_duration": video.audio_summary_duration if video.processing_status == "completed" else None
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


@app.get("/audio-summary/{video_id}")
async def get_audio_summary(video_id: int, db: Session = Depends(get_db)):
    """Get audio summary file for a specific video"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if not video.audio_summary_path or not os.path.exists(video.audio_summary_path):
        raise HTTPException(status_code=404, detail="Audio summary not found")

    return FileResponse(
        video.audio_summary_path,
        media_type="audio/mpeg",
        filename=f"summary_{video_id}.mp3"
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Video Analyzer API is running",
        "multi_language_support": True,
        "supported_languages": ["en", "ja"],
        "features": ["video_analysis", "course_generation"]
    }


# ============================================================
# Q2: COURSE GENERATION ENDPOINTS
# ============================================================

@app.post("/api/course/analyze")
async def analyze_and_create_course_structure(
    request: CourseAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze video transcript and create course structure
    Step 1 of course generation
    """
    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        if video.processing_status != "completed":
            raise HTTPException(status_code=400, detail="Video processing not completed yet")

        if not video.transcription:
            raise HTTPException(status_code=400, detail="Video transcription not available")

        # Create course structure from transcript
        course_structure = course_structurer.analyze_content(
            content=video.transcription,
            source_type="transcript",
            language=request.language,
            duration_minutes=video.audio_summary_duration
        )

        return {
            "message": "Course structure created successfully",
            "video_id": request.video_id,
            "course_structure": course_structure
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze content: {str(e)}")


@app.post("/api/course/generate")
async def generate_complete_course(
    request: CourseGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate complete course (structure + slides + quiz) from video
    All-in-one endpoint
    """
    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        if video.processing_status != "completed":
            raise HTTPException(status_code=400, detail="Video processing not completed yet")

        if not video.transcription:
            raise HTTPException(status_code=400, detail="Video transcription not available")

        # Step 1: Create course structure
        course_structure = course_structurer.analyze_content(
            content=video.transcription,
            source_type="transcript",
            language=request.language,
            duration_minutes=video.audio_summary_duration
        )

        # Step 2: Generate slides
        slide_generator.apply_theme(request.theme)
        slides_html = slide_generator.create_slide_deck(
            course_data=course_structure,
            language=request.language
        )

        # Step 3: Generate quiz
        quiz_data = quiz_generator.generate_quiz(
            course_data=course_structure,
            num_questions=request.num_questions,
            language=request.language
        )

        # Step 4: Assemble complete course
        course_id = f"course_{request.video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        course_package = course_assembler.assemble_course(
            course_structure=course_structure,
            slides_html=slides_html,
            quiz_data=quiz_data,
            course_id=course_id,
            metadata={
                "video_id": request.video_id,
                "video_filename": video.filename,
                "language": request.language,
                "theme": request.theme,
                "num_questions": request.num_questions
            }
        )

        # Create ZIP in background
        background_tasks.add_task(course_assembler.export_to_zip, course_id)

        # Save course to database
        import json
        db_course = Course(
            video_id=request.video_id,
            course_id=course_id,
            title=course_structure.get("course", {}).get("title", ""),
            description=course_structure.get("course", {}).get("description", ""),
            course_dir=course_package["course_dir"],
            slides_path=course_package["files"]["slides"],
            quiz_path=course_package["files"]["quiz_html"],
            viewer_path=course_package["files"]["viewer"],
            language=request.language,
            theme=request.theme,
            total_slides=course_structure.get("course", {}).get("total_slides", 0),
            total_questions=len(quiz_data.get("quiz", {}).get("questions", [])),
            course_structure=json.dumps(course_structure, ensure_ascii=False)
        )
        db.add(db_course)
        db.commit()
        db.refresh(db_course)

        return {
            "message": "Course generated successfully",
            "video_id": request.video_id,
            "course_id": course_id,
            "course_package": course_package,
            "course_title": course_structure.get("course", {}).get("title", ""),
            "total_slides": course_structure.get("course", {}).get("total_slides", 0),
            "total_questions": len(quiz_data.get("quiz", {}).get("questions", []))
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate course: {str(e)}")


@app.post("/api/course/generate-slides")
async def generate_slides_only(
    video_id: int,
    theme: str = Query("light", description="Slide theme: light, dark, or corporate"),
    language: str = Query("en", description="Language code"),
    db: Session = Depends(get_db)
):
    """Generate slides from existing course structure"""
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        if not video.transcription:
            raise HTTPException(status_code=400, detail="Video transcription not available")

        # Create course structure first
        course_structure = course_structurer.analyze_content(
            content=video.transcription,
            source_type="transcript",
            language=language
        )

        # Generate slides
        slide_generator.apply_theme(theme)
        slides_html = slide_generator.create_slide_deck(
            course_data=course_structure,
            language=language
        )

        return {
            "message": "Slides generated successfully",
            "slides_html": slides_html,
            "theme": theme,
            "total_slides": course_structure.get("course", {}).get("total_slides", 0)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate slides: {str(e)}")


@app.post("/api/course/generate-quiz")
async def generate_quiz_only(
    video_id: int,
    num_questions: int = Query(10, description="Number of questions"),
    language: str = Query("en", description="Language code"),
    db: Session = Depends(get_db)
):
    """Generate quiz from existing course structure"""
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        if not video.transcription:
            raise HTTPException(status_code=400, detail="Video transcription not available")

        # Create course structure first
        course_structure = course_structurer.analyze_content(
            content=video.transcription,
            source_type="transcript",
            language=language
        )

        # Generate quiz
        quiz_data = quiz_generator.generate_quiz(
            course_data=course_structure,
            num_questions=num_questions,
            language=language
        )

        return {
            "message": "Quiz generated successfully",
            "quiz_data": quiz_data,
            "total_questions": len(quiz_data.get("quiz", {}).get("questions", []))
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")


@app.get("/api/course/{course_id}/export")
async def export_course(course_id: str):
    """Export course as ZIP file"""
    try:
        zip_path = course_assembler.export_to_zip(course_id)

        if not zip_path or not os.path.exists(zip_path):
            raise HTTPException(status_code=404, detail="Course package not found")

        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"{course_id}.zip"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export course: {str(e)}")


@app.get("/api/course/{course_id}/files")
async def get_course_files(course_id: str):
    """Get URLs to course files (slides, quiz, viewer)"""
    try:
        course_dir = os.path.join("generated_courses", course_id)

        if not os.path.exists(course_dir):
            raise HTTPException(status_code=404, detail="Course not found")

        # Read metadata
        metadata_path = os.path.join(course_dir, "metadata.json")
        if os.path.exists(metadata_path):
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}

        return {
            "course_id": course_id,
            "files": {
                "viewer": f"/course-files/{course_id}/index.html",
                "slides": f"/course-files/{course_id}/slides.html",
                "quiz": f"/course-files/{course_id}/quiz.html"
            },
            "metadata": metadata
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get course files: {str(e)}")


@app.get("/course-files/{course_id}/{filename}")
async def serve_course_file(course_id: str, filename: str):
    """Serve individual course files"""
    try:
        file_path = os.path.join("generated_courses", course_id, filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # Determine media type
        media_type = "text/html"
        if filename.endswith(".json"):
            media_type = "application/json"

        return FileResponse(file_path, media_type=media_type)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve file: {str(e)}")


# ============================================================
# COURSE MANAGEMENT ENDPOINTS
# ============================================================

@app.get("/api/courses")
async def list_all_courses(
    db: Session = Depends(get_db),
    skip: int = Query(0, description="Number of courses to skip"),
    limit: int = Query(100, description="Maximum number of courses to return")
):
    """
    List all generated courses with metadata and storage info
    """
    try:
        # Get all courses from database
        courses = db.query(Course).order_by(Course.created_at.desc()).offset(skip).limit(limit).all()
        total_courses = db.query(Course).count()

        # Calculate storage for each course
        courses_data = []
        total_storage = 0

        for course in courses:
            course_dir = course.course_dir
            course_size = 0

            # Calculate directory size
            if course_dir and os.path.exists(course_dir):
                for dirpath, dirnames, filenames in os.walk(course_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        course_size += os.path.getsize(filepath)

            total_storage += course_size

            courses_data.append({
                "id": course.id,
                "course_id": course.course_id,
                "video_id": course.video_id,
                "title": course.title,
                "description": course.description,
                "language": course.language,
                "theme": course.theme,
                "total_slides": course.total_slides,
                "total_questions": course.total_questions,
                "storage_mb": round(course_size / (1024 * 1024), 2),
                "created_at": course.created_at.isoformat() if course.created_at else None
            })

        return {
            "total_courses": total_courses,
            "courses": courses_data,
            "total_storage_mb": round(total_storage / (1024 * 1024), 2),
            "showing": len(courses_data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list courses: {str(e)}")


@app.delete("/api/course/{course_id}")
async def delete_course(course_id: str, db: Session = Depends(get_db)):
    """
    Delete a specific course (removes from database and deletes all files)
    """
    try:
        # Find course in database
        course = db.query(Course).filter(Course.course_id == course_id).first()

        if not course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Delete files from filesystem
        import shutil
        if course.course_dir and os.path.exists(course.course_dir):
            shutil.rmtree(course.course_dir)

        # Delete from database
        db.delete(course)
        db.commit()

        return {
            "message": "Course deleted successfully",
            "course_id": course_id,
            "title": course.title
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete course: {str(e)}")


@app.post("/api/courses/cleanup")
async def cleanup_old_courses(
    days: int = Query(30, description="Delete courses older than X days"),
    db: Session = Depends(get_db)
):
    """
    Clean up courses older than specified days
    """
    try:
        import shutil
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Find old courses
        old_courses = db.query(Course).filter(Course.created_at < cutoff_date).all()

        deleted_count = 0
        freed_space = 0

        for course in old_courses:
            # Calculate size before deleting
            if course.course_dir and os.path.exists(course.course_dir):
                course_size = 0
                for dirpath, dirnames, filenames in os.walk(course.course_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        course_size += os.path.getsize(filepath)

                freed_space += course_size

                # Delete files
                shutil.rmtree(course.course_dir)

            # Delete from database
            db.delete(course)
            deleted_count += 1

        db.commit()

        return {
            "message": f"Cleaned up {deleted_count} courses older than {days} days",
            "deleted_courses": deleted_count,
            "freed_space_mb": round(freed_space / (1024 * 1024), 2)
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to cleanup courses: {str(e)}")


@app.get("/api/courses/storage-stats")
async def get_storage_stats(db: Session = Depends(get_db)):
    """
    Get detailed storage statistics for all courses
    """
    try:
        total_courses = db.query(Course).count()

        # Calculate total storage
        total_storage = 0
        courses_dir = "generated_courses"

        if os.path.exists(courses_dir):
            for dirpath, dirnames, filenames in os.walk(courses_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_storage += os.path.getsize(filepath)

        # Get database size
        db_size = 0
        db_path = "video_analyzer.db"
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)

        # Group by language
        import json
        courses = db.query(Course).all()

        stats_by_language = {}
        stats_by_theme = {}

        for course in courses:
            # By language
            lang = course.language or "unknown"
            if lang not in stats_by_language:
                stats_by_language[lang] = {"count": 0, "slides": 0, "questions": 0}
            stats_by_language[lang]["count"] += 1
            stats_by_language[lang]["slides"] += course.total_slides or 0
            stats_by_language[lang]["questions"] += course.total_questions or 0

            # By theme
            theme = course.theme or "unknown"
            if theme not in stats_by_theme:
                stats_by_theme[theme] = 0
            stats_by_theme[theme] += 1

        return {
            "total_courses": total_courses,
            "total_storage_mb": round(total_storage / (1024 * 1024), 2),
            "database_size_mb": round(db_size / (1024 * 1024), 2),
            "total_storage_gb": round(total_storage / (1024 * 1024 * 1024), 2),
            "stats_by_language": stats_by_language,
            "stats_by_theme": stats_by_theme,
            "average_course_size_mb": round((total_storage / total_courses) / (1024 * 1024), 2) if total_courses > 0 else 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get storage stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
