"""
profile_frame.py — Profile & Settings Tab
"""

import tkinter as tk
from tkinter import messagebox
from ui_components import (C, PrimaryButton, GhostButton,
                            make_table, Toast, StatCard)
import database as db


class ProfileFrame(tk.Frame):
    def __init__(self, parent, user, on_logout, **kw):
        super().__init__(parent, bg=C["surface"], **kw)
        self._user     = user
        self._on_logout = on_logout
        self._build()

    def _build(self):
        # ── Two pane layout ───────────────────────────
        outer = tk.Frame(self, bg=C["surface"])
        outer.pack(fill="both", expand=True, padx=24, pady=20)
        outer.columnconfigure(0, weight=0, minsize=280)
        outer.columnconfigure(1, weight=1)
        outer.rowconfigure(0, weight=1)

        # ── LEFT: Profile card ────────────────────────
        left = tk.Frame(outer, bg=C["surface"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0,16))

        # Avatar card
        avatar_card = tk.Frame(left, bg=C["card"],
                               highlightbackground=C["border"],
                               highlightthickness=1, padx=20, pady=24)
        avatar_card.pack(fill="x")

        av = tk.Label(avatar_card, text=self._user["name"][0].upper(),
                      font=("Georgia", 28, "bold"),
                      fg=C["gold_light"], bg=C["forest"],
                      width=3, height=1)
        av.pack(pady=(0, 10))

        tk.Label(avatar_card, text=self._user["name"],
                 font=("Georgia", 15, "bold"),
                 fg=C["forest"], bg=C["card"]).pack()
        tk.Label(avatar_card, text=self._user["email"],
                 font=("Segoe UI", 10), fg=C["ink_light"],
                 bg=C["card"]).pack(pady=(2,4))

        role_color = C["gold"] if self._user["role"] == "admin" else C["moss"]
        tk.Label(avatar_card, text=self._user["role"].upper(),
                 font=("Segoe UI", 9, "bold"),
                 fg=role_color, bg=C["card"],
                 padx=10, pady=4).pack()

        # Mini stats
        hist = db.get_user_history(self._user["id"])
        returned = sum(1 for r in hist if r["status"] == "returned")
        active   = sum(1 for r in hist if r["status"] in ("borrowed","reserved"))
        total_fine = sum(r["fine_amount"] or 0 for r in hist)

        stats_frame = tk.Frame(left, bg=C["surface"])
        stats_frame.pack(fill="x", pady=10)
        stats_frame.columnconfigure((0,1), weight=1)

        def mini_stat(parent, row, col, val, lbl, accent):
            f = tk.Frame(parent, bg=C["card"],
                         highlightbackground=C["border"],
                         highlightthickness=1, padx=12, pady=10)
            f.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            tk.Label(f, text=str(val), font=("Georgia", 22, "bold"),
                     fg=accent, bg=C["card"]).pack()
            tk.Label(f, text=lbl, font=("Segoe UI", 9),
                     fg=C["ink_light"], bg=C["card"]).pack()

        mini_stat(stats_frame, 0, 0, returned,    "Returned", C["forest"])
        mini_stat(stats_frame, 0, 1, active,       "Active",   "#4caf50")
        mini_stat(stats_frame, 1, 0, len(hist),    "Total",    C["ink_mid"])
        mini_stat(stats_frame, 1, 1, f"₹{total_fine:.0f}", "Fines", C["rust"])

        # Edit form
        edit_card = tk.Frame(left, bg=C["card"],
                             highlightbackground=C["border"],
                             highlightthickness=1, padx=18, pady=16)
        edit_card.pack(fill="x", pady=(6,0))
        tk.Label(edit_card, text="Update Profile",
                 font=("Georgia", 12, "bold"),
                 fg=C["forest"], bg=C["card"]).pack(anchor="w", pady=(0,10))

        user_full = db.query("SELECT * FROM users WHERE id=%s",
                             (self._user["id"],), fetchone=True)
        self._n  = tk.StringVar(value=user_full["name"])
        self._ph = tk.StringVar(value=user_full["phone"] or "")
        self._ad = tk.StringVar(value=user_full["address"] or "")
        self._pw = tk.StringVar()

        for label, var, show in [
            ("FULL NAME", self._n, None),
            ("PHONE",     self._ph, None),
            ("ADDRESS",   self._ad, None),
            ("NEW PASSWORD (leave blank to keep)", self._pw, "●"),
        ]:
            f = tk.Frame(edit_card, bg=C["card"])
            f.pack(fill="x", pady=4)
            tk.Label(f, text=label, font=("Segoe UI", 8,"bold"),
                     fg=C["ink_light"], bg=C["card"]).pack(anchor="w")
            kw = {"show": show} if show else {}
            tk.Entry(f, textvariable=var, font=("Segoe UI", 10),
                     bg=C["white"], relief="flat",
                     highlightbackground=C["border"],
                     highlightthickness=1, **kw).pack(fill="x", ipady=5)

        PrimaryButton(edit_card, "💾  Save Changes", self._save).pack(fill="x", pady=(10,0))

        # Logout button
        logout_frame = tk.Frame(left, bg=C["surface"])
        logout_frame.pack(fill="x", pady=8)
        tk.Button(logout_frame, text="↩  Logout",
                  font=("Segoe UI", 10),
                  bg="#fde8e8", fg=C["rust"],
                  relief="flat", bd=0, cursor="hand2",
                  padx=14, pady=8,
                  command=self._on_logout).pack(fill="x")

        # ── RIGHT: Borrow History ──────────────────────
        right = tk.Frame(outer, bg=C["surface"])
        right.grid(row=0, column=1, sticky="nsew")

        right_card = tk.Frame(right, bg=C["card"],
                              highlightbackground=C["border"],
                              highlightthickness=1)
        right_card.pack(fill="both", expand=True)

        hdr = tk.Frame(right_card, bg=C["card"], padx=16, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Borrow History",
                 font=("Georgia", 13, "bold"),
                 fg=C["forest"], bg=C["card"]).pack(side="left")
        tk.Label(hdr, text=f"{len(hist)} records",
                 font=("Segoe UI", 9), fg=C["ink_light"],
                 bg=C["card"]).pack(side="right")

        cols = ["Book","Author","Reserved","Due","Return","Status","Fine"]
        f, tree = make_table(right_card, cols)
        f.pack(fill="both", expand=True, padx=8, pady=(0,8))
        for c, w in [("Book",200),("Author",130),("Reserved",90),
                     ("Due",90),("Return",90),("Status",80),("Fine",70)]:
            tree.heading(c, text=c)
            tree.column(c, width=w)
        for i, r in enumerate(hist):
            tag = r["status"] if r["status"] in ("overdue","returned","borrowed") else ("odd" if i%2 else "even")
            fine = f"₹{r['fine_amount']:.2f}" if r.get("fine_amount") else "—"
            tree.insert("","end", tags=(tag,),
                        values=(r["book_title"][:28], r["author"][:18],
                                str(r["reserved_date"]), str(r["due_date"] or "—"),
                                str(r["return_date"] or "—"), r["status"], fine))

    def _save(self):
        name    = self._n.get().strip()
        phone   = self._ph.get().strip()
        address = self._ad.get().strip()
        new_pw  = self._pw.get()
        if not name:
            messagebox.showwarning("Required", "Name cannot be empty.")
            return
        if new_pw and len(new_pw) < 6:
            messagebox.showwarning("Password", "Password must be at least 6 characters.")
            return
        db.update_profile(self._user["id"], name, phone, address,
                          new_pw if new_pw else None)
        self._user["name"] = name
        self._pw.set("")
        Toast(self.winfo_toplevel(), "Profile updated!", "success")

    def refresh(self):
        pass  # re-open tab to see updated stats
