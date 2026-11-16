import sqlite3

DB_NAME = "wishlist.db"

# Connect to the database and create tables
def initialize_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Wishlist table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Budget table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL
        )
    """)

    # Insert default budget if it does not exist
    cursor.execute("""
        INSERT OR IGNORE INTO budget (id, amount)
        VALUES (1, 0)
    """)

    conn.commit()
    conn.close()


# Add a new wishlist item
def add_item(name, category, price, description, image):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO wishlist
        (name, category, price, description, image)
        VALUES (?, ?, ?, ?, ?)
    """, (name, category, price, description, image))

    conn.commit()
    conn.close()


# Retrieve wishlist items
def get_items(search="", category="All"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = "SELECT * FROM wishlist WHERE name LIKE ?"
    values = ["%" + search + "%"]

    if category != "All":
        query += " AND category = ?"
        values.append(category)

    query += " ORDER BY id DESC"

    cursor.execute(query, values)
    items = cursor.fetchall()

    conn.close()
    return items


# Update an existing item
def update_item(item_id, name, category, price, description, image):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE wishlist
        SET name = ?, category = ?, price = ?,
            description = ?, image = ?
        WHERE id = ?
    """, (name, category, price, description, image, item_id))

    conn.commit()
    conn.close()


# Delete an item
def delete_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM wishlist WHERE id = ?", (item_id,)
    )

    conn.commit()
    conn.close()


# Change purchase status
def update_status(item_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE wishlist
        SET status = ?
        WHERE id = ?
    """, (status, item_id))

    conn.commit()
    conn.close()


# Get dashboard statistics
def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM wishlist")
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM wishlist WHERE status = 'Purchased'"
    )
    purchased = cursor.fetchone()[0]

    pending = total - purchased

    cursor.execute("""
        SELECT COALESCE(SUM(price), 0)
        FROM wishlist
        WHERE status = 'Purchased'
    """)
    spent = cursor.fetchone()[0]

    cursor.execute("SELECT amount FROM budget WHERE id = 1")
    budget = cursor.fetchone()[0]

    conn.close()

    return total, purchased, pending, spent, budget


# Set the user's budget
def set_budget(amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE budget
        SET amount = ?
        WHERE id = 1
    """, (amount,))

    conn.commit()
    conn.close()


# Create database automatically when this file is imported
initialize_db()
