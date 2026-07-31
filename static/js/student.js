/**
 * PlacementIQ Student Portal JavaScript Controller
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Sidebar Toggle functionality for Mobile screens
    const toggleBtn = document.getElementById('studentSidebarToggle');
    const sidebar = document.getElementById('studentSidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });

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
 * Print / Save PDF Prediction Report
 */
function printReport() {
    window.print();
}
