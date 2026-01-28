// Course Manager JavaScript
// Handles course listing, filtering, deletion, and bulk cleanup
// Version: 2026-01-28 v2 - Bulk cleanup fully working

const API_BASE_URL = 'http://localhost:8000';

let allCourses = [];
let courseToDelete = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadCourses();
    loadStorageStats();

    // Setup event listeners
    document.getElementById('searchInput').addEventListener('input', filterCourses);
    document.getElementById('languageFilter').addEventListener('change', filterCourses);
    document.getElementById('themeFilter').addEventListener('change', filterCourses);
});

// Load all courses from API
async function loadCourses() {
    showLoading(true);
    hideAlert();

    try {
        const response = await fetch(`${API_BASE_URL}/api/courses`);

        if (!response.ok) {
            throw new Error('Failed to load courses');
        }

        const data = await response.json();
        allCourses = data.courses;

        console.log('Loaded courses:', allCourses);
        console.log('First course (if exists):', allCourses[0]);

        // Update statistics
        document.getElementById('totalCourses').textContent = data.total_courses;
        document.getElementById('totalStorage').textContent = `${data.total_storage_mb} MB`;

        // Calculate total slides and questions
        const totalSlides = allCourses.reduce((sum, course) => sum + (course.total_slides || 0), 0);
        const totalQuestions = allCourses.reduce((sum, course) => sum + (course.total_questions || 0), 0);

        document.getElementById('totalSlides').textContent = totalSlides;
        document.getElementById('totalQuestions').textContent = totalQuestions;

        // Display courses
        displayCourses(allCourses);

    } catch (error) {
        console.error('Error loading courses:', error);
        showAlert('Failed to load courses. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

// Load storage statistics
async function loadStorageStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/courses/storage-stats`);

        if (response.ok) {
            const stats = await response.json();
            console.log('Storage Statistics:', stats);
        }
    } catch (error) {
        console.error('Error loading storage stats:', error);
    }
}

// Display courses in table
function displayCourses(courses) {
    const tbody = document.getElementById('coursesTableBody');
    const emptyState = document.getElementById('emptyState');
    const tableContainer = document.getElementById('tableContainer');

    if (courses.length === 0) {
        tableContainer.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    tableContainer.style.display = 'block';
    emptyState.style.display = 'none';

    tbody.innerHTML = courses.map(course => `
        <tr>
            <td>
                <div class="course-title">${escapeHtml(course.title)}</div>
                <div class="course-desc">${escapeHtml(course.description || 'No description')}</div>
            </td>
            <td>
                <span class="badge badge-language">
                    ${course.language === 'en' ? '🇺🇸 English' : '🇯🇵 Japanese'}
                </span>
            </td>
            <td>
                <span class="badge badge-theme">
                    ${getThemeIcon(course.theme)} ${capitalizeFirst(course.theme)}
                </span>
            </td>
            <td>${course.total_slides || 0}</td>
            <td>${course.total_questions || 0}</td>
            <td>${course.storage_mb} MB</td>
            <td>${formatDate(course.created_at)}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-secondary btn-small view-course-btn" data-course-id="${escapeHtml(course.course_id)}" title="View Course">
                        View
                    </button>
                    <button class="btn btn-danger btn-small delete-course-btn" data-course-id="${escapeHtml(course.course_id)}" data-course-title="${escapeHtml(course.title)}" title="Delete Course">
                        Delete
                    </button>
                </div>
            </td>
        </tr>
    `).join('');

    // Add event listeners for view buttons
    document.querySelectorAll('.view-course-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            viewCourse(courseId);
        });
    });

    // Add event listeners for delete buttons
    document.querySelectorAll('.delete-course-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const courseId = this.getAttribute('data-course-id');
            const courseTitle = this.getAttribute('data-course-title');
            openDeleteModal(courseId, courseTitle);
        });
    });
}

// Filter courses based on search and filters
function filterCourses() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const languageFilter = document.getElementById('languageFilter').value;
    const themeFilter = document.getElementById('themeFilter').value;

    const filteredCourses = allCourses.filter(course => {
        // Search filter
        const matchesSearch = !searchTerm ||
            course.title.toLowerCase().includes(searchTerm) ||
            (course.description && course.description.toLowerCase().includes(searchTerm));

        // Language filter
        const matchesLanguage = !languageFilter || course.language === languageFilter;

        // Theme filter
        const matchesTheme = !themeFilter || course.theme === themeFilter;

        return matchesSearch && matchesLanguage && matchesTheme;
    });

    displayCourses(filteredCourses);
}

// View course
function viewCourse(courseId) {
    window.open(`${API_BASE_URL}/course-files/${courseId}/index.html`, '_blank');
}

// Open delete modal
function openDeleteModal(courseId, courseTitle) {
    console.log('Opening delete modal for:', { courseId, courseTitle });
    courseToDelete = courseId;
    document.getElementById('deleteCourseTitle').textContent = courseTitle;
    document.getElementById('deleteModal').classList.add('show');
}

// Close delete modal
function closeDeleteModal() {
    courseToDelete = null;
    document.getElementById('deleteModal').classList.remove('show');
}

// Confirm delete
async function confirmDelete() {
    if (!courseToDelete) return;

    const deleteUrl = `${API_BASE_URL}/api/course/${courseToDelete}`;
    console.log('Deleting course with URL:', deleteUrl);
    console.log('Course ID to delete:', courseToDelete);

    closeDeleteModal();
    showLoading(true);
    hideAlert();

    try {
        const response = await fetch(deleteUrl, {
            method: 'DELETE'
        });

        console.log('Delete response status:', response.status);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            console.error('Delete error response:', errorData);
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Delete success:', data);
        showAlert(`Successfully deleted: ${data.title}`, 'success');

        // Reload courses
        await loadCourses();
        await loadStorageStats();

    } catch (error) {
        console.error('Error deleting course:', error);
        showAlert(`Failed to delete course: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Open cleanup modal
function openCleanupModal() {
    document.getElementById('cleanupModal').classList.add('show');
}

// Close cleanup modal
function closeCleanupModal() {
    document.getElementById('cleanupModal').classList.remove('show');
}

// Confirm bulk cleanup
async function confirmCleanup() {
    console.log('=== BULK CLEANUP STARTED ===');
    const days = parseInt(document.getElementById('cleanupDays').value);

    console.log('Cleanup days value:', days);

    if (!days || days < 1) {
        showAlert('Please enter a valid number of days (minimum 1).', 'error');
        return;
    }

    const cleanupUrl = `${API_BASE_URL}/api/courses/cleanup?days=${days}`;
    console.log('Cleanup URL:', cleanupUrl);

    closeCleanupModal();
    showLoading(true);
    hideAlert();

    try {
        const response = await fetch(cleanupUrl, {
            method: 'POST'
        });

        console.log('Cleanup response status:', response.status);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            console.error('Cleanup error response:', errorData);
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Cleanup success:', data);
        console.log(`Deleted ${data.deleted_courses} courses, freed ${data.freed_space_mb} MB`);

        if (data.deleted_courses === 0) {
            showAlert(`✓ No courses found older than ${days} days.`, 'success');
        } else {
            showAlert(
                `✓ Successfully deleted ${data.deleted_courses} course(s) older than ${days} days. ` +
                `Freed ${data.freed_space_mb} MB of storage.`,
                'success'
            );
        }

        console.log('Reloading courses and statistics...');
        // Reload courses
        await loadCourses();
        await loadStorageStats();
        console.log('=== BULK CLEANUP COMPLETED ===');

    } catch (error) {
        console.error('=== BULK CLEANUP FAILED ===');
        console.error('Error during cleanup:', error);
        console.error('Error message:', error.message);
        showAlert(`❌ Failed to cleanup courses: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Refresh courses
async function refreshCourses() {
    await loadCourses();
    await loadStorageStats();
    showAlert('Courses refreshed successfully!', 'success');

    // Auto-hide success message after 3 seconds
    setTimeout(() => {
        hideAlert();
    }, 3000);
}

// Show/hide loading state
function showLoading(show) {
    const loadingState = document.getElementById('loadingState');
    const tableContainer = document.getElementById('tableContainer');

    if (show) {
        loadingState.classList.add('show');
        tableContainer.style.display = 'none';
    } else {
        loadingState.classList.remove('show');
    }
}

// Show alert message
function showAlert(message, type) {
    hideAlert();

    const alertId = type === 'success' ? 'successAlert' : 'errorAlert';
    const alertElement = document.getElementById(alertId);

    alertElement.textContent = message;
    alertElement.classList.add('show');

    // Scroll to top to ensure alert is visible
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Auto-hide messages after appropriate time
    if (type === 'error') {
        setTimeout(() => {
            hideAlert();
        }, 5000);
    } else {
        // Auto-hide success messages after 8 seconds
        setTimeout(() => {
            hideAlert();
        }, 8000);
    }
}

// Hide all alerts
function hideAlert() {
    document.getElementById('successAlert').classList.remove('show');
    document.getElementById('errorAlert').classList.remove('show');
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function getThemeIcon(theme) {
    const icons = {
        'light': '☀️',
        'dark': '🌙',
        'corporate': '💼'
    };
    return icons[theme] || '🎨';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
        return 'Today';
    } else if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else if (diffDays < 30) {
        const weeks = Math.floor(diffDays / 7);
        return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    } else if (diffDays < 365) {
        const months = Math.floor(diffDays / 30);
        return `${months} month${months > 1 ? 's' : ''} ago`;
    } else {
        const years = Math.floor(diffDays / 365);
        return `${years} year${years > 1 ? 's' : ''} ago`;
    }
}
