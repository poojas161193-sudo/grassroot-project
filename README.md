# Video Analyzer AI

An AI-powered video analysis system that allows users to upload videos, extract audio, transcribe speech to text, and interact with an AI chatbot to ask questions about the video content.

## Features

- 📹 **Video Upload**: Support for various video formats (MP4, AVI, MOV, etc.)
- 🎵 **Audio Extraction**: Automatically extracts audio from uploaded videos
- 📝 **Speech-to-Text**: Uses OpenAI Whisper for accurate transcription
- 🤖 **AI Chat**: Chat with AI about video content using GPT-3.5-turbo
- 📊 **Video Summary**: Automatic generation of video summaries
- 💾 **Database Storage**: Persistent storage of videos and chat history
- 🌐 **Web Interface**: Modern, responsive web interface

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM)
- **MoviePy**: Video processing library for audio extraction
- **Azure OpenAI**: For Whisper transcription and GPT-4 chat responses
- **SQLite**: Local database for development

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **Vanilla JavaScript**: No frameworks, pure JS for simplicity
- **Fetch API**: For making HTTP requests to the backend

## Prerequisites

1. Python 3.12.7 (recommended) or Python 3.8+ 
2. Azure OpenAI service with deployed models (GPT-4 and Whisper)
3. FFmpeg (required by MoviePy for video processing)

## Installation

1. **Clone or download the project:**
   ```bash
   cd grassroot_video_analyser
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg:**
   - **Mac (using Homebrew):**
     ```bash
     brew install ffmpeg
     ```
   - **Windows:**
     Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - **Linux (Ubuntu/Debian):**
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```

4. **Configure environment variables:**
   - Open the `.env` file
   - Configure your Azure OpenAI settings:
     ```
     AZURE_ENDPOINT="https://your-resource.openai.azure.com"
     AZURE_API_KEY="your-azure-openai-api-key"
     DEPLOYMENT_NAME="your-gpt-deployment-name"
     WHISPER_AZURE_ENDPOINT="https://your-whisper-resource.cognitiveservices.azure.com"
     WHISPER_DEPLOYMENT_NAME="your-whisper-deployment-name"
     WHISPER_API_KEY="your-whisper-api-key"
     ```
   - Optionally, modify other settings like upload directory

## Usage

1. **Start the backend server:**
   ```bash
   cd backend
   python main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Open the frontend:**
   - Navigate to the `frontend` directory
   - Open `index.html` in your web browser
   - Or serve it with a simple HTTP server:
     ```bash
     cd frontend
     python -m http.server 3000
     ```
     Then visit `http://localhost:3000`

3. **Using the application:**
   - Upload a video by dragging and dropping or clicking the upload area
   - Wait for the video to be processed (this may take a few minutes)
   - Once processed, you'll see a summary of the video
   - Use the chat interface to ask questions about the video content

## API Endpoints

### Upload Video
- **POST** `/upload-video/`
- Uploads and processes a video file
- Returns video ID, transcription, and summary

### Ask Question
- **POST** `/ask-question/`
- Asks a question about a specific video
- Requires `video_id` and `question` in request body

### Get Videos
- **GET** `/videos/`
- Returns list of all uploaded videos

### Get Video Details
- **GET** `/video/{video_id}`
- Returns detailed information about a specific video

### Get Chat History
- **GET** `/chat-history/{video_id}`
- Returns chat history for a specific video

## Example Questions You Can Ask

- "What is this video about?"
- "Summarize the main points discussed"
- "Who are the speakers in this video?"
- "What topics are covered?"
- "What are the key takeaways?"
- "Can you explain the technical concepts mentioned?"

## File Structure

```
grassroot_video_analyser/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   └── video_processor.py   # Video processing logic
├── frontend/
│   ├── index.html          # Main web interface
│   └── script.js           # Frontend JavaScript
├── uploads/                # Directory for uploaded videos
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
└── README.md              # This file
```

## Configuration

The `.env` file contains the following configurable options:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DATABASE_URL`: Database connection string (default: SQLite)
- `SECRET_KEY`: Secret key for the application
- `UPLOAD_DIR`: Directory for storing uploaded videos

## Troubleshooting

1. **Video processing fails:**
   - Ensure FFmpeg is properly installed
   - Check if the video format is supported
   - Verify the OpenAI API key is correct

2. **Transcription not working:**
   - Confirm your OpenAI API key has access to Whisper
   - Check if you have sufficient API credits

3. **Chat responses not working:**
   - Verify your OpenAI API key has access to GPT-3.5-turbo
   - Check your API usage limits

## Security Notes

- The application stores uploaded videos locally
- Transcriptions and chat history are stored in the local database
- Ensure your OpenAI API key is kept secure
- Consider implementing user authentication for production use

## License

This project is provided as-is for educational and development purposes.