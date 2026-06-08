document.addEventListener('DOMContentLoaded', () => {
    // === COUNTDOWN LOGIC ===
    // Date cible de l'événement : 23 Mai 2026 à 09:00:00 (Heure de Suisse)
    const targetDate = new Date('2026-05-23T09:00:00').getTime();
    
    // Conteneur principal pour afficher un message si terminé
    const countdownContainer = document.getElementById('countdown');

    function updateCountdown() {
        if (!countdownContainer) return;
        
        const now = new Date().getTime();
        const distance = targetDate - now;

        const elDays = document.getElementById('cd-days');
        const elHours = document.getElementById('cd-hours');
        const elMins = document.getElementById('cd-mins');
        const elSecs = document.getElementById('cd-secs');

        if (!elDays || !elHours || !elMins || !elSecs) return;

        // Si l'événement a commencé
        if (distance < 0) {
            countdownContainer.innerHTML = '<div class="event-started-msg" style="font-size: 1.5rem; color: var(--accent-primary); font-weight: 800; text-shadow: 0 0 15px var(--accent-glow);">L\'ÉVÉNEMENT EST EN COURS !</div>';
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

    // Mise à jour toutes les secondes
    setInterval(updateCountdown, 1000);
    updateCountdown(); // Appel initial
});
