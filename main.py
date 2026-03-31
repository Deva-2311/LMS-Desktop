"""
main.py — LibraryOS Desktop Application
========================================
Run:  python main.py
Requires: Python 3.8+, mysql-connector-python, werkzeug
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import C, apply_theme, SidebarButton
from auth_window import AuthWindow
from dashboard_frame import DashboardFrame
from books_frame import BooksFrame
from reservations_frame import ReservationsFrame
from users_frame import UsersFrame
from profile_frame import ProfileFrame
import database as db


class LibraryApp(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self._user = user
        self.title("LibraryOS — Library Management System")
        self.geometry("1200x720")
        self.minsize(900, 600)
        self.configure(bg=C["forest"])
        apply_theme(self)
        self._center()
        self._frames = {}
        self._nav_btns = {}
        self._active_tab = None
        self._build_ui()
        self._navigate("dashboard")

    def _center(self):
        self.update_idletasks()
        w, h = 1200, 720
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # ── SIDEBAR ───────────────────────────────────
        self._sidebar = tk.Frame(self, bg=C["forest"], width=230)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Brand
        brand = tk.Frame(self._sidebar, bg=C["forest"], padx=18, pady=20)
        brand.pack(fill="x")
        tk.Label(brand, text="📚", font=("Segoe UI", 28),
                 bg=C["forest"]).pack(side="left", padx=(0,10))
        tk.Frame(brand, bg=C["forest"]).pack(side="left")
        name_frame = tk.Frame(brand, bg=C["forest"])
        name_frame.pack(side="left")
        tk.Label(name_frame, text="LibraryOS",
                 font=("Georgia", 16, "bold"),
                 fg=C["gold_light"], bg=C["forest"]).pack(anchor="w")
        tk.Label(name_frame, text="Management System",
                 font=("Segoe UI", 8),
                 fg=C["sage"], bg=C["forest"]).pack(anchor="w")

        # Separator
        tk.Frame(self._sidebar, bg=C["forest_mid"], height=1).pack(fill="x", padx=12)

        # Nav buttons
        nav_frame = tk.Frame(self._sidebar, bg=C["forest"], pady=10)
        nav_frame.pack(fill="x")

        nav_items = [
            ("dashboard",    "Dashboard",    "▪"),
            ("books",        "Books",        "📖"),
            ("reservations", "Reservations", "🔖"),
        ]
        if self._user["role"] == "admin":
            nav_items.append(("members", "Members", "👥"))
        nav_items.append(("profile", "Profile", "👤"))

        for key, label, icon in nav_items:
            btn = SidebarButton(nav_frame, label, icon,
                                command=lambda k=key: self._navigate(k))
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_btns[key] = btn

        # Spacer
        tk.Frame(self._sidebar, bg=C["forest"]).pack(fill="both", expand=True)

        # Separator
        tk.Frame(self._sidebar, bg=C["forest_mid"], height=1).pack(fill="x", padx=12)

        # User pill
        user_frame = tk.Frame(self._sidebar, bg=C["forest"], padx=14, pady=12)
        user_frame.pack(fill="x")

        av = tk.Label(user_frame, text=self._user["name"][0].upper(),
                      font=("Georgia", 13, "bold"),
                      fg=C["forest"], bg=C["gold"],
                      width=2, height=1, padx=4)
        av.pack(side="left", padx=(0, 8))

        inf = tk.Frame(user_frame, bg=C["forest"])
        inf.pack(side="left")
        tk.Label(inf, text=self._user["name"].split()[0],
                 font=("Segoe UI", 11, "bold"),
                 fg=C["white"], bg=C["forest"]).pack(anchor="w")
        role_col = C["gold"] if self._user["role"]=="admin" else C["sage"]
        tk.Label(inf, text=self._user["role"],
                 font=("Segoe UI", 9),
                 fg=role_col, bg=C["forest"]).pack(anchor="w")

        # Logout
        logout = tk.Label(self._sidebar, text="↩  Logout",
                          font=("Segoe UI", 9), cursor="hand2",
                          fg="#e8a088", bg=C["forest"],
                          padx=16, pady=8, anchor="w")
        logout.pack(fill="x")
        logout.bind("<Button-1>", lambda e: self._logout())
        logout.bind("<Enter>", lambda e: logout.config(bg="#7a1c10"))
        logout.bind("<Leave>", lambda e: logout.config(bg=C["forest"]))

        # ── MAIN CONTENT ──────────────────────────────
        self._content = tk.Frame(self, bg=C["surface"])
        self._content.pack(side="right", fill="both", expand=True)

    def _navigate(self, tab_key):
        # Update sidebar active state
        if self._active_tab and self._active_tab in self._nav_btns:
            self._nav_btns[self._active_tab].set_active(False)
        if tab_key in self._nav_btns:
            self._nav_btns[tab_key].set_active(True)
        self._active_tab = tab_key

        # Hide all frames
        for f in self._frames.values():
            f.pack_forget()

        # Build or show the frame
        if tab_key not in self._frames:
            self._frames[tab_key] = self._build_frame(tab_key)

        frame = self._frames[tab_key]
        if frame:
            frame.pack(fill="both", expand=True)
            if hasattr(frame, "refresh"):
                frame.refresh()

    def _build_frame(self, key):
        parent = self._content
        if key == "dashboard":
            return DashboardFrame(parent, self._user)
        elif key == "books":
            return BooksFrame(parent, self._user)
        elif key == "reservations":
            return ReservationsFrame(parent, self._user)
        elif key == "members":
            return UsersFrame(parent, self._user)
        elif key == "profile":
            return ProfileFrame(parent, self._user,
                                on_logout=self._logout)
        return None

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()
            _run_auth()

    def refresh_current(self):
        if self._active_tab and self._active_tab in self._frames:
            f = self._frames[self._active_tab]
            if hasattr(f, "refresh"):
                f.refresh()


def _run_auth():
    """Show login window and return logged-in user."""
    auth = AuthWindow()
    auth.mainloop()
    return auth.get_user()


def main():
    # Test DB connection first
    try:
        db.get_stats()
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Database Error",
            f"Cannot connect to MySQL database.\n\n"
            f"Error: {e}\n\n"
            f"Please:\n"
            f"1. Open database.py\n"
            f"2. Update DB_CONFIG with your MySQL credentials\n"
            f"3. Run the schema.sql file\n"
            f"4. Run setup_users.py to hash passwords"
        )
        root.destroy()
        return

    user = _run_auth()
    if user:
        app = LibraryApp(user)
        app.mainloop()


if __name__ == "__main__":
    main()
