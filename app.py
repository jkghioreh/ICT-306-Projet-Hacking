import os
from flask import Flask, render_template, request, jsonify, redirect, make_response
from models import db, Team, Member
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

# === ROUTES PRIVÉES (DASHBOARD CTF) ===

@app.route('/ctf/dashboard')
@token_required
def dashboard(current_team):
    return f"""
    <h1>Dashboard CTF - Hacking International 2026</h1>
    <h2>Équipe : {current_team.name}</h2>
    <p>Score Actuel : {current_team.score_total} points</p>
    <p>Bienvenue dans l'arène ! Les challenges seront bientôt disponibles ici.</p>
    """

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
