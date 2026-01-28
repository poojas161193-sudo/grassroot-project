"""
Multi-language configuration and utilities
Supports English (default) and Japanese
"""

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': {
        'name': 'English',
        'native_name': 'English',
        'flag': '🇺🇸',
        'enabled': True
    },
    'ja': {
        'name': 'Japanese',
        'native_name': '日本語',
        'flag': '🇯🇵',
        'enabled': True
    }
}

DEFAULT_LANGUAGE = 'en'
DEFAULT_UI_LANGUAGE = 'en'


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
