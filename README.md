# 📚 LibraryOS — Desktop Application

A full-featured Library Management System as a **native desktop app**
built with **Python + Tkinter** (GUI), connected to **MySQL** via **mysql-connector-python**.

> No browser. No server. Just double-click and run.

---

## 🗂️ Project Structure

```
library_desktop/
├── main.py                ← Entry point — run this
├── database.py            ← All MySQL queries (update credentials here)
├── ui_components.py       ← Reusable widgets, theme, color palette
├── auth_window.py         ← Login & Register window
├── dashboard_frame.py     ← Dashboard tab (stats, activity, popular books)
├── books_frame.py         ← Books catalogue, search, add/edit/delete
├── reservations_frame.py  ← Reservations management
├── users_frame.py         ← Members management (admin only)
├── profile_frame.py       ← Profile editor & borrow history
└── requirements.txt       ← pip dependencies
```

> The `schema.sql` and `setup_users.py` files from the web project
> are shared — use the same database.

---

## ⚙️ Setup Instructions

### 1. Install dependencies
```bash
pip install -r requirements.txt
```
> **Note:** `tkinter` is built into Python on Windows and most Linux distros.
> On Ubuntu/Debian if missing: `sudo apt install python3-tk`

### 2. Set up the database (skip if already done for web version)
```bash
mysql -u root -p < ../library_mgmt/schema.sql
python ../library_mgmt/setup_users.py
```

### 3. Update DB credentials
Open `database.py` and change:
```python
DB_CONFIG = {
    "host": "localhost",
    "database": "library_db",
    "user": "root",
    "password": "yourpassword",   # ← YOUR MySQL password
}
```

### 4. Run!
```bash
python main.py
```

---

## 🔑 Demo Login Credentials

| Role   | Email                 | Password  |
|--------|-----------------------|-----------|
| Admin  | admin@library.com     | admin123  |
| Member | arjun@email.com       | member123 |

---

## ✨ Features

### Desktop UI
- Native window (no browser needed)
- Sidebar navigation with active state highlighting
- Sortable, scrollable tables with color-coded rows
- Toast notifications (auto-dismiss after 3 seconds)
- Popup dialogs for add/edit forms
- Responsive layout (resizable window, min 900×600)
- Forest-green & gold editorial theme

### Functionality (same as web version)
| Feature | Admin | Member |
|---|---|---|
| Dashboard with live stats | ✅ | ✅ |
| Browse & search books | ✅ | ✅ |
| Reserve books | — | ✅ |
| Add / Edit / Delete books | ✅ | — |
| Issue books (reserved→borrowed) | ✅ | — |
| Process returns + auto-fine | ✅ | — |
| Cancel reservations | ✅ | — |
| Manage members (activate/promote) | ✅ | — |
| View borrow history | ✅ | ✅ |
| Edit own profile | ✅ | ✅ |
| Check overdue status | ✅ | — |

---

## 🧩 Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| GUI      | Python Tkinter + ttk (built-in)     |
| Backend  | Pure Python (no web framework)      |
| Database | MySQL 8.0                           |
| DB Layer | mysql-connector-python              |
| Auth     | Werkzeug password hashing           |

---

## 📌 Notes

- All passwords hashed with PBKDF2-SHA256
- Fine: ₹2 per overdue day (calculated on return)
- The app checks DB connectivity on launch and shows a helpful error if misconfigured
- Shared database with the web version — both can run simultaneously
# LMS-Desktop
