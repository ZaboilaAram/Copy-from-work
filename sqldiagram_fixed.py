import tkinter as tk
from tkinter import filedialog, messagebox, Canvas, Frame, Label, Button, Scrollbar
import sqlite3
import re
import math

class Win95SQLDiagram:
    def __init__(self, rootsqldiagR):
        self.rootsqldiagR = rootsqldiagR
        self.rootsqldiagR.title("SQL Database Diagram")
        self.rootsqldiagR.geometry("1000x700")
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.dark_border = "#808080"
        self.light_border = "#ffffff"
        self.title_bg = "#000080"
        self.title_fg = "#ffffff"
        
        self.rootsqldiagR.configure(bg=self.bg_color)
        
        self.tables = {}
        self.connections = []
        self.dragging = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.create_widgets()
    
    def create_3d_frame(self, parent, raised=True):
        frame = Frame(parent, bg=self.bg_color, bd=2)
        if raised:
            frame.config(relief="raised")
        else:
            frame.config(relief="sunken")
        return frame
    
    def create_widgets(self):
        # Menu bar
        menu_frame = self.create_3d_frame(self.rootsqldiagR, raised=True)
        menu_frame.pack(fill="x", padx=2, pady=2)
        
        btn_open_db = Button(
            menu_frame, 
            text="Open SQLite DB", 
            command=self.open_sqlite,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_open_db.pack(side="left", padx=2, pady=2)
        
        btn_open_sql = Button(
            menu_frame,
            text="Open SQL File",
            command=self.open_sql_file,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_open_sql.pack(side="left", padx=2, pady=2)
        
        btn_clear = Button(
            menu_frame,
            text="Clear Diagram",
            command=self.clear_diagram,
            bg=self.bg_color,
            relief="raised",
            bd=2,
            padx=10,
            pady=2
        )
        btn_clear.pack(side="left", padx=2, pady=2)
        
        # Status bar
        self.status_label = Label(
            menu_frame,
            text="Ready",
            bg=self.bg_color,
            anchor="w",
            relief="sunken",
            bd=1
        )
        self.status_label.pack(side="right", fill="x", expand=True, padx=2, pady=2)
        
        # Canvas frame
        canvas_frame = self.create_3d_frame(self.rootsqldiagR, raised=False)
        canvas_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Canvas with scrollbars
        self.canvas = Canvas(
            canvas_frame,
            bg="#ffffff",
            highlightthickness=0
        )
        
        v_scrollbar = Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.canvas.configure(scrollregion=(0, 0, 2000, 2000))
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # Bind mouse wheel for scrolling
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)  # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)  # Linux scroll down
    
    def open_sqlite(self):
        filename = filedialog.askopenfilename(
            title="Open SQLite Database",
            filetypes=[("SQLite Database", "*.db *.sqlite *.sqlite3"), ("All Files", "*.*")]
        )
        if filename:
            try:
                conn = sqlite3.connect(filename)
                cursor = conn.cursor()
                
                # Get all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                self.clear_diagram()
                
                for table in tables:
                    table_name = table[0]
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
                
                conn.close()
                
                if len(self.tables) == 0:
                    messagebox.showinfo("Info", "No tables found in database")
                else:
                    self.layout_tables()
                    self.draw_connections()
                    self.status_label.config(text=f"Loaded: {filename} ({len(self.tables)} tables)")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open database: {str(e)}")
    
    def open_sql_file(self):
        filename = filedialog.askopenfilename(
            title="Open SQL File",
            filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")]
        )
        if filename:
            try:
                # Try different encodings
                encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
                sql_content = None
                
                for encoding in encodings:
                    try:
                        with open(filename, 'r', encoding=encoding) as f:
                            sql_content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if sql_content is None:
                    raise Exception("Could not decode file with any supported encoding")
                
                self.parse_sql(sql_content)
                self.layout_tables()
                self.draw_connections()
                self.status_label.config(text=f"Loaded: {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open SQL file: {str(e)}")
    
    def parse_sql(self, sql_content):
        self.clear_diagram()
        
        # Remove comments first
        sql_content = re.sub(r'--[^\n]*', '', sql_content)
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
        
        # Find all CREATE TABLE statements with a more flexible approach
        # Match CREATE TABLE ... ( ... ); allowing for optional elements
        pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[\[\`\"\']?(\w+)[\]\`\"\']?\s*\(((?:[^()]+|\([^()]*\))*)\)\s*;?'
        matches = re.finditer(pattern, sql_content, re.IGNORECASE | re.DOTALL)
        
        tables_found = 0
        for match in matches:
            table_name = match.group(1)
            columns_str = match.group(2)
            
            col_list = []
            fk_list = []
            
            # Split by comma, but be careful with commas inside parentheses
            lines = []
            current_line = ""
            paren_count = 0
            
            for char in columns_str + ',':
                if char == '(':
                    paren_count += 1
                    current_line += char
                elif char == ')':
                    paren_count -= 1
                    current_line += char
                elif char == ',' and paren_count == 0:
                    if current_line.strip():
                        lines.append(current_line.strip())
                    current_line = ""
                else:
                    current_line += char
            
            for line in lines:
                if not line:
                    continue
                
                # Parse FOREIGN KEY constraints
                if re.search(r'FOREIGN\s+KEY', line, re.IGNORECASE):
                    fk_match = re.search(r'FOREIGN\s+KEY\s*\(\s*[\[\`\"\']?(\w+)[\]\`\"\']?\s*\)\s*REFERENCES\s+[\[\`\"\']?(\w+)[\]\`\"\']?\s*\(\s*[\[\`\"\']?(\w+)[\]\`\"\']?\s*\)', line, re.IGNORECASE)
                    if fk_match:
                        fk_list.append({
                            'column': fk_match.group(1),
                            'ref_table': fk_match.group(2),
                            'ref_column': fk_match.group(3)
                        })
                    continue
                
                # Skip other constraints
                if re.match(r'^\s*(PRIMARY KEY|UNIQUE|CHECK|CONSTRAINT|KEY|INDEX)\s*\(', line, re.IGNORECASE):
                    continue
                
                # Parse column definition
                col_match = re.match(r'^\s*[\[\`\"\']?(\w+)[\]\`\"\']?\s+(\w+(?:\s*\(\s*\d+\s*(?:,\s*\d+\s*)?\))?)(.*)', line, re.IGNORECASE)
                if col_match:
                    col_name = col_match.group(1)
                    col_type = col_match.group(2).strip()
                    col_constraints = col_match.group(3) if col_match.group(3) else ""
                    
                    is_pk = bool(re.search(r'PRIMARY\s+KEY', col_constraints, re.IGNORECASE))
                    
                    # Check for inline REFERENCES
                    fk_match = re.search(r'REFERENCES\s+[\[\`\"\']?(\w+)[\]\`\"\']?\s*\(\s*[\[\`\"\']?(\w+)[\]\`\"\']?\s*\)', col_constraints, re.IGNORECASE)
                    if fk_match:
                        fk_list.append({
                            'column': col_name,
                            'ref_table': fk_match.group(1),
                            'ref_column': fk_match.group(2)
                        })
                    
                    col_list.append({
                        'name': col_name,
                        'type': col_type,
                        'primary_key': is_pk
                    })
            
            if col_list:
                self.add_table(table_name, col_list, fk_list)
                tables_found += 1
        
        if tables_found == 0:
            messagebox.showinfo("Info", "No CREATE TABLE statements found in SQL file.\nMake sure each CREATE TABLE statement ends with );")
        
    def add_table(self, name, columns, foreign_keys):
        self.tables[name] = {
            'name': name,
            'columns': columns,
            'foreign_keys': foreign_keys,
            'x': 0,
            'y': 0,
            'width': 0,
            'height': 0
        }
    
    def layout_tables(self):
        num_tables = len(self.tables)
        if num_tables == 0:
            return
        
        cols = math.ceil(math.sqrt(num_tables))
        x_spacing = 250
        y_spacing = 300
        start_x = 50
        start_y = 50
        
        # Sort tables alphabetically for consistent layout
        sorted_tables = sorted(self.tables.items(), key=lambda x: x[0])
        
        for idx, (name, table) in enumerate(sorted_tables):
            row = idx // cols
            col = idx % cols
            table['x'] = start_x + col * x_spacing
            table['y'] = start_y + row * y_spacing
        
        self.draw_tables()
    
    def draw_tables(self):
        self.canvas.delete("all")
        
        # FIRST draw connections (in background)
        self.draw_connections()
        
        # THEN draw tables (on top)
        for name, table in self.tables.items():
            x = table['x']
            y = table['y']
            
            # Calculate height
            header_height = 25
            row_height = 20
            table_height = header_height + len(table['columns']) * row_height
            table_width = 200
            
            table['width'] = table_width
            table['height'] = table_height
            
            # Draw table rectangle
            rect = self.canvas.create_rectangle(
                x, y, x + table_width, y + table_height,
                fill="#ffffff",
                outline="#000000",
                width=2,
                tags=("table", name)
            )
            
            # Draw header
            header = self.canvas.create_rectangle(
                x, y, x + table_width, y + header_height,
                fill=self.title_bg,
                outline="#000000",
                width=1,
                tags=("table", name)
            )
            
            # Table name
            self.canvas.create_text(
                x + table_width // 2, y + header_height // 2,
                text=name,
                fill=self.title_fg,
                font=("MS Sans Serif", 10, "bold"),
                tags=("table", name)
            )
            
            # Draw columns
            for idx, col in enumerate(table['columns']):
                col_y = y + header_height + idx * row_height
                
                # Draw separator line
                self.canvas.create_line(
                    x, col_y, x + table_width, col_y,
                    fill="#c0c0c0",
                    tags=("table", name)
                )
                
                # Column text
                pk_marker = "[PK] " if col['primary_key'] else ""
                col_text = f"{pk_marker}{col['name']}: {col['type']}"
                
                self.canvas.create_text(
                    x + 5, col_y + row_height // 2,
                    text=col_text,
                    anchor="w",
                    fill="#000000",
                    font=("MS Sans Serif", 8),
                    tags=("table", name)
                )
    
    def draw_connections(self):
        self.canvas.delete("connection")
        
        for name, table in self.tables.items():
            for fk in table['foreign_keys']:
                if fk['ref_table'] in self.tables:
                    self.draw_connection(name, fk['ref_table'])
    
    def draw_connection(self, from_table, to_table):
        if from_table not in self.tables or to_table not in self.tables:
            return
        
        t1 = self.tables[from_table]
        t2 = self.tables[to_table]
        
        # Calculate connection points (center right of from_table to center left of to_table)
        x1 = t1['x'] + t1['width']
        y1 = t1['y'] + t1['height'] // 2
        
        x2 = t2['x']
        y2 = t2['y'] + t2['height'] // 2
        
        # Draw line with better visibility
        self.canvas.create_line(
            x1, y1, x2, y2,
            fill="#ff0000",  # RED pentru mai bună vizibilitate
            width=3,  # Mai groasă
            arrow=tk.LAST,
            tags="connection",
            smooth=True  # Linie mai smooth
        )
        
        # Add a circle at the start point
        self.canvas.create_oval(
            x1-4, y1-4, x1+4, y1+4,
            fill="#ff0000",
            outline="#ff0000",
            tags="connection"
        )
    
    def clear_diagram(self):
        self.tables = {}
        self.canvas.delete("all")
        self.status_label.config(text="Diagram cleared")
    
    def on_mouse_down(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in items:
            tags = self.canvas.gettags(item)
            if "table" in tags:
                for tag in tags:
                    if tag in self.tables:
                        self.dragging = tag
                        self.drag_start_x = x - self.tables[tag]['x']
                        self.drag_start_y = y - self.tables[tag]['y']
                        break
                break
    
    def on_mouse_move(self, event):
        if self.dragging:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            
            self.tables[self.dragging]['x'] = x - self.drag_start_x
            self.tables[self.dragging]['y'] = y - self.drag_start_y
            
            self.draw_tables()
            self.draw_connections()
    
    def on_mouse_up(self, event):
        self.dragging = None
    
    def on_mouse_wheel(self, event):
        # Handle mouse wheel scrolling
        if event.num == 5 or event.delta < 0:
            # Scroll down
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            # Scroll up
            self.canvas.yview_scroll(-1, "units")

if __name__ == "__main__":
    rootsqldiagR = tk.Tk()
    app = Win95SQLDiagram(rootsqldiagR)
    rootsqldiagR.mainloop()