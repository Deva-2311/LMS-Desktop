"""
auth_window.py — Login & Register Screen
"""

import tkinter as tk
from tkinter import messagebox
from ui_components import C, PrimaryButton, GhostButton
import database as db


class AuthWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LibraryOS — Login")
        self.geometry("860x560")
        self.resizable(False, False)
        self.configure(bg=C["forest"])
        self._center()
        self._current_user = None
        self._show_login()

    def _center(self):
        self.update_idletasks()
        w, h = 860, 560
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # ── LOGIN ──────────────────────────────────────────
    def _show_login(self):
        self._clear()
        self._build_hero()
        right = tk.Frame(self, bg=C["surface"], width=400)
        right.pack(side="right", fill="both", expand=False)
        right.pack_propagate(False)

        inner = tk.Frame(right, bg=C["surface"], padx=44, pady=0)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(inner, text="Welcome back", font=("Georgia", 24, "bold"),
                 fg=C["forest"], bg=C["surface"]).pack(anchor="w")
        tk.Label(inner, text="Sign in to your library account",
                 font=("Segoe UI", 10), fg=C["ink_light"],
                 bg=C["surface"]).pack(anchor="w", pady=(4, 22))

        # Fields
        self._email_var = tk.StringVar()
        self._pw_var    = tk.StringVar()
        self._err_var   = tk.StringVar()

        self._field(inner, "EMAIL ADDRESS", self._email_var)
        self._field(inner, "PASSWORD", self._pw_var, show="●")

        self._err_label = tk.Label(inner, textvariable=self._err_var,
                                   font=("Segoe UI", 9), fg=C["rust"],
                                   bg=C["surface"])
        self._err_label.pack(anchor="w", pady=(2, 0))

        btn = PrimaryButton(inner, "  Sign In  →", self._do_login, width=22)
        btn.pack(fill="x", pady=(14, 0))

        sep = tk.Frame(inner, height=1, bg=C["border"])
        sep.pack(fill="x", pady=16)

        tk.Label(inner, text="No account?", font=("Segoe UI", 10),
                 fg=C["ink_light"], bg=C["surface"]).pack(side="left")
        lnk = tk.Label(inner, text=" Register here",
                       font=("Segoe UI", 10, "bold"),
                       fg=C["forest"], bg=C["surface"], cursor="hand2")
        lnk.pack(side="left")
        lnk.bind("<Button-1>", lambda e: self._show_register())

        # Demo hint box
        hint = tk.Frame(right, bg="#eae4d6", padx=16, pady=10)
        hint.place(relx=0.5, rely=0.94, anchor="s", relwidth=0.84)
        tk.Label(hint, text="Demo: admin@library.com / admin123",
                 font=("Segoe UI", 9), fg=C["ink_light"], bg="#eae4d6").pack()

        # Bind Enter key
        self.bind("<Return>", lambda e: self._do_login())

    def _show_register(self):
        self._clear()
        self._build_hero()
        right = tk.Frame(self, bg=C["surface"], width=400)
        right.pack(side="right", fill="both", expand=False)
        right.pack_propagate(False)

        inner = tk.Frame(right, bg=C["surface"], padx=44)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(inner, text="Create account", font=("Georgia", 24, "bold"),
                 fg=C["forest"], bg=C["surface"]).pack(anchor="w")
        tk.Label(inner, text="Register as a library member",
                 font=("Segoe UI", 10), fg=C["ink_light"],
                 bg=C["surface"]).pack(anchor="w", pady=(4, 18))

        self._r_name  = tk.StringVar()
        self._r_email = tk.StringVar()
        self._r_phone = tk.StringVar()
        self._r_pw    = tk.StringVar()
        self._r_err   = tk.StringVar()

        self._field(inner, "FULL NAME",      self._r_name)
        self._field(inner, "EMAIL ADDRESS",  self._r_email)
        self._field(inner, "PHONE NUMBER",   self._r_phone)
        self._field(inner, "PASSWORD",       self._r_pw, show="●")

        tk.Label(inner, textvariable=self._r_err,
                 font=("Segoe UI", 9), fg=C["rust"],
                 bg=C["surface"]).pack(anchor="w", pady=(2, 0))

        PrimaryButton(inner, "  Create Account  →", self._do_register,
                      width=22).pack(fill="x", pady=(10, 0))

        sep = tk.Frame(inner, height=1, bg=C["border"])
        sep.pack(fill="x", pady=12)

        tk.Label(inner, text="Already registered?",
                 font=("Segoe UI", 10), fg=C["ink_light"],
                 bg=C["surface"]).pack(side="left")
        lnk = tk.Label(inner, text=" Sign in",
                       font=("Segoe UI", 10, "bold"),
                       fg=C["forest"], bg=C["surface"], cursor="hand2")
        lnk.pack(side="left")
        lnk.bind("<Button-1>", lambda e: self._show_login())

    def _build_hero(self):
        left = tk.Frame(self, bg=C["forest"])
        left.pack(side="left", fill="both", expand=True)
        tk.Label(left, text="📚", font=("Segoe UI", 52),
                 bg=C["forest"]).pack(pady=(80, 10))
        tk.Label(left, text="LibraryOS",
                 font=("Georgia", 32, "bold"),
                 fg=C["gold_light"], bg=C["forest"]).pack()
        tk.Label(left, text="Management System",
                 font=("Segoe UI", 11),
                 fg=C["sage"], bg=C["forest"]).pack(pady=(4, 16))
        tk.Label(left,
                 text="Browse · Reserve · Manage",
                 font=("Segoe UI", 10, "italic"),
                 fg=C["moss"], bg=C["forest"]).pack()

    def _field(self, parent, label, var, show=None):
        f = tk.Frame(parent, bg=C["surface"])
        f.pack(fill="x", pady=5)
        tk.Label(f, text=label, font=("Segoe UI", 8, "bold"),
                 fg=C["ink_light"], bg=C["surface"]).pack(anchor="w")
        kw = {"show": show} if show else {}
        e = tk.Entry(f, textvariable=var, font=("Segoe UI", 11),
                     bg=C["white"], relief="flat",
                     highlightbackground=C["border"], highlightthickness=1,
                     **kw)
        e.pack(fill="x", ipady=6)
        return e

    def _do_login(self):
        email = self._email_var.get().strip()
        pw    = self._pw_var.get()
        if not email or not pw:
            self._err_var.set("Please enter email and password.")
            return
        try:
            user = db.login_user(email, pw)
        except Exception as ex:
            self._err_var.set(f"DB Error: {ex}")
            return
        if user:
            self._current_user = user
            self.destroy()
        else:
            self._err_var.set("Invalid email or password.")

    def _do_register(self):
        name  = self._r_name.get().strip()
        email = self._r_email.get().strip()
        phone = self._r_phone.get().strip()
        pw    = self._r_pw.get()
        if not name or not email or not pw:
            self._r_err.set("Name, email and password are required.")
            return
        if len(pw) < 6:
            self._r_err.set("Password must be at least 6 characters.")
            return
        try:
            ok, msg = db.register_user(name, email, pw, phone)
        except Exception as ex:
            self._r_err.set(f"DB Error: {ex}")
            return
        if ok:
            messagebox.showinfo("Success", msg + "\nPlease login.")
            self._show_login()
        else:
            self._r_err.set(msg)

    def get_user(self):
        return self._current_user
