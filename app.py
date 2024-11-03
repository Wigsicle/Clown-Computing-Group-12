from flask import Flask, render_template, request, redirect, url_for, g, session, jsonify
from flask_migrate import Migrate
import os
import json
from db import db
from auth import auth
from dotenv import load_dotenv
from datetime import timedelta
import transaction_history

import grpc
import hashlib  # Import hashlib for SHA-256 hashing
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
            "listing_id": listing.listing_id,
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

# Initialize gRPC channel and stub globally for reuse
channel = grpc.insecure_channel('localhost:50051')
stub = TicketStub(channel)

@app.route('/add_ticket', methods=['POST'])
def add_ticket():
    data = request.get_json()
    guid = data.get('guid')
    passkey = data.get('passkey')

    if not guid or not passkey:
        response_data = {'status': 'error', 'message': 'GUID and passkey are required'}
        print("CLI Output:", response_data)  # Print to CLI
        return jsonify(response_data), 400

    # Hash the passkey with SHA-256
    hashed_passkey = hashlib.sha256(passkey.encode()).hexdigest()
    
    read_ticket_request = ReadTicketByIdRequest(ticketId=guid)
    
    try:
        # Call the gRPC method
        response = stub.ReadTicketById(read_ticket_request)  # This should return a ReadTicketByIdReply
            
        # Get the string from the gRPC response and parse it as JSON
        ticket_info_string = response.ticketInfo
        ticket_info_dict = json.loads(ticket_info_string)
            
        # Parse the JSON string to a dictionary
        ticket_info_dict = json.loads(ticket_info_string)

       # Print the contents of ticket_info_dict for debugging
        print("Ticket Info Dictionary:", ticket_info_dict)
        
        print(ticket_info_dict['HashVal']) #the hash value within the blockchain
        print(hashed_passkey)    #the hashed_passkey is not matching the one in the blockchain.

        # Check the hashed passkey against the stored HashVal
        if ticket_info_dict.get('HashVal') == hashed_passkey:
            # Prepare the data structure for the front end
            return jsonify({
                'status': 'found',
                'ticket_info': {
                    'ticket_id': ticket_info_dict.get('TicketID', 'N/A'),
                    'event_name': ticket_info_dict.get('EventName', 'N/A'),
                    'category': ticket_info_dict.get('TicketCategory', 'N/A'),
                    'seat_number': ticket_info_dict.get('SeatNumber', 'N/A'),
                    'owner_id': ticket_info_dict.get('OwnerID', 'N/A')
                }
            })
        else:
            # If the hashes do not match, return not found status
            return jsonify({'status': 'not_found', 'message': 'Ticket not found or passkey incorrect'}), 404

    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': 'Invalid JSON response from gRPC service'}), 500
    except grpc.RpcError as e:
        return jsonify({'status': 'error', 'message': f'RPC failed: {e.code()} - {e.details()}'}), 500
    
    
@app.route('/confirm_add_ticket', methods=['POST'])
def confirm_add_ticket():
    data = request.get_json()
    guid = data.get('guid')

    # Simulate ticket addition logic here


    return jsonify({'status': 'success', 'message': 'Ticket added to user inventory'})

if __name__ == '__main__':
    app.run(debug=True)
