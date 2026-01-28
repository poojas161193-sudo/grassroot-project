from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from decouple import config

DATABASE_URL = config('DATABASE_URL', default='sqlite:///./video_analyzer.db')

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    transcription = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # Multi-language support fields
    detected_language = Column(String(10), nullable=True)       # Auto-detected language (ISO 639-1 code: 'en', 'ja', etc.)
    user_selected_language = Column(String(10), nullable=True)  # User override language
    ui_language = Column(String(10), default='en')              # Language for summaries/UI responses
    transcription_method = Column(String(50), nullable=True)    # Transcription method used (gpt-4o-transcribe)

    # Audio summary fields (TTS-1-HD)
    audio_summary_path = Column(String, nullable=True)          # Path to generated TTS audio file
    audio_summary_duration = Column(Float, nullable=True)       # Duration of audio summary in seconds


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, index=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Multi-language support field
    language = Column(String(10), default='en')  # Language of the Q&A interaction (ISO 639-1 code: 'en', 'ja', etc.)


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
