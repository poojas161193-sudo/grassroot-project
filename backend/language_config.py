"""
Multi-language configuration and utilities
Supports English (default) and Japanese
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
    }
}

DEFAULT_LANGUAGE = 'en'
DEFAULT_UI_LANGUAGE = 'en'


def get_azure_language_code(lang_code: str) -> str:
    """
    Get Azure Speech Services language code from ISO 639-1 code

    Args:
        lang_code: ISO 639-1 code ('en', 'ja')

    Returns:
        Azure language code ('en-US', 'ja-JP')
    """
    return SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES['en'])['azure_code']


def get_whisper_language_code(lang_code: str) -> str:
    """
    Get Whisper language code from ISO 639-1 code

    Args:
        lang_code: ISO 639-1 code ('en', 'ja')

    Returns:
        Whisper language code ('en', 'ja')
    """
    return SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES['en'])['whisper_code']


def get_language_name(lang_code: str) -> str:
    """
    Get language native name

    Args:
        lang_code: ISO 639-1 code ('en', 'ja')

    Returns:
        Native language name ('English', '日本語')
    """
    return SUPPORTED_LANGUAGES.get(lang_code, SUPPORTED_LANGUAGES['en'])['native_name']


def is_language_supported(lang_code: str) -> bool:
    """
    Check if language is supported

    Args:
        lang_code: ISO 639-1 code to check

    Returns:
        True if supported, False otherwise
    """
    return lang_code in SUPPORTED_LANGUAGES and SUPPORTED_LANGUAGES[lang_code]['enabled']


def get_enabled_languages() -> dict:
    """
    Get all enabled languages

    Returns:
        Dictionary of enabled languages
    """
    return {k: v for k, v in SUPPORTED_LANGUAGES.items() if v['enabled']}


# Language detection candidates for Azure Speech
# Azure supports max 4 candidates at once, we only have 2
AZURE_LANGUAGE_CANDIDATES = [
    lang['azure_code'] for lang in SUPPORTED_LANGUAGES.values() if lang['enabled']
]
