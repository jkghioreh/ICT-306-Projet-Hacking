import os
from flask import Flask, render_template, request, jsonify, redirect, make_response
from models import db, Team, Member, Challenge, Submission
from auth import generate_token, token_required, admin_required

app = Flask(__name__)

# Basic Config
app.config['SECRET_KEY'] = 'hackint2026-super-secret-key-change-in-prod'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hacking_ctf.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init Database
db.init_app(app)

# === ROUTES PUBLIQUES (FRONTEND) ===

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/planning')
def planning():
    return render_template('planning.html')

@app.route('/reglement')
def reglement():
    return render_template('reglement.html')

@app.route('/inscriptions', methods=['GET', 'POST'])
def inscriptions():
    if request.method == 'GET':
        return render_template('inscriptions.html')
    
    if request.method == 'POST':
        # Récupération des données d'équipe
        team_name = request.form.get('team_name')
        coach_name = request.form.get('coach_name')
        coach_email = request.form.get('coach_email')
        team_password = request.form.get('team_password')
        
        # Validation de base
        if not all([team_name, coach_name, coach_email, team_password]):
            return "Veuillez remplir tous les champs obligatoires (nom, coach, email, mot de passe).", 400
        
        if Team.query.filter_by(name=team_name).first():
            return "Ce nom d'équipe est déjà utilisé.", 400
            
        if Team.query.filter_by(coach_email=coach_email).first():
            return "Cette adresse email est déjà enregistrée pour une autre équipe.", 400

        # Création de l'équipe
        new_team = Team(name=team_name, coach_name=coach_name, coach_email=coach_email)
        new_team.set_password(team_password)
        db.session.add(new_team)
        db.session.flush() # Pour récupérer new_team.id sans commit complet

        # Ajout dynamique des membres (max 4)
        for i in range(1, 5):
            pseudo = request.form.get(f'member_{i}_pseudo')
            email = request.form.get(f'member_{i}_email')
            if pseudo and email:
                member = Member(team_id=new_team.id, pseudo=pseudo, email=email)
                db.session.add(member)
                
        db.session.commit()
        return "Candidature reçue ! Votre compte a été créé. Il est en attente de validation par un administrateur.", 201

# === ROUTE AUTHENTIFICATION (LOGIN) ===

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Formulaire brut temporaire, en attendant la vraie maquette de login
        return '''
        <div style="max-width: 400px; margin: 100px auto; font-family: sans-serif; background: #f4f4f4; padding: 20px; border-radius: 8px;">
            <h2>Login au CTF</h2>
            <form method="POST">
                <label>Email Coach / Admin :</label><br>
                <input type="text" name="email" style="width: 100%; margin-bottom: 10px; padding: 5px;"><br>
                <label>Mot de passe :</label><br>
                <input type="password" name="password" style="width: 100%; margin-bottom: 20px; padding: 5px;"><br>
                <input type="submit" value="Se connecter" style="padding: 10px 20px; background: #00ff88; border: none; font-weight: bold; cursor: pointer;">
            </form>
        </div>
        '''
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    team = Team.query.filter_by(coach_email=email).first()
    
    if not team or not team.check_password(password):
        return 'Identifiants invalides', 401
        
    # Vérification du statut d'approbation (les admins sont bypassés)
    if team.status != 'approuve' and team.role != 'admin':
        return 'Votre compte est toujours en attente de validation par SafeNetAcademy.', 403
        
    # Génération du JWT
    token = generate_token(team.id, team.role)
    
    # Redirection selon le rôle
    target_url = '/admin' if team.role == 'admin' else '/ctf/dashboard'
    resp = make_response(redirect(target_url))
    
    # Stockage du JWT dans un cookie sécurisé (HttpOnly)
    resp.set_cookie('token', token, httponly=True, secure=False) # secure=False temporaire pour HTTP local
    return resp

@app.route('/logout')
def logout():
    # Détruit la session de l'utilisateur en supprimant le cookie
    resp = make_response(redirect('/'))
    resp.set_cookie('token', '', expires=0, httponly=True)
    return resp

# === ROUTES PRIVÉES (DASHBOARD CTF) ===

