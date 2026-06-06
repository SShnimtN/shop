from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import database

app = Flask(__name__)
app.secret_key = '123'


def get_db_connection():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_cart_count():
    if 'user_id' not in session:
        return 0
    conn = get_db_connection()
    count = conn.execute('SELECT SUM(quantity) FROM cart WHERE user_id = ?', (session['user_id'],)).fetchone()[0]
    conn.close()
    return count if count else 0


@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products, cart_count=get_cart_count())


# РЕГИСТРАЦИЯ
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)  # Шифруем пароль

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Это имя пользователя уже занято.', 'danger')
        finally:
            conn.close()

    return render_template('register.html', cart_count=get_cart_count())


# ЛОГИН
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль.', 'danger')

    return render_template('login.html', cart_count=get_cart_count())


# ВЫХОД ИЗ АККАУНТА
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ДОБАВЛЕНИЕ В КОРЗИНУ
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в аккаунт, чтобы добавлять товары в корзину.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cart_item = conn.execute('SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
                             (session['user_id'], product_id)).fetchone()

    if cart_item:
        conn.execute('UPDATE cart SET quantity = quantity + 1 WHERE id = ?', (cart_item['id'],))
    else:
        conn.execute('INSERT INTO cart (user_id, product_id) VALUES (?, ?)', (session['user_id'], product_id))

    conn.commit()
    conn.close()
    flash('Товар успешно добавлен в корзину!', 'success')
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Пожалуйста, войдите в аккаунт для просмотра корзины.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()

    items = conn.execute('''
        SELECT cart.id as cart_id, products.title, products.price, products.image, cart.quantity 
        FROM cart 
        JOIN products ON cart.product_id = products.id 
        WHERE cart.user_id = ?
    ''', (session['user_id'],)).fetchall()
    conn.close()

    total_price = sum(item['price'] * item['quantity'] for item in items)

    return render_template('cart.html', items=items, total_price=total_price, cart_count=get_cart_count())


@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM cart WHERE id = ? AND user_id = ?', (cart_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('cart'))


if __name__ == '__main__':
    if not os.path.exists('shop.db'):
        print("База данных не найдена. Создаю...")
        database.init_db()

    app.run(debug=True)