# Multi-Language Support Enhancement - Implementation Plan

## 📋 Project Overview

**Project Name:** Video Analyzer AI - Multi-Language Support
**Version:** 3.1.0
**Document Version:** 1.0
**Last Updated:** November 4, 2025
**Status:** Ready for Implementation

---

## 🎯 Executive Summary

This document outlines the complete implementation plan for adding multi-language support to the Video Analyzer AI application. The enhancement will enable users to:

- Upload videos in any of 100+ supported languages
- Automatically detect the video language
- Transcribe audio in multiple languages (Japanese, English, Spanish, French, German, Chinese, Korean, etc.)
- Generate summaries in the user's preferred language
- Interact with the chatbot in multiple languages
- Switch UI language dynamically

### Business Value
- **Market Expansion:** Opens Japanese and other non-English markets
- **User Experience:** Native language support improves usability
- **Competitive Advantage:** Few video analyzers support 100+ languages
- **Accessibility:** Makes the tool accessible globally

---

## ✅ Prerequisites Check

### Environment Validation
- ✅ Azure Speech Services: Configured and verified
- ✅ Azure Whisper (Fallback): Configured and verified
- ✅ Rakuten AI Gateway (GPT-4o): Configured and verified
- ✅ Python 3.9+: Installed
- ✅ FastAPI Backend: Running
- ✅ SQLite Database: Operational
- ✅ FFmpeg: Installed for video processing

### Credentials Confirmed
```
✅ AZURE_SPEACH_KEY: Active
✅ AZURE_REGION: eastus
✅ WHISPER_API_KEY: Active
✅ WHISPER_AZURE_ENDPOINT: Active
✅ OPENAI_API_KEY: Rakuten AI Gateway
✅ OPENAI_BASE_URL: https://api.ai.public.rakuten-it.com/openai/v1
```

---

## 🗓️ Implementation Timeline

| Phase | Duration | Effort | Priority |
|-------|----------|--------|----------|
| **Phase 1: Database Schema** | 2 hours | Low | Critical |
| **Phase 2: Backend Core** | 4 hours | Medium | Critical |
| **Phase 3: Language Detection** | 3 hours | Medium | Critical |
| **Phase 4: Frontend UI** | 4 hours | Medium | Critical |
| **Phase 5: Testing** | 4 hours | High | Critical |
| **Phase 6: Documentation** | 2 hours | Low | High |
| **Phase 7: Deployment** | 2 hours | Low | High |

**Total Estimated Time:** 21 hours (3 working days)

---

## 📊 Phase 1: Database Schema Updates

### Objective
Add language-related fields to existing database tables to store language preferences and detection results.

### Tasks

#### 1.1 Update Video Model
**File:** `backend/models.py`

**New Fields to Add:**
```python
class Video(Base):
    # Existing fields...
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    transcription = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    processing_status = Column(String, default="pending")
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # NEW FIELDS
    detected_language = Column(String(10), nullable=True)      # Auto-detected language (ISO 639-1)
    user_selected_language = Column(String(10), nullable=True)  # User override language
    ui_language = Column(String(10), default='en')             # Language for summaries/UI
    transcription_method = Column(String(50), nullable=True)   # Which method was used (azure/whisper/local)
```

#### 1.2 Update ChatHistory Model
**File:** `backend/models.py`

**New Fields to Add:**
```python
class ChatHistory(Base):
    # Existing fields...
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, index=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # NEW FIELD
    language = Column(String(10), default='en')  # Language of the Q&A interaction
```

#### 1.3 Create Migration Script
**File:** `backend/migrate_db_multilang.py`

```python
"""
Database migration script to add multi-language support fields
"""
from sqlalchemy import create_engine, text
from decouple import config

DATABASE_URL = config('DATABASE_URL', default='sqlite:///./video_analyzer.db')

def migrate_database():
    """Add new language-related columns to existing tables"""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    with engine.connect() as conn:
        # Add columns to videos table
        try:
            conn.execute(text("ALTER TABLE videos ADD COLUMN detected_language VARCHAR(10)"))
            print("✅ Added detected_language to videos table")
        except:
            print("⚠️  detected_language column already exists")

        try:
            conn.execute(text("ALTER TABLE videos ADD COLUMN user_selected_language VARCHAR(10)"))
            print("✅ Added user_selected_language to videos table")
        except:
            print("⚠️  user_selected_language column already exists")

        try:
            conn.execute(text("ALTER TABLE videos ADD COLUMN ui_language VARCHAR(10) DEFAULT 'en'"))
            print("✅ Added ui_language to videos table")
        except:
            print("⚠️  ui_language column already exists")

        try:
            conn.execute(text("ALTER TABLE videos ADD COLUMN transcription_method VARCHAR(50)"))
            print("✅ Added transcription_method to videos table")
        except:
            print("⚠️  transcription_method column already exists")

        # Add column to chat_history table
        try:
            conn.execute(text("ALTER TABLE chat_history ADD COLUMN language VARCHAR(10) DEFAULT 'en'"))
            print("✅ Added language to chat_history table")
        except:
            print("⚠️  language column already exists")

        conn.commit()

    print("\n✅ Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
```

### Success Criteria
- [ ] All new database columns added successfully
- [ ] Existing data remains intact
- [ ] Migration script runs without errors
- [ ] Database schema matches updated models

### Estimated Time: 2 hours

---

## 🔧 Phase 2: Backend Core - Language Configuration

### Objective
Create language configuration system and update core backend files.

### Tasks

#### 2.1 Create Language Configuration File
**File:** `backend/language_config.py` (New File)

