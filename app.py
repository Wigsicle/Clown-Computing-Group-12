from flask import Flask, render_template, request, redirect, url_for, session
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
@app.route('/event_list')
def eventlist():
    user_email = session.get('user')
    
    return render_template('event_list.html', user_email=user_email)

# Route for event details page
@app.route('/event_details')
def eventdetails():
    
    return render_template('event_details.html')

# Route for event details page
@app.route('/ticket_transaction_history')
def tickettransactionhistory():
    
    return render_template('ticket_transaction_history.html')

# Route for the ticket inventory page
# List of user purchased ticket
@app.route('/ticket_inventory')
def ticketinventory():
    
    user_email = session.get('user')
    user_type = session.get('user_type')
    
    if not user_email:
        return redirect(url_for('auth.signin'))
    
    if user_type != 'admin':
        return redirect(url_for('eventlist'))
    
    return render_template('ticket_inventory.html', user_email=user_email, user_type=user_type)

# Route for ticket selling page
@app.route('/sell_ticket_1')
def sellticket1():
    
    return render_template('ticket_sell1.html')

@app.route('/sell_ticket_2')
def sellticket2():
    
    return render_template('ticket_sell2.html')

# Route for browsing resale tickets
@app.route('/resale_market')
def resale_market():
    # You can add any necessary logic here, e.g., fetching tickets from the database
    user_email = session.get('user')
    
    return render_template('resale_market.html', user_email=user_email)

if __name__ == '__main__':
    app.run(debug=True)