// Real-time updates via WebSocket or polling

class RealtimeUpdater {
    constructor(updateInterval = 5000) {
        this.updateInterval = updateInterval;
        this.isRunning = false;
    }

    start() {
        if (this.isRunning) return;

        this.isRunning = true;
        this.update();
        this.intervalId = setInterval(() => this.update(), this.updateInterval);
    }

    stop() {
        if (!this.isRunning) return;

        this.isRunning = false;
        clearInterval(this.intervalId);
    }

    update() {
        fetch('/api/metrics/realtime')
            .then(response => response.json())
            .then(data => {
                this.onUpdate(data);
            })
            .catch(error => {
                console.error('Error fetching real-time data:', error);
            });
    }

    onUpdate(data) {
        // Override this method to handle updates
        console.log('Real-time update:', data);
    }
}

// Initialize real-time updater
const realtimeUpdater = new RealtimeUpdater();

$(document).ready(function () {
    if ($('.realtime-dashboard').length) {
        realtimeUpdater.start();
    }
});
