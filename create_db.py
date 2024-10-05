from app import app, db
from models import User, Event, Ticket

# Create all tables inside an application context
with app.app_context():
    db.create_all()

print("Database tables created successfully!")
