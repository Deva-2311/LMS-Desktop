"""
users_frame.py — Members Management Tab (Admin only)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import (C, PrimaryButton, GhostButton,
                            GoldButton, DangerButton, make_table, Toast)
import database as db


class UsersFrame(tk.Frame):
    def __init__(self, parent, user, **kw):
        super().__init__(parent, bg=C["surface"], **kw)
        self._user = user
        self._selected_id = None
        self._build()

    def _build(self):
        # ── Toolbar ───────────────────────────────────
        toolbar = tk.Frame(self, bg=C["card"],
                           highlightbackground=C["border"],
                           highlightthickness=1)
        toolbar.pack(fill="x", padx=24, pady=(20, 0))

        inner = tk.Frame(toolbar, bg=C["card"], padx=16, pady=12)
        inner.pack(fill="x")

        tk.Label(inner, text="Library Members",
                 font=("Georgia", 16, "bold"),
                 fg=C["forest"], bg=C["card"]).pack(side="left")

        self._search_var = tk.StringVar()
        se = tk.Entry(inner, textvariable=self._search_var,
                      font=("Segoe UI", 10), bg=C["surface"],
                      relief="flat", highlightbackground=C["border"],
                      highlightthickness=1, width=22)
        se.pack(side="left", padx=(20, 4), ipady=5)
        se.bind("<Return>", lambda e: self.refresh())

        PrimaryButton(inner, "🔍 Search", self.refresh).pack(side="left", padx=2)
        GhostButton(inner, "✕", self._clear).pack(side="left", padx=2)

        self._count_var = tk.StringVar()
        tk.Label(inner, textvariable=self._count_var,
                 font=("Segoe UI", 9), fg=C["ink_light"],
                 bg=C["card"]).pack(side="right")

        # ── Table ─────────────────────────────────────
        tbl_outer = tk.Frame(self, bg=C["card"],
                             highlightbackground=C["border"],
                             highlightthickness=1)
        tbl_outer.pack(fill="both", expand=True, padx=24, pady=12)

        cols = ["ID","Name","Email","Phone","Role","Joined","Status"]
        f, self._tree = make_table(tbl_outer, cols)
        f.pack(fill="both", expand=True, padx=8, pady=8)

        widths = {"ID":40,"Name":160,"Email":200,"Phone":120,
                  "Role":80,"Joined":100,"Status":80}
        for col in cols:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=widths.get(col,100), minwidth=36)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Action Bar ────────────────────────────────
        action_bar = tk.Frame(self, bg=C["surface"], padx=24, pady=8)
        action_bar.pack(fill="x")

        GhostButton(action_bar, "🔒 Toggle Active/Inactive",
                    self._toggle).pack(side="left", padx=4)
        GoldButton(action_bar, "⬆ Toggle Role",
                   self._promote).pack(side="left", padx=4)
        GhostButton(action_bar, "📋 View History",
                    self._view_history).pack(side="left", padx=4)

        self._hint = tk.Label(action_bar, text="Select a member to manage.",
                              font=("Segoe UI", 9), fg=C["ink_light"],
                              bg=C["surface"])
        self._hint.pack(side="right")

        self.refresh()

    def refresh(self):
        q = self._search_var.get().strip()
        users = db.get_users(search=q)
        self._count_var.set(f"{len(users)} users")
        self._tree.delete(*self._tree.get_children())
        for i, u in enumerate(users):
            is_active = "✅ Active" if u["is_active"] else "🔒 Inactive"
            tag = "odd" if i % 2 else "even"
            self._tree.insert("","end", iid=str(u["id"]), tags=(tag,),
                values=(u["id"], u["name"], u["email"],
                        u["phone"] or "—", u["role"].upper(),
                        str(u["joined_date"] or "—"), is_active))

    def _clear(self):
        self._search_var.set("")
        self.refresh()

    def _on_select(self, event):
        sel = self._tree.selection()
        self._selected_id = int(sel[0]) if sel else None
        if self._selected_id:
            vals = self._tree.item(sel[0], "values")
            self._hint.config(text=f"Selected: {vals[1]} ({vals[4]})")

    def _toggle(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Select a member first.")
            return
        if self._selected_id == self._user["id"]:
            messagebox.showwarning("Not Allowed", "You cannot deactivate yourself.")
            return
        db.toggle_user(self._selected_id)
        self.refresh()
        Toast(self.winfo_toplevel(), "User status updated.", "info")

    def _promote(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Select a member first.")
            return
        if self._selected_id == self._user["id"]:
            messagebox.showwarning("Not Allowed", "You cannot change your own role.")
            return
        db.promote_user(self._selected_id)
        self.refresh()
        Toast(self.winfo_toplevel(), "Role updated.", "success")

    def _view_history(self):
        if not self._selected_id:
            messagebox.showwarning("Select", "Select a member first.")
            return
        hist = db.get_user_history(self._selected_id)
        vals = self._tree.item(str(self._selected_id), "values")
        name = vals[1] if vals else "Member"

        win = tk.Toplevel(self.winfo_toplevel())
        win.title(f"Borrow History — {name}")
        win.geometry("640x400")
        win.configure(bg=C["surface"])
        tk.Label(win, text=f"Borrow History: {name}",
                 font=("Georgia", 14, "bold"),
                 fg=C["forest"], bg=C["surface"], padx=16, pady=10).pack(anchor="w")
        cols = ["Book","Author","Reserved","Due","Return","Status","Fine"]
        f, tree = make_table(win, cols)
        f.pack(fill="both", expand=True, padx=12, pady=8)
        for c, w in [("Book",180),("Author",130),("Reserved",90),
                     ("Due",90),("Return",90),("Status",80),("Fine",70)]:
            tree.heading(c, text=c)
            tree.column(c, width=w)
        for i, r in enumerate(hist):
            tag = r["status"] if r["status"] in ("overdue","returned","borrowed") else ("odd" if i%2 else "even")
            fine = f"₹{r['fine_amount']:.2f}" if r.get("fine_amount") else "—"
            tree.insert("","end", tags=(tag,),
                        values=(r["book_title"][:25], r["author"][:18],
                                str(r["reserved_date"]), str(r["due_date"] or "—"),
                                str(r["return_date"] or "—"), r["status"], fine))
