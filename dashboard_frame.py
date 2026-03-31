"""
dashboard_frame.py — Dashboard Tab
"""

import tkinter as tk
from tkinter import ttk
from ui_components import C, StatCard, SectionTitle, make_table, GhostButton
import database as db


class DashboardFrame(tk.Frame):
    def __init__(self, parent, user, **kw):
        super().__init__(parent, bg=C["surface"], **kw)
        self._user = user
        self._stat_cards = {}
        self._build()

    def _build(self):
        # ── Header ────────────────────────────────────
        hdr = tk.Frame(self, bg=C["surface"])
        hdr.pack(fill="x", padx=28, pady=(24, 6))
        tk.Label(hdr, text=f"Good day, {self._user['name'].split()[0]} 👋",
                 font=("Georgia", 20, "bold"),
                 fg=C["forest"], bg=C["surface"]).pack(side="left")
        if self._user["role"] == "admin":
            btn = tk.Button(hdr, text="🔄  Check Overdue",
                            font=("Segoe UI", 9),
                            bg=C["parchment"], fg=C["forest"],
                            relief="flat", cursor="hand2",
                            padx=10, pady=5,
                            command=self._check_overdue)
            btn.pack(side="right")

        # ── Stat Cards ────────────────────────────────
        card_frame = tk.Frame(self, bg=C["surface"])
        card_frame.pack(fill="x", padx=24, pady=10)
        card_frame.columnconfigure((0, 1, 2, 3), weight=1)

        defs = [
            ("total_books",    "Total Books",    C["forest"],   "📚"),
            ("total_members",  "Members",        C["gold"],     "👥"),
            ("active_borrows", "Active Borrows", "#4caf50",     "🔖"),
            ("overdue",        "Overdue",        C["rust"],     "⚠️"),
        ]
        stats = db.get_stats()
        for col, (key, label, accent, icon) in enumerate(defs):
            card = StatCard(card_frame, label, stats.get(key, 0),
                            accent, icon)
            card.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")
            self._stat_cards[key] = card

        # ── Two-column section ────────────────────────
        two_col = tk.Frame(self, bg=C["surface"])
        two_col.pack(fill="both", expand=True, padx=24, pady=8)
        two_col.columnconfigure(0, weight=3)
        two_col.columnconfigure(1, weight=2)
        two_col.rowconfigure(0, weight=1)

        # Recent Activity table
        left_box = tk.Frame(two_col, bg=C["card"],
                            highlightbackground=C["border"],
                            highlightthickness=1)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        lhdr = tk.Frame(left_box, bg=C["card"], padx=16, pady=12)
        lhdr.pack(fill="x")
        tk.Label(lhdr, text="Recent Activity",
                 font=("Georgia", 13, "bold"),
                 fg=C["forest"], bg=C["card"]).pack(side="left")

        cols = ["#", "Member", "Book", "Status", "Due"] if self._user["role"] == "admin" \
               else ["#", "Book", "Status", "Due"]
        tbl_frame, self._activity_tree = make_table(left_box, cols)
        tbl_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        widths = {"#": 40, "Member": 120, "Book": 200, "Status": 90, "Due": 90}
        for col in cols:
            self._activity_tree.heading(col, text=col)
            self._activity_tree.column(col, width=widths.get(col, 100),
                                       minwidth=40, anchor="w")

        # Popular books
        right_box = tk.Frame(two_col, bg=C["card"],
                             highlightbackground=C["border"],
                             highlightthickness=1)
        right_box.grid(row=0, column=1, sticky="nsew")
        rhdr = tk.Frame(right_box, bg=C["card"], padx=16, pady=12)
        rhdr.pack(fill="x")
        tk.Label(rhdr, text="Popular Books",
                 font=("Georgia", 13, "bold"),
                 fg=C["forest"], bg=C["card"]).pack(side="left")

        pop_frame, self._pop_tree = make_table(right_box, ["#", "Title", "Author", "Borrows"])
        pop_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        for c, w in [("#", 30), ("Title", 160), ("Author", 120), ("Borrows", 60)]:
            self._pop_tree.heading(c, text=c)
            self._pop_tree.column(c, width=w, minwidth=30)

        self.refresh()

    def refresh(self):
        stats = db.get_stats()
        for key, card in self._stat_cards.items():
            card.update_value(stats.get(key, 0))

        # Activity
        self._activity_tree.delete(*self._activity_tree.get_children())
        for i, r in enumerate(db.get_recent_activity()):
            tag = r["status"] if r["status"] in ("overdue", "returned", "borrowed") else ("odd" if i%2 else "even")
            if self._user["role"] == "admin":
                vals = (r["id"], r["user_name"], r["book_title"][:30], r["status"], str(r["due_date"] or "—"))
            else:
                vals = (r["id"], r["book_title"][:35], r["status"], str(r["due_date"] or "—"))
            self._activity_tree.insert("", "end", values=vals, tags=(tag,))

        # Popular
        self._pop_tree.delete(*self._pop_tree.get_children())
        for i, b in enumerate(db.get_popular_books()):
            tag = "odd" if i % 2 else "even"
            self._pop_tree.insert("", "end",
                values=(i+1, b["title"][:25], b["author"][:18], b["borrow_count"]),
                tags=(tag,))

    def _check_overdue(self):
        db.mark_overdue()
        self.refresh()
        from tkinter import messagebox
        messagebox.showinfo("Done", "Overdue status updated.")
