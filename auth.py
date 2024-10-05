from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models import User
from db import db
auth = Blueprint('auth', __name__)


@auth.route('/signin', methods=['GET', 'POST'])

def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:
            session['user'] = user.email
            
            if user.user_type == "customer":
                return redirect(url_for('eventlist'))
            elif user.user_type == "organizer":
                return redirect(url_for('eventmanagement'))
            else:
                return redirect(url_for('auth.signin'))
        else:
            flash('Invalid email or password')
            redirect(url_for('auth.signin'))
            
    return render_template('signin.html')