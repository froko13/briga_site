from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, login_required, logout_user, current_user, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func, desc
from sqlalchemy import exc
from datetime import datetime, timedelta
from app.models import User
from runner import bp, db


# Ваши маршруты


@bp.route('/')
def home():
    return render_template('index.html')

@bp.route("/register", methods=["GET", "POST"])
def register():

    labelLogin = ''

    if request.method == 'POST':
        username = request.form['username'] #получает логин
        password = request.form['password'] #получает пароль
        email = request.form['email']

        #хэшируем пароль
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        #создаем нового пользователя с username и хэшированным паролем
        new_user = User(username=username, password=hashed_password, email = email, user_id = 0)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('main.home'), 301)  

        except exc.IntegrityError:
            db.session.rollback()
            labelLogin = 'Этот Email уже зарегистрирован. Войдите в аккаунт'

    
    return render_template('register.html', labelLogin = labelLogin)

@bp.route('/login', methods=["GET", "POST"])
def login():
    statusLogin = ''

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        new_user = User.query.filter_by(username = username).first()
        if new_user and check_password_hash(new_user.password, password):
            login_user(new_user, remember=True)
            return redirect(url_for('main.home'))
        else:
            statusLogin = 'Вы ввели неправильные данные'
    return render_template('login.html', statusLogin = statusLogin)

@bp.route('/news')
def news():
    return 'news'

@bp.route('/education')
def education():
    return 'education'

@bp.route('/forum')
@login_required
def forum():
    return 'forum'

@bp.route('/cabinet')
@login_required
def cabinet():
    return 'cabinet'

@bp.route('/leaderboard')
@login_required
def leaderboard():
    return 'leaderboard'

@bp.route('/forum/funds')
@login_required
def funds():
    return 'funds'

@bp.route('/forum/shares')
@login_required
def shares():
    return 'shares'

@bp.route('/forum/obligation')
@login_required
def obligation():
    return 'obligation'




