"""
database.py — MySQL Database Layer
All queries for the Library Desktop App
"""

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta


# ─── DB CONFIG ────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "database": "library_db",
    "user": "root",
    "password": "123456789",   # ← YOUR MySQL password
}


def get_conn():
    return mysql.connector.connect(**DB_CONFIG)


def query(sql, params=(), fetchone=False, commit=False):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        if commit:
            conn.commit()
            return cur.lastrowid
        return cur.fetchone() if fetchone else cur.fetchall()
    except Error as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# ─── AUTH ─────────────────────────────────────────────
def login_user(email, password):
    user = query("SELECT * FROM users WHERE email=%s AND is_active=1", (email,), fetchone=True)
    if user and check_password_hash(user["password"], password):
        return user
    return None


def register_user(name, email, password, phone=""):
    existing = query("SELECT id FROM users WHERE email=%s", (email,), fetchone=True)
    if existing:
        return False, "Email already registered."
    hashed = generate_password_hash(password)
    query("INSERT INTO users (name,email,password,phone) VALUES (%s,%s,%s,%s)",
          (name, email, hashed, phone), commit=True)
    return True, "Registration successful!"


def update_profile(user_id, name, phone, address, new_password=None):
    if new_password:
        hashed = generate_password_hash(new_password)
        query("UPDATE users SET name=%s,phone=%s,address=%s,password=%s WHERE id=%s",
              (name, phone, address, hashed, user_id), commit=True)
    else:
        query("UPDATE users SET name=%s,phone=%s,address=%s WHERE id=%s",
              (name, phone, address, user_id), commit=True)


# ─── BOOKS ────────────────────────────────────────────
def get_books(search="", genre=""):
    if search:
        return query("""SELECT * FROM books WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s ORDER BY title""",
                     (f"%{search}%", f"%{search}%", f"%{search}%"))
    if genre:
        return query("SELECT * FROM books WHERE genre=%s ORDER BY title", (genre,))
    return query("SELECT * FROM books ORDER BY title")


def get_book(book_id):
    return query("SELECT * FROM books WHERE id=%s", (book_id,), fetchone=True)


