import sqlite3

DB_NAME = "airbnb.db"


# ---------------- CONNECTION ----------------
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


# ---------------- CREATE TABLES ----------------
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # BOOKINGS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_name TEXT NOT NULL,
        check_in TEXT NOT NULL,
        check_out TEXT NOT NULL,
        revenue REAL NOT NULL,
        booking_source TEXT NOT NULL
    )
    """)

    # EXPENSES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        notes TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- BOOKINGS ----------------
def add_booking(guest_name, check_in, check_out, revenue, booking_source):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO bookings (guest_name, check_in, check_out, revenue, booking_source)
    VALUES (?, ?, ?, ?, ?)
    """, (guest_name, check_in, check_out, revenue, booking_source))

    conn.commit()
    conn.close()


def get_bookings():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows


# ---------------- EXPENSES ----------------
def add_expense(date, category, amount, notes):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO expenses (date, category, amount, notes)
    VALUES (?, ?, ?, ?)
    """, (date, category, amount, notes))

    conn.commit()
    conn.close()


def get_expenses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows