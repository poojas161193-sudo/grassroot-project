/**
 * Multi-language translations for Video Analyzer AI
 * Supports English (en) and Japanese (ja)
 */

const translations = {
    en: {
        // Header
        appTitle: "Video Analyzer AI",
        appSubtitle: "Upload, Transcribe, Analyze with AI",

        // Language selector
        interfaceLanguage: "Interface Language:",
        videoLanguage: "Video Language:",
        autoDetect: "Auto-detect",

        // Upload section
        uploadTitle: "Upload Video",
        uploadText: "Drag and drop video here or click to browse",
        uploadHint: "Supports MP4, AVI, MOV, and more",
        uploading: "Uploading video...",
        processing: "Processing video... This may take a few minutes.",

        // Video info
        filename: "Filename:",
        detectedLanguage: "Detected Language:",
        transcriptionMethod: "Transcription Method:",
        summary: "Summary",
        audioSummary: "Audio Summary",

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

        // Quick action questions (full text)
        create10QAQuestion: "Create 10 Question-Answer pairs from the video content",
        keyPointsQuestion: "List 10 key highlighted points from the video",
        detailedSummaryQuestion: "Provide a detailed summary of the video",

        // Status messages
        uploadSuccess: "Video uploaded successfully!",
        processingInBackground: "Processing in background...",
        processingComplete: "Processing complete!",
        languageDetected: "Language detected:",
        error: "Error",

        // Buttons
        cancel: "Cancel",
        ok: "OK",

        // Language names
        english: "English",
        japanese: "Japanese"
    },

    ja: {
        // ヘッダー
        appTitle: "ビデオ分析AI",
        appSubtitle: "アップロード、文字起こし、AI分析",

        // 言語選択
        interfaceLanguage: "インターフェース言語:",
        videoLanguage: "ビデオの言語:",
        autoDetect: "自動検出",

        // アップロードセクション
        uploadTitle: "ビデオをアップロード",
        uploadText: "ビデオをここにドラッグ＆ドロップまたはクリックして選択",
        uploadHint: "MP4、AVI、MOVなどをサポート",
        uploading: "ビデオをアップロード中...",
        processing: "ビデオを処理中...数分かかる場合があります。",

        // ビデオ情報
        filename: "ファイル名:",
        detectedLanguage: "検出された言語:",
        transcriptionMethod: "文字起こし方法:",
        summary: "要約",
        audioSummary: "音声要約",

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

        // クイックアクションの質問（全文）
        create10QAQuestion: "ビデオコンテンツから10個の質問と回答のペアを作成してください",
        keyPointsQuestion: "ビデオから10個の重要なポイントをリストアップしてください",
        detailedSummaryQuestion: "ビデオの詳細な要約を提供してください",

        // ステータスメッセージ
        uploadSuccess: "ビデオが正常にアップロードされました！",
        processingInBackground: "バックグラウンドで処理中...",
        processingComplete: "処理が完了しました！",
        languageDetected: "検出された言語:",
        error: "エラー",

        // ボタン
        cancel: "キャンセル",
        ok: "OK",

        // 言語名
        english: "英語",
        japanese: "日本語"
    }
};

/**
 * Language Manager Class
 * Handles language switching and UI updates
 */
class LanguageManager {
    constructor() {
        this.currentUILanguage = localStorage.getItem('uiLanguage') || 'en';
        this.currentVideoLanguage = localStorage.getItem('videoLanguage') || 'auto';
        this.supportedLanguages = null;
    }

    /**
     * Load supported languages from API
     */
    async loadSupportedLanguages() {
        try {
            const response = await fetch(`${API_BASE_URL}/supported-languages/`);
            const data = await response.json();
            this.supportedLanguages = data.languages;
            return this.supportedLanguages;
        } catch (error) {
            console.error('Failed to load supported languages:', error);
            // Fallback to hardcoded languages
            this.supportedLanguages = {
                'en': {
                    'name': 'English',
                    'native_name': 'English',
                    'flag': '🇺🇸',
                    'enabled': true
                },
                'ja': {
                    'name': 'Japanese',
                    'native_name': '日本語',
                    'flag': '🇯🇵',
                    'enabled': true
                }
            };
            return this.supportedLanguages;
        }
    }

    /**
     * Set UI language and update interface
     */
    setUILanguage(lang) {
        this.currentUILanguage = lang;
        localStorage.setItem('uiLanguage', lang);
        this.updateUI();
        document.documentElement.lang = lang;
    }

    /**
     * Set video language preference
     */
    setVideoLanguage(lang) {
        this.currentVideoLanguage = lang;
        localStorage.setItem('videoLanguage', lang);
    }

    /**
     * Get current UI language
     */
    getUILanguage() {
        return this.currentUILanguage;
    }

    /**
     * Get current video language preference
     */
    getVideoLanguage() {
        return this.currentVideoLanguage;
    }

    /**
     * Translate a key to current language
     */
    t(key) {
        return translations[this.currentUILanguage]?.[key] || translations['en'][key] || key;
    }

    /**
     * Update all UI elements with translations
     */
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

    /**
     * Get language display name with flag
     */
    getLanguageDisplay(langCode) {
        if (this.supportedLanguages && this.supportedLanguages[langCode]) {
            const lang = this.supportedLanguages[langCode];
            return `${lang.flag} ${lang.native_name}`;
        }
        return langCode;
    }
}

// Initialize global language manager
const i18n = new LanguageManager();
