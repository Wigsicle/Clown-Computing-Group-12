from flask import Flask, render_template, request, redirect, url_for, g, session, flash
from flask import Flask, render_template, request, redirect, url_for, g, session, flash
from flask_migrate import Migrate
import os
from db import db
from auth import auth
from dotenv import load_dotenv
from datetime import timedelta, datetime
import transaction_history

import grpc
from Ticket_pb2_grpc import TicketStub
from Ticket_pb2 import ReadTicketByIdRequest, TransferTicketRequest


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
    print(request.method)
    if not g.user:
        return redirect(url_for('auth.signin'))
    
    if request.method == 'POST':
        ticket_id = request.form['ticket_id']
        selling_price = request.form['selling_price']
        
        ticket = Ticket.query.get(ticket_id)
        if not ticket or ticket.owner_id != g.user.user_id:
            return "Ticket not found", 404
        
        existing_listing = Ticket_Listing.query.filter_by(ticket_id=ticket_id, status='Available').first()
        if existing_listing:
            return redirect(url_for('resale_market'))
        
        new_listing = Ticket_Listing(
            ticket_id=ticket_id,
            seller_id=g.user.user_id,
            sale_price_cents = ticket.ticket_price_cents,
            status='Available'
        )
        
        db.session.add(new_listing)
        db.session.commit()
        print(f"New listing created: {new_listing}")
        
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
@app.route('/listing/<int:id>')
def listing_details(id):
    """Displays the chosen ticket_listing"""
    listing: Ticket_Listing = Ticket_Listing.query.filter_by(listing_id=id).first_or_404()
    ticket: Ticket = listing.ticket
    event: Event = listing.ticket.event

    # info retrieved from the ticket listing's event
    event_info:dict = {
        'name': event.event_name,
        'details': event.description,
        'date': event.event_datetime.strftime('%d %b %Y'), # date string format: 28 Jan 2025
        'time': event.event_datetime.strftime('%I:%M %p'), # time string format: 01:40 PM format
        'location': event.location,
        'img_path': event.event_image, # relative path to the event image stored in static/images/
    }

    ticket_info:dict = {
        'list_id': id,
        'list_price': listing.get_price_str(),
        'category': ticket.seat_category,
        'seat_no': ticket.seat_number,
    }
@app.route('/listing/<int:id>')
def listing_details(id):
    """Displays the chosen ticket_listing"""
    listing: Ticket_Listing = Ticket_Listing.query.filter_by(listing_id=id).first_or_404()
    ticket: Ticket = listing.ticket
    event: Event = listing.ticket.event

    # info retrieved from the ticket listing's event
    event_info:dict = {
        'name': event.event_name,
        'details': event.description,
        'date': event.event_datetime.strftime('%d %b %Y'), # date string format: 28 Jan 2025
        'time': event.event_datetime.strftime('%I:%M %p'), # time string format: 01:40 PM format
        'location': event.location,
        'img_path': event.event_image, # relative path to the event image stored in static/images/
    }

    ticket_info:dict = {
        'list_id': id,
        'list_price': listing.get_price_str(),
        'category': ticket.seat_category,
        'seat_no': ticket.seat_number,
    }

    return render_template('listing_details.html',event_info=event_info,ticket_info=ticket_info)

# Initialize gRPC channel and stub globally for reuse
channel = grpc.insecure_channel('localhost:50051')
stub = TicketStub(channel)

# Route for user purchase ticket
@app.route('/purchase_ticket/<int:list_id>', methods=['GET','POST'])
def purchaseticket(list_id):
    if not g.user:
        return redirect(url_for('auth.signin'))
    
    if request.method == 'POST' or list_id:
        sel_listing:Ticket_Listing = db.get_or_404(Ticket_Listing, list_id)
        sel_ticket:Ticket = sel_listing.ticket

        if sel_listing.real_status == 'Available': # checks if listing is still available
            sel_listing.sold_on = datetime.now()
            sel_listing.buyer_id = g.user.user_id #buyer
            sel_ticket.owner_id = g.user.user_id  #new owner
            
            # TODO add the gRPC function that updates the owner_id attribute on BC
            #Calls a GRPC transfer request
            bc_trans_ticket_id = str(sel_listing.ticket_id)
            bc_trans_owner_id = str(g.user.user_id)
            transfer_ticket_request = TransferTicketRequest(ticketId=bc_trans_ticket_id, newOwner=bc_trans_owner_id)
            response = stub.TransferTicket(transfer_ticket_request)
            print(response.success)
            
            #Calls a GRPC read request to ensure that the data is transferred.
            read_ticket_request = ReadTicketByIdRequest(ticketId=bc_trans_ticket_id)
            response2 = stub.ReadTicketById(read_ticket_request)  # This should return a ReadTicketByIdReply
            print(response2.ticketInfo)
            
            db.session.commit()
            flash('Succesfully purchased the ticket, check the details in your inventory')
            return redirect(url_for('ticketinventory'))
        else:
            flash('Selected listing has already been purchased, redirecting you back to the Marketplace')


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

if __name__ == '__main__':
    app.run(debug=True)
