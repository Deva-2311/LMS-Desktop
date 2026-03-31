"""
books_frame.py — Books Catalogue Tab
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ui_components import (C, PrimaryButton, GoldButton, DangerButton,
                            GhostButton, SectionTitle, make_table,
                            Toast, GENRES)
import database as db


class BooksFrame(tk.Frame):
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

        tk.Label(inner, text="Book Catalogue",
                 font=("Georgia", 16, "bold"),
                 fg=C["forest"], bg=C["card"]).pack(side="left")

        # Search
        self._search_var = tk.StringVar()
        se = tk.Entry(inner, textvariable=self._search_var,
                      font=("Segoe UI", 10), bg=C["surface"],
                      relief="flat", highlightbackground=C["border"],
                      highlightthickness=1, width=24)
        se.pack(side="left", padx=(20, 4), ipady=5)
        se.bind("<Return>", lambda e: self.refresh())
        se.insert(0, "Search title, author, ISBN…")
        se.config(fg=C["ink_light"])
        se.bind("<FocusIn>",  lambda e: (se.delete(0,"end"), se.config(fg=C["ink"])) if se.get()=="Search title, author, ISBN…" else None)
        se.bind("<FocusOut>", lambda e: (se.insert(0,"Search title, author, ISBN…"), se.config(fg=C["ink_light"])) if not se.get() else None)

        PrimaryButton(inner, "🔍 Search", self.refresh).pack(side="left", padx=2)

        # Genre filter
        self._genre_var = tk.StringVar(value="All Genres")
        genre_cb = ttk.Combobox(inner, textvariable=self._genre_var,
                                values=["All Genres"] + db.get_genres(),
                                state="readonly", width=16,
                                font=("Segoe UI", 10))
        genre_cb.pack(side="left", padx=(12, 2))
        genre_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        GhostButton(inner, "✕ Clear", self._clear_filters).pack(side="left", padx=4)

        if self._user["role"] == "admin":
            PrimaryButton(inner, "+  Add Book", self._open_book_dialog).pack(side="right")

        # Count label
        self._count_var = tk.StringVar(value="")
        tk.Label(inner, textvariable=self._count_var,
                 font=("Segoe UI", 9), fg=C["ink_light"],
                 bg=C["card"]).pack(side="right", padx=8)

        # ── Table ─────────────────────────────────────
        tbl_outer = tk.Frame(self, bg=C["card"],
                             highlightbackground=C["border"],
                             highlightthickness=1)
        tbl_outer.pack(fill="both", expand=True, padx=24, pady=12)

        cols = ["ID", "Title", "Author", "Genre", "Year", "Available", "Total", "ISBN"]
        tbl_frame, self._tree = make_table(tbl_outer, cols)
        tbl_frame.pack(fill="both", expand=True, padx=8, pady=8)

        widths = {"ID":40,"Title":220,"Author":160,"Genre":100,
                  "Year":60,"Available":80,"Total":60,"ISBN":130}
        for col in cols:
            self._tree.heading(col, text=col,
                               command=lambda c=col: self._sort_by(c))
            self._tree.column(col, width=widths.get(col,100), minwidth=40)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-1>", lambda e: self._open_book_dialog(edit=True))

        # ── Action Bar ────────────────────────────────
        action_bar = tk.Frame(self, bg=C["surface"], padx=24, pady=8)
        action_bar.pack(fill="x")

        if self._user["role"] == "member":
            GoldButton(action_bar, "🔖  Reserve Selected", self._reserve).pack(side="left", padx=4)
        else:
            GoldButton(action_bar, "✏️  Edit", lambda: self._open_book_dialog(edit=True)).pack(side="left", padx=4)
            DangerButton(action_bar, "🗑  Delete", self._delete).pack(side="left", padx=4)
            GhostButton(action_bar, "🔖  View Reservations", self._view_reservations).pack(side="left", padx=4)

        self._action_hint = tk.Label(action_bar, text="Select a row to act on it.",
                                     font=("Segoe UI", 9), fg=C["ink_light"],
                                     bg=C["surface"])
        self._action_hint.pack(side="right")

        self.refresh()

    def refresh(self):
        q = self._search_var.get().strip()
        if q in ("", "Search title, author, ISBN…"):
            q = ""
        genre = self._genre_var.get()
        if genre == "All Genres":
            genre = ""
        books = db.get_books(search=q, genre=genre)
        self._count_var.set(f"{len(books)} book{'s' if len(books)!=1 else ''}")
        self._tree.delete(*self._tree.get_children())
        for i, b in enumerate(books):
            avail = b["available_copies"]
            tag = "overdue" if avail == 0 else ("odd" if i % 2 else "even")
            self._tree.insert("", "end", iid=str(b["id"]), tags=(tag,),
                values=(b["id"], b["title"], b["author"],
                        b["genre"] or "—", b["year_published"] or "—",
                        f"{avail} / {b['total_copies']}", b["total_copies"],
                        b["isbn"] or "—"))

    def _clear_filters(self):
        self._search_var.set("")
        self._genre_var.set("All Genres")
        self.refresh()

    def _on_select(self, event):
        sel = self._tree.selection()
        self._selected_id = int(sel[0]) if sel else None
        if self._selected_id:
            book = db.get_book(self._selected_id)
            self._action_hint.config(
                text=f"Selected: {book['title'][:45]}")

    def _sort_by(self, col):
        items = [(self._tree.set(k, col), k)
                 for k in self._tree.get_children("")]
        items.sort()
        for i, (_, k) in enumerate(items):
            self._tree.move(k, "", i)

    def _reserve(self):
        if not self._selected_id:
            messagebox.showwarning("Select Book", "Please select a book first.")
            return
        ok, msg = db.reserve_book(self._user["id"], self._selected_id)
        kind = "success" if ok else "danger"
        Toast(self.winfo_toplevel(), msg, kind)
        self.refresh()

    def _delete(self):
        if not self._selected_id:
            messagebox.showwarning("Select Book", "Please select a book first.")
            return
        book = db.get_book(self._selected_id)
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete '{book['title']}'?\nThis cannot be undone."):
            return
        db.delete_book(self._selected_id)
        self._selected_id = None
        self.refresh()
        Toast(self.winfo_toplevel(), "Book deleted.", "info")

    def _view_reservations(self):
        if not self._selected_id:
            messagebox.showwarning("Select Book", "Select a book first.")
            return
        book = db.get_book(self._selected_id)
        recs = db.query("""SELECT r.*, u.name as user_name FROM reservations r
                           JOIN users u ON r.user_id=u.id WHERE r.book_id=%s
                           ORDER BY r.created_at DESC""", (self._selected_id,))
        win = tk.Toplevel(self.winfo_toplevel())
        win.title(f"Reservations — {book['title'][:40]}")
        win.geometry("640x400")
        win.configure(bg=C["surface"])
        tk.Label(win, text=book["title"], font=("Georgia", 14, "bold"),
                 fg=C["forest"], bg=C["surface"], padx=16, pady=10).pack(anchor="w")
        cols = ["Member", "Reserved", "Due", "Status", "Fine"]
        f, tree = make_table(win, cols)
        f.pack(fill="both", expand=True, padx=12, pady=8)
        for c, w in [("Member",160),("Reserved",100),("Due",100),("Status",90),("Fine",70)]:
            tree.heading(c, text=c); tree.column(c, width=w)
        for i, r in enumerate(recs):
            tag = r["status"] if r["status"] in ("overdue","returned","borrowed") else ("odd" if i%2 else "even")
            fine = f"₹{r['fine_amount']:.2f}" if r["fine_amount"] else "—"
            tree.insert("","end", values=(r["user_name"], str(r["reserved_date"]),
                                          str(r["due_date"] or "—"), r["status"], fine), tags=(tag,))

    def _open_book_dialog(self, edit=False):
        book = db.get_book(self._selected_id) if (edit and self._selected_id) else None
        if edit and not book:
            messagebox.showwarning("Select", "Select a book to edit.")
            return
        BookDialog(self.winfo_toplevel(), book, on_save=self.refresh)


class BookDialog(tk.Toplevel):
    """Add / Edit Book popup window."""
    def __init__(self, parent, book, on_save):
        super().__init__(parent)
        self._book   = book
        self._on_save = on_save
        self.title("Edit Book" if book else "Add New Book")
        self.geometry("560x580")
        self.resizable(False, False)
        self.configure(bg=C["surface"])
        self.grab_set()
        self._center(parent)
        self._build()

    def _center(self, parent):
        self.update_idletasks()
        px, py = parent.winfo_x(), parent.winfo_y()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        x = px + (pw - 560) // 2
        y = py + (ph - 580) // 2
        self.geometry(f"560x580+{x}+{y}")

    def _build(self):
        hdr = tk.Frame(self, bg=C["forest"], padx=24, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text="✏️ Edit Book" if self._book else "＋ Add New Book",
                 font=("Georgia", 15, "bold"),
                 fg=C["gold_light"], bg=C["forest"]).pack(anchor="w")

        body = tk.Frame(self, bg=C["surface"], padx=28, pady=20)
        body.pack(fill="both", expand=True)

        b = self._book or {}
        self._v = {k: tk.StringVar(value=str(b.get(k) or ""))
                   for k in ["title","author","isbn","publisher","year_published","total_copies","description"]}
        self._genre_v = tk.StringVar(value=b.get("genre",""))

        grid = tk.Frame(body, bg=C["surface"])
        grid.pack(fill="x")
        grid.columnconfigure((0,1), weight=1)

        def lf(parent, label, var, row, col, colspan=1, show=None):
            f = tk.Frame(parent, bg=C["surface"])
            f.grid(row=row, column=col, columnspan=colspan,
                   sticky="ew", padx=6, pady=5)
            tk.Label(f, text=label, font=("Segoe UI", 8,"bold"),
                     fg=C["ink_light"], bg=C["surface"]).pack(anchor="w")
            kw = {"show": show} if show else {}
            e = tk.Entry(f, textvariable=var, font=("Segoe UI", 10),
                         bg=C["white"], relief="flat",
                         highlightbackground=C["border"],
                         highlightthickness=1, **kw)
            e.pack(fill="x", ipady=5)

        lf(grid, "TITLE *",        self._v["title"],          0, 0, colspan=2)
        lf(grid, "AUTHOR(S) *",    self._v["author"],         1, 0, colspan=2)
        lf(grid, "ISBN",           self._v["isbn"],           2, 0)
        lf(grid, "YEAR PUBLISHED", self._v["year_published"], 2, 1)
        lf(grid, "PUBLISHER",      self._v["publisher"],      3, 0)
        lf(grid, "TOTAL COPIES",   self._v["total_copies"],   3, 1)

        gf = tk.Frame(grid, bg=C["surface"])
        gf.grid(row=4, column=0, columnspan=2, sticky="ew", padx=6, pady=5)
        tk.Label(gf, text="GENRE", font=("Segoe UI", 8, "bold"),
                 fg=C["ink_light"], bg=C["surface"]).pack(anchor="w")
        ttk.Combobox(gf, textvariable=self._genre_v,
                     values=GENRES, font=("Segoe UI", 10),
                     state="normal").pack(fill="x")

        df = tk.Frame(grid, bg=C["surface"])
        df.grid(row=5, column=0, columnspan=2, sticky="ew", padx=6, pady=5)
        tk.Label(df, text="DESCRIPTION", font=("Segoe UI", 8, "bold"),
                 fg=C["ink_light"], bg=C["surface"]).pack(anchor="w")
        self._desc_text = tk.Text(df, height=4, font=("Segoe UI", 10),
                                   bg=C["white"], relief="flat",
                                   highlightbackground=C["border"],
                                   highlightthickness=1, padx=6, pady=4)
        self._desc_text.pack(fill="x")
        if b.get("description"):
            self._desc_text.insert("1.0", b["description"])

        # Buttons
        btn_row = tk.Frame(body, bg=C["surface"], pady=10)
        btn_row.pack(fill="x")
        PrimaryButton(btn_row, "💾  Save Book", self._save).pack(side="left", padx=6)
        GhostButton(btn_row, "Cancel", self.destroy).pack(side="left")

    def _save(self):
        title  = self._v["title"].get().strip()
        author = self._v["author"].get().strip()
        if not title or not author:
            messagebox.showwarning("Required", "Title and Author are required.", parent=self)
            return
        try:
            copies = int(self._v["total_copies"].get() or 1)
        except ValueError:
            messagebox.showwarning("Invalid", "Total copies must be a number.", parent=self)
            return
        desc = self._desc_text.get("1.0", "end").strip()
        year = self._v["year_published"].get().strip() or None
        try:
            if self._book:
                db.update_book(self._book["id"], title, author,
                               self._v["isbn"].get().strip(),
                               self._genre_v.get().strip(),
                               self._v["publisher"].get().strip(),
                               year, copies, desc)
            else:
                db.add_book(title, author,
                            self._v["isbn"].get().strip(),
                            self._genre_v.get().strip(),
                            self._v["publisher"].get().strip(),
                            year, copies, desc)
        except Exception as e:
            messagebox.showerror("DB Error", str(e), parent=self)
            return
        self._on_save()
        self.destroy()
