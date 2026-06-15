import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app, redirect
from models import Team

def generate_token(team_id, role):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24), # Valable 24h
        'iat': datetime.datetime.utcnow(),
        'sub': team_id,
        'role': role
    }
    return jwt.encode(payload, current_app.config.get('SECRET_KEY'), algorithm='HS256')

def token_required(f):
    """
    Décorateur pour protéger les routes qui nécessitent une authentification.
    Vérifie la présence et la validité du token JWT dans les cookies.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'token' in request.cookies:
            token = request.cookies.get('token')
            
        elif 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == 'Bearer':
                token = parts[1]

        if not token:
            # Si on accède à une page web ou une api non autorisée
            if request.path.startswith('/api/'):
                return jsonify({'message': 'Token JWT manquant!'}), 401
            return redirect('/login')

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_team = Team.query.filter_by(id=data['sub']).first()
            if not current_team:
                raise Exception("Equipe introuvable")
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expiré, veuillez vous reconnecter.'}), 401
        except Exception as e:
            return jsonify({'message': 'Token invalide!', 'error': str(e)}), 401

        return f(current_team, *args, **kwargs)
    return decorated

def admin_required(f):
    """
    Décorateur secondaire à combiner avec @token_required.
    Vérifie que l'utilisateur a bien le rôle d'administrateur.
    """
    @wraps(f)
    def decorated(current_team, *args, **kwargs):
        if current_team.role != 'admin':
            return jsonify({'message': 'Accès refusé. Privilèges administrateur requis!'}), 403
        return f(current_team, *args, **kwargs)
    return decorated
