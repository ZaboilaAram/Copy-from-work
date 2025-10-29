import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, ttk, simpledialog
import sqlite3
import json
import csv
import os
from datetime import datetime
import shutil
import threading
import hashlib
import re

class DatabaseManager:
    def __init__(self, rootdbman3):
        self.rootdbman3 = rootdbman3
        self.rootdbman3.title("Advanced Database Manager Pro")
        self.rootdbman3.geometry("1600x900")
        
        # Windows 95 Color Scheme
        self.bg_color = "#c0c0c0"
        self.button_color = "#c0c0c0"
        self.active_bg = "#000080"
        self.text_bg = "#ffffff"
        self.border_light = "#ffffff"
        self.border_dark = "#808080"
        self.border_black = "#000000"
        
        self.rootdbman3.configure(bg=self.bg_color)
        
        self.db_path = None
        self.conn = None
        self.current_table = None
        self.query_history = []
        self.bookmarks = {}
        self.recent_databases = []
        self.auto_refresh = False
        self.page_size = 100
        self.current_page = 0
        
        self.setup_ui()
        self.load_settings()
        
    def create_win95_button(self, parent, text, command, width=15):
        """Create a Windows 95 style button"""
        btn = tk.Button(
            parent, 
            text=text, 
            command=command,
            width=width,
            bg=self.button_color,
            fg="#000000",
            relief=tk.RAISED,
            bd=2,
            font=("MS Sans Serif", 8),
            activebackground=self.bg_color,
            cursor="hand2"
        )
        return btn
        
    def create_win95_frame(self, parent, sunken=False):
        """Create a Windows 95 style frame"""
        frame = tk.Frame(
            parent,
            bg=self.bg_color,
            relief=tk.SUNKEN if sunken else tk.RAISED,
            bd=2
        )
        return frame
        
    def setup_ui(self):
        # Menu Bar
        menubar = tk.Menu(self.rootdbman3, bg=self.bg_color, fg="#000000", 
                         activebackground=self.active_bg, activeforeground="#ffffff")
        self.rootdbman3.config(menu=menubar)
        
        # Database Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg="#000000",
                           activebackground=self.active_bg, activeforeground="#ffffff")
        menubar.add_cascade(label="Database", menu=file_menu)
        file_menu.add_command(label="New Database", command=self.new_database, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Database", command=self.open_database, accelerator="Ctrl+O")
        file_menu.add_command(label="Close Database", command=self.close_database, accelerator="Ctrl+W")
        file_menu.add_separator()
        
        # Recent Databases submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0, bg=self.bg_color, fg="#000000",
                                   activebackground=self.active_bg, activeforeground="#ffffff")
        file_menu.add_cascade(label="Recent Databases", menu=self.recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_command(label="Restore Database", command=self.restore_database)
        file_menu.add_command(label="Clone Database", command=self.clone_database)
        file_menu.add_command(label="Compact Database", command=self.compact_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.rootdbman3.quit, accelerator="Alt+F4")
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg="#000000",
                            activebackground=self.active_bg, activeforeground="#ffffff")
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Execute SQL", command=self.show_sql_executor, accelerator="F5")
        tools_menu.add_command(label="Query Builder", command=self.show_query_builder)
        tools_menu.add_command(label="Query History", command=self.show_query_history)
        tools_menu.add_separator()
        tools_menu.add_command(label="Find & Replace", command=self.show_find_replace)
        tools_menu.add_command(label="Data Generator", command=self.show_data_generator)
        tools_menu.add_command(label="Schema Comparison", command=self.compare_schemas)
        tools_menu.add_separator()
        tools_menu.add_command(label="Database Statistics", command=self.show_statistics)
        tools_menu.add_command(label="Integrity Check", command=self.integrity_check)
        tools_menu.add_command(label="Optimize Database", command=self.optimize_database)
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg="#000000",
                           activebackground=self.active_bg, activeforeground="#ffffff")
        menubar.add_cascade(label="View", menu=view_menu)
        self.auto_refresh_var = tk.BooleanVar(value=False)
        view_menu.add_checkbutton(label="Auto Refresh", variable=self.auto_refresh_var, 
                                  command=self.toggle_auto_refresh)
        view_menu.add_separator()
        view_menu.add_command(label="Refresh Tables", command=self.refresh_tables_list, accelerator="F5")
        view_menu.add_command(label="Refresh Data", command=self.load_table_data, accelerator="Ctrl+R")
        
        # Export/Import Menu
        export_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg="#000000",
                             activebackground=self.active_bg, activeforeground="#ffffff")
        menubar.add_cascade(label="Export/Import", menu=export_menu)
        export_menu.add_command(label="Export Table to CSV", command=self.export_csv)
        export_menu.add_command(label="Export Table to JSON", command=self.export_json)
        export_menu.add_command(label="Export Table to SQL", command=self.export_sql)
        export_menu.add_command(label="Export All Tables", command=self.export_all_tables)
        export_menu.add_separator()
        export_menu.add_command(label="Import from CSV", command=self.import_csv)
        export_menu.add_command(label="Import from JSON", command=self.import_json)
        export_menu.add_command(label="Import from SQL", command=self.import_sql)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, fg="#000000",
                           activebackground=self.active_bg, activeforeground="#ffffff")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="SQL Reference", command=self.show_sql_reference)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        
        # Toolbar
        toolbar = self.create_win95_frame(self.rootdbman3)
        toolbar.pack(fill=tk.X, padx=4, pady=4)
        
        toolbar_inner = tk.Frame(toolbar, bg=self.bg_color)
        toolbar_inner.pack(fill=tk.X, padx=2, pady=2)
        
        self.create_win95_button(toolbar_inner, "New DB", self.new_database, 10).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(toolbar_inner, "Open DB", self.open_database, 10).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(toolbar_inner, "Save", self.save_changes, 10).pack(side=tk.LEFT, padx=2)
        
        tk.Frame(toolbar_inner, width=2, bg=self.border_dark).pack(side=tk.LEFT, fill=tk.Y, padx=4)
        
        self.create_win95_button(toolbar_inner, "SQL", self.show_sql_executor, 10).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(toolbar_inner, "Stats", self.show_statistics, 10).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(toolbar_inner, "Backup", self.backup_database, 10).pack(side=tk.LEFT, padx=2)
        
        # Main Container with Paned Window
        main_container = tk.PanedWindow(self.rootdbman3, orient=tk.HORIZONTAL, 
                                       bg=self.bg_color, sashwidth=5, sashrelief=tk.RAISED)
        main_container.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Left Panel - Tables List
        left_panel = self.create_win95_frame(main_container)
        main_container.add(left_panel, minsize=200)
        
        title_frame = tk.Frame(left_panel, bg=self.active_bg, height=20)
        title_frame.pack(fill=tk.X)
        tk.Label(title_frame, text="Database Objects", font=("MS Sans Serif", 8, "bold"), 
                bg=self.active_bg, fg="#ffffff").pack(pady=2)
        
        # Tabs for different object types
        tab_frame = tk.Frame(left_panel, bg=self.bg_color)
        tab_frame.pack(fill=tk.X, padx=2, pady=2)
        
        self.object_type = tk.StringVar(value="tables")
        tk.Radiobutton(tab_frame, text="Tables", variable=self.object_type, value="tables",
                      bg=self.bg_color, command=self.refresh_objects_list, 
                      font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(tab_frame, text="Views", variable=self.object_type, value="views",
                      bg=self.bg_color, command=self.refresh_objects_list,
                      font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(tab_frame, text="Indexes", variable=self.object_type, value="indexes",
                      bg=self.bg_color, command=self.refresh_objects_list,
                      font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        listbox_frame = self.create_win95_frame(left_panel, sunken=True)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tables_listbox = tk.Listbox(
            listbox_frame, 
            font=("Fixedsys", 9),
            bg=self.text_bg,
            fg="#000000",
            selectbackground=self.active_bg,
            selectforeground="#ffffff",
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.tables_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tables_listbox.yview)
        self.tables_listbox.bind("<<ListboxSelect>>", self.on_table_select)
        self.tables_listbox.bind("<Double-Button-1>", lambda e: self.load_table_data())
        self.tables_listbox.bind("<Button-3>", self.show_context_menu)
        
        table_buttons = tk.Frame(left_panel, bg=self.bg_color)
        table_buttons.pack(fill=tk.X, padx=4, pady=4)
        
        self.create_win95_button(table_buttons, "New Table", 
                                self.create_table_dialog, 20).pack(fill=tk.X, pady=2)
        self.create_win95_button(table_buttons, "Create View", 
                                self.create_view_dialog, 20).pack(fill=tk.X, pady=2)
        self.create_win95_button(table_buttons, "Drop Object", 
                                self.drop_object, 20).pack(fill=tk.X, pady=2)
        self.create_win95_button(table_buttons, "View Structure", 
                                self.view_table_structure, 20).pack(fill=tk.X, pady=2)
        
        # Right Panel - Data View with Notebook
        right_panel = tk.Frame(main_container, bg=self.bg_color)
        main_container.add(right_panel, minsize=800)
        
        # Create notebook for multiple tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Data Tab
        data_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(data_tab, text="Data View")
        
        self.setup_data_tab(data_tab)
        
        # Relationships Tab
        relations_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(relations_tab, text="Relationships")
        self.setup_relations_tab(relations_tab)
        
        # Status Bar
        status_frame = self.create_win95_frame(self.rootdbman3, sunken=True)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=4)
        
        status_inner = tk.Frame(status_frame, bg=self.bg_color)
        status_inner.pack(fill=tk.X, padx=2, pady=2)
        
        self.status_bar = tk.Label(
            status_inner, 
            text="Ready", 
            font=("MS Sans Serif", 8),
            bg=self.bg_color,
            fg="#000000",
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.record_count_label = tk.Label(
            status_inner,
            text="Records: 0",
            font=("MS Sans Serif", 8),
            bg=self.bg_color,
            fg="#000000"
        )
        self.record_count_label.pack(side=tk.RIGHT, padx=10)
        
        # Keyboard shortcuts
        self.rootdbman3.bind('<Control-n>', lambda e: self.new_database())
        self.rootdbman3.bind('<Control-o>', lambda e: self.open_database())
        self.rootdbman3.bind('<Control-w>', lambda e: self.close_database())
        self.rootdbman3.bind('<F5>', lambda e: self.show_sql_executor())
        self.rootdbman3.bind('<Control-r>', lambda e: self.load_table_data())
        self.rootdbman3.bind('<Control-f>', lambda e: self.show_find_replace())
        
    def setup_data_tab(self, parent):
        # Top Section - Table Info and Controls
        top_section = self.create_win95_frame(parent)
        top_section.pack(fill=tk.X, pady=(0, 4))
        
        info_inner = tk.Frame(top_section, bg=self.bg_color)
        info_inner.pack(fill=tk.X, padx=2, pady=2)
        
        self.table_label = tk.Label(
            info_inner, 
            text="No table selected", 
            font=("MS Sans Serif", 9, "bold"),
            bg=self.bg_color,
            fg="#000000",
            anchor="w"
        )
        self.table_label.pack(side=tk.LEFT, padx=4)
        
        # Search and Filter Section
        search_frame = self.create_win95_frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 4))
        
        search_inner = tk.Frame(search_frame, bg=self.bg_color)
        search_inner.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Label(search_inner, text="Search:", font=("MS Sans Serif", 8), 
                bg=self.bg_color).pack(side=tk.LEFT, padx=4)
        
        self.search_entry = tk.Entry(search_inner, width=30, font=("MS Sans Serif", 8),
                                     relief=tk.SUNKEN, bd=2)
        self.search_entry.pack(side=tk.LEFT, padx=4)
        self.search_entry.bind('<Return>', lambda e: self.filter_data())
        
        tk.Label(search_inner, text="Column:", font=("MS Sans Serif", 8),
                bg=self.bg_color).pack(side=tk.LEFT, padx=4)
        
        self.filter_column = ttk.Combobox(search_inner, width=15, 
                                         font=("MS Sans Serif", 8), state="readonly")
        self.filter_column.pack(side=tk.LEFT, padx=4)
        
        self.create_win95_button(search_inner, "Filter", 
                                self.filter_data, 10).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(search_inner, "Clear", 
                                self.clear_filter, 10).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(search_inner, "Advanced", 
                                self.show_advanced_filter, 10).pack(side=tk.LEFT, padx=2)
        
        # Sorting controls
        tk.Label(search_inner, text="Sort:", font=("MS Sans Serif", 8),
                bg=self.bg_color).pack(side=tk.LEFT, padx=(20, 4))
        
        self.sort_column = ttk.Combobox(search_inner, width=15,
                                       font=("MS Sans Serif", 8), state="readonly")
        self.sort_column.pack(side=tk.LEFT, padx=4)
        
        self.sort_order = ttk.Combobox(search_inner, width=8,
                                      font=("MS Sans Serif", 8), state="readonly",
                                      values=["ASC", "DESC"])
        self.sort_order.set("ASC")
        self.sort_order.pack(side=tk.LEFT, padx=4)
        
        self.create_win95_button(search_inner, "Sort", 
                                self.apply_sort, 8).pack(side=tk.LEFT, padx=2)
        
        # Data Display with Treeview for better column display
        data_outer = self.create_win95_frame(parent, sunken=True)
        data_outer.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        
        # Create Treeview
        tree_frame = tk.Frame(data_outer, bg="#ffffff")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        y_scrollbar = tk.Scrollbar(tree_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.data_tree = ttk.Treeview(tree_frame, 
                                     yscrollcommand=y_scrollbar.set,
                                     xscrollcommand=x_scrollbar.set,
                                     selectmode='browse')
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.data_tree.yview)
        x_scrollbar.config(command=self.data_tree.xview)
        
        self.data_tree.bind('<Double-Button-1>', lambda e: self.update_record_dialog())
        self.data_tree.bind('<Button-3>', self.show_data_context_menu)
        
        # Pagination controls
        pagination_frame = self.create_win95_frame(parent)
        pagination_frame.pack(fill=tk.X, pady=(0, 4))
        
        pag_inner = tk.Frame(pagination_frame, bg=self.bg_color)
        pag_inner.pack(fill=tk.X, padx=2, pady=2)
        
        self.create_win95_button(pag_inner, "<<", 
                                lambda: self.change_page(-10), 5).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(pag_inner, "<", 
                                lambda: self.change_page(-1), 5).pack(side=tk.LEFT, padx=2)
        
        self.page_label = tk.Label(pag_inner, text="Page: 1", 
                                   font=("MS Sans Serif", 8), bg=self.bg_color)
        self.page_label.pack(side=tk.LEFT, padx=10)
        
        self.create_win95_button(pag_inner, ">", 
                                lambda: self.change_page(1), 5).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(pag_inner, ">>", 
                                lambda: self.change_page(10), 5).pack(side=tk.LEFT, padx=2)
        
        tk.Label(pag_inner, text="Page Size:", font=("MS Sans Serif", 8),
                bg=self.bg_color).pack(side=tk.LEFT, padx=(20, 4))
        
        self.page_size_var = tk.StringVar(value="100")
        page_size_combo = ttk.Combobox(pag_inner, textvariable=self.page_size_var,
                                      width=8, font=("MS Sans Serif", 8),
                                      values=["50", "100", "200", "500", "1000"],
                                      state="readonly")
        page_size_combo.pack(side=tk.LEFT, padx=4)
        page_size_combo.bind('<<ComboboxSelected>>', lambda e: self.change_page_size())
        
        # Operations Section
        ops_frame = self.create_win95_frame(parent)
        ops_frame.pack(fill=tk.X, pady=(0, 4))
        
        ops_inner = tk.Frame(ops_frame, bg=self.bg_color)
        ops_inner.pack(fill=tk.X, padx=2, pady=2)
        
        self.create_win95_button(ops_inner, "Insert", 
                                self.insert_record_dialog, 12).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(ops_inner, "Update", 
                                self.update_record_dialog, 12).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(ops_inner, "Delete", 
                                self.delete_record, 12).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(ops_inner, "Duplicate", 
                                self.duplicate_record, 12).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(ops_inner, "Refresh", 
                                self.load_table_data, 12).pack(side=tk.LEFT, padx=2)
        
        tk.Frame(ops_inner, width=20, bg=self.bg_color).pack(side=tk.LEFT)
        
        self.create_win95_button(ops_inner, "Export CSV", 
                                self.export_csv, 12).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(ops_inner, "Export JSON", 
                                self.export_json, 12).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(ops_inner, "Import CSV", 
                                self.import_csv, 12).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(ops_inner, "Bulk Edit", 
                                self.show_bulk_edit, 12).pack(side=tk.LEFT, padx=2)
    
    def setup_relations_tab(self, parent):
        info_frame = self.create_win95_frame(parent)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        text_frame = self.create_win95_frame(info_frame, sunken=True)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        self.relations_text = scrolledtext.ScrolledText(
            text_frame,
            font=("Fixedsys", 9),
            bg="#ffffff",
            fg="#000000",
            bd=0
        )
        self.relations_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        btn_frame = tk.Frame(info_frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=4, pady=4)
        
        self.create_win95_button(btn_frame, "Refresh Relations", 
                                self.load_relations, 15).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(btn_frame, "Create Foreign Key", 
                                self.create_foreign_key, 15).pack(side=tk.LEFT, padx=2)
        
    def load_relations(self):
        if not self.conn:
            return
            
        self.relations_text.delete("1.0", tk.END)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            self.relations_text.insert(tk.END, "DATABASE RELATIONSHIPS\n")
            self.relations_text.insert(tk.END, "=" * 80 + "\n\n")
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                fkeys = cursor.fetchall()
                
                if fkeys:
                    self.relations_text.insert(tk.END, f"Table: {table_name}\n")
                    self.relations_text.insert(tk.END, "-" * 40 + "\n")
                    
                    for fkey in fkeys:
                        self.relations_text.insert(tk.END, 
                            f"  {fkey[3]} -> {fkey[2]}.{fkey[4]}\n")
                    
                    self.relations_text.insert(tk.END, "\n")
                    
        except Exception as e:
            self.relations_text.insert(tk.END, f"Error loading relations: {str(e)}")
    
    def create_foreign_key(self):
        messagebox.showinfo("Foreign Key", 
            "Foreign keys must be defined when creating tables.\n\n" +
            "Example:\n" +
            "CREATE TABLE orders (\n" +
            "  id INTEGER PRIMARY KEY,\n" +
            "  customer_id INTEGER,\n" +
            "  FOREIGN KEY (customer_id) REFERENCES customers(id)\n" +
            ");")
    
    def change_page(self, delta):
        new_page = max(0, self.current_page + delta)
        if new_page != self.current_page:
            self.current_page = new_page
            self.load_table_data()
    
    def change_page_size(self):
        try:
            self.page_size = int(self.page_size_var.get())
            self.current_page = 0
            self.load_table_data()
        except:
            pass
    
    def show_context_menu(self, event):
        menu = tk.Menu(self.rootdbman3, tearoff=0, bg=self.bg_color, fg="#000000")
        menu.add_command(label="Open Table", command=self.load_table_data)
        menu.add_command(label="View Structure", command=self.view_table_structure)
        menu.add_command(label="Rename Table", command=self.rename_table)
        menu.add_separator()
        menu.add_command(label="Copy Table", command=self.copy_table)
        menu.add_command(label="Truncate Table", command=self.truncate_table)
        menu.add_command(label="Drop Table", command=self.drop_object)
        
        menu.post(event.x_rootdbman3, event.y_rootdbman3)
    
    def show_data_context_menu(self, event):
        menu = tk.Menu(self.rootdbman3, tearoff=0, bg=self.bg_color, fg="#000000")
        menu.add_command(label="Edit Record", command=self.update_record_dialog)
        menu.add_command(label="Duplicate Record", command=self.duplicate_record)
        menu.add_command(label="Delete Record", command=self.delete_record)
        menu.add_separator()
        menu.add_command(label="Copy Row", command=self.copy_row)
        menu.add_command(label="Export Selected", command=self.export_selected)
        
        menu.post(event.x_rootdbman3, event.y_rootdbman3)
    
    def copy_row(self):
        selection = self.data_tree.selection()
        if selection:
            values = self.data_tree.item(selection[0])['values']
            self.rootdbman3.clipboard_clear()
            self.rootdbman3.clipboard_append('\t'.join(str(v) for v in values))
            self.update_status("Row copied to clipboard")
    
    def export_selected(self):
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select records to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("JSON Files", "*.json")]
        )
        
        if file_path:
            try:
                data = []
                columns = [self.data_tree.heading(col)['text'] for col in self.data_tree['columns']]
                
                for item in selection:
                    data.append(self.data_tree.item(item)['values'])
                
                if file_path.endswith('.json'):
                    json_data = []
                    for row in data:
                        json_data.append(dict(zip(columns, row)))
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2)
                else:
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(columns)
                        writer.writerows(data)
                
                self.update_status(f"Exported {len(data)} selected records")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def rename_table(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        # Folosește simpledialog corect
        new_name = simpledialog.askstring(
            "Rename Table", 
            f"Enter new name for '{self.current_table}':",
            parent=self.rootdbman3
        )
        
        if new_name:
            new_name = new_name.strip()
            
            # Validează numele
            if not new_name.replace('_', '').isalnum():
                messagebox.showerror("Error", 
                    "Table name can only contain letters, numbers and underscores")
                return
            
            if new_name == self.current_table:
                messagebox.showinfo("Info", "New name is the same as the old name")
                return
            
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"ALTER TABLE {self.current_table} RENAME TO {new_name}")
                self.conn.commit()
                self.current_table = new_name
                self.refresh_tables_list()
                self.update_status(f"Renamed table to {new_name}")
                messagebox.showinfo("Success", f"Table renamed to '{new_name}'")
            except sqlite3.Error as e:
                messagebox.showerror("SQL Error", f"Failed to rename table:\n\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename table: {str(e)}")

    
    def copy_table(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        new_name = tk.simpledialog.askstring("Copy Table",
                                            f"Enter name for copy of '{self.current_table}':")
        if new_name:
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"CREATE TABLE {new_name} AS SELECT * FROM {self.current_table}")
                self.conn.commit()
                self.refresh_tables_list()
                self.update_status(f"Created table copy: {new_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy table: {str(e)}")
    
    def truncate_table(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        if messagebox.askyesno("Confirm", 
                              f"Delete all records from '{self.current_table}'?"):
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"DELETE FROM {self.current_table}")
                self.conn.commit()
                self.load_table_data()
                self.update_status(f"Truncated table {self.current_table}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to truncate table: {str(e)}")
    
    def duplicate_record(self):
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record first")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns_info = cursor.fetchall()
            
            values = list(self.data_tree.item(selection[0])['values'])
            
            # Remove primary key if auto-increment
            columns = []
            new_values = []
            for i, col in enumerate(columns_info):
                if not (bool(col[5]) and "AUTOINCREMENT" in str(col[2]).upper()):
                    columns.append(col[1])
                    new_values.append(values[i])
            
            placeholders = ", ".join(["?" for _ in new_values])
            sql = f"INSERT INTO {self.current_table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            cursor.execute(sql, new_values)
            self.conn.commit()
            self.load_table_data()
            self.update_status("Record duplicated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to duplicate record: {str(e)}")
    
    def show_bulk_edit(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title(f"Bulk Edit: {self.current_table}")
        dialog.geometry("600x450")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        content = tk.Frame(main_frame, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Obține informații despre coloane
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]
        # Stochează tipurile pentru validare
        column_types = {col[1]: col[2] for col in columns_info}
        
        tk.Label(content, text="Column to Update:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).pack(pady=4)
        
        column_combo = ttk.Combobox(content, values=columns, width=30,
                                    font=("MS Sans Serif", 8), state="readonly")
        column_combo.pack(pady=4)
        
        tk.Label(content, text="New Value:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).pack(pady=4)
        
        value_frame = tk.Frame(content, bg=self.bg_color)
        value_frame.pack(pady=4)
        
        value_entry = tk.Entry(value_frame, width=35, font=("MS Sans Serif", 8))
        value_entry.pack(side=tk.LEFT, padx=4)
        
        # Checkbox pentru NULL
        null_var = tk.BooleanVar(value=False)
        null_check = tk.Checkbutton(value_frame, text="Set to NULL", 
                                   variable=null_var, bg=self.bg_color,
                                   font=("MS Sans Serif", 8),
                                   command=lambda: value_entry.config(
                                       state='disabled' if null_var.get() else 'normal'))
        null_check.pack(side=tk.LEFT, padx=4)
        
        tk.Label(content, text="WHERE Condition (optional):", 
                font=("MS Sans Serif", 8, "bold"), bg=self.bg_color).pack(pady=4)
        
        condition_frame = self.create_win95_frame(content, sunken=True)
        condition_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        condition_entry = scrolledtext.ScrolledText(condition_frame, height=5,
                                                   font=("Fixedsys", 9),
                                                   bg="#ffffff", fg="#000000", bd=0)
        condition_entry.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        tk.Label(content, text="Examples: id > 10  |  status = 'active'  |  age BETWEEN 18 AND 65",
                font=("MS Sans Serif", 7), bg=self.bg_color, fg="#666666").pack(pady=2)
        
        # Preview frame
        preview_frame = tk.Frame(content, bg=self.bg_color)
        preview_frame.pack(fill=tk.X, pady=8)
        
        preview_label = tk.Label(preview_frame, text="", font=("MS Sans Serif", 7),
                                bg=self.bg_color, fg="#000080", wraplength=550)
        preview_label.pack()
        
        def update_preview():
            """Arată un preview al query-ului care va fi executat"""
            column = column_combo.get()
            if not column:
                preview_label.config(text="")
                return
            
            if null_var.get():
                value_display = "NULL"
            else:
                value = value_entry.get().strip()
                if not value:
                    preview_label.config(text="")
                    return
                
                # Verifică tipul coloanei pentru ghilimele
                col_type = column_types.get(column, "TEXT").upper()
                if "INT" in col_type or "REAL" in col_type or "NUMERIC" in col_type:
                    value_display = value
                else:
                    value_display = f"'{value}'"
            
            sql = f"UPDATE {self.current_table} SET {column} = {value_display}"
            
            condition = condition_entry.get("1.0", tk.END).strip()
            if condition:
                sql += f" WHERE {condition}"
            
            preview_label.config(text=f"SQL Preview: {sql}")
        
        # Update preview când se schimbă ceva
        column_combo.bind('<<ComboboxSelected>>', lambda e: update_preview())
        value_entry.bind('<KeyRelease>', lambda e: update_preview())
        null_var.trace('w', lambda *args: update_preview())
        condition_entry.bind('<KeyRelease>', lambda e: update_preview())
        
        def apply_bulk_edit():
            column = column_combo.get()
            condition = condition_entry.get("1.0", tk.END).strip()
            
            if not column:
                messagebox.showwarning("Warning", "Please select a column to update")
                return
            
            # Construiește query-ul corect
            if null_var.get():
                value = None
                sql = f"UPDATE {self.current_table} SET {column} = NULL"
            else:
                value = value_entry.get().strip()
                if not value:
                    messagebox.showwarning("Warning", "Please enter a value or check 'Set to NULL'")
                    return
                
                sql = f"UPDATE {self.current_table} SET {column} = ?"
            
            if condition:
                sql += f" WHERE {condition}"
            
            # Verifică câte rânduri vor fi afectate
            try:
                cursor = self.conn.cursor()
                count_sql = f"SELECT COUNT(*) FROM {self.current_table}"
                if condition:
                    count_sql += f" WHERE {condition}"
                cursor.execute(count_sql)
                affected_count = cursor.fetchone()[0]
                
                if affected_count == 0:
                    messagebox.showinfo("Info", "No records match the condition")
                    return
                
                # Confirmă acțiunea
                confirm_msg = f"This will update {affected_count} record(s).\n\n"
                confirm_msg += f"Column: {column}\n"
                confirm_msg += f"New Value: {'NULL' if null_var.get() else value}\n"
                if condition:
                    confirm_msg += f"Condition: {condition}\n"
                confirm_msg += "\nContinue?"
                
                if not messagebox.askyesno("Confirm Bulk Edit", confirm_msg):
                    return
                
                # Execută update-ul
                if null_var.get():
                    cursor.execute(sql)
                else:
                    cursor.execute(sql, (value,))
                
                self.conn.commit()
                self.load_table_data()
                self.update_status(f"Updated {cursor.rowcount} records")
                messagebox.showinfo("Success", f"Successfully updated {cursor.rowcount} records")
                dialog.destroy()
                
            except sqlite3.Error as e:
                messagebox.showerror("SQL Error", f"Failed to update:\n\n{str(e)}\n\nCheck your WHERE condition syntax.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")
        
        btn_frame = tk.Frame(content, bg=self.bg_color)
        btn_frame.pack(pady=8)
        
        self.create_win95_button(btn_frame, "Apply", apply_bulk_edit, 15).pack(side=tk.LEFT, padx=4)
        self.create_win95_button(btn_frame, "Cancel", dialog.destroy, 15).pack(side=tk.LEFT, padx=4)


    def show_advanced_filter(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title("Advanced Filter")
        dialog.geometry("700x500")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        content = tk.Frame(main_frame, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        tk.Label(content, text="Build Complex Filter", 
                font=("MS Sans Serif", 10, "bold"), bg=self.bg_color).pack(pady=8)
        
        tk.Label(content, text="WHERE Clause:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).pack(pady=4)
        
        text_frame = self.create_win95_frame(content, sunken=True)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        where_text = scrolledtext.ScrolledText(
            text_frame,
            height=10,
            font=("Fixedsys", 9),
            bg="#ffffff",
            fg="#000000",
            bd=0
        )
        where_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        examples = tk.Label(content, 
            text="Examples:\n" +
                 "age > 18 AND city = 'New York'\n" +
                 "salary BETWEEN 50000 AND 100000\n" +
                 "name LIKE '%Smith%' OR email LIKE '%@gmail.com'",
            font=("MS Sans Serif", 7),
            bg=self.bg_color,
            fg="#666666",
            justify=tk.LEFT)
        examples.pack(pady=8)
        
        def apply_filter():
            where_clause = where_text.get("1.0", tk.END).strip()
            if where_clause:
                self.apply_advanced_filter(where_clause)
                dialog.destroy()
        
        btn_frame = tk.Frame(content, bg=self.bg_color)
        btn_frame.pack(pady=8)
        
        self.create_win95_button(btn_frame, "Apply Filter", apply_filter, 15).pack(side=tk.LEFT, padx=4)
        self.create_win95_button(btn_frame, "Cancel", dialog.destroy, 15).pack(side=tk.LEFT, padx=4)
    
    def apply_advanced_filter(self, where_clause):
        if not self.conn or not self.current_table:
            return
        
        try:
            cursor = self.conn.cursor()
            sql = f"SELECT * FROM {self.current_table} WHERE {where_clause}"
            cursor.execute(sql)
            
            # Clear existing data
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            rows = cursor.fetchall()
            for row in rows:
                self.data_tree.insert('', tk.END, values=row)
            
            self.record_count_label.config(text=f"Records: {len(rows)}")
            self.update_status(f"Filter applied: {len(rows)} records found")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid filter: {str(e)}")
    
    def apply_sort(self):
        if not self.current_table:
            return
        
        column = self.sort_column.get()
        order = self.sort_order.get()
        
        if not column:
            messagebox.showwarning("Warning", "Please select a column to sort")
            return
        
        try:
            cursor = self.conn.cursor()
            sql = f"SELECT * FROM {self.current_table} ORDER BY {column} {order}"
            cursor.execute(sql)
            
            # Clear and reload
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            rows = cursor.fetchall()
            for row in rows:
                self.data_tree.insert('', tk.END, values=row)
            
            self.update_status(f"Sorted by {column} {order}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sort: {str(e)}")
    
    def clear_filter(self):
        self.search_entry.delete(0, tk.END)
        self.load_table_data()
    
    def show_find_replace(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title("Find & Replace")
        dialog.geometry("600x400")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        content = tk.Frame(main_frame, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        tk.Label(content, text="Column:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).pack(pady=4)
        column_combo = ttk.Combobox(content, values=columns, width=30,
                                    font=("MS Sans Serif", 8), state="readonly")
        column_combo.pack(pady=4)
        
        tk.Label(content, text="Find:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).pack(pady=4)
        find_entry = tk.Entry(content, width=40, font=("MS Sans Serif", 8))
        find_entry.pack(pady=4)
        
        tk.Label(content, text="Replace with:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).pack(pady=4)
        replace_entry = tk.Entry(content, width=40, font=("MS Sans Serif", 8))
        replace_entry.pack(pady=4)
        
        case_var = tk.BooleanVar(value=False)
        tk.Checkbutton(content, text="Case sensitive", variable=case_var,
                      bg=self.bg_color, font=("MS Sans Serif", 8)).pack(pady=4)
        
        result_label = tk.Label(content, text="", font=("MS Sans Serif", 8),
                               bg=self.bg_color, fg="#000080")
        result_label.pack(pady=8)
        
        def find_matches():
            column = column_combo.get()
            find_text = find_entry.get()
            
            if not column or not find_text:
                messagebox.showwarning("Warning", "Please fill in required fields")
                return
            
            try:
                cursor = self.conn.cursor()
                if case_var.get():
                    sql = f"SELECT COUNT(*) FROM {self.current_table} WHERE {column} LIKE ?"
                else:
                    sql = f"SELECT COUNT(*) FROM {self.current_table} WHERE LOWER({column}) LIKE LOWER(?)"
                
                cursor.execute(sql, (f"%{find_text}%",))
                count = cursor.fetchone()[0]
                result_label.config(text=f"Found {count} matches")
            except Exception as e:
                messagebox.showerror("Error", f"Search failed: {str(e)}")
        
        def replace_all():
            column = column_combo.get()
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            
            if not column or not find_text:
                messagebox.showwarning("Warning", "Please fill in required fields")
                return
            
            if not messagebox.askyesno("Confirm", "Replace all matches?"):
                return
            
            try:
                cursor = self.conn.cursor()
                sql = f"UPDATE {self.current_table} SET {column} = REPLACE({column}, ?, ?)"
                cursor.execute(sql, (find_text, replace_text))
                self.conn.commit()
                self.load_table_data()
                messagebox.showinfo("Success", f"Replaced in {cursor.rowcount} records")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Replace failed: {str(e)}")
        
        btn_frame = tk.Frame(content, bg=self.bg_color)
        btn_frame.pack(pady=8)
        
        self.create_win95_button(btn_frame, "Find", find_matches, 12).pack(side=tk.LEFT, padx=4)
        self.create_win95_button(btn_frame, "Replace All", replace_all, 12).pack(side=tk.LEFT, padx=4)
    
    def show_data_generator(self):
        messagebox.showinfo("Data Generator",
            "Data Generator allows you to create test data.\n\n" +
            "Features:\n" +
            "- Generate random names, emails, dates\n" +
            "- Custom data patterns\n" +
            "- Bulk data creation\n\n" +
            "This feature is coming in the next update!")
    
    def compare_schemas(self):
        file_path = filedialog.askopenfilename(
            title="Select database to compare",
            filetypes=[("SQLite Database", "*.db")]
        )
        
        if not file_path or not self.conn:
            return
        
        try:
            other_conn = sqlite3.connect(file_path)
            other_cursor = other_conn.cursor()
            
            dialog = tk.Toplevel(self.rootdbman3)
            dialog.title("Schema Comparison")
            dialog.geometry("800x600")
            dialog.configure(bg=self.bg_color)
            
            main_frame = self.create_win95_frame(dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            
            text_frame = self.create_win95_frame(main_frame, sunken=True)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
            
            text = scrolledtext.ScrolledText(text_frame, font=("Fixedsys", 9),
                                            bg="#ffffff", fg="#000000", bd=0)
            text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            text.insert(tk.END, "SCHEMA COMPARISON\n")
            text.insert(tk.END, "=" * 80 + "\n\n")
            text.insert(tk.END, f"Database 1: {os.path.basename(self.db_path)}\n")
            text.insert(tk.END, f"Database 2: {os.path.basename(file_path)}\n\n")
            
            # Get tables from both databases
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables1 = set(t[0] for t in cursor.fetchall())
            
            other_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables2 = set(t[0] for t in other_cursor.fetchall())
            
            # Tables only in DB1
            only_in_1 = tables1 - tables2
            if only_in_1:
                text.insert(tk.END, f"Tables only in {os.path.basename(self.db_path)}:\n")
                for table in only_in_1:
                    text.insert(tk.END, f"  - {table}\n")
                text.insert(tk.END, "\n")
            
            # Tables only in DB2
            only_in_2 = tables2 - tables1
            if only_in_2:
                text.insert(tk.END, f"Tables only in {os.path.basename(file_path)}:\n")
                for table in only_in_2:
                    text.insert(tk.END, f"  - {table}\n")
                text.insert(tk.END, "\n")
            
            # Common tables
            common = tables1 & tables2
            if common:
                text.insert(tk.END, "Common tables:\n")
                for table in common:
                    text.insert(tk.END, f"  - {table}\n")
            
            other_conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Comparison failed: {str(e)}")
    
    def integrity_check(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchall()
            
            if result[0][0] == "ok":
                messagebox.showinfo("Integrity Check", "Database integrity: OK ✓")
            else:
                msg = "Database integrity issues found:\n\n"
                msg += "\n".join([r[0] for r in result])
                messagebox.showwarning("Integrity Check", msg)
                
            self.update_status("Integrity check completed")
        except Exception as e:
            messagebox.showerror("Error", f"Integrity check failed: {str(e)}")
    
    def optimize_database(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        if messagebox.askyesno("Optimize", "Optimize database? This may take a while."):
            try:
                cursor = self.conn.cursor()
                cursor.execute("VACUUM")
                cursor.execute("ANALYZE")
                self.conn.commit()
                messagebox.showinfo("Success", "Database optimized successfully")
                self.update_status("Database optimized")
            except Exception as e:
                messagebox.showerror("Error", f"Optimization failed: {str(e)}")
    
    def compact_database(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        original_size = os.path.getsize(self.db_path)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("VACUUM")
            self.conn.commit()
            
            new_size = os.path.getsize(self.db_path)
            saved = original_size - new_size
            
            messagebox.showinfo("Success",
                f"Database compacted successfully\n\n" +
                f"Original size: {original_size / 1024:.2f} KB\n" +
                f"New size: {new_size / 1024:.2f} KB\n" +
                f"Space saved: {saved / 1024:.2f} KB")
            
            self.update_status("Database compacted")
        except Exception as e:
            messagebox.showerror("Error", f"Compaction failed: {str(e)}")
    
    def clone_database(self):
        if not self.conn or not self.db_path:
            messagebox.showwarning("Warning", "No database is currently open")
            return
        
        clone_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")],
            initialfile=f"clone_{os.path.basename(self.db_path)}"
        )
        
        if clone_path:
            try:
                shutil.copy2(self.db_path, clone_path)
                self.update_status(f"Database cloned to {os.path.basename(clone_path)}")
                messagebox.showinfo("Success", "Database cloned successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clone: {str(e)}")
    
    def show_query_history(self):
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title("Query History")
        dialog.geometry("800x600")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        text_frame = self.create_win95_frame(main_frame, sunken=True)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        text = scrolledtext.ScrolledText(text_frame, font=("Fixedsys", 9),
                                        bg="#ffffff", fg="#000000", bd=0)
        text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        text.insert(tk.END, "QUERY HISTORY\n")
        text.insert(tk.END, "=" * 80 + "\n\n")
        
        for i, query in enumerate(reversed(self.query_history[-50:]), 1):
            text.insert(tk.END, f"{i}. {query}\n\n")
        
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=4, pady=4)
        
        self.create_win95_button(btn_frame, "Clear History",
                                lambda: self.query_history.clear(), 15).pack(side=tk.LEFT, padx=4)
    
    def show_sql_reference(self):
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title("SQL Reference")
        dialog.geometry("700x600")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        text_frame = self.create_win95_frame(main_frame, sunken=True)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        text = scrolledtext.ScrolledText(text_frame, font=("Fixedsys", 9),
                                        bg="#ffffff", fg="#000000", bd=0)
        text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        reference = """SQL QUICK REFERENCE
================================================================================

SELECT
------
SELECT column1, column2 FROM table_name;
SELECT * FROM table_name WHERE condition;
SELECT * FROM table_name ORDER BY column ASC/DESC;
SELECT * FROM table_name LIMIT 10 OFFSET 20;

INSERT
------
INSERT INTO table_name (column1, column2) VALUES (value1, value2);
INSERT INTO table_name VALUES (value1, value2, value3);

UPDATE
------
UPDATE table_name SET column1 = value1 WHERE condition;

DELETE
------
DELETE FROM table_name WHERE condition;

CREATE TABLE
------------
CREATE TABLE table_name (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    age INTEGER CHECK(age >= 0),
    created_date TEXT DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE
-----------
ALTER TABLE table_name ADD COLUMN column_name TYPE;
ALTER TABLE table_name RENAME TO new_name;
ALTER TABLE table_name RENAME COLUMN old_name TO new_name;

DROP TABLE
----------
DROP TABLE table_name;
DROP TABLE IF EXISTS table_name;

JOINS
-----
SELECT * FROM table1 INNER JOIN table2 ON table1.id = table2.foreign_id;
SELECT * FROM table1 LEFT JOIN table2 ON table1.id = table2.foreign_id;

AGGREGATE FUNCTIONS
-------------------
SELECT COUNT(*) FROM table_name;
SELECT AVG(column) FROM table_name;
SELECT SUM(column) FROM table_name;
SELECT MIN(column), MAX(column) FROM table_name;

GROUP BY
--------
SELECT column, COUNT(*) FROM table_name GROUP BY column;
SELECT column, AVG(value) FROM table_name GROUP BY column HAVING AVG(value) > 10;

INDEXES
-------
CREATE INDEX index_name ON table_name (column);
CREATE UNIQUE INDEX index_name ON table_name (column);
DROP INDEX index_name;

VIEWS
-----
CREATE VIEW view_name AS SELECT column FROM table_name WHERE condition;
DROP VIEW view_name;

TRANSACTIONS
------------
BEGIN TRANSACTION;
COMMIT;
ROLLBACK;

OPERATORS
---------
=, !=, <, >, <=, >=
LIKE '%pattern%'
IN (value1, value2)
BETWEEN value1 AND value2
IS NULL, IS NOT NULL
AND, OR, NOT
"""
        text.insert(tk.END, reference)
        text.config(state=tk.DISABLED)
    
    def show_shortcuts(self):
        shortcuts = """KEYBOARD SHORTCUTS
================================================================================

Database Operations:
Ctrl+N          New Database
Ctrl+O          Open Database
Ctrl+W          Close Database
Ctrl+S          Save Changes

View Operations:
F5              Execute SQL / Refresh
Ctrl+R          Refresh Data
Ctrl+F          Find & Replace

Data Operations:
Insert          Insert New Record
Delete          Delete Selected Record
Enter           Edit Selected Record

Navigation:
Tab             Move to next field
Shift+Tab       Move to previous field
Arrow Keys      Navigate records

Other:
Ctrl+C          Copy selected data
Alt+F4          Exit application
"""
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def toggle_auto_refresh(self):
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        def refresh_loop():
            while self.auto_refresh:
                self.load_table_data()
                threading.Event().wait(5)  # Refresh every 5 seconds
        
        thread = threading.Thread(target=refresh_loop, daemon=True)
        thread.start()
    
    def stop_auto_refresh(self):
        self.auto_refresh = False
    
    def save_changes(self):
        if self.conn:
            self.conn.commit()
            self.update_status("Changes saved")
            messagebox.showinfo("Success", "All changes saved successfully")
        else:
            messagebox.showwarning("Warning", "No database is open")
    
    def update_status(self, message):
        self.status_bar.config(text=message)
        self.rootdbman3.update_idletasks()
    
    def on_table_select(self, event):
        selection = self.tables_listbox.curselection()
        if selection:
            self.current_table = self.tables_listbox.get(selection[0])
            self.table_label.config(text=f"Table: {self.current_table}")
            self.load_relations()
    
    def refresh_objects_list(self):
        self.tables_listbox.delete(0, tk.END)
        
        if not self.conn:
            return
        
        try:
            cursor = self.conn.cursor()
            obj_type = self.object_type.get()
            
            if obj_type == "tables":
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            elif obj_type == "views":
                cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
            elif obj_type == "indexes":
                cursor.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")
            
            objects = cursor.fetchall()
            for obj in objects:
                self.tables_listbox.insert(tk.END, obj[0])
        except Exception as e:
            self.update_status(f"Error loading objects: {str(e)}")
    
    def refresh_tables_list(self):
        self.refresh_objects_list()
    
    def new_database(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                if self.conn:
                    self.conn.close()
                
                self.conn = sqlite3.connect(file_path)
                self.db_path = file_path
                self.rootdbman3.title(f"Advanced Database Manager Pro - {os.path.basename(file_path)}")
                self.add_to_recent(file_path)
                self.refresh_tables_list()
                self.update_status(f"Created new database: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "New database created successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create database: {str(e)}")
    
    def open_database(self):
        file_path = filedialog.askopenfilename(
            title="Open Database",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                if self.conn:
                    self.conn.close()
                
                self.conn = sqlite3.connect(file_path)
                self.db_path = file_path
                self.rootdbman3.title(f"Advanced Database Manager Pro - {os.path.basename(file_path)}")
                self.add_to_recent(file_path)
                self.refresh_tables_list()
                self.load_relations()
                self.update_status(f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open database: {str(e)}")
    
    def close_database(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.db_path = None
            self.current_table = None
            self.tables_listbox.delete(0, tk.END)
            
            # Clear data tree
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            self.table_label.config(text="No table selected")
            self.rootdbman3.title("Advanced Database Manager Pro")
            self.update_status("Database closed")
    
    def add_to_recent(self, file_path):
        if file_path in self.recent_databases:
            self.recent_databases.remove(file_path)
        
        self.recent_databases.insert(0, file_path)
        self.recent_databases = self.recent_databases[:10]  # Keep only 10 recent
        
        self.update_recent_menu()
        self.save_settings()
    
    def update_recent_menu(self):
        self.recent_menu.delete(0, tk.END)
        
        for path in self.recent_databases:
            if os.path.exists(path):
                self.recent_menu.add_command(
                    label=os.path.basename(path),
                    command=lambda p=path: self.open_recent(p)
                )
    
    def open_recent(self, file_path):
        try:
            if self.conn:
                self.conn.close()
            
            self.conn = sqlite3.connect(file_path)
            self.db_path = file_path
            self.rootdbman3.title(f"Advanced Database Manager Pro - {os.path.basename(file_path)}")
            self.refresh_tables_list()
            self.load_relations()
            self.update_status(f"Opened: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open database: {str(e)}")
            self.recent_databases.remove(file_path)
            self.update_recent_menu()
    
    def load_table_data(self):
        if not self.conn or not self.current_table:
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns_info = cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            # Update filter and sort combos
            self.filter_column['values'] = columns
            self.sort_column['values'] = columns
            
            # Get data with pagination
            offset = self.current_page * self.page_size
            cursor.execute(f"SELECT * FROM {self.current_table} LIMIT {self.page_size} OFFSET {offset}")
            rows = cursor.fetchall()
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM {self.current_table}")
            total_count = cursor.fetchone()[0]
            
            # Clear existing data
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            # Configure columns
            self.data_tree['columns'] = columns
            self.data_tree['show'] = 'headings'
            
            for col in columns:
                self.data_tree.heading(col, text=col)
                self.data_tree.column(col, width=100, anchor='w')
            
            # Insert data
            for row in rows:
                self.data_tree.insert('', tk.END, values=row)
            
            # Update UI
            total_pages = (total_count + self.page_size - 1) // self.page_size
            self.page_label.config(text=f"Page: {self.current_page + 1} of {total_pages}")
            self.record_count_label.config(text=f"Records: {total_count}")
            self.table_label.config(text=f"Table: {self.current_table}")
            self.update_status(f"Loaded {len(rows)} records from {self.current_table}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def filter_data(self):
        if not self.conn or not self.current_table:
            return
        
        search_text = self.search_entry.get().strip()
        column = self.filter_column.get()
        
        if not search_text:
            self.load_table_data()
            return
        
        try:
            cursor = self.conn.cursor()
            
            if column:
                sql = f"SELECT * FROM {self.current_table} WHERE {column} LIKE ?"
                cursor.execute(sql, (f"%{search_text}%",))
            else:
                # Search in all columns
                cursor.execute(f"PRAGMA table_info({self.current_table})")
                columns = [col[1] for col in cursor.fetchall()]
                
                conditions = " OR ".join([f"{col} LIKE ?" for col in columns])
                sql = f"SELECT * FROM {self.current_table} WHERE {conditions}"
                cursor.execute(sql, tuple([f"%{search_text}%"] * len(columns)))
            
            # Clear and display results
            for item in self.data_tree.get_children():
                self.data_tree.delete(item)
            
            rows = cursor.fetchall()
            for row in rows:
                self.data_tree.insert('', tk.END, values=row)
            
            self.record_count_label.config(text=f"Records: {len(rows)}")
            self.update_status(f"Found {len(rows)} matching records")
            
        except Exception as e:
            messagebox.showerror("Error", f"Filter failed: {str(e)}")
    
    def create_table_dialog(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title("Create New Table")
        dialog.geometry("700x600")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        content = tk.Frame(main_frame, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        tk.Label(content, text="Table Name:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).grid(row=0, column=0, sticky="w", padx=4, pady=4)
        
        table_name_entry = tk.Entry(content, width=40, font=("MS Sans Serif", 8))
        table_name_entry.grid(row=0, column=1, columnspan=2, sticky="we", padx=4, pady=4)
        
        tk.Label(content, text="Columns:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).grid(row=1, column=0, sticky="nw", padx=4, pady=4)
        
        columns_frame = self.create_win95_frame(content, sunken=True)
        columns_frame.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=4, pady=4)
        
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(1, weight=1)
        
        columns_text = scrolledtext.ScrolledText(
            columns_frame,
            height=15,
            font=("Fixedsys", 9),
            bg="#ffffff",
            fg="#000000",
            bd=0
        )
        columns_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Example text
        example = """id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
email TEXT UNIQUE,
age INTEGER,
created_date TEXT DEFAULT CURRENT_TIMESTAMP"""
        
        columns_text.insert("1.0", example)
        
        tk.Label(content, 
                text="Define one column per line: column_name TYPE [constraints]",
                font=("MS Sans Serif", 7),
                bg=self.bg_color,
                fg="#666666").grid(row=2, column=1, columnspan=2, sticky="w", padx=4, pady=4)
        
        def create_table():
            table_name = table_name_entry.get().strip()
            columns_def = columns_text.get("1.0", tk.END).strip()
            
            if not table_name or not columns_def:
                messagebox.showwarning("Warning", "Please fill in all fields")
                return
            
            try:
                sql = f"CREATE TABLE {table_name} (\n{columns_def}\n)"
                cursor = self.conn.cursor()
                cursor.execute(sql)
                self.conn.commit()
                self.refresh_tables_list()
                self.update_status(f"Created table: {table_name}")
                messagebox.showinfo("Success", f"Table '{table_name}' created successfully")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create table: {str(e)}")
        
        btn_frame = tk.Frame(content, bg=self.bg_color)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=8)
        
        self.create_win95_button(btn_frame, "Create Table", create_table, 15).pack(side=tk.LEFT, padx=4)
        self.create_win95_button(btn_frame, "Cancel", dialog.destroy, 15).pack(side=tk.LEFT, padx=4)
    
    def create_view_dialog(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title("Create View")
        dialog.geometry("700x550")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        content = tk.Frame(main_frame, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        tk.Label(content, text="View Name:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).pack(pady=4)
        
        view_name_entry = tk.Entry(content, width=40, font=("MS Sans Serif", 8))
        view_name_entry.pack(pady=4)
        
        tk.Label(content, text="SELECT Query:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).pack(pady=4)
        
        query_frame = self.create_win95_frame(content, sunken=True)
        query_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        query_text = scrolledtext.ScrolledText(
            query_frame,
            height=12,
            font=("Fixedsys", 9),
            bg="#ffffff",
            fg="#000000",
            bd=0
        )
        query_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Adaugă un exemplu de query
        example = "SELECT column1, column2\nFROM table_name\nWHERE condition"
        query_text.insert("1.0", example)
        query_text.tag_add("example", "1.0", "end")
        query_text.tag_config("example", foreground="#888888")
        
        # Șterge exemplul când utilizatorul începe să scrie
        def clear_example(event):
            current = query_text.get("1.0", "end-1c")
            if current.strip() == example.strip():
                query_text.delete("1.0", tk.END)
                query_text.tag_remove("example", "1.0", "end")
        
        query_text.bind("<FocusIn>", clear_example)
        
        # Label pentru erori/succes
        status_label = tk.Label(content, text="", font=("MS Sans Serif", 7),
                               bg=self.bg_color, fg="#cc0000", wraplength=650)
        status_label.pack(pady=4)
        
        tk.Label(content, 
                text="Note: Write only the SELECT query, without 'CREATE VIEW ... AS'",
                font=("MS Sans Serif", 7), bg=self.bg_color, fg="#666666").pack(pady=2)
        
        def validate_query():
            """Validează query-ul înainte de a crea view-ul"""
            query = query_text.get("1.0", tk.END).strip()
            
            if not query or query == example.strip():
                status_label.config(text="⚠ Please enter a SELECT query", fg="#cc0000")
                return False
            
            # Verifică dacă începe cu SELECT
            if not query.upper().startswith("SELECT"):
                status_label.config(text="⚠ Query must start with SELECT", fg="#cc0000")
                return False
            
            # Încearcă să execute query-ul pentru validare
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"EXPLAIN {query}")
                status_label.config(text="✓ Query is valid", fg="#008000")
                return True
            except sqlite3.Error as e:
                status_label.config(text=f"⚠ SQL Error: {str(e)}", fg="#cc0000")
                return False
        
        def create_view():
            view_name = view_name_entry.get().strip()
            query = query_text.get("1.0", tk.END).strip()
            
            if not view_name:
                messagebox.showwarning("Warning", "Please enter a view name")
                view_name_entry.focus()
                return
            
            if not query or query == example.strip():
                messagebox.showwarning("Warning", "Please enter a SELECT query")
                query_text.focus()
                return
            
            # Validează numele view-ului
            if not view_name.replace('_', '').isalnum():
                messagebox.showerror("Error", 
                    "View name can only contain letters, numbers and underscores")
                return
            
            # Verifică dacă view-ul există deja
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name=?", 
                              (view_name,))
                if cursor.fetchone():
                    if not messagebox.askyesno("View Exists", 
                        f"View '{view_name}' already exists. Replace it?"):
                        return
                    cursor.execute(f"DROP VIEW {view_name}")
            except:
                pass
            
            # Creează view-ul
            try:
                sql = f"CREATE VIEW {view_name} AS {query}"
                cursor = self.conn.cursor()
                cursor.execute(sql)
                self.conn.commit()
                
                self.refresh_objects_list()
                self.update_status(f"Created view: {view_name}")
                messagebox.showinfo("Success", 
                    f"View '{view_name}' created successfully!\n\n"
                    f"You can now find it in the 'Views' tab.")
                dialog.destroy()
                
            except sqlite3.Error as e:
                error_msg = str(e)
                messagebox.showerror("SQL Error", 
                    f"Failed to create view:\n\n{error_msg}\n\n"
                    f"Please check your SELECT query syntax.")
                status_label.config(text=f"⚠ {error_msg}", fg="#cc0000")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create view: {str(e)}")
        
        btn_frame = tk.Frame(content, bg=self.bg_color)
        btn_frame.pack(pady=8)
        
        self.create_win95_button(btn_frame, "Validate Query", 
                                validate_query, 15).pack(side=tk.LEFT, padx=4)
        self.create_win95_button(btn_frame, "Create View", 
                                create_view, 15).pack(side=tk.LEFT, padx=4)
        self.create_win95_button(btn_frame, "Cancel", 
                                dialog.destroy, 15).pack(side=tk.LEFT, padx=4)
        
        # Bind F5 pentru validare rapidă
        dialog.bind('<F5>', lambda e: validate_query())


    
    def drop_object(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select an object first")
            return
        
        obj_type = self.object_type.get().rstrip('s')  # Remove trailing 's'
        
        if messagebox.askyesno("Confirm", 
                              f"Drop {obj_type} '{self.current_table}'?\n\nThis action cannot be undone!"):
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"DROP {obj_type.upper()} {self.current_table}")
                self.conn.commit()
                self.refresh_objects_list()
                self.current_table = None
                self.update_status(f"Dropped {obj_type}: {self.current_table}")
                
                # Clear data view
                for item in self.data_tree.get_children():
                    self.data_tree.delete(item)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to drop {obj_type}: {str(e)}")
    
    def view_table_structure(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title(f"Structure: {self.current_table}")
        dialog.geometry("800x600")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        text_frame = self.create_win95_frame(main_frame, sunken=True)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        text = scrolledtext.ScrolledText(text_frame, font=("Fixedsys", 9),
                                        bg="#ffffff", fg="#000000", bd=0)
        text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        try:
            cursor = self.conn.cursor()
            
            # Table info
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = cursor.fetchall()
            
            text.insert(tk.END, f"TABLE: {self.current_table}\n")
            text.insert(tk.END, "=" * 80 + "\n\n")
            text.insert(tk.END, "COLUMNS:\n")
            text.insert(tk.END, "-" * 80 + "\n")
            text.insert(tk.END, f"{'Name':<20} {'Type':<15} {'NotNull':<10} {'Default':<15} {'PK'}\n")
            text.insert(tk.END, "-" * 80 + "\n")
            
            for col in columns:
                text.insert(tk.END, 
                    f"{col[1]:<20} {col[2]:<15} {str(bool(col[3])):<10} {str(col[4] or ''):<15} {bool(col[5])}\n")
            
            # Indexes
            text.insert(tk.END, "\n\nINDEXES:\n")
            text.insert(tk.END, "-" * 80 + "\n")
            cursor.execute(f"PRAGMA index_list({self.current_table})")
            indexes = cursor.fetchall()
            
            if indexes:
                for idx in indexes:
                    text.insert(tk.END, f"Name: {idx[1]}, Unique: {bool(idx[2])}\n")
            else:
                text.insert(tk.END, "No indexes found\n")
            
            # Foreign Keys
            text.insert(tk.END, "\n\nFOREIGN KEYS:\n")
            text.insert(tk.END, "-" * 80 + "\n")
            cursor.execute(f"PRAGMA foreign_key_list({self.current_table})")
            fkeys = cursor.fetchall()
            
            if fkeys:
                for fk in fkeys:
                    text.insert(tk.END, f"{fk[3]} -> {fk[2]}.{fk[4]}\n")
            else:
                text.insert(tk.END, "No foreign keys found\n")
            
            # CREATE statement
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", 
                          (self.current_table,))
            create_sql = cursor.fetchone()
            
            if create_sql:
                text.insert(tk.END, "\n\nCREATE STATEMENT:\n")
                text.insert(tk.END, "-" * 80 + "\n")
                text.insert(tk.END, create_sql[0] + ";\n")
            
            text.config(state=tk.DISABLED)
            
        except Exception as e:
            text.insert(tk.END, f"Error: {str(e)}")
    
    def insert_record_dialog(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title(f"Insert Record: {self.current_table}")
        dialog.geometry("600x500")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        scrollbar.pack(side="right", fill="y")
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = cursor.fetchall()
            
            entries = {}
            
            for i, col in enumerate(columns):
                col_name = col[1]
                col_type = col[2]
                not_null = bool(col[3])
                default_val = col[4]
                is_pk = bool(col[5])
                
                frame = tk.Frame(scrollable_frame, bg=self.bg_color)
                frame.pack(fill=tk.X, padx=4, pady=4)
                
                label_text = col_name
                if not_null:
                    label_text += " *"
                if is_pk:
                    label_text += " (PK)"
                
                tk.Label(frame, text=label_text, font=("MS Sans Serif", 8),
                        bg=self.bg_color, width=20, anchor="w").pack(side=tk.LEFT, padx=4)
                
                entry = tk.Entry(frame, width=40, font=("MS Sans Serif", 8))
                entry.pack(side=tk.LEFT, padx=4)
                
                if default_val:
                    entry.insert(0, str(default_val))
                
                entries[col_name] = entry
                
                tk.Label(frame, text=col_type, font=("MS Sans Serif", 7),
                        bg=self.bg_color, fg="#666666").pack(side=tk.LEFT, padx=4)
            
            def insert_record():
                values = []
                columns_list = []
                
                for col in columns:
                    col_name = col[1]
                    value = entries[col_name].get().strip()
                    
                    if value or not bool(col[5]):  # Include if has value or not PK
                        columns_list.append(col_name)
                        values.append(value if value else None)
                
                try:
                    placeholders = ", ".join(["?" for _ in values])
                    sql = f"INSERT INTO {self.current_table} ({', '.join(columns_list)}) VALUES ({placeholders})"
                    
                    cursor = self.conn.cursor()
                    cursor.execute(sql, values)
                    self.conn.commit()
                    self.load_table_data()
                    self.update_status("Record inserted successfully")
                    messagebox.showinfo("Success", "Record inserted successfully")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to insert record: {str(e)}")
            
            btn_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
            btn_frame.pack(pady=8)
            
            self.create_win95_button(btn_frame, "Insert", insert_record, 15).pack(side=tk.LEFT, padx=4)
            self.create_win95_button(btn_frame, "Cancel", dialog.destroy, 15).pack(side=tk.LEFT, padx=4)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table structure: {str(e)}")
    
    def update_record_dialog(self):
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record first")
            return
        
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title(f"Update Record: {self.current_table}")
        dialog.geometry("600x500")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        scrollbar.pack(side="right", fill="y")
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = cursor.fetchall()
            
            current_values = self.data_tree.item(selection[0])['values']
            
            entries = {}
            
            for i, col in enumerate(columns):
                col_name = col[1]
                col_type = col[2]
                is_pk = bool(col[5])
                
                frame = tk.Frame(scrollable_frame, bg=self.bg_color)
                frame.pack(fill=tk.X, padx=4, pady=4)
                
                label_text = col_name
                if is_pk:
                    label_text += " (PK)"
                
                tk.Label(frame, text=label_text, font=("MS Sans Serif", 8),
                        bg=self.bg_color, width=20, anchor="w").pack(side=tk.LEFT, padx=4)
                
                entry = tk.Entry(frame, width=40, font=("MS Sans Serif", 8))
                entry.pack(side=tk.LEFT, padx=4)
                entry.insert(0, str(current_values[i]))
                
                if is_pk:
                    entry.config(state="readonly")
                
                entries[col_name] = entry
                
                tk.Label(frame, text=col_type, font=("MS Sans Serif", 7),
                        bg=self.bg_color, fg="#666666").pack(side=tk.LEFT, padx=4)
            
            def update_record():
                set_clause = []
                values = []
                pk_column = None
                pk_value = None
                
                for col in columns:
                    col_name = col[1]
                    value = entries[col_name].get().strip()
                    
                    if bool(col[5]):  # Primary key
                        pk_column = col_name
                        pk_value = value
                    else:
                        set_clause.append(f"{col_name} = ?")
                        values.append(value if value else None)
                
                if not pk_column:
                    messagebox.showerror("Error", "No primary key found")
                    return
                
                try:
                    sql = f"UPDATE {self.current_table} SET {', '.join(set_clause)} WHERE {pk_column} = ?"
                    values.append(pk_value)
                    
                    cursor = self.conn.cursor()
                    cursor.execute(sql, values)
                    self.conn.commit()
                    self.load_table_data()
                    self.update_status("Record updated successfully")
                    messagebox.showinfo("Success", "Record updated successfully")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update record: {str(e)}")
            
            btn_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
            btn_frame.pack(pady=8)
            
            self.create_win95_button(btn_frame, "Update", update_record, 15).pack(side=tk.LEFT, padx=4)
            self.create_win95_button(btn_frame, "Cancel", dialog.destroy, 15).pack(side=tk.LEFT, padx=4)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load record: {str(e)}")
    
    def delete_record(self):
        selection = self.data_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a record first")
            return
        
        if not messagebox.askyesno("Confirm", "Delete selected record?"):
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = cursor.fetchall()
            
            # Find primary key
            pk_column = None
            pk_index = None
            for i, col in enumerate(columns):
                if bool(col[5]):
                    pk_column = col[1]
                    pk_index = i
                    break
            
            if not pk_column:
                messagebox.showerror("Error", "No primary key found")
                return
            
            values = self.data_tree.item(selection[0])['values']
            pk_value = values[pk_index]
            
            sql = f"DELETE FROM {self.current_table} WHERE {pk_column} = ?"
            cursor.execute(sql, (pk_value,))
            self.conn.commit()
            self.load_table_data()
            self.update_status("Record deleted successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record: {str(e)}")
    
    def show_sql_executor(self):
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title("SQL Executor")
        dialog.geometry("900x700")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # SQL Input
        input_frame = self.create_win95_frame(main_frame)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        tk.Label(input_frame, text="SQL Query:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).pack(anchor="w", padx=4, pady=4)
        
        text_frame = self.create_win95_frame(input_frame, sunken=True)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        sql_text = scrolledtext.ScrolledText(
            text_frame,
            height=10,
            font=("Fixedsys", 9),
            bg="#ffffff",
            fg="#000000",
            bd=0
        )
        sql_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=4, pady=4)
        
        def execute_query():
            query = sql_text.get("1.0", tk.END).strip()
            if not query:
                messagebox.showwarning("Warning", "Please enter a query")
                return
            
            try:
                cursor = self.conn.cursor()
                cursor.execute(query)
                
                # Add to history
                self.query_history.append(query)
                
                if query.strip().upper().startswith("SELECT"):
                    # Display results
                    results = cursor.fetchall()
                    column_names = [description[0] for description in cursor.description]
                    
                    # Clear previous results
                    for item in results_tree.get_children():
                        results_tree.delete(item)
                    
                    # Configure columns
                    results_tree['columns'] = column_names
                    results_tree['show'] = 'headings'
                    
                    for col in column_names:
                        results_tree.heading(col, text=col)
                        results_tree.column(col, width=100)
                    
                    # Insert data
                    for row in results:
                        results_tree.insert('', tk.END, values=row)
                    
                    result_label.config(text=f"{len(results)} rows returned")
                else:
                    self.conn.commit()
                    result_label.config(text=f"Query executed successfully. {cursor.rowcount} rows affected")
                    self.refresh_tables_list()
                
            except Exception as e:
                messagebox.showerror("Error", f"Query failed: {str(e)}")
                result_label.config(text=f"Error: {str(e)}")
        
        def clear_query():
            sql_text.delete("1.0", tk.END)
            for item in results_tree.get_children():
                results_tree.delete(item)
            result_label.config(text="")
        
        self.create_win95_button(btn_frame, "Execute (F5)", execute_query, 15).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(btn_frame, "Clear", clear_query, 10).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(btn_frame, "Format", lambda: self.format_sql(sql_text), 10).pack(side=tk.LEFT, padx=2)
        self.create_win95_button(btn_frame, "History", self.show_query_history, 10).pack(side=tk.LEFT, padx=2)
        
        dialog.bind('<F5>', lambda e: execute_query())
        
        # Results
        results_frame = self.create_win95_frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        tk.Label(results_frame, text="Results:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).pack(anchor="w", padx=4, pady=4)
        
        tree_frame = self.create_win95_frame(results_frame, sunken=True)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        tree_scroll_y = tk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        results_tree = ttk.Treeview(tree_frame,
                                   yscrollcommand=tree_scroll_y.set,
                                   xscrollcommand=tree_scroll_x.set)
        results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=results_tree.yview)
        tree_scroll_x.config(command=results_tree.xview)
        
        result_label = tk.Label(results_frame, text="", font=("MS Sans Serif", 8),
                               bg=self.bg_color, fg="#000080")
        result_label.pack(anchor="w", padx=4, pady=4)
    
    def format_sql(self, text_widget):
        """Basic SQL formatting"""
        sql = text_widget.get("1.0", tk.END).strip()
        
        # Simple formatting
        keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 
                   'INNER JOIN', 'ORDER BY', 'GROUP BY', 'HAVING', 'LIMIT', 
                   'INSERT INTO', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER']
        
        formatted = sql
        for keyword in keywords:
            formatted = re.sub(f'\\b{keyword}\\b', f'\n{keyword}', formatted, flags=re.IGNORECASE)
        
        formatted = formatted.strip()
        
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", formatted)
    
    def show_query_builder(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title("Query Builder")
        dialog.geometry("800x600")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        content = tk.Frame(main_frame, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Get tables
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        # Table selection
        tk.Label(content, text="Select Table:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).grid(row=0, column=0, sticky="w", padx=4, pady=4)
        
        table_combo = ttk.Combobox(content, values=tables, width=30,
                                   font=("MS Sans Serif", 8), state="readonly")
        table_combo.grid(row=0, column=1, sticky="we", padx=4, pady=4)
        
        # Columns selection
        tk.Label(content, text="Select Columns:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).grid(row=1, column=0, sticky="nw", padx=4, pady=4)
        
        columns_frame = self.create_win95_frame(content, sunken=True)
        columns_frame.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)
        
        columns_listbox = tk.Listbox(columns_frame, selectmode=tk.MULTIPLE,
                                     font=("MS Sans Serif", 8), bg="#ffffff",
                                     height=6)
        columns_listbox.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # WHERE clause
        tk.Label(content, text="WHERE Clause:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).grid(row=2, column=0, sticky="w", padx=4, pady=4)
        
        where_entry = tk.Entry(content, width=40, font=("MS Sans Serif", 8))
        where_entry.grid(row=2, column=1, sticky="we", padx=4, pady=4)
        
        # ORDER BY
        tk.Label(content, text="ORDER BY:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).grid(row=3, column=0, sticky="w", padx=4, pady=4)
        
        order_frame = tk.Frame(content, bg=self.bg_color)
        order_frame.grid(row=3, column=1, sticky="we", padx=4, pady=4)
        
        order_combo = ttk.Combobox(order_frame, width=20, font=("MS Sans Serif", 8))
        order_combo.pack(side=tk.LEFT, padx=4)
        
        order_dir = ttk.Combobox(order_frame, values=["ASC", "DESC"], width=8,
                                font=("MS Sans Serif", 8), state="readonly")
        order_dir.set("ASC")
        order_dir.pack(side=tk.LEFT, padx=4)
        
        # LIMIT
        tk.Label(content, text="LIMIT:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).grid(row=4, column=0, sticky="w", padx=4, pady=4)
        
        limit_entry = tk.Entry(content, width=10, font=("MS Sans Serif", 8))
        limit_entry.grid(row=4, column=1, sticky="w", padx=4, pady=4)
        
        # Generated query
        tk.Label(content, text="Generated Query:", font=("MS Sans Serif", 8, "bold"),
                bg=self.bg_color).grid(row=5, column=0, sticky="nw", padx=4, pady=4)
        
        query_frame = self.create_win95_frame(content, sunken=True)
        query_frame.grid(row=5, column=1, sticky="nsew", padx=4, pady=4)
        
        query_text = scrolledtext.ScrolledText(query_frame, height=6,
                                              font=("Fixedsys", 9),
                                              bg="#ffffff", fg="#000000", bd=0)
        query_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        content.grid_rowconfigure(1, weight=1)
        content.grid_rowconfigure(5, weight=1)
        content.grid_columnconfigure(1, weight=1)
        
        def load_columns():
            table = table_combo.get()
            if table:
                columns_listbox.delete(0, tk.END)
                cursor.execute(f"PRAGMA table_info({table})")
                cols = cursor.fetchall()
                
                columns_listbox.insert(tk.END, "* (All columns)")
                for col in cols:
                    columns_listbox.insert(tk.END, col[1])
                
                order_combo['values'] = [col[1] for col in cols]
        
        def build_query():
            table = table_combo.get()
            if not table:
                messagebox.showwarning("Warning", "Please select a table")
                return
            
            # Get selected columns
            selected = columns_listbox.curselection()
            if not selected:
                columns = "*"
            elif 0 in selected:
                columns = "*"
            else:
                cols = [columns_listbox.get(i) for i in selected]
                columns = ", ".join(cols)
            
            # Build query
            query = f"SELECT {columns}\nFROM {table}"
            
            where = where_entry.get().strip()
            if where:
                query += f"\nWHERE {where}"
            
            order_col = order_combo.get()
            if order_col:
                query += f"\nORDER BY {order_col} {order_dir.get()}"
            
            limit = limit_entry.get().strip()
            if limit:
                query += f"\nLIMIT {limit}"
            
            query += ";"
            
            query_text.delete("1.0", tk.END)
            query_text.insert("1.0", query)
        
        def execute_query():
            query = query_text.get("1.0", tk.END).strip()
            if query:
                dialog.destroy()
                # Open SQL executor with this query
                exec_dialog = tk.Toplevel(self.rootdbman3)
                exec_dialog.title("Execute Query")
                exec_dialog.geometry("800x600")
                exec_dialog.configure(bg=self.bg_color)
                
                # Similar to show_sql_executor but with pre-filled query
                # For brevity, just show a message
                messagebox.showinfo("Query Built", f"Query:\n\n{query}")
        
        table_combo.bind('<<ComboboxSelected>>', lambda e: load_columns())
        
        btn_frame = tk.Frame(content, bg=self.bg_color)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=8)
        
        self.create_win95_button(btn_frame, "Build Query", build_query, 15).pack(side=tk.LEFT, padx=4)
        self.create_win95_button(btn_frame, "Execute", execute_query, 15).pack(side=tk.LEFT, padx=4)
        self.create_win95_button(btn_frame, "Close", dialog.destroy, 15).pack(side=tk.LEFT, padx=4)
    
    def export_csv(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"{self.current_table}.csv"
        )
        
        if file_path:
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT * FROM {self.current_table}")
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    writer.writerows(rows)
                
                self.update_status(f"Exported {len(rows)} records to CSV")
                messagebox.showinfo("Success", f"Exported {len(rows)} records to CSV")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_json(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile=f"{self.current_table}.json"
        )
        
        if file_path:
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT * FROM {self.current_table}")
                
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                self.update_status(f"Exported {len(rows)} records to JSON")
                messagebox.showinfo("Success", f"Exported {len(rows)} records to JSON")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_sql(self):
        if not self.current_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL Files", "*.sql")],
            initialfile=f"{self.current_table}.sql"
        )
        
        if file_path:
            try:
                cursor = self.conn.cursor()
                
                # Get CREATE statement
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                             (self.current_table,))
                create_sql = cursor.fetchone()[0]
                
                # Get data
                cursor.execute(f"SELECT * FROM {self.current_table}")
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"-- Export of table: {self.current_table}\n")
                    f.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"{create_sql};\n\n")
                    
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append("NULL")
                            elif isinstance(val, str):
                                escaped_val = val.replace("'", "''")
                                values.append(f"'{escaped_val}'")
                            else:
                                values.append(str(val))
                        
                        f.write(f"INSERT INTO {self.current_table} ({', '.join(columns)}) ")
                        f.write(f"VALUES ({', '.join(values)});\n")
                
                self.update_status(f"Exported {len(rows)} records to SQL")
                messagebox.showinfo("Success", f"Exported {len(rows)} records to SQL")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def export_all_tables(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        directory = filedialog.askdirectory(title="Select export directory")
        
        if directory:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                exported = 0
                for table in tables:
                    table_name = table[0]
                    self.current_table = table_name
                    
                    file_path = os.path.join(directory, f"{table_name}.csv")
                    
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(columns)
                        writer.writerows(rows)
                    
                    exported += 1
                
                self.update_status(f"Exported {exported} tables")
                messagebox.showinfo("Success", f"Exported {exported} tables to {directory}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def import_csv(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV Files", "*.csv")]
        )
        
        if file_path:
            # Ask for table name
            table_name = tk.simpledialog.askstring("Table Name",
                "Enter name for new table:",
                initialvalue=os.path.splitext(os.path.basename(file_path))[0])
            
            if not table_name:
                return
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    
                    # Create table
                    columns_def = ", ".join([f"{col} TEXT" for col in headers])
                    cursor = self.conn.cursor()
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})")
                    
                    # Insert data
                    placeholders = ", ".join(["?" for _ in headers])
                    insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                    
                    count = 0
                    for row in reader:
                        cursor.execute(insert_sql, row)
                        count += 1
                    
                    self.conn.commit()
                    self.refresh_tables_list()
                    self.update_status(f"Imported {count} records")
                    messagebox.showinfo("Success", f"Imported {count} records into table '{table_name}'")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    def import_json(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON Files", "*.json")]
        )
        
        if file_path:
            table_name = tk.simpledialog.askstring("Table Name",
                "Enter name for new table:",
                initialvalue=os.path.splitext(os.path.basename(file_path))[0])
            
            if not table_name:
                return
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not data:
                    messagebox.showwarning("Warning", "JSON file is empty")
                    return
                
                # Get columns from first record
                headers = list(data[0].keys())
                
                # Create table
                columns_def = ", ".join([f"{col} TEXT" for col in headers])
                cursor = self.conn.cursor()
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})")
                
                # Insert data
                placeholders = ", ".join(["?" for _ in headers])
                insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                
                for record in data:
                    values = [record.get(col, None) for col in headers]
                    cursor.execute(insert_sql, values)
                
                self.conn.commit()
                self.refresh_tables_list()
                self.update_status(f"Imported {len(data)} records")
                messagebox.showinfo("Success", f"Imported {len(data)} records into table '{table_name}'")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    def import_sql(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select SQL file",
            filetypes=[("SQL Files", "*.sql")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                
                cursor = self.conn.cursor()
                cursor.executescript(sql_script)
                self.conn.commit()
                
                self.refresh_tables_list()
                self.update_status("SQL script executed successfully")
                messagebox.showinfo("Success", "SQL script imported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {str(e)}")
    
    def backup_database(self):
        if not self.conn or not self.db_path:
            messagebox.showwarning("Warning", "No database is currently open")
            return
        
        backup_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")],
            initialfile=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(self.db_path)}"
        )
        
        if backup_path:
            try:
                # Use SQLite backup API
                backup_conn = sqlite3.connect(backup_path)
                with backup_conn:
                    self.conn.backup(backup_conn)
                backup_conn.close()
                
                self.update_status(f"Backup created: {os.path.basename(backup_path)}")
                messagebox.showinfo("Success", "Database backed up successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Backup failed: {str(e)}")
    
    def restore_database(self):
        backup_path = filedialog.askopenfilename(
            title="Select backup file to restore",
            filetypes=[("SQLite Database", "*.db")]
        )
        
        if backup_path:
            if messagebox.askyesno("Confirm", 
                "Restore will replace current database. Continue?"):
                try:
                    if self.conn:
                        self.conn.close()
                    
                    if self.db_path:
                        shutil.copy2(backup_path, self.db_path)
                        self.conn = sqlite3.connect(self.db_path)
                        self.refresh_tables_list()
                        self.update_status("Database restored successfully")
                        messagebox.showinfo("Success", "Database restored successfully")
                    else:
                        messagebox.showwarning("Warning", "No active database to restore to")
                except Exception as e:
                    messagebox.showerror("Error", f"Restore failed: {str(e)}")
    
    def show_statistics(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Please open a database first")
            return
        
        dialog = tk.Toplevel(self.rootdbman3)
        dialog.title("Database Statistics")
        dialog.geometry("700x600")
        dialog.configure(bg=self.bg_color)
        
        main_frame = self.create_win95_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        text_frame = self.create_win95_frame(main_frame, sunken=True)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        text = scrolledtext.ScrolledText(text_frame, font=("Fixedsys", 9),
                                        bg="#ffffff", fg="#000000", bd=0)
        text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        try:
            cursor = self.conn.cursor()
            
            text.insert(tk.END, "DATABASE STATISTICS\n")
            text.insert(tk.END, "=" * 80 + "\n\n")
            
            # Database file info
            if self.db_path:
                file_size = os.path.getsize(self.db_path)
                text.insert(tk.END, f"File: {os.path.basename(self.db_path)}\n")
                text.insert(tk.END, f"Size: {file_size / 1024:.2f} KB ({file_size:,} bytes)\n")
                text.insert(tk.END, f"Path: {self.db_path}\n\n")
            
            # Tables count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            tables_count = cursor.fetchone()[0]
            text.insert(tk.END, f"Total Tables: {tables_count}\n\n")
            
            # Table statistics
            text.insert(tk.END, "TABLE DETAILS:\n")
            text.insert(tk.END, "-" * 80 + "\n")
            text.insert(tk.END, f"{'Table Name':<30} {'Rows':<15} {'Columns':<15}\n")
            text.insert(tk.END, "-" * 80 + "\n")
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            total_rows = 0
            for table in tables:
                table_name = table[0]
                
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_count = len(cursor.fetchall())
                
                text.insert(tk.END, f"{table_name:<30} {row_count:<15} {columns_count:<15}\n")
            
            text.insert(tk.END, "\n")
            text.insert(tk.END, f"Total Records: {total_rows:,}\n\n")
            
            # Indexes
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
            indexes_count = cursor.fetchone()[0]
            text.insert(tk.END, f"Total Indexes: {indexes_count}\n")
            
            # Views
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view'")
            views_count = cursor.fetchone()[0]
            text.insert(tk.END, f"Total Views: {views_count}\n")
            
            text.config(state=tk.DISABLED)
            
        except Exception as e:
            text.insert(tk.END, f"Error generating statistics: {str(e)}")
    
    def show_about(self):
        about_text = """Advanced Database Manager Pro
Version 2.0

A comprehensive SQLite database management tool with a classic Windows 95 interface.

Features:
- Create, open, and manage SQLite databases
- Advanced table operations (CRUD)
- SQL query executor with syntax support
- Visual query builder
- Import/Export (CSV, JSON, SQL)
- Database backup and restore
- Schema comparison and analysis
- Find & Replace functionality
- Bulk editing operations
- Database statistics and optimization
- Foreign key relationship viewer

Keyboard Shortcuts:
- Ctrl+N: New Database
- Ctrl+O: Open Database
- F5: Execute SQL / Refresh
- Ctrl+R: Refresh Data
- Ctrl+F: Find & Replace

© 2025 Database Manager Pro
Built with Python and Tkinter
"""
        messagebox.showinfo("About", about_text)
    
    def load_settings(self):
        """Load application settings from file"""
        settings_file = "db_manager_settings.json"
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.recent_databases = settings.get('recent_databases', [])
                    self.bookmarks = settings.get('bookmarks', {})
                    self.page_size = settings.get('page_size', 100)
                    self.page_size_var.set(str(self.page_size))
                    
                    self.update_recent_menu()
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save application settings to file"""
        settings_file = "db_manager_settings.json"
        try:
            settings = {
                'recent_databases': self.recent_databases,
                'bookmarks': self.bookmarks,
                'page_size': self.page_size
            }
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def __del__(self):
        """Cleanup when application closes"""
        if self.conn:
            self.conn.close()
        self.save_settings()


def main():
    rootdbman3 = tk.Tk()
    app = DatabaseManager(rootdbman3)
    
    # Set window icon (if available)
    try:
        # You can add an icon file here
        # rootdbman3.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    # Handle window close event
    def on_closing():
        if app.conn:
            if messagebox.askokcancel("Quit", "Close database and exit?"):
                app.save_settings()
                rootdbman3.destroy()
        else:
            app.save_settings()
            rootdbman3.destroy()
    
    rootdbman3.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Center window on screen
    rootdbman3.update_idletasks()
    width = rootdbman3.winfo_width()
    height = rootdbman3.winfo_height()
    x = (rootdbman3.winfo_screenwidth() // 2) - (width // 2)
    y = (rootdbman3.winfo_screenheight() // 2) - (height // 2)
    rootdbman3.geometry(f'{width}x{height}+{x}+{y}')
    
    rootdbman3.mainloop()


if __name__ == "__main__":
    main()