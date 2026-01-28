#!/usr/bin/env python3
"""
Offline Database Designer - Windows 95 Style
A retro database design tool with classic Windows 95 aesthetics
"""

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import json
import os

# Windows 95 Color Scheme
WIN95_BG = "#c0c0c0"
WIN95_FG = "#000000"
WIN95_BUTTON_FACE = "#c0c0c0"
WIN95_BUTTON_SHADOW = "#808080"
WIN95_BUTTON_HIGHLIGHT = "#ffffff"
WIN95_ACTIVE_TITLE = "#000080"
WIN95_INACTIVE_TITLE = "#808080"
WIN95_TITLE_TEXT = "#ffffff"
WIN95_WINDOW_BG = "#ffffff"
WIN95_BORDER = "#000000"


class Table:
    """Represents a database table"""
    def __init__(self, name, x=100, y=100):
        self.name = name
        self.x = x
        self.y = y
        self.columns = []
        self.primary_key = None
        
    def add_column(self, name, data_type, nullable=True, unique=False):
        self.columns.append({
            'name': name,
            'type': data_type,
            'nullable': nullable,
            'unique': unique
        })
    
    def remove_column(self, index):
        if 0 <= index < len(self.columns):
            del self.columns[index]
    
    def to_dict(self):
        return {
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'columns': self.columns,
            'primary_key': self.primary_key
        }
    
    @staticmethod
    def from_dict(data):
        table = Table(data['name'], data['x'], data['y'])
        table.columns = data['columns']
        table.primary_key = data.get('primary_key')
        return table


class Relationship:
    """Represents a relationship between tables"""
    def __init__(self, from_table, to_table, rel_type="1:N"):
        self.from_table = from_table
        self.to_table = to_table
        self.rel_type = rel_type  # 1:1, 1:N, N:N
    
    def to_dict(self):
        return {
            'from_table': self.from_table,
            'to_table': self.to_table,
            'rel_type': self.rel_type
        }
    
    @staticmethod
    def from_dict(data):
        return Relationship(data['from_table'], data['to_table'], data['rel_type'])


class Win95Frame(tk.Frame):
    """A Windows 95 styled frame with raised border"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg=WIN95_BG, relief=tk.RAISED, bd=2)


class Win95Button(tk.Button):
    """A Windows 95 styled button"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(
            bg=WIN95_BUTTON_FACE,
            fg=WIN95_FG,
            relief=tk.RAISED,
            bd=2,
            activebackground=WIN95_BG,
            font=('MS Sans Serif', 8)
        )


class Win95Label(tk.Label):
    """A Windows 95 styled label"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(
            bg=WIN95_BG,
            fg=WIN95_FG,
            font=('MS Sans Serif', 8)
        )


class Win95Entry(tk.Entry):
    """A Windows 95 styled entry"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(
            bg=WIN95_WINDOW_BG,
            fg=WIN95_FG,
            relief=tk.SUNKEN,
            bd=2,
            font=('MS Sans Serif', 8)
        )


