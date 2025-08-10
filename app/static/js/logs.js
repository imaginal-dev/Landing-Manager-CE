// static/js/logs.js
document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('toggle-logs-btn');
    const logsViewer = document.getElementById('logs-viewer');
    const logsContent = document.getElementById('logs-content');

    if (toggleButton) {
        toggleButton.addEventListener('click', function() {
            const isHidden = logsViewer.style.display === 'none' || logsViewer.style.display === '';
            
            if (isHidden) {
                // Show the container and fetch logs
                logsViewer.style.display = 'block';
                toggleButton.textContent = 'Hide Logs';
                logsContent.textContent = 'Loading logs...';

                fetch('/api/logs')
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                        return response.text();
                    })
                    .then(data => {
                        logsContent.textContent = data || 'Logs are empty.';
                    })
                    .catch(error => {
                        console.error('Error fetching logs:', error);
                        logsContent.textContent = 'Failed to load logs. See browser console for details.';
                    });
            } else {
                // Hide the container
                logsViewer.style.display = 'none';
                toggleButton.textContent = 'Show Logs';
            }
        });
    }
});
