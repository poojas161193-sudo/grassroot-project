const API_BASE_URL = 'http://localhost:8000';

let currentVideoId = null;
let videoAnalyzer = null;

class VideoAnalyzer {
    constructor() {
        this.progressStages = ['upload', 'extracting', 'transcribing', 'summarizing', 'audio'];
        this.currentStageIndex = 0;
        this.initializeLanguageManager();
        this.initializeEventListeners();
        this.setupDragAndDrop();
        this.setupSuggestionChips();
    }

    async initializeLanguageManager() {
        // Load supported languages from API
        await i18n.loadSupportedLanguages();

        // Set initial UI language
        const savedUILang = i18n.getUILanguage();
        document.getElementById('uiLanguageSelect').value = savedUILang;
        i18n.updateUI();

        // Set initial video language preference
        const savedVideoLang = i18n.getVideoLanguage();
        document.getElementById('videoLanguageSelect').value = savedVideoLang;

        // Setup language change listeners
        document.getElementById('uiLanguageSelect').addEventListener('change', (e) => {
            i18n.setUILanguage(e.target.value);
        });

        document.getElementById('videoLanguageSelect').addEventListener('change', (e) => {
            i18n.setVideoLanguage(e.target.value);
        });
    }

    initializeEventListeners() {
        document.getElementById('fileInput').addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        document.getElementById('askButton').addEventListener('click', () => {
            this.askQuestion();
        });

        document.getElementById('clearChatButton').addEventListener('click', () => {
            this.clearChat();
        });

        document.getElementById('questionInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.askQuestion();
            }
        });
    }

    setupSuggestionChips() {
        const chips = document.querySelectorAll('.chip[data-question-key]');
        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                const questionKey = chip.getAttribute('data-question-key');
                // Get translated question based on current UI language
                const question = i18n.t(questionKey);
                this.askPredefinedQuestion(question);
            });
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.querySelector('.upload-area');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
    }

    async handleFileSelect(file) {
        if (!file) return;

        if (!file.type.startsWith('video/')) {
            this.showError(i18n.t('error') + ': Please select a valid video file.');
            return;
        }

        this.showProgress(true);
        this.hideError();

        // Stage 0: Upload
        this.advanceToStage(0);

        try {
            const formData = new FormData();
            formData.append('file', file);

            // Get selected languages
            const videoLanguage = i18n.getVideoLanguage();
            const uiLanguage = i18n.getUILanguage();

            // Add language parameters to URL
            const url = new URL(`${API_BASE_URL}/upload-video/`);
            url.searchParams.append('language', videoLanguage);
            url.searchParams.append('ui_language', uiLanguage);

            const response = await fetch(url.toString(), {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to upload video');
            }

            const data = await response.json();
            currentVideoId = data.video_id;

            // Upload complete, move to extracting stage
            this.advanceToStage(1); // Extracting audio

            // Poll for processing status
            await this.pollProcessingStatus(currentVideoId);

        } catch (error) {
            console.error('Error uploading video:', error);
            this.showError(`${i18n.t('error')}: ${error.message}`);
            this.showProgress(false);
        }
    }

    async pollProcessingStatus(videoId) {
        const maxAttempts = 60; // Poll for up to 10 minutes (60 * 10 seconds)
        let attempts = 0;
        let lastStage = 1; // Start from extracting (upload is already done)

        const poll = async () => {
            try {
                console.log(`Polling status for video ${videoId}, attempt ${attempts + 1}/${maxAttempts}`);
                const response = await fetch(`${API_BASE_URL}/video-status/${videoId}`);

                if (!response.ok) {
                    throw new Error('Failed to check processing status');
                }

                const data = await response.json();
                console.log('Received status data:', data);

                // Update progress based on attempts (simulate stages)
                if (attempts === 1) {
                    this.advanceToStage(2); // Transcribing
                    lastStage = 2;
                } else if (attempts === 3 && lastStage < 3) {
                    this.advanceToStage(3); // Summarizing
                    lastStage = 3;
                } else if (attempts === 5 && lastStage < 4) {
                    this.advanceToStage(4); // Audio generation
                    lastStage = 4;
                }

                if (data.processing_status === 'completed') {
                    // Processing complete, display results
                    console.log('Processing completed! Summary length:', data.summary ? data.summary.length : 0);
                    this.completeAllStages();

                    setTimeout(() => {
                        this.showProgress(false);
                        this.displayVideoInfo(data);
                        this.showChatSection();
                        this.showSuccess(i18n.t('processingComplete'));
                    }, 1000);
                    return;
                } else if (data.processing_status === 'failed') {
                    // Processing failed
                    console.error('Processing failed:', data.error_message);
                    this.showProgress(false);
                    this.showError(`${i18n.t('error')}: ${data.error_message || 'Unknown error'}`);
                    return;
                } else if (data.processing_status === 'processing' || data.processing_status === 'pending') {
                    // Still processing, continue polling
                    attempts++;
                    if (attempts < maxAttempts) {
                        setTimeout(poll, 5000); // Poll every 5 seconds
                    } else {
                        console.error('Processing timeout after', attempts, 'attempts');
                        this.showProgress(false);
                        this.showError('Processing timeout. Please refresh and try again.');
                    }
                }
            } catch (error) {
                console.error('Error checking status:', error);
                this.showProgress(false);
                this.showError('Failed to check processing status. Please refresh.');
            }
        };

        // Start polling
        poll();
    }

    async askQuestion() {
        if (!currentVideoId) {
            this.showError('Please upload a video first.');
            return;
        }

        const questionInput = document.getElementById('questionInput');
        const question = questionInput.value.trim();

        if (!question) {
            this.showError('Please enter a question.');
            return;
        }

        this.addMessageToChat(question, 'user');
        questionInput.value = '';

        this.addLoadingMessage();

        try {
            // Add UI language parameter to URL
            const url = new URL(`${API_BASE_URL}/ask-question/`);
            url.searchParams.append('ui_language', i18n.getUILanguage());

            const response = await fetch(url.toString(), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    video_id: currentVideoId,
                    question: question
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to get answer');
            }

            const data = await response.json();
            this.removeLoadingMessage();
            this.addMessageToChat(data.answer, 'ai');

        } catch (error) {
            console.error('Error asking question:', error);
            this.removeLoadingMessage();
            this.addMessageToChat(`${i18n.t('error')}: ${error.message}`, 'ai error');
        }
    }

    displayVideoInfo(data) {
        console.log('Displaying video info:', data);
        const videoInfo = document.getElementById('videoInfo');
        const videoDetails = document.getElementById('videoDetails');
        const videoSummary = document.getElementById('videoSummary');

        // Escape HTML and preserve line breaks
        const escapedFilename = this.escapeHtml(data.filename || 'Unknown file');
        const summaryText = data.summary || 'No summary available';
        const escapedSummary = this.escapeHtml(summaryText).replace(/\n/g, '<br>');

        // Build video details section with language information
        let detailsHTML = `<p><strong>${i18n.t('filename')}</strong> ${escapedFilename}</p>`;

        if (data.detected_language) {
            const langDisplay = i18n.getLanguageDisplay(data.detected_language) || data.detected_language;
            detailsHTML += `<p><strong>${i18n.t('detectedLanguage')}</strong> ${langDisplay}</p>`;
        }

        if (data.transcription_method) {
            detailsHTML += `<p><strong>${i18n.t('transcriptionMethod')}</strong> ${data.transcription_method}</p>`;
        }

        videoDetails.innerHTML = detailsHTML;
        videoSummary.innerHTML = `<p style="line-height: 1.6; white-space: pre-wrap;">${escapedSummary}</p>`;

        // Handle audio summary if available
        if (data.audio_summary_path && data.audio_summary_duration) {
            const audioSection = document.getElementById('audioSummarySection');
            const audioPlayer = document.getElementById('audioPlayer');
            const audioDuration = document.getElementById('audioDuration');

            // Set audio source
            audioPlayer.src = `${API_BASE_URL}/audio-summary/${currentVideoId}`;

            // Display duration
            const minutes = Math.floor(data.audio_summary_duration / 60);
            const seconds = Math.floor(data.audio_summary_duration % 60);
            audioDuration.textContent = `Duration: ${minutes}:${seconds.toString().padStart(2, '0')}`;

            // Show audio section
            audioSection.style.display = 'block';
            console.log('Audio summary loaded:', audioPlayer.src);
        } else {
            // Hide audio section if no audio summary
            document.getElementById('audioSummarySection').style.display = 'none';
        }

        videoInfo.style.display = 'block';

        // Show suggestion chips only if processing is complete
        if (data.summary) {
            console.log('Showing suggestion chips');
            document.getElementById('suggestionChips').style.display = 'block';
        } else {
            console.warn('No summary in data:', data);
        }
    }

    showChatSection() {
        document.getElementById('chatSection').style.display = 'block';
        document.getElementById('questionInput').focus();
    }

    async askPredefinedQuestion(question) {
        if (!currentVideoId) {
            this.showError('Please upload a video first.');
            return;
        }

        // Show chat section if not already visible
        this.showChatSection();

        // Add user question to chat
        this.addMessageToChat(question, 'user');

        this.addLoadingMessage();

        try {
            // Add UI language parameter to URL
            const url = new URL(`${API_BASE_URL}/ask-question/`);
            const uiLanguage = i18n.getUILanguage();
            url.searchParams.append('ui_language', uiLanguage);

            const response = await fetch(url.toString(), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    video_id: currentVideoId,
                    question: question
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to get answer');
            }

            const data = await response.json();
            this.removeLoadingMessage();
            this.addMessageToChat(data.answer, 'ai');

        } catch (error) {
            console.error('Error asking question:', error);
            this.removeLoadingMessage();
            this.addMessageToChat(`${i18n.t('error')}: ${error.message}`, 'ai error');
        }
    }

    enableCustomQuestion() {
        this.showChatSection();

        // Scroll to chat section
        document.getElementById('chatSection').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }

    addMessageToChat(message, type) {
        const chatHistory = document.getElementById('chatHistory');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        if (type === 'user') {
            messageDiv.innerHTML = `<strong>You:</strong> ${this.escapeHtml(message)}`;
        } else if (type === 'ai error') {
            messageDiv.innerHTML = `<strong>AI:</strong> <span style="color: #cc0000;">${this.escapeHtml(message)}</span>`;
            messageDiv.className = 'message ai-message';
        } else {
            const formattedMessage = this.formatMarkdown(message);
            messageDiv.innerHTML = `<strong>AI:</strong><div class="ai-response-content">${formattedMessage}</div>`;
        }

        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatMarkdown(text) {
        // Replace horizontal rules
        text = text.replace(/^---+$/gm, '<hr class="separator">');

        // Replace headers (### header)
        text = text.replace(/^###\s+(.+)$/gm, '<h3 class="md-h3">$1</h3>');
        text = text.replace(/^##\s+(.+)$/gm, '<h2 class="md-h2">$1</h2>');
        text = text.replace(/^#\s+(.+)$/gm, '<h1 class="md-h1">$1</h1>');

        // Replace bold text (**text**)
        text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Replace italic text (*text*)
        text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Replace inline code (`code`)
        text = text.replace(/`(.+?)`/g, '<code class="inline-code">$1</code>');

        // Replace code blocks (```code```)
        text = text.replace(/```([\s\S]+?)```/g, '<pre class="code-block"><code>$1</code></pre>');

        // Convert line breaks to <br> but preserve paragraph structure
        text = text.split('\n\n').map(para => {
            if (!para.trim().startsWith('<') && para.trim() !== '') {
                return '<p>' + para.replace(/\n/g, '<br>') + '</p>';
            }
            return para.replace(/\n/g, '<br>');
        }).join('');

        return text;
    }

    addLoadingMessage() {
        const chatHistory = document.getElementById('chatHistory');
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message ai-message loading-message';
        loadingDiv.innerHTML = '<strong>AI:</strong> <span class="loading-dots">Thinking...</span>';
        chatHistory.appendChild(loadingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    removeLoadingMessage() {
        const loadingMessage = document.querySelector('.loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }

    showProgress(show) {
        const progressContainer = document.getElementById('progressContainer');
        const uploadArea = document.querySelector('.upload-area');

        if (show) {
            progressContainer.style.display = 'block';
            uploadArea.style.opacity = '0.5';
            uploadArea.style.pointerEvents = 'none';
            this.resetProgress();
        } else {
            progressContainer.style.display = 'none';
            uploadArea.style.opacity = '1';
            uploadArea.style.pointerEvents = 'auto';
        }
    }

    resetProgress() {
        this.currentStageIndex = 0;
        this.updateProgress(0);

        // Reset progress icon and text
        document.getElementById('progressIcon').textContent = '⏳';
        document.getElementById('progressText').textContent = i18n.t('processing') || 'Processing Video';
    }

    updateProgress(percentage) {
        const progressBar = document.getElementById('progressBar');
        const progressPercentage = document.getElementById('progressPercentage');

        progressBar.style.width = percentage + '%';
        progressPercentage.textContent = Math.round(percentage) + '%';
    }

    setStage(stageName, status) {
        // Stage elements removed - keeping method for compatibility
        // Progress is now tracked only via progress bar percentage
    }

    advanceToStage(stageIndex) {
        // Update progress bar based on stage (each stage is 20%)
        if (stageIndex < this.progressStages.length) {
            this.currentStageIndex = stageIndex;
            const progress = (stageIndex / this.progressStages.length) * 100;
            this.updateProgress(progress);
        }
    }

    completeAllStages() {
        this.updateProgress(100);
        document.getElementById('progressIcon').textContent = '✅';
        document.getElementById('progressText').textContent = i18n.t('completed') || 'Processing Complete!';
    }

    showLoading(show, message) {
        // Keep for compatibility, but redirect to progress indicator
        if (show) {
            this.showProgress(true);
        } else {
            this.showProgress(false);
        }
    }

    showError(message) {
        this.removeError();
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = message;
        errorDiv.id = 'errorMessage';
        document.querySelector('.upload-section').appendChild(errorDiv);
    }

    showSuccess(message) {
        this.removeError();
        const successDiv = document.createElement('div');
        successDiv.className = 'success';
        successDiv.textContent = message;
        successDiv.id = 'successMessage';
        document.querySelector('.upload-section').appendChild(successDiv);
        
        setTimeout(() => {
            this.removeError();
        }, 5000);
    }

    hideError() {
        this.removeError();
    }

    removeError() {
        const existingError = document.getElementById('errorMessage');
        const existingSuccess = document.getElementById('successMessage');
        if (existingError) existingError.remove();
        if (existingSuccess) existingSuccess.remove();
    }

    clearChat() {
        const chatHistory = document.getElementById('chatHistory');
        if (confirm(i18n.t('clearChatConfirm'))) {
            chatHistory.innerHTML = '';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    videoAnalyzer = new VideoAnalyzer();
});

const style = document.createElement('style');
style.textContent = `
    .loading-dots::after {
        content: '';
        display: inline-block;
        animation: dots 1.5s infinite;
    }

    @keyframes dots {
        0%, 20% { content: '.'; }
        40% { content: '..'; }
        60% { content: '...'; }
        80%, 100% { content: ''; }
    }
`;
document.head.appendChild(style);