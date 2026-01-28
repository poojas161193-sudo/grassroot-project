import os
from openai import OpenAI
from moviepy.editor import VideoFileClip
from decouple import config
from mutagen.mp3 import MP3
from language_config import get_language_name

client = OpenAI(
    api_key=config('OPENAI_API_KEY'),
    base_url=config('OPENAI_BASE_URL')
)


class VideoProcessor:
    def __init__(self):
        self.upload_dir = config('UPLOAD_DIR', default='./uploads')
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

    def _contains_japanese_chars(self, text: str) -> bool:
        """
        Check if text contains Japanese characters (Hiragana, Katakana, Kanji)

        Args:
            text: Text to check

        Returns:
            True if text contains Japanese characters, False otherwise
        """
        if not text:
            return False

        # Japanese Unicode ranges:
        # Hiragana: \u3040-\u309F
        # Katakana: \u30A0-\u30FF
        # Kanji (CJK Unified Ideographs): \u4E00-\u9FFF
        import re
        japanese_pattern = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+')
        return bool(japanese_pattern.search(text))

    def extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio from video file and save as M4A with optimization for API limits"""
        try:
            video = VideoFileClip(video_path)
            audio_path = video_path.rsplit('.', 1)[0] + '.m4a'

            # Extract audio as M4A (AAC codec) with optimized settings
            # M4A/AAC provides better compression and compatibility with OpenAI API
            # 16kHz sample rate is sufficient for speech recognition
            video.audio.write_audiofile(
                audio_path,
                fps=16000,      # 16kHz sample rate for speech
                nbytes=2,       # 16-bit audio
                codec='aac',    # AAC codec in M4A container
                bitrate='32k',  # Low bitrate (32kbps) to minimize file size
                verbose=False,
                logger=None
            )
            video.close()
            return audio_path
        except Exception as e:
            raise Exception(f"Failed to extract audio: {str(e)}")

    def transcribe_with_gpt4o(self, audio_path: str, language: str = 'auto') -> tuple:
        """
        Transcribe audio using GPT-4o via Rakuten AI Gateway

        Args:
            audio_path: Path to audio file
            language: ISO 639-1 language code ('en', 'ja', 'auto' for auto-detection)

        Returns:
            Tuple of (transcription_text, detected_language)
        """
        try:
            transcription_model = config('TRANSCRIPTION_MODEL', default='gpt-4o-transcribe')
            transcription_language = language if language != 'auto' else config('TRANSCRIPTION_LANGUAGE', default='auto')

            print(f"🎤 Starting transcription using {transcription_model}...")
            if transcription_language != 'auto':
                print(f"   Language: {get_language_name(transcription_language)}")
            else:
                print(f"   Language: Auto-detect")

            # Call GPT-4o transcription via Rakuten AI Gateway
            # Check file size (API limit is 25MB)
            file_size_mb = os.path.getsize(audio_path) / (1024*1024)
            print(f"   API Request Details:")
            print(f"   - Model: {transcription_model}")
            print(f"   - Language: {transcription_language if transcription_language != 'auto' else 'auto-detect (parameter omitted)'}")
            print(f"   - File: {os.path.basename(audio_path)}")
            print(f"   - File size: {file_size_mb:.2f} MB")

            if file_size_mb > 25:
                raise Exception(f"Audio file size ({file_size_mb:.2f} MB) exceeds 25MB API limit. Please use a shorter video.")

            # Open file - must pass actual file path for proper multipart encoding
            # The SDK needs the filename to create the multipart/form-data correctly
            from pathlib import Path

            try:
                if transcription_language != 'auto':
                    with open(audio_path, "rb") as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model=transcription_model,
                            file=(Path(audio_path).name, audio_file, "audio/m4a"),
                            language=transcription_language
                        )
                else:
                    with open(audio_path, "rb") as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model=transcription_model,
                            file=(Path(audio_path).name, audio_file, "audio/m4a")
                        )
            except Exception as api_error:
                print(f"\n❌ API Error Details:")
                print(f"   Error Type: {type(api_error).__name__}")
                print(f"   Error Message: {str(api_error)}")
                if hasattr(api_error, 'response'):
                    print(f"   Response: {api_error.response}")
                if hasattr(api_error, 'status_code'):
                    print(f"   Status Code: {api_error.status_code}")
                if hasattr(api_error, 'body'):
                    print(f"   Response Body: {api_error.body}")
                raise

            # GPT-4o returns detected language in response
            detected_lang = getattr(transcript, 'language', transcription_language)
            if detected_lang == 'auto' or not detected_lang:
                detected_lang = 'en'  # Default fallback

            # Convert language codes (e.g., 'english' -> 'en', 'japanese' -> 'ja')
            lang_map = {'english': 'en', 'japanese': 'ja', 'en': 'en', 'ja': 'ja'}
            detected_lang = lang_map.get(detected_lang.lower(), detected_lang[:2].lower())

            print(f"✅ Transcription completed using {transcription_model}")
            print(f"   Detected language: {get_language_name(detected_lang)}")
            print(f"   Length: {len(transcript.text)} characters")

            return (transcript.text, detected_lang)

        except Exception as e:
            raise Exception(f"GPT-4o transcription failed: {str(e)}")

    def generate_audio_summary(self, summary_text: str, video_id: int, language: str = 'en') -> tuple:
        """
        Generate audio summary using TTS-1-HD via Rakuten AI Gateway

        Args:
            summary_text: Text summary to convert to speech
            video_id: Video ID for generating unique filename
            language: ISO 639-1 language code ('en', 'ja')

        Returns:
            Tuple of (audio_file_path, duration_in_seconds)
        """
        try:
            tts_model = config('OPENAI_TTS_MODEL', default='tts-1-hd')
            tts_voice = config('OPENAI_TTS_VOICE', default='nova')
            tts_speed = float(config('OPENAI_TTS_SPEED', default='1.0'))

            print(f"🔊 Generating audio summary using {tts_model}...")
            print(f"   Voice: {tts_voice}, Speed: {tts_speed}x")

            # Generate speech using TTS-1-HD
            response = client.audio.speech.create(
                model=tts_model,
                voice=tts_voice,
                input=summary_text,
                speed=tts_speed
            )

            # Save audio file
            audio_filename = f"summary_{video_id}.mp3"
            audio_path = os.path.join(self.upload_dir, audio_filename)

            # Write audio content to file
            with open(audio_path, 'wb') as audio_file:
                audio_file.write(response.content)

            # Get audio duration using mutagen
            audio = MP3(audio_path)
            duration = audio.info.length

            print(f"✅ Audio summary generated: {audio_filename}")
            print(f"   Duration: {duration:.2f} seconds")

            return (audio_path, duration)

        except Exception as e:
            raise Exception(f"TTS-1-HD audio generation failed: {str(e)}")

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

        # Add language-specific instruction prefix for stronger language signal
        language_prefix = ''
        if language == 'ja':
            language_prefix = '日本語で要約してください。\n\n'
        elif language == 'en':
            language_prefix = 'Please answer in English.\n\n'

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
                        "content": f"{language_prefix}Please summarize this video transcription:\n\n{transcription}"
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

    def process_video(self, video_path: str, user_language: str = None, ui_language: str = 'en', video_id: int = None) -> dict:
        """
        Process video with multi-language support

        Args:
            video_path: Path to video file
            user_language: User-specified language (optional, auto-detect if None or 'auto')
            ui_language: Language for UI responses (summary, Q&A) - 'en' or 'ja'
            video_id: Video ID for generating audio summary filename (required for audio generation)

        Returns:
            Dictionary with transcription, summary, detected_language, transcription_method,
            audio_summary_path, audio_summary_duration
        """
        try:
            print("=" * 70)
            print("🎬 VIDEO PROCESSING STARTED")
            print("=" * 70)

            # Extract audio
            print("\n📹 Step 1: Extracting audio from video...")
            audio_path = self.extract_audio_from_video(video_path)
            print(f"✅ Audio extracted: {audio_path}")

            # Transcribe audio with GPT-4o (includes language detection)
            print(f"\n📝 Step 2: Transcribing audio with GPT-4o...")
            if user_language and user_language != 'auto':
                print(f"   Using user-specified language: {get_language_name(user_language)}")
                transcription, detected_language = self.transcribe_with_gpt4o(audio_path, user_language)
            else:
                # Smart auto-detection: Use UI language as a hint when auto-detecting
                # This improves accuracy, especially for Japanese content
                language_hint = 'auto'
                if ui_language and ui_language != 'en':
                    language_hint = ui_language
                    print(f"   Auto-detecting language with {get_language_name(ui_language)} hint...")
                else:
                    print(f"   Auto-detecting language...")
                transcription, detected_language = self.transcribe_with_gpt4o(audio_path, language_hint)

            # Post-transcription language verification
            # Check if transcription contains Japanese characters but was detected as English
            if detected_language == 'en' and self._contains_japanese_chars(transcription):
                print(f"   ⚠️  Misdetection corrected: Transcription contains Japanese characters")
                detected_language = 'ja'
                print(f"   ✅ Corrected language: {get_language_name(detected_language)}")

            print(f"✅ Transcription completed ({len(transcription)} characters)")

            # Generate text summary in UI language
            print(f"\n📋 Step 3: Generating text summary in {get_language_name(ui_language)}...")
            summary = self.generate_summary(transcription, ui_language)

            # Generate audio summary if video_id provided
            audio_summary_path = None
            audio_summary_duration = None
            if video_id:
                print(f"\n🔊 Step 4: Generating audio summary in {get_language_name(ui_language)}...")
                try:
                    audio_summary_path, audio_summary_duration = self.generate_audio_summary(
                        summary, video_id, ui_language
                    )
                except Exception as audio_error:
                    print(f"⚠️  Audio summary generation failed: {audio_error}")
                    # Continue without audio summary

            # Clean up audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"\n🗑️  Cleaned up temporary audio file")

            print("\n" + "=" * 70)
            print("✅ VIDEO PROCESSING COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print(f"   Video Language: {get_language_name(detected_language)}")
            print(f"   UI Language: {get_language_name(ui_language)}")
            print(f"   Transcription Method: gpt-4o-transcribe")
            if audio_summary_path:
                print(f"   Audio Summary: Generated ({audio_summary_duration:.2f}s)")
            print("=" * 70 + "\n")

            return {
                "transcription": transcription,
                "summary": summary,
                "detected_language": detected_language,
                "transcription_method": "gpt-4o-transcribe",
                "audio_summary_path": audio_summary_path,
                "audio_summary_duration": audio_summary_duration
            }
        except Exception as e:
            # Clean up audio file on error
            if 'audio_path' in locals() and os.path.exists(audio_path):
                os.remove(audio_path)
            raise Exception(f"Failed to process video: {str(e)}")
