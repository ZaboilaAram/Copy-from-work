import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, colorchooser, font as tkfont
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from datetime import datetime
import os
import re

class CustomTitleBar:
    """Windows 95 style title bar"""
    def __init__(self, parent, title):
        self.parent = parent
        self.title_text = title
        
        self.parent.overrideredirect(True)
        
        self.parent.bind("<Map>", self.on_map)
        
        self.title_bar = tk.Frame(parent, bg="#000080", relief=tk.RAISED, bd=1)
        self.title_bar.pack(side=tk.TOP, fill=tk.X)
        
        self.title_label = tk.Label(self.title_bar, text="  " + title, 
                                     bg="#000080", fg="white", 
                                     font=("MS Sans Serif", 8, "bold"),
                                     anchor=tk.W)
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        
        self.btn_minimize = tk.Button(self.title_bar, text="_", width=3, 
                                      bg="#C0C0C0", font=("MS Sans Serif", 8, "bold"),
                                      relief=tk.RAISED, bd=1,
                                      command=self.minimize_window)
        self.btn_minimize.pack(side=tk.RIGHT, padx=1)
        
        self.btn_maximize = tk.Button(self.title_bar, text="□", width=3,
                                      bg="#C0C0C0", font=("MS Sans Serif", 7),
                                      relief=tk.RAISED, bd=1,
                                      command=self.maximize_window)
        self.btn_maximize.pack(side=tk.RIGHT, padx=1)
        
        self.btn_close = tk.Button(self.title_bar, text="X", width=3,
                                   bg="#C0C0C0", font=("MS Sans Serif", 8, "bold"),
                                   relief=tk.RAISED, bd=1,
                                   command=self.close_window)
        self.btn_close.pack(side=tk.RIGHT, padx=1)
        
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_move)
        self.title_label.bind("<Button-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.on_move)
        
        self.x = 0
        self.y = 0
        self.maximized = False
        
    def on_map(self, event):
        """Called when window is restored from minimized state"""
        # Small delay to ensure window is fully mapped
        self.parent.after(10, lambda: self.parent.overrideredirect(True))
        
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
        
    def on_move(self, event):
        if not self.maximized:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.parent.winfo_x() + deltax
            y = self.parent.winfo_y() + deltay
            self.parent.geometry(f"+{x}+{y}")
            
    def minimize_window(self):
        try:
            self.parent.iconify()
        except:
            # If iconify fails due to overrideredirect, use withdraw instead
            self.parent.withdraw()
            # Schedule restoration - add to taskbar alternative
            self.parent.after(100, lambda: self.parent.deiconify())
        
    def maximize_window(self):
        if not self.maximized:
            self.parent.state('zoomed')
            self.maximized = True
        else:
            self.parent.state('normal')
            self.maximized = False
            
    def close_window(self):
        self.parent.event_generate("<<AppClose>>")
        
    def set_title(self, title):
        self.title_label.config(text="  " + title)

class MO95Office:
    def __init__(self, rootmo95):
        self.rootmo95 = rootmo95
        self.rootmo95.title("Multiapp Office")
        self.rootmo95.geometry("1000x700")
        
        # Colors
        self.bg_color = "#C0C0C0"
        self.title_blue = "#000080"
        self.white = "#FFFFFF"
        self.gray_dark = "#808080"
        self.gray_light = "#DFDFDF"
        
        self.title_bar = CustomTitleBar(self.rootmo95, "Multiapp Office - Untitled")
        self.rootmo95.configure(bg=self.bg_color)
        
        # Document state
        self.current_file = None
        self.document_modified = False
        self.recent_files = []
        self.find_index = "1.0"
        self.tables = {}
        
        # Page margins in inches
        self.left_margin = 1.25
        self.right_margin = 1.25
        self.top_margin = 1.0
        self.bottom_margin = 1.0
        
        # Font state
        self.current_font_family = "Arial"
        self.current_font_size = 12
        
        # Margin padding mode (True = frame-based, False = tag-based)
        self.show_margin_padding = True
        
        self.create_menu()
        self.create_toolbar()
        self.create_format_bar()
        self.create_ruler()
        self.create_editor()
        self.create_statusbar()
        
        # Bind events
        self.text_editor.bind("<<Modified>>", self.on_text_modified)
        self.text_editor.bind("<Control-b>", lambda e: self.toggle_bold())
        self.text_editor.bind("<Control-i>", lambda e: self.toggle_italic())
        self.text_editor.bind("<Control-u>", lambda e: self.toggle_underline())
        self.text_editor.bind("<Control-f>", lambda e: self.find_text())
        self.text_editor.bind("<Control-h>", lambda e: self.replace_text())
        
        # Handle close event
        self.rootmo95.bind("<<AppClose>>", lambda e: self.exit_application())
        
        # Handle window resize to update margins
        self.rootmo95.bind("<Configure>", self.on_window_resize)
        
        self.load_recent_files()
        
    def create_menu(self):
        menubar = tk.Menu(self.rootmo95, bg=self.bg_color, relief=tk.FLAT, bd=0)
        self.rootmo95.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_document, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_document, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_document, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_as_document)
        file_menu.add_separator()
        
        self.recent_menu = tk.Menu(file_menu, tearoff=0, bg=self.bg_color)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Page Setup...", command=self.page_setup)
        file_menu.add_command(label="Print Preview", command=self.print_preview)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_application)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Delete", command=self.delete_selection)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Find...", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace...", command=self.replace_text, accelerator="Ctrl+H")
        
        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Adaugă opțiunea Show Margin Padding
        self.margin_padding_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Show Margin Padding", 
                                   variable=self.margin_padding_var,
                                   command=self.toggle_margin_padding)
        view_menu.add_separator()
        
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Normal View", command=self.normal_zoom)
        view_menu.add_separator()
        view_menu.add_command(label="Word Count", command=self.show_word_count)
        
        # Format Menu
        format_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Bold", command=self.toggle_bold, accelerator="Ctrl+B")
        format_menu.add_command(label="Italic", command=self.toggle_italic, accelerator="Ctrl+I")
        format_menu.add_command(label="Underline", command=self.toggle_underline, accelerator="Ctrl+U")
        format_menu.add_separator()
        
        align_menu = tk.Menu(format_menu, tearoff=0, bg=self.bg_color)
        format_menu.add_cascade(label="Alignment", menu=align_menu)
        align_menu.add_command(label="Align Left", command=lambda: self.set_alignment("left"))
        align_menu.add_command(label="Center", command=lambda: self.set_alignment("center"))
        align_menu.add_command(label="Align Right", command=lambda: self.set_alignment("right"))
        align_menu.add_command(label="Justify", command=lambda: self.set_alignment("justify"))
        
        format_menu.add_separator()
        format_menu.add_command(label="Font...", command=self.change_font)
        format_menu.add_command(label="Text Color...", command=self.change_text_color)
        format_menu.add_command(label="Highlight Color...", command=self.change_highlight_color)
        
        # Insert Menu
        insert_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Insert", menu=insert_menu)
        insert_menu.add_command(label="Table...", command=self.insert_table)
        insert_menu.add_command(label="Date and Time", command=self.insert_datetime)
        insert_menu.add_command(label="Page Break", command=self.insert_page_break)
        insert_menu.add_command(label="Horizontal Line", command=self.insert_horizontal_line)
        
        # Table Menu
        table_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Table", menu=table_menu)
        table_menu.add_command(label="Insert Table...", command=self.insert_table)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About Multiapp Office", command=self.show_about)
        
        # Keyboard shortcuts
        self.rootmo95.bind("<Control-n>", lambda e: self.new_document())
        self.rootmo95.bind("<Control-o>", lambda e: self.open_document())
        self.rootmo95.bind("<Control-s>", lambda e: self.save_document())
        
    def toggle_margin_padding(self):
        """Toggle între frame-based și tag-based margins"""
        self.show_margin_padding = self.margin_padding_var.get()
        
        # Recreează editor-ul cu noul mod
        self.recreate_editor()
        
        self.status_label.config(text=f"Margin padding: {'On' if self.show_margin_padding else 'Off'}")
        
    def recreate_editor(self):
        """Recreează editor-ul pentru a schimba modul de marje"""
        # Salvează conținutul și starea curentă
        content = self.text_editor.get("1.0", tk.END)
        cursor_pos = self.text_editor.index(tk.INSERT)
        
        # Salvează toate tag-urile
        saved_tags = {}
        all_tags = self.text_editor.tag_names()
        for tag in all_tags:
            if tag not in ["sel", "current", "margins"]:
                ranges = self.text_editor.tag_ranges(tag)
                if ranges:
                    saved_tags[tag] = [(str(ranges[i]), str(ranges[i+1])) 
                                      for i in range(0, len(ranges), 2)]
        
        # Salvează datele tabelelor
        saved_tables = []
        for table_id, table_info in self.tables.items():
            try:
                frame = table_info['frame']
                table_data = []
                for row_frame in frame.winfo_children():
                    row_data = []
                    for text_widget in row_frame.winfo_children():
                        if isinstance(text_widget, tk.Text):
                            row_data.append(text_widget.get("1.0", "end-1c"))
                    if row_data:
                        table_data.append(row_data)
                
                saved_tables.append({
                    'position': table_info['position'],
                    'rows': table_info['rows'],
                    'cols': table_info['cols'],
                    'data': table_data
                })
            except:
                pass
        
        # Distruge container-ul vechi
        self.editor_container.destroy()
        
        # Recreează editor-ul
        self.create_editor()
        
        # Restituie conținutul
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", content)
        
        # Restituie tag-urile
        for tag, ranges in saved_tags.items():
            # Re-configurează tag-ul dacă e nevoie
            if tag.startswith("color_"):
                color = tag.replace("color_", "")
                self.text_editor.tag_configure(tag, foreground=color)
            elif tag.startswith("bg_"):
                color = tag.replace("bg_", "")
                self.text_editor.tag_configure(tag, background=color)
            
            for start, end in ranges:
                try:
                    self.text_editor.tag_add(tag, start, end)
                except:
                    pass
        
        # Restituie tabelele
        self.tables = {}
        for table_info in saved_tables:
            try:
                rows = table_info['rows']
                cols = table_info['cols']
                position = table_info['position']
                data = table_info['data']
                
                # Creează frame-ul tabelului
                table_frame = tk.Frame(self.text_editor, bg="black", relief=tk.SOLID, bd=1)
                
                for r in range(rows):
                    row_frame = tk.Frame(table_frame, bg="white")
                    row_frame.grid(row=r, column=0, sticky="ew")
                    table_frame.grid_rowconfigure(r, weight=1)
                    
                    text_widgets = []
                    for c in range(cols):
                        text = tk.Text(row_frame, width=15, height=1, 
                                      relief=tk.SOLID, bd=1, wrap=tk.WORD,
                                      font=(self.current_font_family, self.current_font_size))
                        text.grid(row=0, column=c, padx=0, pady=0, sticky="nsew")
                        row_frame.grid_columnconfigure(c, weight=1)
                        
                        # Inserează datele
                        if r < len(data) and c < len(data[r]):
                            text.insert("1.0", data[r][c])
                        
                        text_widgets.append(text)
                    
                    # Bind auto-resize pentru acest rând
                    for txt in text_widgets:
                        txt.bind('<KeyRelease>', lambda e, t=txt, rw=text_widgets: self.auto_resize_table_row(e, t, rw))
                
                # Inserează tabelul
                self.text_editor.mark_set(tk.INSERT, position)
                self.text_editor.window_create(position, window=table_frame)
                
                # Salvează referința
                table_id = f"table_{len(self.tables)}"
                self.tables[table_id] = {
                    'frame': table_frame,
                    'rows': rows,
                    'cols': cols,
                    'position': position
                }
            except Exception as e:
                print(f"Error restoring table: {e}")
        
        # Restituie poziția cursorului
        try:
            self.text_editor.mark_set(tk.INSERT, cursor_pos)
            self.text_editor.see(cursor_pos)
        except:
            pass
        
        # Resetează flag-ul de modificare
        self.text_editor.edit_modified(False)
        
    def create_toolbar(self):
        toolbar_frame = tk.Frame(self.rootmo95, bg=self.bg_color, relief=tk.RAISED, bd=1)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
        
        self.create_toolbar_button(toolbar_frame, "New", self.new_document)
        self.create_toolbar_button(toolbar_frame, "Open", self.open_document)
        self.create_toolbar_button(toolbar_frame, "Save", self.save_document)
        
        self.create_separator(toolbar_frame)
        
        self.create_toolbar_button(toolbar_frame, "Cut", self.cut)
        self.create_toolbar_button(toolbar_frame, "Copy", self.copy)
        self.create_toolbar_button(toolbar_frame, "Paste", self.paste)
        
        self.create_separator(toolbar_frame)
        
        self.create_toolbar_button(toolbar_frame, "Undo", self.undo)
        self.create_toolbar_button(toolbar_frame, "Redo", self.redo)
        
        self.create_separator(toolbar_frame)
        
        self.create_toolbar_button(toolbar_frame, "Table", self.insert_table)
        
    def create_format_bar(self):
        format_frame = tk.Frame(self.rootmo95, bg=self.bg_color, relief=tk.RAISED, bd=1)
        format_frame.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
        
        tk.Label(format_frame, text="Font:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        self.font_var = tk.StringVar(value="Arial")
        font_families = ["Arial", "Times New Roman", "Courier New", "Comic Sans MS", 
                        "Verdana", "Georgia", "Tahoma", "Trebuchet MS"]
        self.font_menu = tk.OptionMenu(format_frame, self.font_var, *font_families, 
                                       command=self.on_font_change)
        self.font_menu.config(bg=self.bg_color, width=14, font=("MS Sans Serif", 8))
        self.font_menu.pack(side=tk.LEFT, padx=2, pady=2)
        
        tk.Label(format_frame, text="Size:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        self.size_var = tk.StringVar(value="12")
        sizes = ["8", "9", "10", "11", "12", "14", "16", "18", "20", "24", "28", "36", "48", "72"]
        self.size_menu = tk.OptionMenu(format_frame, self.size_var, *sizes, 
                                       command=self.on_size_change)
        self.size_menu.config(bg=self.bg_color, width=4, font=("MS Sans Serif", 8))
        self.size_menu.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.create_separator(format_frame)
        
        self.btn_bold = self.create_format_button(format_frame, "B", self.toggle_bold, 
                                                  font=("Arial", 9, "bold"))
        self.btn_italic = self.create_format_button(format_frame, "I", self.toggle_italic,
                                                    font=("Arial", 9, "italic"))
        self.btn_underline = self.create_format_button(format_frame, "U", self.toggle_underline,
                                                       font=("Arial", 9, "underline"))
        
        self.create_separator(format_frame)
        
        self.btn_left = self.create_format_button(format_frame, "L", 
                                                  lambda: self.set_alignment("left"))
        self.btn_center = self.create_format_button(format_frame, "C", 
                                                    lambda: self.set_alignment("center"))
        self.btn_right = self.create_format_button(format_frame, "R", 
                                                   lambda: self.set_alignment("right"))
        self.btn_justify = self.create_format_button(format_frame, "J", 
                                                     lambda: self.set_alignment("justify"))
        
        self.create_separator(format_frame)
        
        self.create_toolbar_button(format_frame, "Color", self.change_text_color)
        self.create_toolbar_button(format_frame, "Highlight", self.change_highlight_color)
        
    def create_ruler(self):
        ruler_frame = tk.Frame(self.rootmo95, bg=self.white, height=25, relief=tk.SUNKEN, bd=1)
        ruler_frame.pack(side=tk.TOP, fill=tk.X, padx=1)
        ruler_frame.pack_propagate(False)
        
        self.ruler_canvas = tk.Canvas(ruler_frame, bg=self.white, height=23, 
                                highlightthickness=0)
        self.ruler_canvas.pack(fill=tk.BOTH, expand=True)
        
        self.ruler_canvas.bind("<Button-1>", self.on_ruler_click)
        self.ruler_canvas.bind("<B1-Motion>", self.on_ruler_drag)
        self.ruler_canvas.bind("<ButtonRelease-1>", self.on_ruler_release)
        self.ruler_canvas.bind("<Configure>", lambda e: self.draw_ruler())
        
        self.dragging_margin = None
        
        # Initial draw after a delay to ensure proper sizing
        self.rootmo95.after(100, self.draw_ruler)
        
    def draw_ruler(self):
        """Draw ruler with current margins"""
        self.ruler_canvas.delete("all")
        
        # Get actual canvas width
        self.ruler_canvas.update_idletasks()
        width = self.ruler_canvas.winfo_width()
        if width <= 1:
            width = 800
        
        # Paper width in inches (8.5" for letter size)
        paper_width = 8.5
        pixels_per_inch = width / paper_width
        
        # Draw background
        self.ruler_canvas.create_rectangle(0, 0, width, 23, fill=self.white, outline="")
        
        # Draw ruler marks
        for i in range(int(paper_width * 10) + 1):
            x = i * (pixels_per_inch / 10)
            
            if i % 10 == 0:
                # Inch mark
                inch = i // 10
                self.ruler_canvas.create_line(x, 0, x, 15, fill=self.gray_dark, width=2)
                self.ruler_canvas.create_text(x, 20, text=str(inch), 
                                       font=("MS Sans Serif", 7, "bold"), fill="#000000")
            elif i % 5 == 0:
                # Half inch mark
                self.ruler_canvas.create_line(x, 0, x, 12, fill=self.gray_dark, width=1)
            else:
                # Tenth inch mark
                self.ruler_canvas.create_line(x, 0, x, 7, fill=self.gray_light, width=1)
        
        # Calculate margin positions
        left_margin_x = self.left_margin * pixels_per_inch
        right_margin_x = (paper_width - self.right_margin) * pixels_per_inch - 19
        
        # Draw left margin marker (triangle pointing right)
        self.left_marker = self.ruler_canvas.create_polygon(
            left_margin_x, 0, 
            left_margin_x, 10, 
            left_margin_x + 8, 5,
            fill="#0000FF", outline="#000080", width=1, tags="left_margin")
        
        # Draw right margin marker (triangle pointing left)
        self.right_marker = self.ruler_canvas.create_polygon(
            right_margin_x, 0, 
            right_margin_x, 10, 
            right_margin_x - 8, 5,
            fill="#0000FF", outline="#000080", width=1, tags="right_margin")
        
        # Draw margin guide lines
        self.ruler_canvas.create_line(left_margin_x, 10, left_margin_x, 23, 
                                      fill="#0000FF", width=1, dash=(2, 2))
        self.ruler_canvas.create_line(right_margin_x, 10, right_margin_x, 23, 
                                      fill="#0000FF", width=1, dash=(2, 2))
        
    def on_ruler_click(self, event):
        """Handle ruler click to start dragging margins"""
        width = self.ruler_canvas.winfo_width()
        if width <= 1:
            return
            
        paper_width = 8.5
        pixels_per_inch = width / paper_width
        
        left_margin_x = self.left_margin * pixels_per_inch
        right_margin_x = (paper_width - self.right_margin) * pixels_per_inch - 19
        
        # Check if clicking near left margin marker
        if abs(event.x - left_margin_x) < 15:
            self.dragging_margin = "left"
        # Check if clicking near right margin marker
        elif abs(event.x - right_margin_x) < 15:
            self.dragging_margin = "right"
        else:
            self.dragging_margin = None
            
    def on_ruler_drag(self, event):
        """Handle dragging margins"""
        if self.dragging_margin is None:
            return
            
        width = self.ruler_canvas.winfo_width()
        if width <= 1:
            return
            
        paper_width = 8.5
        pixels_per_inch = width / paper_width
        
        # Convert mouse position to inches
        inches = event.x / pixels_per_inch
        inches = max(0, min(paper_width, inches))
        
        if self.dragging_margin == "left":
            self.left_margin = max(0, min(6, inches))
            # Only update left margin in document
            self.draw_ruler()
            self.apply_margins_to_document(margin_type='left')
        elif self.dragging_margin == "right":
            # Compensate for the -19 pixel offset when dragging
            adjusted_x = event.x + 19
            inches = adjusted_x / pixels_per_inch
            
            right_inches = paper_width - inches
            self.right_margin = max(0, min(6, right_inches))
            # Only update right margin in document
            self.draw_ruler()
            self.apply_margins_to_document(margin_type='right')

        # Afișează poziția absolută de pe grid pentru ambele
        # Afișează poziția absolută de pe grid pentru ambele
        offset_inches = 19 / pixels_per_inch
        right_position_on_grid = paper_width - self.right_margin - offset_inches
        #right_position_on_grid = paper_width - self.right_margin - (19 / pixels_per_inch)
        self.status_label.config(text=f"Margins: Left={self.left_margin:.2f}\" Right={right_position_on_grid:.2f}\" (grid position)")
        
    def on_ruler_release(self, event):
        """Handle releasing margin drag"""
        self.dragging_margin = None
        
    def apply_margins_to_document(self, margin_type='both'):
        """Apply current margins to the entire document based on mode
        
        Args:
            margin_type: 'both', 'left', or 'right' - which margin to update
        """
        try:
            # Get ruler canvas width to calculate pixels per inch (same as ruler)
            self.ruler_canvas.update_idletasks()
            ruler_width = self.ruler_canvas.winfo_width()
            if ruler_width <= 1:
                ruler_width = 800
            
            paper_width = 8.5  # inches
            pixels_per_inch = ruler_width / paper_width
            
            # Calculate margin pixels using the same scale as the ruler
            left_pixels = int(self.left_margin * pixels_per_inch)
            right_pixels = int(self.right_margin * pixels_per_inch)
            
            if self.show_margin_padding:
                # Frame-based mode (mo95_office_advanced_best.py)
                if hasattr(self, 'left_margin_frame') and hasattr(self, 'right_margin_frame'):
                    self.left_margin_frame.config(width=left_pixels)
                    self.right_margin_frame.config(width=right_pixels)
            else:
                # Tag-based mode (mo95_office_advanced (2).py)
                if margin_type == 'left':
                    self.text_editor.tag_configure("margins", 
                                                  lmargin1=left_pixels,
                                                  lmargin2=left_pixels)
                elif margin_type == 'right':
                    self.text_editor.tag_configure("margins", 
                                                  rmargin=right_pixels)
                else:
                    self.text_editor.tag_configure("margins", 
                                                  lmargin1=left_pixels,
                                                  lmargin2=left_pixels,
                                                  rmargin=right_pixels)
                
                # Apply margin tag to entire document
                self.text_editor.tag_add("margins", "1.0", "end")
            
        except Exception as e:
            pass
        
    def create_editor(self):
        self.editor_container = tk.Frame(self.rootmo95, bg=self.gray_dark)
        self.editor_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        scrollbar = tk.Scrollbar(self.editor_container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        if self.show_margin_padding:
            # Frame-based mode (mo95_office_advanced_best.py)
            # Create a container that will hold margin frames and text editor
            self.editor_wrapper = tk.Frame(self.editor_container, bg=self.gray_light)
            self.editor_wrapper.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Left margin frame
            self.left_margin_frame = tk.Frame(self.editor_wrapper, bg=self.gray_light, width=0)
            self.left_margin_frame.pack(side=tk.LEFT, fill=tk.Y)
            self.left_margin_frame.pack_propagate(False)
            
            # Right margin frame
            self.right_margin_frame = tk.Frame(self.editor_wrapper, bg=self.gray_light, width=0)
            self.right_margin_frame.pack(side=tk.RIGHT, fill=tk.Y)
            self.right_margin_frame.pack_propagate(False)
            
            # Text editor in the middle
            self.text_editor = tk.Text(self.editor_wrapper, wrap=tk.WORD, undo=True, 
                                       font=(self.current_font_family, self.current_font_size), 
                                       bg=self.white, fg="black", 
                                       yscrollcommand=scrollbar.set,
                                       relief=tk.FLAT, bd=0, padx=10, pady=15,
                                       insertwidth=2, selectbackground="#000080",
                                       selectforeground="white")
            self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        else:
            # Tag-based mode (mo95_office_advanced (2).py)
            self.text_editor = tk.Text(self.editor_container, wrap=tk.WORD, undo=True, 
                                       font=(self.current_font_family, self.current_font_size), 
                                       bg=self.white, fg="black", 
                                       yscrollcommand=scrollbar.set,
                                       relief=tk.FLAT, bd=0, padx=0, pady=15,
                                       insertwidth=2, selectbackground="#000080",
                                       selectforeground="white")
            self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.text_editor.yview)
        
        # Enable mouse wheel scrolling
        self.text_editor.bind("<MouseWheel>", self.on_mousewheel)
        self.text_editor.bind("<Button-4>", self.on_mousewheel)
        self.text_editor.bind("<Button-5>", self.on_mousewheel)
        
        self.configure_tags()
        
        # Apply initial margins
        self.apply_margins_to_document()
        
        # Bind events for status updates
        self.text_editor.bind("<KeyRelease>", self.update_status)
        self.text_editor.bind("<ButtonRelease>", self.update_status)
        self.text_editor.bind("<<Modified>>", self.on_text_modified)
        
        # Initial update
        self.rootmo95.after(100, self.update_status)
        
    def on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.num == 5 or event.delta < 0:
            self.text_editor.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.text_editor.yview_scroll(-1, "units")
        return "break"
        
    def configure_tags(self):
        self.text_editor.tag_configure("bold", font=(self.current_font_family, 
                                                     self.current_font_size, "bold"))
        self.text_editor.tag_configure("italic", font=(self.current_font_family, 
                                                       self.current_font_size, "italic"))
        self.text_editor.tag_configure("underline", underline=True)
        self.text_editor.tag_configure("bold_italic", font=(self.current_font_family, 
                                                            self.current_font_size, "bold italic"))
        
        self.text_editor.tag_configure("left", justify=tk.LEFT)
        self.text_editor.tag_configure("center", justify=tk.CENTER)
        self.text_editor.tag_configure("right", justify=tk.RIGHT)
        self.text_editor.tag_configure("justify", justify=tk.LEFT)
        
    def update_status(self, event=None):
        """Update status bar with cursor position and word count"""
        self.update_cursor_position()
        self.update_word_count()
        
    def create_statusbar(self):
        statusbar = tk.Frame(self.rootmo95, bg=self.gray_light, relief=tk.SUNKEN, bd=1)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(statusbar, text="Ready", bg=self.gray_light, 
                                     anchor=tk.W, padx=10, font=("MS Sans Serif", 8))
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.word_count_label = tk.Label(statusbar, text="Words: 0", bg=self.gray_light,
                                         width=15, anchor=tk.E, padx=10,
                                         font=("MS Sans Serif", 8))
        self.word_count_label.pack(side=tk.RIGHT)
        
        self.zoom_label = tk.Label(statusbar, text="100%", bg=self.gray_light,
                                   width=8, anchor=tk.E, padx=10,
                                   font=("MS Sans Serif", 8))
        self.zoom_label.pack(side=tk.RIGHT)
        
        self.pos_label = tk.Label(statusbar, text="Ln 1, Col 1", bg=self.gray_light, 
                                 width=15, anchor=tk.E, padx=10,
                                 font=("MS Sans Serif", 8))
        self.pos_label.pack(side=tk.RIGHT)
        
    def create_toolbar_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, width=6, relief=tk.RAISED, 
                       bg=self.bg_color, command=command,
                       font=("MS Sans Serif", 8), bd=1)
        btn.pack(side=tk.LEFT, padx=1, pady=2)
        return btn
        
    def create_format_button(self, parent, text, command, font=None):
        if font is None:
            font = ("MS Sans Serif", 8)
        btn = tk.Button(parent, text=text, width=3, relief=tk.RAISED, 
                       bg=self.bg_color, command=command,
                       font=font, bd=1)
        btn.pack(side=tk.LEFT, padx=1, pady=2)
        return btn
        
    def create_separator(self, parent):
        sep = tk.Frame(parent, width=2, bg=self.gray_dark, relief=tk.SUNKEN)
        sep.pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=2)
        return sep
        
    def update_cursor_position(self, event=None):
        cursor_pos = self.text_editor.index(tk.INSERT)
        line, col = cursor_pos.split(".")
        self.pos_label.config(text=f"Ln {line}, Col {int(col)+1}")
        
    def update_word_count(self, event=None):
        content = self.text_editor.get("1.0", tk.END)
        words = len(content.split())
        self.word_count_label.config(text=f"Words: {words}")
        
    def on_text_modified(self, event=None):
        if self.text_editor.edit_modified():
            self.document_modified = True
            self.update_title()
            self.text_editor.edit_modified(False)
    
    def on_window_resize(self, event=None):
        """Handle window resize to update ruler and margins"""
        # Only process resize events from the rootmo95 window
        if event and event.widget != self.rootmo95:
            return
        # Redraw ruler and reapply margins with new scale
        self.rootmo95.after(50, lambda: (self.draw_ruler(), self.apply_margins_to_document()))
            
    def update_title(self):
        title = "Multiapp Office - "
        if self.current_file:
            title += os.path.basename(self.current_file)
        else:
            title += "Untitled"
        if self.document_modified:
            title += " *"
        self.title_bar.set_title(title)
        
    def new_document(self):
        if self.document_modified:
            response = messagebox.askyesnocancel("Multiapp Office", 
                                                 "Do you want to save changes?")
            if response is None:
                return
            elif response:
                self.save_document()
                
        self.text_editor.delete("1.0", tk.END)
        self.current_file = None
        self.document_modified = False
        self.update_title()
        self.status_label.config(text="New document created")
        
    def open_document(self):
        if self.document_modified:
            response = messagebox.askyesnocancel("Multiapp Office", 
                                                 "Do you want to save changes?")
            if response is None:
                return
            elif response:
                self.save_document()
                
        filename = filedialog.askopenfilename(
            defaultextension=".mo95",
            filetypes=[("MO95 Documents", "*.mo95")]
        )
        
        if filename:
            try:
                tree = ET.parse(filename)
                rootmo95 = tree.getroot()
                
                content_elem = rootmo95.find('content')
                if content_elem is not None and content_elem.text:
                    self.text_editor.delete("1.0", tk.END)
                    self.text_editor.insert("1.0", content_elem.text)
                
                formatting_elem = rootmo95.find('formatting')
                if formatting_elem is not None:
                    for fmt in formatting_elem.findall('format'):
                        start_idx = fmt.get('start')
                        end_idx = fmt.get('end')
                        tags_str = fmt.get('tags', '')
                        
                        if tags_str:
                            tags = tags_str.split(',')
                            for tag in tags:
                                tag = tag.strip()
                                if tag.startswith("color_"):
                                    color = tag.replace("color_", "")
                                    self.text_editor.tag_configure(tag, foreground=color)
                                elif tag.startswith("bg_"):
                                    color = tag.replace("bg_", "")
                                    self.text_editor.tag_configure(tag, background=color)
                                
                                self.text_editor.tag_add(tag, start_idx, end_idx)
                
                page_setup_elem = rootmo95.find('page_setup')
                if page_setup_elem is not None:
                    self.left_margin = float(page_setup_elem.get('left_margin', 1.25))
                    self.right_margin = float(page_setup_elem.get('right_margin', 1.25))
                    self.top_margin = float(page_setup_elem.get('top_margin', 1.0))
                    self.bottom_margin = float(page_setup_elem.get('bottom_margin', 1.0))
                    self.draw_ruler()
                    self.apply_margins_to_document()
                    
                font_elem = rootmo95.find('font_settings')
                if font_elem is not None:
                    self.current_font_family = font_elem.get('family', 'Arial')
                    self.current_font_size = int(font_elem.get('size', 12))
                    
                    self.font_var.set(self.current_font_family)
                    self.size_var.set(str(self.current_font_size))
                    self.text_editor.configure(font=(self.current_font_family, self.current_font_size))
                    self.update_tag_fonts()
                
                # Restaurează tabelele
                self.tables = {}
                tables_elem = rootmo95.find('tables')
                if tables_elem is not None:
                    for table in tables_elem.findall('table'):
                        try:
                            position = table.get('position')
                            rows = int(table.get('rows'))
                            cols = int(table.get('cols'))
                            
                            # Creează frame-ul tabelului
                            table_frame = tk.Frame(self.text_editor, bg="black", relief=tk.SOLID, bd=1)
                            
                            for r in range(rows):
                                row_frame = tk.Frame(table_frame, bg="white")
                                row_frame.grid(row=r, column=0, sticky="ew")
                                table_frame.grid_rowconfigure(r, weight=1)
                                
                                text_widgets = []
                                for c in range(cols):
                                    text = tk.Text(row_frame, width=15, height=1, 
                                                  relief=tk.SOLID, bd=1, wrap=tk.WORD,
                                                  font=(self.current_font_family, self.current_font_size))
                                    text.grid(row=0, column=c, padx=0, pady=0, sticky="nsew")
                                    row_frame.grid_columnconfigure(c, weight=1)
                                    
                                    # Găsește conținutul
                                    for cell in table.findall('cell'):
                                        if int(cell.get('row')) == r and int(cell.get('col')) == c:
                                            if cell.text:
                                                text.insert("1.0", cell.text)
                                    
                                    text_widgets.append(text)
                                
                                # Bind auto-resize pentru acest rând
                                for txt in text_widgets:
                                    txt.bind('<KeyRelease>', lambda e, t=txt, rw=text_widgets: self.auto_resize_table_row(e, t, rw))
                            
                            # Inserează tabelul
                            self.text_editor.mark_set(tk.INSERT, position)
                            self.text_editor.window_create(position, window=table_frame)
                            
                            # Salvează referința
                            table_id = f"table_{len(self.tables)}"
                            self.tables[table_id] = {
                                'frame': table_frame,
                                'rows': rows,
                                'cols': cols,
                                'position': position
                            }
                        except Exception as e:
                            print(f"Error loading table: {e}")
                
                self.current_file = filename
                self.document_modified = False
                self.update_title()
                self.add_to_recent_files(filename)
                self.status_label.config(text=f"Opened: {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open document:\n{str(e)}")
    
    def auto_resize_table_row(self, event=None, txt=None, row_texts=None):
        """Auto-resize table row based on content"""
        if row_texts is None:
            row_texts = []
        
        # Calculate required lines for this text
        content = txt.get("1.0", "end-1c")
        if content:
            # Estimate lines needed based on content length and width
            chars_per_line = 15  # Approximate chars that fit in width
            lines_needed = max(1, (len(content) // chars_per_line) + 1)
            
            # Find max height needed in this row
            max_height = lines_needed
            for t in row_texts:
                t_content = t.get("1.0", "end-1c")
                t_lines = max(1, (len(t_content) // chars_per_line) + 1)
                max_height = max(max_height, t_lines)
            
            # Apply height to all text widgets in row
            for t in row_texts:
                t.config(height=max_height)
        else:
            txt.config(height=1)
        
    def save_document(self):
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as_document()
            
    def save_as_document(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".mo95",
            filetypes=[("MO95 Documents", "*.mo95")]
        )
        
        if filename:
            self.save_to_file(filename)
            self.current_file = filename
            self.add_to_recent_files(filename)
            self.update_title()
            
    def save_to_file(self, filename):
        try:
            rootmo95 = ET.Element('mo95_document')
            rootmo95.set('version', '2.0')
            
            content = self.text_editor.get("1.0", "end-1c")
            content_elem = ET.SubElement(rootmo95, 'content')
            content_elem.text = content
            
            # Salvează tabelele
            tables_elem = ET.SubElement(rootmo95, 'tables')
            for table_id, table_info in self.tables.items():
                try:
                    table_elem = ET.SubElement(tables_elem, 'table')
                    table_elem.set('position', table_info['position'])
                    table_elem.set('rows', str(table_info['rows']))
                    table_elem.set('cols', str(table_info['cols']))
                    
                    frame = table_info['frame']
                    for r, row_frame in enumerate(frame.winfo_children()):
                        for c, text_widget in enumerate(row_frame.winfo_children()):
                            if isinstance(text_widget, tk.Text):
                                cell_elem = ET.SubElement(table_elem, 'cell')
                                cell_elem.set('row', str(r))
                                cell_elem.set('col', str(c))
                                cell_elem.text = text_widget.get("1.0", "end-1c")
                except:
                    pass
            
            formatting_elem = ET.SubElement(rootmo95, 'formatting')
            all_tags = self.text_editor.tag_names()
            
            for tag in all_tags:
                if tag in ["sel", "current", "margins"]:
                    continue
                    
                ranges = self.text_editor.tag_ranges(tag)
                for i in range(0, len(ranges), 2):
                    if i + 1 < len(ranges):
                        fmt_elem = ET.SubElement(formatting_elem, 'format')
                        fmt_elem.set('start', str(ranges[i]))
                        fmt_elem.set('end', str(ranges[i+1]))
                        fmt_elem.set('tags', tag)
            
            page_setup_elem = ET.SubElement(rootmo95, 'page_setup')
            page_setup_elem.set('left_margin', str(self.left_margin))
            page_setup_elem.set('right_margin', str(self.right_margin))
            page_setup_elem.set('top_margin', str(self.top_margin))
            page_setup_elem.set('bottom_margin', str(self.bottom_margin))
            page_setup_elem.set('orientation', 'portrait')
            
            metadata_elem = ET.SubElement(rootmo95, 'metadata')
            metadata_elem.set('created', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            metadata_elem.set('application', 'Multiapp Office MO95')
            metadata_elem.set('version', '2.0')
            
            font_elem = ET.SubElement(rootmo95, 'font_settings')
            font_elem.set('family', self.current_font_family)
            font_elem.set('size', str(self.current_font_size))
            
            xml_str = minidom.parseString(ET.tostring(rootmo95)).toprettyxml(indent="  ")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(xml_str)
            
            self.document_modified = False
            self.update_title()
            self.status_label.config(text=f"Saved: {os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save document:\n{str(e)}")
            
    def exit_application(self):
        if self.document_modified:
            response = messagebox.askyesnocancel("Multiapp Office", 
                                                 "Do you want to save changes before exiting?")
            if response is None:
                return
            elif response:
                self.save_document()
        self.save_recent_files()
        self.rootmo95.quit()
        
    def undo(self):
        try:
            self.text_editor.edit_undo()
        except:
            pass
            
    def redo(self):
        try:
            self.text_editor.edit_redo()
        except:
            pass
            
    def cut(self):
        try:
            self.text_editor.event_generate("<<Cut>>")
        except:
            pass
            
    def copy(self):
        try:
            self.text_editor.event_generate("<<Copy>>")
        except:
            pass
            
    def paste(self):
        try:
            self.text_editor.event_generate("<<Paste>>")
        except:
            pass
            
    def delete_selection(self):
        try:
            self.text_editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
            
    def select_all(self):
        self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        self.text_editor.mark_set(tk.INSERT, "1.0")
        self.text_editor.see(tk.INSERT)
        
    def find_text(self):
        find_window = tk.Toplevel(self.rootmo95)
        find_window.title("Find")
        find_window.geometry("400x120")
        find_window.configure(bg=self.bg_color)
        find_window.transient(self.rootmo95)
        
        tk.Label(find_window, text="Find what:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        
        find_entry = tk.Entry(find_window, width=30, font=("MS Sans Serif", 9))
        find_entry.grid(row=0, column=1, padx=10, pady=10)
        find_entry.focus()
        
        def do_find():
            search_term = find_entry.get()
            if search_term:
                self.text_editor.tag_remove("search", "1.0", tk.END)
                
                start_pos = self.find_index
                pos = self.text_editor.search(search_term, start_pos, tk.END)
                
                if pos:
                    end_pos = f"{pos}+{len(search_term)}c"
                    self.text_editor.tag_add("search", pos, end_pos)
                    self.text_editor.tag_configure("search", background="yellow", 
                                                  foreground="black")
                    self.text_editor.see(pos)
                    self.text_editor.mark_set(tk.INSERT, pos)
                    self.find_index = end_pos
                else:
                    self.find_index = "1.0"
                    messagebox.showinfo("Find", "No more occurrences found.")
        
        tk.Button(find_window, text="Find Next", command=do_find, width=12,
                 bg=self.bg_color, font=("MS Sans Serif", 8)).grid(row=0, column=2, 
                                                                      padx=10, pady=10)
        tk.Button(find_window, text="Cancel", command=find_window.destroy, width=12,
                 bg=self.bg_color, font=("MS Sans Serif", 8)).grid(row=1, column=2, 
                                                                      padx=10, pady=10)
        
    def replace_text(self):
        replace_window = tk.Toplevel(self.rootmo95)
        replace_window.title("Replace")
        replace_window.geometry("450x160")
        replace_window.configure(bg=self.bg_color)
        replace_window.transient(self.rootmo95)
        
        tk.Label(replace_window, text="Find what:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        find_entry = tk.Entry(replace_window, width=30, font=("MS Sans Serif", 9))
        find_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(replace_window, text="Replace with:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        replace_entry = tk.Entry(replace_window, width=30, font=("MS Sans Serif", 9))
        replace_entry.grid(row=1, column=1, padx=10, pady=10)
        
        def do_replace():
            search_term = find_entry.get()
            replace_term = replace_entry.get()
            
            if search_term:
                try:
                    start_pos = tk.SEL_FIRST
                    end_pos = tk.SEL_LAST
                    selected = self.text_editor.get(start_pos, end_pos)
                    
                    if selected == search_term:
                        self.text_editor.delete(start_pos, end_pos)
                        self.text_editor.insert(start_pos, replace_term)
                except:
                    pass
        
        def do_replace_all():
            search_term = find_entry.get()
            replace_term = replace_entry.get()
            
            if search_term:
                content = self.text_editor.get("1.0", tk.END)
                new_content = content.replace(search_term, replace_term)
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", new_content)
                messagebox.showinfo("Replace All", "Replacement complete.")
        
        tk.Button(replace_window, text="Replace", command=do_replace, width=12,
                 bg=self.bg_color, font=("MS Sans Serif", 8)).grid(row=0, column=2, 
                                                                      padx=10, pady=5)
        tk.Button(replace_window, text="Replace All", command=do_replace_all, width=12,
                 bg=self.bg_color, font=("MS Sans Serif", 8)).grid(row=1, column=2, 
                                                                      padx=10, pady=5)
        tk.Button(replace_window, text="Cancel", command=replace_window.destroy, width=12,
                 bg=self.bg_color, font=("MS Sans Serif", 8)).grid(row=2, column=2, 
                                                                      padx=10, pady=5)
        
    def toggle_bold(self):
        try:
            current_tags = self.text_editor.tag_names(tk.SEL_FIRST)
            if "bold" in current_tags:
                self.text_editor.tag_remove("bold", tk.SEL_FIRST, tk.SEL_LAST)
            else:
                self.text_editor.tag_add("bold", tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
            
    def toggle_italic(self):
        try:
            current_tags = self.text_editor.tag_names(tk.SEL_FIRST)
            if "italic" in current_tags:
                self.text_editor.tag_remove("italic", tk.SEL_FIRST, tk.SEL_LAST)
            else:
                self.text_editor.tag_add("italic", tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
            
    def toggle_underline(self):
        try:
            current_tags = self.text_editor.tag_names(tk.SEL_FIRST)
            if "underline" in current_tags:
                self.text_editor.tag_remove("underline", tk.SEL_FIRST, tk.SEL_LAST)
            else:
                self.text_editor.tag_add("underline", tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
            
    def set_alignment(self, align):
        try:
            current_line = self.text_editor.index(tk.INSERT).split('.')[0]
            start = f"{current_line}.0"
            end = f"{current_line}.end"
            
            for a in ["left", "center", "right", "justify"]:
                self.text_editor.tag_remove(a, start, end)
            
            self.text_editor.tag_add(align, start, end)
        except:
            pass
            
    def change_font(self):
        font_window = tk.Toplevel(self.rootmo95)
        font_window.title("Font")
        font_window.geometry("350x400")
        font_window.configure(bg=self.bg_color)
        font_window.transient(self.rootmo95)
        font_window.grab_set()
        
        font_frame = tk.Frame(font_window, bg=self.white, relief=tk.SUNKEN, bd=1)
        font_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(font_frame, text="Font:", bg=self.white,
                font=("MS Sans Serif", 8)).pack(anchor=tk.W, padx=10, pady=5)
        
        font_listbox = tk.Listbox(font_frame, height=10, font=("MS Sans Serif", 9))
        font_listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        fonts = ["Arial", "Times New Roman", "Courier New", "Comic Sans MS", 
                "Verdana", "Georgia", "Tahoma", "Trebuchet MS", "Impact", "Lucida Console"]
        
        for f in fonts:
            font_listbox.insert(tk.END, f)
        
        try:
            idx = fonts.index(self.current_font_family)
            font_listbox.selection_set(idx)
            font_listbox.see(idx)
        except:
            pass
        
        def apply_font():
            selection = font_listbox.curselection()
            if selection:
                self.current_font_family = font_listbox.get(selection[0])
                self.font_var.set(self.current_font_family)
                self.text_editor.configure(font=(self.current_font_family, self.current_font_size))
                self.update_tag_fonts()
                
                for table_id, table_info in self.tables.items():
                    try:
                        frame = table_info['frame']
                        for row_frame in frame.winfo_children():
                            for text_widget in row_frame.winfo_children():
                                if isinstance(text_widget, tk.Text):
                                    text_widget.configure(font=(self.current_font_family, self.current_font_size))
                    except:
                        pass
                
                font_window.destroy()
        
        button_frame = tk.Frame(font_window, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=apply_font, width=10, 
                 bg=self.bg_color, font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=font_window.destroy, width=10,
                 bg=self.bg_color, font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=5)
        
    def on_font_change(self, value):
        self.current_font_family = value
        self.text_editor.configure(font=(self.current_font_family, self.current_font_size))
        self.update_tag_fonts()
        
        for table_id, table_info in self.tables.items():
            try:
                frame = table_info['frame']
                for row_frame in frame.winfo_children():  # <-- Corectare aici
                    for text_widget in row_frame.winfo_children():
                        if isinstance(text_widget, tk.Text):
                            text_widget.configure(font=(self.current_font_family, self.current_font_size))
            except:
                pass
        
    def on_size_change(self, value):
        self.current_font_size = int(value)
        self.text_editor.configure(font=(self.current_font_family, self.current_font_size))
        self.update_tag_fonts()
        
        for table_id, table_info in self.tables.items():
            try:
                frame = table_info['frame']
                for row_frame in frame.winfo_children():
                    for text_widget in row_frame.winfo_children():
                        if isinstance(text_widget, tk.Text):
                            text_widget.configure(font=(self.current_font_family, self.current_font_size))
            except:
                pass
        
    def update_tag_fonts(self):
        self.text_editor.tag_configure("bold", font=(self.current_font_family, 
                                                     self.current_font_size, "bold"))
        self.text_editor.tag_configure("italic", font=(self.current_font_family, 
                                                       self.current_font_size, "italic"))
        self.text_editor.tag_configure("bold_italic", font=(self.current_font_family, 
                                                            self.current_font_size, "bold italic"))
        
    def change_text_color(self):
        color = colorchooser.askcolor(title="Choose Text Color")
        if color[1]:
            try:
                tag_name = f"color_{color[1]}"
                self.text_editor.tag_configure(tag_name, foreground=color[1])
                self.text_editor.tag_add(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
            except:
                pass
                
    def change_highlight_color(self):
        color = colorchooser.askcolor(title="Choose Highlight Color")
        if color[1]:
            try:
                tag_name = f"bg_{color[1]}"
                self.text_editor.tag_configure(tag_name, background=color[1])
                self.text_editor.tag_add(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
            except:
                pass
                
    def insert_table(self):
        """Insert Excel-like table with auto-resizing rows"""
        dialog = tk.Toplevel(self.rootmo95)
        dialog.title("Insert Table")
        dialog.geometry("300x150")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.rootmo95)
        dialog.grab_set()
        
        tk.Label(dialog, text="Rows:", bg=self.bg_color).grid(row=0, column=0, padx=10, pady=10)
        rows_entry = tk.Entry(dialog, width=10)
        rows_entry.grid(row=0, column=1, padx=10, pady=10)
        rows_entry.insert(0, "3")
        
        tk.Label(dialog, text="Columns:", bg=self.bg_color).grid(row=1, column=0, padx=10, pady=10)
        cols_entry = tk.Entry(dialog, width=10)
        cols_entry.grid(row=1, column=1, padx=10, pady=10)
        cols_entry.insert(0, "3")
        
        def create_table():
            try:
                rows = int(rows_entry.get())
                cols = int(cols_entry.get())
                dialog.destroy()
                
                # Create table frame
                table_frame = tk.Frame(self.text_editor, bg="black", relief=tk.SOLID, bd=1)
                
                # Store all text widgets for each row
                row_widgets = []
                
                for r in range(rows):
                    row_frame = tk.Frame(table_frame, bg="white")
                    row_frame.grid(row=r, column=0, sticky="ew")
                    table_frame.grid_rowconfigure(r, weight=1)
                    
                    text_widgets = []
                    for c in range(cols):
                        # Use Text widget instead of Entry for multi-line support
                        text = tk.Text(row_frame, width=15, height=1, 
                                      relief=tk.SOLID, bd=1, wrap=tk.WORD,
                                      font=(self.current_font_family, self.current_font_size))
                        text.grid(row=0, column=c, padx=0, pady=0, sticky="nsew")
                        row_frame.grid_columnconfigure(c, weight=1)
                        
                        # Auto-resize function for this text widget
                        def auto_resize(event=None, txt=text, row_texts=None):
                            if row_texts is None:
                                row_texts = []
                            
                            # Calculate required lines for this text
                            content = txt.get("1.0", "end-1c")
                            if content:
                                # Estimate lines needed based on content length and width
                                chars_per_line = 15  # Approximate chars that fit in width
                                lines_needed = max(1, (len(content) // chars_per_line) + 1)
                                
                                # Find max height needed in this row
                                max_height = lines_needed
                                for t in row_texts:
                                    t_content = t.get("1.0", "end-1c")
                                    t_lines = max(1, (len(t_content) // chars_per_line) + 1)
                                    max_height = max(max_height, t_lines)
                                
                                # Apply height to all text widgets in row
                                for t in row_texts:
                                    t.config(height=max_height)
                            else:
                                txt.config(height=1)
                        
                        text_widgets.append(text)
                    
                    # Bind auto-resize to all text widgets in this row
                    # for txt in text_widgets:
                        # txt.bind('<KeyRelease>', lambda e, t=txt, rw=text_widgets: auto_resize(e, t, rw))
                    for txt in text_widgets:
                        txt.bind('<KeyRelease>', lambda e, t=txt, rw=text_widgets: self.auto_resize_table_row(e, t, rw))
                    
                    row_widgets.append(text_widgets)
                
                # Make table frame expandable
                table_frame.grid_columnconfigure(0, weight=1)
                
                # Insert frame into text widget
                insert_pos = self.text_editor.index(tk.INSERT)
                self.text_editor.window_create(tk.INSERT, window=table_frame)
                self.text_editor.insert(tk.INSERT, "\n")
                
                # Salvează referința la tabel
                table_id = f"table_{len(self.tables)}"
                self.tables[table_id] = {
                    'frame': table_frame,
                    'rows': rows,
                    'cols': cols,
                    'position': insert_pos
                }
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        
        tk.Button(dialog, text="Insert", command=create_table, bg=self.bg_color).grid(row=2, column=0, columnspan=2, pady=20)
    
    def generate_ascii_table(self, rows, cols):
        """Generate ASCII table with borders"""
        col_width = 15
        
        # Create horizontal line
        def make_line(left, mid, right, horiz):
            return left + mid.join([horiz * col_width for _ in range(cols)]) + right
        
        # Top border
        top_border = make_line("+", "+", "+", "-")
        
        # Middle separator
        mid_separator = make_line("+", "+", "+", "-")
        
        # Bottom border
        bottom_border = make_line("+", "+", "+", "-")
        
        # Build table
        table_lines = [top_border]
        
        for r in range(rows):
            # Empty data row
            row_data = [" " * col_width for _ in range(cols)]
            table_lines.append("|" + "|".join(row_data) + "|")
            
            # Add separator between rows (except after last row)
            if r < rows - 1:
                table_lines.append(mid_separator)
        
        table_lines.append(bottom_border)
        
        return "\n".join(table_lines)
        
    def insert_datetime(self):
        current_time = datetime.now().strftime("%B %d, %Y %I:%M:%S %p")
        self.text_editor.insert(tk.INSERT, current_time)
        
    def insert_page_break(self):
        page_break = "\n" + "─" * 50 + " Page Break " + "─" * 50 + "\n\n"
        self.text_editor.insert(tk.INSERT, page_break)
        
    def insert_horizontal_line(self):
        hr = "\n" + "─" * 100 + "\n"
        self.text_editor.insert(tk.INSERT, hr)
        
    def zoom_in(self):
        if self.current_font_size < 72:
            self.current_font_size += 2
            self.size_var.set(str(self.current_font_size))
            self.text_editor.configure(font=(self.current_font_family, self.current_font_size))
            self.update_tag_fonts()
            zoom_percent = int((self.current_font_size / 12) * 100)
            self.zoom_label.config(text=f"{zoom_percent}%")
            
    def zoom_out(self):
        if self.current_font_size > 8:
            self.current_font_size -= 2
            self.size_var.set(str(self.current_font_size))
            self.text_editor.configure(font=(self.current_font_family, self.current_font_size))
            self.update_tag_fonts()
            zoom_percent = int((self.current_font_size / 12) * 100)
            self.zoom_label.config(text=f"{zoom_percent}%")
            
    def normal_zoom(self):
        self.current_font_size = 12
        self.size_var.set("12")
        self.text_editor.configure(font=(self.current_font_family, self.current_font_size))
        self.update_tag_fonts()
        self.zoom_label.config(text="100%")
        
    def show_word_count(self):
        content = self.text_editor.get("1.0", tk.END)
        words = len(content.split())
        chars = len(content)
        lines = int(self.text_editor.index('end-1c').split('.')[0])
        
        stats_msg = f"Statistics:\n\n"
        stats_msg += f"Words: {words}\n"
        stats_msg += f"Characters: {chars}\n"
        stats_msg += f"Lines: {lines}"
        
        messagebox.showinfo("Word Count", stats_msg)
        
    def page_setup(self):
        """Functional page setup dialog with proper margin controls"""
        setup_window = tk.Toplevel(self.rootmo95)
        setup_window.title("Page Setup")
        setup_window.geometry("400x320")
        setup_window.configure(bg=self.bg_color)
        setup_window.transient(self.rootmo95)
        setup_window.grab_set()
        
        margins_frame = tk.LabelFrame(setup_window, text="Margins (inches)", 
                                     bg=self.white, font=("MS Sans Serif", 8))
        margins_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # tk.Label(margins_frame, text="Top:", bg=self.white,
                # font=("MS Sans Serif", 8)).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        # top_entry = tk.Entry(margins_frame, width=10, font=("MS Sans Serif", 9))
        # top_entry.grid(row=0, column=1, padx=10, pady=10)
        # top_entry.insert(0, str(self.top_margin))
        
        # tk.Label(margins_frame, text="Bottom:", bg=self.white,
                # font=("MS Sans Serif", 8)).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        # bottom_entry = tk.Entry(margins_frame, width=10, font=("MS Sans Serif", 9))
        # bottom_entry.grid(row=1, column=1, padx=10, pady=10)
        # bottom_entry.insert(0, str(self.bottom_margin))
        
        tk.Label(margins_frame, text="Left:", bg=self.white,
                font=("MS Sans Serif", 8)).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        left_entry = tk.Entry(margins_frame, width=10, font=("MS Sans Serif", 9))
        left_entry.grid(row=2, column=1, padx=10, pady=10)
        left_entry.insert(0, str(self.left_margin))
        
        tk.Label(margins_frame, text="Right:", bg=self.white,
                font=("MS Sans Serif", 8)).grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        right_entry = tk.Entry(margins_frame, width=10, font=("MS Sans Serif", 9))
        right_entry.grid(row=3, column=1, padx=10, pady=10)
        #right_entry.insert(0, str(self.right_margin))
        paper_width = 8.5
        #right_position_on_grid = paper_width - self.right_margin
        right_position_on_grid = paper_width - self.right_margin - (19 / ((self.ruler_canvas.winfo_width() if self.ruler_canvas.winfo_width() > 1 else 800) / paper_width))
        right_entry.insert(0, str(round(right_position_on_grid, 2)))
        
        def apply_setup():
            try:
                #new_top = float(top_entry.get())
                #new_bottom = float(bottom_entry.get())
                new_left = float(left_entry.get())
                new_right_position = float(right_entry.get())  # poziție de pe grid
                paper_width = 8.5
                #new_right = paper_width - new_right_position  # convertește în distanță de la dreapta
                new_right = paper_width - new_right_position - (19 / ((self.ruler_canvas.winfo_width() if self.ruler_canvas.winfo_width() > 1 else 800) / paper_width))
                
                # Validate margins
                #if new_top < 0 or new_top > 5:
                    #raise ValueError("Top margin must be between 0 and 5 inches")
                #if new_bottom < 0 or new_bottom > 5:
                    #raise ValueError("Bottom margin must be between 0 and 5 inches")
                if new_right_position < 0 or new_right_position > 8.5:
                    raise ValueError("Right position must be between 0 and 8.5 inches")
                # if new_left < 0 or new_left > 6:
                    # raise ValueError("Left margin must be between 0 and 6 inches")
                # if new_right < 0 or new_right > 6:
                    # raise ValueError("Right margin must be between 0 and 6 inches")
                
                # Apply new margins
                #self.top_margin = new_top
                #self.bottom_margin = new_bottom
                self.left_margin = new_left
                self.right_margin = new_right
                
                # Update ruler and document
                self.draw_ruler()
                self.apply_margins_to_document()
                
                setup_window.destroy()
                #right_position_on_grid = paper_width - self.right_margin
                right_position_on_grid = paper_width - self.right_margin - (19 / ((self.ruler_canvas.winfo_width() if self.ruler_canvas.winfo_width() > 1 else 800) / paper_width))
                self.status_label.config(text=f"Margins: Left={self.left_margin:.2f}\" Right={right_position_on_grid:.2f}\" (from edges)")
                messagebox.showinfo("Page Setup", "Margins updated successfully!")
                
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        button_frame = tk.Frame(setup_window, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="OK", command=apply_setup, width=10,
                 bg=self.bg_color, font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=setup_window.destroy, width=10,
                 bg=self.bg_color, font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=5)
        
    def print_preview(self):
        messagebox.showinfo("Print Preview", "Print preview functionality\n\nDocument is ready for printing")
        
    def load_recent_files(self):
        try:
            recent_file = os.path.join(os.path.dirname(__file__), "mo95_recent.txt")
            if os.path.exists(recent_file):
                with open(recent_file, 'r') as f:
                    self.recent_files = [line.strip() for line in f.readlines()]
        except:
            self.recent_files = []
            
    def save_recent_files(self):
        try:
            recent_file = os.path.join(os.path.dirname(__file__), "mo95_recent.txt")
            with open(recent_file, 'w') as f:
                for filepath in self.recent_files[:10]:
                    f.write(filepath + '\n')
        except:
            pass
            
    def add_to_recent_files(self, filename):
        if filename in self.recent_files:
            self.recent_files.remove(filename)
        self.recent_files.insert(0, filename)
        self.recent_files = self.recent_files[:10]
        self.update_recent_menu()
        
    def update_recent_menu(self):
        self.recent_menu.delete(0, tk.END)
        
        if not self.recent_files:
            self.recent_menu.add_command(label="(No recent files)", state=tk.DISABLED)
        else:
            for i, filepath in enumerate(self.recent_files[:10]):
                filename = os.path.basename(filepath)
                self.recent_menu.add_command(
                    label=f"{i+1}. {filename}",
                    command=lambda f=filepath: self.open_recent_file(f)
                )
                
    def open_recent_file(self, filepath):
        if os.path.exists(filepath):
            self.current_file = filepath
            self.open_document()
        else:
            messagebox.showerror("Error", f"File not found:\n{filepath}")
            self.recent_files.remove(filepath)
            self.update_recent_menu()
            
    def show_about(self):
        about_window = tk.Toplevel(self.rootmo95)
        about_window.title("About Multiapp Office")
        about_window.geometry("450x300")
        about_window.configure(bg=self.bg_color)
        about_window.transient(self.rootmo95)
        about_window.grab_set()
        
        title_frame = tk.Frame(about_window, bg=self.title_blue, height=35)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        tk.Label(title_frame, text="Multiapp Office MO95", bg=self.title_blue, 
                fg=self.white, font=("MS Sans Serif", 11, "bold")).pack(expand=True)
        
        content_frame = tk.Frame(about_window, bg=self.white)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        tk.Label(content_frame, text="Multiapp Office", bg=self.white, 
                font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(content_frame, text="Professional Edition", bg=self.white, 
                font=("Arial", 10)).pack()
        tk.Label(content_frame, text="Version 2.0 (MO95)", bg=self.white, 
                font=("Arial", 10)).pack(pady=5)
        tk.Label(content_frame, text="With Toggle Margin Padding", bg=self.white, 
                font=("Arial", 9, "italic")).pack(pady=5)
        tk.Label(content_frame, text="Copyright © 2025 Retro Computing Division", 
                bg=self.white, font=("MS Sans Serif", 8)).pack(pady=10)
        tk.Label(content_frame, text="All rights reserved.", bg=self.white, 
                font=("MS Sans Serif", 8)).pack()
        
        tk.Button(about_window, text="OK", command=about_window.destroy, width=12, 
                 bg=self.bg_color, font=("MS Sans Serif", 8)).pack(pady=15)

if __name__ == "__main__":
    rootmo95 = tk.Tk()
    app = MO95Office(rootmo95)
    rootmo95.mainloop()