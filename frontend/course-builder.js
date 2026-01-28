/**
 * Course Builder JavaScript
 * Handles course generation from processed videos
 */

const API_BASE_URL = 'http://localhost:8000';
let selectedVideoId = null;
let generatedCourseId = null;

// Load videos on page load
document.addEventListener('DOMContentLoaded', () => {
    loadVideos();
    setupThemeSelection();
});

/**
 * Setup theme card selection interaction
 */
function setupThemeSelection() {
    const themeCards = document.querySelectorAll('.theme-card');
    themeCards.forEach(card => {
        card.addEventListener('click', () => {
            themeCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            const radio = card.querySelector('input[type="radio"]');
            radio.checked = true;
        });
    });
}

/**
 * Load available processed videos from the API
 */
async function loadVideos() {
    try {
        const response = await fetch(`${API_BASE_URL}/videos/`);
        const videos = await response.json();

        const select = document.getElementById('videoSelect');

        // Filter only completed videos
        const completedVideos = videos.filter(v => v.processing_status === 'completed');

        if (completedVideos.length === 0) {
            select.innerHTML = '<option value="">No processed videos available</option>';
            return;
        }

        select.innerHTML = '<option value="">-- Select a video --</option>';
        completedVideos.forEach(video => {
            const option = document.createElement('option');
            option.value = video.id;
            option.textContent = `${video.filename} (${video.detected_language || 'Unknown'})`;
            option.dataset.video = JSON.stringify(video);
            select.appendChild(option);
        });

        select.addEventListener('change', onVideoSelected);
    } catch (error) {
        console.error('Error loading videos:', error);
        showError('Failed to load videos. Please refresh the page.');
    }
}

/**
 * Handle video selection change
 */
function onVideoSelected(event) {
    const select = event.target;
    const selectedOption = select.options[select.selectedIndex];

    if (!selectedOption.value) {
        document.getElementById('videoInfo').classList.remove('show');
        selectedVideoId = null;
        return;
    }

    selectedVideoId = selectedOption.value;
    const video = JSON.parse(selectedOption.dataset.video);

    // Display video info
    document.getElementById('videoFilename').textContent = video.filename;
    document.getElementById('videoLanguage').textContent = video.detected_language || 'Unknown';
    document.getElementById('videoSummary').textContent = video.summary || 'No summary available';
    document.getElementById('videoInfo').classList.add('show');
}

/**
 * Generate complete course from selected video
 */
async function generateCourse() {
    // Validation
    if (!selectedVideoId) {
        showError('Please select a video first.');
        return;
    }

    const theme = document.querySelector('input[name="theme"]:checked').value;
    const language = document.getElementById('languageSelect').value;
    const numQuestions = parseInt(document.getElementById('numQuestions').value);

    if (numQuestions < 5 || numQuestions > 50) {
        showError('Number of questions must be between 5 and 50.');
        return;
    }

    // Hide error, show progress
    hideError();
    document.getElementById('generateBtn').disabled = true;
    document.getElementById('progressSection').classList.add('show');
    document.getElementById('resultSection').classList.remove('show');

    // Animate progress steps
    animateProgressSteps();

    try {
        const response = await fetch(`${API_BASE_URL}/api/course/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_id: parseInt(selectedVideoId),
                language: language,
                theme: theme,
                num_questions: numQuestions
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate course');
        }

        const result = await response.json();
        generatedCourseId = result.course_id;

        // Show results
        showResults(result);

    } catch (error) {
        console.error('Error generating course:', error);
        showError(`Failed to generate course: ${error.message}`);
        document.getElementById('progressSection').classList.remove('show');
    } finally {
        document.getElementById('generateBtn').disabled = false;
    }
}

/**
 * Animate progress steps during course generation
 */
function animateProgressSteps() {
    const steps = ['step1', 'step2', 'step3', 'step4'];
    let currentStep = 0;

    const interval = setInterval(() => {
        if (currentStep < steps.length) {
            document.getElementById(steps[currentStep]).classList.add('active');
            if (currentStep > 0) {
                document.getElementById(steps[currentStep - 1]).classList.remove('active');
                document.getElementById(steps[currentStep - 1]).classList.add('completed');
            }
            currentStep++;
        } else {
            clearInterval(interval);
            // Mark last step as completed
            document.getElementById(steps[steps.length - 1]).classList.remove('active');
            document.getElementById(steps[steps.length - 1]).classList.add('completed');
        }
    }, 1500);

    // Store interval ID to clear if needed
    window.progressInterval = interval;
}

/**
 * Show course generation results
 */
function showResults(result) {
    // Clear progress interval
    if (window.progressInterval) {
        clearInterval(window.progressInterval);
    }

    document.getElementById('progressSection').classList.remove('show');
    document.getElementById('resultSection').classList.add('show');

    // Update result info
    document.getElementById('courseTitle').textContent = result.course_title;
    document.getElementById('courseStats').textContent =
        `${result.total_slides} Slides • ${result.total_questions} Questions`;

    // Setup action buttons
    const courseId = result.course_id;
    document.getElementById('viewCourseBtn').href = `${API_BASE_URL}/course-files/${courseId}/index.html`;
    document.getElementById('viewSlidesBtn').href = `${API_BASE_URL}/course-files/${courseId}/slides.html`;
    document.getElementById('takeQuizBtn').href = `${API_BASE_URL}/course-files/${courseId}/quiz.html`;
    document.getElementById('downloadBtn').href = `${API_BASE_URL}/api/course/${courseId}/export`;
}

/**
 * Display error message
 */
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
}

/**
 * Hide error message
 */
function hideError() {
    document.getElementById('errorMessage').classList.remove('show');
}
