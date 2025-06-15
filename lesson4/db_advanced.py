import sqlite3
from datetime import datetime

# Функція для заповнення бази даних
def setup_database(conn):
    cursor = conn.cursor()
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        product_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        category TEXT NOT NULL,
                        price REAL NOT NULL
                    )''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS customers (
                        customer_id INTEGER PRIMARY KEY,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE
                    )''')
        
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        order_id INTEGER PRIMARY KEY,
                        customer_id INTEGER NOT NULL,
                        product_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        order_date DATE NOT NULL,
                        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                        FOREIGN KEY (product_id) REFERENCES products(product_id)
                    )''')
    conn.commit()


# Функція для створення з'єднання з базою даних
def create_connection():
    return sqlite3.connect("electronics_store.db")


# Функція для заповнення бази даних
def fill_database(conn):
    cursor = conn.cursor()

    # списрк товарів для вставки 

    products = [
        ("Lenovo Leion Y520", "Ноутбуки", 39900),
        ("Samsung", "Телефон", 40000),
        ("Apple", "Планшет", 50000),
        ("Lenovo", "Телефон", 80000),
        ("Xiaomi", "Годиник", 30000),
        ("MacBook", "компютер", 70000)
    ]

    # перевірка та вставка товарів

    for name, category, price in products:
        cursor.execute("SELECT COUNT(*) FROM products WHERE name = ?", (name,))
        # (0, )
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO products (name, category, price) VALUES (?, ?, ?)", (name, category, price))
    

    # список клієнтів для вставки
    customers = [
        ("Олександр", "Кужель", "kuzhel@gmail.com"),
        ("Олексій", "Кадура", "kadura@gmail.com"),
        ("Владислав", "Казістов", "vlad@gmail.com"),
        ("Ангеліна", "Авраменко", "angelina@gmail.com")
    ]

    for first_name, last_name, email in customers:
        cursor.execute("SELECT COUNT(*) FROM customers WHERE email = ?", (email,))
        # якщо такого товару ще немає
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO customers (first_name, last_name, email) VALUES (?, ?, ?)", (first_name, last_name, email))
    
    # список замовлень для вставки
    orders = [
        (1, 1, 1, "2025-06-13"),
        (1, 3, 1, "2025-06-11"),
        (2, 2, 2, "2025-06-10"),
        (2, 4, 1, "2025-06-13"),
        (3, 5, 1, "2025-06-08"),
        (3, 6, 3, "2025-06-02"),
    ]

    for customer_id, product_id, quantity, order_date in orders:
        cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ?", (customer_id,))
        # якщо такого товару ще немає
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (?, ?, ?, ?)", (customer_id, product_id, quantity, order_date))

    conn.commit()



# Функція для виконання запитів до бази даних
def execute_query(conn, query, params=(), fetch=False):
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
        return cursor.fetchall()
    return None


# Функція для підрахунку сумарного обсягу продажів (сума за всі замовлення)
def total_sales(conn):
    query = '''
        SELECT SUM(products.price * orders.quantity)
        FROM orders
        JOIN products ON orders.product_id = products.product_id
    '''
    result = execute_query(conn, query, fatch = True)
    return result[0][0]


# Функція для підрахунку кількості замовлень на кожного клієнта
def orders_per_customer(conn):
    query = '''
        SELECT customers.first_name, customers.last_name, COUNT(orsers.orser_id)
        FROM customers
        INNER JOIN orders ON customers.customer_id = orders.customer_id
        GROUP BY customers.customer_id,
    '''
    result = execute_query(conn, query, fatch = True)
    return result


# Функція для підрахунку середнього чеку замовлення (середня сума грошей в одному замовленні)
def average_order_value(conn):
    query = '''
        SELECT AVG(SUM(poducts.price * orders.quantity) AS total))
        FROM orders
        JOIN products ON orders.product_id = products.product_id
        GROUP BY orders.order_id
    '''
    result = execute_query(conn, query, fetch=True)
    return result


# Функція для пошуку категорії товарів, яка має найбільше замовлень
def most_popular_category(conn):
    query = '''
        SELECT products.category, COUNT(orders.order_id) as count
        FROM products
        JOIN orders ON products.product_id = orders.product_id
        GROUP BY products.category
        ORDER BY count DESC
        LIMIT 1
    '''
    return execute_query(conn, query, fetch=True)



# Функція для обрахунку загальної кількості товарів кожної категорії
def products_per_category(conn):
    query = '''
        SELECT products.category, COUNT(*)
        FROM products
        GROUP BY products.category
    '''
    return execute_query(conn, query, fetch=True)


# Функція для оновлення ціни товарів в категорії "смартфони" на 10% збільшення
def update_smartphone_prices(conn):
    query = '''
        UPDATE products
        SET price = price * 1.10
        WHERE categoty = 'Смартфони'
    '''
    execute_query(conn, query)


# Основна фунуція
def main():
    conn = create_connection()
    setup_database(conn)
    fill_database(conn)

    while True:
        print("\nМеню:")
        print("1. Загальний обсяг продажів")
        print("2. Кількість замовлень на клієнта")
        print("3. Середній чек замовлення")
        print("4. Найпопулярніша категорія")
        print("5. Кількість товарів у категоріях")
        print("6. Оновити ціни смартфонів (+10%)")
        print("7. Вийти")
        
        choice = input("Виберіть опцію (1-7): ")

        # Загальний обсяг продажів
        if choice == '1':
            result = total_sales(conn)
            print(f"Загальний обсяг продажів: ${result:.2f}")

        # Кількість замовлень на клієнта
        elif choice == '2':
            results = orders_per_customer(conn)
            for first_name, last_name, count in results:
                print(f"{first_name} {last_name}: {count} замовлень")

        # Середній чек замовлення 
        elif choice == '3':
            result = average_order_value(conn)
            print(f"Середній чек: ${result:.2f}")

        # Найпопулярніша категорія   
        elif choice == '4':
            result = most_popular_category(conn)
            if result:
                category, count = result[0]
                print(f"Найпопулярніша категорія: {category} ({count} замовлень)")

        # Кількість товарів у категоріях      
        elif choice == '5':
            results = products_per_category(conn)
            for category, count in results:
                print(f"{category}: {count} товарів")
        
        # Оновити ціни смартфонів (+10%)        
        elif choice == '6':
            update_smartphone_prices(conn)
            print("Ціни на смартфони оновлено")

        # Вийти
        elif choice == '7':
            save = input("Зберегти зміни? (так/ні): ").lower()
            if save == 'так':
                conn.commit()
                print("Зміни збережено")
            else:
                conn.rollback()
                print("Зміни скасовано")
            break
            
        else:
            print("Невірний вибір")

    conn.close()

if __name__ == "__main__":
    main()
    