```python
"""
Multi-language configuration and utilities
"""

# Supported languages with Azure and Whisper mappings
SUPPORTED_LANGUAGES = {
    'en': {
        'name': 'English',
        'native_name': 'English',
        'azure_code': 'en-US',
        'whisper_code': 'en',
        'flag': '🇺🇸',
        'enabled': True
    },
    'ja': {
        'name': 'Japanese',
        'native_name': '日本語',
        'azure_code': 'ja-JP',
        'whisper_code': 'ja',
        'flag': '🇯🇵',
        'enabled': True
    },
    'es': {
        'name': 'Spanish',
        'native_name': 'Español',
        'azure_code': 'es-ES',
        'whisper_code': 'es',
        'flag': '🇪🇸',
        'enabled': True
    },
    'fr': {
        'name': 'French',
        'native_name': 'Français',
        'azure_code': 'fr-FR',
        'whisper_code': 'fr',
        'flag': '🇫🇷',
        'enabled': True
    },
    'de': {
        'name': 'German',
        'native_name': 'Deutsch',
        'azure_code': 'de-DE',
        'whisper_code': 'de',
        'flag': '🇩🇪',
        'enabled': True
    },
    'zh': {
        'name': 'Chinese (Simplified)',
        'native_name': '简体中文',
        'azure_code': 'zh-CN',
        'whisper_code': 'zh',
        'flag': '🇨🇳',
        'enabled': True
    },
    'ko': {
        'name': 'Korean',
        'native_name': '한국어',
        'azure_code': 'ko-KR',
        'whisper_code': 'ko',
        'flag': '🇰🇷',
        'enabled': True
    },
    'pt': {
        'name': 'Portuguese',
        'native_name': 'Português',
        'azure_code': 'pt-BR',
        'whisper_code': 'pt',
        'flag': '🇧🇷',
        'enabled': True
    },
    'it': {
        'name': 'Italian',
        'native_name': 'Italiano',
        'azure_code': 'it-IT',
        'whisper_code': 'it',
        'flag': '🇮🇹',
        'enabled': True
    },
    'ru': {
        'name': 'Russian',
        'native_name': 'Русский',
        'azure_code': 'ru-RU',
        'whisper_code': 'ru',
        'flag': '🇷🇺',
        'enabled': True
    }
}

DEFAULT_LANGUAGE = 'en'
DEFAULT_UI_LANGUAGE = 'en'

def get_azure_language_code(lang_code: str) -> str:
    """Get Azure Speech Services language code from ISO 639-1 code"""
    return SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES['en'])['azure_code']

def get_whisper_language_code(lang_code: str) -> str:
    """Get Whisper language code from ISO 639-1 code"""
    return SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES['en'])['whisper_code']

def get_language_name(lang_code: str) -> str:
    """Get language native name"""
    return SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES['en'])['native_name']

def is_language_supported(lang_code: str) -> bool:
    """Check if language is supported"""
    return lang_code in SUPPORTED_LANGUAGES and SUPPORTED_LANGUAGES[lang_code]['enabled']

def get_enabled_languages() -> dict:
    """Get all enabled languages"""
    return {k: v for k, v in SUPPORTED_LANGUAGES.items() if v['enabled']}

# Language detection candidates for Azure Speech
AZURE_LANGUAGE_CANDIDATES = [
    lang['azure_code'] for lang in SUPPORTED_LANGUAGES.values() if lang['enabled']
]
```

#### 2.2 Update Environment Configuration
**File:** `.env` (Add new configuration)

```env
# Multi-language Configuration (ADD THESE)
DEFAULT_UI_LANGUAGE=en
DEFAULT_VIDEO_LANGUAGE=auto
ENABLE_AUTO_LANGUAGE_DETECTION=true
SUPPORTED_LANGUAGES=en,ja,es,fr,de,zh,ko,pt,it,ru
MAX_DETECTION_AUDIO_DURATION=30
```

### Success Criteria
- [ ] Language configuration file created and tested
- [ ] All language mappings correct
- [ ] Helper functions working properly
- [ ] Environment variables added

### Estimated Time: 2 hours

---

## 🎙️ Phase 3: Language Detection & Processing

### Objective
Implement automatic language detection and multi-language transcription in video processor.

### Tasks

#### 3.1 Update Video Processor with Language Detection
**File:** `backend/video_processor.py`

**Key Changes:**

1. **Add Language Detection Method:**
```python
def detect_language(self, audio_path: str) -> str:
    """
    Detect language from audio using Azure Speech Services
    Returns ISO 639-1 language code (e.g., 'en', 'ja')
    """
    try:
        from language_config import AZURE_LANGUAGE_CANDIDATES

        speech_key = config('AZURE_SPEACH_KEY')
        service_region = config('AZURE_REGION', default='eastus')

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

        # Configure auto-detect with all supported languages
        auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=AZURE_LANGUAGE_CANDIDATES[:4]  # Azure supports max 4 candidates at once
        )

        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)

        # Create recognizer with language detection
        source_language_recognizer = speechsdk.SourceLanguageRecognizer(
            speech_config=speech_config,
            auto_detect_source_language_config=auto_detect_source_language_config,
            audio_config=audio_config
        )

        result = source_language_recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            detected = result.properties[
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
            ]
            # Convert 'en-US' to 'en', 'ja-JP' to 'ja'
            return detected.split('-')[0] if detected else 'en'
        else:
            print(f"Language detection failed, defaulting to English")
            return 'en'

    except Exception as e:
        print(f"Language detection error: {e}, defaulting to English")
        return 'en'
```

