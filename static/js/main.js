document.addEventListener('DOMContentLoaded', () => {
    // === COUNTDOWN LOGIC ===
    // Set target date for May 23, 2026, 09:00:00 (Swiss Time)
    const targetDate = new Date('2026-05-23T09:00:00').getTime();

    function updateCountdown() {
        const now = new Date().getTime();
        const distance = targetDate - now;

        const elDays = document.getElementById('cd-days');
        const elHours = document.getElementById('cd-hours');
        const elMins = document.getElementById('cd-mins');
        const elSecs = document.getElementById('cd-secs');

        if (!elDays || !elHours || !elMins || !elSecs) return;

        if (distance < 0) {
            elDays.innerText = "00";
            elHours.innerText = "00";
            elMins.innerText = "00";
            elSecs.innerText = "00";
            return;
        }

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        elDays.innerText = days.toString().padStart(2, '0');
        elHours.innerText = hours.toString().padStart(2, '0');
        elMins.innerText = minutes.toString().padStart(2, '0');
        elSecs.innerText = seconds.toString().padStart(2, '0');
    }

    // Update countdown every second
    setInterval(updateCountdown, 1000);
    updateCountdown(); // Initial call
});
