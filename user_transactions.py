from flask import Blueprint, render_template, request, session, redirect, url_for, flash, render_template_string
from models import User, Ticket_Listing, Ticket
#from db import db

user_transacts = Blueprint('transaction_history', __name__)

@user_transacts.route('/transactions', methods=['GET'])

def getUserTransacts()->str:


    if request.method == 'GET':
        payload:dict = {}
        currentUser:User = session['user']
        if currentUser.ticket_buy_list:
            buyList:dict
            for listing in currentUser.ticket_buy_list:

            payload['buyList']
            # TODO finish this implementation and replace the 