2. **Update Transcription Methods with Language Parameter:**
```python
def transcribe_audio(self, audio_path: str, language: str = 'en') -> tuple[str, str]:
    """
    Transcribe audio to text with specific language
    Returns: (transcription_text, method_used)
    """
    try:
        text = self._transcribe_with_azure_speech(audio_path, language)
        return (text, 'azure_speech')
    except Exception as azure_error:
        print(f"Azure Speech failed: {azure_error}")
        try:
            text = self._transcribe_with_azure_whisper(audio_path, language)
            return (text, 'azure_whisper')
        except Exception as whisper_error:
            print(f"Azure Whisper failed: {whisper_error}")
            try:
                text = self._transcribe_with_local_whisper(audio_path, language)
                return (text, 'local_whisper')
            except Exception as local_error:
                raise Exception(f"All transcription methods failed: {str(local_error)}")

def _transcribe_with_azure_speech(self, audio_path: str, language: str = 'en') -> str:
    """Transcribe using Azure Speech Services with specified language"""
    from language_config import get_azure_language_code

    speech_key = config('AZURE_SPEACH_KEY')
    service_region = config('AZURE_REGION', default='eastus')

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = get_azure_language_code(language)
    speech_config.enable_dictation()
    speech_config.request_word_level_timestamps()

    # ... rest of the implementation
```

3. **Update Summary Generation for Multi-Language:**
```python
def generate_summary(self, transcription: str, language: str = 'en') -> str:
    """Generate summary in specified language"""
    from language_config import get_language_name

    lang_name = get_language_name(language)

    try:
        response = client.chat.completions.create(
            model=config('LLM_MODEL', default='gpt-4o'),
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an AI assistant that creates concise summaries of video transcriptions. "
                        f"Provide a clear, informative summary in {lang_name} language that captures "
                        f"the main points and key information. Respond ONLY in {lang_name}."
                    )
                },
                {
                    "role": "user",
                    "content": f"Please summarize this video transcription:\n\n{transcription}"
                }
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Failed to generate summary: {str(e)}")
```

4. **Update Q&A for Multi-Language:**
```python
def answer_question(self, transcription: str, question: str, language: str = 'en') -> str:
    """Answer questions in specified language"""
    from language_config import get_language_name

    lang_name = get_language_name(language)

    try:
        response = client.chat.completions.create(
            model=config('LLM_MODEL', default='gpt-4o'),
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are an AI assistant that answers questions about video content in {lang_name} language. "
                        f"Base your answers on the transcription provided. Respond ONLY in {lang_name}.\n\n"
                        f"When generating multiple Q&A pairs:\n"
                        f"- Add a blank line after each answer before starting the next question\n"
                        f"- Use clear headings in {lang_name}\n"
                        f"- Ensure proper spacing for better readability\n\n"
                        f"Be accurate and informative. If the answer cannot be found in the transcription, "
                        f"clearly state that in {lang_name}."
                    )
                },
                {
                    "role": "user",
                    "content": f"Video transcription: {transcription}\n\nQuestion: {question}"
                }
            ],
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Failed to answer question: {str(e)}")
```

5. **Update Main Process Method:**
```python
def process_video(self, video_path: str, user_language: str = None, ui_language: str = 'en') -> dict:
    """
    Process video with multi-language support

    Args:
        video_path: Path to video file
        user_language: User-specified language (optional, auto-detect if None)
        ui_language: Language for UI responses (summary, Q&A)

    Returns:
        dict with transcription, summary, detected_language, transcription_method
    """
    try:
        # Extract audio
        audio_path = self.extract_audio_from_video(video_path)

        # Detect or use specified language
        if user_language and user_language != 'auto':
            detected_language = user_language
            print(f"Using user-specified language: {detected_language}")
        else:
            detected_language = self.detect_language(audio_path)
            print(f"Auto-detected language: {detected_language}")

        # Transcribe audio in detected/specified language
        transcription, method = self.transcribe_audio(audio_path, detected_language)
        print(f"Transcription completed using: {method}")

        # Generate summary in UI language
        summary = self.generate_summary(transcription, ui_language)

        # Clean up audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {
            "transcription": transcription,
            "summary": summary,
            "detected_language": detected_language,
            "transcription_method": method
        }
    except Exception as e:
        raise Exception(f"Failed to process video: {str(e)}")
```

### Success Criteria
- [ ] Language detection working for multiple languages
- [ ] Multi-language transcription functional
- [ ] Summary generation in correct language
- [ ] Q&A responses in correct language
- [ ] Proper fallback mechanism

### Estimated Time: 4 hours

---

## 🌐 Phase 4: API Endpoints Update

### Objective
Update FastAPI endpoints to support language parameters and return language information.

### Tasks

#### 4.1 Update Main API File
**File:** `backend/main.py`

**Key Changes:**

1. **Add Language Endpoints:**
```python
from language_config import SUPPORTED_LANGUAGES, get_enabled_languages

@app.get("/supported-languages/")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": get_enabled_languages(),
        "default": "en"
    }

@app.get("/language-info/{lang_code}")
async def get_language_info(lang_code: str):
    """Get detailed info about a specific language"""
    if lang_code in SUPPORTED_LANGUAGES:
        return SUPPORTED_LANGUAGES[lang_code]
    else:
        raise HTTPException(status_code=404, detail="Language not supported")
```

