from flask import Flask, render_template, request, redirect, url_for, session
import os
from db import db
from auth import auth

app = Flask(__name__)
app.secret_key = 'anything'

app.register_blueprint(auth)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:db123@localhost/ticket_hive?charset=utf8mb4&collation=utf8mb4_general_ci'
app.config

db.init_app(app)
from models import User, Event, Ticket

# Route for the homepage
@app.route('/')
def home():
    
    return render_template('index.html')

# Route for the sign-in page
@app.route('/signin')
def signup():
    
    return render_template('signin.html')

# Route for the event management page for event organizer 
# CRUD events
@app.route('/event_management')
def eventmanagement():
    
    return render_template('event_management.html')

# Route for the event list page for users
# User able to buy event ticket, resale ticket and sell tickets
@app.route('/event_list')
def eventlist():
    
    return render_template('event_list.html')

# Route for event details page
@app.route('/event_details')
def eventdetails():
    
    return render_template('event_details.html')

# Route for the ticket inventory page
# List of user purchased ticket
@app.route('/ticket_inventory')
def ticketinventory():
    
    return render_template('ticket_inventory.html')

# Route for ticket selling page
@app.route('/sell_ticket_1')
def sellticket1():
    
    return render_template('ticket_sell1.html')

@app.route('/sell_ticket_2')
def sellticket2():
    
    return render_template('ticket_sell2.html')

if __name__ == '__main__':
    app.run(debug=True)