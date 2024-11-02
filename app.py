from flask import Flask, render_template, request, redirect, url_for, g, session
from flask_migrate import Migrate
import os
from db import db
from auth import auth
from dotenv import load_dotenv
from datetime import timedelta
import transaction_history
import threading
import queue
import time
import atexit
import logging


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

task_queue = queue.Queue()

def consumer():
    while True:
        task = task_queue.get()
        if task is None:
            break
        
        try:
            process_task(task)
        except Exception as e:
            print(f"Error processing task: {e}")
        finally:
            task_queue.task_done()
            
def process_task(task):
    ticket_id, ticket_price_str, user_id = task
    
    with app.app_context():
        ticket_price_str = ticket_price_str.replace('$', '').replace(',', '').strip()
        ticket_price_cents = int(float(ticket_price_str) * 100)
        ticket_listing = Ticket_Listing(
            ticket_id=ticket_id,
            seller_id=user_id,
            sale_price_cents=ticket_price_cents,
            status = 'Available'
        )
        
        db.session.add(ticket_listing)
        db.session.commit()
        
consumer_thread = threading.Thread(target=consumer)
consumer_thread.daemon = True
consumer_thread.start()

    
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
@app.route('/ticket_inventory', methods=['GET', 'POST'])
def ticketinventory():
    if not g.user:
        return redirect(url_for('auth.signin'))
    
    if request.method == 'POST':
        ticket_id = request.form.get('ticket_id')
        selling_price = request.form.get('selling_price')
        
        if not ticket_id or not selling_price:
            return "Invalid request", 400
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket or ticket.owner_id != g.user.user_id:
            return "Ticket not found", 404
        
        existing_listing = Ticket_Listing.query.filter_by(ticket_id=ticket_id, status='Available').first()
        if existing_listing:
            return redirect(url_for('resale_market'))
        
        task_queue.put((ticket_id, selling_price, g.user.user_id))
        
        logging.info(f"Task added to queue: {ticket_id}, {selling_price}, {g.user.user_id}")
        
        """new_listing = Ticket_Listing(
            ticket_id=ticket_id,
            seller_id=g.user.user_id,
            sale_price_cents = ticket.ticket_price_cents,
            status='Available'
        )"""
        
        """db.session.add(new_listing)
        db.session.commit()
        print(f"New listing created: {new_listing}")"""
        
        return redirect(url_for('resale_market'))
    
    if request.method == 'GET':
        # Fetching tickets owned by the user
        owned_tickets = g.user.tickets_owned 
        print(f"Owned tickets: {[ticket.ticket_id for ticket in owned_tickets]}")

        """ticket_info = [{
            "event_name": ticket.event.event_name,
            "event_datetime": ticket.event.event_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "category": ticket.seat_category,
            "price": ticket.get_price_str(),
            "id": ticket.ticket_id
        }   for ticket in owned_tickets]"""
        
        ticket_info = []
        for ticket in owned_tickets:
            ticket_data = {
                "event_name": ticket.event.event_name,
                "event_datetime": ticket.event.event_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                "category": ticket.seat_category,
                "price": ticket.get_price_str(),
                "id": ticket.ticket_id,
            }
            existing_listing = Ticket_Listing.query.filter_by(ticket_id=ticket.ticket_id, status='Available').first()
            ticket_data['listing_status'] = 'Listed' if existing_listing else 'Not Listed'
            ticket_info.append(ticket_data)
    
        print(ticket_info)

        return render_template('ticket_inventory.html', tickets=ticket_info)

# Route for browsing resale tickets
@app.route('/resale_market')
def resale_market():
    if not g.user:
        return redirect(url_for('auth.signin'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    available_tickets = Ticket_Listing.query.filter_by(status='Available').all()
    
    valid_listings = [
        listing for listing in available_tickets
        if listing.real_status == "Available"
    ]
    
    ticket_paginated = valid_listings[(page - 1) * per_page: page * per_page]
    
    ticket_info = []
    
    for listing in ticket_paginated:
        ticket = listing.ticket
        if ticket and ticket.event:
            ticket_info.append({
            "listing_id": listing.listing_id,
            "event_name": ticket.event.event_name,
            "event_datetime": ticket.event.event_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "category": ticket.seat_category,
            "price": listing.get_price_str(),
            "listing_status": listing.real_status
            
        #event = ticket.event
        
        })
            
    print(ticket_info)
    
    total_pages = len(valid_listings) // per_page + (1 if len(valid_listings) % per_page > 0 else 0)
    
    return render_template('resale_market.html',
                           tickets=ticket_info,
                           total_pages=total_pages,
                           current_page=page)

# Route for event details page
@app.route('/event_details/<int:id>')
def eventdetails(id):
    ticket_detail = Ticket_Listing.query.filter_by(listing_id=id)

    event_info = []

    for listing in ticket_detail:
        ticket = listing.ticket
        event_info.append({
            "event_name": ticket.event.event_name,
            "event_datetime": ticket.event.event_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "event_location": ticket.event.location,
            "event_description": ticket.event.description,
            "event_image": ticket.event.event_image, 
            "price":listing.get_price_str(),
        })

    return render_template('event_details.html', events=event_info)

# Route for user purchase ticket
@app.route('/purchase_ticket', methods=['POST'])
def purchaseticket():

    return redirect(url_for('resale_market'))
    
@app.route('/sell_tickets', methods=['GET','POST'])
def sell_tickets():
    if not g.user:
        return redirect(url_for('auth.signin'))
    
    ticket_id = request.form['ticket_id']
    selling_price = request.form['selling_price']
    
    ticket = Ticket.query.get(ticket_id)
    
    if not ticket or ticket.owner_id != g.user.user_id:
        return "Ticket not found", 404
    
    existing_listing = Ticket_Listing.query.filter_by(ticket_id=ticket_id).first()
    if existing_listing:
        return redirect(url_for('resale_market'))
    
    new_listing = Ticket_Listing(
        ticket_id=ticket_id,
        seller_id=g.user.user_id,
        price=selling_price,
        status='Available'
    )
    
    db.session.add(new_listing)
    db.session.commit()
    print(new_listing)
    
    return render_template('resale_market.html')
    
    
def shutdown_consumer():
    task_queue.put(None)
    consumer_thread.join(timeout=10)
atexit.register(shutdown_consumer)

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    app.run(debug=True)
