# Video Analyzer AI - Complete Project Documentation

**Version**: 2.0 (Multi-Language Edition)
**Last Updated**: November 2024
**Maintainer**: Development Team

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Features](#4-features)
5. [Multi-Language System](#5-multi-language-system)
6. [Backend Architecture](#6-backend-architecture)
7. [Frontend Architecture](#7-frontend-architecture)
8. [Database Schema](#8-database-schema)
9. [API Endpoints](#9-api-endpoints)
10. [Video Processing Pipeline](#10-video-processing-pipeline)
11. [File Structure](#11-file-structure)
12. [Configuration](#12-configuration)
13. [Setup & Installation](#13-setup--installation)
14. [Performance Considerations](#14-performance-considerations)
15. [Troubleshooting](#15-troubleshooting)
16. [Future Enhancements](#16-future-enhancements)

---

## 1. Project Overview

### What is Video Analyzer AI?

Video Analyzer AI is a web-based application that allows users to:
- Upload video files in various formats (MP4, AVI, MOV, etc.)
- Automatically transcribe video audio using Azure Speech Services
- Generate AI-powered summaries of video content
- Ask questions about the video and receive intelligent answers
- Support for multiple languages (English and Japanese)

### Key Capabilities

- **Automatic Language Detection**: Detects the language spoken in videos
- **Multi-Language UI**: Interface available in English and Japanese
- **AI-Powered Q&A**: Ask questions about video content using GPT-4
- **Background Processing**: Videos process asynchronously without blocking the UI
- **Real-time Status Updates**: Polling mechanism for processing progress
- **Three-Tier Transcription**: Fallback system (Azure Speech → Azure Whisper → Local Whisper)

### Use Cases

1. **Educational Content**: Students can upload lecture videos and ask questions
2. **Meeting Recordings**: Extract key points and summaries from meetings
3. **Video Research**: Analyze video content without watching the entire video
4. **Cross-Language Learning**: Watch Japanese videos with English summaries or vice versa
5. **Content Accessibility**: Make video content searchable and accessible

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Frontend (HTML/CSS/JavaScript)                        │    │
│  │  - index.html (UI Structure)                           │    │
│  │  - script.js (Application Logic)                       │    │
│  │  - translations.js (Multi-Language Support)            │    │
│  └─────────────────┬──────────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────────┘
                     │
                     │ HTTP/HTTPS Requests
                     │
┌────────────────────▼───────────────────────────────────────────┐
│                    BACKEND SERVER                               │
│  ┌──────────────────────────────────────────────────────┐     │
│  │  FastAPI Application (main.py)                       │     │
│  │  - REST API Endpoints                                │     │
│  │  - Background Task Management                        │     │
│  │  - CORS Configuration                                │     │
│  └──────────────┬────────────┬────────────┬─────────────┘     │
│                 │            │            │                     │
│  ┌──────────────▼──┐  ┌─────▼──────┐  ┌─▼──────────────┐     │
│  │ Video Processor │  │   Models   │  │ Language Config │     │
│  │ (video_processor│  │ (models.py)│  │(language_config │     │
│  │      .py)       │  │            │  │     .py)        │     │
│  │                 │  │            │  │                 │     │
│  │ - Audio Extract │  │ - Video    │  │ - Language Maps │     │
│  │ - Transcription │  │ - ChatHist │  │ - Translations  │     │
│  │ - AI Summary    │  │ - Database │  │                 │     │
│  │ - Q&A           │  │   Session  │  │                 │     │
│  └────────┬────────┘  └─────┬──────┘  └─────────────────┘     │
└───────────┼──────────────────┼─────────────────────────────────┘
            │                  │
            │                  │
    ┌───────▼────────┐  ┌─────▼──────────┐
    │  External APIs │  │    Database    │
    │                │  │                │
    │ • Azure Speech │  │   SQLite DB    │
    │ • Azure Whisper│  │                │
    │ • OpenAI GPT-4 │  │ • Videos Table │
    │ • Rakuten AI   │  │ • Chat History │
    └────────────────┘  └────────────────┘
```

### Component Interaction Flow

1. **User uploads video** → Frontend sends file to Backend
2. **Backend saves file** → Creates database entry with "pending" status
3. **Background processing starts** → FastAPI BackgroundTasks
4. **Video processing pipeline**:
   - Extract audio from video (moviepy/FFmpeg)
   - Detect language (Azure Speech Services)
   - Transcribe audio (3-tier fallback system)
   - Generate summary (GPT-4 via Rakuten AI Gateway)
5. **Frontend polls for status** → Every 5 seconds
6. **Processing completes** → Status changes to "completed"
7. **Display results** → Show summary and enable Q&A

---

## 3. Technology Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.104.1 | High-performance web framework |
| **Server** | Uvicorn | 0.24.0 | ASGI server |
| **Database** | SQLite | - | Embedded database |
| **ORM** | SQLAlchemy | 2.0.23 | Database abstraction |
| **Video Processing** | moviepy | 1.0.3 | Audio extraction |
| **Audio Processing** | Azure Speech SDK | 1.32.1 | Transcription & language detection |
| **AI/LLM** | OpenAI (via Rakuten) | 1.3.7+ | GPT-4 for summaries & Q&A |
| **Configuration** | python-decouple | 3.8 | Environment variable management |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Core** | Vanilla JavaScript | ES6+ | Application logic |
| **UI** | HTML5 + CSS3 | - | User interface |
| **HTTP Client** | Fetch API | Native | API communication |
| **Storage** | LocalStorage | Native | Language preferences |
| **Styling** | CSS Gradients | - | Modern UI design |

### External Services

| Service | Provider | Purpose |
|---------|----------|---------|
| **Azure Speech Services** | Microsoft Azure | Language detection & transcription |
| **Azure Whisper** | Microsoft Azure | Fallback transcription |
| **Rakuten AI Gateway** | Rakuten | OpenAI API proxy for GPT-4 |
| **Local Whisper** | OpenAI (self-hosted) | Final fallback transcription |

---

## 4. Features

### Core Features

#### 4.1 Video Upload & Processing

**Description**: Users can upload videos which are processed in the background.

**Supported Formats**: MP4, AVI, MOV, MKV, and most common video formats

**Process**:
1. Client-side validation (file type check)
2. Chunked upload (1MB chunks) for large files
3. Server-side storage in `./uploads/` directory
4. Background processing initiated immediately

**Technical Details**:
- Maximum file size: Limited by server configuration
- Upload endpoint: `/upload-video/`
- Processing is asynchronous (non-blocking)
- Status can be checked via polling

#### 4.2 Automatic Transcription

**Description**: Videos are automatically transcribed using a 3-tier fallback system.

**Transcription Methods** (in order of preference):
1. **Azure Speech Services** (Primary)
   - Fastest and most accurate
   - Supports continuous recognition for long videos
   - Real-time language detection

2. **Azure Whisper** (Fallback #1)
   - Uses OpenAI's Whisper model via Rakuten AI Gateway
   - Good accuracy for multiple languages

3. **Local Whisper** (Fallback #2)
   - Self-hosted Whisper model
   - Fully offline operation
   - Slowest but most reliable

**Technical Details**:
- Audio extracted at 16kHz mono for optimal speech recognition
- Supports English and Japanese natively
- Transcription stored in database for future queries

#### 4.3 AI-Powered Summaries

**Description**: GPT-4 generates concise summaries of video content.

**Features**:
- Automatic summary generation after transcription
- Summary language matches UI language preference
- Typically 200-500 words
- Highlights key points and main themes

**Technical Details**:
- Uses GPT-4 via Rakuten AI Gateway
- Max tokens: 500
- Prompt engineered for video content summarization
- Language-specific prompts for better results

#### 4.4 Interactive Q&A

**Description**: Users can ask questions about video content.

**Features**:
- Natural language question processing
- Context-aware answers based on transcription
- Support for multiple questions
- Quick action buttons for common queries:
  - "Create 10 Q&A"
  - "10 Key Points"
  - "Detailed Summary"
  - Custom questions

**Technical Details**:
- Uses GPT-4 with video transcription as context
- Answers stored in `chat_history` table
- Language-specific responses
- Max tokens: 2000 per answer

#### 4.5 Multi-Language Support (NEW in v2.0)

**Description**: Full internationalization support for English and Japanese.

**Supported Languages**:
- **English (en)**: Default language
- **Japanese (ja)**: Full UI and processing support

**Features**:
- **Dual Language Selectors**:
  - Interface Language: Controls UI text
  - Video Language: Controls transcription language or auto-detect

- **Automatic Language Detection**:
  - Uses Azure Speech Services
  - Detects language from first 10-15 seconds of audio

- **Language Persistence**:
  - Settings saved in browser LocalStorage
  - Preferences survive page refresh

- **Per-Video Language Tracking**:
  - Detected language stored with video
  - UI language stored with video
  - Transcription method tracked

**Technical Details**:
- Language codes: ISO 639-1 format (en, ja)
- Translation system: `translations.js` with 60+ keys
- LanguageManager class for state management
- API parameters: `language`, `ui_language`

---

## 5. Multi-Language System

### Overview

The multi-language system consists of three layers:

1. **Frontend Translation Layer**: UI text translations
2. **Backend Language Processing**: Transcription and AI responses
3. **Database Language Tracking**: Storage of language metadata

### 5.1 Frontend Translation System

#### Translation Dictionary Structure

**File**: `/frontend/translations.js`

```javascript
const translations = {
    en: {
        // English translations
        appTitle: "Video Analyzer AI",
        uploadText: "Drag and drop video here or click to browse",
        // ... 60+ more keys
    },
    ja: {
        // Japanese translations
        appTitle: "ビデオ分析AI",
        uploadText: "ビデオをここにドラッグ＆ドロップまたはクリックして選択",
        // ... 60+ more keys
    }
};
```

#### LanguageManager Class

**Purpose**: Manages language state and UI updates

**Key Methods**:
- `setUILanguage(lang)`: Changes interface language
- `setVideoLanguage(lang)`: Sets video transcription preference
- `getUILanguage()`: Returns current UI language
- `getVideoLanguage()`: Returns video language preference
- `t(key)`: Translates a key to current language
- `updateUI()`: Updates all UI elements with current translations
- `loadSupportedLanguages()`: Fetches supported languages from API

**LocalStorage Keys**:
- `uiLanguage`: Current interface language (en/ja)
- `videoLanguage`: Video transcription preference (auto/en/ja)

#### HTML Integration

**Data Attributes**: Elements marked with `data-i18n` attribute:

```html
<h1 data-i18n="appTitle">Video Analyzer AI</h1>
<button data-i18n="send">Send</button>
```

**Language Selectors**:
```html
<select id="uiLanguageSelect">
    <option value="en">🇺🇸 English</option>
    <option value="ja">🇯🇵 日本語</option>
</select>

<select id="videoLanguageSelect">
    <option value="auto">Auto-detect</option>
    <option value="en">🇺🇸 English</option>
    <option value="ja">🇯🇵 日本語</option>
</select>
```

### 5.2 Backend Language Configuration

#### Language Configuration File

**File**: `/backend/language_config.py`

**Purpose**: Central configuration for all language-related settings

**Structure**:
```python
SUPPORTED_LANGUAGES = {
    'en': {
        'name': 'English',
        'native_name': 'English',
        'azure_code': 'en-US',      # Azure Speech format
        'whisper_code': 'en',        # Whisper format
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
    }
}
```

**Key Functions**:
- `get_azure_language_code(lang)`: Converts 'en' → 'en-US'
- `get_whisper_language_code(lang)`: Converts 'en' → 'en'
- `get_language_name(lang)`: Returns "English" for 'en'
- `get_enabled_languages()`: Returns all enabled languages

#### Language Detection

**File**: `/backend/video_processor.py`

**Method**: `detect_language(audio_path)`

**Process**:
1. Initialize Azure Speech SDK
2. Configure auto-detect with candidate languages (en-US, ja-JP)
3. Create SourceLanguageRecognizer
4. Recognize from first portion of audio
5. Extract language code (en-US → en)
6. Return ISO 639-1 code

**Example**:
```python
def detect_language(self, audio_path: str) -> str:
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key,
        region=service_region
    )

    auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
        languages=['en-US', 'ja-JP']
    )

    recognizer = speechsdk.SourceLanguageRecognizer(
        speech_config=speech_config,
        auto_detect_source_language_config=auto_detect_config,
        audio_config=audio_config
    )

    result = recognizer.recognize_once()
    detected = result.properties[PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult]
    return detected.split('-')[0]  # 'en-US' -> 'en'
```

### 5.3 Language-Aware Processing

#### Transcription with Language

**Method**: `transcribe_audio(audio_path, language)`

**Parameters**:
- `audio_path`: Path to extracted audio file
- `language`: ISO 639-1 code ('en', 'ja')

**Process**:
```python
def transcribe_audio(self, audio_path: str, language: str = 'en') -> tuple:
    try:
        # Try Azure Speech first with specific language
        text = self._transcribe_with_azure_speech(audio_path, language)
        return (text, 'azure_speech')
    except Exception as azure_error:
        # Fallback to Azure Whisper
        try:
            text = self._transcribe_with_azure_whisper(audio_path, language)
            return (text, 'azure_whisper')
        except Exception as whisper_error:
            # Final fallback to local Whisper
            text = self._transcribe_with_local_whisper(audio_path, language)
            return (text, 'local_whisper')
```

#### Summary Generation with Language

**Method**: `generate_summary(transcription, language)`

**Process**:
1. Get language name (en → "English")
2. Create language-specific system prompt
3. Send to GPT-4 with instruction to respond in target language
4. Return summary in requested language

**Example Prompt**:
```python
system_prompt = (
    f"You are an AI assistant that creates concise summaries of video transcriptions. "
    f"Provide a clear, informative summary in {lang_name} language that captures "
    f"the main points and key information. Respond ONLY in {lang_name}."
)
```

#### Q&A with Language

**Method**: `answer_question(transcription, question, language)`

**Process**:
1. Accept question in any language
2. Use transcription (in original language) as context
3. Generate answer in specified UI language
4. Return formatted response

**Key Feature**: Cross-language Q&A
- Question in English → Answer in Japanese
- Question in Japanese → Answer in English
- Depends on `ui_language` parameter

---

## 6. Backend Architecture

### 6.1 Main Application (main.py)

#### Initialization

```python
app = FastAPI(
    title="Video Analyzer API",
    description="AI-powered video analysis and Q&A system with multi-language support"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
processor = VideoProcessor()  # Handles all video processing
create_tables()               # Initialize database
```

#### Key Components

1. **Request Models** (Pydantic):
```python
class QuestionRequest(BaseModel):
    video_id: int
    question: str

class VideoResponse(BaseModel):
    id: int
    filename: str
    transcription: str
    summary: str
```

2. **Background Processing**:
```python
async def process_video_background(
    video_id: int,
    file_path: str,
    language: str = None,
    ui_language: str = 'en'
):
    # Runs in background thread
    # Updates database as processing progresses
    # Handles errors gracefully
```

### 6.2 Video Processor (video_processor.py)

#### Class Structure

```python
class VideoProcessor:
    def __init__(self):
        self.upload_dir = config('UPLOAD_DIR', default='./uploads')

    # Audio extraction
    def extract_audio_from_video(self, video_path: str) -> str

    # Language detection
    def detect_language(self, audio_path: str) -> str

    # Transcription (3 methods)
    def transcribe_audio(self, audio_path: str, language: str) -> tuple
    def _transcribe_with_azure_speech(self, audio_path: str, language: str) -> str
    def _transcribe_with_azure_whisper(self, audio_path: str, language: str) -> str
    def _transcribe_with_local_whisper(self, audio_path: str, language: str) -> str

    # AI generation
    def generate_summary(self, transcription: str, language: str) -> str
    def answer_question(self, transcription: str, question: str, language: str) -> str

    # Main pipeline
    def process_video(self, video_path: str, user_language: str, ui_language: str) -> dict
```

#### Processing Pipeline

```python
def process_video(self, video_path: str, user_language: str = None, ui_language: str = 'en') -> dict:
    # Step 1: Extract audio
    audio_path = self.extract_audio_from_video(video_path)

    # Step 2: Detect or use specified language
    if user_language and user_language != 'auto':
        detected_language = user_language
    else:
        detected_language = self.detect_language(audio_path)

    # Step 3: Transcribe in detected language
    transcription, method = self.transcribe_audio(audio_path, detected_language)

    # Step 4: Generate summary in UI language
    summary = self.generate_summary(transcription, ui_language)

    # Step 5: Cleanup and return
    os.remove(audio_path)

    return {
        "transcription": transcription,
        "summary": summary,
        "detected_language": detected_language,
        "transcription_method": method
    }
```

### 6.3 Database Models (models.py)

#### Video Model

```python
class Video(Base):
    __tablename__ = "videos"

    # Core fields
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    transcription = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)

    # Status tracking
    processing_status = Column(String, default="pending")  # pending/processing/completed/failed
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    # Multi-language fields (NEW in v2.0)
    detected_language = Column(String(10), nullable=True)       # Auto-detected: 'en', 'ja'
    user_selected_language = Column(String(10), nullable=True)  # User override
    ui_language = Column(String(10), default='en')              # Summary/Q&A language
    transcription_method = Column(String(50), nullable=True)    # Method used
```

#### ChatHistory Model

```python
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, index=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Multi-language field (NEW in v2.0)
    language = Column(String(10), default='en')  # Language of Q&A interaction
```

---

## 7. Frontend Architecture

### 7.1 Main Application (script.js)

#### VideoAnalyzer Class

**Purpose**: Main application controller

**Structure**:
```javascript
class VideoAnalyzer {
    constructor() {
        this.initializeLanguageManager();    // Setup i18n
        this.initializeEventListeners();     // Setup event handlers
        this.setupDragAndDrop();             // Enable drag & drop upload
        this.setupSuggestionChips();         // Quick action buttons
    }

    // Language management
    async initializeLanguageManager()

    // File handling
    async handleFileSelect(file)
    async pollProcessingStatus(videoId)

    // Q&A
    async askQuestion()
    async askPredefinedQuestion(question)

    // UI updates
    displayVideoInfo(data)
    showChatSection()
    addMessageToChat(message, type)

    // Utilities
    formatMarkdown(text)
    escapeHtml(text)
    showLoading(show, message)
    showError(message)
    showSuccess(message)
    clearChat()
}
```

#### Key Methods

##### Language Initialization
```javascript
async initializeLanguageManager() {
    // Load supported languages from API
    await i18n.loadSupportedLanguages();

    // Set initial values from LocalStorage
    const savedUILang = i18n.getUILanguage();
    document.getElementById('uiLanguageSelect').value = savedUILang;
    i18n.updateUI();

    const savedVideoLang = i18n.getVideoLanguage();
    document.getElementById('videoLanguageSelect').value = savedVideoLang;

    // Setup change listeners
    document.getElementById('uiLanguageSelect').addEventListener('change', (e) => {
        i18n.setUILanguage(e.target.value);
    });

    document.getElementById('videoLanguageSelect').addEventListener('change', (e) => {
        i18n.setVideoLanguage(e.target.value);
    });
}
```

##### File Upload with Language
```javascript
async handleFileSelect(file) {
    // Get selected languages
    const videoLanguage = i18n.getVideoLanguage();  // 'auto', 'en', or 'ja'
    const uiLanguage = i18n.getUILanguage();        // 'en' or 'ja'

    // Add language parameters to URL
    const url = new URL(`${API_BASE_URL}/upload-video/`);
    url.searchParams.append('language', videoLanguage);
    url.searchParams.append('ui_language', uiLanguage);

    // Upload with language params
    const response = await fetch(url.toString(), {
        method: 'POST',
        body: formData
    });

    // Start polling
    await this.pollProcessingStatus(currentVideoId);
}
```

##### Status Polling
```javascript
async pollProcessingStatus(videoId) {
    const maxAttempts = 60;  // 10 minutes max
    let attempts = 0;

    const poll = async () => {
        const response = await fetch(`${API_BASE_URL}/video-status/${videoId}`);
        const data = await response.json();

        if (data.processing_status === 'completed') {
            this.displayVideoInfo(data);
            this.showChatSection();
            return;
        } else if (data.processing_status === 'failed') {
            this.showError(data.error_message);
            return;
        } else {
            // Continue polling
            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(poll, 5000);  // Poll every 5 seconds
            }
        }
    };

    poll();
}
```

##### Q&A with Language
```javascript
async askQuestion() {
    const question = document.getElementById('questionInput').value.trim();

    // Add UI language parameter
    const url = new URL(`${API_BASE_URL}/ask-question/`);
    url.searchParams.append('ui_language', i18n.getUILanguage());

    const response = await fetch(url.toString(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            video_id: currentVideoId,
            question: question
        })
    });

    const data = await response.json();
    this.addMessageToChat(data.answer, 'ai');
}
```

### 7.2 Translation System (translations.js)

#### LanguageManager Class

```javascript
class LanguageManager {
    constructor() {
        this.currentUILanguage = localStorage.getItem('uiLanguage') || 'en';
        this.currentVideoLanguage = localStorage.getItem('videoLanguage') || 'auto';
        this.supportedLanguages = null;
    }

    async loadSupportedLanguages() {
        const response = await fetch(`${API_BASE_URL}/supported-languages/`);
        const data = await response.json();
        this.supportedLanguages = data.languages;
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

    t(key) {
        return translations[this.currentUILanguage]?.[key]
            || translations['en'][key]
            || key;
    }

    updateUI() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);

            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        });

        document.title = this.t('appTitle');
    }

    getLanguageDisplay(langCode) {
        if (this.supportedLanguages && this.supportedLanguages[langCode]) {
            const lang = this.supportedLanguages[langCode];
            return `${lang.flag} ${lang.native_name}`;
        }
        return langCode;
    }
}

// Global instance
const i18n = new LanguageManager();
```

---

## 8. Database Schema

### Schema Diagram

```sql
┌─────────────────────────────────────────────────────────────────┐
│                           videos                                 │
├─────────────────────────────────────────────────────────────────┤
│ id                      INTEGER PRIMARY KEY                      │
│ filename                VARCHAR(255) INDEX                       │
│ file_path               VARCHAR(512)                             │
│ transcription           TEXT                                     │
│ summary                 TEXT                                     │
│ processing_status       VARCHAR(50) DEFAULT 'pending'           │
│ error_message           TEXT                                     │
│ uploaded_at             DATETIME DEFAULT CURRENT_TIMESTAMP       │
│ processed_at            DATETIME                                 │
│ detected_language       VARCHAR(10)        -- NEW v2.0          │
│ user_selected_language  VARCHAR(10)        -- NEW v2.0          │
│ ui_language             VARCHAR(10) DEFAULT 'en'  -- NEW v2.0   │
│ transcription_method    VARCHAR(50)        -- NEW v2.0          │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ 1:N
                                  │
┌─────────────────────────────────▼───────────────────────────────┐
│                         chat_history                             │
├─────────────────────────────────────────────────────────────────┤
│ id                      INTEGER PRIMARY KEY                      │
│ video_id                INTEGER INDEX (FK → videos.id)          │
│ question                TEXT                                     │
│ answer                  TEXT                                     │
│ timestamp               DATETIME DEFAULT CURRENT_TIMESTAMP       │
│ language                VARCHAR(10) DEFAULT 'en'  -- NEW v2.0   │
└─────────────────────────────────────────────────────────────────┘
```

### Field Descriptions

#### videos Table

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | INTEGER | NO | Primary key, auto-increment |
| `filename` | VARCHAR(255) | NO | Original filename of uploaded video |
| `file_path` | VARCHAR(512) | NO | Server path to stored video file |
| `transcription` | TEXT | YES | Full transcription of video audio |
| `summary` | TEXT | YES | AI-generated summary |
| `processing_status` | VARCHAR(50) | NO | Status: 'pending', 'processing', 'completed', 'failed' |
| `error_message` | TEXT | YES | Error details if processing failed |
| `uploaded_at` | DATETIME | NO | Timestamp when video was uploaded |
| `processed_at` | DATETIME | YES | Timestamp when processing completed |
| `detected_language` | VARCHAR(10) | YES | Auto-detected language code (en, ja) |
| `user_selected_language` | VARCHAR(10) | YES | User-specified language override |
| `ui_language` | VARCHAR(10) | NO | Language for summary/Q&A (default: 'en') |
| `transcription_method` | VARCHAR(50) | YES | Method used: 'azure_speech', 'azure_whisper', 'local_whisper' |

#### chat_history Table

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | INTEGER | NO | Primary key, auto-increment |
| `video_id` | INTEGER | NO | Foreign key to videos table |
| `question` | TEXT | NO | User's question |
| `answer` | TEXT | NO | AI-generated answer |
| `timestamp` | DATETIME | NO | When question was asked |
| `language` | VARCHAR(10) | NO | Language of Q&A interaction (default: 'en') |

### Indexes

```sql
-- Existing indexes
CREATE INDEX idx_videos_filename ON videos(filename);
CREATE INDEX idx_chat_history_video_id ON chat_history(video_id);

-- Recommended indexes (from performance optimization plan)
CREATE INDEX idx_videos_processing_status ON videos(processing_status);
CREATE INDEX idx_videos_uploaded_at ON videos(uploaded_at);
CREATE INDEX idx_videos_processed_at ON videos(processed_at);
CREATE INDEX idx_videos_detected_language ON videos(detected_language);
CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp);
CREATE INDEX idx_chat_history_language ON chat_history(language);
```

### Database Migrations

#### Migration Script

**File**: `/backend/migrate_db_multilang.py`

**Purpose**: Add multi-language fields to existing database

**Usage**:
```bash
python3 migrate_db_multilang.py
```

**What it does**:
1. Checks if new columns exist
2. Adds missing columns with defaults
3. Preserves existing data
4. Verifies migration success

**Output**:
```
======================================================================
DATABASE MIGRATION: Multi-Language Support
======================================================================

📊 Migrating 'videos' table...
  ✅ Added column: detected_language
  ✅ Added column: user_selected_language
  ✅ Added column: ui_language (default: 'en')
  ✅ Added column: transcription_method

💬 Migrating 'chat_history' table...
  ✅ Added column: language (default: 'en')

✅ DATABASE MIGRATION COMPLETED SUCCESSFULLY!
```

---

## 9. API Endpoints

### Endpoint Summary

| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| GET | `/` | Health check | No |
| GET | `/supported-languages/` | Get supported languages | No |
| POST | `/upload-video/` | Upload video file | No |
| POST | `/ask-question/` | Ask question about video | No |
| GET | `/videos/` | List all videos | No |
| GET | `/video/{video_id}` | Get video details | No |
| GET | `/video-status/{video_id}` | Check processing status | No |
| GET | `/chat-history/{video_id}` | Get Q&A history | No |

---

### Detailed Endpoint Documentation

#### GET `/`

**Purpose**: Health check and API information

**Request**: None

**Response**:
```json
{
    "message": "Video Analyzer API is running",
    "multi_language_support": true,
    "supported_languages": ["en", "ja"]
}
```

---

#### GET `/supported-languages/`

**Purpose**: Get list of supported languages with metadata

**Request**: None

**Response**:
```json
{
    "languages": {
        "en": {
            "name": "English",
            "native_name": "English",
            "azure_code": "en-US",
            "whisper_code": "en",
            "flag": "🇺🇸",
            "enabled": true
        },
        "ja": {
            "name": "Japanese",
            "native_name": "日本語",
            "azure_code": "ja-JP",
            "whisper_code": "ja",
            "flag": "🇯🇵",
            "enabled": true
        }
    },
    "default": "en"
}
```

---

#### POST `/upload-video/`

**Purpose**: Upload video file for processing

**Query Parameters**:
- `language` (optional): Video language ('en', 'ja', 'auto'). Default: None (auto-detect)
- `ui_language` (optional): UI response language ('en', 'ja'). Default: 'en'

**Request**:
```
Content-Type: multipart/form-data

file: <video file>
```

**Example**:
```bash
curl -X POST "http://localhost:8000/upload-video/?language=ja&ui_language=en" \
  -F "file=@video.mp4"
```

**Response**:
```json
{
    "message": "Video uploaded successfully. Processing started in background.",
    "video_id": 1,
    "filename": "video.mp4",
    "processing_status": "pending",
    "language": "ja",
    "ui_language": "en"
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid file type
- `500`: Server error

---

#### GET `/video-status/{video_id}`

**Purpose**: Check processing status of a video

**Path Parameters**:
- `video_id`: Integer, ID of the video

**Response** (Processing):
```json
{
    "video_id": 1,
    "filename": "video.mp4",
    "processing_status": "processing",
    "error_message": null,
    "detected_language": null,
    "ui_language": "en",
    "transcription_method": null,
    "transcription": null,
    "summary": null
}
```

**Response** (Completed):
```json
{
    "video_id": 1,
    "filename": "video.mp4",
    "processing_status": "completed",
    "error_message": null,
    "detected_language": "ja",
    "ui_language": "en",
    "transcription_method": "azure_speech",
    "transcription": "Full transcription text...",
    "summary": "Video summary in English..."
}
```

**Status Codes**:
- `200`: Success
- `404`: Video not found

---

#### POST `/ask-question/`

**Purpose**: Ask a question about a video

**Query Parameters**:
- `ui_language` (optional): Response language ('en', 'ja'). Default: video's ui_language

**Request Body**:
```json
{
    "video_id": 1,
    "question": "What is the main topic of this video?"
}
```

**Example**:
```bash
curl -X POST "http://localhost:8000/ask-question/?ui_language=ja" \
  -H "Content-Type: application/json" \
  -d '{"video_id": 1, "question": "このビデオの主なトピックは何ですか？"}'
```

**Response**:
```json
{
    "question": "このビデオの主なトピックは何ですか？",
    "answer": "このビデオの主なトピックは...",
    "video_id": 1,
    "language": "ja"
}
```

**Status Codes**:
- `200`: Success
- `404`: Video not found
- `500`: Failed to generate answer

---

#### GET `/videos/`

**Purpose**: Get list of all uploaded videos

**Response**:
```json
[
    {
        "id": 1,
        "filename": "video.mp4",
        "summary": "Brief summary of the video content...",
        "uploaded_at": "2024-11-05T10:30:00",
        "detected_language": "ja",
        "ui_language": "en",
        "processing_status": "completed"
    },
    {
        "id": 2,
        "filename": "another_video.mp4",
        "summary": "Another video summary...",
        "uploaded_at": "2024-11-05T11:00:00",
        "detected_language": "en",
        "ui_language": "en",
        "processing_status": "completed"
    }
]
```

---

#### GET `/video/{video_id}`

**Purpose**: Get detailed information about a specific video

**Path Parameters**:
- `video_id`: Integer, ID of the video

**Response**:
```json
{
    "id": 1,
    "filename": "video.mp4",
    "transcription": "Full transcription of the video...",
    "summary": "Detailed summary...",
    "processing_status": "completed",
    "error_message": null,
    "uploaded_at": "2024-11-05T10:30:00",
    "processed_at": "2024-11-05T10:35:00",
    "detected_language": "ja",
    "user_selected_language": null,
    "ui_language": "en",
    "transcription_method": "azure_speech"
}
```

**Status Codes**:
- `200`: Success
- `404`: Video not found

---

#### GET `/chat-history/{video_id}`

**Purpose**: Get all Q&A interactions for a video

**Path Parameters**:
- `video_id`: Integer, ID of the video

**Response**:
```json
[
    {
        "question": "What is this video about?",
        "answer": "This video is about...",
        "timestamp": "2024-11-05T10:40:00",
        "language": "en"
    },
    {
        "question": "このビデオの長さは？",
        "answer": "このビデオは約5分間です。",
        "timestamp": "2024-11-05T10:42:00",
        "language": "ja"
    }
]
```

**Status Codes**:
- `200`: Success (empty array if no history)

---

## 10. Video Processing Pipeline

### Pipeline Overview

```
┌──────────────┐
│ Video Upload │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Save to Database │  Status: "pending"
│ (video entry)    │
└──────┬───────────┘
       │
       ▼
┌─────────────────────┐
│ Background Task     │  Status: "processing"
│ Starts              │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Step 1:             │
│ Extract Audio       │  15-60 seconds
│ (moviepy/FFmpeg)    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Step 2:             │
│ Detect Language     │  5-10 seconds
│ (Azure Speech)      │  OR use user selection
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Step 3:             │
│ Transcribe Audio    │  60-180 seconds
│ (3-tier fallback)   │
│                     │
│ Try Azure Speech    │ ───► Success? ─┐
│ ↓ Failed            │                │
│ Try Azure Whisper   │ ───► Success? ─┤
│ ↓ Failed            │                │
│ Try Local Whisper   │ ───► Success? ─┤
│                     │                │
└──────┬──────────────┘                │
       │◄───────────────────────────────┘
       ▼
┌─────────────────────┐
│ Step 4:             │
│ Generate Summary    │  10-20 seconds
│ (GPT-4)             │  In UI language
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Step 5:             │
│ Cleanup & Save      │
│ - Remove temp audio │
│ - Update database   │  Status: "completed"
│ - Set timestamps    │
└──────┬──────────────┘
       │
       ▼
┌──────────────────┐
│ Ready for Q&A    │
└──────────────────┘
```

### Detailed Step Descriptions

#### Step 1: Audio Extraction

**Purpose**: Extract audio track from video file

**Method**: `extract_audio_from_video(video_path)`

**Process**:
1. Load video file with moviepy
2. Extract audio track
3. Convert to WAV format (16kHz, mono, 16-bit PCM)
4. Save to temporary file

**Output**: WAV file at `./uploads/video_name.wav`

**Performance**:
- Current: 30-60 seconds for 5-minute video
- Optimized (FFmpeg): 6-12 seconds

**Code**:
```python
def extract_audio_from_video(self, video_path: str) -> str:
    video = VideoFileClip(video_path)
    audio_path = video_path.rsplit('.', 1)[0] + '.wav'

    video.audio.write_audiofile(
        audio_path,
        fps=16000,      # 16kHz sample rate
        nbytes=2,       # 16-bit audio
        codec='pcm_s16le',
        verbose=False,
        logger=None,
        bitrate='64k'
    )
    video.close()
    return audio_path
```

---

#### Step 2: Language Detection

**Purpose**: Automatically detect spoken language

**Method**: `detect_language(audio_path)`

**Process**:
1. Initialize Azure Speech SDK
2. Configure auto-detection for en-US and ja-JP
3. Analyze first portion of audio
4. Extract detected language code
5. Convert to ISO 639-1 format

**Output**: Language code ('en' or 'ja')

**Fallback**: If detection fails, defaults to 'en'

**Performance**: 5-10 seconds

**Note**: Skipped if user selects specific language

---

#### Step 3: Transcription (3-Tier Fallback)

**Purpose**: Convert speech to text

**Method**: `transcribe_audio(audio_path, language)`

**Tier 1: Azure Speech Services** (Primary)
- **Pros**: Fastest, most accurate, supports continuous recognition
- **Cons**: Requires Azure subscription
- **Process**:
  ```python
  speech_config.speech_recognition_language = get_azure_language_code(language)
  recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)
  recognizer.start_continuous_recognition()
  # Collect all recognized text
  ```

**Tier 2: Azure Whisper** (Fallback #1)
- **Pros**: Good accuracy, cloud-based
- **Cons**: Slower than Azure Speech
- **Process**:
  ```python
  transcript = client.audio.transcriptions.create(
      model="whisper-1",
      file=audio_file,
      language=get_whisper_language_code(language)
  )
  ```

**Tier 3: Local Whisper** (Fallback #2)
- **Pros**: Works offline, no API limits
- **Cons**: Slowest, resource-intensive
- **Process**:
  ```python
  model = whisper.load_model("base")
  result = model.transcribe(audio_path, language=language)
  ```

**Output**: Tuple of `(transcription_text, method_used)`

**Performance**: 60-180 seconds depending on video length and method

---

#### Step 4: Summary Generation

**Purpose**: Create concise summary of video content

**Method**: `generate_summary(transcription, language)`

**Process**:
1. Determine target language (UI language)
2. Create language-specific system prompt
3. Send transcription to GPT-4
4. Receive summary in target language

**Prompt Template**:
```
System: You are an AI assistant that creates concise summaries of video transcriptions.
Provide a clear, informative summary in {language} language that captures the main points
and key information. Respond ONLY in {language}.

User: Please summarize this video transcription:
{transcription}
```

**Parameters**:
- Model: gpt-4o
- Max tokens: 500
- Temperature: Default (0.7)

**Output**: Summary text in specified UI language

**Performance**: 10-20 seconds

---

#### Step 5: Cleanup & Database Update

**Purpose**: Finalize processing and update database

**Process**:
1. Delete temporary audio file
2. Update video record in database:
   - Set `transcription`
   - Set `summary`
   - Set `detected_language`
   - Set `transcription_method`
   - Set `processing_status = "completed"`
   - Set `processed_at = current_timestamp`

**Error Handling**:
If any step fails:
1. Set `processing_status = "failed"`
2. Store error message in `error_message` field
3. Still clean up temporary files

---

### Error Handling in Pipeline

```python
try:
    # Processing steps
    audio_path = extract_audio_from_video(video_path)
    detected_language = detect_language(audio_path)
    transcription, method = transcribe_audio(audio_path, detected_language)
    summary = generate_summary(transcription, ui_language)

    # Success - update database
    video.processing_status = "completed"
    video.transcription = transcription
    video.summary = summary
    # ... etc

except Exception as e:
    # Failure - record error
    video.processing_status = "failed"
    video.error_message = str(e)

finally:
    # Always cleanup
    if os.path.exists(audio_path):
        os.remove(audio_path)
    db.commit()
```

---

## 11. File Structure

```
grassroot_video_analyser_v3/
│
├── backend/
│   ├── main.py                          # FastAPI application entry point
│   ├── models.py                        # SQLAlchemy database models
│   ├── video_processor.py               # Video processing logic
│   ├── language_config.py               # Language configuration & mappings
│   ├── migrate_db_multilang.py          # Database migration script
│   ├── requirements.txt                 # Python dependencies
│   ├── .env                             # Environment variables (not in git)
│   ├── video_analyzer.db                # SQLite database file
│   └── uploads/                         # Uploaded video files directory
│       ├── video1.mp4
│       ├── video1.wav                   # Temporary audio files (auto-deleted)
│       └── ...
│
├── frontend/
│   ├── index.html                       # Main HTML file
│   ├── script.js                        # Application JavaScript
│   ├── translations.js                  # Multi-language translation system
│   └── (no CSS file - styles in HTML)
│
├── PROJECT_DOCUMENTATION.md             # Original project documentation
├── MULTI_LANGUAGE_IMPLEMENTATION_PLAN.md # Multi-language implementation plan
├── IMPLEMENTATION_SUMMARY.md            # Summary of multi-language changes
├── COMPLETE_PROJECT_DOCUMENTATION.md    # This file - comprehensive guide
├── TESTING_GUIDE.md                     # Testing instructions
│
└── README.md                            # Project README
```

### Key File Descriptions

#### Backend Files

**main.py** (280 lines)
- FastAPI application setup
- All REST API endpoints
- Background task management
- CORS configuration
- Request/response models

**video_processor.py** (374 lines)
- VideoProcessor class
- Audio extraction
- Language detection
- Three-tier transcription fallback
- AI summary generation
- Q&A processing
- Main processing pipeline

**models.py** (58 lines)
- Video model (with multi-language fields)
- ChatHistory model (with language field)
- Database session management
- Table creation

**language_config.py** (92 lines)
- SUPPORTED_LANGUAGES dictionary
- Language code conversion functions
- Azure/Whisper format mappings
- Enabled languages management

**migrate_db_multilang.py** (110 lines)
- Database migration utility
- Adds multi-language columns
- Idempotent (safe to run multiple times)
- Verification logic

#### Frontend Files

**index.html** (551 lines)
- HTML structure
- Embedded CSS (470 lines)
- Language selector components
- Upload interface
- Video info display
- Chat interface
- Script includes

**script.js** (439 lines)
- VideoAnalyzer class
- Event handling
- API communication
- Status polling
- Q&A functionality
- UI updates
- Markdown formatting

**translations.js** (228 lines)
- Translation dictionaries (en, ja)
- LanguageManager class
- LocalStorage management
- UI update logic
- Language display utilities

#### Documentation Files

**PROJECT_DOCUMENTATION.md**
- Original project documentation
- Basic feature descriptions
- Initial architecture notes

**MULTI_LANGUAGE_IMPLEMENTATION_PLAN.md**
- 8-phase implementation plan
- Detailed code examples
- Testing strategies
- Timeline estimates

**IMPLEMENTATION_SUMMARY.md**
- Summary of completed work
- Code changes made
- API usage examples
- Success metrics

**COMPLETE_PROJECT_DOCUMENTATION.md** (This file)
- Comprehensive technical guide
- Architecture deep-dive
- Code explanations
- Setup instructions
- Troubleshooting guide

---

## 12. Configuration

### Environment Variables (.env)

```bash
# ============================================
# OPENAI / RAKUTEN AI GATEWAY
# ============================================
OPENAI_API_KEY=raik-sk-xxxxx...
OPENAI_BASE_URL=https://api.ai.public.rakuten-it.com/openai/v1
LLM_MODEL=gpt-4o

# ============================================
# DATABASE
# ============================================
DATABASE_URL=sqlite:///./video_analyzer.db
UPLOAD_DIR=./uploads

# ============================================
# AZURE SPEECH SERVICES
# ============================================
AZURE_SPEACH_KEY=xxxxx...        # Note: typo in variable name
AZURE_REGION=eastus
AZURE_COGNITIVE_SERVICE_KEY=xxxxx...
AZURE_COGNITIVE_SERVICE_ENDPOINT=https://eastus.api.cognitive.microsoft.com/

# ============================================
# AZURE WHISPER (Fallback Transcription)
# ============================================
WHISPER_AZURE_ENDPOINT=https://xxxxx.cognitiveservices.azure.com
WHISPER_DEPLOYMENT_NAME=whisper
WHISPER_API_KEY=xxxxx...

# ============================================
# MULTI-LANGUAGE CONFIGURATION
# ============================================
# Default language for UI and responses
DEFAULT_UI_LANGUAGE=en

# Default video language (auto = auto-detect, en = English, ja = Japanese)
DEFAULT_VIDEO_LANGUAGE=auto

# Enable automatic language detection (requires Azure Speech Services)
ENABLE_AUTO_LANGUAGE_DETECTION=true

# Supported languages (comma-separated ISO 639-1 codes)
SUPPORTED_LANGUAGES=en,ja

# Maximum audio duration for language detection (seconds)
MAX_DETECTION_AUDIO_DURATION=30
```

### Configuration Best Practices

1. **Never commit .env to version control**
   - Add `.env` to `.gitignore`
   - Use `.env.example` for template

2. **API Key Rotation**
   - Rotate keys regularly
   - Use different keys for dev/prod

3. **Database Configuration**
   - Use PostgreSQL/MySQL in production (not SQLite)
   - Configure connection pooling
   - Set up regular backups

4. **Upload Directory**
   - Ensure sufficient disk space
   - Implement cleanup policy for old videos
   - Consider cloud storage (S3, Azure Blob)

---

## 13. Setup & Installation

### Prerequisites

- Python 3.9+
- pip (Python package manager)
- FFmpeg (optional, for faster audio extraction)
- Azure Speech Services subscription
- Rakuten AI Gateway access (or OpenAI API key)

### Backend Setup

#### 1. Clone Repository
```bash
cd /path/to/project
cd grassroot_video_analyser_v3
```

#### 2. Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

**requirements.txt**:
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
python-decouple==3.8
openai==1.3.7+
moviepy==1.0.3
azure-cognitiveservices-speech==1.32.1
python-multipart==0.0.6
```

#### 4. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit with your credentials
nano .env
```

Required variables:
- `OPENAI_API_KEY` or `RAKUTEN_AI_GATEWAY_KEY`
- `OPENAI_BASE_URL`
- `AZURE_SPEACH_KEY`
- `AZURE_REGION`

#### 5. Initialize Database
```bash
# Run migration to create/update tables
python3 migrate_db_multilang.py
```

Output:
```
✅ DATABASE MIGRATION COMPLETED SUCCESSFULLY!
```

#### 6. Create Upload Directory
```bash
mkdir -p uploads
chmod 755 uploads
```

#### 7. Start Backend Server
```bash
python3 main.py
```

Output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd ../frontend
```

#### 2. Start HTTP Server

**Option A: Python HTTP Server**
```bash
python3 -m http.server 8080
```

**Option B: Node.js http-server**
```bash
npm install -g http-server
http-server -p 8080
```

**Option C: PHP Built-in Server**
```bash
php -S localhost:8080
```

#### 3. Access Application
```
Open browser: http://localhost:8080
```

### Installation Verification

#### 1. Check Backend Health
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
    "message": "Video Analyzer API is running",
    "multi_language_support": true,
    "supported_languages": ["en", "ja"]
}
```

#### 2. Check Supported Languages
```bash
curl http://localhost:8000/supported-languages/
```

#### 3. Test Frontend
- Open http://localhost:8080
- Verify language selectors appear
- Try switching UI language
- Check browser console for errors

### Common Installation Issues

#### Issue: ModuleNotFoundError for azure.cognitiveservices.speech

**Solution**:
```bash
pip install azure-cognitiveservices-speech==1.32.1
```

#### Issue: FFmpeg not found

**Solution**:
- macOS: `brew install ffmpeg`
- Ubuntu: `apt-get install ffmpeg`
- Windows: Download from https://ffmpeg.org/

#### Issue: CORS errors in browser

**Solution**: Ensure backend is running and CORS is configured correctly in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue: Database not found

**Solution**: Run migration script:
```bash
python3 migrate_db_multilang.py
```

---

## 14. Performance Considerations

### Current Performance Metrics

**Video Processing** (5-minute video):
- Upload: 10-15 seconds
- Audio extraction: 30-60 seconds (moviepy)
- Language detection: 5-10 seconds
- Transcription: 60-180 seconds (depends on method)
- Summary: 10-20 seconds
- **Total**: 115-285 seconds (2-5 minutes)

**Frontend**:
- Status polling: Every 5 seconds (120+ requests for 10-min job)
- Q&A response: 5-10 seconds
- Video list load: 500ms-2s (100 videos)

### Identified Bottlenecks

#### Backend Bottlenecks
1. **Sequential Processing**: Each step waits for previous to complete
2. **moviepy Audio Extraction**: Slow and memory-intensive
3. **No Model Caching**: Whisper model loaded every time
4. **No Request Caching**: Same data fetched repeatedly

#### Frontend Bottlenecks
1. **Fixed Polling Interval**: Wastes bandwidth
2. **No Response Caching**: Status data re-fetched constantly
3. **No Virtualization**: Chat slows with 20+ messages

#### Database Bottlenecks
1. **Missing Indexes**: Slow queries on status, date fields
2. **Full Objects Returned**: Unnecessary data transfer

### Optimization Recommendations

See detailed performance optimization plan in conversation above. Quick wins include:

1. **Add Database Indexes** (Easy, High Impact)
   - 70-90% faster queries
   - 1-2 hours to implement

2. **Cache Whisper Model** (Easy, High Impact)
   - Save 5-10 seconds per transcription
   - 1-2 hours to implement

3. **Exponential Backoff Polling** (Easy, High Impact)
   - 85% fewer requests
   - 2-3 hours to implement

4. **Replace moviepy with FFmpeg** (Easy, Very High Impact)
   - 5-10x faster audio extraction
   - 3-4 hours to implement

5. **Implement Response Caching** (Medium, High Impact)
   - 90%+ faster repeated queries
   - 1-2 days to implement

### Scalability Considerations

#### Current Limitations
- SQLite not suitable for high concurrency
- Background tasks run in-process
- No horizontal scaling
- No load balancing

#### Production Recommendations
1. **Database**: Migrate to PostgreSQL or MySQL
2. **Task Queue**: Use Celery or RQ for background jobs
3. **Caching**: Implement Redis for response caching
4. **Storage**: Move uploads to S3 or Azure Blob
5. **Scaling**: Deploy with Kubernetes or Docker Swarm
6. **Monitoring**: Add Prometheus + Grafana
7. **Load Balancing**: Nginx or AWS ALB

---

## 15. Troubleshooting

### Common Issues & Solutions

#### Issue: Video Upload Fails

**Symptoms**:
- "Failed to upload video" error
- 400 Bad Request

**Possible Causes**:
1. File type not supported
2. File too large
3. Upload directory doesn't exist or not writable

**Solutions**:
```bash
# Check if uploads directory exists
ls -la backend/uploads/

# Create if missing
mkdir -p backend/uploads/
chmod 755 backend/uploads/

# Check file type on client side
# Ensure file.type.startsWith('video/')
```

---

#### Issue: Processing Stuck at "Processing..."

**Symptoms**:
- Status remains "processing" indefinitely
- No error message

**Possible Causes**:
1. Background task crashed
2. Transcription service unavailable
3. Audio extraction failed

**Debug Steps**:
```bash
# Check backend logs
tail -f backend/logs/app.log  # If logging enabled

# Check database status
sqlite3 backend/video_analyzer.db
SELECT id, filename, processing_status, error_message
FROM videos
WHERE processing_status = 'processing';

# Manually check video file
ls -lh backend/uploads/
```

**Solutions**:
1. Restart backend server
2. Check API credentials in `.env`
3. Verify audio file was created
4. Manually set status to 'failed' and retry

---

#### Issue: Transcription Returns Empty

**Symptoms**:
- Processing completes but transcription is empty
- No audio detected

**Possible Causes**:
1. Video has no audio track
2. Audio too quiet
3. Unsupported audio codec

**Debug Steps**:
```bash
# Check if audio file was created
ls backend/uploads/*.wav

# Test audio file manually
ffmpeg -i backend/uploads/video.wav -af "volumedetect" -f null /dev/null

# Test Azure Speech credentials
curl -X POST "https://${AZURE_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-US" \
  -H "Ocp-Apim-Subscription-Key: ${AZURE_SPEACH_KEY}" \
  -H "Content-Type: audio/wav" \
  --data-binary @backend/uploads/video.wav
```

**Solutions**:
1. Verify video has audio: `ffprobe video.mp4`
2. Increase audio volume in extraction
3. Try different transcription method

---

#### Issue: Language Detection Always Returns English

**Symptoms**:
- Japanese videos detected as English
- `detected_language` always "en"

**Possible Causes**:
1. Azure Speech credentials incorrect
2. Auto-detection disabled
3. Audio sample too short

**Debug Steps**:
```bash
# Verify environment variables
echo $AZURE_SPEACH_KEY
echo $AZURE_REGION
echo $ENABLE_AUTO_LANGUAGE_DETECTION

# Test Azure Speech connection
python3 -c "
import azure.cognitiveservices.speech as speechsdk
from decouple import config

speech_config = speechsdk.SpeechConfig(
    subscription=config('AZURE_SPEACH_KEY'),
    region=config('AZURE_REGION')
)
print('Connection OK')
"
```

**Solutions**:
1. Verify API keys are correct
2. Check `ENABLE_AUTO_LANGUAGE_DETECTION=true` in `.env`
3. Ensure video has clear speech in first 15 seconds
4. Manually specify language instead of auto-detect

---

#### Issue: UI Not Updating When Language Changed

**Symptoms**:
- Selecting language does nothing
- Text remains in English

**Possible Causes**:
1. `translations.js` not loaded
2. JavaScript errors preventing execution
3. `data-i18n` attributes missing

**Debug Steps**:
```javascript
// Open browser console (F12)
console.log(i18n);  // Should show LanguageManager instance
console.log(i18n.currentUILanguage);  // Should show current language

// Check if translations loaded
console.log(translations);

// Test translation
console.log(i18n.t('appTitle'));  // Should return translated text
```

**Solutions**:
1. Ensure `<script src="translations.js"></script>` comes before `script.js`
2. Check browser console for errors
3. Clear browser cache and reload
4. Verify `data-i18n` attributes on elements

---

#### Issue: Q&A Not Working

**Symptoms**:
- Questions don't get answers
- Error: "Failed to answer question"

**Possible Causes**:
1. OpenAI API key invalid
2. Video not fully processed
3. Transcription empty

**Debug Steps**:
```bash
# Check video status
curl http://localhost:8000/video-status/1

# Verify transcription exists and is not empty
sqlite3 backend/video_analyzer.db
SELECT id, LENGTH(transcription), processing_status
FROM videos
WHERE id = 1;

# Test OpenAI connection
curl https://api.ai.public.rakuten-it.com/openai/v1/models \
  -H "Authorization: Bearer ${OPENAI_API_KEY}"
```

**Solutions**:
1. Wait for processing to complete
2. Verify API key in `.env`
3. Check API rate limits
4. Retry upload if transcription is empty

---

#### Issue: Frontend Can't Connect to Backend

**Symptoms**:
- "Failed to fetch" errors
- Network errors in console

**Possible Causes**:
1. Backend not running
2. CORS issues
3. Wrong API URL

**Debug Steps**:
```bash
# Check if backend is running
curl http://localhost:8000/

# Check API_BASE_URL in script.js
grep "API_BASE_URL" frontend/script.js

# Check browser console for CORS errors
```

**Solutions**:
1. Start backend: `python3 main.py`
2. Verify `API_BASE_URL = 'http://localhost:8000'` in `script.js`
3. Check CORS configuration in `main.py`
4. Ensure no firewall blocking port 8000

---

### Debug Mode

Enable verbose logging:

**Backend** (`main.py`):
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

**Frontend** (`script.js`):
```javascript
// Add to VideoAnalyzer constructor
this.debug = true;

// In methods, add:
if (this.debug) {
    console.log('Debug:', data);
}
```

---

## 16. Future Enhancements

### Planned Features

#### Short-Term (1-3 months)

1. **Performance Optimizations** ⭐ High Priority
   - Replace moviepy with FFmpeg
   - Cache Whisper model
   - Implement exponential backoff polling
   - Add database indexes
   - Target: 40-50% performance improvement

2. **Additional Languages**
   - Spanish (es)
   - French (fr)
   - German (de)
   - Chinese (zh)
   - Korean (ko)

3. **Video Timestamps**
   - Link transcription segments to timestamps
   - Click-to-play functionality
   - Timeline navigation

4. **Export Functionality**
   - Export transcription (TXT, SRT, VTT)
   - Export Q&A history (PDF, MD)
   - Export summary (DOCX)

#### Mid-Term (3-6 months)

1. **WebSocket Real-Time Updates** ⭐ High Priority
   - Eliminate polling
   - Instant status updates
   - Progress indicators

2. **Semantic Search with Vector Database** ⭐ High Priority
   - ChromaDB integration
   - Embedding-based search
   - 90%+ better Q&A accuracy

3. **User Authentication**
   - User accounts
   - Private video libraries
   - Access control

4. **Batch Processing**
   - Upload multiple videos
   - Queue management
   - Bulk operations

5. **Advanced Summarization**
   - Configurable summary length
   - Multiple summary styles
   - Chapter generation

#### Long-Term (6-12 months)

1. **Video Editing Integration**
   - Cut/trim based on transcription
   - Remove silence
   - Highlight key moments

2. **Collaboration Features**
   - Shared videos
   - Comments/annotations
   - Team workspaces

3. **Mobile Applications**
   - iOS app
   - Android app
   - Mobile-optimized web

4. **Advanced Analytics**
   - Content insights
   - Speech pattern analysis
   - Sentiment analysis

5. **API Access**
   - Public API
   - SDKs (Python, JavaScript)
   - Webhooks

### Architecture Improvements

1. **Microservices Architecture**
   - Separate transcription service
   - Separate AI/LLM service
   - API gateway

2. **Cloud-Native Deployment**
   - Kubernetes orchestration
   - Auto-scaling
   - Multi-region support

3. **Enhanced Security**
   - End-to-end encryption
   - Video watermarking
   - Audit logs

4. **Monitoring & Observability**
   - Prometheus metrics
   - Grafana dashboards
   - Sentry error tracking
   - Request tracing

### Research Areas

1. **Custom Speech Models**
   - Fine-tuned Whisper models
   - Domain-specific vocabulary
   - Accent adaptation

2. **Real-Time Processing**
   - Live video transcription
   - Streaming Q&A
   - Real-time translation

3. **Multi-Modal Analysis**
   - Visual scene detection
   - Object recognition
   - Face detection
   - Emotion recognition

---

## Appendix A: Code Reference

### Key Code Snippets

#### A.1 Language Detection Implementation

```python
def detect_language(self, audio_path: str) -> str:
    """
    Detect language from audio using Azure Speech Services

    Args:
        audio_path: Path to audio file

    Returns:
        ISO 639-1 language code ('en', 'ja')
    """
    try:
        speech_key = config('AZURE_SPEACH_KEY')
        service_region = config('AZURE_REGION', default='eastus')

        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key,
            region=service_region
        )

        # Configure auto-detect with supported languages
        auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=['en-US', 'ja-JP']
        )

        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)

        # Create recognizer with language detection
        source_language_recognizer = speechsdk.SourceLanguageRecognizer(
            speech_config=speech_config,
            auto_detect_source_language_config=auto_detect_source_language_config,
            audio_config=audio_config
        )

        print("🔍 Detecting language from audio...")
        result = source_language_recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            detected = result.properties[
                speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult
            ]
            # Convert 'en-US' to 'en', 'ja-JP' to 'ja'
            lang_code = detected.split('-')[0] if detected else 'en'
            print(f"✅ Language detected: {lang_code}")
            return lang_code
        else:
            print(f"⚠️ Language detection failed, defaulting to English")
            return 'en'

    except Exception as e:
        print(f"⚠️ Language detection error: {e}, defaulting to English")
        return 'en'
```

#### A.2 Frontend Language Switching

```javascript
setUILanguage(lang) {
    this.currentUILanguage = lang;
    localStorage.setItem('uiLanguage', lang);
    this.updateUI();
    document.documentElement.lang = lang;
}

updateUI() {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = this.t(key);

        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.placeholder = translation;
        } else {
            element.textContent = translation;
        }
    });

    // Update title
    document.title = this.t('appTitle');
}
```

---

## Appendix B: Database Queries

### Useful SQL Queries

#### Get Processing Statistics
```sql
SELECT
    processing_status,
    COUNT(*) as count,
    AVG(CAST((julianday(processed_at) - julianday(uploaded_at)) * 86400 AS INTEGER)) as avg_processing_time_seconds
FROM videos
WHERE processed_at IS NOT NULL
GROUP BY processing_status;
```

#### Get Language Distribution
```sql
SELECT
    detected_language,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM videos), 2) as percentage
FROM videos
WHERE detected_language IS NOT NULL
GROUP BY detected_language
ORDER BY count DESC;
```

#### Get Transcription Method Usage
```sql
SELECT
    transcription_method,
    COUNT(*) as count,
    AVG(CAST((julianday(processed_at) - julianday(uploaded_at)) * 86400 AS INTEGER)) as avg_time_seconds
FROM videos
WHERE transcription_method IS NOT NULL
GROUP BY transcription_method;
```

#### Get Failed Videos with Errors
```sql
SELECT
    id,
    filename,
    uploaded_at,
    error_message
FROM videos
WHERE processing_status = 'failed'
ORDER BY uploaded_at DESC
LIMIT 10;
```

#### Get Q&A Activity by Language
```sql
SELECT
    language,
    COUNT(*) as total_questions,
    COUNT(DISTINCT video_id) as unique_videos
FROM chat_history
GROUP BY language;
```

---

## Appendix C: Testing Checklist

### Manual Testing Checklist

#### Multi-Language Feature Testing

- [ ] **English UI + English Video**
  - [ ] Upload English video
  - [ ] Verify English UI
  - [ ] Check summary in English
  - [ ] Ask question in English, get answer in English

- [ ] **Japanese UI + Japanese Video**
  - [ ] Switch to Japanese UI
  - [ ] Upload Japanese video
  - [ ] Verify Japanese UI
  - [ ] Check summary in Japanese
  - [ ] Ask question in Japanese, get answer in Japanese

- [ ] **English UI + Japanese Video**
  - [ ] Set UI to English
  - [ ] Upload Japanese video
  - [ ] Verify summary in English (cross-language)
  - [ ] Ask question in English about Japanese video

- [ ] **Japanese UI + English Video**
  - [ ] Set UI to Japanese
  - [ ] Upload English video
  - [ ] Verify summary in Japanese (cross-language)
  - [ ] Ask question in Japanese about English video

- [ ] **Auto-Detect**
  - [ ] Set video language to auto-detect
  - [ ] Upload video
  - [ ] Verify correct language detected

- [ ] **Language Persistence**
  - [ ] Set UI to Japanese
  - [ ] Refresh page
  - [ ] Verify UI still in Japanese

#### Core Functionality Testing

- [ ] **Video Upload**
  - [ ] Upload MP4 file
  - [ ] Upload AVI file
  - [ ] Upload MOV file
  - [ ] Try to upload non-video file (should fail)
  - [ ] Upload very large file (test limits)

- [ ] **Processing Status**
  - [ ] Verify "pending" status immediately after upload
  - [ ] Verify "processing" status during processing
  - [ ] Verify "completed" status after success
  - [ ] Verify "failed" status after error

- [ ] **Q&A Functionality**
  - [ ] Ask simple question
  - [ ] Ask complex question
  - [ ] Click "Create 10 Q&A" button
  - [ ] Click "10 Key Points" button
  - [ ] Click "Detailed Summary" button
  - [ ] Clear chat history

#### UI/UX Testing

- [ ] Responsive design on mobile
- [ ] Drag and drop video upload
- [ ] Language selector styling
- [ ] Loading indicators
- [ ] Error messages display correctly
- [ ] Success messages display correctly

---

## Appendix D: API Testing with curl

### Complete API Test Suite

```bash
# 1. Health Check
curl http://localhost:8000/

# 2. Get Supported Languages
curl http://localhost:8000/supported-languages/

# 3. Upload Video (English, English UI)
curl -X POST "http://localhost:8000/upload-video/?language=en&ui_language=en" \
  -F "file=@test_video_en.mp4"

# 4. Upload Video (Auto-detect, Japanese UI)
curl -X POST "http://localhost:8000/upload-video/?language=auto&ui_language=ja" \
  -F "file=@test_video_ja.mp4"

# 5. Check Video Status
curl http://localhost:8000/video-status/1

# 6. Get Video Details
curl http://localhost:8000/video/1

# 7. Ask Question (English)
curl -X POST "http://localhost:8000/ask-question/?ui_language=en" \
  -H "Content-Type: application/json" \
  -d '{"video_id": 1, "question": "What is this video about?"}'

# 8. Ask Question (Japanese)
curl -X POST "http://localhost:8000/ask-question/?ui_language=ja" \
  -H "Content-Type: application/json" \
  -d '{"video_id": 1, "question": "このビデオの内容は何ですか？"}'

# 9. Get All Videos
curl http://localhost:8000/videos/

# 10. Get Chat History
curl http://localhost:8000/chat-history/1
```

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2024-11-05 | Dev Team | Initial comprehensive documentation |
| 2.0 | 2024-11-05 | Dev Team | Added multi-language feature documentation |

---

## Contact & Support

For questions or issues:
1. Check this documentation
2. Review [TROUBLESHOOTING](#15-troubleshooting) section
3. Check server logs
4. Contact development team

---

**End of Documentation**