2. **Update Upload Endpoint:**
```python
@app.post("/upload-video/")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Query(None, description="Video language (ISO 639-1 code or 'auto')"),
    ui_language: str = Query('en', description="UI language for responses"),
    db: Session = Depends(get_db)
):
    """Upload video file with language specification"""
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")

    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        CHUNK_SIZE = 1024 * 1024
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(CHUNK_SIZE):
                buffer.write(chunk)

        # Create database entry with language info
        db_video = Video(
            filename=file.filename,
            file_path=file_path,
            processing_status="pending",
            user_selected_language=language if language != 'auto' else None,
            ui_language=ui_language
        )
        db.add(db_video)
        db.commit()
        db.refresh(db_video)

        # Pass language info to background task
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
```

3. **Update Background Processing:**
```python
async def process_video_background(
    video_id: int,
    file_path: str,
    language: str = None,
    ui_language: str = 'en'
):
    """Background task to process video with language support"""
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        video.processing_status = "processing"
        db.commit()

        # Process with language parameters
        result = processor.process_video(file_path, language, ui_language)

        # Update with results including language info
        video.transcription = result["transcription"]
        video.summary = result["summary"]
        video.detected_language = result["detected_language"]
        video.transcription_method = result["transcription_method"]
        video.processing_status = "completed"
        video.processed_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        video = db.query(Video).filter(Video.id == video_id).first()
        video.processing_status = "failed"
        video.error_message = str(e)
        db.commit()
    finally:
        db.close()
```

4. **Update Q&A Endpoint:**
```python
@app.post("/ask-question/")
async def ask_question(
    request: QuestionRequest,
    ui_language: str = Query(None, description="Response language"),
    db: Session = Depends(get_db)
):
    """Ask question with language specification"""
    try:
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        # Use specified language or video's UI language
        response_language = ui_language or video.ui_language or 'en'

        # Get answer in specified language
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
```

5. **Update Video Status Endpoint:**
```python
@app.get("/video-status/{video_id}")
async def get_video_status(video_id: int, db: Session = Depends(get_db)):
    """Check processing status with language info"""
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
```

### Success Criteria
- [ ] All endpoints accept language parameters
- [ ] Language info returned in responses
- [ ] API documentation updated automatically
- [ ] Error handling for invalid languages

### Estimated Time: 3 hours

---

## 🎨 Phase 5: Frontend - UI Internationalization

### Objective
Create multi-language UI with language selectors and translations.

### Tasks

#### 5.1 Create Translation System
**File:** `frontend/translations.js` (New File)

```javascript
const translations = {
    en: {
        // Header
        appTitle: "Video Analyzer AI",
        appSubtitle: "Upload, Transcribe, Analyze with AI",

        // Language selector
        selectLanguage: "Select Language",
        autoDetect: "Auto-detect",
        videoLanguage: "Video Language",
        interfaceLanguage: "Interface Language",

        // Upload section
        uploadTitle: "Upload Video",
        uploadText: "Drag and drop video here or click to browse",
        uploadHint: "Supports MP4, AVI, MOV, and more",
        uploading: "Uploading video...",
        processing: "Processing video... This may take a few minutes.",

        // Video info
        filename: "Filename",
        detectedLanguage: "Detected Language",
        transcriptionMethod: "Transcription Method",
        summary: "Summary",

        // Chat section
        chatTitle: "Ask Questions",
        questionPlaceholder: "Type your question here...",
        send: "Send",
        clearChat: "Clear Chat",
        clearChatConfirm: "Are you sure you want to clear the chat history?",

        // Quick actions
        quickActions: "Quick Actions",
        create10QA: "Create 10 Q&A",
        keyPoints: "10 Key Points",
        detailedSummary: "Detailed Summary",
        askAnyQuestion: "Ask Any Question",

        // Status messages
        uploadSuccess: "Video uploaded successfully!",
        processingInBackground: "Processing in background...",
        processingComplete: "Processing complete!",
        languageDetected: "Language detected:",
        error: "Error",

        // Buttons
        cancel: "Cancel",
        ok: "OK"
    },

    ja: {
        // ヘッダー
        appTitle: "ビデオ分析AI",
        appSubtitle: "アップロード、文字起こし、AI分析",

        // 言語選択
        selectLanguage: "言語を選択",
        autoDetect: "自動検出",
        videoLanguage: "ビデオの言語",
        interfaceLanguage: "インターフェース言語",

        // アップロードセクション
        uploadTitle: "ビデオをアップロード",
        uploadText: "ビデオをここにドラッグ＆ドロップまたはクリックして選択",
        uploadHint: "MP4、AVI、MOVなどをサポート",
        uploading: "ビデオをアップロード中...",
        processing: "ビデオを処理中...数分かかる場合があります。",

        // ビデオ情報
        filename: "ファイル名",
        detectedLanguage: "検出された言語",
        transcriptionMethod: "文字起こし方法",
        summary: "要約",

        // チャットセクション
        chatTitle: "質問する",
        questionPlaceholder: "ここに質問を入力してください...",
        send: "送信",
        clearChat: "チャットをクリア",
        clearChatConfirm: "チャット履歴をクリアしてもよろしいですか？",

        // クイックアクション
        quickActions: "クイックアクション",
        create10QA: "10個のQ&Aを作成",
        keyPoints: "10個の重要ポイント",
        detailedSummary: "詳細な要約",
        askAnyQuestion: "任意の質問をする",

        // ステータスメッセージ
        uploadSuccess: "ビデオが正常にアップロードされました！",
        processingInBackground: "バックグラウンドで処理中...",
        processingComplete: "処理が完了しました！",
        languageDetected: "検出された言語:",
        error: "エラー",

        // ボタン
        cancel: "キャンセル",
        ok: "OK"
    },

    es: {
        // Encabezado
        appTitle: "Analizador de Video AI",
        appSubtitle: "Sube, Transcribe, Analiza con IA",

        // Selector de idioma
        selectLanguage: "Seleccionar Idioma",
        autoDetect: "Detección automática",
        videoLanguage: "Idioma del Video",
        interfaceLanguage: "Idioma de la Interfaz",

        // Sección de carga
        uploadTitle: "Subir Video",
        uploadText: "Arrastra y suelta el video aquí o haz clic para buscar",
        uploadHint: "Compatible con MP4, AVI, MOV y más",
        uploading: "Subiendo video...",
        processing: "Procesando video... Esto puede tardar unos minutos.",

        // Información del video
        filename: "Nombre del archivo",
        detectedLanguage: "Idioma detectado",
        transcriptionMethod: "Método de transcripción",
        summary: "Resumen",

        // Sección de chat
        chatTitle: "Hacer Preguntas",
        questionPlaceholder: "Escribe tu pregunta aquí...",
        send: "Enviar",
        clearChat: "Limpiar Chat",
        clearChatConfirm: "¿Estás seguro de que quieres borrar el historial del chat?",

        // Acciones rápidas
        quickActions: "Acciones Rápidas",
        create10QA: "Crear 10 P&R",
        keyPoints: "10 Puntos Clave",
        detailedSummary: "Resumen Detallado",
        askAnyQuestion: "Hacer Cualquier Pregunta",

        // Mensajes de estado
        uploadSuccess: "¡Video subido exitosamente!",
        processingInBackground: "Procesando en segundo plano...",
        processingComplete: "¡Procesamiento completo!",
        languageDetected: "Idioma detectado:",
        error: "Error",

        // Botones
        cancel: "Cancelar",
        ok: "OK"
    }
};

// Language manager class
class LanguageManager {
    constructor() {
        this.currentUILanguage = localStorage.getItem('uiLanguage') || 'en';
        this.currentVideoLanguage = localStorage.getItem('videoLanguage') || 'auto';
        this.supportedLanguages = null;
    }

    async loadSupportedLanguages() {
        try {
            const response = await fetch(`${API_BASE_URL}/supported-languages/`);
            const data = await response.json();
            this.supportedLanguages = data.languages;
            return this.supportedLanguages;
        } catch (error) {
            console.error('Failed to load supported languages:', error);
            return null;
        }
    }

    setUILanguage(lang) {
        this.currentUILanguage = lang;
        localStorage.setItem('uiLanguage', lang);
        this.updateUI();
        document.documentElement.lang = lang;
    }

    setVideoLanguage(lang) {
        this.currentVideoLanguage = lang;
        localStorage.setItem('videoLanguage', lang);
    }

    getUILanguage() {
        return this.currentUILanguage;
    }

    getVideoLanguage() {
        return this.currentVideoLanguage;
    }

    t(key) {
        return translations[this.currentUILanguage]?.[key] || translations['en'][key] || key;
    }

    updateUI() {
        // Update all text elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = this.t(key);
            } else {
                element.textContent = this.t(key);
            }
        });

        // Update title and meta tags
        document.title = this.t('appTitle');
    }
}

// Initialize global language manager
const i18n = new LanguageManager();
```