def add_book(title, author, isbn, genre, publisher, year, copies, description):
    return query("""INSERT INTO books (title,author,isbn,genre,publisher,year_published,
                    total_copies,available_copies,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                 (title, author, isbn or None, genre, publisher, year or None,
                  copies, copies, description), commit=True)


def update_book(book_id, title, author, isbn, genre, publisher, year, copies, description):
    book = get_book(book_id)
    diff = copies - book["total_copies"]
    new_avail = max(0, book["available_copies"] + diff)
    query("""UPDATE books SET title=%s,author=%s,isbn=%s,genre=%s,publisher=%s,
             year_published=%s,total_copies=%s,available_copies=%s,description=%s WHERE id=%s""",
          (title, author, isbn or None, genre, publisher, year or None,
           copies, new_avail, description, book_id), commit=True)


def delete_book(book_id):
    query("DELETE FROM books WHERE id=%s", (book_id,), commit=True)


def get_genres():
    rows = query("SELECT DISTINCT genre FROM books WHERE genre IS NOT NULL ORDER BY genre")
    return [r["genre"] for r in rows]


# ─── USERS ────────────────────────────────────────────
def get_users(search=""):
    if search:
        return query("SELECT * FROM users WHERE name LIKE %s OR email LIKE %s ORDER BY name",
                     (f"%{search}%", f"%{search}%"))
    return query("SELECT * FROM users ORDER BY role DESC, name")


def toggle_user(user_id):
    user = query("SELECT is_active FROM users WHERE id=%s", (user_id,), fetchone=True)
    new_status = 0 if user["is_active"] else 1
    query("UPDATE users SET is_active=%s WHERE id=%s", (new_status, user_id), commit=True)


def promote_user(user_id):
    user = query("SELECT role FROM users WHERE id=%s", (user_id,), fetchone=True)
    new_role = "member" if user["role"] == "admin" else "admin"
    query("UPDATE users SET role=%s WHERE id=%s", (new_role, user_id), commit=True)


# ─── RESERVATIONS ─────────────────────────────────────
def get_reservations(user_id=None, role="member"):
    if role == "admin":
        return query("""SELECT r.*, u.name as user_name, b.title as book_title, b.author
                        FROM reservations r JOIN users u ON r.user_id=u.id
                        JOIN books b ON r.book_id=b.id ORDER BY r.created_at DESC""")
    return query("""SELECT r.*, b.title as book_title, b.author
                    FROM reservations r JOIN books b ON r.book_id=b.id
                    WHERE r.user_id=%s ORDER BY r.created_at DESC""", (user_id,))


def reserve_book(user_id, book_id):
    book = get_book(book_id)
    if not book:
        return False, "Book not found."
    if book["available_copies"] < 1:
        return False, "No copies available right now."
    existing = query("""SELECT id FROM reservations WHERE user_id=%s AND book_id=%s
                        AND status IN ('reserved','borrowed')""", (user_id, book_id), fetchone=True)
    if existing:
        return False, "You already have this book reserved or borrowed."
    due_date = date.today() + timedelta(days=14)
    query("INSERT INTO reservations (user_id,book_id,due_date,status) VALUES (%s,%s,%s,'reserved')",
          (user_id, book_id, due_date), commit=True)
    query("UPDATE books SET available_copies=available_copies-1 WHERE id=%s", (book_id,), commit=True)
    return True, f"Reserved! Due: {due_date}"


def update_reservation(res_id, action):
    res = query("SELECT * FROM reservations WHERE id=%s", (res_id,), fetchone=True)
    if not res:
        return False, "Not found."
    if action == "borrow" and res["status"] == "reserved":
        query("UPDATE reservations SET status='borrowed' WHERE id=%s", (res_id,), commit=True)
        return True, "Issued to member."
    elif action == "return" and res["status"] in ("borrowed", "overdue"):
        fine = 0.0
        if res["due_date"] and date.today() > res["due_date"]:
            fine = (date.today() - res["due_date"]).days * 2.0
        query("UPDATE reservations SET status='returned',return_date=%s,fine_amount=%s WHERE id=%s",
              (date.today(), fine, res_id), commit=True)
        query("UPDATE books SET available_copies=available_copies+1 WHERE id=%s",
              (res["book_id"],), commit=True)
        msg = f"Returned. Fine: ₹{fine:.2f}" if fine else "Returned successfully."
        return True, msg
    elif action == "cancel" and res["status"] == "reserved":
        query("UPDATE reservations SET status='cancelled' WHERE id=%s", (res_id,), commit=True)
        query("UPDATE books SET available_copies=available_copies+1 WHERE id=%s",
              (res["book_id"],), commit=True)
        return True, "Reservation cancelled."
    return False, "Action not applicable."


def mark_overdue():
    query("""UPDATE reservations SET status='overdue'
             WHERE status='borrowed' AND due_date < CURDATE()""", commit=True)


# ─── DASHBOARD STATS ──────────────────────────────────
def get_stats():
    return {
        "total_books":   query("SELECT COUNT(*) as c FROM books", fetchone=True)["c"],
        "available":     query("SELECT SUM(available_copies) as c FROM books", fetchone=True)["c"] or 0,
        "total_members": query("SELECT COUNT(*) as c FROM users WHERE role='member'", fetchone=True)["c"],
        "active_borrows":query("SELECT COUNT(*) as c FROM reservations WHERE status IN ('borrowed','reserved')", fetchone=True)["c"],
        "overdue":       query("SELECT COUNT(*) as c FROM reservations WHERE status='overdue'", fetchone=True)["c"],
    }


def get_recent_activity(limit=8):
    return query("""SELECT r.id, u.name as user_name, b.title as book_title, r.status, r.due_date
                    FROM reservations r JOIN users u ON r.user_id=u.id JOIN books b ON r.book_id=b.id
                    ORDER BY r.created_at DESC LIMIT %s""", (limit,))


def get_popular_books(limit=5):
    return query("""SELECT b.title, b.author, COUNT(r.id) as borrow_count
                    FROM books b LEFT JOIN reservations r ON b.id=r.book_id
                    GROUP BY b.id ORDER BY borrow_count DESC LIMIT %s""", (limit,))


def get_user_history(user_id):
    return query("""SELECT r.*, b.title as book_title, b.author FROM reservations r
                    JOIN books b ON r.book_id=b.id WHERE r.user_id=%s ORDER BY r.created_at DESC""",
                 (user_id,))
