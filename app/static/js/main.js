// Utility functions for CSV Parser and Visualizer

// Auto-resize charts on window resize
window.addEventListener('resize', function() {
    const charts = document.querySelectorAll('.js-plotly-plot');
    if (charts.length > 0) {
        charts.forEach(function(chart) {
            if (typeof Plotly !== 'undefined') {
                Plotly.Plots.resize(chart);
            }
        });
    }
});

// Utility function to check if a string value could be numeric
function isNumeric(str) {
    if (typeof str !== 'string') return false;
    return !isNaN(str) && !isNaN(parseFloat(str));
}

// Initialize Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});
