# Règles de Contribution et Stratégie de Branches

Afin de garantir la stabilité de l'infrastructure du tournoi, merci de respecter les directives suivantes lors de vos développements.

## 🌳 Stratégie de Branches (Git Flow Simplifié)

Le dépôt repose sur **deux branches principales protégées** :
- `main` : Contient le code de production. Toujours stable et prêt à être déployé sur les serveurs de l'événement.
- `develop` : Branche d'intégration globale. Regroupe toutes les fonctionnalités testées avant leur bascule vers `main`.

**Aucun commit direct n'est autorisé sur `main` ou `develop`.**

### Comment travailler sur une nouvelle issue :
1. Assurez-vous d'être à jour sur `develop` : `git checkout develop && git pull`
2. Créez une nouvelle branche de travail : `git checkout -b <type>/<nom-issue>`
   - *Types autorisés :* `feat` (nouvelle fonctionnalité), `fix` (correction de bug), `docs` (documentation), `refactor` (optimisation du code).
   - *Exemple :* `git checkout -b feat/formulaire-inscription`

## 🔀 Règles de Pull Requests (PR)

Toute fusion de code doit obligatoirement passer par une **Pull Request** pointant vers la branche `develop`.

### Exigences avant validation d'une PR :
1. **Conventional Commits** : Vos commits doivent obligatoirement respecter la nomenclature conventionnelle (ex: `feat(ui): ajout du compte à rebours`).
2. **Validation Technique** : Le code Frontend doit utiliser uniquement HTML/CSS/JS Vanilla (aucun framework tiers type React/Tailwind).
3. **Revue de Code** : La PR nécessite l'approbation d'au moins **1 administrateur / Lead Dev**.
4. **Template de PR** : La description de votre Pull Request doit suivre le template officiel `.github/PULL_REQUEST_TEMPLATE.md` automatiquement chargé par GitHub.

## 🛡️ Protection des Branches (Branch Protection Rules)
Côté serveur GitHub, des règles strictes empêchent le `push force` et exigent que toutes les discussions (threads) d'une PR soient résolues avant de pouvoir cliquer sur le bouton *Merge*.
