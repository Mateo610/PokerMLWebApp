# app.py

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user, UserMixin
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from models import User, GameSession, UserGameSession, HandHistory, Leaderboard

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://project:your_password@localhost/poker_game'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure logging
if not app.debug:
    file_handler = RotatingFileHandler('logs/poker_game.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Poker game startup')

# Models
class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Matches the table name in your database
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    chips = db.Column(db.Integer, default=1000)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    game_sessions = db.relationship('UserGameSession', back_populates='user', cascade='all, delete-orphan')
    hand_histories = db.relationship('HandHistory', back_populates='user', cascade='all, delete-orphan')

class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    users = db.relationship('UserGameSession', back_populates='game_session', cascade='all, delete-orphan')
    hand_histories = db.relationship('HandHistory', back_populates='game_session', cascade='all, delete-orphan')

class UserGameSession(db.Model):
    __tablename__ = 'user_game_sessions'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    game_session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), primary_key=True)
    is_active = db.Column(db.Boolean, default=True)
    # Relationships
    user = db.relationship('User', back_populates='game_sessions')
    game_session = db.relationship('GameSession', back_populates='users')

class HandHistory(db.Model):
    __tablename__ = 'hand_histories'
    id = db.Column(db.Integer, primary_key=True)
    game_session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hand_data = db.Column(db.Text)
    result = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    user = db.relationship('User', back_populates='hand_histories')
    game_session = db.relationship('GameSession', back_populates='hand_histories')

class Leaderboard(db.Model):
    __tablename__ = 'leaderboards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_wins = db.Column(db.Integer, default=0)
    total_losses = db.Column(db.Integer, default=0)
    total_chips_won = db.Column(db.Integer, default=0)
    total_chips_lost = db.Column(db.Integer, default=0)
    # Relationships
    user = db.relationship('User', backref=db.backref('leaderboard', uselist=False))

# User loader callback
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Input validation
        if not username or not email or not password:
            flash('Please fill out all fields.')
            return redirect(url_for('register'))

        # Check if user already exists
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            flash('Username or email already registered.')
            return redirect(url_for('register'))

        # Create new user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error registering user: {e}")
            flash('An error occurred during registration. Please try again.')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = request.form['password']

        # Find user by email or username
        user = User.query.filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid email/username or password.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
    if request.method == 'POST':
        session_name = request.form['session_name']

        if not session_name:
            flash('Please enter a session name.')
            return redirect(url_for('create_game'))

        new_game_session = GameSession(session_name=session_name)
        try:
            db.session.add(new_game_session)
            db.session.commit()

            # Add the current user to the game session
            user_game_session = UserGameSession(
                user_id=current_user.id,
                game_session_id=new_game_session.id
            )
            db.session.add(user_game_session)
            db.session.commit()

            flash('Game session created.')
            return redirect(url_for('game', game_session_id=new_game_session.id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating game session: {e}")
            flash('An error occurred while creating the game session. Please try again.')
            return redirect(url_for('create_game'))

    return render_template('create_game.html')

@app.route('/join_game', methods=['GET', 'POST'])
@login_required
def join_game():
    if request.method == 'POST':
        session_id = request.form['session_id']

        # Check if the game session exists
        game_session = GameSession.query.get(session_id)
        if not game_session:
            flash('Game session not found.')
            return redirect(url_for('join_game'))

        # Add the user to the game session
        existing_entry = UserGameSession.query.filter_by(
            user_id=current_user.id, game_session_id=session_id
        ).first()
        if existing_entry:
            flash('You have already joined this game session.')
            return redirect(url_for('game', game_session_id=session_id))

        user_game_session = UserGameSession(
            user_id=current_user.id,
            game_session_id=session_id
        )
        try:
            db.session.add(user_game_session)
            db.session.commit()
            flash('Joined the game session.')
            return redirect(url_for('game', game_session_id=session_id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error joining game session: {e}")
            flash('An error occurred while joining the game session. Please try again.')
            return redirect(url_for('join_game'))

    # Display available game sessions
    game_sessions = GameSession.query.all()
    return render_template('join_game.html', game_sessions=game_sessions)

@app.route('/game/<int:game_session_id>')
@login_required
def game(game_session_id):
    game_session = GameSession.query.get_or_404(game_session_id)
    # Check if the user is part of this game session
    user_in_session = UserGameSession.query.filter_by(
        user_id=current_user.id, game_session_id=game_session_id
    ).first()
    if not user_in_session:
        flash('You are not part of this game session.')
        return redirect(url_for('join_game'))

    # Implement game logic here
    return render_template('game.html', game_session=game_session)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Main block to run the app
if __name__ == '__main__':
    app.run(debug=True)
