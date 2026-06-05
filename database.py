import sqlite3

def init_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()

    c.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price INTEGER NOT NULL,
                image TEXT NOT NULL
            )
            ''')

    c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            ''')

    c.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
            ''')

    c.execute('DELETE FROM products')

    products = [
        ('Синтезатор Yamaha PSR-EW310', 20000, '1.jpg'),
        ('Классическая гитара Yamaha C40', 12000, '2.jpg'),
        ('Укулеле Flight NUB 310', 10000, '3.jpg'),
        ('Скрипка Stentor Student I', 30000, '4.jpg'),
        ('Арфа Ravenna 34', 180000, '5.jpg'),
    ]

    c.executemany('INSERT INTO products (title, price, image) VALUES (?, ?, ?)', products)

    conn.commit()
    conn.close()
    print("БД успешно создана и обновлена!")

if __name__ == '__main__':
    init_db()