class Win95Listbox(tk.Listbox):
    """A Windows 95 styled listbox"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(
            bg=WIN95_WINDOW_BG,
            fg=WIN95_FG,
            relief=tk.SUNKEN,
            bd=2,
            font=('MS Sans Serif', 8),
            selectbackground=WIN95_ACTIVE_TITLE,
            selectforeground=WIN95_TITLE_TEXT
        )


class TableDialog(tk.Toplevel):
    """Dialog for creating/editing tables"""
    def __init__(self, parent, table=None):
        super().__init__(parent)
        self.title("Table Properties")
        self.geometry("450x400")
        self.config(bg=WIN95_BG)
        self.resizable(False, False)
        
        self.result = None
        self.table = table
        
        # Table name
        name_frame = Win95Frame(self)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Label(name_frame, text="Table Name:").pack(side=tk.LEFT, padx=5)
        self.name_entry = Win95Entry(name_frame, width=30)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
        if table:
            self.name_entry.insert(0, table.name)
        
        # Columns section
        columns_frame = Win95Frame(self)
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        Win95Label(columns_frame, text="Columns:").pack(anchor=tk.W, padx=5, pady=5)
        
        # Listbox with scrollbar
        list_frame = tk.Frame(columns_frame, bg=WIN95_BG)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.columns_list = Win95Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.columns_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.columns_list.yview)
        
        # Load existing columns
        self.columns_data = []
        if table:
            for col in table.columns:
                self.columns_data.append(col.copy())
                self.update_columns_list()
        
        # Column buttons
        btn_frame = Win95Frame(columns_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Button(btn_frame, text="Add Column", command=self.add_column).pack(side=tk.LEFT, padx=2)
        Win95Button(btn_frame, text="Edit Column", command=self.edit_column).pack(side=tk.LEFT, padx=2)
        Win95Button(btn_frame, text="Remove Column", command=self.remove_column).pack(side=tk.LEFT, padx=2)
        
        # OK/Cancel buttons
        bottom_frame = Win95Frame(self)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Button(bottom_frame, text="OK", width=10, command=self.ok).pack(side=tk.RIGHT, padx=2)
        Win95Button(bottom_frame, text="Cancel", width=10, command=self.cancel).pack(side=tk.RIGHT, padx=2)
        
        self.transient(parent)
        self.grab_set()
        
    def update_columns_list(self):
        self.columns_list.delete(0, tk.END)
        for col in self.columns_data:
            pk_mark = " [PK]" if col.get('is_pk', False) else ""
            nullable = "" if col['nullable'] else " NOT NULL"
            unique = " UNIQUE" if col.get('unique', False) else ""
            text = f"{col['name']} - {col['type']}{nullable}{unique}{pk_mark}"
            self.columns_list.insert(tk.END, text)
    
    def add_column(self):
        dialog = ColumnDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.columns_data.append(dialog.result)
            self.update_columns_list()
    
    def edit_column(self):
        selection = self.columns_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a column to edit")
            return
        
        index = selection[0]
        dialog = ColumnDialog(self, self.columns_data[index])
        self.wait_window(dialog)
        if dialog.result:
            self.columns_data[index] = dialog.result
            self.update_columns_list()
    
    def remove_column(self):
        selection = self.columns_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a column to remove")
            return
        
        if messagebox.askyesno("Confirm", "Remove selected column?"):
            del self.columns_data[selection[0]]
            self.update_columns_list()
    
    def ok(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Table name is required")
            return
        
        if not self.columns_data:
            messagebox.showerror("Error", "Table must have at least one column")
            return
        
        # Find primary key
        pk = None
        for i, col in enumerate(self.columns_data):
            if col.get('is_pk', False):
                pk = i
                break
        
        self.result = {
            'name': name,
            'columns': self.columns_data,
            'primary_key': pk
        }
        self.destroy()
    
    def cancel(self):
        self.destroy()


class ColumnDialog(tk.Toplevel):
    """Dialog for creating/editing columns"""
    def __init__(self, parent, column=None):
        super().__init__(parent)
        self.title("Column Properties")
        self.geometry("350x220")
        self.config(bg=WIN95_BG)
        self.resizable(False, False)
        
        self.result = None
        
        # Column name
        name_frame = Win95Frame(self)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Label(name_frame, text="Name:").pack(side=tk.LEFT, padx=5)
        self.name_entry = Win95Entry(name_frame, width=25)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
        # Data type
        type_frame = Win95Frame(self)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Label(type_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.type_var = tk.StringVar(value="VARCHAR(255)")
        types = ["INT", "VARCHAR(255)", "TEXT", "DATE", "DATETIME", "BOOLEAN", "DECIMAL", "FLOAT"]
        type_menu = tk.OptionMenu(type_frame, self.type_var, *types)
        type_menu.config(bg=WIN95_BUTTON_FACE, relief=tk.RAISED, bd=2)
        type_menu.pack(side=tk.LEFT, padx=5)
        
        # Checkboxes
        check_frame = Win95Frame(self)
        check_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.nullable_var = tk.BooleanVar(value=True)
        self.unique_var = tk.BooleanVar(value=False)
        self.pk_var = tk.BooleanVar(value=False)
        
        tk.Checkbutton(check_frame, text="Nullable", variable=self.nullable_var,
                      bg=WIN95_BG, fg=WIN95_FG, selectcolor=WIN95_WINDOW_BG).pack(anchor=tk.W, padx=10)
        tk.Checkbutton(check_frame, text="Unique", variable=self.unique_var,
                      bg=WIN95_BG, fg=WIN95_FG, selectcolor=WIN95_WINDOW_BG).pack(anchor=tk.W, padx=10)
        tk.Checkbutton(check_frame, text="Primary Key", variable=self.pk_var,
                      bg=WIN95_BG, fg=WIN95_FG, selectcolor=WIN95_WINDOW_BG).pack(anchor=tk.W, padx=10)
        
        # Load existing data
        if column:
            self.name_entry.insert(0, column['name'])
            self.type_var.set(column['type'])
            self.nullable_var.set(column['nullable'])
            self.unique_var.set(column.get('unique', False))
            self.pk_var.set(column.get('is_pk', False))
        
        # Buttons
        btn_frame = Win95Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Button(btn_frame, text="OK", width=10, command=self.ok).pack(side=tk.RIGHT, padx=2)
        Win95Button(btn_frame, text="Cancel", width=10, command=self.cancel).pack(side=tk.RIGHT, padx=2)
        
        self.transient(parent)
        self.grab_set()
    
    def ok(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Column name is required")
            return
        
        self.result = {
            'name': name,
            'type': self.type_var.get(),
            'nullable': self.nullable_var.get(),
            'unique': self.unique_var.get(),
            'is_pk': self.pk_var.get()
        }
        self.destroy()
    
    def cancel(self):
        self.destroy()


class DatabaseDesigner:
    """Main application window"""
    def __init__(self, rootsqldesg):
        self.rootsqldesg = rootsqldesg
        self.rootsqldesg.title("Database Designer - Untitled")
        self.rootsqldesg.geometry("900x600")
        self.rootsqldesg.config(bg=WIN95_BG)
        
        self.tables = {}
        self.relationships = []
        self.current_file = None
        self.selected_table = None
        self.selected_relationship = None
        self.drag_data = {"x": 0, "y": 0, "item": None}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.rootsqldesg, bg=WIN95_BG, fg=WIN95_FG)
        self.rootsqldesg.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=WIN95_BG, fg=WIN95_FG)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_database)
        file_menu.add_command(label="Open...", command=self.open_database)
        file_menu.add_command(label="Save", command=self.save_database)
        file_menu.add_command(label="Save As...", command=self.save_database_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export SQL...", command=self.export_sql)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.rootsqldesg.destroy)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=WIN95_BG, fg=WIN95_FG)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Table", command=self.add_table)
        edit_menu.add_command(label="Edit Table", command=self.edit_table)
        edit_menu.add_command(label="Delete Table", command=self.delete_table)
        edit_menu.add_separator()
        edit_menu.add_command(label="Add Relationship", command=self.add_relationship)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=WIN95_BG, fg=WIN95_FG)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Toolbar
        toolbar = Win95Frame(self.rootsqldesg)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        Win95Button(toolbar, text="New", width=8, command=self.new_database).pack(side=tk.LEFT, padx=2)
        Win95Button(toolbar, text="Open", width=8, command=self.open_database).pack(side=tk.LEFT, padx=2)
        Win95Button(toolbar, text="Save", width=8, command=self.save_database).pack(side=tk.LEFT, padx=2)
        
        tk.Frame(toolbar, width=2, bg=WIN95_BUTTON_SHADOW).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        Win95Button(toolbar, text="Add Table", width=10, command=self.add_table).pack(side=tk.LEFT, padx=2)
        Win95Button(toolbar, text="Edit Table", width=10, command=self.edit_table).pack(side=tk.LEFT, padx=2)
        Win95Button(toolbar, text="Delete", width=8, command=self.delete_table).pack(side=tk.LEFT, padx=2)
        
        tk.Frame(toolbar, width=2, bg=WIN95_BUTTON_SHADOW).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        Win95Button(toolbar, text="Relationship", width=12, command=self.add_relationship).pack(side=tk.LEFT, padx=2)
        self.edit_rel_button = Win95Button(toolbar, text="Edit Relationship", command=self.edit_relationship, state=tk.DISABLED)
        self.edit_rel_button.pack(side=tk.LEFT, padx=2)
                
        # Main container
        main_container = Win95Frame(self.rootsqldesg)
        main_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Canvas for drawing
        canvas_frame = Win95Frame(main_container)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg=WIN95_WINDOW_BG, relief=tk.SUNKEN, bd=2)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        
        # Status bar
        status_frame = Win95Frame(self.rootsqldesg)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)
        
        self.status_label = Win95Label(status_frame, text="Ready", anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def draw_table(self, table):
        """Draw a table on the canvas"""
        # Clear existing representation
        self.canvas.delete(f"table_{table.name}")
        
        x, y = table.x, table.y
        width = 200
        header_height = 25
        row_height = 20
        height = header_height + len(table.columns) * row_height + 10
        
        # Table border
        is_selected = self.selected_table == table.name
        border_color = WIN95_ACTIVE_TITLE if is_selected else WIN95_BORDER
        border_width = 2 if is_selected else 1
        
        self.canvas.create_rectangle(x, y, x + width, y + height,
                                     fill=WIN95_WINDOW_BG, outline=border_color,
                                     width=border_width, tags=f"table_{table.name}")
        
        # Table header
        self.canvas.create_rectangle(x, y, x + width, y + header_height,
                                     fill=WIN95_ACTIVE_TITLE, outline=WIN95_BORDER,
                                     tags=f"table_{table.name}")
        self.canvas.create_text(x + width // 2, y + header_height // 2,
                               text=table.name, fill=WIN95_TITLE_TEXT,
                               font=('MS Sans Serif', 9, 'bold'),
                               tags=f"table_{table.name}")
        
        # Columns
        current_y = y + header_height + 5
        for i, col in enumerate(table.columns):
            pk_mark = "[PK] " if table.primary_key == i else ""
            col_text = f"{pk_mark}{col['name']}: {col['type']}"
            self.canvas.create_text(x + 10, current_y,
                                   text=col_text, anchor=tk.W,
                                   font=('MS Sans Serif', 8),
                                   tags=f"table_{table.name}")
            current_y += row_height
    
    def draw_relationship(self, rel):
        """Draw a relationship line between tables"""
        if rel.from_table not in self.tables or rel.to_table not in self.tables:
            return
        
        from_table = self.tables[rel.from_table]
        to_table = self.tables[rel.to_table]
        
        # Calculate connection points (center right/left of tables)
        from_x = from_table.x + 200
        from_y = from_table.y + 25
        to_x = to_table.x
        to_y = to_table.y + 25
        
        # Draw line
        self.canvas.create_line(from_x, from_y, to_x, to_y,
                               fill=WIN95_FG, width=2, tags="relationship")
        
        # Draw relationship type
        mid_x = (from_x + to_x) // 2
        mid_y = (from_y + to_y) // 2
        self.canvas.create_text(mid_x, mid_y - 10, text=rel.rel_type,
                               font=('MS Sans Serif', 8), tags="relationship")
    
    def redraw_all(self):
        """Redraw all tables and relationships"""
        self.canvas.delete("all")
        
        # Draw relationships first (behind tables)
        for rel in self.relationships:
            if rel.from_table in self.tables and rel.to_table in self.tables:
                from_table = self.tables[rel.from_table]
                to_table = self.tables[rel.to_table]
                
                x1 = from_table.x + 75
                y1 = from_table.y + 15
                x2 = to_table.x + 75
                y2 = to_table.y + 15
                
                # Highlight if selected
                color = "red" if rel == self.selected_relationship else "blue"
                width = 3 if rel == self.selected_relationship else 2
                
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, arrow=tk.LAST)
                
                # Label
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                self.canvas.create_text(mid_x, mid_y - 10, text=rel.rel_type, 
                                       fill="blue", font=('MS Sans Serif', 8))
        
        # Draw tables
        for table in self.tables.values():
            self.draw_table(table)
        
        self.update_status(f"{len(self.tables)} tables, {len(self.relationships)} relationships")
        
        # Update button states
        if self.selected_relationship:
            self.edit_rel_button.config(state=tk.NORMAL)
        else:
            self.edit_rel_button.config(state=tk.DISABLED)
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        # Find clicked table
        clicked = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        
        self.selected_table = None
        for item in clicked:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("table_"):
                    table_name = tag[6:]
                    self.selected_table = table_name
                    self.drag_data["item"] = table_name
                    self.drag_data["x"] = event.x
                    self.drag_data["y"] = event.y
                    break
                    
        # Check if clicked on a relationship line
        clicked_rel = None
        for rel in self.relationships:
            if rel.from_table in self.tables and rel.to_table in self.tables:
                from_table = self.tables[rel.from_table]
                to_table = self.tables[rel.to_table]
                
                # Simple line click detection (within 5 pixels)
                x1, y1 = from_table.x + 75, from_table.y + 15
                x2, y2 = to_table.x + 75, to_table.y + 15
                
                # Distance from point to line segment
                if self.point_to_line_distance(event.x, event.y, x1, y1, x2, y2) < 5:
                    clicked_rel = rel
                    break

        if clicked_rel:
            self.selected_table = None
            self.selected_relationship = clicked_rel
            self.redraw_all()
        
        self.redraw_all()
    
    def point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Calculate distance from point to line segment"""
        line_len_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if line_len_sq == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_len_sq))
        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)
        
        return ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5
        
    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        if self.drag_data["item"]:
            table_name = self.drag_data["item"]
            if table_name in self.tables:
                dx = event.x - self.drag_data["x"]
                dy = event.y - self.drag_data["y"]
                
                self.tables[table_name].x += dx
                self.tables[table_name].y += dy
                
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                
                self.redraw_all()
    
    def on_canvas_release(self, event):
        """Handle canvas release"""
        self.drag_data["item"] = None
    
    def on_canvas_double_click(self, event):
        """Handle double click to edit table"""
        if self.selected_table:
            self.edit_table()
    
    def new_database(self):
        """Create a new database"""
        if messagebox.askyesno("New Database", "Create new database? Unsaved changes will be lost."):
            self.tables = {}
            self.relationships = []
            self.current_file = None
            self.selected_table = None
            self.rootsqldesg.title("Database Designer - Untitled")
            self.redraw_all()
    
    def add_table(self):
        """Add a new table"""
        dialog = TableDialog(self.rootsqldesg)
        self.rootsqldesg.wait_window(dialog)
        
        if dialog.result:
            name = dialog.result['name']
            if name in self.tables:
                messagebox.showerror("Error", f"Table '{name}' already exists")
                return
            
            # Find a good position for new table
            x = 50 + (len(self.tables) % 3) * 250
            y = 50 + (len(self.tables) // 3) * 200
            
            table = Table(name, x, y)
            table.columns = dialog.result['columns']
            table.primary_key = dialog.result['primary_key']
            
            self.tables[name] = table
            self.redraw_all()
    
    def edit_table(self):
        """Edit selected table"""
        if not self.selected_table:
            messagebox.showwarning("Warning", "Please select a table to edit")
            return
        
        table = self.tables[self.selected_table]
        dialog = TableDialog(self.rootsqldesg, table)
        self.rootsqldesg.wait_window(dialog)
        
        if dialog.result:
            old_name = self.selected_table
            new_name = dialog.result['name']
            
            # Update table
            table.name = new_name
            table.columns = dialog.result['columns']
            table.primary_key = dialog.result['primary_key']
            
            # If name changed, update dictionary
            if old_name != new_name:
                if new_name in self.tables and new_name != old_name:
                    messagebox.showerror("Error", f"Table '{new_name}' already exists")
                    table.name = old_name
                    return
                
                del self.tables[old_name]
                self.tables[new_name] = table
                self.selected_table = new_name
                
                # Update relationships
                for rel in self.relationships:
                    if rel.from_table == old_name:
                        rel.from_table = new_name
                    if rel.to_table == old_name:
                        rel.to_table = new_name
            
            self.redraw_all()
    
    def delete_table(self):
        """Delete selected table"""
        if not self.selected_table:
            messagebox.showwarning("Warning", "Please select a table to delete")
            return
        
        if messagebox.askyesno("Confirm", f"Delete table '{self.selected_table}'?"):
            # Remove relationships involving this table
            self.relationships = [r for r in self.relationships 
                                 if r.from_table != self.selected_table 
                                 and r.to_table != self.selected_table]
            
            del self.tables[self.selected_table]
            self.selected_table = None
            self.redraw_all()
    
    def add_relationship(self):
        """Add a relationship between tables"""
        if len(self.tables) < 2:
            messagebox.showwarning("Warning", "Need at least 2 tables to create a relationship")
            return
        
        dialog = RelationshipDialog(self.rootsqldesg, list(self.tables.keys()))
        self.rootsqldesg.wait_window(dialog)
        
        if dialog.result:
            rel = Relationship(dialog.result['from'], dialog.result['to'], dialog.result['type'])
            self.relationships.append(rel)
            self.redraw_all()
    
    def save_database(self):
        """Save database to file"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_database_as()
    
    def edit_relationship(self):
        """Edit or delete selected relationship"""
        if not self.selected_relationship:
            return
        
        dialog = RelationshipEditDialog(self.rootsqldesg, self.selected_relationship, 
                                        list(self.tables.keys()))
        self.rootsqldesg.wait_window(dialog)
        
        if dialog.result == 'delete':
            self.relationships.remove(self.selected_relationship)
            self.selected_relationship = None
            self.redraw_all()
        elif dialog.result:
            self.selected_relationship.from_table = dialog.result['from']
            self.selected_relationship.to_table = dialog.result['to']
            self.selected_relationship.rel_type = dialog.result['type']
            self.redraw_all()
            
    def save_database_as(self):
        """Save database to new file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".dbdesign",
            filetypes=[("Database Design", "*.dbdesign"), ("All Files", "*.*")]
        )
        if filename:
            self._save_to_file(filename)
    
    def _save_to_file(self, filename):
        """Internal save method"""
        data = {
            'tables': [table.to_dict() for table in self.tables.values()],
            'relationships': [rel.to_dict() for rel in self.relationships]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.current_file = filename
            self.rootsqldesg.title(f"Database Designer - {os.path.basename(filename)}")
            self.update_status(f"Saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def open_database(self):
        """Open database from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Database Design", "*.dbdesign"), ("All Files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                self.tables = {}
                for table_data in data['tables']:
                    table = Table.from_dict(table_data)
                    self.tables[table.name] = table
                
                self.relationships = [Relationship.from_dict(r) for r in data['relationships']]
                self.current_file = filename
                self.rootsqldesg.title(f"Database Designer - {os.path.basename(filename)}")
                self.redraw_all()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open: {str(e)}")
    
    def export_sql(self):
        """Export database schema as SQL"""
        if not self.tables:
            messagebox.showwarning("Warning", "No tables to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".sql",
            filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("-- Database Schema Export\n")
                    f.write("-- Generated by Database Designer\n\n")
                    
                    for table in self.tables.values():
                        f.write(f"CREATE TABLE {table.name} (\n")
                        
                        cols = []
                        for i, col in enumerate(table.columns):
                            col_def = f"    {col['name']} {col['type']}"
                            if not col['nullable']:
                                col_def += " NOT NULL"
                            if col.get('unique', False):
                                col_def += " UNIQUE"
                            if table.primary_key == i:
                                col_def += " PRIMARY KEY"
                            cols.append(col_def)
                        
                        f.write(",\n".join(cols))
                        f.write("\n);\n\n")
                    
                    # Add foreign key constraints based on relationships
                    for rel in self.relationships:
                        if rel.rel_type in ["1:N", "1:1"]:
                            f.write(f"-- Relationship: {rel.from_table} {rel.rel_type} {rel.to_table}\n")
                            f.write(f"-- ALTER TABLE {rel.to_table} ADD FOREIGN KEY ({rel.from_table}_id) ")
                            f.write(f"REFERENCES {rel.from_table}(id);\n\n")
                
                self.update_status(f"Exported to {filename}")
                messagebox.showinfo("Success", f"SQL exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About Database Designer",
                           "Database Designer v1.0\n\n"
                           "Design your database schema with tables,\n"
                           "columns, and relationships.")


class RelationshipDialog(tk.Toplevel):
    """Dialog for creating relationships"""
    def __init__(self, parent, table_names):
        super().__init__(parent)
        self.title("Add Relationship")
        self.geometry("300x180")
        self.config(bg=WIN95_BG)
        self.resizable(False, False)
        
        self.result = None
        
        # From table
        from_frame = Win95Frame(self)
        from_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Label(from_frame, text="From Table:").pack(side=tk.LEFT, padx=5)
        self.from_var = tk.StringVar(value=table_names[0] if table_names else "")
        from_menu = tk.OptionMenu(from_frame, self.from_var, *table_names)
        from_menu.config(bg=WIN95_BUTTON_FACE, relief=tk.RAISED, bd=2)
        from_menu.pack(side=tk.LEFT, padx=5)
        
        # To table
        to_frame = Win95Frame(self)
        to_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Label(to_frame, text="To Table:").pack(side=tk.LEFT, padx=5)
        self.to_var = tk.StringVar(value=table_names[1] if len(table_names) > 1 else table_names[0])
        to_menu = tk.OptionMenu(to_frame, self.to_var, *table_names)
        to_menu.config(bg=WIN95_BUTTON_FACE, relief=tk.RAISED, bd=2)
        to_menu.pack(side=tk.LEFT, padx=5)
        
        # Relationship type
        type_frame = Win95Frame(self)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Label(type_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.type_var = tk.StringVar(value="1:N")
        type_menu = tk.OptionMenu(type_frame, self.type_var, "1:1", "1:N", "N:N")
        type_menu.config(bg=WIN95_BUTTON_FACE, relief=tk.RAISED, bd=2)
        type_menu.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        btn_frame = Win95Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Button(btn_frame, text="OK", width=10, command=self.ok).pack(side=tk.RIGHT, padx=2)
        Win95Button(btn_frame, text="Cancel", width=10, command=self.cancel).pack(side=tk.RIGHT, padx=2)
        
        self.transient(parent)
        self.grab_set()
    
    def ok(self):
        from_table = self.from_var.get()
        to_table = self.to_var.get()
        
        if from_table == to_table:
            messagebox.showwarning("Warning", "Cannot create relationship to same table")
            return
        
        self.result = {
            'from': from_table,
            'to': to_table,
            'type': self.type_var.get()
        }
        self.destroy()
    
    def cancel(self):
        self.destroy()

class RelationshipEditDialog(tk.Toplevel):
    """Dialog for editing relationships"""
    def __init__(self, parent, relationship, table_names):
        super().__init__(parent)
        self.title("Edit Relationship")
        self.geometry("300x220")
        self.config(bg=WIN95_BG)
        self.resizable(False, False)
        
        self.result = None
        
        # From table
        from_frame = Win95Frame(self)
        from_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Label(from_frame, text="From Table:").pack(side=tk.LEFT, padx=5)
        self.from_var = tk.StringVar(value=relationship.from_table)
        from_menu = tk.OptionMenu(from_frame, self.from_var, *table_names)
        from_menu.config(bg=WIN95_BUTTON_FACE, relief=tk.RAISED, bd=2)
        from_menu.pack(side=tk.LEFT, padx=5)
        
        # To table
        to_frame = Win95Frame(self)
        to_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Label(to_frame, text="To Table:").pack(side=tk.LEFT, padx=5)
        self.to_var = tk.StringVar(value=relationship.to_table)
        to_menu = tk.OptionMenu(to_frame, self.to_var, *table_names)
        to_menu.config(bg=WIN95_BUTTON_FACE, relief=tk.RAISED, bd=2)
        to_menu.pack(side=tk.LEFT, padx=5)
        
        # Relationship type
        type_frame = Win95Frame(self)
        type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Label(type_frame, text="Type:").pack(side=tk.LEFT, padx=5)
        self.type_var = tk.StringVar(value=relationship.rel_type)
        type_menu = tk.OptionMenu(type_frame, self.type_var, "1:1", "1:N", "N:N")
        type_menu.config(bg=WIN95_BUTTON_FACE, relief=tk.RAISED, bd=2)
        type_menu.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        btn_frame = Win95Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        Win95Button(btn_frame, text="OK", width=10, command=self.ok).pack(side=tk.RIGHT, padx=2)
        Win95Button(btn_frame, text="Delete", width=10, command=self.delete).pack(side=tk.RIGHT, padx=2)
        Win95Button(btn_frame, text="Cancel", width=10, command=self.cancel).pack(side=tk.RIGHT, padx=2)
        
        self.transient(parent)
        self.grab_set()
    
    def ok(self):
        from_table = self.from_var.get()
        to_table = self.to_var.get()
        
        if from_table == to_table:
            messagebox.showwarning("Warning", "Cannot create relationship to same table")
            return
        
        self.result = {
            'from': from_table,
            'to': to_table,
            'type': self.type_var.get()
        }
        self.destroy()
    
    def delete(self):
        if messagebox.askyesno("Confirm", "Delete this relationship?"):
            self.result = 'delete'
            self.destroy()
    
    def cancel(self):
        self.destroy()
def main():
    rootsqldesg = tk.Tk()
    app = DatabaseDesigner(rootsqldesg)
    rootsqldesg.mainloop()


if __name__ == "__main__":
    main()