#### 5.2 Update HTML with Language Selectors
**File:** `frontend/index.html`

Add language selector section in the header:

```html
<div class="header">
    <h1 data-i18n="appTitle">Video Analyzer AI</h1>
    <p data-i18n="appSubtitle">Upload, Transcribe, Analyze with AI</p>

    <!-- Language Selector Section -->
    <div class="language-selector-container">
        <div class="language-selector">
            <label for="uiLanguageSelect" data-i18n="interfaceLanguage">Interface Language:</label>
            <select id="uiLanguageSelect" class="language-dropdown">
                <!-- Will be populated dynamically -->
            </select>
        </div>

        <div class="language-selector">
            <label for="videoLanguageSelect" data-i18n="videoLanguage">Video Language:</label>
            <select id="videoLanguageSelect" class="language-dropdown">
                <option value="auto" data-i18n="autoDetect">Auto-detect</option>
                <!-- Will be populated dynamically -->
            </select>
        </div>
    </div>
</div>
```

Add CSS for language selectors:

```css
.language-selector-container {
    display: flex;
    gap: 20px;
    justify-content: center;
    margin-top: 20px;
    flex-wrap: wrap;
}

.language-selector {
    display: flex;
    align-items: center;
    gap: 10px;
}

.language-selector label {
    font-size: 0.9em;
    font-weight: 500;
}

.language-dropdown {
    padding: 8px 15px;
    border-radius: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    background: rgba(255, 255, 255, 0.2);
    color: white;
    font-size: 0.9em;
    cursor: pointer;
    transition: all 0.3s ease;
}

.language-dropdown:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
}

.language-dropdown:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.4);
}

.language-dropdown option {
    background: #fff;
    color: #333;
}
```

#### 5.3 Update JavaScript for Multi-Language
**File:** `frontend/script.js`

