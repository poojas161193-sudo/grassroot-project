import os
from openai import OpenAI
from moviepy.editor import VideoFileClip
from decouple import config
import azure.cognitiveservices.speech as speechsdk
from language_config import (
    get_azure_language_code,
    get_whisper_language_code,
    get_language_name,
    AZURE_LANGUAGE_CANDIDATES
)

client = OpenAI(
    api_key=config('OPENAI_API_KEY'),
    base_url=config('OPENAI_BASE_URL')
)


class VideoProcessor:
    def __init__(self):
        self.upload_dir = config('UPLOAD_DIR', default='./uploads')
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    def extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio from video file and save as WAV with optimization"""
        try:
            video = VideoFileClip(video_path)
            audio_path = video_path.rsplit('.', 1)[0] + '.wav'

            # Extract audio with lower quality settings for faster processing
            # 16kHz sample rate is sufficient for speech recognition
            video.audio.write_audiofile(
                audio_path,
                fps=16000,  # Lower sample rate for faster processing
                nbytes=2,   # 16-bit audio
                codec='pcm_s16le',  # Uncompressed PCM for compatibility
                verbose=False,
                logger=None,
                bitrate='64k'  # Lower bitrate
            )
            video.close()
            return audio_path
        except Exception as e:
            raise Exception(f"Failed to extract audio: {str(e)}")

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

            speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

            # Configure auto-detect with supported languages (English and Japanese)
            auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
                languages=AZURE_LANGUAGE_CANDIDATES  # ['en-US', 'ja-JP']
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
                print(f"✅ Language detected: {lang_code} ({get_language_name(lang_code)})")
                return lang_code
            else:
                print(f"⚠️  Language detection failed, defaulting to English")
                return 'en'

        except Exception as e:
            print(f"⚠️  Language detection error: {e}, defaulting to English")
            return 'en'

    def transcribe_audio(self, audio_path: str, language: str = 'en') -> tuple:
        """
        Transcribe audio to text with specific language

        Args:
            audio_path: Path to audio file
            language: ISO 639-1 language code ('en', 'ja')

        Returns:
            Tuple of (transcription_text, method_used)
        """
        try:
            text = self._transcribe_with_azure_speech(audio_path, language)
            return (text, 'azure_speech')
        except Exception as azure_error:
            print(f"⚠️  Azure Speech failed: {azure_error}")
            try:
                text = self._transcribe_with_azure_whisper(audio_path, language)
                return (text, 'azure_whisper')
            except Exception as whisper_error:
                print(f"⚠️  Azure Whisper failed: {whisper_error}")
                try:
                    text = self._transcribe_with_local_whisper(audio_path, language)
                    return (text, 'local_whisper')
                except Exception as local_error:
                    raise Exception(f"All transcription methods failed. Last error: {str(local_error)}")

    def _transcribe_with_azure_speech(self, audio_path: str, language: str = 'en') -> str:
        """
        Transcribe using Azure Speech Services with specified language

        Args:
            audio_path: Path to audio file
            language: ISO 639-1 language code ('en', 'ja')

        Returns:
            Transcription text
        """
        speech_key = config('AZURE_SPEACH_KEY')  # Note: keeping the typo from your env file
        service_region = config('AZURE_REGION', default='eastus')

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_recognition_language = get_azure_language_code(language)

        # Enable profanity filter and other optimizations
        speech_config.enable_dictation()
        speech_config.request_word_level_timestamps()

        audio_config = speechsdk.audio.AudioConfig(filename=audio_path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # For longer files, use continuous recognition
        done = False
        recognized_text = []
        recognition_error = None

        def stop_cb(evt):
            nonlocal done
            done = True

        def recognized_cb(evt):
            if evt.result.text:
                recognized_text.append(evt.result.text)

        def canceled_cb(evt):
            nonlocal recognition_error
            if evt.reason == speechsdk.CancellationReason.Error:
                recognition_error = evt.error_details

        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(canceled_cb)

        print(f"🎤 Starting transcription using Azure Speech ({get_language_name(language)})...")
        speech_recognizer.start_continuous_recognition()

        # Wait for completion with reduced polling interval
        import time
        timeout = 600  # 10 minutes timeout for longer videos
        elapsed = 0
        while not done and elapsed < timeout:
            time.sleep(0.1)  # Reduced from 0.5 to 0.1 for faster completion detection
            elapsed += 0.1

        speech_recognizer.stop_continuous_recognition()

        if recognition_error:
            raise Exception(f"Speech recognition error: {recognition_error}")

        if not recognized_text:
            raise Exception("No speech could be recognized in the audio file")

        print(f"✅ Transcription completed using Azure Speech")
        return " ".join(recognized_text)

    def _transcribe_with_azure_whisper(self, audio_path: str, language: str = 'en') -> str:
        """
        Transcribe using OpenAI Whisper via Rakuten AI Gateway

        Args:
            audio_path: Path to audio file
            language: ISO 639-1 language code ('en', 'ja')

        Returns:
            Transcription text
        """
        print(f"🎤 Starting transcription using Azure Whisper ({get_language_name(language)})...")
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=get_whisper_language_code(language)
            )
        print(f"✅ Transcription completed using Azure Whisper")
        return transcript.text

    def _transcribe_with_local_whisper(self, audio_path: str, language: str = 'en') -> str:
        """
        Transcribe using local OpenAI Whisper

        Args:
            audio_path: Path to audio file
            language: ISO 639-1 language code ('en', 'ja')

        Returns:
            Transcription text
        """
        print(f"🎤 Starting transcription using Local Whisper ({get_language_name(language)})...")
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language=get_whisper_language_code(language))
        print(f"✅ Transcription completed using Local Whisper")
        return result["text"]

    def generate_summary(self, transcription: str, language: str = 'en') -> str:
        """
        Generate summary in specified language

        Args:
            transcription: Video transcription text
            language: ISO 639-1 language code for summary ('en', 'ja')

        Returns:
            Summary text in specified language
        """
        lang_name = get_language_name(language)

        try:
            print(f"📝 Generating summary in {lang_name}...")
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
            print(f"✅ Summary generated in {lang_name}")
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")

    def answer_question(self, transcription: str, question: str, language: str = 'en') -> str:
        """
        Answer questions in specified language

        Args:
            transcription: Video transcription text
            question: User's question
            language: ISO 639-1 language code for answer ('en', 'ja')

        Returns:
            Answer text in specified language
        """
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
                            f"- Add three dashes (---) as a separator between each Q&A pair\n"
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

    def process_video(self, video_path: str, user_language: str = None, ui_language: str = 'en') -> dict:
        """
        Process video with multi-language support

        Args:
            video_path: Path to video file
            user_language: User-specified language (optional, auto-detect if None or 'auto')
            ui_language: Language for UI responses (summary, Q&A) - 'en' or 'ja'

        Returns:
            Dictionary with transcription, summary, detected_language, transcription_method
        """
        try:
            print("=" * 70)
            print("🎬 VIDEO PROCESSING STARTED")
            print("=" * 70)

            # Extract audio
            print("\n📹 Step 1: Extracting audio from video...")
            audio_path = self.extract_audio_from_video(video_path)
            print(f"✅ Audio extracted: {audio_path}")

            # Detect or use specified language
            print("\n🌍 Step 2: Language detection...")
            if user_language and user_language != 'auto':
                detected_language = user_language
                print(f"✅ Using user-specified language: {detected_language} ({get_language_name(detected_language)})")
            else:
                detected_language = self.detect_language(audio_path)

            # Transcribe audio in detected/specified language
            print(f"\n📝 Step 3: Transcribing audio in {get_language_name(detected_language)}...")
            transcription, method = self.transcribe_audio(audio_path, detected_language)
            print(f"✅ Transcription completed ({len(transcription)} characters)")

            # Generate summary in UI language
            print(f"\n📋 Step 4: Generating summary in {get_language_name(ui_language)}...")
            summary = self.generate_summary(transcription, ui_language)

            # Clean up audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"🗑️  Cleaned up temporary audio file")

            print("\n" + "=" * 70)
            print("✅ VIDEO PROCESSING COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print(f"   Video Language: {get_language_name(detected_language)}")
            print(f"   UI Language: {get_language_name(ui_language)}")
            print(f"   Transcription Method: {method}")
            print("=" * 70 + "\n")

            return {
                "transcription": transcription,
                "summary": summary,
                "detected_language": detected_language,
                "transcription_method": method
            }
        except Exception as e:
            # Clean up audio file on error
            if 'audio_path' in locals() and os.path.exists(audio_path):
                os.remove(audio_path)
            raise Exception(f"Failed to process video: {str(e)}")
