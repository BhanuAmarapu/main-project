// Main JavaScript for Secure Cloud Deduplication System

$(document).ready(function () {
    console.log('Secure Cloud Deduplication System - Initialized');

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function () {
        $('.alert').fadeOut('slow');
    }, 5000);

    // File size validation
    $('input[type="file"]').on('change', function () {
        const maxSize = 100 * 1024 * 1024; // 100MB
        const file = this.files[0];

        if (file && file.size > maxSize) {
            alert('File size exceeds 100MB limit!');
            $(this).val('');
        }
    });

    // Tooltips
    $('[data-toggle="tooltip"]').tooltip();

    // Confirm delete actions
    $('.delete-btn').on('click', function (e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });
});

// Format bytes to human readable
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Format time duration
function formatDuration(seconds) {
    if (seconds < 60) {
        return seconds.toFixed(2) + 's';
    } else if (seconds < 3600) {
        return (seconds / 60).toFixed(2) + 'm';
    } else {
        return (seconds / 3600).toFixed(2) + 'h';
    }
}
