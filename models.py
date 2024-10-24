# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from app import db  # Import the db object from your app

# User model
class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Matches the table name in your database
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    chips = db.Column(db.Integer, default=1000)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    # Relationships
    game_sessions = db.relationship(
        'UserGameSession', back_populates='user', cascade='all, delete-orphan'
    )
    hand_histories = db.relationship(
        'HandHistory', back_populates='user', cascade='all, delete-orphan'
    )
    leaderboard = db.relationship(
        'Leaderboard', back_populates='user', uselist=False, cascade='all, delete-orphan'
    )

# GameSession model
class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    id = db.Column(db.Integer, primary_key=True)
    session_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    users = db.relationship(
        'UserGameSession', back_populates='game_session', cascade='all, delete-orphan'
    )
    hand_histories = db.relationship(
        'HandHistory', back_populates='game_session', cascade='all, delete-orphan'
    )

# Association table for many-to-many relationship between User and GameSession
class UserGameSession(db.Model):
    __tablename__ = 'user_game_sessions'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    game_session_id = db.Column(
        db.Integer, db.ForeignKey('game_sessions.id'), primary_key=True
    )
    is_active = db.Column(db.Boolean, default=True)
    # Relationships
    user = db.relationship('User', back_populates='game_sessions')
    game_session = db.relationship('GameSession', back_populates='users')

# HandHistory model
class HandHistory(db.Model):
    __tablename__ = 'hand_histories'
    id = db.Column(db.Integer, primary_key=True)
    game_session_id = db.Column(
        db.Integer, db.ForeignKey('game_sessions.id'), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hand_data = db.Column(db.Text)
    result = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    user = db.relationship('User', back_populates='hand_histories')
    game_session = db.relationship('GameSession', back_populates='hand_histories')

# Leaderboard model
class Leaderboard(db.Model):
    __tablename__ = 'leaderboards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_wins = db.Column(db.Integer, default=0)
    total_losses = db.Column(db.Integer, default=0)
    total_chips_won = db.Column(db.Integer, default=0)
    total_chips_lost = db.Column(db.Integer, default=0)
    # Relationships
    user = db.relationship('User', back_populates='leaderboard')
