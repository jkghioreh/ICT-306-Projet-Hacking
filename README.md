# 🚩 Hacking International 2026 - SafeNetAcademy

Bienvenue sur le dépôt officiel du projet **Hacking International 2026**.
Ce projet abrite l'intégralité de l'infrastructure logicielle pour le tournoi annuel de cybersécurité (CTF) organisé par SafeNetAcademy au SwissTech Convention Center (STCC) les 23 et 24 mai 2026.

## 🎯 Objectif du Projet
Développer une plateforme complète divisée en deux parties :
1. **Site Web Événementiel (Public) :** Informations, planning, règles, hébergement, inscriptions des équipes et intégration d'un flux de streaming en direct.
2. **Plateforme CTF (Privée) :** Dashboard de jeu, validation des flags, Scoreboard en temps réel et panel d'administration pour la gestion de l'événement.

## 🛠️ Stack Technique Stricte
Afin de répondre aux contraintes académiques et techniques du mandat :
- **Frontend :** HTML5, CSS3 pur (Vanilla, responsive via Media Queries), JavaScript Vanilla.
- **Backend :** Python avec le framework Flask.
- **Base de données :** SQLite (gestion via SQL pur ou Flask-SQLAlchemy).
- **Sécurité :** Authentification par JSON Web Tokens (JWT) et hachage renforcé des mots de passe.

## 👥 Rôles Utilisateurs
1. **Spectateur (Public) :** Lecture seule, suivi du classement en live.
2. **Équipe (Participant) :** Dashboard privé, soumission de flags.
3. **Administrateur (Orga) :** Gestion des équipes, des challenges et analyse des logs.

## 🚀 Lancement Rapide (Local)
*(La documentation concernant le lancement de l'environnement Flask sera ajoutée lors de l'initialisation du Backend).*

## 🤝 Contribution & Conventions
Pour participer au développement, merci de lire attentivement les règles de versioning et de Pull Request décrites dans le fichier [CONTRIBUTING.md](CONTRIBUTING.md).
