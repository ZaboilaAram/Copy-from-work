import tkinter as tk
from tkinter import filedialog, messagebox, Text, Frame, Label, Button, Scrollbar, Canvas, Listbox
import sqlite3
import time
import re
import math

class SQLWorkspace:
    def __init__(self, parent, bg_color, title_bg, title_fg, text_bg):
        self.parent = parent
        self.bg_color = bg_color
        self.title_bg = title_bg
        self.title_fg = title_fg
        self.text_bg = text_bg
        
        # Use in-memory database for this workspace
        self.db_connection = sqlite3.connect(':memory:')
        self.query_history = []
        self.current_results = []
        self.current_columns = []
        
        # Diagram data
        self.tables = {}
        self.dragging = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.create_workspace()
    
    def create_3d_frame(self, parent, raised=True):
        frame = Frame(parent, bg=self.bg_color, bd=2)
        if raised:
            frame.config(relief="raised")
        else:
            frame.config(relief="sunken")
        return frame
    
    def create_workspace(self):
        # Main container
        main_container = Frame(self.parent, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Left panel - Query editor
        left_panel = Frame(main_container, bg=self.bg_color)
        left_panel.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        
        # Query editor frame
        editor_frame = self.create_3d_frame(left_panel, raised=False)
        editor_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        editor_label = Label(
            editor_frame,
            text="SQL Query Editor",
            bg=self.title_bg,
            fg=self.title_fg,
            font=("MS Sans Serif", 9, "bold")
        )
        editor_label.pack(fill="x")
        
        # Query editor
        editor_container = Frame(editor_frame, bg=self.bg_color)
        editor_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.query_text = Text(
            editor_container,
            bg=self.text_bg,
            fg="#000000",
            font=("Courier New", 10),
            relief="sunken",
            bd=2,
            wrap="word"
        )
        
        query_scrollbar = Scrollbar(editor_container, command=self.query_text.yview)
        self.query_text.configure(yscrollcommand=query_scrollbar.set)
        
        query_scrollbar.pack(side="right", fill="y")
        self.query_text.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel to query text
        self.query_text.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, self.query_text))
        self.query_text.bind("<Button-4>", lambda e: self._on_mousewheel(e, self.query_text))
        self.query_text.bind("<Button-5>", lambda e: self._on_mousewheel(e, self.query_text))
        
        # Query history frame
        history_frame = self.create_3d_frame(left_panel, raised=False)
        history_frame.pack(fill="both", expand=False, padx=2, pady=2)
        
        history_label = Label(
            history_frame,
            text="Query History",
            bg=self.title_bg,
            fg=self.title_fg,
            font=("MS Sans Serif", 9, "bold")
        )
        history_label.pack(fill="x")
        
        history_container = Frame(history_frame, bg=self.bg_color)
        history_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.history_listbox = Listbox(
            history_container,
            bg=self.text_bg,
            fg="#000000",
            font=("MS Sans Serif", 8),
            relief="sunken",
            bd=2,
            height=5
        )
        
        history_scrollbar = Scrollbar(history_container, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=history_scrollbar.set)
        
        history_scrollbar.pack(side="right", fill="y")
        self.history_listbox.pack(side="left", fill="both", expand=True)
        
        self.history_listbox.bind("<Double-Button-1>", self.load_history_query)
        
        # Bind mousewheel to history listbox
        self.history_listbox.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, self.history_listbox))
        self.history_listbox.bind("<Button-4>", lambda e: self._on_mousewheel(e, self.history_listbox))
        self.history_listbox.bind("<Button-5>", lambda e: self._on_mousewheel(e, self.history_listbox))
        
        # Right panel - Diagram and results
        right_panel = Frame(main_container, bg=self.bg_color)
        right_panel.pack(side="right", fill="both", expand=True, padx=2, pady=2)
        
        # Diagram frame
        diagram_frame = self.create_3d_frame(right_panel, raised=False)
        diagram_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        diagram_label = Label(
            diagram_frame,
            text="Database Diagram",
            bg=self.title_bg,
            fg=self.title_fg,
            font=("MS Sans Serif", 9, "bold")
        )
        diagram_label.pack(fill="x")
        
        # Canvas for diagram
        diagram_container = Frame(diagram_frame, bg=self.bg_color)
        diagram_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.diagram_canvas = Canvas(
            diagram_container,
            bg=self.text_bg,
            highlightthickness=0
        )
        
        diagram_v_scrollbar = Scrollbar(diagram_container, orient="vertical", command=self.diagram_canvas.yview)
        diagram_h_scrollbar = Scrollbar(diagram_container, orient="horizontal", command=self.diagram_canvas.xview)
        
        self.diagram_canvas.configure(yscrollcommand=diagram_v_scrollbar.set, xscrollcommand=diagram_h_scrollbar.set)
        self.diagram_canvas.configure(scrollregion=(0, 0, 1500, 1500))
        
        diagram_v_scrollbar.pack(side="right", fill="y")
        diagram_h_scrollbar.pack(side="bottom", fill="x")
        self.diagram_canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mouse events for dragging
        self.diagram_canvas.bind("<ButtonPress-1>", self.on_diagram_mouse_down)
        self.diagram_canvas.bind("<B1-Motion>", self.on_diagram_mouse_move)
        self.diagram_canvas.bind("<ButtonRelease-1>", self.on_diagram_mouse_up)
        
        # Bind mousewheel for diagram
        self.diagram_canvas.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, self.diagram_canvas))
        self.diagram_canvas.bind("<Button-4>", lambda e: self._on_mousewheel(e, self.diagram_canvas))
        self.diagram_canvas.bind("<Button-5>", lambda e: self._on_mousewheel(e, self.diagram_canvas))
        
        # Statistics and Results frame
        results_frame = self.create_3d_frame(right_panel, raised=False)
        results_frame.pack(fill="both", expand=False, padx=2, pady=2)
        
        results_label = Label(
            results_frame,
            text="Query Results & Statistics",
            bg=self.title_bg,
            fg=self.title_fg,
            font=("MS Sans Serif", 9, "bold")
        )
        results_label.pack(fill="x")
        
        # Statistics
        self.stats_text = Text(
            results_frame,
            bg=self.text_bg,
            fg="#000000",
            font=("MS Sans Serif", 8),
            relief="sunken",
            bd=2,
            height=3,
            state="disabled"
        )
        self.stats_text.pack(fill="x", padx=2, pady=2)
        
        # Canvas for results table
        results_container = Frame(results_frame, bg=self.bg_color)
        results_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.results_canvas = Canvas(
            results_container,
            bg=self.text_bg,
            highlightthickness=0,
            height=150
        )
        
        v_scrollbar = Scrollbar(results_container, orient="vertical", command=self.results_canvas.yview)
        h_scrollbar = Scrollbar(results_container, orient="horizontal", command=self.results_canvas.xview)
        
        self.results_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.results_canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel for results
        self.results_canvas.bind("<MouseWheel>", lambda e: self._on_mousewheel(e, self.results_canvas))
        self.results_canvas.bind("<Button-4>", lambda e: self._on_mousewheel(e, self.results_canvas))
        self.results_canvas.bind("<Button-5>", lambda e: self._on_mousewheel(e, self.results_canvas))
    
    def execute_query(self):
        query = self.query_text.get("1.0", "end-1c").strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a SQL query")
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Start timing
            start_time = time.time()
            
            # Split queries by semicolon and execute
            queries = [q.strip() for q in query.split(';') if q.strip()]
            
            last_query_type = None
            last_results = None
            last_columns = None
            total_rows_affected = 0
            
            for single_query in queries:
                cursor.execute(single_query)
                
                query_type = single_query.strip().upper().split()[0]
                last_query_type = query_type
                
                if query_type == "SELECT":
                    last_results = cursor.fetchall()
                    last_columns = [description[0] for description in cursor.description]
                else:
                    self.db_connection.commit()
                    total_rows_affected += cursor.rowcount
            
            # End timing
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000
            
            # Refresh diagram after any query execution
            self.refresh_diagram()
            
            # Display results of last SELECT query if any
            if last_query_type == "SELECT" and last_results is not None:
                self.current_results = last_results
                self.current_columns = last_columns
                
                self.display_results(last_results, last_columns)
                
                self.update_statistics(
                    query_type=last_query_type,
                    rows_affected=len(last_results),
                    execution_time=execution_time,
                    columns_count=len(last_columns)
                )
            else:
                # For INSERT, UPDATE, DELETE, CREATE, etc.
                self.results_canvas.delete("all")
                self.current_results = []
                self.current_columns = []
                
                self.update_statistics(
                    query_type=last_query_type,
                    rows_affected=total_rows_affected,
                    execution_time=execution_time
                )
                
                messagebox.showinfo("Success", f"{last_query_type} completed: {total_rows_affected} rows affected")
            
            # Add to history
            self.add_to_history(query)
            
        except Exception as e:
            messagebox.showerror("Error", f"Query execution failed: {str(e)}")
    
    def refresh_diagram(self):
        try:
            cursor = self.db_connection.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables_result = cursor.fetchall()
            
            self.tables = {}
            
            for table_row in tables_result:
                table_name = table_row[0]
                if table_name.startswith('sqlite_'):
                    continue
                
                # Get columns
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Get foreign keys
                cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                fks = cursor.fetchall()
                
                col_list = []
                for col in columns:
                    col_name = col[1]
                    col_type = col[2]
                    is_pk = col[5] == 1
                    col_list.append({
                        'name': col_name,
                        'type': col_type,
                        'primary_key': is_pk
                    })
                
                fk_list = []
                for fk in fks:
                    fk_list.append({
                        'column': fk[3],
                        'ref_table': fk[2],
                        'ref_column': fk[4]
                    })
                
                self.add_table(table_name, col_list, fk_list)
            
            if len(self.tables) > 0:
                self.layout_tables()
                self.draw_tables()
                self.draw_connections()
        
        except Exception as e:
            pass
    
    def add_table(self, name, columns, foreign_keys):
        if name not in self.tables:
            self.tables[name] = {
                'name': name,
                'columns': columns,
                'foreign_keys': foreign_keys,
                'x': 0,
                'y': 0,
                'width': 0,
                'height': 0
            }
        else:
            # Update existing table
            self.tables[name]['columns'] = columns
            self.tables[name]['foreign_keys'] = foreign_keys
    
    def layout_tables(self):
        num_tables = len(self.tables)
        if num_tables == 0:
            return
        
        cols = math.ceil(math.sqrt(num_tables))
        x_spacing = 220
        y_spacing = 250
        start_x = 30
        start_y = 30
        
        # Sort tables alphabetically for consistent layout
        sorted_tables = sorted(self.tables.items(), key=lambda x: x[0])
        
        for idx, (name, table) in enumerate(sorted_tables):
            # Only set position if table doesn't have one yet
            if table['x'] == 0 and table['y'] == 0:
                row = idx // cols
                col = idx % cols
                table['x'] = start_x + col * x_spacing
                table['y'] = start_y + row * y_spacing
    
    def draw_tables(self):
        self.diagram_canvas.delete("all")
        
        # FIRST draw connections (in background)
        #self.draw_connections()
        
        # THEN draw tables (on top)
        for name, table in self.tables.items():
            x = table['x']
            y = table['y']
            
            # Calculate height
            header_height = 25
            row_height = 20
            table_height = header_height + len(table['columns']) * row_height
            table_width = 180
            
            table['width'] = table_width
            table['height'] = table_height
            
            # Draw table rectangle
            self.diagram_canvas.create_rectangle(
                x, y, x + table_width, y + table_height,
                fill="#ffffff",
                outline="#000000",
                width=2,
                tags=("table", name)
            )
            
            # Draw header
            self.diagram_canvas.create_rectangle(
                x, y, x + table_width, y + header_height,
                fill=self.title_bg,
                outline="#000000",
                width=1,
                tags=("table", name)
            )
            
            # Table name
            self.diagram_canvas.create_text(
                x + table_width // 2, y + header_height // 2,
                text=name,
                fill=self.title_fg,
                font=("MS Sans Serif", 9, "bold"),
                tags=("table", name)
            )
            
            # Draw columns
            for idx, col in enumerate(table['columns']):
                col_y = y + header_height + idx * row_height
                
                # Draw separator line
                self.diagram_canvas.create_line(
                    x, col_y, x + table_width, col_y,
                    fill="#c0c0c0",
                    tags=("table", name)
                )
                
                # Column text
                pk_marker = "[PK] " if col['primary_key'] else ""
                col_text = f"{pk_marker}{col['name']}: {col['type']}"
                
                self.diagram_canvas.create_text(
                    x + 5, col_y + row_height // 2,
                    text=col_text,
                    anchor="w",
                    fill="#000000",
                    font=("MS Sans Serif", 8),
                    tags=("table", name)
                )
        self.draw_connections()
    
    def draw_connections(self):
        self.diagram_canvas.delete("connection")
        
        for name, table in self.tables.items():
            for fk in table['foreign_keys']:
                if fk['ref_table'] in self.tables:
                    self.draw_connection(name, fk['ref_table'])
    
    def draw_connection(self, from_table, to_table):
        if from_table not in self.tables or to_table not in self.tables:
            return
        
        t1 = self.tables[from_table]
        t2 = self.tables[to_table]
        
        # Calculate connection points
        x1 = t1['x'] + t1['width']
        y1 = t1['y'] + t1['height'] // 2
        
        x2 = t2['x']
        y2 = t2['y'] + t2['height'] // 2
        
        # Draw line
        self.diagram_canvas.create_line(
            x1, y1, x2, y2,
            fill="#ff0000",
            width=2,
            arrow=tk.LAST,
            tags="connection"
        )
        
        # Add circle at start
        self.diagram_canvas.create_oval(
            x1-3, y1-3, x1+3, y1+3,
            fill="#ff0000",
            outline="#ff0000",
            tags="connection"
        )
    
    def on_diagram_mouse_down(self, event):
        x = self.diagram_canvas.canvasx(event.x)
        y = self.diagram_canvas.canvasy(event.y)
        
        items = self.diagram_canvas.find_overlapping(x, y, x, y)
        for item in items:
            tags = self.diagram_canvas.gettags(item)
            if "table" in tags:
                for tag in tags:
                    if tag in self.tables:
                        self.dragging = tag
                        self.drag_start_x = x - self.tables[tag]['x']
                        self.drag_start_y = y - self.tables[tag]['y']
                        break
                break
    
    def on_diagram_mouse_move(self, event):
        if self.dragging:
            x = self.diagram_canvas.canvasx(event.x)
            y = self.diagram_canvas.canvasy(event.y)
            
            self.tables[self.dragging]['x'] = x - self.drag_start_x
            self.tables[self.dragging]['y'] = y - self.drag_start_y
            
            self.draw_tables()
    
    def on_diagram_mouse_up(self, event):
        self.dragging = None
    
    def _on_mousewheel(self, event, widget):
        """Handle mousewheel scrolling for all widgets"""
        if event.num == 5 or event.delta < 0:
            # Scroll down
            if isinstance(widget, Canvas):
                widget.yview_scroll(1, "units")
            elif isinstance(widget, Text):
                widget.yview_scroll(1, "units")
            elif isinstance(widget, Listbox):
                widget.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            # Scroll up
            if isinstance(widget, Canvas):
                widget.yview_scroll(-1, "units")
            elif isinstance(widget, Text):
                widget.yview_scroll(-1, "units")
            elif isinstance(widget, Listbox):
                widget.yview_scroll(-1, "units")
    
    def reset_database(self):
        """Reset the database - drop all tables and clear everything"""
        try:
            # Close old connection
            self.db_connection.close()
            
            # Create new in-memory database
            self.db_connection = sqlite3.connect(':memory:')
            
            # Clear all data
            self.tables = {}
            self.current_results = []
            self.current_columns = []
            self.query_history = []
            
            # Clear UI
            self.diagram_canvas.delete("all")
            self.results_canvas.delete("all")
            self.history_listbox.delete(0, "end")
            
            self.stats_text.config(state="normal")
            self.stats_text.delete("1.0", "end")
            self.stats_text.config(state="disabled")
            
            messagebox.showinfo("Success", "Database reset successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset database: {str(e)}")
    
    def open_file(self):
        """Open SQL file or SQLite database"""
        filename = filedialog.askopenfilename(
            title="Open SQL File or SQLite Database",
            filetypes=[
                ("SQL Files", "*.sql"),
                ("SQLite Database", "*.db"),
                ("SQLite Database", "*.sqlite"),
                ("SQLite Database", "*.sqlite3"),
                ("All Files", "*.*")
            ]
        )
        
        if filename:
            try:
                # Check if it's a SQLite database by reading the header
                with open(filename, 'rb') as f:
                    header = f.read(16)
                
                is_sqlite = header[:13] == b'SQLite format'
                
                if is_sqlite:
                    # It's a SQLite database - extract schema
                    schema_sql = self.extract_sqlite_schema(filename)
                    if schema_sql:
                        self.query_text.delete("1.0", "end")
                        self.query_text.insert("1.0", schema_sql)
                        messagebox.showinfo("Success", "Schema extracted from database!")
                    else:
                        messagebox.showwarning("Warning", "No tables found in database!")
                else:
                    # It's a text SQL file
                    with open(filename, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    
                    self.query_text.delete("1.0", "end")
                    self.query_text.insert("1.0", sql_content)
                    messagebox.showinfo("Success", "SQL file loaded!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    def extract_sqlite_schema(self, db_path):
        """Extract CREATE TABLE statements from SQLite database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables (excluding sqlite internal tables)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = cursor.fetchall()
            
            schema_sql = []
            for (table_name,) in tables:
                # Get CREATE TABLE statement
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
                create_sql = cursor.fetchone()
                if create_sql and create_sql[0]:
                    schema_sql.append(create_sql[0] + ";")
                    schema_sql.append("")  # Empty line between tables
            
            conn.close()
            return "\n".join(schema_sql)
            
        except Exception as e:
            raise Exception(f"Failed to extract schema: {str(e)}")
    
    def display_results(self, results, columns):
        self.results_canvas.delete("all")
        
        if not results:
            self.results_canvas.create_text(
                10, 10,
                text="No results to display",
                anchor="nw",
                font=("MS Sans Serif", 9),
                fill="#808080"
            )
            return
        
        # Calculate column widths
        col_widths = []
        for i, col_name in enumerate(columns):
            max_width = len(str(col_name)) * 8
            for row in results:
                cell_width = len(str(row[i])) * 8
                if cell_width > max_width:
                    max_width = cell_width
            col_widths.append(min(max_width + 20, 300))
        
        # Draw table
        x_offset = 10
        y_offset = 10
        row_height = 25
        
        # Draw header
        current_x = x_offset
        for i, col_name in enumerate(columns):
            # Header background
            self.results_canvas.create_rectangle(
                current_x, y_offset,
                current_x + col_widths[i], y_offset + row_height,
                fill=self.title_bg,
                outline="#000000",
                width=1
            )
            
            # Header text
            self.results_canvas.create_text(
                current_x + 5, y_offset + row_height // 2,
                text=col_name,
                anchor="w",
                fill=self.title_fg,
                font=("MS Sans Serif", 9, "bold")
            )
            
            current_x += col_widths[i]
        
        # Draw rows
        current_y = y_offset + row_height
        for row_idx, row in enumerate(results):
            current_x = x_offset
            
            # Alternate row colors
            row_bg = "#ffffff" if row_idx % 2 == 0 else "#f0f0f0"
            
            for col_idx, cell_value in enumerate(row):
                # Cell background
                self.results_canvas.create_rectangle(
                    current_x, current_y,
                    current_x + col_widths[col_idx], current_y + row_height,
                    fill=row_bg,
                    outline="#c0c0c0",
                    width=1
                )
                
                # Cell text
                cell_text = str(cell_value) if cell_value is not None else "NULL"
                self.results_canvas.create_text(
                    current_x + 5, current_y + row_height // 2,
                    text=cell_text,
                    anchor="w",
                    fill="#000000",
                    font=("MS Sans Serif", 8)
                )
                
                current_x += col_widths[col_idx]
            
            current_y += row_height
        
        # Update scroll region
        total_width = sum(col_widths) + 20
        total_height = (len(results) + 1) * row_height + 20
        self.results_canvas.configure(scrollregion=(0, 0, total_width, total_height))
    
    def update_statistics(self, query_type, rows_affected, execution_time, columns_count=0):
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")
        
        stats = f"Query Type: {query_type} | "
        stats += f"Rows: {rows_affected} | "
        stats += f"Time: {execution_time:.2f} ms"
        if columns_count > 0:
            stats += f" | Columns: {columns_count}"
        
        self.stats_text.insert("1.0", stats)
        self.stats_text.config(state="disabled")
    
    def add_to_history(self, query):
        # Truncate long queries for display
        display_query = query[:60] + "..." if len(query) > 60 else query
        display_query = display_query.replace("\n", " ")
        
        timestamp = time.strftime("%H:%M:%S")
        history_entry = f"[{timestamp}] {display_query}"
        
        self.query_history.append(query)
        self.history_listbox.insert(0, history_entry)
        
        # Limit history to 50 entries
        if self.history_listbox.size() > 50:
            self.history_listbox.delete(50)
            self.query_history = self.query_history[-50:]
    
    def load_history_query(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            index = selection[0]
            actual_index = len(self.query_history) - 1 - index
            if 0 <= actual_index < len(self.query_history):
                query = self.query_history[actual_index]
                self.query_text.delete("1.0", "end")
                self.query_text.insert("1.0", query)
    
    def clear_results(self):
        self.results_canvas.delete("all")
        self.current_results = []
        self.current_columns = []
        
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")
        self.stats_text.config(state="disabled")
    
    def save_sql(self):
        query = self.query_text.get("1.0", "end-1c").strip()
        
        if not query and not self.current_results:
            messagebox.showwarning("Warning", "No query or results to save")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save SQL File",
            defaultextension=".sql",
            filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    # Write current query
                    if query:
                        f.write("-- Current Query\n")
                        f.write(f"{query};\n\n")
                    
                    # If we have results, generate INSERT statements
                    if self.current_results and self.current_columns:
                        f.write("-- Results as INSERT statements\n")
                        f.write("-- Generated table structure\n\n")
                        
                        table_name = "exported_results"
                        
                        # CREATE TABLE statement
                        column_defs = [f"{col} TEXT" for col in self.current_columns]
                        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
                        create_sql += ",\n".join(f"    {col_def}" for col_def in column_defs)
                        create_sql += "\n);\n\n"
                        f.write(create_sql)
                        
                        # INSERT statements
                        for row in self.current_results:
                            values = []
                            for val in row:
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                else:
                                    escaped = str(val).replace("'", "''")
                                    values.append(f"'{escaped}'")
                            
                            insert_sql = f"INSERT INTO {table_name} VALUES ({', '.join(values)});\n"
                            f.write(insert_sql)
                
                messagebox.showinfo("Success", f"SQL saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save SQL: {str(e)}")
    
    # def export_to_sqlite(self):
        # if not self.current_results or not self.current_columns:
            # messagebox.showwarning("Warning", "No results to export")
            # return
        
        # filename = filedialog.asksaveasfilename(
            # title="Export to SQLite Database",
            # defaultextension=".db",
            # filetypes=[
                # ("SQLite Database", "*.db"),
                # ("SQLite Database", "*.sqlite"),
                # ("SQLite Database", "*.sqlite3")
            # ]
        # )
        
        # if filename:
            # try:
                # # Create new database
                # export_conn = sqlite3.connect(filename)
                # export_cursor = export_conn.cursor()
                
                # # Generate table name
                # table_name = "exported_results"
                
                # # Create table schema
                # column_defs = []
                # for col in self.current_columns:
                    # col_def = f"{col} TEXT"
                    # column_defs.append(col_def)
                
                # create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
                # export_cursor.execute(create_table_sql)
                
                # # Insert data
                # placeholders = ', '.join(['?' for _ in self.current_columns])
                # insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                
                # for row in self.current_results:
                    # export_cursor.execute(insert_sql, row)
                
                # export_conn.commit()
                # export_conn.close()
                
                # messagebox.showinfo("Success", f"Exported {len(self.current_results)} rows to {filename}")
                
            # except Exception as e:
                # messagebox.showerror("Error", f"Export failed: {str(e)}")
    def export_to_sqlite(self):
        filename = filedialog.asksaveasfilename(
            title="Export to SQLite Database",
            defaultextension=".db",
            filetypes=[
                ("SQLite Database", "*.db"),
                ("SQLite Database", "*.sqlite"),
                ("SQLite Database", "*.sqlite3")
            ]
        )
        
        if filename:
            try:
                # Get all tables from current database
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                tables = cursor.fetchall()
                
                if not tables:
                    messagebox.showwarning("Warning", "No tables to export")
                    return
                
                # Create export database
                export_conn = sqlite3.connect(filename)
                
                # Backup entire database
                self.db_connection.backup(export_conn)
                
                export_conn.close()
                
                messagebox.showinfo("Success", f"Database exported to {filename}\nTables: {len(tables)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")

class Win95SQLExecutor:
    def __init__(self, rootexdiag):
        self.rootexdiag = rootexdiag
        self.rootexdiag.title("SQL Query Executor")
        self.rootexdiag.geometry("1400x900")
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.dark_border = "#808080"
        self.light_border = "#ffffff"
        self.title_bg = "#000080"
        self.title_fg = "#ffffff"
        self.text_bg = "#ffffff"
        
        self.rootexdiag.configure(bg=self.bg_color)
        
        # Tab management
        self.tabs = []
        self.current_tab_index = 0
        self.tab_counter = 1
        
        self.create_widgets()
        self.add_new_tab()
    
    def create_3d_frame(self, parent, raised=True):
        frame = Frame(parent, bg=self.bg_color, bd=2)
        if raised:
            frame.config(relief="raised")
        else:
            frame.config(relief="sunken")
        return frame
    
    def create_widgets(self):
        # Menu bar
        menu_frame = self.create_3d_frame(self.rootexdiag, raised=True)
        menu_frame.pack(fill="x", padx=2, pady=2)
        
        btn_new_tab = Button(
            menu_frame,
            text="New Tab",
            command=self.add_new_tab,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_new_tab.pack(side="left", padx=2, pady=2)
        
        btn_close_tab = Button(
            menu_frame,
            text="Close Tab",
            command=self.close_current_tab,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_close_tab.pack(side="left", padx=2, pady=2)
        
        btn_open_file = Button(
            menu_frame,
            text="Open SQL/DB",
            command=self.open_file,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_open_file.pack(side="left", padx=2, pady=2)
        
        btn_execute = Button(
            menu_frame,
            text="Execute Query",
            command=self.execute_query,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_execute.pack(side="left", padx=2, pady=2)
        
        btn_clear = Button(
            menu_frame,
            text="Clear Results",
            command=self.clear_results,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_clear.pack(side="left", padx=2, pady=2)
        
        btn_export_db = Button(
            menu_frame,
            text="Export to SQLite",
            command=self.export_to_sqlite,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_export_db.pack(side="left", padx=2, pady=2)
        
        btn_save_sql = Button(
            menu_frame,
            text="Save SQL",
            command=self.save_sql,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_save_sql.pack(side="left", padx=2, pady=2)
        
        btn_refresh_diagram = Button(
            menu_frame,
            text="Refresh Diagram",
            command=self.refresh_diagram,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_refresh_diagram.pack(side="left", padx=2, pady=2)
        
        btn_reset_db = Button(
            menu_frame,
            text="Reset Database",
            command=self.reset_database,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_reset_db.pack(side="left", padx=2, pady=2)
        
        # Status label
        self.status_label = Label(
            menu_frame,
            text="Ready - Write your SQL queries",
            bg=self.bg_color,
            anchor="w",
            relief="sunken",
            bd=1
        )
        self.status_label.pack(side="right", fill="x", expand=True, padx=2, pady=2)
        
        # Tab bar
        self.tab_bar_frame = self.create_3d_frame(self.rootexdiag, raised=False)
        self.tab_bar_frame.pack(fill="x", padx=2, pady=(0, 2))
        
        # Tab content area
        self.tab_content_frame = Frame(self.rootexdiag, bg=self.bg_color)
        self.tab_content_frame.pack(fill="both", expand=True)
    
    def add_new_tab(self):
        # Create tab button
        tab_name = f"Tab {self.tab_counter}"
        self.tab_counter += 1
        
        tab_button = Button(
            self.tab_bar_frame,
            text=tab_name,
            command=lambda idx=len(self.tabs): self.switch_tab(idx),
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=15,
            pady=2,
            font=("MS Sans Serif", 8)
        )
        tab_button.pack(side="left", padx=1, pady=2)
        
        # Create tab content frame
        tab_frame = Frame(self.tab_content_frame, bg=self.bg_color)
        
        # Create workspace
        workspace = SQLWorkspace(tab_frame, self.bg_color, self.title_bg, self.title_fg, self.text_bg)
        
        # Store tab info
        self.tabs.append({
            'name': tab_name,
            'button': tab_button,
            'frame': tab_frame,
            'workspace': workspace
        })
        
        # Switch to new tab
        self.switch_tab(len(self.tabs) - 1)
    
    def close_current_tab(self):
        if len(self.tabs) <= 1:
            messagebox.showwarning("Warning", "Cannot close the last tab")
            return
        
        # Close database connection
        self.tabs[self.current_tab_index]['workspace'].db_connection.close()
        
        # Destroy button and frame
        self.tabs[self.current_tab_index]['button'].destroy()
        self.tabs[self.current_tab_index]['frame'].destroy()
        
        # Remove from list
        self.tabs.pop(self.current_tab_index)
        
        # Switch to previous tab or first tab
        new_index = min(self.current_tab_index, len(self.tabs) - 1)
        self.switch_tab(new_index)
    
    def switch_tab(self, index):
        if index < 0 or index >= len(self.tabs):
            return
        
        # Hide all tabs
        for tab in self.tabs:
            tab['frame'].pack_forget()
            tab['button'].config(relief="raised", bg=self.bg_color)
        
        # Show selected tab
        self.tabs[index]['frame'].pack(fill="both", expand=True)
        self.tabs[index]['button'].config(relief="sunken", bg="#ffffff")
        
        self.current_tab_index = index
        self.status_label.config(text=f"{self.tabs[index]['name']} - Ready")
    
    def get_current_workspace(self):
        if 0 <= self.current_tab_index < len(self.tabs):
            return self.tabs[self.current_tab_index]['workspace']
        return None
    
    def execute_query(self):
        workspace = self.get_current_workspace()
        if workspace:
            workspace.execute_query()
    
    def clear_results(self):
        workspace = self.get_current_workspace()
        if workspace:
            workspace.clear_results()
    
    def save_sql(self):
        workspace = self.get_current_workspace()
        if workspace:
            workspace.save_sql()
    
    def export_to_sqlite(self):
        workspace = self.get_current_workspace()
        if workspace:
            workspace.export_to_sqlite()
    
    def refresh_diagram(self):
        workspace = self.get_current_workspace()
        if workspace:
            workspace.refresh_diagram()
    
    def open_file(self):
        workspace = self.get_current_workspace()
        if workspace:
            workspace.open_file()
    
    def reset_database(self):
        workspace = self.get_current_workspace()
        if workspace:
            result = messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the database? All data will be lost.")
            if result:
                workspace.reset_database()

if __name__ == "__main__":
    rootexdiag = tk.Tk()
    app = Win95SQLExecutor(rootexdiag)
    rootexdiag.mainloop()
