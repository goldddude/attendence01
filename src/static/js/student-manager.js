/**
 * Student Management UI Logic
 */

class StudentManager {
    static async loadStudents(containerId, filters = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        UI.showLoading(container);

        try {
            const data = await APIClient.getStudents(filters);
            this.renderStudentList(container, data.students);
        } catch (error) {
            container.innerHTML = `
                <div class="alert alert-error">
                    Failed to load students: ${error.message}
                </div>
            `;
        }
    }

    static renderStudentList(container, students) {
        if (students.length === 0) {
            container.innerHTML = `
                <div class="text-center" style="padding: 3rem;">
                    <h3>No students found</h3>
                    <p class="text-secondary">Add students manually or upload an Excel file to get started.</p>
                </div>
            `;
            return;
        }

        const html = `
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Register Number</th>
                            <th>Name</th>
                            <th>Section</th>
                            <th>Department</th>
                            <th>Duration</th>
                            <th>NFC Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${students.map(student => `
                            <tr>
                                <td><strong>${student.register_number}</strong></td>
                                <td>${student.name}</td>
                                <td>${student.section}</td>
                                <td>${student.department}</td>
                                <td>${student.duration}</td>
                                <td>
                                    ${student.has_nfc
                ? '<span class="badge badge-success">✓ Registered</span>'
                : '<span class="badge badge-warning">Not Registered</span>'}
                                </td>
                                <td>
                                    <a href="student-profile.html?id=${student.id}" class="btn btn-secondary btn-icon" title="View Profile">
                                        👤
                                    </a>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.innerHTML = html;
    }

    static async loadStudentProfile(studentId, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        UI.showLoading(container);

        try {
            const data = await APIClient.getStudent(studentId);
            const attendanceData = await APIClient.getStudentAttendance(studentId, 10);

            this.renderStudentProfile(container, data.student, attendanceData.attendance);
        } catch (error) {
            container.innerHTML = `
                <div class="alert alert-error">
                    Failed to load student profile: ${error.message}
                </div>
            `;
        }
    }

    static renderStudentProfile(container, student, attendance) {
        const html = `
            <div class="grid grid-2">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Student Information</h3>
                    </div>
                    <div style="display: grid; gap: 1rem;">
                        <div>
                            <strong>Name:</strong> ${student.name}
                        </div>
                        <div>
                            <strong>Register Number:</strong> ${student.register_number}
                        </div>
                        <div>
                            <strong>Section:</strong> ${student.section}
                        </div>
                        <div>
                            <strong>Department:</strong> ${student.department}
                        </div>
                        <div>
                            <strong>Duration:</strong> ${student.duration}
                        </div>
                        <div>
                            <strong>NFC Status:</strong> 
                            ${student.has_nfc
                ? `<span class="badge badge-success">✓ Registered</span><br><small>${student.nfc_tag_id}</small>`
                : '<span class="badge badge-warning">Not Registered</span>'}
                        </div>
                    </div>
                    <div class="mt-3">
                        ${!student.has_nfc
                ? `<button onclick="registerNFC(${student.id})" class="btn btn-primary">📱 Register NFC Tag</button>`
                : `<button onclick="unregisterNFC(${student.id})" class="btn btn-secondary">Remove NFC Tag</button>`}
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">Recent Attendance</h3>
                        <p class="card-subtitle">Last 10 records</p>
                    </div>
                    ${attendance.length > 0 ? `
                        <div style="display: grid; gap: 0.75rem;">
                            ${attendance.map(record => `
                                <div style="padding: 0.75rem; background: var(--surface-hover); border-radius: var(--radius-md);">
                                    <div style="display: flex; justify-content: space-between;">
                                        <span><strong>${UI.formatDate(record.timestamp)}</strong></span>
                                        <span class="badge badge-success">Present</span>
                                    </div>
                                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                        Recorded by: ${record.recorded_by}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : `
                        <p class="text-secondary">No attendance records yet.</p>
                    `}
                </div>
            </div>
        `;

        container.innerHTML = html;
    }
}

// Export for use in HTML pages
window.StudentManager = StudentManager;
