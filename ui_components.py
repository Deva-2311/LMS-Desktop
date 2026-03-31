"""
ui_components.py — Reusable Tkinter Widgets & Theme
Forest-Green + Gold editorial theme
"""

import tkinter as tk
from tkinter import ttk, font as tkfont


# ─── COLOR PALETTE ────────────────────────────────────
C = {
    "forest":        "#1a2e1f",
    "forest_mid":    "#2d4a35",
    "forest_light":  "#3d6147",
    "moss":          "#5a7a60",
    "sage":          "#8aaa8f",
    "mint":          "#c4dbc8",
    "cream":         "#f5f0e8",
    "parchment":     "#ede5d5",
    "gold":          "#c9a84c",
    "gold_light":    "#e8c96a",
    "rust":          "#b85c38",
    "white":         "#ffffff",
    "surface":       "#f6f2ea",
    "card":          "#ffffff",
    "border":        "#ddd5c5",
    "ink":           "#1c1c1e",
    "ink_mid":       "#3a3a3c",
    "ink_light":     "#7a7870",
    "success_bg":    "#e8f5e9",
    "success_fg":    "#2e7d32",
    "danger_bg":     "#fdecea",
    "danger_fg":     "#c62828",
    "warn_bg":       "#fff8e1",
    "warn_fg":       "#e65100",
    "info_bg":       "#e3f2fd",
    "info_fg":       "#1565c0",
}

STATUS_COLORS = {
    "reserved":  ("#d0e8ff", "#1565c0"),
    "borrowed":  ("#fff3cd", "#92550a"),
    "returned":  ("#d4edda", "#1a5c2a"),
    "overdue":   ("#fde8e8", "#9b1c1c"),
    "cancelled": ("#ede8f5", "#5b2d8e"),
}

GENRES = ["Technology", "Fiction", "Non-Fiction", "Autobiography",
          "History", "Science", "Self-Help", "Finance", "Philosophy", "Other"]


