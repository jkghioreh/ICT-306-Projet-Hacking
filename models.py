from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    coach_name = db.Column(db.String(100), nullable=False)
    coach_email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='equipe') # roles: equipe, admin, public
    status = db.Column(db.String(20), default='en_attente') # status: en_attente, approuve, rejete
    score_total = db.Column(db.Integer, default=0)
    
    members = db.relationship('Member', backref='team', lazy=True, cascade="all, delete-orphan")
    submissions = db.relationship('Submission', backref='team', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    pseudo = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)

class Challenge(db.Model):
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False) # Web, Crypto, Osint, Pwn, Reverse
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False)
    flag = db.Column(db.String(200), nullable=False)
    
    submissions = db.relationship('Submission', backref='challenge', lazy=True, cascade="all, delete-orphan")

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_correct = db.Column(db.Boolean, default=False)
    submitted_flag = db.Column(db.String(200), nullable=True)
