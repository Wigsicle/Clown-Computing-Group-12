from flask import Flask, render_template, request, redirect, url_for, session
from flask_migrate import Migrate
import os
from db import db
from auth import auth
from dotenv import load_dotenv
from datetime import timedelta
import transaction_history

load_dotenv()

if not os.getenv("DB_USERNAME"):
    raise RuntimeError("Database local dev environment variables not set.")

DB_USER = os.getenv('DB_USERNAME')
DB_PASS = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config['SESSION_PERMANENT'] = True

app.register_blueprint(auth)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://' + DB_USER + ':' + DB_PASS + '@' + DB_HOST + ':' + DB_PORT + '/' + DB_NAME + '?charset=utf8mb4&collation=utf8mb4_general_ci'

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
@app.route('/homepage')
def homepage():
    user_email = session.get('user')
    
    return render_template('homepage.html', user_email=user_email)

# Route for user transaction history page
@app.route('/ticket_transaction_history')
def tickettransactionhistory():
    '''Let user view their past ticket transactions
    Passes the buy and sell transactions as two separate lists to the ticket_transaction_history page to rendere'''
    user_email:str = session.get('user') # use user email from session for now TODO change to user_id when ready

    selected_page_num = request.args.get('page', 1, type=int) # gets the selected page number from GET request
    records_per_page = 10   # number of records per page

    if not user_email:
        return redirect(url_for('auth.signin'))
    
    user:User = User.query.filter_by(email=user_email).first() # gets the latest transaction history when page loads 

    if not user:
        return "User not found", 404
    
    buy_list_history:list = [] 
    if user.ticket_buy_list is not None:    # checks if the attribute exist or else skips the fn call
        buy_list_history = transaction_history.buyListTransTable(user.ticket_buy_list)
    
    # Buy pagination
    buy_history_paginated = transaction_history.sliceListIntoPages(buy_list_history, records_per_page, selected_page_num)
    buy_total_pages = (len(buy_list_history) + records_per_page - 1) // records_per_page

    sell_list_history:list = [] 
    if user.ticket_sell_list is not None:
        sell_list_history = transaction_history.saleListTransTable(user.ticket_sell_list)

    # Sell pagination
    sell_history_paginated = transaction_history.sliceListIntoPages(sell_list_history, 10, selected_page_num)
    sell_total_pages = (len(sell_list_history) + records_per_page - 1) // records_per_page

    return render_template('ticket_transaction_history.html', 
                           buyList=buy_history_paginated,
                           buy_total_pages=buy_total_pages, # tells page how many buy pages there are
                           buy_current_page=selected_page_num, # tracks current Buy table page
                           sellList=sell_history_paginated,
                           sell_total_pages=sell_total_pages,
                           sell_current_page=selected_page_num)

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
    user_email = session.get('user')
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if not user_email:
        return redirect(url_for('auth.signin'))
    
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
