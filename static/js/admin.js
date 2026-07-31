/**
 * PlacementIQ Admin Dashboard JavaScript Controller
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Sidebar Toggle functionality for Mobile & Tablet screens
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('adminSidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function (e) {
            if (window.innerWidth <= 992) {
                if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target) && sidebar.classList.contains('show')) {
                    sidebar.classList.remove('show');
                }
            }
        });
    }

    // 2. Auto dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

/**
 * Populate Edit Student Modal with target student details
 */
function openEditModal(student) {
    document.getElementById('edit_student_id').value = student.id;
    document.getElementById('edit_student_name').value = student.student_name || '';
    document.getElementById('edit_register_number').value = student.register_number || '';
    document.getElementById('edit_department').value = student.department || '';
    document.getElementById('edit_cgpa').value = student.cgpa || 7.0;
    document.getElementById('edit_tenth_percentage').value = student.tenth_percentage || 70.0;
    document.getElementById('edit_twelfth_percentage').value = student.twelfth_percentage || 70.0;
    document.getElementById('edit_aptitude_score').value = student.aptitude_score || 65;
    document.getElementById('edit_coding_score').value = student.coding_score || 65;
    document.getElementById('edit_communication_skill').value = student.communication_skill || 'Average';
    document.getElementById('edit_internship').value = student.internship || 'No';
    document.getElementById('edit_certifications').value = student.certifications || 0;
    document.getElementById('edit_projects_completed').value = student.projects_completed || 1;
    document.getElementById('edit_backlogs').value = student.backlogs || 0;
    document.getElementById('edit_placement_status').value = student.placement_status !== undefined ? student.placement_status : 0;

    const form = document.getElementById('editStudentForm');
    if (form) {
        form.action = '/admin/students/edit/' + student.id;
    }

    const editModal = new bootstrap.Modal(document.getElementById('editStudentModal'));
    editModal.show();
}

/**
 * Populate Delete Student Modal
 */
function openDeleteModal(studentId, studentName) {
    const nameEl = document.getElementById('delete_student_name_span');
    if (nameEl) nameEl.textContent = studentName;

    const form = document.getElementById('deleteStudentForm');
    if (form) {
        form.action = '/admin/students/delete/' + studentId;
    }

    const deleteModal = new bootstrap.Modal(document.getElementById('deleteStudentModal'));
    deleteModal.show();
}

/**
 * Initialize Analytics Dashboard Chart.js Visualizations
 */
function initAnalyticsCharts(analyticsData) {
    if (!analyticsData) return;

    // Common Chart.js default font & color settings for dark dashboard
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";

    // 1. Placed vs Not Placed Doughnut Chart
    const ctxPlaced = document.getElementById('placedVsUnplacedChart');
    if (ctxPlaced) {
        new Chart(ctxPlaced, {
            type: 'doughnut',
            data: {
                labels: ['Likely Placed', 'Unlikely Placed'],
                datasets: [{
                    data: [
                        analyticsData.placed_vs_unplaced.placed,
                        analyticsData.placed_vs_unplaced.unplaced
                    ],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 0,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 14, padding: 16 } }
                },
                cutout: '70%'
            }
        });
    }

    // 2. Department-wise Placement Rate Bar Chart
    const ctxDept = document.getElementById('deptPlacementChart');
    if (ctxDept) {
        new Chart(ctxDept, {
            type: 'bar',
            data: {
                labels: analyticsData.department_analytics.labels,
                datasets: [{
                    label: 'Placement Rate (%)',
                    data: analyticsData.department_analytics.rates,
                    backgroundColor: '#6366f1',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // 3. Average CGPA by Department
    const ctxCgpa = document.getElementById('deptCgpaChart');
    if (ctxCgpa) {
        new Chart(ctxCgpa, {
            type: 'bar',
            data: {
                labels: analyticsData.department_analytics.labels,
                datasets: [{
                    label: 'Average CGPA',
                    data: analyticsData.department_analytics.avg_cgpa,
                    backgroundColor: '#06b6d4',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { min: 5.0, max: 10.0, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // 4. Internship vs Placement Grouped Bar Chart
    const ctxIntern = document.getElementById('internshipPlacementChart');
    if (ctxIntern) {
        new Chart(ctxIntern, {
            type: 'bar',
            data: {
                labels: ['Internship Done (Yes)', 'No Internship (No)'],
                datasets: [
                    {
                        label: 'Placed Students',
                        data: [
                            analyticsData.internship_analytics.Yes.placed,
                            analyticsData.internship_analytics.No.placed
                        ],
                        backgroundColor: '#10b981',
                        borderRadius: 6
                    },
                    {
                        label: 'Unplaced Students',
                        data: [
                            analyticsData.internship_analytics.Yes.unplaced,
                            analyticsData.internship_analytics.No.unplaced
                        ],
                        backgroundColor: '#f59e0b',
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 5. Certification Count vs Placement
    const ctxCert = document.getElementById('certPlacementChart');
    if (ctxCert) {
        new Chart(ctxCert, {
            type: 'line',
            data: {
                labels: analyticsData.certification_analytics.labels,
                datasets: [{
                    label: 'Placement Success Rate (%)',
                    data: analyticsData.certification_analytics.rates,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.15)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 6. Monthly Prediction Statistics Line Chart
    const ctxMonthly = document.getElementById('monthlyPredictionChart');
    if (ctxMonthly) {
        new Chart(ctxMonthly, {
            type: 'line',
            data: {
                labels: analyticsData.monthly_predictions.labels.length > 0 ? analyticsData.monthly_predictions.labels : ['Current Month'],
                datasets: [{
                    label: 'Prediction Volume',
                    data: analyticsData.monthly_predictions.counts.length > 0 ? analyticsData.monthly_predictions.counts : [1],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }
}
