"""
reservations_frame.py — Reservations Tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
from ui_components import (C, PrimaryButton, GoldButton,
                            GhostButton, make_table, Toast)
import database as db


class ReservationsFrame(tk.Frame):
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

        title = "All Reservations" if self._user["role"] == "admin" else "My Reservations"
        tk.Label(inner, text=title,
                 font=("Georgia", 16, "bold"),
                 fg=C["forest"], bg=C["card"]).pack(side="left")

        # Status filter
        self._status_var = tk.StringVar(value="All")
        ttk.Combobox(inner,
                     textvariable=self._status_var,
                     values=["All","reserved","borrowed","overdue","returned","cancelled"],
                     state="readonly", width=14,
                     font=("Segoe UI", 10)).pack(side="left", padx=16)
        self._status_var.trace_add("write", lambda *_: self.refresh())

        self._count_var = tk.StringVar()
        tk.Label(inner, textvariable=self._count_var,
                 font=("Segoe UI", 9), fg=C["ink_light"],
                 bg=C["card"]).pack(side="right")

        # ── Table ─────────────────────────────────────
        tbl_outer = tk.Frame(self, bg=C["card"],
                             highlightbackground=C["border"],
                             highlightthickness=1)
        tbl_outer.pack(fill="both", expand=True, padx=24, pady=12)

        if self._user["role"] == "admin":
            cols = ["ID","Member","Book","Author","Reserved","Due","Status","Fine"]
        else:
            cols = ["ID","Book","Author","Reserved","Due","Status","Fine"]

        f, self._tree = make_table(tbl_outer, cols)
        f.pack(fill="both", expand=True, padx=8, pady=8)

        widths = {"ID":40,"Member":130,"Book":200,"Author":130,
                  "Reserved":95,"Due":95,"Status":90,"Fine":70}
        for col in cols:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=widths.get(col, 100), minwidth=36)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Action Bar ────────────────────────────────
        if self._user["role"] == "admin":
            action_bar = tk.Frame(self, bg=C["surface"], padx=24, pady=8)
            action_bar.pack(fill="x")
            GoldButton(action_bar, "📤  Issue Book",
                       lambda: self._act("borrow")).pack(side="left", padx=4)
            PrimaryButton(action_bar, "↩  Mark Returned",
                          lambda: self._act("return")).pack(side="left", padx=4)
            GhostButton(action_bar, "✕  Cancel",
                        lambda: self._act("cancel")).pack(side="left", padx=4)
            self._hint = tk.Label(action_bar, text="Select a reservation to take action.",
                                  font=("Segoe UI", 9), fg=C["ink_light"],
                                  bg=C["surface"])
            self._hint.pack(side="right")

        self.refresh()

    def refresh(self):
        recs = db.get_reservations(self._user["id"], self._user["role"])
        status_filter = self._status_var.get()
        if status_filter != "All":
            recs = [r for r in recs if r["status"] == status_filter]
        self._count_var.set(f"{len(recs)} record{'s' if len(recs)!=1 else ''}")
        self._tree.delete(*self._tree.get_children())
        for i, r in enumerate(recs):
            status = r["status"]
            tag = status if status in ("overdue","returned","borrowed") else ("odd" if i%2 else "even")
            fine = f"₹{r['fine_amount']:.2f}" if r.get("fine_amount") else "—"
            if self._user["role"] == "admin":
                vals = (r["id"], r["user_name"], r["book_title"][:28],
                        r["author"][:18], str(r["reserved_date"]),
                        str(r["due_date"] or "—"), status, fine)
            else:
                vals = (r["id"], r["book_title"][:32],
                        r["author"][:20], str(r["reserved_date"]),
                        str(r["due_date"] or "—"), status, fine)
            self._tree.insert("", "end", iid=str(r["id"]),
                               values=vals, tags=(tag,))

    def _on_select(self, event):
        sel = self._tree.selection()
        self._selected_id = int(sel[0]) if sel else None
        if self._user["role"] == "admin" and self._selected_id and hasattr(self, "_hint"):
            vals = self._tree.item(sel[0], "values")
            self._hint.config(text=f"ID {self._selected_id} — {vals[2] if len(vals)>2 else ''}")

    def _act(self, action):
        if not self._selected_id:
            messagebox.showwarning("Select", "Please select a reservation first.")
            return
        ok, msg = db.update_reservation(self._selected_id, action)
        Toast(self.winfo_toplevel(), msg, "success" if ok else "danger")
        self._selected_id = None
        self.refresh()
