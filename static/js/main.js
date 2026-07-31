/**
 * AI Student Placement Prediction - Frontend Client Controller
 * Handles client-side form validation, AJAX prediction requests, and result visualization.
 */

document.addEventListener('DOMContentLoaded', () => {
    initFormValidation();
    initPredictionForm();
});

/**
 * Real-time client-side form validation feedback.
 * Attaches blur and input event listeners to inputs to toggle visual state classes.
 */
function initFormValidation() {
    const inputs = document.querySelectorAll('#placement-form .form-control');
    
    inputs.forEach(input => {
        // Validate on losing focus (blur)
        input.addEventListener('blur', () => {
            validateField(input);
        });

        // Validate dynamically on input change (once already touched or typed)
        input.addEventListener('input', () => {
            if (input.classList.contains('is-valid') || input.classList.contains('is-invalid')) {
                validateField(input);
            }
        });
    });
}

/**
 * Validates a single input element and updates its CSS status classes.
 * @param {HTMLInputElement|HTMLSelectElement} input The input field element to validate.
 */
function validateField(input) {
    if (input.checkValidity()) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        return true;
    } else {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        return false;
    }
}

/**
 * Handle form submission asynchronously via AJAX.
 * Verifies form validity, prepares the payload, and makes the API call.
 */
function initPredictionForm() {
    const form = document.getElementById('placement-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const inputs = form.querySelectorAll('.form-control');
        let isFormValid = true;

        // Validate all fields on submit trigger
        inputs.forEach(input => {
            if (!validateField(input)) {
                isFormValid = false;
            }
        });

        // If client-side validation fails, scroll to the first invalid element and abort
        if (!isFormValid) {
            const firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalid.focus();
            }
            return;
        }

        const submitBtn = document.getElementById('submit-btn');
        const spinner = document.getElementById('btn-spinner');
        const btnBolt = document.getElementById('btn-bolt');
        const btnText = document.getElementById('btn-text');
        const resultPanel = document.getElementById('result-panel');

        // UI loading state activation
        if (submitBtn) submitBtn.disabled = true;
        if (spinner) spinner.style.display = 'inline-block';
        if (btnBolt) btnBolt.style.display = 'none';
        if (btnText) btnText.textContent = 'Analyzing Student Profile...';

        // Prepare JSON payload matching backend specifications
        const formData = new FormData(form);
        const payload = {
            student_name: formData.get('student_name').trim(),
            register_number: formData.get('register_number').trim(),
            department: formData.get('department'),
            cgpa: parseFloat(formData.get('cgpa')),
            tenth_percentage: parseFloat(formData.get('tenth_percentage')),
            twelfth_percentage: parseFloat(formData.get('twelfth_percentage')),
            aptitude_score: parseInt(formData.get('aptitude_score')),
            coding_score: parseInt(formData.get('coding_score')),
            communication_skill: formData.get('communication_skill'),
            internship: formData.get('internship'),
            certifications: parseInt(formData.get('certifications')),
            projects_completed: parseInt(formData.get('projects_completed')),
            backlogs: parseInt(formData.get('backlogs'))
        };

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success) {
                renderResults(data);
                if (resultPanel) {
                    resultPanel.style.display = 'block';
                    resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            } else {
                alert('Prediction Error: ' + (data.error || 'Unable to process calculation.'));
            }
        } catch (err) {
            console.error('Request failed:', err);
            alert('Server error occurred while predicting. Please try again.');
        } finally {
            // Restore UI interactive state
            if (submitBtn) submitBtn.disabled = false;
            if (spinner) spinner.style.display = 'none';
            if (btnBolt) btnBolt.style.display = 'inline-block';
            if (btnText) btnText.textContent = 'Predict Placement Chance';
        }
    });
}

let radarChartInstance = null;

/**
 * Render probability gauge, status badges, recommendations, and radar comparison chart.
 * @param {Object} data The success response object from Flask backend prediction API.
 */
