# Video Analyzer AI - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Features](#features)
5. [Installation Guide](#installation-guide)
6. [Configuration](#configuration)
7. [API Documentation](#api-documentation)
8. [Frontend Documentation](#frontend-documentation)
9. [Backend Documentation](#backend-documentation)
10. [Database Schema](#database-schema)
11. [Usage Guide](#usage-guide)
12. [Troubleshooting](#troubleshooting)
13. [Development Guide](#development-guide)
14. [Deployment](#deployment)

---

## Project Overview

**Video Analyzer AI** is a web-based application that allows users to upload videos, automatically transcribe their audio content, generate AI-powered summaries, and interact with an intelligent chatbot to ask questions about the video content.

### Key Capabilities
- Upload videos in various formats (MP4, AVI, MOV, etc.)
- Automatic audio extraction from videos
- Speech-to-text transcription using Azure Speech Services with fallback to Whisper
- AI-generated video summaries
- Interactive Q&A chatbot powered by GPT-4
- Chat history persistence
- Background video processing
- Real-time processing status updates

---

## Architecture

### System Architecture

```
┌─────────────────┐
│   Frontend      │
│   (HTML/JS)     │
│   Port 3000     │
└────────┬────────┘
         │ HTTP/REST API
         ▼
┌─────────────────┐
│   Backend       │
│   (FastAPI)     │
│   Port 8000     │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌─────┐ ┌──────────┐ ┌────────┐
│SQLite  │ │MoviePy│ │Azure     │ │Rakuten │
│Database│ │       │ │Speech    │ │AI      │
│        │ │       │ │Services  │ │Gateway │
└────────┘ └─────┘ └──────────┘ └────────┘
```

### Component Breakdown

1. **Frontend Layer**
   - Vanilla JavaScript (no frameworks)
   - Responsive CSS with gradient design
   - Drag-and-drop file upload
   - Real-time chat interface
   - Markdown rendering support

2. **Backend Layer**
   - FastAPI web framework
   - Asynchronous request handling
   - Background task processing
   - RESTful API endpoints
   - CORS middleware for cross-origin requests

3. **Processing Layer**
   - MoviePy for video/audio processing
   - Azure Speech Services for transcription
   - OpenAI Whisper (fallback)
   - GPT-4 for chat responses

4. **Data Layer**
   - SQLite database
   - SQLAlchemy ORM
   - Persistent storage for videos and chat history

---

## Technology Stack

### Backend Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.8+ (Recommended: 3.12.7) | Core programming language |
| FastAPI | Latest | Web framework for building APIs |
| SQLAlchemy | Latest | ORM for database operations |
| MoviePy | Latest | Video processing and audio extraction |
| Azure Speech SDK | Latest | Primary speech-to-text service |
| OpenAI Python SDK | Latest | AI chat completions via Rakuten Gateway |
| Python-Decouple | Latest | Environment variable management |
| Uvicorn | Latest | ASGI server |

### Frontend Technologies

| Technology | Purpose |
|-----------|---------|
| HTML5 | Markup structure |
| CSS3 | Styling with gradients and animations |
| Vanilla JavaScript | Client-side logic |
| Fetch API | HTTP requests to backend |

### External Services

| Service | Purpose | Configuration |
|---------|---------|--------------|
| Rakuten AI Gateway | GPT-4 chat completions | OPENAI_API_KEY, OPENAI_BASE_URL |
| Azure Speech Services | Speech-to-text transcription | AZURE_SPEACH_KEY, AZURE_REGION |
| Azure OpenAI Whisper | Fallback transcription | WHISPER_API_KEY, WHISPER_AZURE_ENDPOINT |

### Development Tools

- FFmpeg (required for video processing)
- Git (version control)
- VS Code / PyCharm (recommended IDEs)

---

## Features

### 1. Video Upload
- **Drag-and-drop interface**: Simply drag video files onto the upload area
- **Click-to-browse**: Traditional file browser option
- **Format support**: MP4, AVI, MOV, MKV, and other common video formats
- **Large file handling**: Chunked upload for efficient processing of large videos
- **Progress indicators**: Real-time feedback during upload

### 2. Audio Processing
- **Automatic extraction**: Extracts audio track from video files
- **Optimization**:
  - 16kHz sample rate for faster processing
  - 16-bit audio depth
  - PCM encoding for compatibility
  - 64k bitrate for efficient storage

### 3. Speech Transcription
- **Multi-tier fallback system**:
  1. Azure Speech Services (primary)
  2. Azure OpenAI Whisper (secondary)
  3. Local Whisper model (tertiary)
- **Continuous recognition**: Handles long videos (up to 10 minutes)
- **Language support**: English (configurable for other languages)

### 4. AI-Powered Summaries
- **Automatic generation**: Creates concise summaries upon video processing
- **Context-aware**: Captures main points and key information
- **Powered by**: GPT-4 via Rakuten AI Gateway

### 5. Interactive Chat
- **Question answering**: Ask anything about the video content
- **Context retention**: Uses full transcription for accurate responses
- **Predefined queries**: Quick action buttons for common questions
  - Generate 10 Q&A pairs
  - List 10 key points
  - Detailed summary
  - Custom questions
- **Chat management**: Clear chat button with confirmation dialog
- **Markdown support**: Rich text formatting in responses

### 6. Background Processing
- **Non-blocking**: Video processing happens in background
- **Status polling**: Real-time updates on processing status
- **Error handling**: Graceful failure management with error messages

### 7. User Interface
- **Responsive design**: Works on desktop, tablet, and mobile
- **Modern aesthetics**: Gradient color scheme (pink to purple)
- **Intuitive navigation**: Clear visual hierarchy
- **Loading states**: Spinners and progress indicators
- **Error feedback**: Clear error messages with suggestions

---

## Installation Guide

### Prerequisites

1. **Python 3.8+** (Python 3.12.7 recommended)
   ```bash
   python3 --version
   ```

2. **FFmpeg** (required for video processing)
   - **macOS**:
     ```bash
     brew install ffmpeg
     ```
   - **Ubuntu/Debian**:
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

3. **pip** (Python package manager)
   ```bash
   pip3 --version
   ```

### Installation Steps

1. **Navigate to project directory**
   ```bash
   cd grassroot_video_analyser_v3
   ```

2. **Install Python dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure environment variables**
   - Edit the `.env` file with your API credentials:
   ```env
   # Rakuten AI Gateway Configuration
   OPENAI_API_KEY=your_rakuten_api_key
   OPENAI_BASE_URL=https://api.ai.public.rakuten-it.com/openai/v1
   LLM_MODEL=gpt-4o

   # Azure Speech Services (Optional - for transcription)
   AZURE_SPEACH_KEY=your_azure_speech_key
   AZURE_REGION=eastus

   # Azure OpenAI Whisper (Optional - fallback transcription)
   WHISPER_API_KEY=your_whisper_key
   WHISPER_AZURE_ENDPOINT=your_whisper_endpoint
   WHISPER_DEPLOYMENT_NAME=whisper

   # Database and Storage
   DATABASE_URL=sqlite:///./video_analyzer.db
   UPLOAD_DIR=./uploads
   ```

4. **Create uploads directory**
   ```bash
   mkdir -p uploads
   ```

5. **Verify installation**
   ```bash
   python3 -c "import fastapi, sqlalchemy, moviepy, openai; print('All dependencies installed successfully!')"
   ```

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | Rakuten AI Gateway API key |
| `OPENAI_BASE_URL` | Yes | - | Rakuten AI Gateway base URL |
| `LLM_MODEL` | No | gpt-4o | Model name for chat completions |
| `AZURE_SPEACH_KEY` | No | - | Azure Speech Services API key |
| `AZURE_REGION` | No | eastus | Azure Speech Services region |
| `WHISPER_API_KEY` | No | - | Azure OpenAI Whisper API key |
| `WHISPER_AZURE_ENDPOINT` | No | - | Azure OpenAI Whisper endpoint |
| `WHISPER_DEPLOYMENT_NAME` | No | whisper | Whisper deployment name |
| `DATABASE_URL` | No | sqlite:///./video_analyzer.db | Database connection string |
| `UPLOAD_DIR` | No | ./uploads | Directory for uploaded videos |

### Server Configuration

**Backend (FastAPI)**
- Host: `0.0.0.0` (all interfaces)
- Port: `8000`
- Auto-reload: Enabled in development

**Frontend (HTTP Server)**
- Host: `localhost`
- Port: `3000`

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "message": "Video Analyzer API is running"
}
```

---

#### 2. Upload Video
```http
POST /upload-video/
```

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing video file

**Response:**
```json
{
  "message": "Video uploaded successfully. Processing started in background.",
  "video_id": 1,
  "filename": "example.mp4",
  "processing_status": "pending"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid file type
- `500`: Server error

---

#### 3. Check Video Status
```http
GET /video-status/{video_id}
```

**Parameters:**
- `video_id` (path): Integer ID of the video

**Response:**
```json
{
  "video_id": 1,
  "filename": "example.mp4",
  "processing_status": "completed",
  "error_message": null,
  "transcription": "Full transcription text...",
  "summary": "Summary of the video content..."
}
```

**Processing Status Values:**
- `pending`: Video uploaded, waiting to process
- `processing`: Currently being processed
- `completed`: Processing successful
- `failed`: Processing failed (check error_message)

---

#### 4. Get Video Details
```http
GET /video/{video_id}
```

**Parameters:**
- `video_id` (path): Integer ID of the video

**Response:**
```json
{
  "id": 1,
  "filename": "example.mp4",
  "transcription": "Full transcription...",
  "summary": "Video summary...",
  "processing_status": "completed",
  "error_message": null,
  "uploaded_at": "2025-10-09T12:00:00",
  "processed_at": "2025-10-09T12:05:00"
}
```

---

#### 5. Ask Question
```http
POST /ask-question/
```

**Request:**
```json
{
  "video_id": 1,
  "question": "What is the main topic of this video?"
}
```

**Response:**
```json
{
  "question": "What is the main topic of this video?",
  "answer": "The main topic of this video is...",
  "video_id": 1
}
```

---

#### 6. Get All Videos
```http
GET /videos/
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "example.mp4",
    "summary": "Brief summary...",
    "uploaded_at": "2025-10-09T12:00:00"
  }
]
```

---

#### 7. Get Chat History
```http
GET /chat-history/{video_id}
```

**Parameters:**
- `video_id` (path): Integer ID of the video

**Response:**
```json
[
  {
    "question": "What is this video about?",
    "answer": "This video is about...",
    "timestamp": "2025-10-09T12:10:00"
  }
]
```

---

## Frontend Documentation

### File Structure

```
frontend/
├── index.html      # Main HTML file
└── script.js       # JavaScript logic
```

### Main Components

#### 1. VideoAnalyzer Class
Main class that handles all frontend logic.

**Methods:**

- `constructor()`: Initializes event listeners and setup
- `initializeEventListeners()`: Binds UI events
- `setupDragAndDrop()`: Configures drag-and-drop functionality
- `setupSuggestionChips()`: Sets up quick action buttons
- `handleFileSelect(file)`: Handles file selection and upload
- `pollProcessingStatus(videoId)`: Polls server for processing status
- `askQuestion()`: Sends user question to backend
- `askPredefinedQuestion(question)`: Sends predefined question
- `displayVideoInfo(data)`: Displays video summary
- `showChatSection()`: Shows the chat interface
- `addMessageToChat(message, type)`: Adds message to chat UI
- `formatMarkdown(text)`: Converts markdown to HTML
- `clearChat()`: Clears chat history with confirmation
- `showLoading(show, message)`: Shows/hides loading indicator
- `showError(message)`: Displays error message
- `showSuccess(message)`: Displays success message

#### 2. UI Elements

**Upload Section:**
- Drag-and-drop area
- File input button
- Loading indicator

**Video Info Section:**
- Filename display
- Summary display
- Quick action chips

**Chat Section:**
- Chat history container
- Message input field
- Send button
- Clear chat button

### Styling

**Color Scheme:**
- Primary gradient: Pink (#ff008c) to Purple (#9933ff)
- Background: White with slight pink tint
- Borders: Pink accent
- Shadows: Pink glow effects

**Responsive Breakpoints:**
- Desktop: > 768px
- Mobile: ≤ 768px

---

## Backend Documentation

### File Structure

```
backend/
├── main.py              # FastAPI application
├── models.py            # Database models
└── video_processor.py   # Video processing logic
```

### Main Components

#### 1. main.py - FastAPI Application

**Key Components:**
- FastAPI app initialization
- CORS middleware configuration
- Route handlers
- Background task processing
- Database session management

**Background Processing:**
```python
async def process_video_background(video_id: int, file_path: str)
```
Handles video processing asynchronously:
1. Updates status to "processing"
2. Calls VideoProcessor
3. Updates database with results
4. Handles errors and updates status

---

#### 2. models.py - Database Models

**Video Model:**
```python
class Video(Base):
    id: Integer (Primary Key)
    filename: String
    file_path: String
    transcription: Text
    summary: Text
    processing_status: String (default: 'pending')
    error_message: Text
    uploaded_at: DateTime
    processed_at: DateTime
```

**ChatHistory Model:**
```python
class ChatHistory(Base):
    id: Integer (Primary Key)
    video_id: Integer (Foreign Key)
    question: Text
    answer: Text
    timestamp: DateTime
```

---

#### 3. video_processor.py - Video Processing

**VideoProcessor Class:**

Methods:
- `extract_audio_from_video(video_path)`: Extracts audio from video
- `transcribe_audio(audio_path)`: Transcribes audio to text (with fallbacks)
- `_transcribe_with_azure_speech(audio_path)`: Azure Speech Services
- `_transcribe_with_azure_whisper(audio_path)`: Azure OpenAI Whisper
- `_transcribe_with_local_whisper(audio_path)`: Local Whisper model
- `generate_summary(transcription)`: Generates AI summary
- `answer_question(transcription, question)`: Answers user questions
- `process_video(video_path)`: Main processing pipeline

**Processing Pipeline:**
```
Video Upload
    ↓
Extract Audio (MoviePy)
    ↓
Transcribe Audio (Azure Speech / Whisper)
    ↓
Generate Summary (GPT-4)
    ↓
Store in Database
    ↓
Return Results
```

---

## Database Schema

### Tables

#### videos
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| filename | VARCHAR | NOT NULL |
| file_path | VARCHAR | NOT NULL |
| transcription | TEXT | |
| summary | TEXT | |
| processing_status | VARCHAR | DEFAULT 'pending' |
| error_message | TEXT | |
| uploaded_at | DATETIME | DEFAULT CURRENT_TIMESTAMP |
| processed_at | DATETIME | |

#### chat_history
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| video_id | INTEGER | FOREIGN KEY (videos.id) |
| question | TEXT | NOT NULL |
| answer | TEXT | NOT NULL |
| timestamp | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### Relationships
- One Video has many ChatHistory entries (One-to-Many)

---

## Usage Guide

### Starting the Application

**Option 1: Using startup script**
```bash
./start.sh
```
Then manually run:
```bash
# Terminal 1
python3 run_backend.py

# Terminal 2
python3 run_frontend.py
```

**Option 2: Manual start**
```bash
# Start backend
python3 run_backend.py

# Start frontend (in new terminal)
python3 run_frontend.py
```

### Accessing the Application

1. Open browser: `http://localhost:3000`
2. Backend API: `http://localhost:8000`
3. API docs: `http://localhost:8000/docs`

### Using the Application

#### Step 1: Upload Video
1. Drag and drop video file onto upload area, OR
2. Click upload area to browse and select file
3. Wait for "Video uploaded successfully" message

#### Step 2: Wait for Processing
- Processing status shows in real-time
- Can take 2-10 minutes depending on video length
- Progress messages update automatically

#### Step 3: View Summary
- Automatic summary appears when processing completes
- Shows filename and AI-generated summary

#### Step 4: Ask Questions
**Option A: Use Quick Actions**
- Click "Create 10 Q&A" for question-answer pairs
- Click "10 Key Points" for highlighted points
- Click "Detailed Summary" for expanded summary
- Click "Ask Any Question" for custom input

**Option B: Type Custom Question**
- Type question in input field
- Press Enter or click "Send"
- AI responds based on video content

#### Step 5: Manage Chat
- Scroll through chat history
- Click "Clear Chat" to remove all messages
- Confirm when prompted

---

## Troubleshooting

### Common Issues

#### 1. Video Upload Fails
**Error:** "File must be a video"
- **Solution**: Ensure file is a valid video format (MP4, AVI, MOV)

**Error:** "Failed to upload video"
- **Solution**: Check backend is running on port 8000
- **Solution**: Check file size isn't too large
- **Solution**: Verify sufficient disk space

#### 2. Processing Takes Too Long
**Symptom:** Video stuck in "processing" status
- **Solution**: Check backend logs for errors
- **Solution**: Verify FFmpeg is installed: `ffmpeg -version`
- **Solution**: Check API keys are valid
- **Solution**: Try smaller/shorter video

#### 3. Transcription Fails
**Error:** "All transcription methods failed"
- **Solution**: Verify Azure Speech Services key and region
- **Solution**: Check Whisper API credentials
- **Solution**: Ensure audio is clear and contains speech
- **Solution**: Try installing local Whisper: `pip install openai-whisper`

#### 4. Chat Not Working
**Error:** "Failed to answer question"
- **Solution**: Verify Rakuten AI Gateway credentials
- **Solution**: Check OPENAI_BASE_URL is correct
- **Solution**: Ensure video processing completed successfully

#### 5. Port Already in Use
**Error:** "Address already in use"
- **Solution**: Kill existing processes:
  ```bash
  lsof -ti:8000 | xargs kill -9
  lsof -ti:3000 | xargs kill -9
  ```

#### 6. Clear Chat Button Not Working
- **Solution**: Hard refresh browser (Ctrl+Shift+R / Cmd+Shift+R)
- **Solution**: Clear browser cache
- **Solution**: Check browser console for JavaScript errors

### Debugging

#### Check Backend Logs
```bash
# Backend logs show in terminal where run_backend.py was started
# Look for error messages and tracebacks
```

#### Check Frontend Logs
```bash
# Open browser developer console (F12)
# Check Console tab for JavaScript errors
# Check Network tab for failed requests
```

#### Test API Directly
```bash
# Test health check
curl http://localhost:8000/

# Test video status
curl http://localhost:8000/video-status/1
```

#### Verify Dependencies
```bash
# Check Python packages
pip3 list | grep -E "fastapi|sqlalchemy|moviepy|openai"

# Check FFmpeg
ffmpeg -version

# Check Python version
python3 --version
```

---

## Development Guide

### Development Setup

1. **Enable debug mode**
   - FastAPI auto-reload is enabled by default in `run_backend.py`

2. **Install development tools**
   ```bash
   pip3 install black flake8 pytest
   ```

3. **Code formatting**
   ```bash
   black backend/
   ```

4. **Linting**
   ```bash
   flake8 backend/
   ```

### Adding New Features

#### Adding New API Endpoint

1. Add route handler in `backend/main.py`:
```python
@app.get("/my-endpoint")
async def my_endpoint(db: Session = Depends(get_db)):
    # Your logic here
    return {"result": "data"}
```

2. Update frontend to call endpoint in `frontend/script.js`:
```javascript
async myFunction() {
    const response = await fetch(`${API_BASE_URL}/my-endpoint`);
    const data = await response.json();
    // Handle data
}
```

#### Adding Database Model

1. Define model in `backend/models.py`:
```python
class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(Integer, primary_key=True, index=True)
    # Add fields
```

2. Tables auto-create on startup via `create_tables()`

#### Customizing UI

1. Edit styles in `frontend/index.html` `<style>` section
2. Modify HTML structure in `frontend/index.html`
3. Update JavaScript logic in `frontend/script.js`

### Testing

#### Manual Testing
```bash
# Test video upload
curl -X POST -F "file=@test.mp4" http://localhost:8000/upload-video/

# Test question
curl -X POST -H "Content-Type: application/json" \
  -d '{"video_id":1,"question":"What is this about?"}' \
  http://localhost:8000/ask-question/
```

#### Unit Testing (TODO)
- Add pytest tests for video_processor.py
- Add tests for API endpoints
- Add frontend JavaScript tests

---

## Deployment

### Production Checklist

- [ ] Change `DATABASE_URL` to production database
- [ ] Set strong `SECRET_KEY` in .env
- [ ] Configure CORS for specific origins
- [ ] Use production ASGI server (Gunicorn + Uvicorn)
- [ ] Set up HTTPS/SSL
- [ ] Configure file upload limits
- [ ] Set up log rotation
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerts
- [ ] Add authentication/authorization
- [ ] Rate limiting on API endpoints

### Deployment Options

#### Option 1: Docker (Recommended)

Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t video-analyzer .
docker run -p 8000:8000 -p 3000:3000 --env-file .env video-analyzer
```

#### Option 2: Linux Server

1. Install dependencies:
```bash
sudo apt update
sudo apt install python3 python3-pip ffmpeg nginx
```

2. Clone project and install:
```bash
git clone <repo-url>
cd grassroot_video_analyser_v3
pip3 install -r requirements.txt
```

3. Configure systemd service:
```ini
[Unit]
Description=Video Analyzer Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 run_backend.py
Restart=always

[Install]
WantedBy=multi-user.target
```

4. Configure Nginx reverse proxy
5. Set up SSL with Let's Encrypt

#### Option 3: Cloud Platform (AWS/Azure/GCP)

- Use managed services for database
- Deploy backend as containerized service
- Serve frontend via CDN (CloudFront/Azure CDN)
- Use managed file storage (S3/Blob Storage)

---

## Security Considerations

### Current Implementation
- CORS enabled for all origins (development only)
- No authentication/authorization
- API keys stored in .env file
- Local file storage

### Recommended for Production
1. **Authentication**: Implement user authentication (JWT/OAuth)
2. **Authorization**: Role-based access control
3. **CORS**: Restrict to specific domains
4. **File Upload**: Virus scanning, size limits, type validation
5. **Rate Limiting**: Prevent abuse
6. **HTTPS**: Encrypt all traffic
7. **Secrets Management**: Use vault service (AWS Secrets Manager, Azure Key Vault)
8. **Input Validation**: Sanitize all user inputs
9. **SQL Injection**: Already protected by SQLAlchemy ORM
10. **XSS**: Frontend already escapes HTML

---

## Performance Optimization

### Current Optimizations
- Chunked file uploads (1MB chunks)
- Background video processing
- Optimized audio extraction (16kHz, 64k bitrate)
- Connection pooling with database

### Future Improvements
- **Caching**: Redis for API responses
- **CDN**: Serve static assets via CDN
- **Compression**: Gzip/Brotli compression
- **Database**: PostgreSQL for better performance
- **Queue**: Celery for task queue
- **Load Balancing**: Multiple backend instances
- **Video Preprocessing**: Optimize before transcription

---

## License

This project is provided as-is for educational and development purposes.

---

## Support

For issues and questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review API documentation
3. Check backend logs for errors
4. Open issue in project repository

---

## Version History

### v3.0 (Current)
- Switched from Azure OpenAI to Rakuten AI Gateway
- Added clear chat functionality
- Background processing with status polling
- Improved error handling
- Enhanced UI with gradient design

### v2.0
- Added Azure Speech Services
- Fallback transcription system
- Chat history persistence
- Quick action chips

### v1.0
- Initial release
- Basic video upload and processing
- OpenAI Whisper transcription
- Simple Q&A interface

---

## Credits

**Developed by**: Grassroot Team
**AI Models**: OpenAI GPT-4, Whisper
**Infrastructure**: Rakuten AI Gateway, Azure Cognitive Services
**Libraries**: FastAPI, SQLAlchemy, MoviePy

---

## Appendix

### A. Requirements.txt Contents
```
fastapi
uvicorn[standard]
sqlalchemy
python-decouple
moviepy
openai
azure-cognitiveservices-speech
python-multipart
```

### B. File Tree
```
grassroot_video_analyser_v3/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── video_processor.py
├── frontend/
│   ├── index.html
│   └── script.js
├── uploads/
├── .env
├── requirements.txt
├── run_backend.py
├── run_frontend.py
├── start.sh
├── README.md
├── DATABASE_GUIDE.md
└── PROJECT_DOCUMENTATION.md
```

### C. Environment Variables Template
```env
# Rakuten AI Gateway
OPENAI_API_KEY=raik-sk-xxx
OPENAI_BASE_URL=https://api.ai.public.rakuten-it.com/openai/v1
LLM_MODEL=gpt-4o

# Azure Speech Services (Optional)
AZURE_SPEACH_KEY=your_key_here
AZURE_REGION=eastus

# Azure OpenAI Whisper (Optional)
WHISPER_API_KEY=your_key_here
WHISPER_AZURE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com
WHISPER_DEPLOYMENT_NAME=whisper

# Database
DATABASE_URL=sqlite:///./video_analyzer.db

# Storage
UPLOAD_DIR=./uploads
```

---

**End of Documentation**

For the latest updates, visit the project repository.
