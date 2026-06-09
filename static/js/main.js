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
    
    // Appel initial pour éviter un décalage d'une seconde au chargement
    updateCountdown(); 
    
    // === LOGIQUE DE LA FAQ (ACCORDÉON) ===
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    faqQuestions.forEach(question => {
        question.addEventListener('click', () => {
            const faqItem = question.parentElement;
            
            // Si on veut fermer les autres accordéons lorsqu'un est ouvert (optionnel)
            // const activeItem = document.querySelector('.faq-item.active');
            // if (activeItem && activeItem !== faqItem) {
            //     activeItem.classList.remove('active');
            // }

            // Basculer l'état ouvert/fermé
            faqItem.classList.toggle('active');
        });
    });

    // === LOGIQUE DU FORMULAIRE D'INSCRIPTION (MEMBRES DYNAMIQUES) ===
    const membersContainer = document.getElementById('membersContainer');
    const btnAddMember = document.getElementById('btnAddMember');
    const btnRemoveMember = document.getElementById('btnRemoveMember');
    const memberCountSpan = document.getElementById('memberCount');
    
    let currentMembers = 2;
    const maxMembers = 4;
    
    if (btnAddMember && btnRemoveMember && membersContainer) {
        btnAddMember.addEventListener('click', () => {
            if (currentMembers < maxMembers) {
                currentMembers++;
                
                // Créer le bloc du nouveau membre
                const memberBlock = document.createElement('div');
                memberBlock.className = 'member-block';
                memberBlock.id = `memberBlock_${currentMembers}`;
                memberBlock.innerHTML = `
                    <h3>Membre ${currentMembers}</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Pseudo <span class="required">*</span></label>
                            <input type="text" name="member_${currentMembers}_pseudo" required placeholder="Pseudo">
                        </div>
                        <div class="form-group">
                            <label>Email <span class="required">*</span></label>
                            <input type="email" name="member_${currentMembers}_email" required placeholder="email@exemple.com">
                        </div>
                    </div>
                `;
                
                membersContainer.appendChild(memberBlock);
                memberCountSpan.innerText = currentMembers;
                
                // Mettre à jour la visibilité des boutons
                btnRemoveMember.style.display = 'inline-block';
                if (currentMembers === maxMembers) {
                    btnAddMember.style.display = 'none';
                }
            }
        });
        
        btnRemoveMember.addEventListener('click', () => {
            if (currentMembers > 2) {
                const lastMemberBlock = document.getElementById(`memberBlock_${currentMembers}`);
                if (lastMemberBlock) {
                    membersContainer.removeChild(lastMemberBlock);
                }
                
                currentMembers--;
                memberCountSpan.innerText = currentMembers;
                
                // Mettre à jour la visibilité des boutons
                btnAddMember.style.display = 'inline-block';
                if (currentMembers === 2) {
                    btnRemoveMember.style.display = 'none';
                }
            }
        });
    }
    
    // === LOGIQUE DE LA NAVBAR MOBILE ===
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const navLinksContainer = document.querySelector('.nav-links');
    
    if (mobileMenuToggle && navLinksContainer) {
        mobileMenuToggle.addEventListener('click', () => {
            navLinksContainer.classList.toggle('active-menu');
        });
    }
});
