#!/usr/bin/env python3
"""
SQL Manager Studio Pro - Advanced Database Management Tool
Dark Theme with Tabs, Drag & Drop, Custom Icons
"""

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import sqlite3
import os
import re
from datetime import datetime


class IconFactory:
    """Creates custom icons using Canvas"""
    
    @staticmethod
    def create_database_icon(canvas, x, y, size=16):
        s = size
        # Cilindru 3D cu gradient și umbră
        
        # Umbră
        canvas.create_oval(x+1, y+1, x+s+1, y+s//3+1, fill='#000000', outline='')
        
        # Corp cilindru (gradient - partea întunecată)
        canvas.create_rectangle(x, y+s//6, x+s, y+s-s//6, fill='#2A2A2A', outline='')
        
        # Strălucire laterală stângă
        canvas.create_rectangle(x, y+s//6, x+2, y+s-s//6, fill='#404040', outline='')
        
        # Strălucire laterală dreaptă
        canvas.create_rectangle(x+s-2, y+s//6, x+s, y+s-s//6, fill='#1A1A1A', outline='')
        
        # Elipsă de sus (partea vizibilă)
        canvas.create_oval(x, y, x+s, y+s//3, fill='#383838', outline='#FFFFFF', width=2)
        
        # Highlight pe elipsa de sus
        canvas.create_oval(x+2, y+1, x+s-2, y+s//4, fill='#505050', outline='')
        
        # Elipsă de jos
        canvas.create_oval(x, y+s-s//3, x+s, y+s, fill='#2A2A2A', outline='#FFFFFF', width=2)
        
        # Linii laterale (contur alb)
        canvas.create_line(x, y+s//6, x, y+s-s//6, fill='#FFFFFF', width=2)
        canvas.create_line(x+s, y+s//6, x+s, y+s-s//6, fill='#FFFFFF', width=2)
        
    @staticmethod
    def create_table_icon(canvas, x, y, size=16):
        s = size
        # Grid/table shape
        canvas.create_rectangle(x, y, x+s, y+s, fill='#2A2A2A', outline='#FFFFFF', width=2)
        canvas.create_line(x, y+s//3, x+s, y+s//3, fill='#FFFFFF', width=2)
        canvas.create_line(x, y+2*s//3, x+s, y+2*s//3, fill='#FFFFFF', width=1)
        canvas.create_line(x+s//2, y+s//3, x+s//2, y+s, fill='#FFFFFF', width=1)
        canvas.create_rectangle(x, y, x+s, y+s//3, fill='#404040', outline='#FFFFFF', width=2)
        
    @staticmethod
    def create_column_icon(canvas, x, y, size=16):
        s = size
        # Key/column shape
        canvas.create_rectangle(x+2, y+2, x+s-2, y+s-2, fill='#2A2A2A', outline='#FFFFFF', width=2)
        canvas.create_line(x+4, y+s//2, x+s-4, y+s//2, fill='#CCCCCC', width=2)
        
    @staticmethod
    def create_pk_icon(canvas, x, y, size=16):
        s = size
        # Key shape for primary key
        canvas.create_oval(x, y, x+s//2, y+s//2, fill='#FFD700', outline='#FFFFFF', width=2)
        canvas.create_rectangle(x+s//4, y+s//3, x+s, y+s//2, fill='#FFD700', outline='')
        canvas.create_line(x+s//2, y+s//2, x+s, y+s//2, fill='#FFFFFF', width=2)
        canvas.create_line(x+3*s//4, y+s//2, x+3*s//4, y+2*s//3, fill='#FFFFFF', width=2)
        canvas.create_line(x+s-2, y+s//2, x+s-2, y+2*s//3, fill='#FFFFFF', width=2)
        
    @staticmethod
    def create_folder_icon(canvas, x, y, size=16, open_state=False):
        s = size
        if open_state:
            canvas.create_polygon(x, y+s//4, x+s//3, y+s//4, x+s//2, y, x+s, y, 
                                  x+s, y+s//4, x+s, y+s, x, y+s,
                                  fill='#383838', outline='#FFFFFF', width=2)
        else:
            canvas.create_rectangle(x, y+s//4, x+s, y+s, fill='#383838', outline='#FFFFFF', width=2)
            canvas.create_rectangle(x, y+s//6, x+s//2, y+s//3, fill='#4A4A4A', outline='#FFFFFF', width=2)
            
    @staticmethod
    def create_view_icon(canvas, x, y, size=16):
        s = size
        # Eye shape for view
        canvas.create_oval(x, y+s//4, x+s, y+3*s//4, fill='#383838', outline='#FFFFFF', width=2)
        canvas.create_oval(x+s//3, y+s//3, x+2*s//3, y+2*s//3, fill='#CCCCCC', outline='#FFFFFF', width=2)
        
    @staticmethod
    def create_index_icon(canvas, x, y, size=16):
        s = size
        # Lightning bolt for index
        canvas.create_polygon(x+s//2, y, x+s//4, y+s//2, x+s//2, y+s//2,
                              x+s//3, y+s, x+3*s//4, y+s//2, x+s//2, y+s//2,
                              fill='#4A9FFF', outline='#FFFFFF', width=2)


class DraggableItem:
    """Handles drag and drop for tree items"""
    
    def __init__(self, widget, data, on_drag_start, on_drag_end):
        self.widget = widget
        self.data = data
        self.on_drag_start = on_drag_start
        self.on_drag_end = on_drag_end
        self.drag_window = None
        
        widget.bind('<ButtonPress-1>', self.start_drag)
        widget.bind('<B1-Motion>', self.do_drag)
        widget.bind('<ButtonRelease-1>', self.end_drag)
        
    def start_drag(self, event):
        self.on_drag_start(self.data)
        
    def do_drag(self, event):
        pass
        
    def end_drag(self, event):
        self.on_drag_end(event)


class QueryTab:
    """Represents a single query tab"""
    
    def __init__(self, parent, tab_id, name, colors, on_close, on_select):
        self.parent = parent
        self.tab_id = tab_id
        self.name = name
        self.colors = colors
        self.on_close = on_close
        self.on_select = on_select
        self.modified = False
        self.file_path = None
        
        self.frame = tk.Frame(parent, bg=colors['bg_medium'])
        
        self.tab_button = tk.Frame(self.frame, bg=colors['bg_medium'], cursor='hand2')
        self.tab_button.pack(side=tk.LEFT)
        
        self.label = tk.Label(self.tab_button, text=f"  {name}  ", 
            bg=colors['bg_medium'], fg=colors['text_dim'],
            font=('Segoe UI', 9), padx=4, pady=4)
        self.label.pack(side=tk.LEFT)
        
        self.close_btn = tk.Label(self.tab_button, text="x", 
            bg=colors['bg_medium'], fg=colors['text_dim'],
            font=('Segoe UI', 8), padx=4, cursor='hand2')
        self.close_btn.pack(side=tk.LEFT)
        
        self.label.bind('<Button-1>', lambda e: self.on_select(self.tab_id))
        self.tab_button.bind('<Button-1>', lambda e: self.on_select(self.tab_id))
        self.close_btn.bind('<Button-1>', lambda e: self.on_close(self.tab_id))
        
        self.close_btn.bind('<Enter>', lambda e: self.close_btn.configure(fg=colors['error']))
        self.close_btn.bind('<Leave>', lambda e: self.close_btn.configure(
            fg=colors['text'] if self.is_active else colors['text_dim']))
        
        self.is_active = False
        self.content = ""
        
    def set_active(self, active):
        self.is_active = active
        if active:
            self.label.configure(bg=self.colors['bg_dark'], fg=self.colors['text'])
            self.tab_button.configure(bg=self.colors['bg_dark'])
            self.close_btn.configure(bg=self.colors['bg_dark'], fg=self.colors['text'])
        else:
            self.label.configure(bg=self.colors['bg_medium'], fg=self.colors['text_dim'])
            self.tab_button.configure(bg=self.colors['bg_medium'])
            self.close_btn.configure(bg=self.colors['bg_medium'], fg=self.colors['text_dim'])
            
    def set_modified(self, modified):
        self.modified = modified
        display_name = f"  {self.name}{'*' if modified else ''}  "
        self.label.configure(text=display_name)
        
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        
    def destroy(self):
        self.frame.destroy()


class SQLManagerStudioPro:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Manager Studio Pro")
        self.root.geometry("1500x950")
        self.root.minsize(1200, 700)
        
        self.colors = {
            'bg_dark': '#1e1e1e',
            'bg_medium': '#252526',
            'bg_light': '#2d2d30',
            'bg_lighter': '#3c3c3c',
            'bg_hover': '#094771',
            'text': '#d4d4d4',
            'text_dim': '#808080',
            'accent': '#007acc',
            'accent_light': '#1c97ea',
            'success': '#4ec9b0',
            'warning': '#dcdcaa',
            'error': '#f14c4c',
            'keyword': '#569cd6',
            'string': '#ce9178',
            'comment': '#6a9955',
            'number': '#b5cea8',
            'function': '#dcdcaa',
            'border': '#3f3f46',
            'selection': '#264f78',
            'tree_bg': '#252526',
            'grid_header': '#3c3c3c',
            'grid_row_alt': '#2a2a2a',
            'drop_target': '#264f78',
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        
        self.connection = None
        self.current_db_path = None
        self.query_history = []
        self.last_results = None
        self.last_columns = None
        self.tree_items = {}
        
        # Tab management
        self.query_tabs = {}
        self.active_tab_id = None
        self.tab_counter = 0
        
        # Drag and drop
        self.drag_data = None
        self.drag_source = None
        
        # Autocomplete
        self.tables_cache = []
        self.columns_cache = {}
        
        self.sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET',
            'DELETE', 'CREATE', 'TABLE', 'DROP', 'ALTER', 'ADD', 'INDEX', 'VIEW',
            'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AND', 'OR', 'NOT',
            'IN', 'BETWEEN', 'LIKE', 'IS', 'NULL', 'AS', 'ORDER', 'BY', 'ASC',
            'DESC', 'GROUP', 'HAVING', 'DISTINCT', 'LIMIT', 'OFFSET', 'UNION',
            'ALL', 'EXISTS', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'PRIMARY',
            'KEY', 'FOREIGN', 'REFERENCES', 'DEFAULT', 'CHECK', 'UNIQUE',
            'AUTOINCREMENT', 'INTEGER', 'TEXT', 'REAL', 'BLOB', 'VARCHAR',
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'BEGIN', 'COMMIT', 'ROLLBACK',
            'TRANSACTION', 'PRAGMA', 'VACUUM', 'TRIGGER', 'TEMPORARY', 'WITH',
            'CROSS', 'NATURAL', 'USING', 'EXCEPT', 'INTERSECT', 'CAST', 'COALESCE',
            'NULLIF', 'IFNULL', 'IIF', 'GLOB', 'REGEXP', 'MATCH', 'ESCAPE',
            'INDEXED', 'NOT', 'INDEXED', 'COLLATE', 'ASC', 'DESC', 'NULLS',
            'FIRST', 'LAST', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP'
        ]
        
        self.sql_functions = [
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'TOTAL', 'GROUP_CONCAT',
            'ABS', 'COALESCE', 'IFNULL', 'IIF', 'INSTR', 'LENGTH', 'LIKE',
            'LOWER', 'UPPER', 'LTRIM', 'RTRIM', 'TRIM', 'MAX', 'MIN',
            'NULLIF', 'PRINTF', 'QUOTE', 'RANDOM', 'REPLACE', 'ROUND',
            'SUBSTR', 'SUBSTRING', 'TYPEOF', 'UNICODE', 'UNLIKELY', 'LIKELY',
            'ZEROBLOB', 'DATE', 'TIME', 'DATETIME', 'JULIANDAY', 'STRFTIME',
            'HEX', 'UNHEX', 'RANDOMBLOB', 'CAST'
        ]
        
        self._setup_ui()
        self._create_bindings()
        self._create_new_tab()
        
    def _setup_ui(self):
        self._create_menu_bar()
        self._create_toolbar()
        
        self.main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, 
            bg=self.colors['border'], sashwidth=4, sashrelief=tk.FLAT)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self._create_object_explorer()
        self._create_query_panel()
        self._create_status_bar()
        
    def _create_menu_bar(self):
        self.menubar = tk.Menu(self.root, bg=self.colors['bg_medium'], fg=self.colors['text'],
            activebackground=self.colors['accent'], activeforeground='white', borderwidth=0)
        self.root.config(menu=self.menubar)
        
        menu_cfg = {'tearoff': 0, 'bg': self.colors['bg_medium'], 'fg': self.colors['text'],
            'activebackground': self.colors['accent'], 'activeforeground': 'white'}
        
        file_menu = tk.Menu(self.menubar, **menu_cfg)
        self.menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Database...", command=self._new_database, accelerator="Ctrl+Shift+N")
        file_menu.add_command(label="Open Database...", command=self._open_database, accelerator="Ctrl+O")
        file_menu.add_command(label="Close Database", command=self._close_database)
        file_menu.add_separator()
        file_menu.add_command(label="New Query Tab", command=self._create_new_tab, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Query...", command=self._open_query, accelerator="Ctrl+Shift+O")
        file_menu.add_command(label="Save Query", command=self._save_query, accelerator="Ctrl+S")
        file_menu.add_command(label="Save Query As...", command=self._save_query_as)
        file_menu.add_command(label="Close Tab", command=self._close_current_tab, accelerator="Ctrl+W")
        file_menu.add_separator()
        file_menu.add_command(label="Export Results to CSV...", command=self._export_results)
        file_menu.add_command(label="Export Results to JSON...", command=self._export_results_json)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_exit, accelerator="Alt+F4")
        
        edit_menu = tk.Menu(self.menubar, **menu_cfg)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self._cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self._copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self._paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self._select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Find...", command=self._find, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace...", command=self._replace, accelerator="Ctrl+H")
        edit_menu.add_command(label="Go to Line...", command=self._goto_line, accelerator="Ctrl+G")
        
        query_menu = tk.Menu(self.menubar, **menu_cfg)
        self.menubar.add_cascade(label="Query", menu=query_menu)
        query_menu.add_command(label="Execute", command=self._execute_query, accelerator="F5")
        query_menu.add_command(label="Execute Selected", command=self._execute_selected, accelerator="F8")
        query_menu.add_command(label="Execute Current Statement", command=self._execute_current_statement, accelerator="Ctrl+Enter")
        query_menu.add_separator()
        query_menu.add_command(label="Explain Query Plan", command=self._explain_query, accelerator="Ctrl+L")
        query_menu.add_separator()
        query_menu.add_command(label="Comment Selection", command=self._comment_selection, accelerator="Ctrl+K")
        query_menu.add_command(label="Uncomment Selection", command=self._uncomment_selection, accelerator="Ctrl+Shift+K")
        query_menu.add_separator()
        query_menu.add_command(label="Format Query", command=self._format_query, accelerator="Ctrl+Shift+F")
        query_menu.add_command(label="Uppercase Keywords", command=self._uppercase_keywords)
        
        tools_menu = tk.Menu(self.menubar, **menu_cfg)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Database Info", command=self._show_database_info)
        tools_menu.add_command(label="Table Designer...", command=self._table_designer)
        tools_menu.add_command(label="Data Generator...", command=self._data_generator)
        tools_menu.add_separator()
        tools_menu.add_command(label="Vacuum Database", command=self._vacuum_database)
        tools_menu.add_command(label="Integrity Check", command=self._integrity_check)
        tools_menu.add_command(label="Analyze Database", command=self._analyze_database)
        tools_menu.add_separator()
        tools_menu.add_command(label="Query History", command=self._show_query_history)
        tools_menu.add_command(label="Schema Diagram", command=self._show_schema_diagram)
        
        help_menu = tk.Menu(self.menubar, **menu_cfg)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="SQL Reference", command=self._show_sql_reference)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
        
    def _create_toolbar(self):
        self.toolbar = tk.Frame(self.root, bg=self.colors['bg_medium'], height=40)
        self.toolbar.pack(fill=tk.X)
        self.toolbar.pack_propagate(False)
        
        btn_style = {'bg': self.colors['bg_medium'], 'fg': self.colors['text'],
            'activebackground': self.colors['bg_lighter'], 'activeforeground': self.colors['text'],
            'relief': tk.FLAT, 'borderwidth': 0, 'padx': 10, 'pady': 6, 'font': ('Segoe UI', 9)}
        
        # Database buttons
        db_frame = tk.Frame(self.toolbar, bg=self.colors['bg_medium'])
        db_frame.pack(side=tk.LEFT, padx=4, pady=4)
        
        tk.Button(db_frame, text="New DB", command=self._new_database, **btn_style).pack(side=tk.LEFT, padx=1)
        tk.Button(db_frame, text="Open DB", command=self._open_database, **btn_style).pack(side=tk.LEFT, padx=1)
        
        self._add_separator()
        
        # Query buttons
        query_frame = tk.Frame(self.toolbar, bg=self.colors['bg_medium'])
        query_frame.pack(side=tk.LEFT, padx=4, pady=4)
        
        tk.Button(query_frame, text="New Tab", command=self._create_new_tab, **btn_style).pack(side=tk.LEFT, padx=1)
        tk.Button(query_frame, text="Save", command=self._save_query, **btn_style).pack(side=tk.LEFT, padx=1)
        
        self._add_separator()
        
        # Execute buttons
        exec_frame = tk.Frame(self.toolbar, bg=self.colors['bg_medium'])
        exec_frame.pack(side=tk.LEFT, padx=4, pady=4)
        
        self.btn_execute = tk.Button(exec_frame, text="Execute (F5)", command=self._execute_query,
            bg=self.colors['accent'], fg='white', activebackground=self.colors['accent_light'],
            activeforeground='white', relief=tk.FLAT, borderwidth=0, padx=14, pady=6,
            font=('Segoe UI', 9, 'bold'))
        self.btn_execute.pack(side=tk.LEFT, padx=2)
        
        tk.Button(exec_frame, text="Stop", command=self._stop_query,
            bg='#c62828', fg='white', activebackground='#e53935',
            relief=tk.FLAT, borderwidth=0, padx=10, pady=6,
            font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=2)
        
        self._add_separator()
        
        # Database info
        info_frame = tk.Frame(self.toolbar, bg=self.colors['bg_medium'])
        info_frame.pack(side=tk.LEFT, padx=4, pady=4)
        
        tk.Label(info_frame, text="Database:", bg=self.colors['bg_medium'], 
            fg=self.colors['text_dim'], font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(4, 2))
        
        self.db_var = tk.StringVar(value="Not connected")
        self.db_label = tk.Label(info_frame, textvariable=self.db_var, bg=self.colors['bg_light'],
            fg=self.colors['text'], font=('Segoe UI', 9), padx=12, pady=4, width=25, anchor='w')
        self.db_label.pack(side=tk.LEFT, padx=4)
        
        # Connection status indicator
        self.status_indicator = tk.Canvas(info_frame, width=12, height=12, 
            bg=self.colors['bg_medium'], highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=4)
        self._update_connection_indicator(False)
        
    def _add_separator(self):
        tk.Frame(self.toolbar, width=1, bg=self.colors['border']).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=8)
        
    def _update_connection_indicator(self, connected):
        self.status_indicator.delete('all')
        color = self.colors['success'] if connected else self.colors['error']
        self.status_indicator.create_oval(2, 2, 10, 10, fill=color, outline='')
        
    def _create_object_explorer(self):
        self.left_panel = tk.Frame(self.main_paned, bg=self.colors['bg_medium'], width=300)
        self.main_paned.add(self.left_panel, minsize=220)
        
        # Header
        header = tk.Frame(self.left_panel, bg=self.colors['bg_lighter'], height=32)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="Object Explorer", bg=self.colors['bg_lighter'],
            fg=self.colors['text'], font=('Segoe UI', 10, 'bold'), padx=12).pack(side=tk.LEFT, fill=tk.Y)
        
        btn_frame = tk.Frame(header, bg=self.colors['bg_lighter'])
        btn_frame.pack(side=tk.RIGHT, padx=4)
        
        tk.Button(btn_frame, text="Refresh", command=self._refresh_object_explorer,
            bg=self.colors['bg_lighter'], fg=self.colors['text_dim'],
            activebackground=self.colors['bg_light'], relief=tk.FLAT, borderwidth=0,
            font=('Segoe UI', 8), padx=6).pack(side=tk.LEFT, pady=4)
        
        tk.Button(btn_frame, text="Collapse", command=self._collapse_all,
            bg=self.colors['bg_lighter'], fg=self.colors['text_dim'],
            activebackground=self.colors['bg_light'], relief=tk.FLAT, borderwidth=0,
            font=('Segoe UI', 8), padx=6).pack(side=tk.LEFT, pady=4)
        
        # Search box
        search_frame = tk.Frame(self.left_panel, bg=self.colors['bg_medium'])
        search_frame.pack(fill=tk.X, padx=8, pady=6)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self._filter_tree)
        
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
            bg=self.colors['bg_dark'], fg=self.colors['text'],
            insertbackground=self.colors['text'], relief=tk.FLAT,
            font=('Segoe UI', 9))
        self.search_entry.pack(fill=tk.X, ipady=4)
        self.search_entry.insert(0, "Search objects...")
        self.search_entry.configure(fg=self.colors['text_dim'])
        
        self.search_entry.bind('<FocusIn>', self._on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_search_focus_out)
        
        # Tree container
        tree_container = tk.Frame(self.left_panel, bg=self.colors['tree_bg'])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        self.tree_canvas = tk.Canvas(tree_container, bg=self.colors['tree_bg'], 
            highlightthickness=0, borderwidth=0)
        self.tree_scrollbar_y = tk.Scrollbar(tree_container, orient=tk.VERTICAL,
            command=self.tree_canvas.yview, bg=self.colors['bg_lighter'],
            troughcolor=self.colors['bg_medium'], width=10)
        self.tree_scrollbar_x = tk.Scrollbar(tree_container, orient=tk.HORIZONTAL,
            command=self.tree_canvas.xview, bg=self.colors['bg_lighter'],
            troughcolor=self.colors['bg_medium'], width=10)
        
        self.tree_frame = tk.Frame(self.tree_canvas, bg=self.colors['tree_bg'])
        self.tree_canvas.configure(yscrollcommand=self.tree_scrollbar_y.set,
                                   xscrollcommand=self.tree_scrollbar_x.set)
        
        self.tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree_window = self.tree_canvas.create_window((0, 0), window=self.tree_frame, anchor='nw')
        
        self.tree_frame.bind('<Configure>', lambda e: self.tree_canvas.configure(scrollregion=self.tree_canvas.bbox('all')))
        self.tree_canvas.bind('<Configure>', lambda e: self.tree_canvas.itemconfig(self.tree_window, width=max(e.width, 250)))
        self.tree_canvas.bind('<MouseWheel>', lambda e: self.tree_canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))
        
        # Drop target setup
        self.tree_canvas.bind('<Button-1>', self._on_tree_click)
        
        self._show_no_database_message()
        
    def _on_search_focus_in(self, event):
        if self.search_entry.get() == "Search objects...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(fg=self.colors['text'])
            
    def _on_search_focus_out(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search objects...")
            self.search_entry.configure(fg=self.colors['text_dim'])
            
    def _filter_tree(self, *args):
        search_term = self.search_var.get().lower()
        if search_term == "search objects...":
            search_term = ""
        
        for node_id, node_data in self.tree_items.items():
            if 'frame' in node_data:
                if search_term and search_term not in node_data['name'].lower():
                    if node_data['type'] in ['table', 'view', 'column']:
                        node_data['frame'].pack_forget()
                else:
                    if not node_data['frame'].winfo_ismapped():
                        node_data['frame'].pack(fill=tk.X, anchor='w')
        
    def _show_no_database_message(self):
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        
        msg_frame = tk.Frame(self.tree_frame, bg=self.colors['tree_bg'])
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=40)
        
        # Icon
        icon_canvas = tk.Canvas(msg_frame, width=48, height=48, 
            bg=self.colors['tree_bg'], highlightthickness=0)
        icon_canvas.pack(pady=(0, 15))
        IconFactory.create_database_icon(icon_canvas, 8, 8, 32)
        
        tk.Label(msg_frame, text="No Database Connected",
            bg=self.colors['tree_bg'], fg=self.colors['text'],
            font=('Segoe UI', 11, 'bold')).pack()
        
        tk.Label(msg_frame, text="\nOpen or create a database\nto view objects here.\n\nYou can also drag tables\nand columns to the query editor.",
            bg=self.colors['tree_bg'], fg=self.colors['text_dim'],
            font=('Segoe UI', 9), justify=tk.CENTER).pack(pady=10)
        
        tk.Button(msg_frame, text="Open Database", command=self._open_database,
            bg=self.colors['accent'], fg='white', relief=tk.FLAT,
            font=('Segoe UI', 9), padx=20, pady=6).pack(pady=10)
        
    def _create_query_panel(self):
        self.right_panel = tk.Frame(self.main_paned, bg=self.colors['bg_dark'])
        self.main_paned.add(self.right_panel, minsize=600)
        
        self.query_paned = tk.PanedWindow(self.right_panel, orient=tk.VERTICAL,
            bg=self.colors['border'], sashwidth=4, sashrelief=tk.FLAT)
        self.query_paned.pack(fill=tk.BOTH, expand=True)
        
        self._create_query_editor()
        self._create_results_panel()
        
    def _create_query_editor(self):
        self.editor_frame = tk.Frame(self.query_paned, bg=self.colors['bg_dark'])
        self.query_paned.add(self.editor_frame, minsize=200)
        
        # Tab bar
        self.tab_bar = tk.Frame(self.editor_frame, bg=self.colors['bg_medium'], height=32)
        self.tab_bar.pack(fill=tk.X)
        self.tab_bar.pack_propagate(False)
        
        self.tabs_container = tk.Frame(self.tab_bar, bg=self.colors['bg_medium'])
        self.tabs_container.pack(side=tk.LEFT, fill=tk.Y)
        
        # New tab button
        self.new_tab_btn = tk.Label(self.tab_bar, text=" + ", 
            bg=self.colors['bg_medium'], fg=self.colors['text_dim'],
            font=('Segoe UI', 10), cursor='hand2', padx=8)
        self.new_tab_btn.pack(side=tk.LEFT, pady=4)
        self.new_tab_btn.bind('<Button-1>', lambda e: self._create_new_tab())
        self.new_tab_btn.bind('<Enter>', lambda e: self.new_tab_btn.configure(fg=self.colors['text']))
        self.new_tab_btn.bind('<Leave>', lambda e: self.new_tab_btn.configure(fg=self.colors['text_dim']))
        
        # Editor area
        self.editor_container = tk.Frame(self.editor_frame, bg=self.colors['bg_dark'])
        self.editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(self.editor_container, width=5, bg=self.colors['bg_medium'],
            fg=self.colors['text_dim'], font=('Consolas', 11), borderwidth=0, highlightthickness=0,
            padx=8, pady=8, state=tk.DISABLED, cursor='arrow', takefocus=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Query text
        text_frame = tk.Frame(self.editor_container, bg=self.colors['bg_dark'])
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.query_text = tk.Text(text_frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
            insertbackground=self.colors['text'], selectbackground=self.colors['selection'],
            selectforeground=self.colors['text'], font=('Consolas', 11), borderwidth=0,
            highlightthickness=0, padx=4, pady=8, undo=True, wrap=tk.NONE, tabs=('4c',))
        
        query_v_scroll = tk.Scrollbar(text_frame, orient=tk.VERTICAL, 
            command=self._sync_scroll, bg=self.colors['bg_lighter'],
            troughcolor=self.colors['bg_medium'], width=10)
        query_h_scroll = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL,
            command=self.query_text.xview, bg=self.colors['bg_lighter'],
            troughcolor=self.colors['bg_medium'], width=10)
        
        self.query_text.configure(
            yscrollcommand=lambda *args: self._on_scroll(*args, scrollbar=query_v_scroll),
            xscrollcommand=query_h_scroll.set)
        
        query_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        query_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.query_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.query_text.tag_configure('keyword', foreground=self.colors['keyword'])
        self.query_text.tag_configure('function', foreground=self.colors['function'])
        self.query_text.tag_configure('string', foreground=self.colors['string'])
        self.query_text.tag_configure('comment', foreground=self.colors['comment'])
        self.query_text.tag_configure('number', foreground=self.colors['number'])
        self.query_text.tag_configure('table', foreground=self.colors['success'])
        self.query_text.tag_configure('drop_target', background=self.colors['drop_target'])
        
        # Bindings
        self.query_text.bind('<KeyRelease>', self._on_key_release)
        self.query_text.bind('<Return>', self._on_return)
        self.query_text.bind('<Tab>', self._on_tab)
        self.query_text.bind('<Control-space>', self._show_autocomplete)
        self.query_text.bind('<<Modified>>', self._on_text_modified)
        
        # Drop target
        self.query_text.bind('<Enter>', self._on_editor_enter)
        self.query_text.bind('<Leave>', self._on_editor_leave)
        self.query_text.bind('<ButtonRelease-1>', self._on_editor_drop)
        
        self.query_text.insert('1.0', "-- Write your SQL query here\n-- Press F5 to execute\n-- Drag tables/columns from Object Explorer\n\nSELECT * FROM ")
        self._apply_syntax_highlighting()
        self._update_line_numbers()
        
    def _create_results_panel(self):
        results_frame = tk.Frame(self.query_paned, bg=self.colors['bg_dark'])
        self.query_paned.add(results_frame, minsize=150)
        
        # Tab bar
        results_tab_bar = tk.Frame(results_frame, bg=self.colors['bg_medium'], height=32)
        results_tab_bar.pack(fill=tk.X)
        results_tab_bar.pack_propagate(False)
        
        self.results_tab = tk.Label(results_tab_bar, text="  Results  ", bg=self.colors['bg_dark'],
            fg=self.colors['text'], font=('Segoe UI', 9), padx=8, pady=6, cursor='hand2')
        self.results_tab.pack(side=tk.LEFT, pady=(2, 0))
        
        self.messages_tab = tk.Label(results_tab_bar, text="  Messages  ", bg=self.colors['bg_medium'],
            fg=self.colors['text_dim'], font=('Segoe UI', 9), padx=8, pady=6, cursor='hand2')
        self.messages_tab.pack(side=tk.LEFT, pady=(2, 0))
        
        self.plan_tab = tk.Label(results_tab_bar, text="  Execution Plan  ", bg=self.colors['bg_medium'],
            fg=self.colors['text_dim'], font=('Segoe UI', 9), padx=8, pady=6, cursor='hand2')
        self.plan_tab.pack(side=tk.LEFT, pady=(2, 0))
        
        self.messages_tab.bind('<Button-1>', lambda e: self._switch_to_messages())
        self.results_tab.bind('<Button-1>', lambda e: self._switch_to_results())
        self.plan_tab.bind('<Button-1>', lambda e: self._switch_to_plan())
        
        # Results count label
        self.results_info = tk.Label(results_tab_bar, text="", bg=self.colors['bg_medium'],
            fg=self.colors['text_dim'], font=('Segoe UI', 9), padx=10)
        self.results_info.pack(side=tk.RIGHT)
        
        # Container
        self.results_container = tk.Frame(results_frame, bg=self.colors['bg_dark'])
        self.results_container.pack(fill=tk.BOTH, expand=True)
        
        # Results grid
        self.results_grid_frame = tk.Frame(self.results_container, bg=self.colors['bg_dark'])
        self.results_grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Messages
        self.messages_frame = tk.Frame(self.results_container, bg=self.colors['bg_dark'])
        
        self.messages_text = tk.Text(self.messages_frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
            font=('Consolas', 10), borderwidth=0, highlightthickness=0, padx=10, pady=10,
            state=tk.DISABLED, wrap=tk.WORD)
        
        msg_scrollbar = tk.Scrollbar(self.messages_frame, orient=tk.VERTICAL,
            command=self.messages_text.yview, bg=self.colors['bg_lighter'],
            troughcolor=self.colors['bg_medium'], width=10)
        
        self.messages_text.configure(yscrollcommand=msg_scrollbar.set)
        msg_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.messages_text.pack(fill=tk.BOTH, expand=True)
        
        self.messages_text.tag_configure('error', foreground=self.colors['error'])
        self.messages_text.tag_configure('success', foreground=self.colors['success'])
        self.messages_text.tag_configure('info', foreground=self.colors['text_dim'])
        self.messages_text.tag_configure('warning', foreground=self.colors['warning'])
        
        # Execution plan
        self.plan_frame = tk.Frame(self.results_container, bg=self.colors['bg_dark'])
        
        self.plan_text = tk.Text(self.plan_frame, bg=self.colors['bg_dark'], fg=self.colors['text'],
            font=('Consolas', 10), borderwidth=0, highlightthickness=0, padx=10, pady=10,
            state=tk.DISABLED, wrap=tk.WORD)
        
        plan_scrollbar = tk.Scrollbar(self.plan_frame, orient=tk.VERTICAL,
            command=self.plan_text.yview, bg=self.colors['bg_lighter'],
            troughcolor=self.colors['bg_medium'], width=10)
        
        self.plan_text.configure(yscrollcommand=plan_scrollbar.set)
        plan_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.plan_text.pack(fill=tk.BOTH, expand=True)
        
        self._create_results_grid()
        
    def _create_results_grid(self):
        for widget in self.results_grid_frame.winfo_children():
            widget.destroy()
        
        grid_container = tk.Frame(self.results_grid_frame, bg=self.colors['bg_dark'])
        grid_container.pack(fill=tk.BOTH, expand=True)
        
        self.grid_canvas = tk.Canvas(grid_container, bg=self.colors['bg_dark'], 
            highlightthickness=0, borderwidth=0)
        
        self.grid_v_scroll = tk.Scrollbar(grid_container, orient=tk.VERTICAL,
            command=self.grid_canvas.yview, bg=self.colors['bg_lighter'],
            troughcolor=self.colors['bg_medium'], width=10)
        self.grid_h_scroll = tk.Scrollbar(grid_container, orient=tk.HORIZONTAL,
            command=self.grid_canvas.xview, bg=self.colors['bg_lighter'],
            troughcolor=self.colors['bg_medium'], width=10)
        
        self.grid_canvas.configure(yscrollcommand=self.grid_v_scroll.set,
            xscrollcommand=self.grid_h_scroll.set)
        
        self.grid_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.grid_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.grid_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.grid_inner_frame = tk.Frame(self.grid_canvas, bg=self.colors['bg_dark'])
        self.grid_canvas.create_window((0, 0), window=self.grid_inner_frame, anchor='nw')
        
        self.grid_inner_frame.bind('<Configure>', 
            lambda e: self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox('all')))
        self.grid_canvas.bind('<MouseWheel>', 
            lambda e: self.grid_canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))
        
        tk.Label(self.grid_inner_frame, text="Execute a query to see results here.",
            bg=self.colors['bg_dark'], fg=self.colors['text_dim'], font=('Segoe UI', 10),
            padx=20, pady=30).pack(anchor='w')
        
    def _create_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg=self.colors['accent'], height=26)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        self.status_text = tk.StringVar(value="Ready")
        tk.Label(self.status_bar, textvariable=self.status_text, bg=self.colors['accent'],
            fg='white', font=('Segoe UI', 9), padx=12).pack(side=tk.LEFT, fill=tk.Y)
        
        # Right side info
        right_frame = tk.Frame(self.status_bar, bg=self.colors['accent'])
        right_frame.pack(side=tk.RIGHT)
        
        self.position_var = tk.StringVar(value="Ln 1, Col 1")
        tk.Label(right_frame, textvariable=self.position_var, bg=self.colors['accent'],
            fg='white', font=('Segoe UI', 9), padx=12).pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Frame(right_frame, width=1, bg='#0066aa').pack(side=tk.RIGHT, fill=tk.Y, pady=4)
        
        self.exec_time_var = tk.StringVar(value="")
        tk.Label(right_frame, textvariable=self.exec_time_var, bg=self.colors['accent'],
            fg='white', font=('Segoe UI', 9), padx=12).pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Frame(right_frame, width=1, bg='#0066aa').pack(side=tk.RIGHT, fill=tk.Y, pady=4)
        
        self.row_count_var = tk.StringVar(value="")
        tk.Label(right_frame, textvariable=self.row_count_var, bg=self.colors['accent'],
            fg='white', font=('Segoe UI', 9), padx=12).pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_bindings(self):
        self.root.bind('<F5>', lambda e: self._execute_query())
        self.root.bind('<F8>', lambda e: self._execute_selected())
        self.root.bind('<Control-Return>', lambda e: self._execute_current_statement())
        self.root.bind('<Control-N>', lambda e: self._create_new_tab())
        self.root.bind('<Control-O>', lambda e: self._open_database())
        self.root.bind('<Control-S>', lambda e: self._save_query())
        self.root.bind('<Control-W>', lambda e: self._close_current_tab())
        self.root.bind('<Control-F>', lambda e: self._find())
        self.root.bind('<Control-H>', lambda e: self._replace())
        self.root.bind('<Control-G>', lambda e: self._goto_line())
        self.root.bind('<Control-K>', lambda e: self._comment_selection())
        self.root.bind('<Control-K>', lambda e: self._uncomment_selection())
        self.root.bind('<Control-L>', lambda e: self._explain_query())
        self.root.bind('<Control-Shift-F>', lambda e: self._format_query())
        
        # Update cursor position
        self.query_text.bind('<KeyRelease>', self._update_position)
        self.query_text.bind('<ButtonRelease-1>', self._update_position)
        
    def _update_position(self, event=None):
        pos = self.query_text.index(tk.INSERT)
        line, col = pos.split('.')
        self.position_var.set(f"Ln {line}, Col {int(col)+1}")
        self._on_key_release(event)

    # ============== Tab Management ==============
    
    def _create_new_tab(self, name=None, content=""):
        self.tab_counter += 1
        tab_id = f"tab_{self.tab_counter}"
        
        if name is None:
            name = f"Query {self.tab_counter}"
        
        tab = QueryTab(self.tabs_container, tab_id, name, self.colors,
                       self._close_tab, self._select_tab)
        tab.pack(side=tk.LEFT)
        tab.content = content if content else "-- New Query\n\nSELECT "
        
        self.query_tabs[tab_id] = tab
        self._select_tab(tab_id)
        
        return tab_id
    
    def _select_tab(self, tab_id):
        if self.active_tab_id and self.active_tab_id in self.query_tabs:
            # Save current content
            self.query_tabs[self.active_tab_id].content = self.query_text.get('1.0', tk.END)
            self.query_tabs[self.active_tab_id].set_active(False)
        
        self.active_tab_id = tab_id
        tab = self.query_tabs[tab_id]
        tab.set_active(True)
        
        # Load content
        self.query_text.delete('1.0', tk.END)
        self.query_text.insert('1.0', tab.content)
        self._apply_syntax_highlighting()
        self._update_line_numbers()
        
    def _close_tab(self, tab_id):
        if len(self.query_tabs) <= 1:
            return
        
        tab = self.query_tabs[tab_id]
        
        if tab.modified:
            result = messagebox.askyesnocancel("Save Changes", 
                f"Do you want to save changes to {tab.name}?")
            if result is None:
                return
            if result:
                self._save_query()
        
        tab.destroy()
        del self.query_tabs[tab_id]
        
        if self.active_tab_id == tab_id:
            remaining = list(self.query_tabs.keys())
            if remaining:
                self._select_tab(remaining[-1])
                
    def _close_current_tab(self):
        if self.active_tab_id:
            self._close_tab(self.active_tab_id)
        return 'break'
        
    def _on_text_modified(self, event=None):
        if self.active_tab_id and self.active_tab_id in self.query_tabs:
            self.query_tabs[self.active_tab_id].set_modified(True)
        self.query_text.edit_modified(False)

    # ============== Drag & Drop ==============
    
    def _start_drag(self, data):
        self.drag_data = data
        self.root.configure(cursor='hand2')
        
    def _end_drag(self, event):
        self.root.configure(cursor='')
        self.drag_data = None
        
    def _on_editor_enter(self, event):
        if self.drag_data:
            self.query_text.tag_add('drop_target', '1.0', tk.END)
            
    def _on_editor_leave(self, event):
        self.query_text.tag_remove('drop_target', '1.0', tk.END)
        
    def _on_editor_drop(self, event):
        self.query_text.tag_remove('drop_target', '1.0', tk.END)
        
        if self.drag_data:
            data = self.drag_data
            self.drag_data = None
            self.root.configure(cursor='')
            
            # Insert at click position
            insert_text = ""
            if data['type'] == 'table':
                insert_text = data['name']
            elif data['type'] == 'column':
                # Remove type info in parentheses
                col_name = data['name']
                if '(' in col_name:
                    col_name = col_name.split('(')[0].strip()
                insert_text = col_name
            
            if insert_text:
                # Insert at mouse click position
                self.query_text.mark_set(tk.INSERT, f"@{event.x},{event.y}")
                self.query_text.insert(tk.INSERT, insert_text)
                self._apply_syntax_highlighting()
                self.query_text.focus_set()
            
            return 'break'
                
    def _on_tree_click(self, event):
        pass

    # ============== Object Explorer ==============
    
    def _refresh_object_explorer(self):
        if not self.connection:
            self._show_no_database_message()
            return
        
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        self.tree_items = {}
        
        # Update caches
        self._update_schema_cache()
        
        try:
            cursor = self.connection.cursor()
            db_name = os.path.basename(self.current_db_path)
            
            # Database node
            db_frame = self._create_tree_node(self.tree_frame, db_name, 0, 'database', True, is_root=True)
            
            # Tables folder
            tables_frame = self._create_tree_node(db_frame, "Tables", 1, 'folder', True)
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                table_frame = self._create_tree_node(tables_frame, table_name, 2, 'table')
                
                # Columns
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns = cursor.fetchall()
                
                for col in columns:
                    col_name = col[1]
                    col_type = col[2] or 'BLOB'
                    is_pk = col[5] == 1
                    not_null = col[3] == 1
                    
                    col_text = f"{col_name} ({col_type})"
                    node_type = 'pk' if is_pk else 'column'
                    
                    self._create_tree_node(table_frame, col_text, 3, node_type, 
                                           extra_info={'table': table_name, 'column': col_name})
                
                # Indexes
                cursor.execute(f"PRAGMA index_list('{table_name}')")
                indexes = cursor.fetchall()
                
                if indexes:
                    idx_folder = self._create_tree_node(table_frame, "Indexes", 3, 'folder')
                    for idx in indexes:
                        self._create_tree_node(idx_folder, idx[1], 4, 'index')
            
            # Views folder
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
            views = cursor.fetchall()
            
            if views:
                views_frame = self._create_tree_node(db_frame, "Views", 1, 'folder')
                for (view_name,) in views:
                    self._create_tree_node(views_frame, view_name, 2, 'view')
            
            # Triggers folder
            cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name")
            triggers = cursor.fetchall()
            
            if triggers:
                triggers_frame = self._create_tree_node(db_frame, "Triggers", 1, 'folder')
                for (trigger_name,) in triggers:
                    self._create_tree_node(triggers_frame, trigger_name, 2, 'trigger')
                    
        except Exception as e:
            self._add_message(f"Error: {e}", 'error')
            
    def _update_schema_cache(self):
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            self.tables_cache = [row[0] for row in cursor.fetchall()]
            
            self.columns_cache = {}
            for table in self.tables_cache:
                cursor.execute(f"PRAGMA table_info('{table}')")
                self.columns_cache[table] = [col[1] for col in cursor.fetchall()]
        except:
            pass
            
    def _create_tree_node(self, parent, text, level, node_type, expanded=False, is_root=False, extra_info=None):
        indent = level * 16
        
        node_frame = tk.Frame(parent, bg=self.colors['tree_bg'])
        node_frame.pack(fill=tk.X, anchor='w')
        
        label_row = tk.Frame(node_frame, bg=self.colors['tree_bg'])
        label_row.pack(fill=tk.X)
        
        # Indent
        if indent > 0:
            tk.Frame(label_row, width=indent, bg=self.colors['tree_bg']).pack(side=tk.LEFT)
        
        # Expand/collapse indicator for folders
        if node_type in ['folder', 'database', 'table']:
            expand_text = "-" if expanded else "+"
            expand_label = tk.Label(label_row, text=expand_text, bg=self.colors['tree_bg'],
                fg=self.colors['text_dim'], font=('Consolas', 9), width=2, cursor='hand2')
            expand_label.pack(side=tk.LEFT)
        else:
            tk.Frame(label_row, width=16, bg=self.colors['tree_bg']).pack(side=tk.LEFT)
        
        # Icon canvas
        icon_canvas = tk.Canvas(label_row, width=20, height=18, 
            bg=self.colors['tree_bg'], highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(0, 4))
        
        # Draw icon
        if node_type == 'database':
            IconFactory.create_database_icon(icon_canvas, 2, 1, 16)
        elif node_type == 'folder':
            IconFactory.create_folder_icon(icon_canvas, 2, 1, 16, expanded)
        elif node_type == 'table':
            IconFactory.create_table_icon(icon_canvas, 2, 1, 16)
        elif node_type == 'view':
            IconFactory.create_view_icon(icon_canvas, 2, 1, 16)
        elif node_type == 'column':
            IconFactory.create_column_icon(icon_canvas, 2, 1, 16)
        elif node_type == 'pk':
            IconFactory.create_pk_icon(icon_canvas, 2, 1, 16)
        elif node_type == 'index':
            IconFactory.create_index_icon(icon_canvas, 2, 1, 16)
        
        # Text label
        text_label = tk.Label(label_row, text=text, bg=self.colors['tree_bg'], fg=self.colors['text'],
            font=('Segoe UI', 9), anchor='w', cursor='hand2')
        text_label.pack(side=tk.LEFT, fill=tk.X)
        
        # Children container
        children_frame = tk.Frame(node_frame, bg=self.colors['tree_bg'])
        if expanded:
            children_frame.pack(fill=tk.X)
        
        # Store reference
        node_id = f"{node_type}_{text}_{id(node_frame)}"
        self.tree_items[node_id] = {
            'frame': node_frame,
            'children': children_frame,
            'type': node_type,
            'name': text,
            'expanded': expanded,
            'expand_label': expand_label if node_type in ['folder', 'database', 'table'] else None,
            'icon_canvas': icon_canvas,
            'extra_info': extra_info
        }
        
        # Toggle function
        def toggle(e=None, nid=node_id):
            node = self.tree_items[nid]
            if node['type'] not in ['folder', 'database', 'table']:
                return
            
            if node['expanded']:
                node['children'].pack_forget()
                if node['expand_label']:
                    node['expand_label'].configure(text='+')
                #node['icon_canvas'].delete('all')
                #if node['type'] == 'folder':
                #    IconFactory.create_folder_icon(node['icon_canvas'], 2, 1, 16, False)
                node['expanded'] = False
            else:
                node['children'].pack(fill=tk.X)
                if node['expand_label']:
                    node['expand_label'].configure(text='-')
                #node['icon_canvas'].delete('all')
                #if node['type'] == 'folder':
                #    IconFactory.create_folder_icon(node['icon_canvas'], 2, 1, 16, True)
                node['expanded'] = True
        
        # Double-click handler
        def dbl_click(e=None, name=text, ntype=node_type):
            if ntype == 'table':
                self.query_text.delete('1.0', tk.END)
                self.query_text.insert('1.0', f"SELECT * FROM {name}\nLIMIT 100;")
                self._apply_syntax_highlighting()
                self._update_line_numbers()
                self._execute_query()
            elif ntype == 'view':
                self.query_text.delete('1.0', tk.END)
                self.query_text.insert('1.0', f"SELECT * FROM {name};")
                self._apply_syntax_highlighting()
                self._update_line_numbers()
                self._execute_query()
        
        # Right-click menu
        def right_click(e, name=text, ntype=node_type, info=extra_info):
            menu = tk.Menu(self.root, tearoff=0, bg=self.colors['bg_medium'], 
                fg=self.colors['text'], activebackground=self.colors['accent'])
            
            if ntype == 'table':
                menu.add_command(label="Select Top 100", command=lambda: self._quick_select(name, 100))
                menu.add_command(label="Select Top 1000", command=lambda: self._quick_select(name, 1000))
                menu.add_command(label="Select All", command=lambda: self._quick_select(name, None))
                menu.add_separator()
                menu.add_command(label="Insert SELECT Template", command=lambda: self._insert_select_template(name))
                menu.add_command(label="Insert INSERT Template", command=lambda: self._insert_insert_template(name))
                menu.add_command(label="Insert UPDATE Template", command=lambda: self._insert_update_template(name))
                menu.add_separator()
                menu.add_command(label="Script as CREATE", command=lambda: self._script_create(name))
                menu.add_command(label="Script as DROP", command=lambda: self._script_drop(name))
                menu.add_separator()
                menu.add_command(label="Rename Table", command=lambda: self._rename_table(name))
                menu.add_command(label="Drop Table", command=lambda: self._drop_table(name))
            elif ntype in ['column', 'pk'] and info:
                col_name = info.get('column', name.split()[0])
                menu.add_command(label=f"Insert Column Name", 
                    command=lambda: self.query_text.insert(tk.INSERT, col_name))
                menu.add_command(label=f"Insert {info['table']}.{col_name}", 
                    command=lambda: self.query_text.insert(tk.INSERT, f"{info['table']}.{col_name}"))
            elif ntype == 'view':
                menu.add_command(label="Select All", command=lambda: self._quick_select(name, None))
                menu.add_separator()
                menu.add_command(label="Script as CREATE", command=lambda: self._script_view_create(name))
                menu.add_command(label="Drop View", command=lambda: self._drop_view(name))
            elif ntype == 'database':
                menu.add_command(label="Refresh", command=self._refresh_object_explorer)
                menu.add_command(label="Database Info", command=self._show_database_info)
            
            menu.tk_popup(e.x_root, e.y_root)
        
        # Drag start for tables and columns
        def start_drag(e, name=text, ntype=node_type, info=extra_info):
            if ntype == 'table':
                self._start_drag({'type': 'table', 'name': name})
            elif ntype in ['column', 'pk'] and info:
                col_name = info.get('column', name.split()[0])
                self._start_drag({'type': 'column', 'name': col_name})
            return 'break'  # Previne propagarea evenimentului
        
        def end_drag(e):
            self._end_drag(e)
        
        # Bind events
        if node_type in ['folder', 'database', 'table']:
            if 'expand_label' in locals():
                expand_label.bind('<Button-1>', toggle)
        
        if node_type in ['table', 'column', 'pk']:
            text_label.bind('<Button-1>', lambda e, n=text, t=node_type, i=extra_info: start_drag(e, n, t, i))
            text_label.bind('<ButtonRelease-1>', lambda e: end_drag(e))
            icon_canvas.bind('<Button-1>', lambda e, n=text, t=node_type, i=extra_info: start_drag(e, n, t, i))
            icon_canvas.bind('<ButtonRelease-1>', lambda e: end_drag(e))
        # Pentru folder-uri și database - enable toggle
        elif node_type in ['folder', 'database']:
            text_label.bind('<Button-1>', lambda e: toggle())
            icon_canvas.bind('<Button-1>', lambda e: toggle())
        # Pentru tabele - atât toggle cât și drag
        elif node_type == 'table':
            # Click pe expand button = toggle
            if 'expand_label' in locals() and expand_label:
                expand_label.bind('<Button-1>', lambda e: toggle())
            # Click pe icon sau text = start drag (fără toggle automat)
            text_label.bind('<Button-1>', lambda e, n=text, t=node_type, i=extra_info: start_drag(e, n, t, i))
            icon_canvas.bind('<Button-1>', lambda e, n=text, t=node_type, i=extra_info: start_drag(e, n, t, i))
            text_label.bind('<ButtonRelease-1>', lambda e: end_drag(e))
            icon_canvas.bind('<ButtonRelease-1>', lambda e: end_drag(e))

        # Common bindings
        text_label.bind('<Double-Button-1>', dbl_click)
        text_label.bind('<Button-3>', lambda e: right_click(e, text, node_type, extra_info))
        icon_canvas.bind('<Double-Button-1>', dbl_click)
        
        # Hover effect
        def on_enter(e):
            label_row.configure(bg=self.colors['bg_hover'])
            icon_canvas.configure(bg=self.colors['bg_hover'])
            text_label.configure(bg=self.colors['bg_hover'])
            if node_type in ['folder', 'database', 'table'] and 'expand_label' in locals():
                expand_label.configure(bg=self.colors['bg_hover'])
                
        def on_leave(e):
            label_row.configure(bg=self.colors['tree_bg'])
            icon_canvas.configure(bg=self.colors['tree_bg'])
            text_label.configure(bg=self.colors['tree_bg'])
            if node_type in ['folder', 'database', 'table'] and 'expand_label' in locals():
                expand_label.configure(bg=self.colors['tree_bg'])
        
        label_row.bind('<Enter>', on_enter)
        label_row.bind('<Leave>', on_leave)
        
        return children_frame
    
    def _collapse_all(self):
        for node_id, node_data in self.tree_items.items():
            if node_data['type'] in ['folder', 'table'] and node_data['expanded']:
                node_data['children'].pack_forget()
                if node_data['expand_label']:
                    node_data['expand_label'].configure(text='+')
                if node_data['type'] == 'folder':
                    node_data['icon_canvas'].delete('all')
                    IconFactory.create_folder_icon(node_data['icon_canvas'], 2, 1, 16, False)
                node_data['expanded'] = False

    # ============== Query Templates ==============
    
    def _insert_select_template(self, table):
        if table in self.columns_cache:
            cols = ', '.join(self.columns_cache[table])
            template = f"SELECT {cols}\nFROM {table}\nWHERE 1=1\nORDER BY 1;"
        else:
            template = f"SELECT *\nFROM {table}\nWHERE 1=1;"
        
        self.query_text.insert(tk.INSERT, template)
        self._apply_syntax_highlighting()
        self._update_line_numbers()
        
    def _insert_insert_template(self, table):
        if table in self.columns_cache:
            cols = ', '.join(self.columns_cache[table])
            placeholders = ', '.join(['?' for _ in self.columns_cache[table]])
            template = f"INSERT INTO {table} ({cols})\nVALUES ({placeholders});"
        else:
            template = f"INSERT INTO {table} (column1, column2)\nVALUES (?, ?);"
        
        self.query_text.insert(tk.INSERT, template)
        self._apply_syntax_highlighting()
        self._update_line_numbers()
        
    def _insert_update_template(self, table):
        if table in self.columns_cache and self.columns_cache[table]:
            first_col = self.columns_cache[table][0]
            set_clause = ', '.join([f"{c} = ?" for c in self.columns_cache[table]])
            template = f"UPDATE {table}\nSET {set_clause}\nWHERE {first_col} = ?;"
        else:
            template = f"UPDATE {table}\nSET column1 = ?\nWHERE id = ?;"
        
        self.query_text.insert(tk.INSERT, template)
        self._apply_syntax_highlighting()
        self._update_line_numbers()

    # ============== Database Operations ==============
    
    def _new_database(self):
        fp = filedialog.asksaveasfilename(title="Create New Database", defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All files", "*.*")])
        if fp:
            try:
                conn = sqlite3.connect(fp)
                conn.close()
                self._connect_to_database(fp)
                self._add_message(f"Database created: {fp}", 'success')
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def _open_database(self):
        fp = filedialog.askopenfilename(title="Open Database",
            filetypes=[("SQLite Database", "*.db;*.sqlite;*.sqlite3;*.db3"), ("All files", "*.*")])
        if fp:
            self._connect_to_database(fp)
        return 'break'
            
    def _connect_to_database(self, fp):
        try:
            if self.connection:
                self.connection.close()
            self.connection = sqlite3.connect(fp)
            self.current_db_path = fp
            self.db_var.set(os.path.basename(fp))
            self.root.title(f"SQL Manager Studio Pro - {os.path.basename(fp)}")
            self._update_connection_indicator(True)
            self._refresh_object_explorer()
            self._add_message(f"Connected to: {fp}", 'success')
            self.status_text.set(f"Connected to {os.path.basename(fp)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._update_connection_indicator(False)
            
    def _close_database(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.current_db_path = None
            self.db_var.set("Not connected")
            self.root.title("SQL Manager Studio Pro")
            self._update_connection_indicator(False)
            self._show_no_database_message()
            self._add_message("Database closed.", 'info')
            self.status_text.set("Ready")
            self.tables_cache = []
            self.columns_cache = {}

    # ============== Query Execution ==============
    
    def _execute_query(self):
        if not self.connection:
            messagebox.showwarning("No Database", "Connect to a database first.")
            return 'break'
        query = self.query_text.get('1.0', tk.END).strip()
        if query:
            self._execute_sql(query)
        return 'break'
        
    def _execute_selected(self):
        if not self.connection:
            messagebox.showwarning("No Database", "Connect to a database first.")
            return 'break'
        try:
            query = self.query_text.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if query:
                self._execute_sql(query)
        except tk.TclError:
            self._execute_query()
        return 'break'
        
    def _execute_current_statement(self):
        if not self.connection:
            messagebox.showwarning("No Database", "Connect to a database first.")
            return 'break'
        
        # Find the current statement (between semicolons)
        content = self.query_text.get('1.0', tk.END)
        cursor_pos = self.query_text.index(tk.INSERT)
        cursor_idx = len(self.query_text.get('1.0', cursor_pos))
        
        # Find statement boundaries
        start = content.rfind(';', 0, cursor_idx)
        start = start + 1 if start >= 0 else 0
        end = content.find(';', cursor_idx)
        end = end + 1 if end >= 0 else len(content)
        
        statement = content[start:end].strip()
        if statement:
            self._execute_sql(statement)
        return 'break'
            
    def _execute_sql(self, query):
        start = datetime.now()
        
        if query and (not self.query_history or self.query_history[-1] != query):
            self.query_history.append(query)
        
        self.status_text.set("Executing...")
        self.btn_execute.configure(state=tk.DISABLED)
        self.root.update()
        
        try:
            cursor = self.connection.cursor()
            
            # Split by semicolons but preserve strings
            statements = self._split_statements(query)
            
            last_result = None
            last_columns = None
            total_affected = 0
            
            for stmt in statements:
                stmt = stmt.strip()
                if not stmt:
                    continue
                
                cursor.execute(stmt)
                
                if cursor.description:
                    last_columns = [d[0] for d in cursor.description]
                    last_result = cursor.fetchall()
                else:
                    self.connection.commit()
                    total_affected += cursor.rowcount
                    self._add_message(f"({cursor.rowcount} row(s) affected)", 'info')
            
            elapsed = (datetime.now() - start).total_seconds()
            
            if last_result is not None and last_columns:
                self.last_results = last_result
                self.last_columns = last_columns
                self._display_results(last_columns, last_result)
                self.row_count_var.set(f"{len(last_result)} rows")
                self.results_info.configure(text=f"{len(last_result)} rows returned")
            else:
                self._create_results_grid()
                self.row_count_var.set(f"{total_affected} affected" if total_affected else "")
                self.results_info.configure(text="")
            
            self.exec_time_var.set(f"{elapsed:.3f}s")
            self.status_text.set("Query executed successfully")
            self._add_message(f"Completed in {elapsed:.3f}s", 'success')
            
            if any(k in query.upper() for k in ['CREATE', 'DROP', 'ALTER']):
                self._refresh_object_explorer()
                
        except Exception as e:
            self.status_text.set("Query failed")
            self.exec_time_var.set("")
            self.row_count_var.set("")
            self._add_message(f"Error: {e}", 'error')
            self._switch_to_messages()
        finally:
            self.btn_execute.configure(state=tk.NORMAL)
            
    def _split_statements(self, query):
        """Split SQL into statements, respecting string literals"""
        statements = []
        current = ""
        in_string = False
        string_char = None
        
        i = 0
        while i < len(query):
            char = query[i]
            
            if char in ("'", '"') and (i == 0 or query[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            
            if char == ';' and not in_string:
                if current.strip():
                    statements.append(current.strip())
                current = ""
            else:
                current += char
            
            i += 1
        
        if current.strip():
            statements.append(current.strip())
        
        return statements
        
    def _stop_query(self):
        self.status_text.set("Stop requested...")
        
    def _explain_query(self):
        if not self.connection:
            return 'break'
        
        query = self.query_text.get('1.0', tk.END).strip()
        if not query:
            return 'break'
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            plan = cursor.fetchall()
            
            self.plan_text.config(state=tk.NORMAL)
            self.plan_text.delete('1.0', tk.END)
            self.plan_text.insert('1.0', "QUERY PLAN\n" + "="*50 + "\n\n")
            
            for row in plan:
                indent = "  " * row[1] if len(row) > 1 else ""
                detail = row[-1] if row else ""
                self.plan_text.insert(tk.END, f"{indent}{detail}\n")
            
            self.plan_text.config(state=tk.DISABLED)
            self._switch_to_plan()
            
        except Exception as e:
            self._add_message(f"Error: {e}", 'error')
        
        return 'break'
    
    def _display_results(self, columns, rows):
        for w in self.grid_inner_frame.winfo_children():
            w.destroy()
        
        if not columns:
            return
        
        # Calculate column widths
        col_widths = []
        for i, col in enumerate(columns):
            w = len(str(col))
            for row in rows[:100]:
                if i < len(row):
                    val = str(row[i]) if row[i] is not None else 'NULL'
                    w = max(w, min(len(val), 50))
            col_widths.append(max(w, 8))
        
        # Header row
        tk.Label(self.grid_inner_frame, text="#", bg=self.colors['grid_header'],
            fg=self.colors['text'], font=('Segoe UI', 9, 'bold'), padx=6, pady=5,
            anchor='e', width=6).grid(row=0, column=0, sticky='nsew', padx=(0,1), pady=(0,1))
        
        for j, col in enumerate(columns):
            header = tk.Label(self.grid_inner_frame, text=col, bg=self.colors['grid_header'],
                fg=self.colors['text'], font=('Segoe UI', 9, 'bold'), padx=6, pady=5,
                anchor='w', width=col_widths[j])
            header.grid(row=0, column=j+1, sticky='nsew', padx=(0,1), pady=(0,1))
            
            # Sort on click
            header.bind('<Button-1>', lambda e, c=j: self._sort_results(c))
            header.configure(cursor='hand2')
        
        # Data rows
        for i, row in enumerate(rows):
            bg = self.colors['bg_dark'] if i % 2 == 0 else self.colors['grid_row_alt']
            
            tk.Label(self.grid_inner_frame, text=str(i+1), bg=self.colors['grid_header'],
                fg=self.colors['text_dim'], font=('Consolas', 9), padx=6, pady=3,
                anchor='e', width=6).grid(row=i+1, column=0, sticky='nsew', padx=(0,1))
            
            for j, val in enumerate(row):
                disp = str(val)[:200] if val is not None else 'NULL'
                fg = self.colors['text_dim'] if val is None else self.colors['text']
                
                cell = tk.Label(self.grid_inner_frame, text=disp, bg=bg, fg=fg,
                    font=('Consolas', 9), padx=6, pady=3, anchor='w', width=col_widths[j])
                cell.grid(row=i+1, column=j+1, sticky='nsew', padx=(0,1))
                cell.bind('<Double-Button-1>', lambda e, v=str(val) if val is not None else 'NULL': self._copy_value(v))
                
                # Hover
                cell.bind('<Enter>', lambda e, c=cell, b=bg: c.configure(bg=self.colors['bg_hover']))
                cell.bind('<Leave>', lambda e, c=cell, b=bg: c.configure(bg=b))
        
        self.grid_inner_frame.update_idletasks()
        self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox('all'))
        self._switch_to_results()
        
    def _sort_results(self, col_idx):
        if self.last_results and self.last_columns:
            try:
                sorted_results = sorted(self.last_results, key=lambda x: (x[col_idx] is None, x[col_idx]))
                self.last_results = sorted_results
                self._display_results(self.last_columns, sorted_results)
            except:
                pass
        
    def _copy_value(self, val):
        self.root.clipboard_clear()
        self.root.clipboard_append(val)
        self.status_text.set("Copied to clipboard")

    # ============== Editor Functions ==============
    
    def _sync_scroll(self, *args):
        self.query_text.yview(*args)
        self.line_numbers.yview(*args)
        
    def _on_scroll(self, *args, scrollbar):
        scrollbar.set(*args)
        self.line_numbers.yview_moveto(args[0])
        
    def _on_key_release(self, e=None):
        self._apply_syntax_highlighting()
        self._update_line_numbers()
        
    def _on_return(self, e):
        line = self.query_text.get("insert linestart", "insert")
        indent = ""
        for c in line:
            if c in (' ', '\t'):
                indent += c
            else:
                break
        
        # Auto-indent after certain keywords
        upper_line = line.strip().upper()
        if upper_line.endswith(('BEGIN', 'THEN', 'ELSE', 'AS', '(')):
            indent += "    "
        
        self.query_text.insert("insert", "\n" + indent)
        return "break"
        
    def _on_tab(self, e):
        self.query_text.insert(tk.INSERT, "    ")
        return "break"
        
    def _show_autocomplete(self, e=None):
        # Get current word
        pos = self.query_text.index(tk.INSERT)
        line = self.query_text.get(f"{pos} linestart", pos)
        
        # Find last word
        word = ""
        for c in reversed(line):
            if c.isalnum() or c == '_':
                word = c + word
            else:
                break
        
        if len(word) < 2:
            return 'break'
        
        # Build suggestions
        suggestions = []
        word_upper = word.upper()
        
        # Keywords
        for kw in self.sql_keywords:
            if kw.startswith(word_upper):
                suggestions.append(kw)
        
        # Tables
        for table in self.tables_cache:
            if table.upper().startswith(word_upper):
                suggestions.append(table)
        
        # Columns
        for table, cols in self.columns_cache.items():
            for col in cols:
                if col.upper().startswith(word_upper):
                    suggestions.append(col)
        
        if not suggestions:
            return 'break'
        
        # Show popup
        self._show_autocomplete_popup(suggestions[:15], word)
        return 'break'
        
    def _show_autocomplete_popup(self, suggestions, current_word):
        popup = tk.Toplevel(self.root)
        popup.wm_overrideredirect(True)
        popup.configure(bg=self.colors['border'])
        
        # Position near cursor
        x = self.query_text.winfo_rootx() + 50
        y = self.query_text.winfo_rooty() + 50
        popup.geometry(f"+{x}+{y}")
        
        listbox = tk.Listbox(popup, bg=self.colors['bg_medium'], fg=self.colors['text'],
            selectbackground=self.colors['accent'], font=('Consolas', 10),
            borderwidth=0, highlightthickness=0, width=30, height=min(len(suggestions), 10))
        listbox.pack(padx=1, pady=1)
        
        for s in suggestions:
            listbox.insert(tk.END, s)
        
        listbox.selection_set(0)
        
        def select(e=None):
            sel = listbox.curselection()
            if sel:
                selected = listbox.get(sel[0])
                # Replace current word
                pos = self.query_text.index(tk.INSERT)
                start = f"{pos}-{len(current_word)}c"
                self.query_text.delete(start, pos)
                self.query_text.insert(start, selected)
                self._apply_syntax_highlighting()
            popup.destroy()
        
        listbox.bind('<Return>', select)
        listbox.bind('<Double-Button-1>', select)
        listbox.bind('<Escape>', lambda e: popup.destroy())
        
        popup.bind('<FocusOut>', lambda e: popup.destroy())
        listbox.focus_set()
        
    def _apply_syntax_highlighting(self):
        for tag in ['keyword', 'function', 'string', 'comment', 'number', 'table']:
            self.query_text.tag_remove(tag, '1.0', tk.END)
        
        content = self.query_text.get('1.0', tk.END)
        
        # Strings
        for m in re.finditer(r"'[^']*'|\"[^\"]*\"", content):
            self.query_text.tag_add('string', f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        
        # Comments
        for m in re.finditer(r'--[^\n]*|/\*[\s\S]*?\*/', content):
            self.query_text.tag_add('comment', f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        
        # Numbers
        for m in re.finditer(r'\b\d+\.?\d*\b', content):
            self.query_text.tag_add('number', f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        
        # Keywords
        for kw in self.sql_keywords:
            for m in re.finditer(r'\b' + kw + r'\b', content, re.IGNORECASE):
                self.query_text.tag_add('keyword', f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        
        # Functions
        for func in self.sql_functions:
            for m in re.finditer(r'\b' + func + r'\s*\(', content, re.IGNORECASE):
                end = m.end() - 1
                self.query_text.tag_add('function', f"1.0+{m.start()}c", f"1.0+{end}c")
        
        # Tables (from cache)
        for table in self.tables_cache:
            for m in re.finditer(r'\b' + re.escape(table) + r'\b', content, re.IGNORECASE):
                self.query_text.tag_add('table', f"1.0+{m.start()}c", f"1.0+{m.end()}c")
                
    def _update_line_numbers(self):
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        lines = self.query_text.get('1.0', tk.END).count('\n')
        for i in range(1, lines + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        self.line_numbers.config(state=tk.DISABLED)

    # ============== Edit Menu Functions ==============
    
    def _undo(self):
        try:
            self.query_text.edit_undo()
        except:
            pass
        return 'break'
        
    def _redo(self):
        try:
            self.query_text.edit_redo()
        except:
            pass
        return 'break'
        
    def _cut(self):
        try:
            self.query_text.event_generate("<<Cut>>")
        except:
            pass
        return 'break'
        
    def _copy(self):
        try:
            self.query_text.event_generate("<<Copy>>")
        except:
            pass
        return 'break'
        
    def _paste(self):
        try:
            self.query_text.event_generate("<<Paste>>")
        except:
            pass
        return 'break'
        
    def _select_all(self):
        self.query_text.tag_add(tk.SEL, '1.0', tk.END)
        self.query_text.mark_set(tk.INSERT, '1.0')
        self.query_text.see(tk.INSERT)
        return 'break'
        
    def _find(self):
        search_text = simpledialog.askstring("Find", "Find what:")
        if search_text:
            start = '1.0'
            while True:
                pos = self.query_text.search(search_text, start, tk.END, nocase=True)
                if not pos:
                    break
                self.query_text.tag_add(tk.SEL, pos, f"{pos}+{len(search_text)}c")
                self.query_text.see(pos)
                start = f"{pos}+1c"
                break
        return 'break'
        
    def _replace(self):
        # Simple replace dialog
        find_text = simpledialog.askstring("Replace", "Find what:")
        if not find_text:
            return 'break'
        
        replace_text = simpledialog.askstring("Replace", "Replace with:")
        if replace_text is None:
            return 'break'
        
        content = self.query_text.get('1.0', tk.END)
        new_content = content.replace(find_text, replace_text)
        
        self.query_text.delete('1.0', tk.END)
        self.query_text.insert('1.0', new_content)
        self._apply_syntax_highlighting()
        
        return 'break'
        
    def _goto_line(self):
        line = simpledialog.askinteger("Go to Line", "Line number:")
        if line:
            self.query_text.mark_set(tk.INSERT, f"{line}.0")
            self.query_text.see(tk.INSERT)
        return 'break'
        
    def _comment_selection(self):
        try:
            start = self.query_text.index(tk.SEL_FIRST)
            end = self.query_text.index(tk.SEL_LAST)
            
            start_line = int(start.split('.')[0])
            end_line = int(end.split('.')[0])
            
            for line in range(start_line, end_line + 1):
                self.query_text.insert(f"{line}.0", "-- ")
            
            self._apply_syntax_highlighting()
        except tk.TclError:
            pass
        return 'break'
        
    def _uncomment_selection(self):
        try:
            start = self.query_text.index(tk.SEL_FIRST)
            end = self.query_text.index(tk.SEL_LAST)
            
            start_line = int(start.split('.')[0])
            end_line = int(end.split('.')[0])
            
            for line in range(start_line, end_line + 1):
                line_text = self.query_text.get(f"{line}.0", f"{line}.end")
                if line_text.startswith("-- "):
                    self.query_text.delete(f"{line}.0", f"{line}.3")
                elif line_text.startswith("--"):
                    self.query_text.delete(f"{line}.0", f"{line}.2")
            
            self._apply_syntax_highlighting()
        except tk.TclError:
            pass
        return 'break'
        
    def _format_query(self):
        query = self.query_text.get('1.0', tk.END).strip()
        
        # Basic formatting
        formatted = query
        formatted = re.sub(r'\s+', ' ', formatted)
        formatted = re.sub(r'\s*,\s*', ',\n    ', formatted)
        formatted = re.sub(r'\bFROM\b', '\nFROM', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bWHERE\b', '\nWHERE', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bAND\b', '\n  AND', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bOR\b', '\n  OR', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bORDER BY\b', '\nORDER BY', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bGROUP BY\b', '\nGROUP BY', formatted, flags=re.IGNORECASE)
        formatted = re.sub(r'\bJOIN\b', '\nJOIN', formatted, flags=re.IGNORECASE)
        
        self.query_text.delete('1.0', tk.END)
        self.query_text.insert('1.0', formatted)
        self._apply_syntax_highlighting()
        self._update_line_numbers()
        
        return 'break'
        
    def _uppercase_keywords(self):
        content = self.query_text.get('1.0', tk.END)
        
        for kw in self.sql_keywords:
            content = re.sub(r'\b' + kw + r'\b', kw.upper(), content, flags=re.IGNORECASE)
        
        self.query_text.delete('1.0', tk.END)
        self.query_text.insert('1.0', content)
        self._apply_syntax_highlighting()

    # ============== File Operations ==============
    
    def _open_query(self):
        fp = filedialog.askopenfilename(title="Open Query",
            filetypes=[("SQL Files", "*.sql"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        if fp:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tab_id = self._create_new_tab(os.path.basename(fp), content)
                self.query_tabs[tab_id].file_path = fp
                self.query_tabs[tab_id].set_modified(False)
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
        return 'break'
        
    def _save_query(self):
        if not self.active_tab_id:
            return 'break'
        
        tab = self.query_tabs[self.active_tab_id]
        
        if tab.file_path:
            try:
                content = self.query_text.get('1.0', tk.END)
                with open(tab.file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                tab.set_modified(False)
                self._add_message(f"Saved: {tab.file_path}", 'success')
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            self._save_query_as()
        
        return 'break'
        
    def _save_query_as(self):
        fp = filedialog.asksaveasfilename(title="Save Query As",
            defaultextension=".sql",
            filetypes=[("SQL Files", "*.sql"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        
        if fp:
            try:
                content = self.query_text.get('1.0', tk.END)
                with open(fp, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                if self.active_tab_id:
                    tab = self.query_tabs[self.active_tab_id]
                    tab.file_path = fp
                    tab.name = os.path.basename(fp)
                    tab.set_modified(False)
                    tab.label.configure(text=f"  {tab.name}  ")
                
                self._add_message(f"Saved: {fp}", 'success')
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ============== Export Functions ==============
    
    def _export_results(self):
        if not self.last_results or not self.last_columns:
            messagebox.showwarning("No Results", "No results to export.")
            return
        
        fp = filedialog.asksaveasfilename(title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        
        if fp:
            try:
                import csv
                with open(fp, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.last_columns)
                    writer.writerows(self.last_results)
                
                self._add_message(f"Exported to: {fp}", 'success')
                messagebox.showinfo("Success", f"Exported {len(self.last_results)} rows to {fp}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
    def _export_results_json(self):
        if not self.last_results or not self.last_columns:
            messagebox.showwarning("No Results", "No results to export.")
            return
        
        fp = filedialog.asksaveasfilename(title="Export to JSON",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        
        if fp:
            try:
                import json
                data = []
                for row in self.last_results:
                    row_dict = {}
                    for i, col in enumerate(self.last_columns):
                        row_dict[col] = row[i]
                    data.append(row_dict)
                
                with open(fp, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                
                self._add_message(f"Exported to: {fp}", 'success')
                messagebox.showinfo("Success", f"Exported {len(data)} rows to {fp}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ============== Results Panel ==============
    
    def _switch_to_results(self):
        self.messages_frame.pack_forget()
        self.plan_frame.pack_forget()
        self.results_grid_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_tab.configure(bg=self.colors['bg_dark'], fg=self.colors['text'])
        self.messages_tab.configure(bg=self.colors['bg_medium'], fg=self.colors['text_dim'])
        self.plan_tab.configure(bg=self.colors['bg_medium'], fg=self.colors['text_dim'])
        
    def _switch_to_messages(self):
        self.results_grid_frame.pack_forget()
        self.plan_frame.pack_forget()
        self.messages_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_tab.configure(bg=self.colors['bg_medium'], fg=self.colors['text_dim'])
        self.messages_tab.configure(bg=self.colors['bg_dark'], fg=self.colors['text'])
        self.plan_tab.configure(bg=self.colors['bg_medium'], fg=self.colors['text_dim'])
        
    def _switch_to_plan(self):
        self.results_grid_frame.pack_forget()
        self.messages_frame.pack_forget()
        self.plan_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_tab.configure(bg=self.colors['bg_medium'], fg=self.colors['text_dim'])
        self.messages_tab.configure(bg=self.colors['bg_medium'], fg=self.colors['text_dim'])
        self.plan_tab.configure(bg=self.colors['bg_dark'], fg=self.colors['text'])
        
    def _add_message(self, msg, msg_type='info'):
        self.messages_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.messages_text.insert(tk.END, f"[{timestamp}] ", 'info')
        self.messages_text.insert(tk.END, f"{msg}\n", msg_type)
        self.messages_text.see(tk.END)
        self.messages_text.config(state=tk.DISABLED)

    # ============== Table Operations ==============
    
    def _quick_select(self, table, limit):
        query = f"SELECT * FROM {table}"
        if limit:
            query += f"\nLIMIT {limit}"
        query += ";"
        
        self.query_text.delete('1.0', tk.END)
        self.query_text.insert('1.0', query)
        self._apply_syntax_highlighting()
        self._update_line_numbers()
        self._execute_query()
        
    def _script_create(self, table):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = cursor.fetchone()
            if result:
                self.query_text.delete('1.0', tk.END)
                self.query_text.insert('1.0', result[0] + ";")
                self._apply_syntax_highlighting()
                self._update_line_numbers()
        except Exception as e:
            self._add_message(f"Error: {e}", 'error')
            
    def _script_drop(self, table):
        self.query_text.insert(tk.INSERT, f"DROP TABLE IF EXISTS {table};")
        self._apply_syntax_highlighting()
        
    def _rename_table(self, table):
        new_name = simpledialog.askstring("Rename Table", f"New name for '{table}':")
        if new_name:
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"ALTER TABLE {table} RENAME TO {new_name}")
                self.connection.commit()
                self._refresh_object_explorer()
                self._add_message(f"Renamed '{table}' to '{new_name}'", 'success')
            except Exception as e:
                self._add_message(f"Error: {e}", 'error')
                
    def _drop_table(self, table):
        if messagebox.askyesno("Confirm", f"Drop table '{table}'?\nThis cannot be undone."):
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"DROP TABLE {table}")
                self.connection.commit()
                self._refresh_object_explorer()
                self._add_message(f"Dropped table '{table}'", 'success')
            except Exception as e:
                self._add_message(f"Error: {e}", 'error')
                
    def _script_view_create(self, view):
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='view' AND name='{view}'")
            result = cursor.fetchone()
            if result:
                self.query_text.delete('1.0', tk.END)
                self.query_text.insert('1.0', result[0] + ";")
                self._apply_syntax_highlighting()
                self._update_line_numbers()
        except Exception as e:
            self._add_message(f"Error: {e}", 'error')
            
    def _drop_view(self, view):
        if messagebox.askyesno("Confirm", f"Drop view '{view}'?"):
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"DROP VIEW {view}")
                self.connection.commit()
                self._refresh_object_explorer()
                self._add_message(f"Dropped view '{view}'", 'success')
            except Exception as e:
                self._add_message(f"Error: {e}", 'error')

    # ============== Tools ==============
    
    def _show_database_info(self):
        if not self.connection:
            messagebox.showwarning("No Database", "Connect to a database first.")
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Tables count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables_count = cursor.fetchone()[0]
            
            # Views count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view'")
            views_count = cursor.fetchone()[0]
            
            # Indexes count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
            indexes_count = cursor.fetchone()[0]
            
            # Database size
            db_size = os.path.getsize(self.current_db_path)
            size_mb = db_size / (1024 * 1024)
            
            # Page count
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            # Page size
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            info = f"""Database Information
{'='*50}

File: {self.current_db_path}
Size: {size_mb:.2f} MB ({db_size:,} bytes)

Page Count: {page_count:,}
Page Size: {page_size:,} bytes

Tables: {tables_count}
Views: {views_count}
Indexes: {indexes_count}
"""
            
            messagebox.showinfo("Database Info", info)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def _table_designer(self):
        messagebox.showinfo("Table Designer", "Table Designer feature coming soon!")
        
    def _data_generator(self):
        messagebox.showinfo("Data Generator", "Data Generator feature coming soon!")
        
    def _vacuum_database(self):
        if not self.connection:
            return
        
        if messagebox.askyesno("Vacuum Database", "This will rebuild the database file.\nContinue?"):
            try:
                cursor = self.connection.cursor()
                cursor.execute("VACUUM")
                self.connection.commit()
                self._add_message("Database vacuumed successfully", 'success')
                messagebox.showinfo("Success", "Database has been vacuumed.")
            except Exception as e:
                self._add_message(f"Error: {e}", 'error')
                
    def _integrity_check(self):
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchall()
            
            if result[0][0] == 'ok':
                messagebox.showinfo("Integrity Check", "Database integrity: OK")
                self._add_message("Integrity check passed", 'success')
            else:
                messagebox.showwarning("Integrity Check", "\n".join([r[0] for r in result]))
                self._add_message("Integrity check found issues", 'warning')
        except Exception as e:
            messagebox.showerror("Error", str(e))
            
    def _analyze_database(self):
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("ANALYZE")
            self.connection.commit()
            self._add_message("Database analyzed successfully", 'success')
            messagebox.showinfo("Success", "Database statistics have been updated.")
        except Exception as e:
            self._add_message(f"Error: {e}", 'error')
            
    def _show_query_history(self):
        if not self.query_history:
            messagebox.showinfo("Query History", "No query history available.")
            return
        
        win = tk.Toplevel(self.root)
        win.title("Query History")
        win.geometry("800x600")
        win.configure(bg=self.colors['bg_dark'])
        
        text = tk.Text(win, bg=self.colors['bg_dark'], fg=self.colors['text'],
            font=('Consolas', 10), wrap=tk.WORD)
        scroll = tk.Scrollbar(win, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for i, query in enumerate(reversed(self.query_history), 1):
            text.insert(tk.END, f"--- Query {i} ---\n{query}\n\n")
        
        text.config(state=tk.DISABLED)
        
    def _show_schema_diagram(self):
        if not self.connection:
            messagebox.showwarning("No Database", "Connect to a database first.")
            return
        
        # Create schema viewer window
        schema_win = tk.Toplevel(self.root)
        schema_win.title("Database Schema Diagram")
        schema_win.geometry("1200x800")
        schema_win.configure(bg=self.colors['bg_dark'])
        
        # Toolbar
        toolbar = tk.Frame(schema_win, bg=self.colors['bg_medium'], height=40)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        tk.Label(toolbar, text="Database Schema", bg=self.colors['bg_medium'],
                 fg=self.colors['text'], font=('Segoe UI', 11, 'bold'),
                 padx=12).pack(side=tk.LEFT, pady=8)
        
        tk.Button(toolbar, text="Refresh", command=lambda: self._draw_schema(canvas, schema_win),
                  bg=self.colors['accent'], fg='white', relief=tk.FLAT,
                  font=('Segoe UI', 9), padx=12, pady=4).pack(side=tk.RIGHT, padx=10, pady=6)
        
        tk.Button(toolbar, text="Zoom In", command=lambda: self._zoom_schema(canvas, 1.2),
                  bg=self.colors['bg_lighter'], fg=self.colors['text'], relief=tk.FLAT,
                  font=('Segoe UI', 9), padx=12, pady=4).pack(side=tk.RIGHT, padx=2, pady=6)
        
        tk.Button(toolbar, text="Zoom Out", command=lambda: self._zoom_schema(canvas, 0.8),
                  bg=self.colors['bg_lighter'], fg=self.colors['text'], relief=tk.FLAT,
                  font=('Segoe UI', 9), padx=12, pady=4).pack(side=tk.RIGHT, padx=2, pady=6)
        
        # Canvas with scrollbars
        canvas_frame = tk.Frame(schema_win, bg=self.colors['bg_dark'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_dark'],
                           highlightthickness=0, borderwidth=0)
        
        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Mouse pan
        canvas.bind('<ButtonPress-2>', lambda e: canvas.scan_mark(e.x, e.y))
        canvas.bind('<B2-Motion>', lambda e: canvas.scan_dragto(e.x, e.y, gain=1))
        
        # Store canvas reference
        schema_win.canvas = canvas
        schema_win.zoom_level = 1.0
        
        # Draw schema
        self._draw_schema(canvas, schema_win)
    
    def _draw_schema(self, canvas, window):
        """Draw database schema with tables and relationships"""
        canvas.delete('all')
        
        if not self.connection:
            return
        
        try:
            cursor = self.connection.cursor()
            
            # Get all tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%' 
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                canvas.create_text(400, 300, text="No tables in database",
                                 fill=self.colors['text_dim'], font=('Segoe UI', 14))
                return
            
            # Get table info and relationships
            table_data = {}
            relationships = []
            
            for table in tables:
                # Get columns
                cursor.execute(f"PRAGMA table_info('{table}')")
                columns = cursor.fetchall()
                
                # Get foreign keys
                cursor.execute(f"PRAGMA foreign_key_list('{table}')")
                fks = cursor.fetchall()
                
                table_data[table] = {
                    'columns': columns,
                    'foreign_keys': fks
                }
                
                # Store relationships
                for fk in fks:
                    relationships.append({
                        'from_table': table,
                        'from_column': fk[3],
                        'to_table': fk[2],
                        'to_column': fk[4] if fk[4] else 'id'
                    })
            
            # Calculate layout (grid-based)
            cols_per_row = max(3, int(len(tables) ** 0.5))
            table_width = 220
            table_spacing_x = 320
            table_spacing_y = 280
            start_x = 80
            start_y = 80
            
            table_positions = {}
            for i, table in enumerate(tables):
                row = i // cols_per_row
                col = i % cols_per_row
                x = start_x + col * table_spacing_x
                y = start_y + row * table_spacing_y
                table_positions[table] = (x, y)
            
            # Draw relationships first (so they appear behind tables)
            for rel in relationships:
                from_table = rel['from_table']
                to_table = rel['to_table']
                
                if from_table in table_positions and to_table in table_positions:
                    x1, y1 = table_positions[from_table]
                    x2, y2 = table_positions[to_table]
                    
                    # Calculate connection points (center of table boxes)
                    x1_center = x1 + table_width // 2
                    y1_center = y1 + 20  # Top of box
                    x2_center = x2 + table_width // 2
                    y2_center = y2 + 20
                    
                    # Determine relationship type (simple heuristic)
                    # In real implementation, you'd analyze the foreign key constraints
                    rel_type = "1:N"  # Default
                    
                    # Draw arrow
                    self._draw_relationship_line(canvas, x1_center, y1_center + 40,
                                                x2_center, y2_center, rel_type)
            
            # Draw tables
            for table, (x, y) in table_positions.items():
                self._draw_table_box(canvas, table, x, y, table_data[table])
            
            # Update scroll region
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox('all'))
            
        except Exception as e:
            canvas.create_text(400, 300, text=f"Error: {e}",
                             fill=self.colors['error'], font=('Segoe UI', 12))
                             
    def _draw_table_box(self, canvas, table_name, x, y, table_info):
        """Draw a single table box with columns"""
        width = 220
        header_height = 35
        row_height = 24
        
        columns = table_info['columns']
        total_height = header_height + len(columns) * row_height
        
        # Shadow
        canvas.create_rectangle(x+3, y+3, x+width+3, y+total_height+3,
                              fill='#000000', outline='', tags='table')
        
        # Main box
        canvas.create_rectangle(x, y, x+width, y+total_height,
                              fill=self.colors['bg_medium'], outline=self.colors['border'],
                              width=2, tags='table')
        
        # Header
        canvas.create_rectangle(x, y, x+width, y+header_height,
                              fill=self.colors['accent'], outline='', tags='table')
        
        # Table icon
        icon_canvas = tk.Canvas(canvas, width=20, height=20, bg=self.colors['accent'],
                               highlightthickness=0)
        canvas.create_window(x+8, y+8, window=icon_canvas, anchor='nw', tags='table')
        IconFactory.create_table_icon(icon_canvas, 2, 2, 16)
        
        # Table name
        canvas.create_text(x+35, y+header_height//2, text=table_name,
                          fill='white', font=('Segoe UI', 10, 'bold'),
                          anchor='w', tags='table')
        
        # Separator line
        canvas.create_line(x, y+header_height, x+width, y+header_height,
                          fill=self.colors['border'], width=1, tags='table')
        
        # Columns
        for i, col in enumerate(columns):
            col_y = y + header_height + i * row_height
            
            col_name = col[1]
            col_type = col[2] or 'BLOB'
            is_pk = col[5] == 1
            not_null = col[3] == 1
            
            # Row background (alternating)
            if i % 2 == 0:
                canvas.create_rectangle(x, col_y, x+width, col_y+row_height,
                                      fill=self.colors['bg_light'], outline='', tags='table')
            
            # Primary key icon or column icon
            icon_x = x + 8
            icon_y = col_y + 4
            
            if is_pk:
                # Draw PK icon directly on canvas
                canvas.create_oval(icon_x, icon_y, icon_x+7, icon_y+7,
                                 fill='#FFD700', outline='#FFFFFF', width=1, tags='table')
                canvas.create_text(icon_x+3.5, icon_y+3.5, text='K',
                                 fill='#000000', font=('Arial', 6, 'bold'), tags='table')
            else:
                # Regular column bullet
                canvas.create_oval(icon_x+2, icon_y+4, icon_x+5, icon_y+7,
                                 fill=self.colors['text_dim'], outline='', tags='table')
            
            # Column name
            canvas.create_text(x+25, col_y+row_height//2, text=col_name,
                             fill=self.colors['text'], font=('Consolas', 9),
                             anchor='w', tags='table')
            
            # Column type
            canvas.create_text(x+width-10, col_y+row_height//2, text=col_type,
                             fill=self.colors['text_dim'], font=('Consolas', 8),
                             anchor='e', tags='table')
            
            # NOT NULL indicator
            if not_null and not is_pk:
                canvas.create_text(x+width-50, col_y+row_height//2, text='*',
                                 fill=self.colors['warning'], font=('Arial', 10, 'bold'),
                                 anchor='e', tags='table')
    
    def _draw_relationship_line(self, canvas, x1, y1, x2, y2, rel_type):
        """Draw relationship line between tables"""
        
        # Choose color based on relationship type
        if rel_type == "1:1":
            color = '#4CAF50'  # Green
        elif rel_type == "1:N":
            color = '#2196F3'  # Blue
        elif rel_type == "N:N":
            color = '#FF9800'  # Orange
        else:
            color = self.colors['text_dim']
        
        # Draw curved line
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        
        # Control points for bezier curve (simple approximation)
        control_offset = abs(x2 - x1) * 0.3
        
        if abs(x2 - x1) > abs(y2 - y1):
            # Horizontal relationship
            canvas.create_line(x1, y1, mid_x, y1, mid_x, y2, x2, y2,
                             fill=color, width=2, smooth=True, tags='relationship')
        else:
            # Vertical relationship
            canvas.create_line(x1, y1, x1, mid_y, x2, mid_y, x2, y2,
                             fill=color, width=2, smooth=True, tags='relationship')
        
        # Draw cardinality indicators
        # Start point (many side - crow's foot)
        if rel_type in ["1:N", "N:N"]:
            canvas.create_line(x1-5, y1-5, x1, y1, x1+5, y1-5,
                             fill=color, width=2, tags='relationship')
        else:
            # One side - perpendicular line
            canvas.create_line(x1-5, y1, x1+5, y1,
                             fill=color, width=2, tags='relationship')
        
        # End point (one side)
        if rel_type == "N:N":
            # Many side
            canvas.create_line(x2-5, y2+5, x2, y2, x2+5, y2+5,
                             fill=color, width=2, tags='relationship')
        else:
            # One side
            canvas.create_line(x2-5, y2, x2+5, y2,
                             fill=color, width=2, tags='relationship')
        
        # Label
        label_text = rel_type
        canvas.create_text(mid_x, mid_y-10, text=label_text,
                          fill=color, font=('Segoe UI', 9, 'bold'),
                          tags='relationship')
    
    def _zoom_schema(self, canvas, factor):
        """Zoom in/out the schema diagram"""
        canvas.scale('all', 0, 0, factor, factor)
        canvas.configure(scrollregion=canvas.bbox('all'))
        
    def _show_sql_reference(self):
        ref_text = """SQLite Quick Reference
{'='*50}

SELECT - Query data
  SELECT column1, column2 FROM table WHERE condition;

INSERT - Add data
  INSERT INTO table (col1, col2) VALUES (val1, val2);

UPDATE - Modify data
  UPDATE table SET col1 = val1 WHERE condition;

DELETE - Remove data
  DELETE FROM table WHERE condition;

CREATE TABLE - Create table
  CREATE TABLE table (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
  );

Common Functions:
  COUNT(), SUM(), AVG(), MIN(), MAX()
  LENGTH(), UPPER(), LOWER(), SUBSTR()
  DATE(), TIME(), DATETIME()
  
Joins:
  INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN
  
Press F5 to execute queries!
"""
        messagebox.showinfo("SQL Reference", ref_text)
        
    def _show_shortcuts(self):
        shortcuts = """Keyboard Shortcuts
{'='*50}

F5                 Execute query
F8                 Execute selected
Ctrl+Enter         Execute current statement
Ctrl+L             Explain query plan

Ctrl+N             New query tab
Ctrl+W             Close tab
Ctrl+O             Open database
Ctrl+S             Save query

Ctrl+Z             Undo
Ctrl+Y             Redo
Ctrl+F             Find
Ctrl+H             Replace
Ctrl+G             Go to line

Ctrl+K             Comment selection
Ctrl+Shift+K       Uncomment selection
Ctrl+Shift+F       Format query
Ctrl+Space         Show autocomplete
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
        
    def _show_about(self):
        about = """SQL Manager Studio Pro
Version 1.0

A professional database management tool for SQLite.

Features:
- Dark theme interface
- Multiple query tabs
- Syntax highlighting
- Drag & drop support
- Object Explorer
- Query history
- Export to CSV/JSON
- And much more!

© 2024 SQL Manager Studio Pro
"""
        messagebox.showinfo("About", about)
        
    def _on_exit(self):
        # Check for unsaved changes
        unsaved = [tab for tab in self.query_tabs.values() if tab.modified]
        
        if unsaved:
            result = messagebox.askyesnocancel("Unsaved Changes",
                f"You have {len(unsaved)} unsaved tab(s).\nSave changes before exiting?")
            
            if result is None:  # Cancel
                return
            elif result:  # Yes
                for tab_id in list(self.query_tabs.keys()):
                    self._select_tab(tab_id)
                    self._save_query()
        
        if self.connection:
            self.connection.close()
        
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SQLManagerStudioPro(root)
    root.protocol("WM_DELETE_WINDOW", app._on_exit)
    root.mainloop()