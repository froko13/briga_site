from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func, desc
from sqlalchemy import exc
from datetime import datetime, timedelta
from app.models import User
from runner import bp, db
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

# Ваши маршруты

ticker = 'AAPL'  # Например, Apple
start_date = '2023-01-01'
end_date = '2023-10-01'

# Загружаем данные о ценах акций
data = yf.download(ticker, start=start_date, end=end_date)
dates = data.index
close_prices = data['Close']

@bp.route('/')
def home():
    return render_template('index_home.html')

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
    return render_template('index_new.html')

@bp.route('/courses')
@login_required
def courses():
    return render_template('index_courses.html')

@bp.route('/stocks')
@login_required
def stocks():
    return render_template('index_stock.html')

@bp.route('/plot')
def plot():
    total_steps = len(close_prices)
    return render_template('plot.html', total_steps=total_steps)

@bp.route('/plot/update_plot/<int:step>')
def update_plot(step):
    if step >= len(dates):
        return jsonify({'plot': None})

    # Настраиваем график
    plt.figure(figsize=(10, 5))
    plt.title(f'График акций {ticker}')
    plt.xlabel('Дата')
    plt.ylabel('Цена закрытия')
    plt.grid()

    # Постепенно отображаем данные
    plt.plot(dates[:step+1], close_prices[:step+1], color='blue')

    # Сохранение графика в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    # Кодирование графика в base64
    plot_data = base64.b64encode(buf.getvalue()).decode('utf8')
    return jsonify({'plot': plot_data})