@app.route('/ctf/dashboard')
@token_required
def dashboard(current_team):
    challenges = Challenge.query.all()
    # Récupérer les ID des challenges déjà réussis par l'équipe
    solved_submissions = Submission.query.filter_by(team_id=current_team.id, is_correct=True).all()
    solved_challenge_ids = [sub.challenge_id for sub in solved_submissions]
    
    html = f"""
    <div style="font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <h1>Dashboard CTF - Hacking International 2026</h1>
        <h2>Équipe : {current_team.name}</h2>
        <p>Score Actuel : <strong style="color: #00ff88; font-size: 1.2rem;">{current_team.score_total} points</strong></p>
        <a href="/logout" style="color: red;">Se déconnecter</a>
        <hr>
        <h3>Liste des Challenges</h3>
        <ul style="list-style-type: none; padding: 0;">
    """
    
    for c in challenges:
        if c.id in solved_challenge_ids:
            html += f"<li style='color: green; padding: 10px; border: 1px solid green; margin-bottom: 10px;'>✅ <strong>[{c.category}] {c.name}</strong> ({c.points} pts) - Résolu !</li>"
        else:
            html += f"""
            <li style='margin-bottom: 20px; padding: 15px; border: 1px solid #ccc; background: #f9f9f9;'>
                <strong>[{c.category}] {c.name}</strong> ({c.points} pts)<br>
                <p><em>{c.description}</em></p>
                <form action="/ctf/submit" method="POST" style="margin-top: 10px;">
                    <input type="hidden" name="challenge_id" value="{c.id}">
                    <input type="text" name="flag" placeholder="Format: FLAG{{...}}" required style="padding: 5px; width: 300px;">
                    <input type="submit" value="Valider le Flag" style="padding: 6px 15px; background: #333; color: white; border: none; cursor: pointer;">
                </form>
            </li>
            """
    html += """
        </ul>
    </div>
    """
    return html

@app.route('/ctf/submit', methods=['POST'])
@token_required
def submit_flag(current_team):
    challenge_id = request.form.get('challenge_id')
    submitted_flag = request.form.get('flag')
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Vérifier si le challenge est déjà résolu par cette équipe
    already_solved = Submission.query.filter_by(team_id=current_team.id, challenge_id=challenge.id, is_correct=True).first()
    if already_solved:
        return "Vous avez déjà résolu ce challenge ! <br><br><a href='/ctf/dashboard'>Retour au Dashboard</a>", 400
        
    # Validation du flag
    is_correct = (submitted_flag.strip() == challenge.flag)
    
    # Enregistrement de la soumission (pour les logs, qu'elle soit bonne ou mauvaise)
    submission = Submission(
        team_id=current_team.id, 
        challenge_id=challenge.id, 
        submitted_flag=submitted_flag, 
        is_correct=is_correct
    )
    db.session.add(submission)
    
    if is_correct:
        # Ajout des points
        current_team.score_total += challenge.points
        db.session.commit()
        return f"<h2 style='color:green;'>🎉 Félicitations ! Flag correct.</h2><p>Vous gagnez {challenge.points} points.</p><a href='/ctf/dashboard'>Retour au dashboard</a>"
    else:
        db.session.commit()
        return "<h2 style='color:red;'>❌ Flag incorrect.</h2><p>Essayez encore !</p><a href='/ctf/dashboard'>Retour au dashboard</a>"

# === ROUTES PRIVÉES (PANEL ADMIN) ===

@app.route('/admin')
@token_required
@admin_required
def admin_panel(current_team):
    # Exemple de récupération des équipes en attente
    pending_teams = Team.query.filter_by(status='en_attente').count()
    return f"""
    <h1>Panel Administrateur - SafeNetAcademy</h1>
    <p>Bienvenue {current_team.coach_name}.</p>
    <p>Vous avez {pending_teams} équipe(s) en attente de validation.</p>
    <hr>
    <ul>
        <li><a href="/admin/equipes">Gérer les équipes</a></li>
        <li><a href="/admin/challenges">Gérer les challenges</a></li>
    </ul>
    """

