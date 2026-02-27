/**
 * API Client for NFC Attendance System
 */

const API_BASE_URL = window.location.origin;

class APIClient {
    /**
     * Make API request
     */
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);

            // Check content type before parsing
            const contentType = response.headers.get('content-type');
            let data;

            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                // If not JSON, get text and create error
                const text = await response.text();
                console.error('Non-JSON response:', text);
                throw new Error(`Server returned non-JSON response. Status: ${response.status}`);
            }

            if (!response.ok) {
                throw new Error(data.error || `Request failed with status ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Student APIs
    static async getStudents(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/api/students?${params}`);
    }

    static async getStudent(id) {
        return this.request(`/api/students/${id}`);
    }

    static async createStudent(data) {
        return this.request('/api/students', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async uploadStudents(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/students/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Check for errors - handle both status code and error field
        if (!response.ok || data.error) {
            throw new Error(data.error || `Upload failed with status ${response.status}`);
        }

        return data;
    }

    static async deleteStudent(id) {
        return this.request(`/api/students/${id}`, {
            method: 'DELETE'
        });
    }

    // NFC APIs
    static async registerNFC(studentId, nfcTagId) {
        return this.request('/api/nfc/register', {
            method: 'POST',
            body: JSON.stringify({
                student_id: studentId,
                nfc_tag_id: nfcTagId
            })
        });
    }

    static async getStudentByTag(tagId) {
        return this.request(`/api/nfc/student/${encodeURIComponent(tagId)}`);
    }

    // Attendance APIs
    static async recordAttendance(data) {
        return this.request('/api/attendance/record', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    static async getStudentAttendance(studentId, limit = null) {
        const params = limit ? `?limit=${limit}` : '';
        return this.request(`/api/attendance/student/${studentId}${params}`);
    }

    static async getRecentAttendance(limit = 50) {
        return this.request(`/api/attendance/recent?limit=${limit}`);
    }

    static async getAttendanceStats() {
        return this.request('/api/attendance/stats');
    }
}

/**
 * UI Utilities
 */
class UI {
    static showAlert(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;

        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);

            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }

    static showLoading(element) {
        element.innerHTML = `
            <div class="loading-container">
                <div class="spinner"></div>
            </div>
        `;
    }

    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    static formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('en-IN', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

/**
 * Form Validation
 */
class Validator {
    static validateRequired(value, fieldName) {
        if (!value || value.trim() === '') {
            throw new Error(`${fieldName} is required`);
        }
    }

    static validateStudentForm(formData) {
        this.validateRequired(formData.name, 'Name');
        this.validateRequired(formData.register_number, 'Register Number');
        this.validateRequired(formData.section, 'Section');
        this.validateRequired(formData.department, 'Department');
        this.validateRequired(formData.duration, 'Duration');
    }
}

// Export for use in other scripts
window.APIClient = APIClient;
window.UI = UI;
window.Validator = Validator;
