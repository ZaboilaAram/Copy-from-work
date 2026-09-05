if excelvar == 1992:
    import sys
    import os
    import subprocess
    from PyQt5.QtWidgets import (QInputDialog, QApplication, QMainWindow, QTabWidget,
                                 QTableView, QFileDialog, QAction, QMenuBar, QMessageBox,
                                 QLineEdit, QVBoxLayout, QWidget, QDialog, QTextEdit,
                                 QPushButton)
    from PyQt5.QtCore import Qt
    from openpyxl import load_workbook, Workbook

    import sqlite3, os as _os
    _db_path = "Config/dbo_bitpack.db"
    _has_key = True  # default
    if _os.path.exists(_db_path):
        _conn = sqlite3.connect(_db_path)
        _cursor = _conn.cursor()
        _cursor.execute("SELECT has_key FROM accounts WHERE var_value='1992'")
        _result = _cursor.fetchone()
        _conn.close()
        if _result is not None:
            _has_key = bool(_result[0])
    
    if not _has_key:
        pass
    else:
        # Definirea numele fișierului pentru salvarea cheii
        FOLDER_NAME = "Serial"
        FILE_NAME = "product_key.lic95"
        cale_fis = "file_paths.txt"
        cale_fldr = "folder_paths.txt"

        # Definirea cheii de validare
        KEY = "R46BX-JHR2J-PG7ER-24QFG-MWKVR"
        
        key_is_valid = False
        file_path = os.path.join(FOLDER_NAME, FILE_NAME)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            try:
                with open(file_path, "r") as file:
                    saved_key = file.read().strip()
                    if saved_key == KEY:
                        key_is_valid = True
            except Exception as e:
                print(f"Error checking key: {e}")
        if not key_is_valid:
            # Verifică și creează folderul Serial dacă nu există
            if not os.path.exists(FOLDER_NAME):
                try:
                    os.makedirs(FOLDER_NAME)
                    print(f"Folder '{FOLDER_NAME}' created successfully.")
                except Exception as e:
                    print(f"Error creating folder '{FOLDER_NAME}': {e}")

            def validate_key(event=None):
                # Funcția pentru validarea cheii
                global xx
                if text_box.get("1.0", "end-1c").strip() == KEY:
                    xx = 2
                    validate_button.config(state=tk.NORMAL)
                    no_key_button.config(state=tk.DISABLED)
                    
                    # Calea completă către fișier în folderul Serial
                    file_path = os.path.join(FOLDER_NAME, FILE_NAME)
                    
                    # Salvarea cheii în fișier text
                    with open(file_path, "w") as file:
                        file.write(KEY)
                    try:
                        if not os.path.exists("file_paths.txt"):
                            with open("file_paths.txt", "w") as file:
                                file.write("")
                    except Exception as e:
                        print(f"An error occurred while creating the file file_paths.txt: {e}")

                    try:
                        if not os.path.exists("folder_paths.txt"):
                            with open("folder_paths.txt", "w") as file:
                                file.write("")
                    except Exception as e:
                        print(f"An error occurred while creating the file folder_paths.txt: {e}")
                else:
                    xx = 0
                    validate_button.config(state=tk.DISABLED)
                    no_key_button.config(state=tk.NORMAL)

            def load_key():
                try:
                    # Calea completă către fișier în folderul Serial
                    file_path = os.path.join(FOLDER_NAME, FILE_NAME)
                    
                    # Încărcarea cheii din fișier text
                    with open(file_path, "r") as file:
                        key = file.read().strip()
                        text_box.delete("1.0", "end")
                        text_box.insert("1.0", key)
                        validate_key()  # Validarea automată a cheii încărcate
                except FileNotFoundError:
                    pass

            def nokey():
                messagebox.showinfo(title="Unlicensed Product", message="Secure connection.\nWelcome to Bitpack!\nFor full access, please contact the administrator (Tudor Marmureanu).")
                sys.exit()

            def valkey():
                messagebox.showinfo(title="Product Activated (professional version)", message="Secure connection.\nWelcome to Bitpack!")
                validation.destroy()

            def on_closing():
                #pass
                messagebox.showwarning("Warning", "Close the program from the Command Prompt to stop all processes!")

            # Crearea ferestrei principale pentru validare
            validation = tk.Tk()
            validation.protocol("WM_DELETE_WINDOW", on_closing)
            validation.title("Product key validation")
            validation.geometry("260x260")  # Setarea dimensiunilor ferestrei principale
            validation.config(bg="gray20")
            #image_icon52 = PhotoImage(file = "img/keylogo.png")
            #validation.iconphoto(False, image_icon52)

            # Crearea obiectului Text editabil
            text_box = tk.Text(validation, height=1, width=30)  # Setarea wrap="none" pentru a face obiectul Text dreptunghiular
            text_box.config(bd=4)
            text_box.pack(pady=10)
            text_box.bind("<KeyRelease>", validate_key)  # Legarea funcției validate_key() de evenimentul de eliberare a tastelor

            # Crearea butonului "I don't have a product key"
            no_key_button = tk.Button(validation, text="I don't have a product key", bg="black", fg="lime green", bd=5, command=nokey)
            no_key_button.pack(pady=5)

            # Crearea butonului "Validate key"
            validate_button = tk.Button(validation, text="Validate key" ,bg="black", fg="lime green", bd=5, command=valkey, state=tk.DISABLED)
            validate_button.pack(pady=5)

            # Încărcarea cheii la deschiderea programului (dacă există)
            load_key()

            # Rularea buclei principale
            validation.mainloop()

    # ======================================================================
    # EXCEL LITE ENGINE (inlined)
    # Formula parser and evaluator, sheet model, filter/sort proxy, filter
    # dialog, help dialog and view helpers. Everything is prefixed with
    # xl_ / Xl / XL_ so nothing can collide with the rest of Bitpack.py.
    # ======================================================================
    """
    excel_lite_core.py  --  Bitpack / Excel Lite
    ==============================================================================
    Motor de formule + model de foaie + sortare/filtrare pentru Excel Lite.

    Se pune langa fisierul principal si se importa. Nu modifica interfata:
    aceleasi widget-uri, acelasi stylesheet. Adauga doar:
      * un parser real de formule (fara eval), cu ~110 functii
      * referinte multi-litera (A..CV), absolute ($A$1) si intre foi (Sheet2!A1)
      * cache de evaluare + detectie de referinte circulare
      * sortare si filtre tip AutoFilter pe coloane
      * undo/redo, clipboard compatibil cu Excel real, Delete pe selectie
    ==============================================================================
    """

    import math
    import random
    import re
    import datetime

    # ---------------------------------------------------------------------------
    # Dimensiuni implicite ale unei foi
    # ---------------------------------------------------------------------------
    XL_DEFAULT_ROWS = 100
    XL_DEFAULT_COLS = 100
    XL_MAX_ROWS = 5000
    XL_MAX_COLS = 256

    XL_EPOCH = datetime.datetime(1899, 12, 30)


    # ===========================================================================
    # 1. Valori de eroare
    # ===========================================================================
    class XlError(object):
        """Valoare de eroare in stil Excel (#VALUE!, #DIV/0! etc.)."""
        __slots__ = ("code",)

        def __init__(self, code):
            self.code = code

        def __str__(self):
            return self.code

        def __repr__(self):
            return self.code

        def __eq__(self, other):
            return isinstance(other, XlError) and other.code == self.code

        def __ne__(self, other):
            return not self.__eq__(other)

        def __hash__(self):
            return hash(self.code)


    XL_ERR_DIV0 = XlError("#DIV/0!")
    XL_ERR_VALUE = XlError("#VALUE!")
    XL_ERR_REF = XlError("#REF!")
    XL_ERR_NAME = XlError("#NAME?")
    XL_ERR_NA = XlError("#N/A")
    XL_ERR_NUM = XlError("#NUM!")
    XL_ERR_NULL = XlError("#NULL!")
    XL_ERR_CYCLE = XlError("#CYCLE!")

    _xl_ERR_BY_CODE = dict((e.code, e) for e in
                        (XL_ERR_DIV0, XL_ERR_VALUE, XL_ERR_REF, XL_ERR_NAME,
                         XL_ERR_NA, XL_ERR_NUM, XL_ERR_NULL, XL_ERR_CYCLE))


    class _xl_Stop(Exception):
        """Exceptie interna: opreste evaluarea si propaga o eroare Excel."""

        def __init__(self, err):
            Exception.__init__(self, err.code)
            self.err = err


    def _xl_fail(err):
        raise _xl_Stop(err)


    # ===========================================================================
    # 2. Adrese de celule
    # ===========================================================================
    def xl_col_to_name(idx):
        """0 -> A, 25 -> Z, 26 -> AA, 99 -> CV"""
        name = ""
        idx = int(idx)
        while True:
            name = chr(ord('A') + idx % 26) + name
            idx = idx // 26 - 1
            if idx < 0:
                break
        return name


    def xl_name_to_col(letters):
        """A -> 0, AA -> 26"""
        idx = 0
        for ch in letters.upper():
            idx = idx * 26 + (ord(ch) - ord('A') + 1)
        return idx - 1


    _xl_A1_RE = re.compile(r"^\$?([A-Za-z]{1,3})\$?([0-9]{1,7})$")


    def xl_parse_a1(text):
        """'B7' -> (6, 1) adica (row, col) zero-based. None daca nu e valid."""
        m = _xl_A1_RE.match(text.strip())
        if not m:
            return None
        return int(m.group(2)) - 1, xl_name_to_col(m.group(1))


    class XlCellRef(object):
        __slots__ = ("sheet", "row", "col")

        def __init__(self, sheet, row, col):
            self.sheet = sheet
            self.row = row
            self.col = col


    class XlCellRange(object):
        """Interval dreptunghiular de celule; se evalueaza lazy."""
        __slots__ = ("ctx", "sheet", "r1", "c1", "r2", "c2")

        def __init__(self, ctx, sheet, r1, c1, r2, c2):
            self.ctx = ctx
            self.sheet = sheet
            self.r1, self.c1 = min(r1, r2), min(c1, c2)
            self.r2, self.c2 = max(r1, r2), max(c1, c2)

        @property
        def nrows(self):
            return self.r2 - self.r1 + 1

        @property
        def ncols(self):
            return self.c2 - self.c1 + 1

        def cell(self, i, j):
            """Valoare relativa in interval (0-based)."""
            return self.ctx.cell_value(self.sheet, self.r1 + i, self.c1 + j)

        def values(self):
            out = []
            for r in range(self.r1, self.r2 + 1):
                for c in range(self.c1, self.c2 + 1):
                    out.append(self.ctx.cell_value(self.sheet, r, c))
            return out


    # ===========================================================================
    # 3. Conversii de tip
    # ===========================================================================
    def xl_is_number(v):
        return isinstance(v, (int, float)) and not isinstance(v, bool)


    def xl_as_scalar(v):
        """Un interval 1x1 devine scalar; altfel eroare."""
        if isinstance(v, XlCellRange):
            if v.nrows == 1 and v.ncols == 1:
                return v.cell(0, 0)
            _xl_fail(XL_ERR_VALUE)
        return v


    def xl_to_num(v):
        v = xl_as_scalar(v)
        if isinstance(v, XlError):
            _xl_fail(v)
        if v is None or v == "":
            return 0
        if isinstance(v, bool):
            return 1 if v else 0
        if xl_is_number(v):
            return v
        if isinstance(v, str):
            s = v.strip().replace(" ", "")
            try:
                if s.endswith("%"):
                    return float(s[:-1]) / 100.0
                return float(s)
            except ValueError:
                _xl_fail(XL_ERR_VALUE)
        _xl_fail(XL_ERR_VALUE)


    def xl_to_int(v):
        return int(math.floor(xl_to_num(v)))


    def xl_to_text(v):
        v = xl_as_scalar(v)
        if isinstance(v, XlError):
            _xl_fail(v)
        if v is None:
            return ""
        if isinstance(v, bool):
            return "TRUE" if v else "FALSE"
        if xl_is_number(v):
            if isinstance(v, float) and v == int(v) and abs(v) < 1e15:
                return str(int(v))
            return repr(round(v, 10)) if isinstance(v, float) else str(v)
        return str(v)


    def xl_to_bool(v):
        v = xl_as_scalar(v)
        if isinstance(v, XlError):
            _xl_fail(v)
        if isinstance(v, bool):
            return v
        if v is None or v == "":
            return False
        if xl_is_number(v):
            return v != 0
        if isinstance(v, str):
            s = v.strip().upper()
            if s == "TRUE":
                return True
            if s == "FALSE":
                return False
        _xl_fail(XL_ERR_VALUE)


    def xl_flat(args):
        """Aplatizeaza argumentele (intervalele se desfac in celule)."""
        out = []
        for a in args:
            if isinstance(a, XlCellRange):
                out.extend(a.values())
            else:
                out.append(a)
        return out


    def xl_nums(args, blanks=False):
        """Numerele din argumente. Din intervale se ignora textul si golurile."""
        out = []
        for a in args:
            if isinstance(a, XlCellRange):
                for v in a.values():
                    if isinstance(v, XlError):
                        _xl_fail(v)
                    if xl_is_number(v):
                        out.append(v)
                    elif isinstance(v, bool):
                        continue
                    elif blanks and (v is None or v == ""):
                        out.append(0)
            else:
                if isinstance(a, XlError):
                    _xl_fail(a)
                if a is None or a == "":
                    if blanks:
                        out.append(0)
                    continue
                out.append(xl_to_num(a))
        return out


    _xl_TYPE_RANK = {"num": 0, "txt": 1, "bool": 2}


    def _xl_rank(v):
        if v is None or v == "":
            return "num"
        if isinstance(v, bool):
            return "bool"
        if xl_is_number(v):
            return "num"
        return "txt"


    def xl_compare(a, b):
        """Comparatie in stil Excel: numar < text < boolean. Returneaza -1/0/1."""
        a, b = xl_as_scalar(a), xl_as_scalar(b)
        if isinstance(a, XlError):
            _xl_fail(a)
        if isinstance(b, XlError):
            _xl_fail(b)
        ra, rb = _xl_rank(a), _xl_rank(b)
        if ra != rb:
            return -1 if _xl_TYPE_RANK[ra] < _xl_TYPE_RANK[rb] else 1
        if ra == "num":
            x = 0 if (a is None or a == "") else a
            y = 0 if (b is None or b == "") else b
            return (x > y) - (x < y)
        if ra == "bool":
            x, y = bool(a), bool(b)
            return (x > y) - (x < y)
        x, y = str(a).upper(), str(b).upper()
        return (x > y) - (x < y)


    # ===========================================================================
    # 4. Date calendaristice (serial Excel)
    # ===========================================================================
    def xl_serial_to_dt(serial):
        return XL_EPOCH + datetime.timedelta(days=float(serial))


    def xl_dt_to_serial(dt):
        if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
            dt = datetime.datetime(dt.year, dt.month, dt.day)
        delta = dt - XL_EPOCH
        return delta.days + delta.seconds / 86400.0


    # ===========================================================================
    # 5. Tokenizer
    # ===========================================================================
    _xl_TOKEN_RE = re.compile(r"""
          (?P<ws>[ \t\r\n]+)
        | (?P<string>"(?:[^"]|"")*")
        | (?P<error>\#(?:DIV/0!|VALUE!|REF!|NAME\?|N/A|NUM!|NULL!|CYCLE!))
        | (?P<ref>(?:'[^']+'|[A-Za-z_][A-Za-z0-9_.]*)!\$?[A-Za-z]{1,3}\$?[0-9]{1,7}
                  |\$?[A-Za-z]{1,3}\$?[0-9]{1,7})(?![A-Za-z0-9_.$(])
        | (?P<func>[A-Za-z_][A-Za-z0-9_.]*)(?=[ \t]*\()
        | (?P<name>[A-Za-z_][A-Za-z0-9_.]*)
        | (?P<number>[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?|\.[0-9]+)
        | (?P<op><=|>=|<>|[-+*/^&<>=%:,;()])
    """, re.VERBOSE)


    def xl_tokenize(text):
        pos, out, n = 0, [], len(text)
        while pos < n:
            m = _xl_TOKEN_RE.match(text, pos)
            if not m:
                _xl_fail(XL_ERR_NAME)
            pos = m.end()
            kind = m.lastgroup
            if kind == "ws":
                continue
            out.append((kind, m.group()))
        return out


    # ===========================================================================
    # 6. XlParser (AST) -- precedenta ca in Excel
    # ===========================================================================
    # Noduri: ("num", v) ("str", s) ("bool", b) ("err", e)
    #         ("ref", sheet, row, col) ("range", n1, n2)
    #         ("bin", op, l, r) ("neg", n) ("pct", n) ("func", name, [args])
    class XlParser(object):
        def __init__(self, tokens):
            self.t = tokens
            self.i = 0

        def peek(self):
            return self.t[self.i] if self.i < len(self.t) else (None, None)

        def next(self):
            tok = self.peek()
            self.i += 1
            return tok

        def expect(self, val):
            k, v = self.next()
            if v != val:
                _xl_fail(XL_ERR_NAME)

        def parse(self):
            node = self.p_compare()
            if self.i != len(self.t):
                _xl_fail(XL_ERR_NAME)
            return node

        def p_compare(self):
            node = self.p_concat()
            while self.peek()[1] in ("=", "<>", "<", ">", "<=", ">="):
                op = self.next()[1]
                node = ("bin", op, node, self.p_concat())
            return node

        def p_concat(self):
            node = self.p_add()
            while self.peek()[1] == "&":
                self.next()
                node = ("bin", "&", node, self.p_add())
            return node

        def p_add(self):
            node = self.p_mul()
            while self.peek()[1] in ("+", "-"):
                op = self.next()[1]
                node = ("bin", op, node, self.p_mul())
            return node

        def p_mul(self):
            node = self.p_power()
            while self.peek()[1] in ("*", "/"):
                op = self.next()[1]
                node = ("bin", op, node, self.p_power())
            return node

        def p_power(self):
            node = self.p_unary()
            while self.peek()[1] == "^":
                self.next()
                node = ("bin", "^", node, self.p_unary())
            return node

        def p_unary(self):
            if self.peek()[1] == "-":
                self.next()
                return ("neg", self.p_unary())
            if self.peek()[1] == "+":
                self.next()
                return self.p_unary()
            return self.p_postfix()

        def p_postfix(self):
            node = self.p_primary()
            while self.peek()[1] == "%":
                self.next()
                node = ("pct", node)
            return node

        def p_primary(self):
            kind, val = self.next()
            if kind is None:
                _xl_fail(XL_ERR_NAME)
            if kind == "number":
                f = float(val)
                return ("num", int(f) if f == int(f) and "." not in val
                        and "e" not in val.lower() else f)
            if kind == "string":
                return ("str", val[1:-1].replace('""', '"'))
            if kind == "error":
                return ("err", _xl_ERR_BY_CODE.get(val, XL_ERR_VALUE))
            if kind == "name":
                up = val.upper()
                if up == "TRUE":
                    return ("bool", True)
                if up == "FALSE":
                    return ("bool", False)
                _xl_fail(XL_ERR_NAME)
            if kind == "func":
                self.expect("(")
                args = []
                if self.peek()[1] != ")":
                    while True:
                        args.append(self.p_compare())
                        if self.peek()[1] in (",", ";"):
                            self.next()
                            continue
                        break
                self.expect(")")
                return ("func", val.upper(), args)
            if kind == "ref":
                node = self._ref_node(val)
                if self.peek()[1] == ":":
                    self.next()
                    k2, v2 = self.next()
                    if k2 != "ref":
                        _xl_fail(XL_ERR_REF)
                    return ("range", node, self._ref_node(v2))
                return node
            if val == "(":
                node = self.p_compare()
                self.expect(")")
                return node
            _xl_fail(XL_ERR_NAME)

        @staticmethod
        def _ref_node(text):
            sheet = None
            if "!" in text:
                sheet, text = text.split("!", 1)
                sheet = sheet.strip("'")
            rc = xl_parse_a1(text)
            if rc is None:
                _xl_fail(XL_ERR_REF)
            return ("ref", sheet, rc[0], rc[1])


    # ===========================================================================
    # 7. Context de evaluare
    # ===========================================================================
    class XlEvalContext(object):
        """Leaga motorul de registrul de lucru (workbook)."""

        def __init__(self, workbook, sheet, row, col):
            self.wb = workbook
            self.sheet = sheet
            self.row = row
            self.col = col

        def cell_value(self, sheet, row, col):
            return self.wb.value(sheet or self.sheet, row, col)


    # ===========================================================================
    # 8. Evaluator
    # ===========================================================================
    _xl_LAZY = ("IF", "IFS", "IFERROR", "IFNA", "AND", "OR", "CHOOSE",
             "ISERROR", "ISERR", "ISNA")


    def _xl_eval(node, ctx):
        t = node[0]
        if t == "num" or t == "str" or t == "bool":
            return node[1]
        if t == "err":
            _xl_fail(node[1])
        if t == "ref":
            return ctx.cell_value(node[1], node[2], node[3])
        if t == "range":
            a, b = node[1], node[2]
            return XlCellRange(ctx, a[1] or b[1], a[2], a[3], b[2], b[3])
        if t == "neg":
            return -xl_to_num(_xl_eval(node[1], ctx))
        if t == "pct":
            return xl_to_num(_xl_eval(node[1], ctx)) / 100.0
        if t == "bin":
            return _xl_eval_bin(node[1], node[2], node[3], ctx)
        if t == "func":
            name, args = node[1], node[2]
            if name in ("ROW", "COLUMN") and args:
                a0 = args[0]
                if a0[0] == "ref":
                    return (a0[2] + 1) if name == "ROW" else (a0[3] + 1)
                if a0[0] == "range":
                    return (a0[1][2] + 1) if name == "ROW" else (a0[1][3] + 1)
            if name in _xl_LAZY:
                return _xl_eval_lazy(name, args, ctx)
            xl_fn = XL_FUNCTIONS.get(name)
            if xl_fn is None:
                _xl_fail(XL_ERR_NAME)
            return xl_fn(ctx, [_xl_eval(a, ctx) for a in args])
        _xl_fail(XL_ERR_VALUE)


    def _xl_eval_bin(op, ln, rn, ctx):
        left = _xl_eval(ln, ctx)
        right = _xl_eval(rn, ctx)
        if op == "&":
            return xl_to_text(left) + xl_to_text(right)
        if op in ("=", "<>", "<", ">", "<=", ">="):
            c = xl_compare(left, right)
            return {"=": c == 0, "<>": c != 0, "<": c < 0,
                    ">": c > 0, "<=": c <= 0, ">=": c >= 0}[op]
        a, b = xl_to_num(left), xl_to_num(right)
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                _xl_fail(XL_ERR_DIV0)
            return a / b
        if op == "^":
            try:
                r = math.pow(a, b)
            except (ValueError, OverflowError):
                _xl_fail(XL_ERR_NUM)
            return r
        _xl_fail(XL_ERR_VALUE)


    def _xl_try(node, ctx):
        """Evalueaza un nod si intoarce (ok, valoare_sau_eroare)."""
        try:
            v = _xl_eval(node, ctx)
        except _xl_Stop as e:
            return False, e.err
        if isinstance(v, XlError):
            return False, v
        return True, v


    def _xl_eval_lazy(name, args, ctx):
        if name == "IF":
            if len(args) < 2:
                _xl_fail(XL_ERR_VALUE)
            if xl_to_bool(_xl_eval(args[0], ctx)):
                return _xl_eval(args[1], ctx)
            return _xl_eval(args[2], ctx) if len(args) > 2 else False
        if name == "IFS":
            i = 0
            while i + 1 < len(args):
                if xl_to_bool(_xl_eval(args[i], ctx)):
                    return _xl_eval(args[i + 1], ctx)
                i += 2
            _xl_fail(XL_ERR_NA)
        if name == "IFERROR":
            if len(args) != 2:
                _xl_fail(XL_ERR_VALUE)
            ok, v = _xl_try(args[0], ctx)
            return xl_as_scalar(v) if ok else _xl_eval(args[1], ctx)
        if name == "IFNA":
            if len(args) != 2:
                _xl_fail(XL_ERR_VALUE)
            ok, v = _xl_try(args[0], ctx)
            if not ok and v == XL_ERR_NA:
                return _xl_eval(args[1], ctx)
            return xl_as_scalar(v) if ok else _xl_fail(v)
        if name in ("ISERROR", "ISERR", "ISNA"):
            if not args:
                _xl_fail(XL_ERR_VALUE)
            ok, v = _xl_try(args[0], ctx)
            if name == "ISNA":
                return (not ok) and v == XL_ERR_NA
            if name == "ISERR":
                return (not ok) and v != XL_ERR_NA
            return not ok
        if name == "AND":
            res = True
            seen = False
            for a in args:
                v = _xl_eval(a, ctx)
                for x in xl_flat([v]):
                    if x is None or x == "":
                        continue
                    seen = True
                    if not xl_to_bool(x):
                        res = False
            return res if seen else _xl_fail(XL_ERR_VALUE)
        if name == "OR":
            res = False
            seen = False
            for a in args:
                v = _xl_eval(a, ctx)
                for x in xl_flat([v]):
                    if x is None or x == "":
                        continue
                    seen = True
                    if xl_to_bool(x):
                        res = True
            return res if seen else _xl_fail(XL_ERR_VALUE)
        if name == "CHOOSE":
            idx = xl_to_int(_xl_eval(args[0], ctx))
            if idx < 1 or idx >= len(args):
                _xl_fail(XL_ERR_VALUE)
            return _xl_eval(args[idx], ctx)
        _xl_fail(XL_ERR_NAME)


    # ===========================================================================
    # 9. Biblioteca de functii
    # ===========================================================================
    XL_FUNCTIONS = {}


    def xl_fn(*names):
        def deco(f):
            for n in names:
                XL_FUNCTIONS[n] = f
            return f
        return deco


    def _xl_arg(args, i, default=None):
        return args[i] if len(args) > i else default


    # --- matematice -----------------------------------------------------------
    @xl_fn("SUM")
    def _xl_sum(ctx, a):
        return sum(xl_nums(a))


    @xl_fn("PRODUCT")
    def _xl_product(ctx, a):
        vals = xl_nums(a)
        r = 1
        for v in vals:
            r *= v
        return r if vals else 0


    @xl_fn("ABS")
    def _xl_abs(ctx, a):
        return abs(xl_to_num(_xl_arg(a, 0)))


    @xl_fn("SIGN")
    def _xl_sign(ctx, a):
        v = xl_to_num(_xl_arg(a, 0))
        return (v > 0) - (v < 0)


    @xl_fn("INT")
    def _xl_int(ctx, a):
        return int(math.floor(xl_to_num(_xl_arg(a, 0))))


    @xl_fn("TRUNC")
    def _xl_trunc(ctx, a):
        d = xl_to_int(_xl_arg(a, 1, 0))
        v = xl_to_num(_xl_arg(a, 0))
        f = 10 ** d
        return math.trunc(v * f) / f


    @xl_fn("ROUND")
    def _xl_round(ctx, a):
        v, d = xl_to_num(_xl_arg(a, 0)), xl_to_int(_xl_arg(a, 1, 0))
        f = 10.0 ** d
        r = math.floor(abs(v) * f + 0.5) / f
        return -r if v < 0 else r


    @xl_fn("ROUNDUP")
    def _xl_roundup(ctx, a):
        v, d = xl_to_num(_xl_arg(a, 0)), xl_to_int(_xl_arg(a, 1, 0))
        f = 10.0 ** d
        r = math.ceil(abs(v) * f) / f
        return -r if v < 0 else r


    @xl_fn("ROUNDDOWN")
    def _xl_rounddown(ctx, a):
        v, d = xl_to_num(_xl_arg(a, 0)), xl_to_int(_xl_arg(a, 1, 0))
        f = 10.0 ** d
        r = math.floor(abs(v) * f) / f
        return -r if v < 0 else r


    @xl_fn("CEILING")
    def _xl_ceiling(ctx, a):
        v, s = xl_to_num(_xl_arg(a, 0)), xl_to_num(_xl_arg(a, 1, 1))
        if s == 0:
            return 0
        return math.ceil(v / s) * s


    @xl_fn("FLOOR")
    def _xl_floor(ctx, a):
        v, s = xl_to_num(_xl_arg(a, 0)), xl_to_num(_xl_arg(a, 1, 1))
        if s == 0:
            _xl_fail(XL_ERR_DIV0)
        return math.floor(v / s) * s


    @xl_fn("MOD")
    def _xl_mod(ctx, a):
        x, y = xl_to_num(_xl_arg(a, 0)), xl_to_num(_xl_arg(a, 1))
        if y == 0:
            _xl_fail(XL_ERR_DIV0)
        return x - y * math.floor(x / y)


    @xl_fn("POWER", "POW")
    def _xl_power(ctx, a):
        try:
            return math.pow(xl_to_num(_xl_arg(a, 0)), xl_to_num(_xl_arg(a, 1)))
        except (ValueError, OverflowError):
            _xl_fail(XL_ERR_NUM)


    @xl_fn("SQRT")
    def _xl_sqrt(ctx, a):
        v = xl_to_num(_xl_arg(a, 0))
        if v < 0:
            _xl_fail(XL_ERR_NUM)
        return math.sqrt(v)


    @xl_fn("EXP")
    def _xl_exp(ctx, a):
        return math.exp(xl_to_num(_xl_arg(a, 0)))


    @xl_fn("LN")
    def _xl_ln(ctx, a):
        v = xl_to_num(_xl_arg(a, 0))
        if v <= 0:
            _xl_fail(XL_ERR_NUM)
        return math.log(v)


    @xl_fn("LOG")
    def _xl_log(ctx, a):
        v = xl_to_num(_xl_arg(a, 0))
        b = xl_to_num(_xl_arg(a, 1, 10))
        if v <= 0 or b <= 0 or b == 1:
            _xl_fail(XL_ERR_NUM)
        return math.log(v, b)


    @xl_fn("LOG10")
    def _xl_log10(ctx, a):
        v = xl_to_num(_xl_arg(a, 0))
        if v <= 0:
            _xl_fail(XL_ERR_NUM)
        return math.log10(v)


    @xl_fn("PI")
    def _xl_pi(ctx, a):
        return math.pi


    @xl_fn("RAND")
    def _xl_rand(ctx, a):
        return random.random()


    @xl_fn("RANDBETWEEN")
    def _xl_randbetween(ctx, a):
        return random.randint(xl_to_int(_xl_arg(a, 0)), xl_to_int(_xl_arg(a, 1)))


    @xl_fn("FACT")
    def _xl_fact(ctx, a):
        n = xl_to_int(_xl_arg(a, 0))
        if n < 0 or n > 170:
            _xl_fail(XL_ERR_NUM)
        return float(math.factorial(n))


    @xl_fn("GCD")
    def _xl_gcd(ctx, a):
        r = 0
        for v in xl_nums(a):
            r = math.gcd(r, abs(int(v)))
        return r


    @xl_fn("LCM")
    def _xl_lcm(ctx, a):
        r = 1
        for v in xl_nums(a):
            v = abs(int(v))
            if v == 0:
                return 0
            r = r * v // math.gcd(r, v)
        return r


    @xl_fn("DEGREES")
    def _xl_degrees(ctx, a):
        return math.degrees(xl_to_num(_xl_arg(a, 0)))


    @xl_fn("RADIANS")
    def _xl_radians(ctx, a):
        return math.radians(xl_to_num(_xl_arg(a, 0)))


    for _xl_tname, _xl_tfunc in (("SIN", math.sin), ("COS", math.cos), ("TAN", math.tan),
                      ("ASIN", math.asin), ("ACOS", math.acos),
                      ("ATAN", math.atan), ("SINH", math.sinh),
                      ("COSH", math.cosh), ("TANH", math.tanh)):
        def _xl_make_trig(f):
            def _trig(ctx, a):
                try:
                    return f(xl_to_num(_xl_arg(a, 0)))
                except ValueError:
                    _xl_fail(XL_ERR_NUM)
            return _trig
        XL_FUNCTIONS[_xl_tname] = _xl_make_trig(_xl_tfunc)


    @xl_fn("ATAN2")
    def _xl_atan2(ctx, a):
        return math.atan2(xl_to_num(_xl_arg(a, 1)), xl_to_num(_xl_arg(a, 0)))


    @xl_fn("SUMPRODUCT")
    def _xl_sumproduct(ctx, a):
        cols = []
        for arg in a:
            cols.append([v if xl_is_number(v) else 0 for v in xl_flat([arg])])
        if not cols:
            return 0
        n = len(cols[0])
        if any(len(c) != n for c in cols):
            _xl_fail(XL_ERR_VALUE)
        total = 0
        for i in range(n):
            p = 1
            for c in cols:
                p *= c[i]
            total += p
        return total


    # --- statistice -----------------------------------------------------------
    @xl_fn("AVERAGE")
    def _xl_average(ctx, a):
        v = xl_nums(a)
        if not v:
            _xl_fail(XL_ERR_DIV0)
        return sum(v) / len(v)


    @xl_fn("MIN")
    def _xl_min(ctx, a):
        v = xl_nums(a)
        return min(v) if v else 0


    @xl_fn("MAX")
    def _xl_max(ctx, a):
        v = xl_nums(a)
        return max(v) if v else 0


    @xl_fn("MEDIAN")
    def _xl_median(ctx, a):
        v = sorted(xl_nums(a))
        if not v:
            _xl_fail(XL_ERR_NUM)
        n = len(v)
        return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


    @xl_fn("MODE")
    def _xl_mode(ctx, a):
        v = xl_nums(a)
        if not v:
            _xl_fail(XL_ERR_NA)
        best, cnt = None, 0
        for x in v:
            c = v.count(x)
            if c > cnt:
                best, cnt = x, c
        if cnt < 2:
            _xl_fail(XL_ERR_NA)
        return best


    @xl_fn("COUNT")
    def _xl_count(ctx, a):
        return len(xl_nums(a))


    @xl_fn("COUNTA")
    def _xl_counta(ctx, a):
        return len([v for v in xl_flat(a) if not (v is None or v == "")])


    @xl_fn("COUNTBLANK")
    def _xl_countblank(ctx, a):
        return len([v for v in xl_flat(a) if v is None or v == ""])


    def _xl_stdev(values, sample):
        n = len(values)
        if n < (2 if sample else 1):
            _xl_fail(XL_ERR_DIV0)
        m = sum(values) / n
        ss = sum((x - m) ** 2 for x in values)
        return math.sqrt(ss / ((n - 1) if sample else n))


    @xl_fn("STDEV", "STDEVA")
    def _xl_stdev_s(ctx, a):
        return _xl_stdev(xl_nums(a), True)


    @xl_fn("STDEVP")
    def _xl_stdev_p(ctx, a):
        return _xl_stdev(xl_nums(a), False)


    @xl_fn("VAR")
    def _xl_var_s(ctx, a):
        return _xl_stdev(xl_nums(a), True) ** 2


    @xl_fn("VARP")
    def _xl_var_p(ctx, a):
        return _xl_stdev(xl_nums(a), False) ** 2


    @xl_fn("LARGE")
    def _xl_large(ctx, a):
        v = sorted(xl_nums([_xl_arg(a, 0)]), reverse=True)
        k = xl_to_int(_xl_arg(a, 1))
        if k < 1 or k > len(v):
            _xl_fail(XL_ERR_NUM)
        return v[k - 1]


    @xl_fn("SMALL")
    def _xl_small(ctx, a):
        v = sorted(xl_nums([_xl_arg(a, 0)]))
        k = xl_to_int(_xl_arg(a, 1))
        if k < 1 or k > len(v):
            _xl_fail(XL_ERR_NUM)
        return v[k - 1]


    @xl_fn("RANK")
    def _xl_rank_fn(ctx, a):
        x = xl_to_num(_xl_arg(a, 0))
        v = xl_nums([_xl_arg(a, 1)])
        asc = len(a) > 2 and xl_to_bool(a[2])
        v = sorted(v) if asc else sorted(v, reverse=True)
        if x not in v:
            _xl_fail(XL_ERR_NA)
        return v.index(x) + 1


    # --- criterii (COUNTIF / SUMIF ...) --------------------------------------
    _xl_CRIT_RE = re.compile(r"^(<=|>=|<>|=|<|>)?(.*)$", re.S)


    def _xl_wildcard(pattern):
        out = ""
        for ch in pattern:
            if ch == "*":
                out += ".*"
            elif ch == "?":
                out += "."
            else:
                out += re.escape(ch)
        return re.compile("^" + out + "$", re.I)


    def xl_make_criteria(crit):
        crit = xl_as_scalar(crit)
        if isinstance(crit, XlError):
            _xl_fail(crit)
        if xl_is_number(crit) or isinstance(crit, bool):
            target = crit
            return lambda v: xl_is_number(v) and v == target
        text = "" if crit is None else str(crit)
        op, rest = _xl_CRIT_RE.match(text).groups()
        op = op or "="
        try:
            num = float(rest)
            has_num = rest.strip() != ""
        except ValueError:
            num, has_num = None, False

        def test(v):
            if has_num:
                if not xl_is_number(v):
                    return op == "<>"
                return {"=": v == num, "<>": v != num, "<": v < num,
                        ">": v > num, "<=": v <= num, ">=": v >= num}[op]
            if op in ("=", "<>"):
                if rest == "":
                    blank = (v is None or v == "")
                    return blank if op == "=" else not blank
                if ("*" in rest) or ("?" in rest):
                    hit = bool(_xl_wildcard(rest).match("" if v is None else str(v)))
                else:
                    hit = str("" if v is None else v).upper() == rest.upper()
                return hit if op == "=" else not hit
            sv = str("" if v is None else v).upper()
            rv = rest.upper()
            return {"<": sv < rv, ">": sv > rv,
                    "<=": sv <= rv, ">=": sv >= rv}[op]

        return test


    def _xl_as_list(arg):
        return xl_flat([arg])


    @xl_fn("COUNTIF")
    def _xl_countif(ctx, a):
        test = xl_make_criteria(_xl_arg(a, 1))
        return len([v for v in _xl_as_list(_xl_arg(a, 0)) if test(v)])


    @xl_fn("SUMIF")
    def _xl_sumif(ctx, a):
        rng = _xl_as_list(_xl_arg(a, 0))
        test = xl_make_criteria(_xl_arg(a, 1))
        tgt = _xl_as_list(_xl_arg(a, 2)) if len(a) > 2 else rng
        total = 0
        for i, v in enumerate(rng):
            if test(v) and i < len(tgt) and xl_is_number(tgt[i]):
                total += tgt[i]
        return total


    @xl_fn("AVERAGEIF")
    def _xl_averageif(ctx, a):
        rng = _xl_as_list(_xl_arg(a, 0))
        test = xl_make_criteria(_xl_arg(a, 1))
        tgt = _xl_as_list(_xl_arg(a, 2)) if len(a) > 2 else rng
        vals = [tgt[i] for i, v in enumerate(rng)
                if test(v) and i < len(tgt) and xl_is_number(tgt[i])]
        if not vals:
            _xl_fail(XL_ERR_DIV0)
        return sum(vals) / len(vals)


    def _xl_multi_mask(pairs):
        mask = None
        for rng, crit in pairs:
            vals = _xl_as_list(rng)
            test = xl_make_criteria(crit)
            cur = [test(v) for v in vals]
            if mask is None:
                mask = cur
            else:
                if len(cur) != len(mask):
                    _xl_fail(XL_ERR_VALUE)
                mask = [m and c for m, c in zip(mask, cur)]
        return mask or []


    @xl_fn("COUNTIFS")
    def _xl_countifs(ctx, a):
        pairs = [(a[i], a[i + 1]) for i in range(0, len(a) - 1, 2)]
        return sum(1 for m in _xl_multi_mask(pairs) if m)


    @xl_fn("SUMIFS")
    def _xl_sumifs(ctx, a):
        tgt = _xl_as_list(_xl_arg(a, 0))
        pairs = [(a[i], a[i + 1]) for i in range(1, len(a) - 1, 2)]
        mask = _xl_multi_mask(pairs)
        return sum(tgt[i] for i, m in enumerate(mask)
                   if m and i < len(tgt) and xl_is_number(tgt[i]))


    @xl_fn("AVERAGEIFS")
    def _xl_averageifs(ctx, a):
        tgt = _xl_as_list(_xl_arg(a, 0))
        pairs = [(a[i], a[i + 1]) for i in range(1, len(a) - 1, 2)]
        mask = _xl_multi_mask(pairs)
        vals = [tgt[i] for i, m in enumerate(mask)
                if m and i < len(tgt) and xl_is_number(tgt[i])]
        if not vals:
            _xl_fail(XL_ERR_DIV0)
        return sum(vals) / len(vals)


    # --- logice / informationale ---------------------------------------------
    @xl_fn("NOT")
    def _xl_not(ctx, a):
        return not xl_to_bool(_xl_arg(a, 0))


    @xl_fn("XOR")
    def _xl_xor(ctx, a):
        return sum(1 for v in xl_flat(a) if xl_to_bool(v)) % 2 == 1


    @xl_fn("TRUE")
    def _xl_true(ctx, a):
        return True


    @xl_fn("FALSE")
    def _xl_false(ctx, a):
        return False


    @xl_fn("NA")
    def _xl_na(ctx, a):
        _xl_fail(XL_ERR_NA)


    @xl_fn("ISBLANK")
    def _xl_isblank(ctx, a):
        v = xl_as_scalar(_xl_arg(a, 0))
        return v is None or v == ""


    @xl_fn("ISNUMBER")
    def _xl_isnumber(ctx, a):
        return xl_is_number(xl_as_scalar(_xl_arg(a, 0)))


    @xl_fn("ISTEXT")
    def _xl_istext(ctx, a):
        v = xl_as_scalar(_xl_arg(a, 0))
        return isinstance(v, str) and v != ""


    @xl_fn("ISEVEN")
    def _xl_iseven(ctx, a):
        return xl_to_int(_xl_arg(a, 0)) % 2 == 0


    @xl_fn("ISODD")
    def _xl_isodd(ctx, a):
        return xl_to_int(_xl_arg(a, 0)) % 2 == 1


    @xl_fn("ISERROR")
    def _xl_iserror(ctx, a):
        return isinstance(xl_as_scalar(_xl_arg(a, 0)), XlError)


    @xl_fn("ISNA")
    def _xl_isna(ctx, a):
        return xl_as_scalar(_xl_arg(a, 0)) == XL_ERR_NA


    # --- text -----------------------------------------------------------------
    @xl_fn("CONCAT", "CONCATENATE")
    def _xl_concat(ctx, a):
        return "".join(xl_to_text(v) for v in xl_flat(a))


    @xl_fn("TEXTJOIN")
    def _xl_textjoin(ctx, a):
        sep = xl_to_text(_xl_arg(a, 0))
        skip = xl_to_bool(_xl_arg(a, 1, True))
        parts = [xl_to_text(v) for v in xl_flat(a[2:])]
        if skip:
            parts = [p for p in parts if p != ""]
        return sep.join(parts)


    @xl_fn("LEN")
    def _xl_len(ctx, a):
        return len(xl_to_text(_xl_arg(a, 0)))


    @xl_fn("LEFT")
    def _xl_left(ctx, a):
        return xl_to_text(_xl_arg(a, 0))[:xl_to_int(_xl_arg(a, 1, 1))]


    @xl_fn("RIGHT")
    def _xl_right(ctx, a):
        n = xl_to_int(_xl_arg(a, 1, 1))
        s = xl_to_text(_xl_arg(a, 0))
        return s[-n:] if n > 0 else ""


    @xl_fn("MID")
    def _xl_mid(ctx, a):
        s = xl_to_text(_xl_arg(a, 0))
        start = xl_to_int(_xl_arg(a, 1)) - 1
        n = xl_to_int(_xl_arg(a, 2))
        if start < 0 or n < 0:
            _xl_fail(XL_ERR_VALUE)
        return s[start:start + n]


    @xl_fn("UPPER")
    def _xl_upper(ctx, a):
        return xl_to_text(_xl_arg(a, 0)).upper()


    @xl_fn("LOWER")
    def _xl_lower(ctx, a):
        return xl_to_text(_xl_arg(a, 0)).lower()


    @xl_fn("PROPER")
    def _xl_proper(ctx, a):
        return xl_to_text(_xl_arg(a, 0)).title()


    @xl_fn("TRIM")
    def _xl_trim(ctx, a):
        return " ".join(xl_to_text(_xl_arg(a, 0)).split())


    @xl_fn("REPT")
    def _xl_rept(ctx, a):
        return xl_to_text(_xl_arg(a, 0)) * max(0, xl_to_int(_xl_arg(a, 1)))


    @xl_fn("SUBSTITUTE")
    def _xl_substitute(ctx, a):
        s, old, new = xl_to_text(_xl_arg(a, 0)), xl_to_text(_xl_arg(a, 1)), xl_to_text(_xl_arg(a, 2))
        if len(a) > 3:
            n = xl_to_int(a[3])
            parts = s.split(old)
            if n < 1 or len(parts) <= n:
                return s
            return old.join(parts[:n]) + new + old.join(parts[n:])
        return s.replace(old, new)


    @xl_fn("REPLACE")
    def _xl_replace(ctx, a):
        s = xl_to_text(_xl_arg(a, 0))
        start = xl_to_int(_xl_arg(a, 1)) - 1
        n = xl_to_int(_xl_arg(a, 2))
        return s[:start] + xl_to_text(_xl_arg(a, 3)) + s[start + n:]


    @xl_fn("FIND")
    def _xl_find(ctx, a):
        needle, hay = xl_to_text(_xl_arg(a, 0)), xl_to_text(_xl_arg(a, 1))
        start = xl_to_int(_xl_arg(a, 2, 1)) - 1
        idx = hay.find(needle, start)
        if idx < 0:
            _xl_fail(XL_ERR_VALUE)
        return idx + 1


    @xl_fn("SEARCH")
    def _xl_search(ctx, a):
        needle = xl_to_text(_xl_arg(a, 0)).upper()
        hay = xl_to_text(_xl_arg(a, 1)).upper()
        start = xl_to_int(_xl_arg(a, 2, 1)) - 1
        idx = hay.find(needle, start)
        if idx < 0:
            _xl_fail(XL_ERR_VALUE)
        return idx + 1


    @xl_fn("EXACT")
    def _xl_exact(ctx, a):
        return xl_to_text(_xl_arg(a, 0)) == xl_to_text(_xl_arg(a, 1))


    @xl_fn("CHAR")
    def _xl_char(ctx, a):
        return chr(xl_to_int(_xl_arg(a, 0)))


    @xl_fn("CODE")
    def _xl_code(ctx, a):
        s = xl_to_text(_xl_arg(a, 0))
        if not s:
            _xl_fail(XL_ERR_VALUE)
        return ord(s[0])


    @xl_fn("VALUE")
    def _xl_value(ctx, a):
        return xl_to_num(_xl_arg(a, 0))


    @xl_fn("TEXT")
    def _xl_text(ctx, a):
        return xl_format_value(xl_as_scalar(_xl_arg(a, 0)), xl_to_text(_xl_arg(a, 1)))


    _xl_DATE_TOKENS = ("yyyy", "yy", "mmmm", "mmm", "mm", "dddd", "ddd", "dd", "d",
                    "m", "hh", "h", "ss", "s")


    def xl_format_value(value, pattern):
        """Formatare minimala in stil Excel pentru TEXT()."""
        p = pattern
        low = p.lower()
        if any(tok in low for tok in ("yy", "dd", "hh", "mmm")) or \
                re.search(r"[dy]", low) and re.search(r"[./-]", low):
            try:
                dt = xl_serial_to_dt(xl_to_num(value))
            except _xl_Stop:
                return xl_to_text(value)
            parts, i = [], 0
            while i < len(low):
                for tok in _xl_DATE_TOKENS:
                    if low.startswith(tok, i):
                        parts.append(("tok", tok))
                        i += len(tok)
                        break
                else:
                    parts.append(("lit", p[i]))
                    i += 1
            out = []
            for k, (kind, val) in enumerate(parts):
                if kind == "lit":
                    out.append(val)
                    continue
                if val in ("m", "mm"):
                    # ca in Excel: m/mm inseamna minute langa ore sau secunde
                    prev = None
                    for t, v in reversed(parts[:k]):
                        if t == "tok":
                            prev = v
                            break
                    nxt = None
                    for t, v in parts[k + 1:]:
                        if t == "tok":
                            nxt = v
                            break
                    if prev in ("h", "hh") or nxt in ("s", "ss"):
                        out.append("%02d" % dt.minute if val == "mm"
                                   else str(dt.minute))
                        continue
                out.append(_xl_fmt_token(val, dt))
            return "".join(out)
        if "%" in p:
            digits = len(p.split(".")[1].replace("%", "")) if "." in p else 0
            return ("{:,.%df}%%" % digits).format(xl_to_num(value) * 100)
        if "0" in p or "#" in p:
            digits = len(p.split(".")[1].replace("0", "0").rstrip("#")) \
                if "." in p else 0
            s = ("{:,.%df}" % digits).format(xl_to_num(value))
            if "," not in p:
                s = s.replace(",", "")
            return s
        return xl_to_text(value)


    def _xl_fmt_token(tok, dt):
        return {
            "yyyy": "%04d" % dt.year, "yy": "%02d" % (dt.year % 100),
            "mmmm": dt.strftime("%B"), "mmm": dt.strftime("%b"),
            "mm": "%02d" % dt.month, "m": str(dt.month),
            "dddd": dt.strftime("%A"), "ddd": dt.strftime("%a"),
            "dd": "%02d" % dt.day, "d": str(dt.day),
            "hh": "%02d" % dt.hour, "h": str(dt.hour),
            "ss": "%02d" % dt.second, "s": str(dt.second),
        }[tok]


    # --- cautare / referinte --------------------------------------------------
    @xl_fn("ROWS")
    def _xl_rows(ctx, a):
        r = _xl_arg(a, 0)
        return r.nrows if isinstance(r, XlCellRange) else 1


    @xl_fn("COLUMNS")
    def _xl_columns(ctx, a):
        r = _xl_arg(a, 0)
        return r.ncols if isinstance(r, XlCellRange) else 1


    @xl_fn("ROW")
    def _xl_row(ctx, a):
        r = _xl_arg(a, 0)
        if isinstance(r, XlCellRange):
            return r.r1 + 1
        return ctx.row + 1


    @xl_fn("COLUMN")
    def _xl_column(ctx, a):
        r = _xl_arg(a, 0)
        if isinstance(r, XlCellRange):
            return r.c1 + 1
        return ctx.col + 1


    @xl_fn("ADDRESS")
    def _xl_address(ctx, a):
        r, c = xl_to_int(_xl_arg(a, 0)), xl_to_int(_xl_arg(a, 1))
        return "$%s$%d" % (xl_col_to_name(c - 1), r)


    @xl_fn("INDIRECT")
    def _xl_indirect(ctx, a):
        text = xl_to_text(_xl_arg(a, 0))
        sheet = None
        if "!" in text:
            sheet, text = text.split("!", 1)
            sheet = sheet.strip("'")
        if ":" in text:
            p1, p2 = text.split(":", 1)
            a1, a2 = xl_parse_a1(p1), xl_parse_a1(p2)
            if not a1 or not a2:
                _xl_fail(XL_ERR_REF)
            return XlCellRange(ctx, sheet or ctx.sheet, a1[0], a1[1], a2[0], a2[1])
        rc = xl_parse_a1(text)
        if not rc:
            _xl_fail(XL_ERR_REF)
        return ctx.cell_value(sheet, rc[0], rc[1])


    @xl_fn("INDEX")
    def _xl_index(ctx, a):
        rng = _xl_arg(a, 0)
        if not isinstance(rng, XlCellRange):
            return rng
        i = xl_to_int(_xl_arg(a, 1, 1))
        j = xl_to_int(_xl_arg(a, 2, 0)) if len(a) > 2 else 0
        if rng.nrows == 1 and len(a) < 3:
            i, j = 1, i
        if j == 0:
            j = 1
        if i < 1 or j < 1 or i > rng.nrows or j > rng.ncols:
            _xl_fail(XL_ERR_REF)
        return rng.cell(i - 1, j - 1)


    @xl_fn("MATCH")
    def _xl_match(ctx, a):
        target = xl_as_scalar(_xl_arg(a, 0))
        rng = _xl_arg(a, 1)
        mtype = xl_to_int(_xl_arg(a, 2, 1)) if len(a) > 2 else 1
        vals = xl_flat([rng])
        if mtype == 0:
            test = xl_make_criteria(target) if isinstance(target, str) \
                else (lambda v: xl_compare(v, target) == 0)
            for i, v in enumerate(vals):
                if test(v):
                    return i + 1
            _xl_fail(XL_ERR_NA)
        best = None
        for i, v in enumerate(vals):
            if v is None or v == "":
                continue
            c = xl_compare(v, target)
            if mtype == 1 and c <= 0:
                best = i + 1
            elif mtype == -1 and c >= 0:
                best = i + 1
        if best is None:
            _xl_fail(XL_ERR_NA)
        return best


    @xl_fn("VLOOKUP")
    def _xl_vlookup(ctx, a):
        target = xl_as_scalar(_xl_arg(a, 0))
        rng = _xl_arg(a, 1)
        col = xl_to_int(_xl_arg(a, 2))
        approx = xl_to_bool(_xl_arg(a, 3, True)) if len(a) > 3 else True
        if not isinstance(rng, XlCellRange):
            _xl_fail(XL_ERR_VALUE)
        if col < 1 or col > rng.ncols:
            _xl_fail(XL_ERR_REF)
        best = None
        for i in range(rng.nrows):
            v = rng.cell(i, 0)
            c = xl_compare(v, target)
            if c == 0:
                return rng.cell(i, col - 1)
            if approx and c < 0:
                best = i
        if approx and best is not None:
            return rng.cell(best, col - 1)
        _xl_fail(XL_ERR_NA)


    @xl_fn("HLOOKUP")
    def _xl_hlookup(ctx, a):
        target = xl_as_scalar(_xl_arg(a, 0))
        rng = _xl_arg(a, 1)
        row = xl_to_int(_xl_arg(a, 2))
        approx = xl_to_bool(_xl_arg(a, 3, True)) if len(a) > 3 else True
        if not isinstance(rng, XlCellRange):
            _xl_fail(XL_ERR_VALUE)
        if row < 1 or row > rng.nrows:
            _xl_fail(XL_ERR_REF)
        best = None
        for j in range(rng.ncols):
            v = rng.cell(0, j)
            c = xl_compare(v, target)
            if c == 0:
                return rng.cell(row - 1, j)
            if approx and c < 0:
                best = j
        if approx and best is not None:
            return rng.cell(row - 1, best)
        _xl_fail(XL_ERR_NA)


    @xl_fn("LOOKUP")
    def _xl_lookup(ctx, a):
        target = xl_as_scalar(_xl_arg(a, 0))
        src = xl_flat([_xl_arg(a, 1)])
        dst = xl_flat([_xl_arg(a, 2)]) if len(a) > 2 else src
        best = None
        for i, v in enumerate(src):
            if v is None or v == "":
                continue
            if xl_compare(v, target) <= 0:
                best = i
        if best is None or best >= len(dst):
            _xl_fail(XL_ERR_NA)
        return dst[best]


    # --- data si ora ----------------------------------------------------------
    @xl_fn("TODAY")
    def _xl_today(ctx, a):
        return int(xl_dt_to_serial(datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0)))


    @xl_fn("NOW")
    def _xl_now(ctx, a):
        return xl_dt_to_serial(datetime.datetime.now())


    @xl_fn("DATE")
    def _xl_date(ctx, a):
        try:
            y, m, d = xl_to_int(_xl_arg(a, 0)), xl_to_int(_xl_arg(a, 1)), xl_to_int(_xl_arg(a, 2))
            base = datetime.datetime(y, 1, 1)
            base = _xl_add_months(base, m - 1)
            return int(xl_dt_to_serial(base + datetime.timedelta(days=d - 1)))
        except (ValueError, OverflowError):
            _xl_fail(XL_ERR_NUM)


    @xl_fn("TIME")
    def _xl_time(ctx, a):
        h, m, s = xl_to_int(_xl_arg(a, 0)), xl_to_int(_xl_arg(a, 1)), xl_to_int(_xl_arg(a, 2))
        return (h * 3600 + m * 60 + s) / 86400.0


    def _xl_add_months(dt, months):
        month = dt.month - 1 + months
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 or not year % 400)
                           else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return dt.replace(year=year, month=month, day=day)


    def _xl_dt_arg(a, i=0):
        try:
            return xl_serial_to_dt(xl_to_num(_xl_arg(a, i)))
        except (ValueError, OverflowError):
            _xl_fail(XL_ERR_NUM)


    @xl_fn("YEAR")
    def _xl_year(ctx, a):
        return _xl_dt_arg(a).year


    @xl_fn("MONTH")
    def _xl_month(ctx, a):
        return _xl_dt_arg(a).month


    @xl_fn("DAY")
    def _xl_day(ctx, a):
        return _xl_dt_arg(a).day


    @xl_fn("HOUR")
    def _xl_hour(ctx, a):
        return _xl_dt_arg(a).hour


    @xl_fn("MINUTE")
    def _xl_minute(ctx, a):
        return _xl_dt_arg(a).minute


    @xl_fn("SECOND")
    def _xl_second(ctx, a):
        return _xl_dt_arg(a).second


    @xl_fn("WEEKDAY")
    def _xl_weekday(ctx, a):
        dt = _xl_dt_arg(a)
        mode = xl_to_int(_xl_arg(a, 1, 1)) if len(a) > 1 else 1
        iso = dt.isoweekday()          # luni=1 ... duminica=7
        if mode == 2:
            return iso
        if mode == 3:
            return iso - 1
        return 1 if iso == 7 else iso + 1


    @xl_fn("DAYS")
    def _xl_days(ctx, a):
        return int(xl_to_num(_xl_arg(a, 0)) - xl_to_num(_xl_arg(a, 1)))


    @xl_fn("EDATE")
    def _xl_edate(ctx, a):
        return int(xl_dt_to_serial(_xl_add_months(_xl_dt_arg(a), xl_to_int(_xl_arg(a, 1)))))


    @xl_fn("EOMONTH")
    def _xl_eomonth(ctx, a):
        dt = _xl_add_months(_xl_dt_arg(a), xl_to_int(_xl_arg(a, 1)))
        nxt = _xl_add_months(dt.replace(day=1), 1)
        return int(xl_dt_to_serial(nxt - datetime.timedelta(days=1)))


    @xl_fn("DATEVALUE")
    def _xl_datevalue(ctx, a):
        s = xl_to_text(_xl_arg(a, 0)).strip()
        for f in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
            try:
                return int(xl_dt_to_serial(datetime.datetime.strptime(s, f)))
            except ValueError:
                continue
        _xl_fail(XL_ERR_VALUE)


    # ===========================================================================
    # 10. API public al motorului
    # ===========================================================================
    _xl_AST_CACHE = {}


    def xl_compile_formula(text):
        node = _xl_AST_CACHE.get(text)
        if node is None:
            node = XlParser(xl_tokenize(text)).parse()
            if len(_xl_AST_CACHE) > 5000:
                _xl_AST_CACHE.clear()
            _xl_AST_CACHE[text] = node
        return node


    def xl_evaluate(formula, workbook, sheet, row, col):
        """Evalueaza '=...' si intoarce o valoare sau un XlError (nu ridica)."""
        try:
            node = xl_compile_formula(formula[1:] if formula.startswith("=") else formula)
            val = _xl_eval(node, XlEvalContext(workbook, sheet, row, col))
            val = xl_as_scalar(val)
            if isinstance(val, float) and abs(val) != float("inf"):
                if val == int(val) and abs(val) < 1e15:
                    val = int(val)
                else:
                    val = round(val, 12)
            return val
        except _xl_Stop as e:
            return e.err
        except RecursionError:
            return XL_ERR_CYCLE
        except ZeroDivisionError:
            return XL_ERR_DIV0
        except Exception:
            return XL_ERR_VALUE


    def xl_function_names():
        return sorted(set(list(XL_FUNCTIONS.keys()) + list(_xl_LAZY)))


    # ===========================================================================
    # 11. Partea Qt: workbook, model de foaie, proxy de filtrare, dialoguri
    # ===========================================================================
    from PyQt5.QtCore import (QAbstractTableModel, QModelIndex, QSortFilterProxyModel,
                              Qt)
    from PyQt5.QtGui import QColor, QKeySequence
    from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication, QCheckBox,
                                 QComboBox, QSplitter,
                                 QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
                                 QLineEdit, QListWidget, QListWidgetItem, QMenu,
                                 QPushButton, QShortcut, QTableView, QVBoxLayout)

    XL_ERROR_COLOR = QColor("#ff6b6b")


    def xl_display_text(value):
        """Textul afisat in celula pentru o valoare deja evaluata."""
        if value is None:
            return ""
        if isinstance(value, XlError):
            return value.code
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        if isinstance(value, float):
            if value == int(value) and abs(value) < 1e15:
                return str(int(value))
            return ("%.10f" % value).rstrip("0").rstrip(".")
        return str(value)


    _xl_PERCENT_RE = re.compile(r"^([+-]?(?:\d+(?:\.\d+)?|\.\d+))\s*%$")


    _xl_SIMPLE_NUM_RE = re.compile(r"^[#,0.]+$")
    _xl_SIMPLE_DATE_RE = re.compile(r"^[dmyhs:./\- ]+$", re.I)
    _xl_TYPED_DATE_RE = re.compile(
        r"^(\d{1,2})([./-])(\d{1,2})\2(\d{4})$|^(\d{4})-(\d{1,2})-(\d{1,2})$")


    def xl_cell_format(number_format):
        """Excel number format -> format intern suportat, sau None.

        Se accepta doar tipare simple: procente, date si numere. Orice altceva
        (General, formate contabile complicate) e ignorat.
        """
        if not number_format:
            return None
        fmt = str(number_format).strip()
        if fmt in ("General", "@", ""):
            return None
        if fmt.endswith("%") and _xl_SIMPLE_NUM_RE.match(fmt[:-1] or "0"):
            m = re.search(r"\.(0+)", fmt)
            return "0." + "0" * len(m.group(1)) + "%" if m else "0%"
        low = fmt.lower()
        if _xl_SIMPLE_DATE_RE.match(low) and re.search(r"[dyh]", low):
            return low
        if _xl_SIMPLE_NUM_RE.match(fmt):
            return fmt
        return None


    def xl_from_excel_cell(cell):
        """Valoarea si formatul unei celule citite cu openpyxl.

        Datele si orele devin numere seriale, ca in Excel, ca sa poata intra in
        calcule; formatul se pastreaza doar pentru afisare.
        """
        value = cell.value
        fmt = xl_cell_format(cell.number_format)
        if isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
            value = xl_dt_to_serial(value)
            if not fmt:
                fmt = "dd.mm.yyyy"
        elif isinstance(value, datetime.time):
            value = (value.hour * 3600 + value.minute * 60 + value.second) / 86400.0
            if not fmt:
                fmt = "hh:mm:ss"
        elif isinstance(value, datetime.timedelta):
            value = value.total_seconds() / 86400.0
            if not fmt:
                fmt = "hh:mm:ss"
        return value, fmt


    def xl_parse_input(text):
        """Textul tastat -> (valoare bruta, format de celula sau None).

        Ca in Excel: '100%' se pastreaza ca 1 dar se afiseaza tot '100%'.
        """
        if isinstance(text, str):
            m = _xl_PERCENT_RE.match(text.strip())
            if m:
                digits = m.group(1)
                dec = len(digits.split(".")[1]) if "." in digits else 0
                fmt = ("0." + "0" * dec + "%") if dec else "0%"
                return float(digits) / 100.0, fmt
            m = _xl_TYPED_DATE_RE.match(text.strip())
            if m:
                if m.group(1):
                    day, month, year = m.group(1), m.group(3), m.group(4)
                    sep = m.group(2)
                else:
                    year, month, day = m.group(5), m.group(6), m.group(7)
                    sep = "-"
                try:
                    serial = xl_dt_to_serial(datetime.datetime(int(year), int(month),
                                                            int(day)))
                except ValueError:
                    return xl_coerce_input(text), None
                fmt = ("yyyy-mm-dd" if sep == "-" and len(year) == 4
                       and m.group(5) else "dd%smm%syyyy" % (sep, sep))
                return int(serial), fmt
        return xl_coerce_input(text), None


    def xl_coerce_input(text):
        """Converteste ce a tastat utilizatorul in numar / bool / text / formula."""
        if text is None:
            return None
        if not isinstance(text, str):
            return text
        s = text.strip()
        if s == "":
            return None
        if s.startswith("="):
            return s
        up = s.upper()
        if up in ("TRUE", "FALSE"):
            return up == "TRUE"
        try:
            if re.match(r"^[+-]?\d+$", s):
                return int(s)
            return float(s)
        except ValueError:
            return text


    # ---------------------------------------------------------------------------
    class XlWorkbook(object):
        """Detine toate foile, cache-ul de evaluare, undo/redo si flag-ul dirty."""

        def __init__(self):
            self.sheets = {}          # nume_lower -> XlSheetModel
            self._cache = {}
            self._stack = set()
            self.undo_stack = []
            self.redo_stack = []
            self.dirty = False
            self.path = None

        # --- gestiunea foilor -------------------------------------------------
        def add_sheet(self, model):
            self.sheets[model.name.lower()] = model
            self.invalidate()

        def remove_sheet(self, name):
            self.sheets.pop(name.lower(), None)
            self.undo_stack = [b for b in self.undo_stack
                               if all(e[0].lower() != name.lower() for e in b)]
            self.redo_stack = []
            self.invalidate()

        def rename_sheet(self, old, new):
            model = self.sheets.pop(old.lower(), None)
            if model is not None:
                model.name = new
                self.sheets[new.lower()] = model
            self.invalidate()

        def clear(self):
            self.sheets.clear()
            self.undo_stack = []
            self.redo_stack = []
            self.invalidate()

        def unique_name(self, base="Sheet"):
            i = 1
            while ("%s%d" % (base, i)).lower() in self.sheets:
                i += 1
            return "%s%d" % (base, i)

        # --- evaluare ---------------------------------------------------------
        def value(self, sheet, row, col):
            model = self.sheets.get((sheet or "").lower())
            if model is None:
                return XL_ERR_REF
            key = (model.name.lower(), row, col)
            if key in self._cache:
                return self._cache[key]
            if key in self._stack:
                return XL_ERR_CYCLE
            raw = model.raw(row, col)
            if isinstance(raw, str) and raw.startswith("=") and len(raw) > 1:
                self._stack.add(key)
                try:
                    val = xl_evaluate(raw, self, model.name, row, col)
                finally:
                    self._stack.discard(key)
            else:
                val = raw
            self._cache[key] = val
            return val

        def invalidate(self):
            self._cache.clear()

        def refresh(self):
            """Goleste cache-ul si cere repictarea tuturor foilor."""
            self.invalidate()
            for model in self.sheets.values():
                if model.rowCount() and model.columnCount():
                    model.dataChanged.emit(
                        model.index(0, 0),
                        model.index(model.rowCount() - 1, model.columnCount() - 1))

        # --- undo / redo ------------------------------------------------------
        def push_undo(self, entries):
            if not entries:
                return
            self.undo_stack.append(entries)
            if len(self.undo_stack) > 200:
                self.undo_stack.pop(0)
            self.redo_stack = []
            self.dirty = True

        def _apply(self, entries, use_old):
            for entry in entries:
                sheet, row, col, old, new = entry[:5]
                old_fmt, new_fmt = (entry[5], entry[6]) if len(entry) > 6 else (None, None)
                model = self.sheets.get(sheet.lower())
                if model is not None:
                    model.set_raw(row, col, old if use_old else new)
                    model.set_format(row, col, old_fmt if use_old else new_fmt)
            self.refresh()

        def undo(self):
            if not self.undo_stack:
                return False
            batch = self.undo_stack.pop()
            self._apply(batch, True)
            self.redo_stack.append(batch)
            self.dirty = True
            return True

        def redo(self):
            if not self.redo_stack:
                return False
            batch = self.redo_stack.pop()
            self._apply(batch, False)
            self.undo_stack.append(batch)
            self.dirty = True
            return True


    # ---------------------------------------------------------------------------
    class XlSheetModel(QAbstractTableModel):
        """Modelul unei foi. Pastreaza datele brute; evaluarea o face workbook-ul."""

        def __init__(self, workbook, name, data=None,
                     rows=XL_DEFAULT_ROWS, cols=XL_DEFAULT_COLS, parent=None):
            QAbstractTableModel.__init__(self, parent)
            self.workbook = workbook
            self.name = name
            self._xl_rows = max(rows, XL_DEFAULT_ROWS)
            self._cols = min(max(cols, XL_DEFAULT_COLS), XL_MAX_COLS)
            self._data = [[None] * self._cols for _ in range(self._xl_rows)]
            self._fmt = {}             # (row, col) -> format de celula ("0%", ...)
            if data:
                for r, row in enumerate(data[:self._xl_rows]):
                    for c, v in enumerate(row[:self._cols]):
                        self._data[r][c] = v

        # --- acces brut -------------------------------------------------------
        def raw(self, row, col):
            if 0 <= row < self._xl_rows and 0 <= col < self._cols:
                return self._data[row][col]
            return None

        def set_raw(self, row, col, value):
            if 0 <= row < self._xl_rows and 0 <= col < self._cols:
                self._data[row][col] = value

        def value(self, row, col):
            return self.workbook.value(self.name, row, col)

        def get_format(self, row, col):
            return self._fmt.get((row, col))

        def set_format(self, row, col, fmt):
            if fmt:
                self._fmt[(row, col)] = fmt
            else:
                self._fmt.pop((row, col), None)

        def formatted(self, value, row, col):
            fmt = self._fmt.get((row, col))
            if fmt and xl_is_number(value):
                return xl_format_value(value, fmt)
            return xl_display_text(value)

        def is_empty(self):
            for row in self._data:
                for v in row:
                    if v is not None and v != "":
                        return False
            return True

        def used_range(self):
            last_r, last_c = -1, -1
            for r in range(self._xl_rows):
                for c in range(self._cols):
                    if self._data[r][c] not in (None, ""):
                        last_r = max(last_r, r)
                        last_c = max(last_c, c)
            return last_r + 1, last_c + 1

        # --- interfata QAbstractTableModel -----------------------------------
        def rowCount(self, parent=QModelIndex()):
            return 0 if parent.isValid() else self._xl_rows

        def columnCount(self, parent=QModelIndex()):
            return 0 if parent.isValid() else self._cols

        def data(self, index, role=Qt.DisplayRole):
            if not index.isValid():
                return None
            row, col = index.row(), index.column()
            if role == Qt.DisplayRole or role == Qt.ToolTipRole:
                return self.formatted(self.value(row, col), row, col)
            if role == Qt.EditRole:
                raw = self.raw(row, col)
                if raw is None:
                    return ""
                if isinstance(raw, str):
                    return raw
                return self.formatted(raw, row, col)
            if role == Qt.TextAlignmentRole:
                v = self.value(row, col)
                if xl_is_number(v):
                    return int(Qt.AlignRight | Qt.AlignVCenter)
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            if role == Qt.ForegroundRole:
                if isinstance(self.value(row, col), XlError):
                    return XL_ERROR_COLOR
            return None

        def setData(self, index, value, role=Qt.EditRole):
            if role != Qt.EditRole or not index.isValid():
                return False
            row, col = index.row(), index.column()
            new, new_fmt = xl_parse_input(value)
            old, old_fmt = self.raw(row, col), self.get_format(row, col)
            if old == new and old_fmt == new_fmt:
                return True
            self.set_raw(row, col, new)
            self.set_format(row, col, new_fmt)
            self.workbook.push_undo(
                [(self.name, row, col, old, new, old_fmt, new_fmt)])
            self.workbook.refresh()
            return True

        def set_many(self, cells):
            """cells = [(row, col, valoare_bruta)] -- o singura intrare de undo."""
            entries = []
            for row, col, val in cells:
                if not (0 <= row < self._xl_rows and 0 <= col < self._cols):
                    continue
                new, new_fmt = xl_parse_input(val)
                old, old_fmt = self.raw(row, col), self.get_format(row, col)
                if old == new and old_fmt == new_fmt:
                    continue
                self.set_raw(row, col, new)
                self.set_format(row, col, new_fmt)
                entries.append((self.name, row, col, old, new, old_fmt, new_fmt))
            if entries:
                self.workbook.push_undo(entries)
                self.workbook.refresh()
            return len(entries)

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if role != Qt.DisplayRole:
                return None
            if orientation == Qt.Horizontal:
                return xl_col_to_name(section)
            return str(section + 1)

        def flags(self, index):
            if not index.isValid():
                return Qt.NoItemFlags
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable


    # ---------------------------------------------------------------------------
    class XlSheetFilterProxy(QSortFilterProxyModel):
        """Sortare + filtre pe coloana, in stil AutoFilter."""

        def __init__(self, parent=None):
            QSortFilterProxyModel.__init__(self, parent)
            self.filters = {}          # col -> set(texte permise)
            self.header_row = False    # True = randul 1 ramane mereu vizibil
            self._order = Qt.AscendingOrder

        # --- filtre -----------------------------------------------------------
        def set_filter(self, col, allowed):
            if allowed is None:
                self.filters.pop(col, None)
            else:
                self.filters[col] = set(allowed)
            self.invalidateFilter()

        def clear_filters(self):
            self.filters.clear()
            self.invalidateFilter()

        def has_filter(self, col):
            return col in self.filters

        def filterAcceptsRow(self, row, parent):
            if not self.filters:
                return True
            if self.header_row and row == 0:
                return True
            src = self.sourceModel()
            for col, allowed in self.filters.items():
                idx = src.index(row, col, parent)
                if src.data(idx, Qt.DisplayRole) not in allowed:
                    return False
            return True

        # --- sortare ----------------------------------------------------------
        def sort(self, column, order=Qt.AscendingOrder):
            self._order = order
            QSortFilterProxyModel.sort(self, column, order)

        def lessThan(self, left, right):
            if self.header_row:
                if left.row() == 0:
                    return self._order == Qt.AscendingOrder
                if right.row() == 0:
                    return self._order != Qt.AscendingOrder
            src = self.sourceModel()
            a = src.value(left.row(), left.column())
            b = src.value(right.row(), right.column())
            empty_a = a is None or a == ""
            empty_b = b is None or b == ""
            if empty_a or empty_b:
                return empty_b and not empty_a
            try:
                return xl_compare(a, b) < 0
            except _xl_Stop:
                return False

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if orientation == Qt.Vertical and role == Qt.DisplayRole:
                src_row = self.mapToSource(self.index(section, 0)).row()
                return str(src_row + 1)
            return QSortFilterProxyModel.headerData(self, section, orientation, role)


    # ---------------------------------------------------------------------------
    class XlFilterDialog(QDialog):
        """Lista de valori distincte cu bife, ca la AutoFilter din Excel."""

        def __init__(self, parent, column_name, values, checked):
            QDialog.__init__(self, parent)
            self.setWindowTitle("Filter - column %s" % column_name)
            self.resize(280, 380)
            layout = QVBoxLayout(self)

            self.search = QLineEdit()
            self.search.setPlaceholderText("Search...")
            self.search.textChanged.connect(self._apply_search)
            layout.addWidget(self.search)

            row = QHBoxLayout()
            self.all_box = QCheckBox("(Select all)")
            self.all_box.setTristate(True)
            self.all_box.clicked.connect(self._toggle_all)
            row.addWidget(self.all_box)
            row.addStretch(1)
            layout.addLayout(row)

            self.list = QListWidget()
            for v in values:
                item = QListWidgetItem("(blank)" if v == "" else v)
                item.setData(Qt.UserRole, v)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if v in checked else Qt.Unchecked)
                self.list.addItem(item)
            layout.addWidget(self.list)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            clear = QPushButton("Clear filter")
            clear.clicked.connect(self._clear)
            buttons.addButton(clear, QDialogButtonBox.ResetRole)
            layout.addWidget(buttons)
            self.cleared = False
            self._sync_all_box()

        def _apply_search(self, text):
            text = text.lower()
            for i in range(self.list.count()):
                item = self.list.item(i)
                item.setHidden(text not in item.text().lower())

        def _toggle_all(self):
            state = Qt.Checked if self.all_box.checkState() != Qt.Checked \
                else Qt.Unchecked
            self.all_box.setCheckState(state)
            for i in range(self.list.count()):
                item = self.list.item(i)
                if not item.isHidden():
                    item.setCheckState(state)

        def _sync_all_box(self):
            total = self.list.count()
            on = sum(1 for i in range(total)
                     if self.list.item(i).checkState() == Qt.Checked)
            self.all_box.setCheckState(Qt.Checked if on == total else
                                       (Qt.Unchecked if on == 0 else
                                        Qt.PartiallyChecked))

        def _clear(self):
            self.cleared = True
            self.accept()

        def selected(self):
            return [self.list.item(i).data(Qt.UserRole)
                    for i in range(self.list.count())
                    if self.list.item(i).checkState() == Qt.Checked]


    # ===========================================================================
    # 12. Helper-e pentru fereastra principala (ExcelViewer)
    # ===========================================================================
    XL_VIEW_STYLE = """
    QTableView {
        background-color: #121212;
        color: #ffffff;
        gridline-color: #808080;
        border: 2px solid #000000;
        selection-background-color: #2f4f2f;
        selection-color: #ccff66;
    }
    QTableView::item:selected { background-color: #2f4f2f; color: #ccff66; }
    QHeaderView::section {
        background-color: #4C4F51; color: #FFFFFF; font-weight: bold;
        border: 1px solid #000000; padding: 2px;
    }
    QTableCornerButton::section { background-color: #4C4F51; border: 1px solid #000000; }
    """


    def xl_source_model(view):
        """Modelul real din spatele proxy-ului de filtrare."""
        model = view.model()
        return model.sourceModel() if isinstance(model, XlSheetFilterProxy) else model


    def xl_proxy_of(view):
        model = view.model()
        return model if isinstance(model, XlSheetFilterProxy) else None


    def xl_create_sheet_view(window, model):
        """Construieste QTableView + proxy + meniu de filtre + scurtaturi."""
        view = QTableView()
        proxy = XlSheetFilterProxy(view)
        proxy.setSourceModel(model)
        proxy.setDynamicSortFilter(False)
        view.setModel(proxy)
        view.setStyleSheet(XL_VIEW_STYLE)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        view.setEditTriggers(QAbstractItemView.DoubleClicked |
                             QAbstractItemView.EditKeyPressed |
                             QAbstractItemView.AnyKeyPressed)
        view.setAlternatingRowColors(False)
        view.horizontalHeader().setSectionsClickable(True)
        view.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        view.horizontalHeader().customContextMenuRequested.connect(
            lambda pos, v=view: xl_show_header_menu(window, v, pos))
        view.verticalHeader().setDefaultSectionSize(22)

        QShortcut(QKeySequence.Copy, view, activated=lambda v=view: xl_copy_selection(v))
        QShortcut(QKeySequence.Paste, view, activated=lambda v=view: xl_paste_selection(v))
        QShortcut(QKeySequence.Cut, view, activated=lambda v=view: xl_cut_selection(v))
        QShortcut(QKeySequence.Delete, view, activated=lambda v=view: xl_clear_selection(v))
        return view


    # --- clipboard (compatibil cu Excel real, prin TSV) ------------------------
    _xl_REF_IN_FORMULA = re.compile(
        r'"(?:[^"]|"")*"'
        r'|(?<![A-Za-z0-9_$])(\$?)([A-Za-z]{1,3})(\$?)([0-9]{1,7})(?![A-Za-z0-9_(])')

    _xl_CLIP = {"text": None, "row": 0, "col": 0}


    def xl_translate_formula(formula, dr, dc):
        """Muta referintele relative dintr-o formula cu (dr, dc) celule."""
        def sub(m):
            if m.group(0).startswith('"'):
                return m.group(0)
            cdol, letters, rdol, digits = m.groups()
            col = xl_name_to_col(letters) + (0 if cdol else dc)
            row = int(digits) - 1 + (0 if rdol else dr)
            if row < 0 or col < 0 or row >= XL_MAX_ROWS or col >= XL_MAX_COLS:
                return "#REF!"
            return "%s%s%s%d" % (cdol, xl_col_to_name(col), rdol, row + 1)
        return _xl_REF_IN_FORMULA.sub(sub, formula)


    def _xl_selected_block(view):
        idx = view.selectionModel().selectedIndexes()
        if not idx:
            return None
        rows = sorted(set(i.row() for i in idx))
        cols = sorted(set(i.column() for i in idx))
        return rows, cols


    def xl_copy_selection(view):
        block = _xl_selected_block(view)
        if not block:
            return
        rows, cols = block
        model = view.model()
        lines = []
        for r in rows:
            cells = []
            for c in cols:
                val = model.data(model.index(r, c), Qt.EditRole)
                cells.append("" if val is None else str(val))
            lines.append("\t".join(cells))
        text = "\n".join(lines)
        proxy = xl_proxy_of(view)
        top = view.model().index(rows[0], cols[0])
        if proxy is not None:
            top = proxy.mapToSource(top)
        _xl_CLIP["text"], _xl_CLIP["row"], _xl_CLIP["col"] = text, top.row(), top.column()
        QApplication.clipboard().setText(text)


    def xl_cut_selection(view):
        xl_copy_selection(view)
        xl_clear_selection(view)


    def xl_clear_selection(view):
        idx = view.selectionModel().selectedIndexes()
        if not idx:
            return
        proxy, model = view.model(), xl_source_model(view)
        cells = []
        for i in idx:
            src = proxy.mapToSource(i) if isinstance(proxy, XlSheetFilterProxy) else i
            cells.append((src.row(), src.column(), None))
        model.set_many(cells)


    def xl_paste_selection(view):
        text = QApplication.clipboard().text()
        if not text:
            return
        idx = view.selectionModel().selectedIndexes()
        if not idx:
            return
        anchor = sorted(idx, key=lambda i: (i.row(), i.column()))[0]
        proxy, model = view.model(), xl_source_model(view)
        src = proxy.mapToSource(anchor) if isinstance(proxy, XlSheetFilterProxy) else anchor
        r0, c0 = src.row(), src.column()
        internal = (text == _xl_CLIP["text"])
        dr, dc = (r0 - _xl_CLIP["row"], c0 - _xl_CLIP["col"]) if internal else (0, 0)
        cells = []
        for i, line in enumerate(text.replace("\r\n", "\n").rstrip("\n").split("\n")):
            for j, val in enumerate(line.split("\t")):
                if internal and (dr or dc) and isinstance(val, str) \
                        and val.startswith("="):
                    val = "=" + xl_translate_formula(val[1:], dr, dc)
                cells.append((r0 + i, c0 + j, val))
        model.set_many(cells)


    # --- sortare / filtrare ----------------------------------------------------
    def xl_sort_column(view, col, order):
        proxy = xl_proxy_of(view)
        if proxy is None:
            return
        proxy.sort(col, order)


    def xl_open_filter_dialog(window, view, col):
        proxy, model = xl_proxy_of(view), xl_source_model(view)
        if proxy is None:
            return
        start = 1 if proxy.header_row else 0
        seen, values = set(), []
        for r in range(start, model.rowCount()):
            txt = model.data(model.index(r, col), Qt.DisplayRole)
            if txt not in seen:
                seen.add(txt)
                values.append(txt)
        values.sort(key=lambda s: (s == "", s.lower()))
        checked = proxy.filters.get(col, set(values))
        dlg = XlFilterDialog(window, xl_col_to_name(col), values, checked)
        if dlg.exec_() == QDialog.Accepted:
            if dlg.cleared:
                proxy.set_filter(col, None)
            else:
                chosen = dlg.selected()
                proxy.set_filter(col, None if len(chosen) == len(values) else chosen)


    def xl_show_header_menu(window, view, pos):
        header = view.horizontalHeader()
        col = header.logicalIndexAt(pos)
        if col < 0:
            return
        proxy = xl_proxy_of(view)
        menu = QMenu(view)
        menu.addAction("Sort A -> Z",
                       lambda: xl_sort_column(view, col, Qt.AscendingOrder))
        menu.addAction("Sort Z -> A",
                       lambda: xl_sort_column(view, col, Qt.DescendingOrder))
        menu.addSeparator()
        menu.addAction("Filter...", lambda: xl_open_filter_dialog(window, view, col))
        act_clear = menu.addAction("Clear filter on this column",
                                   lambda: proxy.set_filter(col, None))
        act_clear.setEnabled(proxy is not None and proxy.has_filter(col))
        menu.addAction("Clear all filters", lambda: xl_clear_all(view))
        menu.addSeparator()
        act_hdr = menu.addAction("First row is header")
        act_hdr.setCheckable(True)
        act_hdr.setChecked(bool(proxy and proxy.header_row))
        act_hdr.triggered.connect(lambda on: xl_toggle_header_row(view, on))
        menu.exec_(header.mapToGlobal(pos))


    def xl_clear_all(view):
        proxy = xl_proxy_of(view)
        if proxy is not None:
            proxy.clear_filters()
            proxy.sort(-1)


    def xl_toggle_header_row(view, on):
        proxy = xl_proxy_of(view)
        if proxy is not None:
            proxy.header_row = bool(on)
            proxy.invalidateFilter()


    def xl_add_data_menu(window):
        """Adauga meniul 'Data' + undo/redo in bara de meniu existenta."""
        def current():
            return window.tabs.currentWidget()

        menubar = window.menuBar()
        data_menu = menubar.addMenu("Data")

        def act(text, slot, shortcut=None):
            a = QAction(text, window)
            a.triggered.connect(slot)
            if shortcut:
                a.setShortcut(shortcut)
            data_menu.addAction(a)
            return a

        def with_view(func):
            def run(*_):
                view = current()
                if view is not None:
                    func(view)
            return run

        def current_col(view):
            idx = view.currentIndex()
            return idx.column() if idx.isValid() else 0

        act("Sort Ascending",
            with_view(lambda v: xl_sort_column(v, current_col(v), Qt.AscendingOrder)))
        act("Sort Descending",
            with_view(lambda v: xl_sort_column(v, current_col(v), Qt.DescendingOrder)))
        data_menu.addSeparator()
        act("Filter Column...",
            with_view(lambda v: xl_open_filter_dialog(window, v, current_col(v))),
            "Ctrl+Shift+L")
        act("Clear All Filters", with_view(xl_clear_all))
        hdr = QAction("First Row Is Header", window)
        hdr.setCheckable(True)
        hdr.triggered.connect(with_view(
            lambda v, a=hdr: xl_toggle_header_row(v, a.isChecked())))
        data_menu.addAction(hdr)
        data_menu.addSeparator()
        act("Undo", lambda: window.workbook.undo(), "Ctrl+Z")
        act("Redo", lambda: window.workbook.redo(), "Ctrl+Y")
        return data_menu


    # ===========================================================================
    # 13. Documentatia functiilor + fereastra de Help
    # ===========================================================================
    # (nume, parametri, descriere, exemplu)
    _xl_DOCS = {
        "Basics": [
            ("Writing a formula", "",
             "Every formula starts with '='. Confirm with Enter. The cell shows the "
             "result, while the formula bar at the top shows the formula itself and "
             "can be used to edit it.",
             "=A1+A2*2"),
            ("Operators", "",
             "Arithmetic: + - * / ^ (power) % (percent, written after a number).\n"
             "Text: & joins two texts.\n"
             "Comparison: = <> < > <= >= return TRUE or FALSE.\n"
             "Order: % then ^ then * / then + - then & then comparisons. Use "
             "parentheses to change it.",
             '=(A1+A2)*10%  |  ="Total: "&B1  |  =A1>=100'),
            ("Cell references", "",
             "A1 is column A row 1. A1:C10 is a rectangular range. $A$1 stays fixed "
             "when the formula is copied, A1 moves with it, $A1 fixes only the "
             "column and A$1 only the row. Sheet2!A1 points to another sheet. "
             "Columns go from A to CV.",
             "=SUM(Sheet2!$A$1:$A$20)"),
            ("Percentages", "",
             "Typing 20% in a cell stores the value 0.2 but keeps showing 20%, "
             "exactly like Excel. Any formula using that cell works with 0.2.",
             "=A1*20%"),
            ("Dates", "",
             "Dates are stored as serial numbers counted from 30.12.1899, so you can "
             "add and subtract them. Use TEXT to display them in a readable form.",
             '=TEXT(TODAY(),"dd.mm.yyyy")'),
            ("Error values", "",
             "#DIV/0! division by zero. #VALUE! wrong type of argument. #REF! "
             "invalid reference. #NAME? unknown function or misspelled name. #N/A "
             "value not found. #NUM! invalid number. #CYCLE! the cell refers to "
             "itself. Wrap a formula in IFERROR to replace the error.",
             '=IFERROR(A1/B1,0)'),
            ("Sorting and filtering", "",
             "Right click a column header, or use the Data menu, to sort the sheet "
             "or to filter it with checkboxes. Turn on 'First row is header' to keep "
             "row 1 pinned at the top while sorting.", ""),
            ("Keyboard shortcuts", "",
             "Ctrl+C copy, Ctrl+X cut, Ctrl+V paste, Delete clear contents, "
             "Ctrl+Z undo, Ctrl+Y redo, Ctrl+O open, Ctrl+S save, "
             "Ctrl+Shift+L filter the current column. Copying a formula shifts its "
             "relative references, and you can paste to and from real Excel.", ""),
        ],
        "Math": [
            ("SUM", "number1, [number2], ...", "Adds all numbers in the cells or ranges given.", "=SUM(A1:C3)"),
            ("PRODUCT", "number1, [number2], ...", "Multiplies all numbers given.", "=PRODUCT(A1:A5)"),
            ("ABS", "number", "Absolute value, without the sign.", "=ABS(-5)"),
            ("SIGN", "number", "Returns 1 for positive, -1 for negative, 0 for zero.", "=SIGN(A1)"),
            ("INT", "number", "Rounds down to the nearest whole number.", "=INT(2.9)"),
            ("TRUNC", "number, [decimals]", "Cuts off the decimals without rounding.", "=TRUNC(2.789,2)"),
            ("ROUND", "number, decimals", "Rounds to the given number of decimals.", "=ROUND(2.567,2)"),
            ("ROUNDUP", "number, decimals", "Always rounds away from zero.", "=ROUNDUP(2.001,2)"),
            ("ROUNDDOWN", "number, decimals", "Always rounds towards zero.", "=ROUNDDOWN(2.999,2)"),
            ("CEILING", "number, significance", "Rounds up to the nearest multiple of significance.", "=CEILING(7,5)"),
            ("FLOOR", "number, significance", "Rounds down to the nearest multiple of significance.", "=FLOOR(7,5)"),
            ("MOD", "number, divisor", "Remainder of the division.", "=MOD(10,3)"),
            ("POWER", "number, exponent", "Raises number to the given power. POW does the same.", "=POWER(2,10)"),
            ("POW", "number, exponent", "Same as POWER.", "=POW(2,10)"),
            ("SQRT", "number", "Square root. Negative numbers give #NUM!.", "=SQRT(16)"),
            ("EXP", "number", "e raised to the given power.", "=EXP(1)"),
            ("LN", "number", "Natural logarithm.", "=LN(10)"),
            ("LOG", "number, [base]", "Logarithm in the given base, 10 by default.", "=LOG(8,2)"),
            ("LOG10", "number", "Base 10 logarithm.", "=LOG10(1000)"),
            ("PI", "", "The number pi, 3.14159...", "=PI()*A1^2"),
            ("RAND", "", "Random number between 0 and 1.", "=RAND()"),
            ("RANDBETWEEN", "bottom, top", "Random whole number between the two limits.", "=RANDBETWEEN(1,100)"),
            ("FACT", "number", "Factorial of the number.", "=FACT(5)"),
            ("GCD", "number1, [number2], ...", "Greatest common divisor.", "=GCD(12,18)"),
            ("LCM", "number1, [number2], ...", "Least common multiple.", "=LCM(4,6)"),
            ("SUMPRODUCT", "range1, range2, ...", "Multiplies the ranges element by element and adds the results. Ideal for quantity times price.", "=SUMPRODUCT(A1:A10,B1:B10)"),
            ("DEGREES", "radians", "Converts radians into degrees.", "=DEGREES(PI())"),
            ("RADIANS", "degrees", "Converts degrees into radians.", "=RADIANS(180)"),
            ("SIN", "number", "Sine of an angle given in radians.", "=SIN(RADIANS(30))"),
            ("COS", "number", "Cosine of an angle given in radians.", "=COS(0)"),
            ("TAN", "number", "Tangent of an angle given in radians.", "=TAN(RADIANS(45))"),
            ("ASIN", "number", "Arcsine, the result is in radians.", "=ASIN(1)"),
            ("ACOS", "number", "Arccosine, the result is in radians.", "=ACOS(0)"),
            ("ATAN", "number", "Arctangent, the result is in radians.", "=ATAN(1)"),
            ("ATAN2", "x, y", "Arctangent of y/x, taking the quadrant into account.", "=ATAN2(1,1)"),
            ("SINH", "number", "Hyperbolic sine.", "=SINH(1)"),
            ("COSH", "number", "Hyperbolic cosine.", "=COSH(1)"),
            ("TANH", "number", "Hyperbolic tangent.", "=TANH(1)"),
        ],
        "Statistics": [
            ("AVERAGE", "number1, [number2], ...", "Arithmetic mean of the numbers. Text and empty cells are ignored.", "=AVERAGE(A1:A10)"),
            ("MIN", "number1, [number2], ...", "Smallest value.", "=MIN(A1:A10)"),
            ("MAX", "number1, [number2], ...", "Largest value.", "=MAX(A1:A10)"),
            ("MEDIAN", "number1, [number2], ...", "Middle value of the sorted list.", "=MEDIAN(A1:A10)"),
            ("MODE", "number1, [number2], ...", "The most frequent value. Gives #N/A if nothing repeats.", "=MODE(A1:A10)"),
            ("COUNT", "value1, [value2], ...", "Counts only the cells that contain numbers.", "=COUNT(A1:A10)"),
            ("COUNTA", "value1, [value2], ...", "Counts every non empty cell, text included.", "=COUNTA(A1:A10)"),
            ("COUNTBLANK", "range", "Counts the empty cells in the range.", "=COUNTBLANK(A1:A10)"),
            ("COUNTIF", "range, criteria", "Counts the cells that meet one condition. Criteria can be a number, a text, a comparison in quotes or a pattern with * and ?.", '=COUNTIF(A1:A10,">100")'),
            ("COUNTIFS", "range1, criteria1, range2, criteria2, ...", "Counts the rows that meet all conditions at the same time.", '=COUNTIFS(A1:A10,"Cluj",B1:B10,">100")'),
            ("SUMIF", "range, criteria, [sum_range]", "Adds the values that meet the condition. Without sum_range it adds the range itself.", '=SUMIF(A1:A10,"Cluj",B1:B10)'),
            ("SUMIFS", "sum_range, range1, criteria1, ...", "Adds the values whose rows meet all conditions. The range to add comes first here.", '=SUMIFS(C1:C10,A1:A10,"Cluj",B1:B10,">100")'),
            ("AVERAGEIF", "range, criteria, [average_range]", "Average of the values that meet the condition.", '=AVERAGEIF(A1:A10,"Cluj",B1:B10)'),
            ("AVERAGEIFS", "average_range, range1, criteria1, ...", "Average of the values whose rows meet all conditions.", '=AVERAGEIFS(C1:C10,A1:A10,"Cluj")'),
            ("STDEV", "number1, [number2], ...", "Standard deviation of a sample.", "=STDEV(A1:A10)"),
            ("STDEVA", "number1, [number2], ...", "Same as STDEV.", "=STDEVA(A1:A10)"),
            ("STDEVP", "number1, [number2], ...", "Standard deviation of the whole population.", "=STDEVP(A1:A10)"),
            ("VAR", "number1, [number2], ...", "Variance of a sample.", "=VAR(A1:A10)"),
            ("VARP", "number1, [number2], ...", "Variance of the whole population.", "=VARP(A1:A10)"),
            ("LARGE", "range, k", "The k-th largest value in the range.", "=LARGE(A1:A10,3)"),
            ("SMALL", "range, k", "The k-th smallest value in the range.", "=SMALL(A1:A10,3)"),
            ("RANK", "number, range, [ascending]", "Position of the number in the range. Leave the third argument out for descending order.", "=RANK(A1,$A$1:$A$10)"),
        ],
        "Logical": [
            ("IF", "condition, value_if_true, [value_if_false]", "Returns one value when the condition is TRUE and another when it is FALSE. Only the needed branch is calculated.", '=IF(A1>=5,"pass","fail")'),
            ("IFS", "condition1, value1, condition2, value2, ...", "Checks the conditions in order and returns the value of the first true one.", '=IFS(A1>90,"A",A1>75,"B",A1>50,"C")'),
            ("IFERROR", "value, value_if_error", "Returns the second argument if the first one produces any error.", "=IFERROR(A1/B1,0)"),
            ("IFNA", "value, value_if_na", "Like IFERROR but it only catches #N/A.", '=IFNA(VLOOKUP(A1,D:E,2,FALSE),"not found")'),
            ("AND", "condition1, [condition2], ...", "TRUE only when every condition is TRUE.", "=AND(A1>0,A1<100)"),
            ("OR", "condition1, [condition2], ...", "TRUE when at least one condition is TRUE.", '=OR(A1="Cluj",A1="Bacau")'),
            ("NOT", "condition", "Reverses TRUE and FALSE.", "=NOT(A1>10)"),
            ("XOR", "condition1, [condition2], ...", "TRUE when an odd number of conditions are TRUE.", "=XOR(A1>0,B1>0)"),
            ("TRUE", "", "The logical value TRUE.", "=TRUE()"),
            ("FALSE", "", "The logical value FALSE.", "=FALSE()"),
            ("CHOOSE", "index, value1, value2, ...", "Returns the value found at the given position.", '=CHOOSE(A1,"low","medium","high")'),
        ],
        "Information": [
            ("ISBLANK", "value", "TRUE when the cell is empty.", "=ISBLANK(A1)"),
            ("ISNUMBER", "value", "TRUE when the value is a number.", "=ISNUMBER(A1)"),
            ("ISTEXT", "value", "TRUE when the value is text.", "=ISTEXT(A1)"),
            ("ISERROR", "value", "TRUE for any error value.", "=ISERROR(A1/B1)"),
            ("ISERR", "value", "TRUE for any error except #N/A.", "=ISERR(A1)"),
            ("ISNA", "value", "TRUE only for #N/A.", "=ISNA(A1)"),
            ("ISEVEN", "number", "TRUE when the number is even.", "=ISEVEN(A1)"),
            ("ISODD", "number", "TRUE when the number is odd.", "=ISODD(A1)"),
            ("NA", "", "Produces the #N/A error on purpose.", "=NA()"),
        ],
        "Text": [
            ("CONCAT", "text1, [text2], ...", "Joins texts and ranges into a single text.", "=CONCAT(A1:B2)"),
            ("CONCATENATE", "text1, [text2], ...", "Same as CONCAT.", '=CONCATENATE(A1," ",B1)'),
            ("TEXTJOIN", "separator, ignore_empty, text1, ...", "Joins the values with a separator between them.", '=TEXTJOIN(", ",TRUE,A1:A10)'),
            ("LEN", "text", "Number of characters, spaces included.", "=LEN(A1)"),
            ("LEFT", "text, [count]", "The first characters of the text.", "=LEFT(A1,3)"),
            ("RIGHT", "text, [count]", "The last characters of the text.", "=RIGHT(A1,4)"),
            ("MID", "text, start, count", "Characters starting at a given position, counting from 1.", "=MID(A1,4,6)"),
            ("UPPER", "text", "Converts the text to upper case.", "=UPPER(A1)"),
            ("LOWER", "text", "Converts the text to lower case.", "=LOWER(A1)"),
            ("PROPER", "text", "Capitalises the first letter of every word.", "=PROPER(A1)"),
            ("TRIM", "text", "Removes leading, trailing and repeated spaces.", "=TRIM(A1)"),
            ("REPT", "text, count", "Repeats the text a number of times.", '=REPT("-",20)'),
            ("SUBSTITUTE", "text, old, new, [occurrence]", "Replaces a piece of text. Without occurrence it replaces every match.", '=SUBSTITUTE(A1,".",",")'),
            ("REPLACE", "text, start, count, new_text", "Replaces the characters found at a given position.", '=REPLACE(A1,1,3,"RO")'),
            ("FIND", "needle, text, [start]", "Position of the searched text, case sensitive. Gives #VALUE! when not found.", '=FIND("-",A1)'),
            ("SEARCH", "needle, text, [start]", "Like FIND but it ignores upper and lower case.", '=SEARCH("cluj",A1)'),
            ("EXACT", "text1, text2", "TRUE only when the two texts are identical, case included.", "=EXACT(A1,B1)"),
            ("CHAR", "code", "The character with the given code.", "=CHAR(65)"),
            ("CODE", "text", "Numeric code of the first character.", '=CODE("A")'),
            ("VALUE", "text", "Converts a text that looks like a number into a real number.", '=VALUE("12.5")'),
            ("TEXT", "value, format", 'Formats a number or a date as text. Useful formats: "0.00", "#,##0.00", "0%", "dd.mm.yyyy", "yyyy-mm-dd".', '=TEXT(A1,"#,##0.00")'),
        ],
        "Lookup": [
            ("VLOOKUP", "value, table, column, [approximate]", "Searches the value in the first column of the table and returns the value from the column with the given number. Use FALSE for an exact match.", "=VLOOKUP(A1,Data!$A$1:$C$100,3,FALSE)"),
            ("HLOOKUP", "value, table, row, [approximate]", "Same as VLOOKUP but it searches along the first row of the table.", "=HLOOKUP(A1,Data!A1:Z2,2,FALSE)"),
            ("LOOKUP", "value, search_range, [result_range]", "Searches in a sorted range and returns the matching value from the other range.", "=LOOKUP(A1,D1:D10,E1:E10)"),
            ("INDEX", "range, row, [column]", "The value found at the given row and column inside the range.", "=INDEX(A1:C10,2,3)"),
            ("MATCH", "value, range, [type]", "The position of the value in the range. Use 0 for an exact match. Works very well together with INDEX.", "=INDEX(C1:C10,MATCH(A1,B1:B10,0))"),
            ("ROW", "[reference]", "The row number of the reference, or of the current cell when left empty.", "=ROW(B7)"),
            ("COLUMN", "[reference]", "The column number of the reference, or of the current cell when left empty.", "=COLUMN(C1)"),
            ("ROWS", "range", "How many rows the range has.", "=ROWS(A1:C10)"),
            ("COLUMNS", "range", "How many columns the range has.", "=COLUMNS(A1:C10)"),
            ("ADDRESS", "row, column", "Builds the address of a cell as text.", "=ADDRESS(2,3)"),
            ("INDIRECT", "reference_text", "Turns a text into a real reference.", '=SUM(INDIRECT("A1:A"&B1))'),
        ],
        "Date & Time": [
            ("TODAY", "", "Today's date.", '=TEXT(TODAY(),"dd.mm.yyyy")'),
            ("NOW", "", "The current date and time.", "=NOW()"),
            ("DATE", "year, month, day", "Builds a date out of the three numbers.", "=DATE(2026,3,15)"),
            ("TIME", "hour, minute, second", "Builds a time as a fraction of a day.", "=TIME(14,30,0)"),
            ("YEAR", "date", "The year of the date.", "=YEAR(A1)"),
            ("MONTH", "date", "The month of the date, 1 to 12.", "=MONTH(A1)"),
            ("DAY", "date", "The day of the month.", "=DAY(A1)"),
            ("HOUR", "time", "The hour, 0 to 23.", "=HOUR(A1)"),
            ("MINUTE", "time", "The minutes, 0 to 59.", "=MINUTE(A1)"),
            ("SECOND", "time", "The seconds, 0 to 59.", "=SECOND(A1)"),
            ("WEEKDAY", "date, [type]", "Day of the week. Type 1 starts on Sunday, type 2 starts on Monday.", "=WEEKDAY(A1,2)"),
            ("DAYS", "end_date, start_date", "Number of days between two dates.", "=DAYS(B1,A1)"),
            ("EDATE", "date, months", "The same day a number of months later or earlier.", "=EDATE(A1,3)"),
            ("EOMONTH", "date, months", "The last day of the month, after moving a number of months.", "=EOMONTH(A1,0)"),
            ("DATEVALUE", "text", "Converts a written date into a real date. It understands dd.mm.yyyy, dd/mm/yyyy and yyyy-mm-dd.", '=DATEVALUE("15.03.2026")'),
        ],
    }

    XL_FUNCTION_DOCS = {}
    for _xl_cat, _xl_items in _xl_DOCS.items():
        for _xl_n, _xl_p, _xl_d, _xl_e in _xl_items:
            XL_FUNCTION_DOCS[_xl_n] = (_xl_cat, _xl_p, _xl_d, _xl_e)


    def xl_function_signature(name):
        doc = XL_FUNCTION_DOCS.get(name)
        if not doc or doc[0] == "Basics":
            return name
        return "%s(%s)" % (name, doc[1])


    def xl_undocumented_functions():
        """Diagnostic: functii implementate care nu apar in Help."""
        return sorted(n for n in xl_function_names() if n not in XL_FUNCTION_DOCS)


    class XlHelpDialog(QDialog):
        """Lista de functii cu parametri, descriere si exemplu."""

        def __init__(self, parent=None):
            QDialog.__init__(self, parent)
            self.setWindowTitle("Excel Lite - Help and function reference")
            self.resize(860, 560)
            self._parent_window = parent

            layout = QVBoxLayout(self)

            top = QHBoxLayout()
            self.category = QComboBox()
            self.category.addItem("All categories")
            for cat in _xl_DOCS:
                self.category.addItem(cat)
            self.category.currentIndexChanged.connect(self._reload)
            top.addWidget(self.category, 1)
            self.search = QLineEdit()
            self.search.setPlaceholderText("Search a function or a keyword...")
            self.search.textChanged.connect(self._reload)
            top.addWidget(self.search, 2)
            layout.addLayout(top)

            body = QSplitter(Qt.Horizontal)
            self.list = QListWidget()
            self.list.currentItemChanged.connect(self._show_details)
            self.list.itemDoubleClicked.connect(self._insert)
            body.addWidget(self.list)
            self.details = QTextEdit()
            self.details.setReadOnly(True)
            body.addWidget(self.details)
            body.setSizes([280, 580])
            layout.addWidget(body)

            row = QHBoxLayout()
            self.count_label = QLabel()
            row.addWidget(self.count_label, 1)
            insert_button = QPushButton("Insert in cell")
            insert_button.clicked.connect(lambda: self._insert(self.list.currentItem()))
            row.addWidget(insert_button)
            close_button = QPushButton("Close")
            close_button.clicked.connect(self.accept)
            row.addWidget(close_button)
            layout.addLayout(row)

            self._reload()

        # --- continut ---------------------------------------------------------
        def _reload(self, *_):
            wanted = self.category.currentText()
            text = self.search.text().strip().lower()
            self.list.clear()
            shown = 0
            for cat, items in _xl_DOCS.items():
                if wanted != "All categories" and cat != wanted:
                    continue
                for name, params, desc, example in items:
                    blob = " ".join((name, params, desc, example)).lower()
                    if text and text not in blob:
                        continue
                    label = name if cat == "Basics" else "%s(%s)" % (name, params)
                    item = QListWidgetItem(label)
                    item.setData(Qt.UserRole, name)
                    self.list.addItem(item)
                    shown += 1
            self.count_label.setText("%d entries - double click to insert a function"
                                     % shown)
            if self.list.count():
                self.list.setCurrentRow(0)
            else:
                self.details.setPlainText("Nothing found.")

        def _show_details(self, item, *_):
            if item is None:
                return
            name = item.data(Qt.UserRole)
            cat, params, desc, example = XL_FUNCTION_DOCS[name]
            if cat == "Basics":
                parts = [name, "", desc]
                if example:
                    parts += ["", "Example:", "    " + example]
            else:
                parts = ["%s(%s)" % (name, params), "",
                         "Category: " + cat, "", desc, "",
                         "Example:", "    " + example, "",
                         "Arguments written between [ ] are optional. "
                         "Arguments are separated by a comma or a semicolon."]
            self.details.setPlainText("\n".join(parts))

        def _insert(self, item):
            """Pune '=NUME(' in bara de formule a ferestrei principale."""
            if item is None:
                return
            name = item.data(Qt.UserRole)
            if XL_FUNCTION_DOCS[name][0] == "Basics":
                return
            window = self._parent_window
            editor = getattr(window, "formula_line_edit", None)
            if editor is None:
                return
            editor.setText("=%s(" % name)
            self.accept()
            editor.setFocus()


    def xl_show_help_dialog(window):
        XlHelpDialog(window).exec_()


    class ExcelViewer(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle('Excel Lite')
            self.setGeometry(100, 100, 800, 600)

            self.main_widget = QWidget()
            self.setCentralWidget(self.main_widget)

            self.layout = QVBoxLayout()
            self.main_widget.setLayout(self.layout)

            # Holds every sheet model, the evaluation cache and the undo/redo stacks
            self.workbook = XlWorkbook()
            self.current_path = None

            # Formula bar: shows the raw content of the current cell and can edit it
            self.formula_line_edit = QLineEdit()
            self.formula_line_edit.setPlaceholderText("fx")
            self.formula_line_edit.returnPressed.connect(self.commit_formula)
            self.layout.addWidget(self.formula_line_edit)

            self.tabs = QTabWidget()
            self.layout.addWidget(self.tabs)

            self.create_menu()
            self.create_empty_sheet()

            self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D2D;  /* Dark background */
            }
            QWidget {
                background-color: #3C3F41;  /* Widget background */
                color: #ffffff;  /* White text */
            }
            QWidget::item:hover {
                background-color: #ccff66;
            }
            QWidget::item:selected {
                background-color: #121212;
            }
            QLineEdit {
                background-color: #4C4F51;  /* QLineEdit background */
                color: #FFFFFF;  /* White text */
                border: 1px solid #666;  /* Border */
            }
            QTabWidget::pane {
                background: #4d4d4d;  /* Tab pane background */
            }
            QTabBar::tab {
                background: #4d4d4d;  /* Tab background */
                color: #ccff66;  /* Tab text */
                padding: 10px;
                border: 2px solid #000000;
            }
            QTabBar::tab:selected {
                background: #121212;  /* Selected tab background */
                color: cyan;
            }
            QPushButton {
                background-color: #4C4F51;  /* Button background */
                color: #FFFFFF;  /* White text */
                border: none;  /* No border */
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #5A5E61;  /* Hover background */
            }
            QMessageBox {
                background-color: #3C3F41;  /* QMessageBox background */
                color: #FFFFFF;  /* White text */
            }
            QTableWidget {
                border: 2px solid #000000;  /* Black table outline */
                gridline-color: #666666;    /* Grid line color */
                background-color: #3C3F41;  /* Dark table background */
                color: #FFFFFF;              /* White table text */
            }
            QTableWidget::item {
                border: 1px solid #666666;  /* Cell border */
            }
            QTableWidget::item:selected {
                background-color: #121212;  /* Selected cell background */
            }
            QHeaderView::section {
                background-color: #4C4F51;  /* Row and column header background */
                color: #FFFFFF;              /* Header text color */
                font-weight: bold;           /* Bold header text */
            }
            QListWidget {
                background-color: #121212;
                color: #FFFFFF;
                border: 1px solid #666666;
            }
            QMenu {
                background-color: #3C3F41;
                color: #FFFFFF;
                border: 1px solid #000000;
            }
            QMenu::item:selected {
                background-color: #121212;
                color: #ccff66;
            }
        """)

        # ------------------------------------------------------------------
        # Menus
        # ------------------------------------------------------------------
        def create_menu(self):
            menubar = self.menuBar()
            
            file_menu = menubar.addMenu('File')
            
            new_file_action = QAction('New', self)
            new_file_action.triggered.connect(self.open_new_instance)
            file_menu.addAction(new_file_action)

            new_sheet_action = QAction('New Sheet', self)
            new_sheet_action.triggered.connect(self.create_new_sheet)
            file_menu.addAction(new_sheet_action)

            open_action = QAction('Open', self)
            open_action.setShortcut('Ctrl+O')
            open_action.triggered.connect(self.load_excel_file)
            file_menu.addAction(open_action)

            save_action = QAction('Save', self)
            save_action.setShortcut('Ctrl+S')
            save_action.triggered.connect(self.save_all_sheets)
            file_menu.addAction(save_action)

            delete_sheet_action = QAction('Delete Sheet', self)
            delete_sheet_action.triggered.connect(self.delete_sheet)
            file_menu.addAction(delete_sheet_action)

            # Edit Menu for Copy, Paste
            edit_menu = menubar.addMenu('Edit')

            # Copy action
            copy_action = QAction('Copy', self)
            copy_action.triggered.connect(self.copy_selected_cells)
            edit_menu.addAction(copy_action)

            # Cut action
            cut_action = QAction('Cut', self)
            cut_action.triggered.connect(self.cut_selected_cells)
            edit_menu.addAction(cut_action)

            # Paste action
            paste_action = QAction('Paste', self)
            paste_action.triggered.connect(self.paste_to_selected_cells)
            edit_menu.addAction(paste_action)

            # Clear action
            clear_action = QAction('Clear Contents', self)
            clear_action.triggered.connect(self.clear_selected_cells)
            edit_menu.addAction(clear_action)

            # Data Menu: sorting, column filters, undo/redo
            xl_add_data_menu(self)

            # Help Menu
            help_menu = menubar.addMenu('Help')

            about_action = QAction('About', self)
            about_action.triggered.connect(self.show_about_dialog)
            help_menu.addAction(about_action)

        def show_about_dialog(self):
            # Searchable reference: every function with its parameters,
            # a description and a working example. Double click inserts it.
            xl_show_help_dialog(self)

        # ------------------------------------------------------------------
        # Clipboard (Ctrl+C / Ctrl+X / Ctrl+V / Delete are wired on each view)
        # ------------------------------------------------------------------
        def copy_selected_cells(self):
            view = self.tabs.currentWidget()
            if view is not None:
                xl_copy_selection(view)

        def cut_selected_cells(self):
            view = self.tabs.currentWidget()
            if view is not None:
                xl_cut_selection(view)

        def paste_to_selected_cells(self):
            view = self.tabs.currentWidget()
            if view is not None:
                xl_paste_selection(view)

        def clear_selected_cells(self):
            view = self.tabs.currentWidget()
            if view is not None:
                xl_clear_selection(view)

        # ------------------------------------------------------------------
        # Sheets
        # ------------------------------------------------------------------
        def open_new_instance(self):
            if getattr(sys, 'frozen', False):
                subprocess.Popen([sys.executable])
            else:
                subprocess.Popen([sys.executable, os.path.abspath(__file__)])

        def create_empty_sheet(self):
            # Ask for the initial sheet name; never leave the window without a sheet
            sheet_name, ok = QInputDialog.getText(self, 'Input Sheet Name',
                                                  'Enter the name of the sheet:')
            if not ok or not sheet_name.strip():
                sheet_name = self.workbook.unique_name("Sheet")
            self.add_sheet(sheet_name.strip(), None)

        def create_new_sheet(self):
            while True:
                sheet_name, ok = QInputDialog.getText(self, 'New Sheet Name',
                                                      'Enter the name of the new sheet:')
                if not ok:
                    return
                sheet_name = sheet_name.strip()
                if not sheet_name:
                    QMessageBox.warning(self, 'Warning',
                                        'Sheet name cannot be empty. Please enter a valid name.')
                    continue
                # Sheet names are case insensitive, like in Excel
                if any(sheet_name.lower() == self.tabs.tabText(i).lower()
                       for i in range(self.tabs.count())):
                    QMessageBox.warning(self, 'Warning',
                                        'Sheet name already exists. Please choose another name.')
                    continue
                self.add_sheet(sheet_name, None)
                self.workbook.dirty = True
                return

        def delete_sheet(self):
            current_index = self.tabs.currentIndex()
            if current_index == -1:
                QMessageBox.warning(self, 'Warning', 'No sheet selected to delete.')
                return
            
            sheet_name = self.tabs.tabText(current_index)

            reply = QMessageBox.question(self, 'Confirm Delete',
                                         f'Are you sure you want to delete the sheet "{sheet_name}"?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.tabs.removeTab(current_index)
                # Drop the data too, not only the tab
                self.workbook.remove_sheet(sheet_name)
                self.workbook.dirty = True
                if self.tabs.count() == 0:
                    self.add_sheet(self.workbook.unique_name("Sheet"), None)
                QMessageBox.information(self, 'Deleted',
                                        f'Sheet "{sheet_name}" has been deleted.')

        def add_sheet(self, sheet_name, data):
            model = XlSheetModel(self.workbook, sheet_name, data)
            self.workbook.add_sheet(model)
            # Builds the QTableView, the filter proxy, the header menu and the shortcuts
            table_view = xl_create_sheet_view(self, model)
            table_view.selectionModel().selectionChanged.connect(
                lambda *_: self.update_formula_display(table_view))
            self.tabs.addTab(table_view, sheet_name)
            self.tabs.setCurrentWidget(table_view)
            return table_view

        # ------------------------------------------------------------------
        # Formula bar
        # ------------------------------------------------------------------
        def update_formula_display(self, table_view):
            index = table_view.currentIndex()
            if not index.isValid():
                self.formula_line_edit.clear()
                return
            # EditRole returns the raw content: the formula itself, not its result
            value = table_view.model().data(index, Qt.EditRole)
            self.formula_line_edit.setText("" if value is None else str(value))
            source_index = table_view.model().mapToSource(index)
            self.statusBar().showMessage("Cell: %s%d" % (xl_col_to_name(index.column()),
                                                         source_index.row() + 1))

        def commit_formula(self):
            table_view = self.tabs.currentWidget()
            if table_view is None:
                return
            index = table_view.currentIndex()
            if index.isValid():
                table_view.model().setData(index, self.formula_line_edit.text(),
                                           Qt.EditRole)
                table_view.setFocus()

        # ------------------------------------------------------------------
        # Open / Save
        # ------------------------------------------------------------------
        def load_excel_file(self):
            # Ask for the file first: cancelling must not destroy the current data
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Excel File", "",
                "Excel Files (*.xlsx);;All Files (*)", options=options)
            if not file_path:
                return

            if self.has_unsaved_changes():
                reply = QMessageBox.warning(
                    self, 'Warning',
                    'Data that has not been saved will be lost. Do you want to continue?',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return

            try:
                workbook = load_workbook(file_path)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Cannot open file:\n{e}')
                return

            self.tabs.clear()
            self.workbook.clear()
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                # Formulas are kept as text so the engine can evaluate them
                # Dates become serial numbers and percent cells keep showing
                # 20% instead of 0.2, exactly like in Excel
                data, formats = [], {}
                for row in sheet.iter_rows():
                    line = []
                    for cell in row:
                        value, cell_format = xl_from_excel_cell(cell)
                        line.append(value)
                        if cell_format:
                            formats[(cell.row - 1, cell.column - 1)] = cell_format
                    data.append(line)
                view = self.add_sheet(sheet_name, data)
                model = xl_source_model(view)
                for (r, c), cell_format in formats.items():
                    if r < model.rowCount() and c < model.columnCount():
                        model.set_format(r, c, cell_format)
            if self.tabs.count() == 0:
                self.add_sheet('Sheet1', None)

            self.current_path = file_path
            self.workbook.dirty = False
            self.setWindowTitle('Excel Lite - %s' % file_path)

        def save_all_sheets(self):
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Excel File", "",
                "Excel Files (*.xlsx);;All Files (*)", options=options)
            if not file_path:
                return
            if not file_path.lower().endswith('.xlsx'):
                file_path += '.xlsx'

            out = Workbook()
            if "Sheet" in out.sheetnames:
                del out["Sheet"]

            for i in range(self.tabs.count()):
                model = xl_source_model(self.tabs.widget(i))
                sheet = out.create_sheet(title=self.tabs.tabText(i))
                # Only the used range is written, so the file stays small
                nrows, ncols = model.used_range()
                for row_index in range(nrows):
                    for column_index in range(ncols):
                        value = model.raw(row_index, column_index)
                        if value is None or value == "":
                            continue
                        cell = sheet.cell(row=row_index + 1,
                                          column=column_index + 1, value=value)
                        cell_format = model.get_format(row_index, column_index)
                        if cell_format:
                            # so a percent cell still reads 20% in real Excel
                            cell.number_format = cell_format

            try:
                out.save(file_path)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Cannot save file:\n{e}')
                return

            self.current_path = file_path
            self.workbook.dirty = False
            self.setWindowTitle('Excel Lite - %s' % file_path)

        def has_unsaved_changes(self):
            # Real dirty flag, set by every edit, paste, undo or sheet removal
            return bool(self.workbook.dirty)

        def closeEvent(self, event):
            if self.has_unsaved_changes():
                reply = QMessageBox.question(
                    self, 'Exit', 'You have unsaved changes. Close anyway?',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    event.ignore()
                    return
            event.accept()

    if __name__ == '__main__':
        app = QApplication(sys.argv)
        viewer = ExcelViewer()
        viewer.show()
        sys.exit(app.exec_())