@app.route('/admin/equipes', methods=['GET'])
@token_required
@admin_required
def admin_equipes(current_team):
    # Consultation de toutes les équipes
    teams = Team.query.filter_by(role='equipe').all()
    html = "<h1>Gestion des Équipes</h1><a href='/admin'>Retour au panel</a><br><br><ul>"
    for t in teams:
        html += f"<li><strong>{t.name}</strong> (Coach: {t.coach_name} | {t.coach_email}) - Statut actuel : <em>{t.status}</em> "
        if t.status == 'en_attente':
            html += f" 👉 <a href='/admin/equipes/{t.id}/approuver' style='color:green;'>[Approuver]</a> "
            html += f" <a href='/admin/equipes/{t.id}/rejeter' style='color:red;'>[Rejeter]</a>"
        html += "</li>"
    html += "</ul>"
    return html

@app.route('/admin/equipes/<int:team_id>/<action>')
@token_required
@admin_required
def admin_equipes_action(current_team, team_id, action):
    # Modification du statut de l'équipe
    team = Team.query.get_or_404(team_id)
    if action == 'approuver':
        team.status = 'approuve'
    elif action == 'rejeter':
        team.status = 'rejete'
    
    db.session.commit()
    return redirect('/admin/equipes')

@app.route('/admin/challenges', methods=['GET', 'POST'])
@token_required
@admin_required
def admin_challenges(current_team):
    # Ajout d'un challenge via formulaire (POST)
    if request.method == 'POST':
        category = request.form.get('category')
        name = request.form.get('name')
        description = request.form.get('description')
        points = request.form.get('points')
        flag = request.form.get('flag')
        
        if all([category, name, description, points, flag]):
            new_challenge = Challenge(
                category=category, 
                name=name, 
                description=description, 
                points=int(points), 
                flag=flag
            )
            db.session.add(new_challenge)
            db.session.commit()
            return redirect('/admin/challenges')
            
    # Consultation des challenges existants (GET)
    challenges = Challenge.query.all()
    
    html = "<h1>Gestion des Challenges</h1><a href='/admin'>Retour au panel</a><br><br>"
    html += "<h2>Créer un nouveau Challenge</h2>"
    html += '''
    <form method="POST" style="margin-bottom: 30px;">
        Catégorie (Ex: Web, Crypto): <input type="text" name="category" required><br><br>
        Nom de l'épreuve: <input type="text" name="name" required><br><br>
        Description: <textarea name="description" required rows="3" cols="40"></textarea><br><br>
        Points attribués: <input type="number" name="points" required><br><br>
        Flag (Format: FLAG{...}): <input type="text" name="flag" required><br><br>
        <input type="submit" value="Ajouter le Challenge" style="background:#00ff88; padding:5px 10px;">
    </form>
    <hr>
    <h2>Liste des Challenges (Base de Données)</h2><ul>
    '''
    for c in challenges:
        html += f"<li><strong>[{c.category}] {c.name}</strong> ({c.points} pts) "
        html += f"👉 Flag: <code>{c.flag}</code> "
        html += f"- <a href='/admin/challenges/{c.id}/delete' style='color:red;'>[Supprimer]</a></li>"
    html += "</ul>"
    
    return html

@app.route('/admin/challenges/<int:challenge_id>/delete')
@token_required
@admin_required
def admin_challenges_delete(current_team, challenge_id):
    # Suppression d'un challenge existant
    challenge = Challenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()
    return redirect('/admin/challenges')

# === INITIALISATION SERVEUR ===

if __name__ == '__main__':
    with app.app_context():
        # Création du dossier instance si nécessaire
        if not os.path.exists('instance'):
            os.makedirs('instance')
            
        # Création de la DB si inexistante
        if not os.path.exists('instance/hacking_ctf.db'):
            db.create_all()
            print("[+] Base de données SQLite initialisée.")
            
            # Création d'un administrateur par défaut s'il n'existe pas
            if not Team.query.filter_by(role='admin').first():
                admin = Team(
                    name='Admin System', 
                    coach_name='SysAdmin', 
                    coach_email='admin@safenet.ch', 
                    role='admin', 
                    status='approuve'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("[+] Compte Administrateur par défaut créé (admin@safenet.ch / admin123).")
                
    # Lancement du serveur sur le port 5000
    app.run(debug=True, port=5000)