```javascript
class VideoAnalyzer {
    constructor() {
        this.initializeLanguages();
        this.initializeEventListeners();
        this.setupDragAndDrop();
        this.setupSuggestionChips();
    }

    async initializeLanguages() {
        // Load supported languages from API
        await i18n.loadSupportedLanguages();

        // Populate language dropdowns
        this.populateLanguageSelectors();

        // Update UI with current language
        i18n.updateUI();

        // Set up language change listeners
        document.getElementById('uiLanguageSelect').addEventListener('change', (e) => {
            i18n.setUILanguage(e.target.value);
        });

        document.getElementById('videoLanguageSelect').addEventListener('change', (e) => {
            i18n.setVideoLanguage(e.target.value);
        });
    }

    populateLanguageSelectors() {
        const uiSelect = document.getElementById('uiLanguageSelect');
        const videoSelect = document.getElementById('videoLanguageSelect');

        if (i18n.supportedLanguages) {
            // Clear existing options
            uiSelect.innerHTML = '';
            videoSelect.innerHTML = '<option value="auto" data-i18n="autoDetect">Auto-detect</option>';

            // Add language options
            Object.entries(i18n.supportedLanguages).forEach(([code, lang]) => {
                const option1 = document.createElement('option');
                option1.value = code;
                option1.textContent = `${lang.flag} ${lang.native_name}`;
                uiSelect.appendChild(option1);

                const option2 = document.createElement('option');
                option2.value = code;
                option2.textContent = `${lang.flag} ${lang.native_name}`;
                videoSelect.appendChild(option2);
            });

            // Set current values
            uiSelect.value = i18n.getUILanguage();
            videoSelect.value = i18n.getVideoLanguage();
        }
    }

    async handleFileSelect(file) {
        if (!file) return;

        if (!file.type.startsWith('video/')) {
            this.showError(i18n.t('error') + ': Invalid video file');
            return;
        }

        this.showLoading(true, i18n.t('uploading'));
        this.hideError();

        try {
            const formData = new FormData();
            formData.append('file', file);

            // Get selected languages
            const videoLang = i18n.getVideoLanguage();
            const uiLang = i18n.getUILanguage();

            // Build URL with language parameters
            let url = `${API_BASE_URL}/upload-video/?ui_language=${uiLang}`;
            if (videoLang && videoLang !== 'auto') {
                url += `&language=${videoLang}`;
            }

            const response = await fetch(url, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || i18n.t('error'));
            }

            const data = await response.json();
            currentVideoId = data.video_id;

            this.showSuccess(i18n.t('uploadSuccess'));
            this.showLoading(true, i18n.t('processing'));

            await this.pollProcessingStatus(currentVideoId);

        } catch (error) {
            this.showError(i18n.t('error') + ': ' + error.message);
            this.showLoading(false);
        }
    }

    async pollProcessingStatus(videoId) {
        const maxAttempts = 120;
        let attempts = 0;

        const checkStatus = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/video-status/${videoId}`);
                const data = await response.json();

                if (data.processing_status === 'completed') {
                    this.showLoading(false);
                    this.showSuccess(i18n.t('processingComplete'));

                    // Show detected language if available
                    if (data.detected_language) {
                        const langInfo = i18n.supportedLanguages[data.detected_language];
                        const langName = langInfo ? langInfo.native_name : data.detected_language;
                        this.showInfo(`${i18n.t('languageDetected')} ${langInfo.flag} ${langName}`);
                    }

                    this.displayVideoInfo(data);
                    this.showChatSection();
                } else if (data.processing_status === 'failed') {
                    this.showLoading(false);
                    this.showError(i18n.t('error') + ': ' + data.error_message);
                } else if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(checkStatus, 2000);
                } else {
                    this.showLoading(false);
                    this.showError(i18n.t('error') + ': Processing timeout');
                }
            } catch (error) {
                this.showError(i18n.t('error') + ': ' + error.message);
                this.showLoading(false);
            }
        };

        checkStatus();
    }

    async askQuestion() {
        const questionInput = document.getElementById('questionInput');
        const question = questionInput.value.trim();

        if (!question || !currentVideoId) return;

        questionInput.value = '';
        this.addMessageToChat(question, 'user');

        try {
            const uiLang = i18n.getUILanguage();
            const response = await fetch(
                `${API_BASE_URL}/ask-question/?ui_language=${uiLang}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        video_id: currentVideoId,
                        question: question
                    })
                }
            );

            if (!response.ok) throw new Error(i18n.t('error'));

            const data = await response.json();
            this.addMessageToChat(data.answer, 'assistant');

        } catch (error) {
            this.showError(i18n.t('error') + ': ' + error.message);
        }
    }

    displayVideoInfo(data) {
        const videoInfo = document.getElementById('videoInfo');
        const summaryDiv = document.getElementById('summary');
        const filenameSpan = document.getElementById('filenameDisplay');

        filenameSpan.textContent = data.filename;

        // Add detected language badge
        if (data.detected_language) {
            const langInfo = i18n.supportedLanguages[data.detected_language];
            const langBadge = document.createElement('span');
            langBadge.className = 'language-badge';
            langBadge.textContent = `${langInfo.flag} ${langInfo.native_name}`;
            filenameSpan.appendChild(document.createTextNode(' '));
            filenameSpan.appendChild(langBadge);
        }

        summaryDiv.innerHTML = this.formatMarkdown(data.summary);
        videoInfo.style.display = 'block';
    }

    clearChat() {
        if (confirm(i18n.t('clearChatConfirm'))) {
            const chatHistory = document.getElementById('chatHistory');
            chatHistory.innerHTML = '';
        }
    }

    showInfo(message) {
        const infoDiv = document.createElement('div');
        infoDiv.className = 'info-message';
        infoDiv.textContent = message;
        document.querySelector('.main-content').insertBefore(
            infoDiv,
            document.querySelector('.upload-section')
        );

        setTimeout(() => {
            infoDiv.remove();
        }, 5000);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    videoAnalyzer = new VideoAnalyzer();
});
```

### Success Criteria
- [ ] Language selectors visible and functional
- [ ] UI updates when language changed
- [ ] All text properly translated
- [ ] Language preferences persist in localStorage
- [ ] Detected language displayed to user

### Estimated Time: 4 hours

---

## 🧪 Phase 6: Testing & Quality Assurance

### Objective
Comprehensive testing of multi-language features across different scenarios.

### Tasks

#### 6.1 Create Test Suite
**File:** `tests/test_multilanguage.py` (New File)

```python
"""
Multi-language feature test suite
"""
import pytest
import os
from backend.video_processor import VideoProcessor
from backend.language_config import SUPPORTED_LANGUAGES, get_azure_language_code

class TestMultiLanguage:

    def test_language_config(self):
        """Test language configuration"""
        assert 'en' in SUPPORTED_LANGUAGES
        assert 'ja' in SUPPORTED_LANGUAGES
        assert get_azure_language_code('en') == 'en-US'
        assert get_azure_language_code('ja') == 'ja-JP'

    def test_language_detection(self):
        """Test language detection with sample audio"""
        # Requires sample audio files
        pass

    def test_multi_language_transcription(self):
        """Test transcription in different languages"""
        # Requires sample videos in different languages
        pass

    def test_multi_language_summary(self):
        """Test summary generation in different languages"""
        processor = VideoProcessor()

        sample_text = "This is a test transcription in English."

        # Test English summary
        summary_en = processor.generate_summary(sample_text, 'en')
        assert len(summary_en) > 0

        # Test Japanese summary
        summary_ja = processor.generate_summary(sample_text, 'ja')
        assert len(summary_ja) > 0
        # Should contain Japanese characters
        assert any(ord(c) > 127 for c in summary_ja)

    def test_api_language_endpoints(self):
        """Test API endpoints for language support"""
        # Test /supported-languages/ endpoint
        # Test language parameters in upload
        # Test language parameters in Q&A
        pass
```

#### 6.2 Manual Testing Checklist

**Functional Tests:**
- [ ] Upload English video → Auto-detect → English transcription
- [ ] Upload Japanese video → Auto-detect → Japanese transcription
- [ ] Upload Spanish video → Auto-detect → Spanish transcription
- [ ] Manual language selection (English)
- [ ] Manual language selection (Japanese)
- [ ] Manual language selection (Spanish)
- [ ] Generate summary in English
- [ ] Generate summary in Japanese
- [ ] Generate summary in Spanish
- [ ] Q&A in English
- [ ] Q&A in Japanese
- [ ] Q&A in Spanish

**UI Tests:**
- [ ] Language selector changes UI language
- [ ] Video language selector works
- [ ] Auto-detect option available
- [ ] Language preferences persist after reload
- [ ] All text properly translated
- [ ] Detected language badge shows correctly
- [ ] Language info in video status

**Edge Cases:**
- [ ] No speech detected → Proper error message
- [ ] Very short video (< 10 seconds)
- [ ] Very long video (> 30 minutes)
- [ ] Poor audio quality
- [ ] Background noise/music
- [ ] Multiple speakers
- [ ] Mixed languages in one video
- [ ] Unsupported language selected

**Performance Tests:**
- [ ] Language detection speed (< 5 seconds)
- [ ] Transcription time acceptable
- [ ] No memory leaks with multiple uploads
- [ ] Concurrent uploads with different languages

#### 6.3 Create Test Videos
Create or obtain test videos in different languages:
- English: 1-2 minute video
- Japanese: 1-2 minute video
- Spanish: 1-2 minute video
- Clear speech, minimal background noise

### Success Criteria
- [ ] All functional tests pass
- [ ] All UI tests pass
- [ ] Edge cases handled gracefully
- [ ] Performance acceptable
- [ ] No critical bugs found

### Estimated Time: 4 hours

---

## 📚 Phase 7: Documentation

### Objective
Update all documentation to reflect multi-language capabilities.

### Tasks

#### 7.1 Update Main Documentation
**File:** `PROJECT_DOCUMENTATION.md`

Add sections:
- Multi-language support overview
- Supported languages list
- Language detection details
- How to use language features
- Troubleshooting language-specific issues

#### 7.2 Update README
**File:** `README.md`

Add:
- Multi-language feature highlights
- Language selector screenshots
- Quick start guide for different languages
- Supported languages badge

#### 7.3 Create Multi-Language Guide
**File:** `MULTILANGUAGE_GUIDE.md` (New File)

Include:
- Detailed feature explanation
- Step-by-step usage guide
- Language-specific tips
- API documentation for language parameters
- Troubleshooting guide
- FAQ

#### 7.4 Update API Documentation
- Add language parameters to API docs
- Document new endpoints
- Add examples for different languages
- Update Postman collection

### Success Criteria
- [ ] All documentation updated
- [ ] New guide created
- [ ] API docs complete
- [ ] Examples provided
- [ ] Screenshots added

### Estimated Time: 2 hours

---

## 🚀 Phase 8: Deployment

### Objective
Deploy multi-language features to production environment.

### Tasks

#### 8.1 Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Database migration script ready
- [ ] Environment variables configured
- [ ] API credentials verified
- [ ] Backup database before migration

#### 8.2 Deployment Steps

1. **Backup Current System:**
```bash
cp video_analyzer.db video_analyzer.db.backup
cp -r uploads uploads.backup
```

2. **Run Database Migration:**
```bash
python3 backend/migrate_db_multilang.py
```

3. **Update Dependencies:**
```bash
pip3 install azure-cognitiveservices-speech --upgrade
pip3 install openai --upgrade
```

4. **Deploy Backend Changes:**
```bash
# Test backend first
python3 backend/main.py

# If successful, restart production server
```

5. **Deploy Frontend Changes:**
```bash
# Copy updated frontend files
# Test frontend
# Deploy to production
```

6. **Verify Deployment:**
- [ ] Health check passes
- [ ] Language endpoints working
- [ ] Upload with language selection works
- [ ] UI language switching works
- [ ] No errors in logs

#### 8.3 Post-Deployment Monitoring
- Monitor API error rates
- Track language usage statistics
- Monitor transcription success rates
- Collect user feedback

### Success Criteria
- [ ] Deployment successful
- [ ] No errors in production
- [ ] All features working
- [ ] Monitoring active
- [ ] Rollback plan ready

### Estimated Time: 2 hours

---

## 📊 Success Metrics

Track these metrics to measure success:

### User Adoption
- Number of videos processed per language
- Language preference distribution
- Auto-detect vs manual selection ratio

### Quality Metrics
- Language detection accuracy (target: >90%)
- Transcription accuracy per language
- User satisfaction ratings
- Error rate by language

### Performance Metrics
- Average detection time (target: <5 seconds)
- Average transcription time per minute of video
- API response times
- System resource usage

---

## 🐛 Troubleshooting Guide

### Common Issues

**Issue 1: Language Detection Not Working**
- Check Azure Speech Services credentials
- Verify audio quality
- Check language is in supported list
- Review Azure service region

**Issue 2: Transcription Failed**
- Check audio extraction successful
- Verify language code correct
- Test fallback methods
- Check API quota not exceeded

**Issue 3: Summary Not in Correct Language**
- Verify ui_language parameter passed correctly
- Check GPT-4 model responding properly
- Review prompt formatting

**Issue 4: UI Not Translating**
- Check translation keys exist
- Verify i18n initialization
- Check browser localStorage
- Clear browser cache

---

## 🔄 Future Enhancements

After successful implementation, consider:

### Phase 2 Features
1. **Real-time Translation**
   - Translate transcriptions between languages
   - Side-by-side view

2. **Subtitle Generation**
   - Generate SRT/VTT files
   - Multi-language subtitles

3. **Voice Synthesis**
   - Generate audio summaries
   - Multi-language narration

4. **Advanced Language Features**
   - Dialect detection (US/UK English, etc.)
   - Code-switching detection
   - Speaker diarization with language

5. **Language Learning Mode**
   - Vocabulary extraction
   - Language difficulty assessment
   - Study materials generation

---

## 💰 Cost Analysis

### Azure Speech Services
- **Transcription:** ~$1 per audio hour
- **Language Detection:** Included
- **Free Tier:** 5 hours/month
- **Expected Monthly Cost:** $10-50 (depending on usage)

### OpenAI/Rakuten Gateway
- **GPT-4 Summary:** ~$0.01 per video
- **GPT-4 Q&A:** ~$0.005 per question
- **Expected Monthly Cost:** $20-100 (depending on usage)

### Total Estimated Cost
- **Light Usage:** $30/month
- **Medium Usage:** $100/month
- **Heavy Usage:** $300/month

---

## 📞 Support & Resources

### Internal Resources
- Project Documentation: `/PROJECT_DOCUMENTATION.md`
- Multi-Language Guide: `/MULTILANGUAGE_GUIDE.md`
- Database Guide: `/DATABASE_GUIDE.md`

### External Resources
- Azure Speech Services: https://docs.microsoft.com/azure/cognitive-services/speech-service/
- OpenAI API: https://platform.openai.com/docs
- ISO 639-1 Language Codes: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

---

## ✅ Implementation Checklist

### Phase 1: Database Schema ✓
- [ ] Update Video model
- [ ] Update ChatHistory model
- [ ] Create migration script
- [ ] Run migration successfully
- [ ] Verify database structure

### Phase 2: Backend Core ✓
- [ ] Create language_config.py
- [ ] Add environment variables
- [ ] Test language mappings
- [ ] Verify helper functions

### Phase 3: Language Detection & Processing ✓
- [ ] Add language detection method
- [ ] Update transcription methods
- [ ] Update summary generation
- [ ] Update Q&A method
- [ ] Update process_video method

### Phase 4: API Endpoints ✓
- [ ] Add language endpoints
- [ ] Update upload endpoint
- [ ] Update background processing
- [ ] Update Q&A endpoint
- [ ] Update status endpoint

### Phase 5: Frontend UI ✓
- [ ] Create translations.js
- [ ] Add language selectors to HTML
- [ ] Update CSS styles
- [ ] Update JavaScript logic
- [ ] Test UI translations

### Phase 6: Testing ✓
- [ ] Functional tests
- [ ] UI tests
- [ ] Edge case tests
- [ ] Performance tests
- [ ] Bug fixes

### Phase 7: Documentation ✓
- [ ] Update PROJECT_DOCUMENTATION.md
- [ ] Update README.md
- [ ] Create MULTILANGUAGE_GUIDE.md
- [ ] Update API docs

### Phase 8: Deployment ✓
- [ ] Backup system
- [ ] Run migration
- [ ] Deploy backend
- [ ] Deploy frontend
- [ ] Verify deployment
- [ ] Monitor system

---

## 🎉 Conclusion

This implementation plan provides a comprehensive roadmap for adding multi-language support to the Video Analyzer AI application. With your existing Azure Speech Services and Rakuten AI Gateway credentials verified and working, you're fully equipped to implement all features.

**Estimated Total Time:** 21 hours (3 working days)

**Next Step:** Begin with Phase 1 (Database Schema Updates)

---

**Document Version:** 1.0
**Last Updated:** November 4, 2025
**Status:** Ready for Implementation
**Created By:** AI Implementation Planning Team
