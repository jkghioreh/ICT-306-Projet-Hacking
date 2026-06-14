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

# === ROUTES SCOREBOARD (TEMPS RÉEL) ===

@app.route('/scoreboard')
def scoreboard():
    return render_template('scoreboard.html')

@app.route('/api/scoreboard')
def api_scoreboard():
    # Récupérer les équipes approuvées, triées par score descendant
    teams = Team.query.filter_by(role='equipe', status='approuve').order_by(Team.score_total.desc()).all()
    
    # Formater les données en JSON pour l'Ajax
    leaderboard = []
    for t in teams:
        leaderboard.append({
            'name': t.name,
            'score': t.score_total
        })
        
    return jsonify(leaderboard)

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

from flask import Flask, render_template, request, jsonify, redirect, make_response, flash

# ... (les imports existent déjà, je vais juste écraser les routes Dashboard)
@app.route('/ctf/dashboard')
@token_required
def dashboard(current_team):
    challenges = Challenge.query.all()
    # Récupérer l'historique complet pour l'équipe (trié par le plus récent)
    submissions = Submission.query.filter_by(team_id=current_team.id).order_by(Submission.timestamp.desc()).all()
    
    # Isoler les IDs résolus pour affichage vert/cacher formulaire
    solved_challenge_ids = [sub.challenge_id for sub in submissions if sub.is_correct]
    
    return render_template(
        'dashboard.html', 
        current_team=current_team, 
        challenges=challenges, 
        solved_challenge_ids=solved_challenge_ids, 
        submissions=submissions
    )

@app.route('/ctf/submit', methods=['POST'])
@token_required
def submit_flag(current_team):
    challenge_id = request.form.get('challenge_id')
    submitted_flag = request.form.get('flag')
    
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Vérifier si le challenge est déjà résolu par cette équipe
    already_solved = Submission.query.filter_by(team_id=current_team.id, challenge_id=challenge.id, is_correct=True).first()
    if already_solved:
        flash("Vous avez déjà résolu ce challenge !", "error")
        return redirect('/ctf/dashboard')
        
    # Validation du flag
    is_correct = (submitted_flag.strip() == challenge.flag)
    
    # Enregistrement de la soumission
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
        flash(f"🎉 Félicitations ! Flag correct. Vous gagnez {challenge.points} points.", "success")
    else:
        db.session.commit()
        flash("❌ Flag incorrect. Essayez encore !", "error")
        
    return redirect('/ctf/dashboard')

# === ROUTES PRIVÉES (PANEL ADMIN) ===

@app.route('/admin')
@token_required
@admin_required
def admin_panel(current_team):
    # Calcul des statistiques pour la vue d'ensemble
    stats = {
        'total_teams': Team.query.filter_by(role='equipe').count(),
        'pending_teams': Team.query.filter_by(status='en_attente').count(),
        'total_challenges': Challenge.query.count(),
        'total_submissions': Submission.query.count()
    }
    return render_template('admin.html', section='overview', stats=stats)

@app.route('/admin/equipes', methods=['GET'])
@token_required
@admin_required
def admin_equipes(current_team):
    teams = Team.query.filter_by(role='equipe').order_by(Team.id.desc()).all()
    return render_template('admin.html', section='equipes', teams=teams)

@app.route('/admin/equipes/<int:team_id>/<action>')
@token_required
@admin_required
def admin_equipes_action(current_team, team_id, action):
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
            
    challenges = Challenge.query.all()
    return render_template('admin.html', section='challenges', challenges=challenges)

@app.route('/admin/challenges/<int:challenge_id>/delete')
@token_required
@admin_required
def admin_challenges_delete(current_team, challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    db.session.delete(challenge)
    db.session.commit()
    return redirect('/admin/challenges')

@app.route('/admin/logs')
@token_required
@admin_required
def admin_logs(current_team):
    # Récupérer les 100 dernières soumissions de flags
    logs = Submission.query.order_by(Submission.timestamp.desc()).limit(100).all()
    return render_template('admin.html', section='logs', logs=logs)

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
