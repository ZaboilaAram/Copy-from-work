result = dict(sorted(
        {row[0]: {"username": row[1], "password": row[2]} for row in cursor.fetchall() if row[0]}.items(),
        key=lambda x: x[0].lower()
    ))

import tkinter as tk
import re
import string

# ── Windows 95 colour palette ──────────────────────────────────────────────
BG          = "#c0c0c0"
DARK_SHADOW = "#808080"
LIGHT_EDGE  = "#ffffff"
TITLE_BAR   = "#000080"
TITLE_TEXT  = "#ffffff"
INSET_BG    = "#ffffff"
INSET_BORDER= "#808080"
BTN_FACE    = "#c0c0c0"
TEXT_BLACK  = "#000000"

# Strength colours (muted, period-appropriate)
COLORS = {
    "Very Weak":  "#ff0000",
    "Weak":       "#ff6600",
    "Fair":       "#cccc00",
    "Strong":     "#009900",
    "Very Strong":"#006600",
}

FONT        = ("MS Sans Serif", 8)
FONT_BOLD   = ("MS Sans Serif", 8, "bold")
FONT_TITLE  = ("MS Sans Serif", 8, "bold")
FONT_MONO   = ("Courier New", 9)


# ── Helper: draw a Win95 raised/sunken bevel ──────────────────────────────
def bevel(parent, x, y, w, h, sunken=False):
    top = DARK_SHADOW if sunken else LIGHT_EDGE
    bot = LIGHT_EDGE  if sunken else DARK_SHADOW
    # top & left
    parent.create_line(x, y+h, x, y, fill=top, width=1)
    parent.create_line(x, y, x+w, y, fill=top, width=1)
    # bottom & right
    parent.create_line(x, y+h, x+w, y+h, fill=bot, width=1)
    parent.create_line(x+w, y, x+w, y+h, fill=bot, width=1)


# ── Password analysis ──────────────────────────────────────────────────────
def analyse(pwd):
    score   = 0
    checks  = {}

    checks["Length >= 8"]       = len(pwd) >= 8
    checks["Length >= 12"]      = len(pwd) >= 12
    checks["Uppercase letter"]  = bool(re.search(r"[A-Z]", pwd))
    checks["Lowercase letter"]  = bool(re.search(r"[a-z]", pwd))
    checks["Digit"]             = bool(re.search(r"\d", pwd))
    checks["Special character"] = bool(re.search(r"[!@#$%^&*()\-_=+\[\]{};:',.<>?/\\|`~]", pwd))
    checks["No common pattern"] = not bool(re.search(
        r"(1234|abcd|password|qwerty|letmein|admin|welcome|monkey|dragon)", pwd, re.I))

    score = sum(checks.values())

    if score <= 1:   strength = "Very Weak"
    elif score <= 3: strength = "Weak"
    elif score == 4: strength = "Fair"
    elif score <= 6: strength = "Strong"
    else:            strength = "Very Strong"

    entropy_bits = 0
    pool = 0
    if re.search(r"[a-z]", pwd): pool += 26
    if re.search(r"[A-Z]", pwd): pool += 26
    if re.search(r"\d",    pwd): pool += 10
    if re.search(r"[^a-zA-Z0-9]", pwd): pool += 32
    if pool > 0 and len(pwd) > 0:
        import math
        entropy_bits = round(len(pwd) * math.log2(pool), 1)

    return strength, score, checks, entropy_bits


