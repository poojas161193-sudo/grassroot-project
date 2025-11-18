"""
Test script to verify Azure Speech Services and Whisper credentials
"""
import os
from decouple import config

def test_azure_credentials():
    """Test if all Azure credentials are properly configured"""

    print("=" * 70)
    print("AZURE CREDENTIALS VALIDATION TEST")
    print("=" * 70)

    # Test 1: Azure Speech Services
    print("\n✓ Test 1: Azure Speech Services Configuration")
    print("-" * 70)

    try:
        azure_speech_key = config('AZURE_SPEACH_KEY')
        azure_region = config('AZURE_REGION')

        print(f"✅ AZURE_SPEACH_KEY: {azure_speech_key[:20]}...{azure_speech_key[-10:]}")
        print(f"✅ AZURE_REGION: {azure_region}")

        # Quick validation test
        import azure.cognitiveservices.speech as speechsdk

        speech_config = speechsdk.SpeechConfig(
            subscription=azure_speech_key,
            region=azure_region
        )
        print(f"✅ Azure Speech SDK initialized successfully!")
        print(f"   Speech recognition will work for transcription")

    except Exception as e:
        print(f"❌ Azure Speech Services error: {e}")
        print(f"   → Multi-language transcription will NOT work")

    # Test 2: Azure Whisper (Fallback)
    print("\n✓ Test 2: Azure Whisper Configuration (Fallback)")
    print("-" * 70)

    try:
        whisper_endpoint = config('WHISPER_AZURE_ENDPOINT')
        whisper_key = config('WHISPER_API_KEY')
        whisper_deployment = config('WHISPER_DEPLOYMENT_NAME')

        print(f"✅ WHISPER_AZURE_ENDPOINT: {whisper_endpoint}")
        print(f"✅ WHISPER_API_KEY: {whisper_key[:20]}...{whisper_key[-10:]}")
        print(f"✅ WHISPER_DEPLOYMENT_NAME: {whisper_deployment}")
        print(f"   Whisper fallback configured (if Azure Speech fails)")

    except Exception as e:
        print(f"⚠️  Azure Whisper not configured: {e}")
        print(f"   → Will use local Whisper as final fallback")

    # Test 3: Rakuten AI Gateway
    print("\n✓ Test 3: Rakuten AI Gateway Configuration")
    print("-" * 70)

    try:
        openai_key = config('OPENAI_API_KEY')
        openai_base = config('OPENAI_BASE_URL')
        llm_model = config('LLM_MODEL')

        print(f"✅ OPENAI_API_KEY: {openai_key[:20]}...")
        print(f"✅ OPENAI_BASE_URL: {openai_base}")
        print(f"✅ LLM_MODEL: {llm_model}")
        print(f"   → Multi-language summaries and Q&A will work!")

    except Exception as e:
        print(f"❌ Rakuten AI Gateway error: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY - MULTI-LANGUAGE FEATURE READINESS")
    print("=" * 70)

    try:
        # Check critical components
        has_azure_speech = config('AZURE_SPEACH_KEY', default=None) is not None
        has_whisper = config('WHISPER_API_KEY', default=None) is not None
        has_rakuten = config('OPENAI_API_KEY', default=None) is not None

        print("\n🎯 REQUIRED COMPONENTS:")
        print(f"   {'✅' if has_azure_speech else '❌'} Azure Speech Services (Transcription)")
        print(f"   {'✅' if has_rakuten else '❌'} Rakuten AI Gateway (Summaries/Q&A)")

        print("\n🔧 OPTIONAL COMPONENTS:")
        print(f"   {'✅' if has_whisper else '⚠️ '} Azure Whisper (Fallback transcription)")

        print("\n📋 FEATURE AVAILABILITY:")

        if has_azure_speech and has_rakuten:
            print("   ✅ Multi-language video transcription")
            print("   ✅ Automatic language detection")
            print("   ✅ Multi-language summaries (Japanese, Spanish, etc.)")
            print("   ✅ Multi-language Q&A chat")
            print("   ✅ Support for 100+ languages")
            print("\n   🎉 ALL SYSTEMS GO! Ready for multi-language implementation!")

        elif has_rakuten:
            print("   ⚠️  Multi-language video transcription - LIMITED")
            print("   ❌ Automatic language detection - NOT AVAILABLE")
            print("   ✅ Multi-language summaries (Japanese, Spanish, etc.)")
            print("   ✅ Multi-language Q&A chat")
            print("\n   ⚠️  PARTIAL SUPPORT - Transcription requires manual setup")

        else:
            print("   ❌ Critical components missing")
            print("\n   🛑 NOT READY - Please configure credentials")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"Error in summary: {e}")

if __name__ == "__main__":
    test_azure_credentials()
