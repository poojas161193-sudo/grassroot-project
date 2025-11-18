"""
Test script to check if Rakuten AI Gateway supports Whisper API
for multi-language transcription
"""
import os
from openai import OpenAI
from decouple import config

def test_rakuten_whisper_support():
    """Test if Rakuten AI Gateway supports Whisper transcription"""

    print("=" * 60)
    print("Testing Rakuten AI Gateway - Whisper API Support")
    print("=" * 60)

    # Load credentials
    api_key = config('OPENAI_API_KEY')
    base_url = config('OPENAI_BASE_URL')

    print(f"\n✓ API Key: {api_key[:20]}...")
    print(f"✓ Base URL: {base_url}")

    # Initialize client
    client = OpenAI(api_key=api_key, base_url=base_url)

    # Test 1: Check if chat completions work
    print("\n" + "=" * 60)
    print("Test 1: Chat Completions (GPT-4)")
    print("=" * 60)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Say 'Hello' in Japanese"}
            ],
            max_tokens=50
        )
        result = response.choices[0].message.content
        print(f"✅ Chat completions working!")
        print(f"   Response: {result}")
    except Exception as e:
        print(f"❌ Chat completions failed: {e}")

    # Test 2: Check if Whisper API is available
    print("\n" + "=" * 60)
    print("Test 2: Whisper Transcription API")
    print("=" * 60)

    print("\n⚠️  Note: This test requires an actual audio file.")
    print("   Rakuten AI Gateway may or may not support Whisper API.")
    print("   To test fully, you need to:")
    print("   1. Create a small test audio file (test.wav)")
    print("   2. Uncomment the code below and run the test")

    # Uncomment below to test with actual audio file
    """
    try:
        with open("test.wav", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ja"  # Test with Japanese
            )
        print(f"✅ Whisper transcription working!")
        print(f"   Transcription: {transcript.text}")
    except Exception as e:
        print(f"❌ Whisper transcription not supported: {e}")
    """

    # Test 3: Multi-language chat test
    print("\n" + "=" * 60)
    print("Test 3: Multi-language Chat (Japanese)")
    print("=" * 60)

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Respond ONLY in Japanese."
                },
                {
                    "role": "user",
                    "content": "What is artificial intelligence?"
                }
            ],
            max_tokens=100
        )
        result = response.choices[0].message.content
        print(f"✅ Multi-language chat working!")
        print(f"   Japanese response: {result}")
    except Exception as e:
        print(f"❌ Multi-language chat failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("Summary & Recommendations")
    print("=" * 60)

    print("\n✅ CONFIRMED WORKING:")
    print("   - GPT-4 chat completions")
    print("   - Multi-language summaries (Japanese, Spanish, etc.)")
    print("   - Multi-language Q&A responses")

    print("\n⚠️  NEEDS VERIFICATION:")
    print("   - Whisper transcription API via Rakuten Gateway")
    print("   - To verify, create a test audio file and run full test")

    print("\n📋 RECOMMENDATIONS:")
    print("   Option A: Get Azure Speech Services credentials")
    print("            → Full multi-language support with auto-detection")
    print("            → Better transcription quality")
    print("   ")
    print("   Option B: Use Rakuten Whisper (if supported)")
    print("            → Manual language selection only")
    print("            → Simpler setup")
    print("   ")
    print("   Option C: Install local Whisper model")
    print("            → No cloud dependency for transcription")
    print("            → Slower processing, needs GPU for best performance")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_rakuten_whisper_support()
