from flask import Flask, render_template, request, redirect, url_for, g, session
from flask_migrate import Migrate
import os
from db import db
from auth import auth
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

if not os.getenv("DB_USERNAME"):
    raise RuntimeError("Database local dev environment variables not set.")

DB_USER = os.getenv('DB_USERNAME')
DB_PASS = os.getenv('DB_PASSWORD')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SESSION_PERMANENT'] = True

app.register_blueprint(auth)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://' + DB_USER + ':' + DB_PASS + '@localhost/ticket_hive?charset=utf8mb4&collation=utf8mb4_general_ci'

db.init_app(app)
migrate = Migrate(app, db)

from models import User, Event, Ticket, Ticket_Listing

@app.context_processor
def inject_user():
    return {'current_user': g.user}

@app.before_request
def load_logged_in_user():
    user_email = session.get('user')
    if user_email is None:
        g.user = None
    else:
        g.user = User.query.filter_by(email=user_email).first()
# Route for the homepage
@app.route('/')
def home():
    
    return render_template('index.html')

# Route for the sign-in page
@app.route('/signin')
def signin():
    
    return render_template('signin.html')

# Route for the event list page for users
# User able to buy event ticket, resale ticket and sell tickets
@app.route('/homepage')
def homepage():
    user_email = session.get('user')
    
    return render_template('homepage.html', user_email=user_email)

# Route for event details page
@app.route('/ticket_transaction_history')
def tickettransactionhistory():
    
    return render_template('ticket_transaction_history.html')

# Route for the ticket inventory page
# List of user purchased ticket
@app.route('/ticket_inventory')
def ticketinventory():
    
    user_email = session.get('user')
    
    if not user_email:
        return redirect(url_for('auth.signin'))
    
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return "User not found", 404  # Handling the case where the user is not found
    
    # Fetching tickets owned by the user
    owned_tickets = user.tickets_owned 

    ticket_info = [{
        "event_name": ticket.event.event_name,
        "event_datetime": ticket.event.event_datetime.strftime('%Y-%m-%d %H:%M:%S'),
        "category": ticket.seat_category,
        "price": ticket.get_price_str(),
    } for ticket in owned_tickets]

    return render_template('ticket_inventory.html', tickets=ticket_info, user_email=user_email)

# Route for browsing resale tickets
@app.route('/resale_market')
def resale_market():
    if not g.user:
        return redirect(url_for('auth.signin'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    available_tickets = Ticket_Listing.query.filter_by(status='Available')
    ticket_paginated = available_tickets.paginate(page=page, per_page=per_page, error_out=False)
    
    ticket_info = []
    
    for listing in ticket_paginated.items:
        ticket = listing.ticket
        if ticket and ticket.event:
            ticket_info.append({
            "event_name": ticket.event.event_name,
            "event_datetime": ticket.event.event_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "category": ticket.seat_category,
            "price": listing.get_price_str(),
            
        #event = ticket.event
        
        })
            
    print(ticket_info)
    
    return render_template('resale_market.html',
                           tickets=ticket_info,
                           total_pages=ticket_paginated.pages,
                           current_page=ticket_paginated.page)

if __name__ == '__main__':
    app.run(debug=True)