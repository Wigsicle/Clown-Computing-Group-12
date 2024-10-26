from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import User
from db import db
auth = Blueprint('auth', __name__)


@auth.route('/signin', methods=['GET', 'POST'])

def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"Form submitted with email: {email}, password: {password}")
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            print(f"User found: {user.email}")
        else:
            print(f"User not found with email: {email}")
        
        if user and user.password == password:
            session['user'] = user.email
            session['user_type'] = user.user_type
            session.permanent = True
            
            if user.user_type == "normal":
                return redirect(url_for('eventlist', user=user.email))
            elif user.user_type == "admin":
                return redirect(url_for('ticketinventory', user=user.email))
            else:
                return redirect(url_for('auth.signin'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('auth.signin'))
            
    return render_template('signin.html')