# ── Main application ───────────────────────────────────────────────────────
class App:
    def __init__(self, rootpswchk):
        self.rootpswchk = rootpswchk
        rootpswchk.title("Password Security Checker")
        rootpswchk.resizable(False, False)
        rootpswchk.configure(bg=BG)

        self._build_window()

    # ── outer window chrome ──────────────────────────────────────────────
    def _build_window(self):
        rootpswchk = self.rootpswchk

        # Title bar (painted manually for authenticity)
        self.tb = tk.Frame(rootpswchk, bg=TITLE_BAR, height=20)
        self.tb.pack(fill="x", padx=2, pady=(2, 0))
        self.tb.pack_propagate(False)

        tk.Label(self.tb, text="Password Security Checker",
                 bg=TITLE_BAR, fg=TITLE_TEXT,
                 font=FONT_TITLE).pack(side="left", padx=4)

        # close button placeholder
        close_btn = tk.Label(self.tb, text="X", bg=BTN_FACE, fg=TEXT_BLACK,
                             font=FONT_BOLD, relief="raised", bd=1,
                             padx=3, pady=0, width=2)
        close_btn.pack(side="right", padx=2, pady=2)
        close_btn.bind("<Button-1>", lambda e: self.rootpswchk.destroy())

        # ── main body ────────────────────────────────────────────────────
        body = tk.Frame(rootpswchk, bg=BG, bd=0)
        body.pack(fill="both", expand=True, padx=2, pady=2)

        # ── GroupBox: Enter Password ──────────────────────────────────
        grp1 = self._groupbox(body, "Enter Password", 10, 10, 370, 80)
        grp1.pack(padx=8, pady=(8, 0), fill="x")

        inner1 = tk.Frame(grp1, bg=BG)
        inner1.pack(fill="x", padx=8, pady=(12, 8))

        tk.Label(inner1, text="Password:", bg=BG, fg=TEXT_BLACK,
                 font=FONT).grid(row=0, column=0, sticky="w")

        self.pwd_var = tk.StringVar()
        self.pwd_var.trace_add("write", self._on_change)

        self.entry = tk.Entry(inner1, textvariable=self.pwd_var,
                              show="*", font=FONT_MONO,
                              bg=INSET_BG, fg=TEXT_BLACK,
                              relief="sunken", bd=2, width=34)
        self.entry.grid(row=0, column=1, padx=(6, 0))

        self.show_var = tk.IntVar(value=0)
        self.chk = tk.Checkbutton(inner1, text="Show", variable=self.show_var,
                                  bg=BG, fg=TEXT_BLACK, font=FONT,
                                  activebackground=BG,
                                  command=self._toggle_show)
        self.chk.grid(row=0, column=2, padx=(6, 0))

        # ── GroupBox: Strength Meter ──────────────────────────────────
        grp2 = self._groupbox(body, "Strength Meter", 10, 100, 370, 80)
        grp2.pack(padx=8, pady=(6, 0), fill="x")

        inner2 = tk.Frame(grp2, bg=BG)
        inner2.pack(fill="x", padx=8, pady=(12, 8))

        # bar container (sunken inset)
        bar_frame = tk.Frame(inner2, bg=INSET_BG, relief="sunken", bd=2,
                             height=20, width=280)
        bar_frame.pack(side="left")
        bar_frame.pack_propagate(False)

        self.bar_canvas = tk.Canvas(bar_frame, bg=INSET_BG,
                                    height=20, width=280,
                                    highlightthickness=0)
        self.bar_canvas.pack()
        self.bar_rect  = self.bar_canvas.create_rectangle(0, 0, 0, 20,
                                                           fill="#000080",
                                                           outline="")

        self.lbl_strength = tk.Label(inner2, text="None",
                                     bg=BG, fg=TEXT_BLACK,
                                     font=FONT_BOLD, width=12)
        self.lbl_strength.pack(side="left", padx=(10, 0))

        # ── GroupBox: Details ─────────────────────────────────────────
        grp3 = self._groupbox(body, "Details", 10, 190, 370, 200)
        grp3.pack(padx=8, pady=(6, 0), fill="x")

        inner3 = tk.Frame(grp3, bg=BG)
        inner3.pack(fill="x", padx=8, pady=(12, 8))

        self.detail_text = tk.Text(inner3, bg=INSET_BG, fg=TEXT_BLACK,
                                   font=FONT_MONO, relief="sunken", bd=2,
                                   height=9, width=46,
                                   state="disabled", cursor="arrow",
                                   wrap="none")
        self.detail_text.pack()

        # scrollbar
        sb = tk.Scrollbar(inner3, orient="vertical",
                          command=self.detail_text.yview)
        # not packed by default – only if needed; keep it simple

        # ── GroupBox: Entropy ─────────────────────────────────────────
        grp4 = self._groupbox(body, "Statistics", 10, 400, 370, 60)
        grp4.pack(padx=8, pady=(6, 0), fill="x")

        inner4 = tk.Frame(grp4, bg=BG)
        inner4.pack(fill="x", padx=8, pady=(12, 8))

        tk.Label(inner4, text="Length:", bg=BG, fg=TEXT_BLACK,
                 font=FONT).grid(row=0, column=0, sticky="w")
        self.lbl_len = tk.Label(inner4, text="0", bg=BG, fg=TEXT_BLACK,
                                font=FONT, width=4, anchor="w")
        self.lbl_len.grid(row=0, column=1, sticky="w", padx=(4, 20))

        tk.Label(inner4, text="Est. Entropy:", bg=BG, fg=TEXT_BLACK,
                 font=FONT).grid(row=0, column=2, sticky="w")
        self.lbl_entropy = tk.Label(inner4, text="0.0 bits", bg=BG,
                                    fg=TEXT_BLACK, font=FONT, width=10,
                                    anchor="w")
        self.lbl_entropy.grid(row=0, column=3, sticky="w", padx=4)

        # ── Buttons ───────────────────────────────────────────────────
        btn_frame = tk.Frame(body, bg=BG)
        btn_frame.pack(padx=8, pady=(8, 10), anchor="e")

        self._w95_btn(btn_frame, "Clear",
                      self._clear).pack(side="left", padx=(0, 6))
        self._w95_btn(btn_frame, "Analyse",
                      self._force_analyse).pack(side="left", padx=(0, 6))
        self._w95_btn(btn_frame, "Quit",
                      self.rootpswchk.destroy).pack(side="left")

        # ── Status bar ────────────────────────────────────────────────
        self.status = tk.Label(body, text="Type a password to begin.",
                               bg=DARK_SHADOW, fg=TITLE_TEXT,
                               font=FONT, anchor="w", relief="sunken", bd=1)
        self.status.pack(fill="x", padx=8, pady=(0, 4))

        # initial state
        self._update_ui("", *analyse(""))

    # ── Windows 95 group-box frame ────────────────────────────────────────
    def _groupbox(self, parent, title, x, y, w, h):
        frame = tk.LabelFrame(parent, text=title,
                              bg=BG, fg=TEXT_BLACK,
                              font=FONT_BOLD,
                              relief="groove", bd=2)
        return frame

    # ── Windows 95 raised button ──────────────────────────────────────────
    def _w95_btn(self, parent, text, cmd):
        btn = tk.Button(parent, text=text, command=cmd,
                        font=FONT, bg=BTN_FACE, fg=TEXT_BLACK,
                        relief="raised", bd=2, padx=10, pady=3,
                        activebackground=BG, cursor="arrow")
        btn.bind("<ButtonPress-1>",   lambda e, b=btn: b.config(relief="sunken"))
        btn.bind("<ButtonRelease-1>", lambda e, b=btn: b.config(relief="raised"))
        return btn

    # ── Callbacks ─────────────────────────────────────────────────────────
    def _on_change(self, *_):
        pwd = self.pwd_var.get()
        self._update_ui(pwd, *analyse(pwd))

    def _toggle_show(self):
        self.entry.config(show="" if self.show_var.get() else "*")

    def _clear(self):
        self.pwd_var.set("")
        self.entry.focus()

    def _force_analyse(self):
        self._on_change()

    # ── Main UI update ────────────────────────────────────────────────────
    def _update_ui(self, pwd, strength, score, checks, entropy):
        # Strength label & colour
        colour = COLORS.get(strength, TEXT_BLACK)
        self.lbl_strength.config(text=strength, fg=colour)

        # Progress bar (280 px wide, 7 possible score values 0-7)
        max_score = 7
        fill_w = int(280 * score / max_score)
        self.bar_canvas.coords(self.bar_rect, 0, 0, fill_w, 20)
        self.bar_canvas.itemconfig(self.bar_rect, fill=colour)

        # Statistics
        self.lbl_len.config(text=str(len(pwd)))
        self.lbl_entropy.config(text=f"{entropy} bits")

        # Details checklist
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        for label, passed in checks.items():
            mark = "[PASS]" if passed else "[FAIL]"
            line = f"  {mark}  {label}\n"
            self.detail_text.insert("end", line)
            tag = f"tag_{label}"
            end_idx = self.detail_text.index("end-1c")
            # colour the mark
            start = self.detail_text.search(mark, "1.0", "end")
        # re-do with proper tagging
        self.detail_text.delete("1.0", "end")
        for i, (label, passed) in enumerate(checks.items(), start=1):
            mark = "[PASS]" if passed else "[FAIL]"
            fg   = "#008000" if passed else "#cc0000"
            line = f"  {mark}  {label}\n"
            self.detail_text.insert("end", line)
            # tag the mark portion
            line_start = f"{i}.0"
            mark_start = f"{i}.2"
            mark_end   = f"{i}.{2+len(mark)}"
            self.detail_text.tag_add(f"t{i}", mark_start, mark_end)
            self.detail_text.tag_config(f"t{i}", foreground=fg, font=FONT_BOLD)

        self.detail_text.config(state="disabled")

        # Status bar
        if not pwd:
            msg = "Type a password to begin."
        elif strength in ("Very Weak", "Weak"):
            msg = f"WARNING: Password is {strength}. Consider a stronger password."
        elif strength == "Fair":
            msg = "Password is acceptable but could be improved."
        else:
            msg = f"Password is {strength}."
        self.status.config(text=f"  {msg}")


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    rootpswchk = tk.Tk()
    rootpswchk.configure(bg=BG)

    # Try to set the icon / window decorations
    # try:
        # rootpswchk.iconbitmap(default="")
    # except Exception:
        # pass

    app = App(rootpswchk)
    rootpswchk.mainloop()