def apply_theme(root):
    """Apply ttk styles globally."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
        background=C["surface"],
        foreground=C["ink"],
        font=("Segoe UI", 10),
        fieldbackground=C["white"],
        borderwidth=0,
        relief="flat",
    )
    # Treeview
    style.configure("Treeview",
        background=C["white"],
        foreground=C["ink"],
        fieldbackground=C["white"],
        rowheight=36,
        font=("Segoe UI", 10),
        borderwidth=0,
    )
    style.configure("Treeview.Heading",
        background=C["surface"],
        foreground=C["ink_light"],
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        padding=(8, 6),
    )
    style.map("Treeview",
        background=[("selected", C["forest_light"])],
        foreground=[("selected", C["white"])],
    )
    # Scrollbar
    style.configure("Vertical.TScrollbar",
        background=C["border"],
        troughcolor=C["surface"],
        borderwidth=0,
        arrowsize=12,
    )
    style.configure("Horizontal.TScrollbar",
        background=C["border"],
        troughcolor=C["surface"],
        borderwidth=0,
        arrowsize=12,
    )
    # Entry
    style.configure("TEntry",
        fieldbackground=C["white"],
        borderwidth=1,
        relief="flat",
        padding=6,
    )
    style.configure("TCombobox",
        fieldbackground=C["white"],
        background=C["white"],
        arrowcolor=C["forest"],
    )
    # Notebook (tabs)
    style.configure("TNotebook",
        background=C["surface"],
        borderwidth=0,
    )
    style.configure("TNotebook.Tab",
        background=C["surface"],
        foreground=C["ink_light"],
        padding=(16, 8),
        font=("Segoe UI", 10),
        borderwidth=0,
    )
    style.map("TNotebook.Tab",
        background=[("selected", C["white"])],
        foreground=[("selected", C["forest"])],
    )
    return style


# ─── HELPER WIDGETS ───────────────────────────────────

class SidebarButton(tk.Label):
    """Flat sidebar nav button."""
    def __init__(self, parent, text, icon, command, **kw):
        super().__init__(parent,
            text=f"  {icon}  {text}",
            font=("Segoe UI", 11),
            fg=C["mint"],
            bg=C["forest"],
            cursor="hand2",
            anchor="w",
            padx=8, pady=10,
            **kw
        )
        self._cmd = command
        self._active = False
        self.bind("<Button-1>", lambda e: command())
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def set_active(self, active):
        self._active = active
        if active:
            self.config(bg=C["forest_light"], fg=C["gold_light"], font=("Segoe UI", 11, "bold"))
        else:
            self.config(bg=C["forest"], fg=C["mint"], font=("Segoe UI", 11))

    def _on_enter(self, e):
        if not self._active:
            self.config(bg=C["forest_mid"])

    def _on_leave(self, e):
        if not self._active:
            self.config(bg=C["forest"])


class PrimaryButton(tk.Button):
    def __init__(self, parent, text, command, width=None, **kw):
        super().__init__(parent,
            text=text, command=command,
            bg=C["forest"], fg=C["white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat", bd=0,
            cursor="hand2",
            padx=18, pady=8,
            activebackground=C["forest_mid"],
            activeforeground=C["white"],
            **kw
        )
        if width:
            self.config(width=width)
        self.bind("<Enter>", lambda e: self.config(bg=C["forest_mid"]))
        self.bind("<Leave>", lambda e: self.config(bg=C["forest"]))


class GoldButton(tk.Button):
    def __init__(self, parent, text, command, **kw):
        super().__init__(parent,
            text=text, command=command,
            bg=C["gold"], fg=C["forest"],
            font=("Segoe UI", 10, "bold"),
            relief="flat", bd=0,
            cursor="hand2",
            padx=14, pady=7,
            activebackground=C["gold_light"],
            activeforeground=C["forest"],
            **kw
        )
        self.bind("<Enter>", lambda e: self.config(bg=C["gold_light"]))
        self.bind("<Leave>", lambda e: self.config(bg=C["gold"]))


class DangerButton(tk.Button):
    def __init__(self, parent, text, command, **kw):
        super().__init__(parent,
            text=text, command=command,
            bg=C["danger_bg"], fg=C["danger_fg"],
            font=("Segoe UI", 10),
            relief="flat", bd=0,
            cursor="hand2",
            padx=14, pady=7,
            activebackground="#ffc9c9",
            activeforeground=C["danger_fg"],
            **kw
        )

class GhostButton(tk.Button):
    def __init__(self, parent, text, command, **kw):
        super().__init__(parent,
            text=text, command=command,
            bg=C["surface"], fg=C["ink_mid"],
            font=("Segoe UI", 10),
            relief="flat", bd=1,
            highlightbackground=C["border"],
            cursor="hand2",
            padx=14, pady=7,
            activebackground=C["parchment"],
            **kw
        )


class StatCard(tk.Frame):
    def __init__(self, parent, label, value, accent, icon, **kw):
        super().__init__(parent, bg=C["card"], bd=0, relief="flat", **kw)
        # Left accent bar
        bar = tk.Frame(self, width=4, bg=accent)
        bar.pack(side="left", fill="y")
        inner = tk.Frame(self, bg=C["card"], padx=20, pady=18)
        inner.pack(side="left", fill="both", expand=True)
        tk.Label(inner, text=label, font=("Segoe UI", 9),
                 fg=C["ink_light"], bg=C["card"],
                 anchor="w").pack(anchor="w")
        self.val_label = tk.Label(inner, text=str(value),
                                  font=("Georgia", 32, "bold"),
                                  fg=C["forest"], bg=C["card"])
        self.val_label.pack(anchor="w")
        tk.Label(self, text=icon, font=("Segoe UI", 22),
                 fg=accent, bg=C["card"],
                 padx=12).pack(side="right")
        self._add_shadow()

    def update_value(self, val):
        self.val_label.config(text=str(val))

    def _add_shadow(self):
        self.config(highlightbackground=C["border"], highlightthickness=1)


class SectionTitle(tk.Label):
    def __init__(self, parent, text, **kw):
        super().__init__(parent,
            text=text,
            font=("Georgia", 14, "bold"),
            fg=C["forest"],
            bg=kw.pop("bg", C["surface"]),
            anchor="w",
            **kw
        )


class FormField(tk.Frame):
    """Label + Entry/Combobox combo."""
    def __init__(self, parent, label, var, widget_type="entry",
                 values=None, bg=C["card"], **kw):
        super().__init__(parent, bg=bg)
        tk.Label(self, text=label.upper(),
                 font=("Segoe UI", 8, "bold"),
                 fg=C["ink_light"], bg=bg).pack(anchor="w")
        if widget_type == "combo":
            w = ttk.Combobox(self, textvariable=var,
                             values=values or [], state="readonly",
                             font=("Segoe UI", 10))
        elif widget_type == "text":
            w = tk.Text(self, height=3, font=("Segoe UI", 10),
                        bg=C["white"], relief="flat",
                        highlightbackground=C["border"],
                        highlightthickness=1, padx=6, pady=4)
        else:
            w = tk.Entry(self, textvariable=var,
                         font=("Segoe UI", 10), bg=C["white"],
                         relief="flat",
                         highlightbackground=C["border"],
                         highlightthickness=1)
        w.pack(fill="x", ipady=4 if widget_type != "text" else 0)
        self.widget = w


class Toast(tk.Frame):
    """Popup notification that auto-dismisses."""
    COLORS = {
        "success": (C["success_bg"], C["success_fg"]),
        "danger":  (C["danger_bg"],  C["danger_fg"]),
        "warning": (C["warn_bg"],    C["warn_fg"]),
        "info":    (C["info_bg"],    C["info_fg"]),
    }

    def __init__(self, root, message, kind="success"):
        bg, fg = self.COLORS.get(kind, (C["info_bg"], C["info_fg"]))
        super().__init__(root, bg=bg, padx=16, pady=10,
                         highlightbackground=fg, highlightthickness=1)
        icons = {"success": "✓", "danger": "✗", "warning": "!", "info": "i"}
        tk.Label(self, text=icons.get(kind, "i"), font=("Segoe UI", 12, "bold"),
                 fg=fg, bg=bg).pack(side="left", padx=(0, 8))
        tk.Label(self, text=message, font=("Segoe UI", 10),
                 fg=fg, bg=bg, wraplength=320).pack(side="left")
        self.place(relx=0.5, rely=0.96, anchor="s")
        root.after(3000, self.destroy)


def make_table(parent, columns, bg=C["white"]):
    """Create a styled Treeview with scrollbar."""
    frame = tk.Frame(parent, bg=bg)
    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        selectmode="browse")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    # Alternating row tags
    tree.tag_configure("odd",  background="#faf8f4")
    tree.tag_configure("even", background=C["white"])
    tree.tag_configure("overdue",  background=C["danger_bg"], foreground=C["danger_fg"])
    tree.tag_configure("returned", background=C["success_bg"], foreground=C["success_fg"])
    tree.tag_configure("borrowed", background=C["warn_bg"],    foreground=C["warn_fg"])
    return frame, tree


class ScrollableFrame(tk.Frame):
    """A vertically scrollable frame container."""
    def __init__(self, parent, bg=C["surface"], **kw):
        outer = tk.Frame(parent, bg=bg)
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        super().__init__(canvas, bg=bg, **kw)
        self._win = canvas.create_window((0, 0), window=self, anchor="nw")
        self.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(self._win, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        self._canvas = canvas
        self._outer = outer

    def get_outer(self):
        return self._outer
