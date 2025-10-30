import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, colorchooser
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io

class RetroPDFEditor:
    def __init__(self, rootacrobated):
        self.rootacrobated = rootacrobated
        self.rootacrobated.title("PDF Editor")
        self.rootacrobated.geometry("1100x700")
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.active_bg = "#000080"
        self.button_bg = "#c0c0c0"
        self.text_color = "#000000"
        
        self.rootacrobated.configure(bg=self.bg_color)
        
        self.pdf_document = None
        self.current_page = 0
        self.pdf_path = None
        self.zoom_level = 1.0
        self.tool_mode = None  # 'text', 'highlight', 'draw', 'erase'
        self.annotations = []
        self.current_color = (1, 0, 0)  # Red
        self.font_size = 12
        self.drawing = False
        self.draw_start = None
        self.temp_shape = None  # For preview rectangle/circle
        self.draw_points = []  # For freehand drawing
        
        self.create_menu()
        self.create_toolbar()
        self.create_main_area()
        self.create_statusbar()
        
    def create_menu(self):
        menubar = tk.Menu(self.rootacrobated, bg=self.bg_color, relief=tk.FLAT)
        self.rootacrobated.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PDF...", command=self.open_pdf, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_pdf, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_pdf_as)
        file_menu.add_command(label="Export Page as Image...", command=self.export_page_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.rootacrobated.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Text", command=lambda: self.set_tool('text'))
        edit_menu.add_command(label="Highlight Text", command=lambda: self.set_tool('highlight'))
        edit_menu.add_command(label="Draw", command=lambda: self.set_tool('draw'))
        edit_menu.add_command(label="Add Rectangle", command=self.add_rectangle)
        edit_menu.add_command(label="Add Circle", command=self.add_circle)
        edit_menu.add_separator()
        edit_menu.add_command(label="Insert Blank Page", command=self.insert_page)
        edit_menu.add_command(label="Delete Page", command=self.delete_page)
        edit_menu.add_command(label="Rotate Page", command=self.rotate_page)
        edit_menu.add_separator()
        edit_menu.add_command(label="Merge PDFs...", command=self.merge_pdfs)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="+")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="-")
        view_menu.add_command(label="Actual Size", command=self.actual_size, accelerator="Ctrl+0")
        view_menu.add_command(label="Fit Width", command=self.fit_width)
        view_menu.add_command(label="Fit Page", command=self.fit_page)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Text Tool", command=lambda: self.set_tool('text'))
        tools_menu.add_command(label="Highlight Tool", command=lambda: self.set_tool('highlight'))
        tools_menu.add_command(label="Draw Tool", command=lambda: self.set_tool('draw'))
        tools_menu.add_separator()
        tools_menu.add_command(label="Choose Color...", command=self.choose_color)
        tools_menu.add_command(label="Font Size...", command=self.set_font_size)
        
        # Document menu
        doc_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Document", menu=doc_menu)
        doc_menu.add_command(label="Document Properties", command=self.show_properties)
        doc_menu.add_command(label="Extract Pages...", command=self.extract_pages)
        doc_menu.add_command(label="Split Document...", command=self.split_document)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_toolbar(self):
        toolbar = tk.Frame(self.rootacrobated, bg=self.bg_color, relief=tk.RAISED, bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        # File operations
        btn_open = tk.Button(toolbar, text="Open", width=7, command=self.open_pdf,
                            bg=self.button_bg, relief=tk.RAISED, bd=2)
        btn_open.pack(side=tk.LEFT, padx=2, pady=2)
        
        btn_save = tk.Button(toolbar, text="Save", width=7, command=self.save_pdf,
                            bg=self.button_bg, relief=tk.RAISED, bd=2)
        btn_save.pack(side=tk.LEFT, padx=2, pady=2)
        
        tk.Frame(toolbar, width=2, bg="#808080", relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=4)
        
        # Navigation
        btn_first = tk.Button(toolbar, text="|<", width=4, command=self.first_page,
                             bg=self.button_bg, relief=tk.RAISED, bd=2)
        btn_first.pack(side=tk.LEFT, padx=1, pady=2)
        
        btn_prev = tk.Button(toolbar, text="<", width=4, command=self.prev_page,
                            bg=self.button_bg, relief=tk.RAISED, bd=2)
        btn_prev.pack(side=tk.LEFT, padx=1, pady=2)
        
        self.page_entry = tk.Entry(toolbar, width=5, justify=tk.CENTER)
        self.page_entry.pack(side=tk.LEFT, padx=2)
        self.page_entry.bind('<Return>', lambda e: self.goto_page())
        
        btn_next = tk.Button(toolbar, text=">", width=4, command=self.next_page,
                            bg=self.button_bg, relief=tk.RAISED, bd=2)
        btn_next.pack(side=tk.LEFT, padx=1, pady=2)
        
        btn_last = tk.Button(toolbar, text=">|", width=4, command=self.last_page,
                            bg=self.button_bg, relief=tk.RAISED, bd=2)
        btn_last.pack(side=tk.LEFT, padx=1, pady=2)
        
        tk.Frame(toolbar, width=2, bg="#808080", relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=4)
        
        # Zoom controls
        btn_zoom_out = tk.Button(toolbar, text="-", width=3, command=self.zoom_out,
                                bg=self.button_bg, relief=tk.RAISED, bd=2)
        btn_zoom_out.pack(side=tk.LEFT, padx=1, pady=2)
        
        self.zoom_label = tk.Label(toolbar, text="100%", width=6, bg=self.bg_color, relief=tk.SUNKEN, bd=1)
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        
        btn_zoom_in = tk.Button(toolbar, text="+", width=3, command=self.zoom_in,
                               bg=self.button_bg, relief=tk.RAISED, bd=2)
        btn_zoom_in.pack(side=tk.LEFT, padx=1, pady=2)
        
        tk.Frame(toolbar, width=2, bg="#808080", relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=4)
        
        # Tool buttons
        self.btn_text = tk.Button(toolbar, text="Text", width=7, command=lambda: self.set_tool('text'),
                                 bg=self.button_bg, relief=tk.RAISED, bd=2)
        self.btn_text.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.btn_highlight = tk.Button(toolbar, text="Highlight", width=8, command=lambda: self.set_tool('highlight'),
                                       bg=self.button_bg, relief=tk.RAISED, bd=2)
        self.btn_highlight.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.btn_draw = tk.Button(toolbar, text="Draw", width=7, command=lambda: self.set_tool('draw'),
                                 bg=self.button_bg, relief=tk.RAISED, bd=2)
        self.btn_draw.pack(side=tk.LEFT, padx=2, pady=2)
        
        tk.Frame(toolbar, width=2, bg="#808080", relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=4)
        
        # Page operations
        btn_rotate = tk.Button(toolbar, text="Rotate", width=7, command=self.rotate_page,
                              bg=self.button_bg, relief=tk.RAISED, bd=2)
        btn_rotate.pack(side=tk.LEFT, padx=2, pady=2)
        
        btn_delete = tk.Button(toolbar, text="Del Page", width=8, command=self.delete_page,
                              bg=self.button_bg, relief=tk.RAISED, bd=2)
        btn_delete.pack(side=tk.LEFT, padx=2, pady=2)
        
    def create_main_area(self):
        # Main container
        main_container = tk.Frame(self.rootacrobated, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left sidebar with thumbnails
        self.sidebar = tk.Frame(main_container, bg=self.bg_color, width=150, relief=tk.SUNKEN, bd=2)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        self.sidebar.pack_propagate(False)
        
        sidebar_label = tk.Label(self.sidebar, text="Pages", bg=self.bg_color, font=("MS Sans Serif", 8, "bold"))
        sidebar_label.pack(pady=5)
        
        self.thumbnail_canvas = tk.Canvas(self.sidebar, bg="white", width=140)
        thumb_scrollbar = tk.Scrollbar(self.sidebar, orient=tk.VERTICAL, command=self.thumbnail_canvas.yview)
        self.thumbnail_canvas.configure(yscrollcommand=thumb_scrollbar.set)
        
        thumb_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.thumbnail_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse wheel for thumbnail scrolling
        self.thumbnail_canvas.bind('<MouseWheel>', self.on_thumbnail_mousewheel)
        self.thumbnail_canvas.bind('<Button-4>', self.on_thumbnail_mousewheel)
        self.thumbnail_canvas.bind('<Button-5>', self.on_thumbnail_mousewheel)
        
        # Main canvas area
        canvas_container = tk.Frame(main_container, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar_y = tk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scrollbar_x = tk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(canvas_container, bg="white", 
                               yscrollcommand=self.scrollbar_y.set,
                               xscrollcommand=self.scrollbar_x.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar_y.config(command=self.canvas.yview)
        self.scrollbar_x.config(command=self.canvas.xview)
        
        # Bind mouse events for drawing
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_canvas_release)
        
        # Bind mouse wheel for scrolling
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.canvas.bind('<Button-4>', self.on_mousewheel)  # Linux scroll up
        self.canvas.bind('<Button-5>', self.on_mousewheel)  # Linux scroll down
        
    def create_statusbar(self):
        statusbar = tk.Frame(self.rootacrobated, bg=self.bg_color, relief=tk.SUNKEN, bd=1)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(statusbar, text="Ready", bg=self.bg_color, 
                                     anchor=tk.W, padx=5)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.tool_label = tk.Label(statusbar, text="Tool: Select", bg=self.bg_color, 
                                   padx=10, relief=tk.SUNKEN, bd=1)
        self.tool_label.pack(side=tk.RIGHT, padx=2)
        
        self.page_label = tk.Label(statusbar, text="No document", bg=self.bg_color, 
                                   padx=10, relief=tk.SUNKEN, bd=1)
        self.page_label.pack(side=tk.RIGHT, padx=2)
        
    def set_tool(self, tool):
        self.tool_mode = tool
        
        # Reset all button reliefs
        self.btn_text.config(relief=tk.RAISED)
        self.btn_highlight.config(relief=tk.RAISED)
        self.btn_draw.config(relief=tk.RAISED)
        
        # Set active button
        if tool == 'text':
            self.btn_text.config(relief=tk.SUNKEN)
            self.tool_label.config(text="Tool: Text")
        elif tool == 'highlight':
            self.btn_highlight.config(relief=tk.SUNKEN)
            self.tool_label.config(text="Tool: Highlight")
        elif tool == 'draw':
            self.btn_draw.config(relief=tk.SUNKEN)
            self.tool_label.config(text="Tool: Draw")
        elif tool == 'rectangle':
            self.tool_label.config(text="Tool: Rectangle")
        elif tool == 'circle':
            self.tool_label.config(text="Tool: Circle")
        else:
            self.tool_label.config(text="Ready")
            
    def on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
    
    def on_thumbnail_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.thumbnail_canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.thumbnail_canvas.yview_scroll(-1, "units")
            
    def on_canvas_click(self, event):
        if not self.pdf_document:
            return
            
        # Convert canvas coordinates to PDF coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        if self.tool_mode == 'text':
            text = simpledialog.askstring("Add Text", "Enter text:")
            if text:
                page = self.pdf_document[self.current_page]
                pdf_x = canvas_x / self.zoom_level
                pdf_y = canvas_y / self.zoom_level
                page.insert_text((pdf_x, pdf_y), text, fontsize=self.font_size, 
                               color=self.current_color)
                self.display_page()
                
        elif self.tool_mode in ['highlight', 'rectangle', 'circle']:
            self.draw_start = (canvas_x, canvas_y)
            self.drawing = True
            
        elif self.tool_mode == 'draw':
            self.drawing = True
            self.draw_points = [(canvas_x, canvas_y)]
            
    def on_canvas_drag(self, event):
        if not self.drawing or not self.pdf_document:
            return
            
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        if self.tool_mode == 'draw':
            # Freehand drawing - add points and draw lines
            if len(self.draw_points) > 0:
                last_point = self.draw_points[-1]
                color_hex = '#{:02x}{:02x}{:02x}'.format(
                    int(self.current_color[0] * 255),
                    int(self.current_color[1] * 255),
                    int(self.current_color[2] * 255)
                )
                # Draw line from last point to current point
                self.canvas.create_line(
                    last_point[0], last_point[1], canvas_x, canvas_y,
                    fill=color_hex, width=3, capstyle=tk.ROUND, smooth=True
                )
                self.draw_points.append((canvas_x, canvas_y))
            return
        
        # For other tools, remove previous preview shape
        if not self.draw_start:
            return
            
        if self.temp_shape:
            self.canvas.delete(self.temp_shape)
            self.temp_shape = None
            
        # Draw preview shape
        x1, y1 = self.draw_start
        
        if self.tool_mode == 'rectangle':
            color_hex = '#{:02x}{:02x}{:02x}'.format(
                int(self.current_color[0] * 255),
                int(self.current_color[1] * 255),
                int(self.current_color[2] * 255)
            )
            self.temp_shape = self.canvas.create_rectangle(
                x1, y1, canvas_x, canvas_y, 
                outline=color_hex, width=2
            )
        elif self.tool_mode == 'circle':
            color_hex = '#{:02x}{:02x}{:02x}'.format(
                int(self.current_color[0] * 255),
                int(self.current_color[1] * 255),
                int(self.current_color[2] * 255)
            )
            self.temp_shape = self.canvas.create_oval(
                x1, y1, canvas_x, canvas_y, 
                outline=color_hex, width=2
            )
        elif self.tool_mode == 'highlight':
            color_hex = '#{:02x}{:02x}{:02x}'.format(
                int(self.current_color[0] * 255),
                int(self.current_color[1] * 255),
                int(self.current_color[2] * 255)
            )
            self.temp_shape = self.canvas.create_rectangle(
                x1, y1, canvas_x, canvas_y,
                fill=color_hex, stipple='gray50', outline=''
            )
            
    def on_canvas_release(self, event):
        if not self.drawing or not self.pdf_document:
            return
            
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Remove preview shape
        if self.temp_shape:
            self.canvas.delete(self.temp_shape)
            self.temp_shape = None
        
        page = self.pdf_document[self.current_page]
        
        if self.tool_mode == 'draw':
            # Freehand drawing - draw all segments
            if len(self.draw_points) > 1:
                for i in range(len(self.draw_points) - 1):
                    x1, y1 = self.draw_points[i][0] / self.zoom_level, self.draw_points[i][1] / self.zoom_level
                    x2, y2 = self.draw_points[i + 1][0] / self.zoom_level, self.draw_points[i + 1][1] / self.zoom_level
                    page.draw_line((x1, y1), (x2, y2), color=self.current_color, width=2)
                self.display_page()
            self.draw_points = []
            
        elif self.draw_start:
            x1, y1 = self.draw_start[0] / self.zoom_level, self.draw_start[1] / self.zoom_level
            x2, y2 = canvas_x / self.zoom_level, canvas_y / self.zoom_level
            
            if self.tool_mode == 'highlight':
                rect = fitz.Rect(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                highlight = page.add_highlight_annot(rect)
                highlight.set_colors({"stroke": self.current_color})
                highlight.update()
                self.display_page()
                
            elif self.tool_mode == 'rectangle':
                rect = fitz.Rect(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                page.draw_rect(rect, color=self.current_color, width=2)
                self.display_page()
                
            elif self.tool_mode == 'circle':
                # Calculate center and radius
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                radius = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 / 2
                center = fitz.Point(center_x, center_y)
                page.draw_circle(center, radius, color=self.current_color, width=2)
                self.display_page()
            
            self.draw_start = None
            
        self.drawing = False
        
    def open_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Open PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.pdf_document = fitz.open(file_path)
                self.pdf_path = file_path
                self.current_page = 0
                self.zoom_level = 1.0
                self.display_page()
                self.generate_thumbnails()
                self.status_label.config(text=f"Opened: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF:\n{str(e)}")
                
    def save_pdf(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
            
        if self.pdf_path:
            try:
                self.pdf_document.save(self.pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
                self.status_label.config(text=f"Saved: {self.pdf_path}")
                messagebox.showinfo("Success", "PDF saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}")
        else:
            self.save_pdf_as()
            
    def save_pdf_as(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.pdf_document.save(file_path)
                self.pdf_path = file_path
                self.status_label.config(text=f"Saved: {file_path}")
                messagebox.showinfo("Success", "PDF saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}")
                
    def display_page(self):
        if not self.pdf_document:
            return
            
        page = self.pdf_document[self.current_page]
        mat = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=mat)
        
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        
        self.photo = ImageTk.PhotoImage(img)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        self.page_label.config(
            text=f"Page {self.current_page + 1} of {len(self.pdf_document)}"
        )
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(self.current_page + 1))
        
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        
    def generate_thumbnails(self):
        if not self.pdf_document:
            return
            
        self.thumbnail_canvas.delete("all")
        y_pos = 10
        
        for i in range(len(self.pdf_document)):
            page = self.pdf_document[i]
            mat = fitz.Matrix(0.2, 0.2)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            thumb = ImageTk.PhotoImage(img)
            # Store reference to prevent garbage collection
            if not hasattr(self, 'thumbnails'):
                self.thumbnails = []
            self.thumbnails.append(thumb)
            
            self.thumbnail_canvas.create_image(70, y_pos, image=thumb)
            self.thumbnail_canvas.create_text(70, y_pos + 60, text=f"Page {i+1}")
            
            # Make clickable
            self.thumbnail_canvas.tag_bind(
                self.thumbnail_canvas.create_rectangle(10, y_pos - 50, 130, y_pos + 70, outline=""),
                '<Button-1>',
                lambda e, page_num=i: self.jump_to_page(page_num)
            )
            
            y_pos += 100
            
        self.thumbnail_canvas.config(scrollregion=self.thumbnail_canvas.bbox(tk.ALL))
        
    def jump_to_page(self, page_num):
        if self.pdf_document and 0 <= page_num < len(self.pdf_document):
            self.current_page = page_num
            self.display_page()
            
    def goto_page(self):
        try:
            page_num = int(self.page_entry.get()) - 1
            self.jump_to_page(page_num)
        except ValueError:
            messagebox.showerror("Error", "Invalid page number!")
            
    def first_page(self):
        if self.pdf_document:
            self.current_page = 0
            self.display_page()
            
    def next_page(self):
        if self.pdf_document and self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.display_page()
            
    def prev_page(self):
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.display_page()
            
    def last_page(self):
        if self.pdf_document:
            self.current_page = len(self.pdf_document) - 1
            self.display_page()
            
    def zoom_in(self):
        if self.pdf_document:
            self.zoom_level *= 1.25
            self.display_page()
            
    def zoom_out(self):
        if self.pdf_document:
            self.zoom_level /= 1.25
            self.display_page()
            
    def actual_size(self):
        if self.pdf_document:
            self.zoom_level = 1.0
            self.display_page()
            
    def fit_width(self):
        if self.pdf_document:
            page = self.pdf_document[self.current_page]
            canvas_width = self.canvas.winfo_width()
            self.zoom_level = canvas_width / page.rect.width
            self.display_page()
            
    def fit_page(self):
        if self.pdf_document:
            page = self.pdf_document[self.current_page]
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            zoom_w = canvas_width / page.rect.width
            zoom_h = canvas_height / page.rect.height
            self.zoom_level = min(zoom_w, zoom_h)
            self.display_page()
            
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Color")
        if color[0]:
            rgb = color[0]
            self.current_color = (rgb[0]/255, rgb[1]/255, rgb[2]/255)
            self.status_label.config(text=f"Color changed")
            
    def set_font_size(self):
        size = simpledialog.askinteger("Font Size", "Enter font size:", 
                                       initialvalue=self.font_size, minvalue=6, maxvalue=72)
        if size:
            self.font_size = size
            
    def add_rectangle(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
        
        self.set_tool('rectangle')
        self.status_label.config(text="Click and drag to draw rectangle")
        
    def add_circle(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
        
        self.set_tool('circle')
        self.status_label.config(text="Click and drag to draw circle")
        
    def insert_page(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
            
        self.pdf_document.insert_page(self.current_page + 1)
        self.current_page += 1
        self.display_page()
        self.generate_thumbnails()
        self.status_label.config(text="Blank page inserted")
        
    def delete_page(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
            
        if len(self.pdf_document) == 1:
            messagebox.showwarning("Warning", "Cannot delete the only page!")
            return
            
        result = messagebox.askyesno("Confirm", 
                                    f"Delete page {self.current_page + 1}?")
        if result:
            self.pdf_document.delete_page(self.current_page)
            if self.current_page >= len(self.pdf_document):
                self.current_page = len(self.pdf_document) - 1
            self.display_page()
            self.generate_thumbnails()
            self.status_label.config(text="Page deleted")
            
    def rotate_page(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
            
        page = self.pdf_document[self.current_page]
        page.set_rotation(page.rotation + 90)
        self.display_page()
        self.generate_thumbnails()
        self.status_label.config(text="Page rotated 90 degrees")
        
    def export_page_image(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Page as Image",
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                page = self.pdf_document[self.current_page]
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                pix.save(file_path)
                self.status_label.config(text=f"Page exported: {file_path}")
                messagebox.showinfo("Success", "Page exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export page:\n{str(e)}")
                
    def merge_pdfs(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
            
        file_paths = filedialog.askopenfilenames(
            title="Select PDFs to Merge",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if file_paths:
            try:
                for file_path in file_paths:
                    src_pdf = fitz.open(file_path)
                    self.pdf_document.insert_pdf(src_pdf)
                    src_pdf.close()
                self.display_page()
                self.generate_thumbnails()
                self.status_label.config(text=f"Merged {len(file_paths)} PDF(s)")
                messagebox.showinfo("Success", "PDFs merged successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")
                
    def extract_pages(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
            
        # Ask for page range
        page_range = simpledialog.askstring("Extract Pages", 
                                           f"Enter page range (e.g., 1-3, 5, 7-9):\n"
                                           f"Total pages: {len(self.pdf_document)}")
        if not page_range:
            return
            
        try:
            # Parse page range
            pages_to_extract = []
            parts = page_range.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    start, end = part.split('-')
                    pages_to_extract.extend(range(int(start)-1, int(end)))
                else:
                    pages_to_extract.append(int(part)-1)
            
            # Create new PDF with extracted pages
            file_path = filedialog.asksaveasfilename(
                title="Save Extracted Pages",
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
            )
            
            if file_path:
                new_pdf = fitz.open()
                for page_num in pages_to_extract:
                    if 0 <= page_num < len(self.pdf_document):
                        new_pdf.insert_pdf(self.pdf_document, from_page=page_num, to_page=page_num)
                new_pdf.save(file_path)
                new_pdf.close()
                self.status_label.config(text=f"Extracted pages saved: {file_path}")
                messagebox.showinfo("Success", "Pages extracted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract pages:\n{str(e)}")
            
    def split_document(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
            
        # Ask for split point
        split_page = simpledialog.askinteger("Split Document", 
                                            f"Split after page number:\n"
                                            f"Total pages: {len(self.pdf_document)}",
                                            minvalue=1, maxvalue=len(self.pdf_document)-1)
        if not split_page:
            return
            
        try:
            folder = filedialog.askdirectory(title="Select Folder to Save Split PDFs")
            if folder:
                # Create first part
                pdf1 = fitz.open()
                pdf1.insert_pdf(self.pdf_document, from_page=0, to_page=split_page-1)
                pdf1.save(f"{folder}/part1.pdf")
                pdf1.close()
                
                # Create second part
                pdf2 = fitz.open()
                pdf2.insert_pdf(self.pdf_document, from_page=split_page, to_page=len(self.pdf_document)-1)
                pdf2.save(f"{folder}/part2.pdf")
                pdf2.close()
                
                self.status_label.config(text=f"Document split into 2 files")
                messagebox.showinfo("Success", "Document split successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to split document:\n{str(e)}")
            
    def show_properties(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF document loaded!")
            return
            
        metadata = self.pdf_document.metadata
        info = f"Document Properties\n\n"
        info += f"Title: {metadata.get('title', 'N/A')}\n"
        info += f"Author: {metadata.get('author', 'N/A')}\n"
        info += f"Subject: {metadata.get('subject', 'N/A')}\n"
        info += f"Keywords: {metadata.get('keywords', 'N/A')}\n"
        info += f"Creator: {metadata.get('creator', 'N/A')}\n"
        info += f"Producer: {metadata.get('producer', 'N/A')}\n"
        info += f"Pages: {len(self.pdf_document)}\n"
        info += f"Format: {metadata.get('format', 'N/A')}\n"
        
        messagebox.showinfo("Document Properties", info)
        
    def show_about(self):
        messagebox.showinfo("About", 
                          "PDF Editor\n\n"
                          "Version 1.0\n\n"
                          "A simple PDF editing application\n\n"
                          "Features:\n"
                          "- Add text and annotations\n"
                          "- Highlight and draw\n"
                          "- Page management\n"
                          "- Merge and split PDFs\n"
                          "- Export pages as images")

if __name__ == "__main__":
    rootacrobated = tk.Tk()
    app = RetroPDFEditor(rootacrobated)
    rootacrobated.mainloop()