function renderResults(data) {
    const probEl = document.getElementById('result-prob');
    const statusEl = document.getElementById('result-status');
    const badgeEl = document.getElementById('result-badge');
    const titleEl = document.getElementById('result-title');
    const subtitleEl = document.getElementById('result-subtitle');
    const recContainer = document.getElementById('recommendations-list');

    // Display personalized information in headers
    if (titleEl) {
        titleEl.innerHTML = `Placement Report for <span class="gradient-text">${data.student_name || 'Student'}</span>`;
    }
    if (subtitleEl) {
        subtitleEl.textContent = `Register No: ${data.register_number || 'N/A'} | Department: ${data.department || 'N/A'}`;
    }

    // Display probability percentage
    if (probEl) {
        probEl.textContent = `${data.probability}%`;
        probEl.style.color = data.color;
    }

    if (statusEl) {
        statusEl.textContent = data.placed_text;
    }

    if (badgeEl) {
        badgeEl.textContent = data.status;
        badgeEl.style.backgroundColor = data.color + '22'; // 20% opacity background
        badgeEl.style.color = data.color;
        badgeEl.style.border = `1px solid ${data.color}`;
    }

    // Populate recommendations list dynamically
    if (recContainer) {
        recContainer.innerHTML = '';
        data.recommendations.forEach(rec => {
            const card = document.createElement('div');
            card.className = `rec-card ${rec.type}`;
            card.innerHTML = `
                <div class="rec-icon">
                    <i class="fas ${rec.icon}"></i>
                </div>
                <div class="rec-content">
                    <h4>${rec.title}</h4>
                    <p>${rec.text}</p>
                </div>
            `;
            recContainer.appendChild(card);
        });
    }

    // Render Radar Comparison Chart mapping inputs to benchmarks
    renderRadarChart(data.inputs, data.placed_averages);
}

/**
 * Render Radar Chart using Chart.js comparing candidate profile against benchmarks.
 * @param {Object} inputs Scaled feature metrics used in the RF model.
 * @param {Object} averages Benchmarks from placed students.
 */
function renderRadarChart(inputs, averages) {
    const ctx = document.getElementById('radarChart');
    if (!ctx) return;

    if (radarChartInstance) {
        radarChartInstance.destroy();
    }

    // Normalized scores out of 100 for radar visual parity mapping
    const studentScores = [
        (inputs.cgpa / 10.0) * 100,
        (inputs.aptitude_score),
        (inputs.internships / 1.0) * 100, // Map Yes/No to 0 or 100%
        (inputs.projects / 5.0) * 100,
        (inputs.soft_skills_score / 5.0) * 100
    ];

    const avgScores = averages ? [
        ((averages.cgpa || 7.8) / 10.0) * 100,
        (averages.aptitude_score || 72),
        ((averages.internships || 0.6) / 1.0) * 100,
        ((averages.projects || 2.4) / 5.0) * 100,
        ((averages.soft_skills_score || 3.8) / 5.0) * 100
    ] : [78, 72, 60, 50, 76];

    radarChartInstance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['CGPA', 'Aptitude', 'Internship', 'Projects', 'Comm. Skill'],
            datasets: [
                {
                    label: 'Your Profile',
                    data: studentScores,
                    fill: true,
                    backgroundColor: 'rgba(99, 102, 241, 0.25)',
                    borderColor: '#6366f1',
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#6366f1'
                },
                {
                    label: 'Placed Student Benchmark',
                    data: avgScores,
                    fill: true,
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    borderColor: '#10b981',
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#10b981'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    pointLabels: {
                        color: '#94a3b8',
                        font: { size: 11, weight: '600' }
                    },
                    ticks: {
                        display: false,
                        max: 100,
                        min: 0
                    }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#f8fafc',
                        font: { weight: '600', size: 11 }
                    }
                }
            }
        }
    });
}
