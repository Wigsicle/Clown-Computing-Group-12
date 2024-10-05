from db import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(45), nullable=False)
    user_type = db.Column(db.String(45), nullable=False)
    
    tickets = db.relationship('Ticket', backref='user', lazy=True)
    
class Event(db.Model):
    __tablename__ = 'event'
    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(120), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    event_time = db.Column(db.String(45), nullable=False)
    event_location = db.Column(db.String(120), nullable=False)
    event_description = db.Column(db.String(120), nullable=False)
    event_image = db.Column(db.String(120), nullable=False)
    
    tickets = db.relationship('Ticket', backref='event', lazy=True)
    
class Ticket(db.Model):
    __tablename__ = 'ticket'
    ticket_id = db.Column(db.Integer, primary_key=True)
    ticket_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), nullable=False)