import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, simpledialog, ttk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageDraw, ImageFont, ImageOps
import os
import math

class Win95ImageEditor:
    def __init__(self, rootimged):
        self.rootimged = rootimged
        self.rootimged.title("Image Editor")
        self.rootimged.configure(bg="#c0c0c0")
        
        # Variables
        self.image = None
        self.original_image = None
        self.photo = None
        self.canvas_images = []
        self.stickers = []
        self.history = []
        self.history_index = -1
        self.current_tool = "select"
        self.drawing = False
        self.start_x = None
        self.start_y = None
        self.current_color = "#000000"
        self.brush_size = 3
        self.zoom_level = 1.0
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.layers = []
        self.selected_text_item = None
        self.text_edit_mode = False
        self.selected_item = None
        self.selection_handles = []
        self.resize_handle = None
        self.original_image_data = {}
        self.transparency_var = tk.IntVar(value=100)
        
        # Create menu bar
        self.create_menu()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main container
        main_container = tk.Frame(self.rootimged, bg="#c0c0c0")
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left sidebar - Tools
        self.create_tool_panel(main_container)
        
        # Center - Canvas
        canvas_frame = tk.Frame(main_container, bg="#c0c0c0", relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#ffffff", width=700, height=500)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        # Right sidebar - Properties
        self.create_properties_panel(main_container)
        
        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        
        # Status bar
        self.create_status_bar()
        
    def create_menu(self):
        menubar = tk.Menu(self.rootimged, bg="#c0c0c0", relief=tk.RAISED, bd=2)
        self.rootimged.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_canvas, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_image_as)
        file_menu.add_command(label="Export Canvas...", command=self.export_canvas)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.rootimged.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Copy", command=self.copy_selection)
        edit_menu.add_command(label="Paste", command=self.paste_selection)
        edit_menu.add_command(label="Delete Selected", command=self.delete_selected)
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Canvas", command=self.clear_canvas)
        edit_menu.add_command(label="Reset Image", command=self.reset_image)
        
        # Image menu
        image_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
        menubar.add_cascade(label="Image", menu=image_menu)
        image_menu.add_command(label="Resize...", command=self.resize_image)
        image_menu.add_command(label="Rotate 90° CW", command=lambda: self.rotate_image(90))
        image_menu.add_command(label="Rotate 90° CCW", command=lambda: self.rotate_image(-90))
        image_menu.add_command(label="Flip Horizontal", command=self.flip_horizontal)
        image_menu.add_command(label="Flip Vertical", command=self.flip_vertical)
        image_menu.add_separator()
        image_menu.add_command(label="Crop to Selection", command=self.crop_image)
        
        # Effects menu
        effects_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
        menubar.add_cascade(label="Effects", menu=effects_menu)
        effects_menu.add_command(label="Blur", command=lambda: self.apply_effect("blur"))
        effects_menu.add_command(label="Sharpen", command=lambda: self.apply_effect("sharpen"))
        effects_menu.add_command(label="Emboss", command=lambda: self.apply_effect("emboss"))
        effects_menu.add_command(label="Contour", command=lambda: self.apply_effect("contour"))
        effects_menu.add_command(label="Edge Enhance", command=lambda: self.apply_effect("edge"))
        effects_menu.add_separator()
        effects_menu.add_command(label="Grayscale", command=self.convert_grayscale)
        effects_menu.add_command(label="Sepia", command=self.apply_sepia)
        effects_menu.add_command(label="Invert Colors", command=self.invert_colors)
        effects_menu.add_command(label="Posterize", command=self.posterize)
        
        # Adjust menu
        adjust_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
        menubar.add_cascade(label="Adjust", menu=adjust_menu)
        adjust_menu.add_command(label="Brightness...", command=self.adjust_brightness_dialog)
        adjust_menu.add_command(label="Contrast...", command=self.adjust_contrast_dialog)
        adjust_menu.add_command(label="Saturation...", command=self.adjust_saturation_dialog)
        adjust_menu.add_command(label="Hue...", command=self.adjust_hue)
        adjust_menu.add_separator()
        adjust_menu.add_command(label="Auto Enhance", command=self.auto_enhance)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Actual Size", command=self.zoom_actual, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_command(label="Grid", command=self.toggle_grid)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_toolbar(self):
        toolbar = tk.Frame(self.rootimged, bg="#c0c0c0", relief=tk.RAISED, bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        btn_style = {"bg": "#c0c0c0", "relief": tk.RAISED, "bd":2,
                    "font": ("MS Sans Serif", 8), "padx": 8, "pady": 2}
        
        tk.Button(toolbar, text="New", command=self.new_canvas, **btn_style).pack(side=tk.LEFT, padx=1, pady=2)
        tk.Button(toolbar, text="Open", command=self.open_image, **btn_style).pack(side=tk.LEFT, padx=1, pady=2)
        tk.Button(toolbar, text="Save", command=self.save_image, **btn_style).pack(side=tk.LEFT, padx=1, pady=2)
        
        tk.Frame(toolbar, width=2, bg="#808080", relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=2)
        
        tk.Button(toolbar, text="Undo", command=self.undo, **btn_style).pack(side=tk.LEFT, padx=1, pady=2)
        tk.Button(toolbar, text="Redo", command=self.redo, **btn_style).pack(side=tk.LEFT, padx=1, pady=2)
        
        tk.Frame(toolbar, width=2, bg="#808080", relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=3, pady=2)
        
        tk.Button(toolbar, text="Zoom In", command=self.zoom_in, **btn_style).pack(side=tk.LEFT, padx=1, pady=2)
        tk.Button(toolbar, text="Zoom Out", command=self.zoom_out, **btn_style).pack(side=tk.LEFT, padx=1, pady=2)
        
        self.zoom_label = tk.Label(toolbar, text="100%", bg="#c0c0c0", font=("MS Sans Serif", 8), width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        
    def create_tool_panel(self, parent):
        tool_frame = tk.Frame(parent, bg="#c0c0c0", relief=tk.RAISED, bd=2, width=120)
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        tool_frame.pack_propagate(False)
        
        tk.Label(tool_frame, text="Tools", bg="#c0c0c0", font=("MS Sans Serif", 9, "bold")).pack(pady=5)
        
        tools = [
            ("Select", "select"),
            ("Draw", "draw"),
            ("Line", "line"),
            ("Rectangle", "rectangle"),
            ("Circle", "circle"),
            ("Text", "text"),
            ("Eraser", "eraser"),
        ]
        
        self.tool_buttons = {}
        for name, tool in tools:
            btn = tk.Button(tool_frame, text=name, command=lambda t=tool: self.set_tool(t),
                          bg="#c0c0c0", relief=tk.RAISED, bd=2, font=("MS Sans Serif", 8),
                          width=12, anchor=tk.W)
            btn.pack(pady=2, padx=5)
            self.tool_buttons[tool] = btn
        
        self.set_tool("select")
        
        tk.Frame(tool_frame, height=2, bg="#808080", relief=tk.SUNKEN).pack(fill=tk.X, pady=5)
        
        tk.Label(tool_frame, text="Color", bg="#c0c0c0", font=("MS Sans Serif", 8)).pack(pady=2)
        self.color_display = tk.Frame(tool_frame, bg=self.current_color, width=50, height=30, 
                                     relief=tk.SUNKEN, bd=2)
        self.color_display.pack(pady=2)
        tk.Button(tool_frame, text="Choose Color", command=self.choose_color,
                 bg="#c0c0c0", relief=tk.RAISED, bd=2, font=("MS Sans Serif", 8)).pack(pady=2)
        
        tk.Label(tool_frame, text="Brush Size", bg="#c0c0c0", font=("MS Sans Serif", 8)).pack(pady=5)
        self.brush_scale = tk.Scale(tool_frame, from_=1, to=20, orient=tk.HORIZONTAL,
                                   bg="#c0c0c0", length=100, command=self.update_brush_size)
        self.brush_scale.set(3)
        self.brush_scale.pack()
        
        tk.Frame(tool_frame, height=2, bg="#808080", relief=tk.SUNKEN).pack(fill=tk.X, pady=5)
        
        tk.Button(tool_frame, text="Sticker Library", command=self.show_sticker_library,
                 bg="#c0c0c0", relief=tk.RAISED, bd=2, font=("MS Sans Serif", 8),
                 width=12).pack(pady=2, padx=5)
        
        tk.Button(tool_frame, text="Add Image", command=self.add_sticker,
                 bg="#c0c0c0", relief=tk.RAISED, bd=2, font=("MS Sans Serif", 8),
                 width=12).pack(pady=2, padx=5)
        
    def create_properties_panel(self, parent):
        props_frame = tk.Frame(parent, bg="#c0c0c0", relief=tk.RAISED, bd=2, width=180)
        props_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        props_frame.pack_propagate(False)
        
        tk.Label(props_frame, text="Properties", bg="#c0c0c0", 
                font=("MS Sans Serif", 9, "bold")).pack(pady=5)
        
        self.props_text = tk.Text(props_frame, height=15, width=20, bg="#ffffff",
                                 font=("MS Sans Serif", 8), relief=tk.SUNKEN, bd=2,
                                 state=tk.DISABLED)
        self.props_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        tk.Frame(props_frame, height=2, bg="#808080", relief=tk.SUNKEN).pack(fill=tk.X, pady=5)
        
        # Frame pentru controale dinamice (transparență, etc.)
        self.dynamic_controls_frame = tk.Frame(props_frame, bg="#c0c0c0")
        self.dynamic_controls_frame.pack(fill=tk.X, padx=5)
        
        tk.Frame(props_frame, height=2, bg="#808080", relief=tk.SUNKEN).pack(fill=tk.X, pady=5)
        
        tk.Label(props_frame, text="Quick Effects", bg="#c0c0c0", 
                font=("MS Sans Serif", 8, "bold")).pack(pady=5)
        
        effect_btn_style = {"bg": "#c0c0c0", "relief": tk.RAISED, "bd": 2,
                          "font": ("MS Sans Serif", 8), "width": 15}
        
        tk.Button(props_frame, text="Auto Enhance", command=self.auto_enhance, **effect_btn_style).pack(pady=2)
        tk.Button(props_frame, text="Sharpen", command=lambda: self.apply_effect("sharpen"), **effect_btn_style).pack(pady=2)
        tk.Button(props_frame, text="Blur", command=lambda: self.apply_effect("blur"), **effect_btn_style).pack(pady=2)
        tk.Button(props_frame, text="Grayscale", command=self.convert_grayscale, **effect_btn_style).pack(pady=2)
        tk.Button(props_frame, text="Sepia", command=self.apply_sepia, **effect_btn_style).pack(pady=2)
        
    def show_transparency_controls(self):
        """Show transparency slider in properties panel"""
        # Șterge orice controale existente
        for widget in self.dynamic_controls_frame.winfo_children():
            widget.destroy()
        
        # Adaugă slider-ul de transparență
        tk.Label(self.dynamic_controls_frame, text="Transparency:", bg="#c0c0c0", 
                font=("MS Sans Serif", 8, "bold")).pack(pady=(5,2))
        
        transparency_slider = tk.Scale(self.dynamic_controls_frame, from_=0, to=100, 
                                      orient=tk.HORIZONTAL,
                                      variable=self.transparency_var,
                                      command=self.update_sticker_transparency,
                                      bg="#c0c0c0", relief=tk.FLAT,
                                      font=("MS Sans Serif", 7))
        transparency_slider.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(self.dynamic_controls_frame, text="(0=transparent, 100=opaque)", bg="#c0c0c0", 
                font=("MS Sans Serif", 7)).pack(pady=(0,5))

    def hide_transparency_controls(self):
        """Hide transparency slider from properties panel"""
        # Șterge toate controalele din frame-ul dinamic
        for widget in self.dynamic_controls_frame.winfo_children():
            widget.destroy()
        
    def create_status_bar(self):
        status_frame = tk.Frame(self.rootimged, bg="#c0c0c0", relief=tk.SUNKEN, bd=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status = tk.Label(status_frame, text="Ready", anchor=tk.W, 
                              bg="#c0c0c0", font=("MS Sans Serif", 8))
        self.status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        self.coords_label = tk.Label(status_frame, text="X: 0  Y: 0", anchor=tk.E,
                                     bg="#c0c0c0", font=("MS Sans Serif", 8), width=15)
        self.coords_label.pack(side=tk.RIGHT, padx=5)
        
        self.canvas.bind("<Motion>", self.update_coords)
        
    def update_coords(self, event):
        self.coords_label.config(text=f"X: {event.x}  Y: {event.y}")
        
    def set_tool(self, tool):
        self.current_tool = tool
        for t, btn in self.tool_buttons.items():
            if t == tool:
                btn.config(relief=tk.SUNKEN, bg="#ffffff")
            else:
                btn.config(relief=tk.RAISED, bg="#c0c0c0")
        if hasattr(self, 'status'):
            self.status.config(text=f"Tool: {tool.capitalize()}")
        
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Color", color=self.current_color)
        if color[1]:
            self.current_color = color[1]
            self.color_display.config(bg=self.current_color)
            
    def update_brush_size(self, value):
        self.brush_size = int(value)
        
    def new_canvas(self):
        self.clear_canvas()
        self.status.config(text="New canvas created")
        
    def update_properties(self):
        if not self.image:
            return
            
        self.props_text.config(state=tk.NORMAL)
        self.props_text.delete(1.0, tk.END)
        
        info = f"Image Information\n{'='*20}\n\n"
        info += f"Size: {self.image.width} x {self.image.height}\n"
        info += f"Mode: {self.image.mode}\n"
        info += f"Format: {getattr(self.image, 'format', 'N/A')}\n\n"
        info += f"Zoom: {int(self.zoom_level * 100)}%\n"
        info += f"Tool: {self.current_tool}\n"
        info += f"Stickers: {len(self.stickers)}\n"
        
        self.props_text.insert(1.0, info)
        self.props_text.config(state=tk.DISABLED)
        
    def save_state(self):
        if self.image:
            self.history = self.history[:self.history_index + 1]
            self.history.append(self.image.copy())
            self.history_index += 1
            if len(self.history) > 20:
                self.history.pop(0)
                self.history_index -= 1
                
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.history[self.history_index].copy()
            self.display_image()
            self.status.config(text="Undo")
            
    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.image = self.history[self.history_index].copy()
            self.display_image()
            self.status.config(text="Redo")
            
    def open_image(self):
        filename = filedialog.askopenfilename(
            title="Open Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.original_image = Image.open(filename)
                self.image = self.original_image.copy()
                self.save_state()
                self.display_image()
                self.update_properties()
                self.status.config(text=f"Loaded: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open image:\n{str(e)}")
    
    def display_image(self):
        if self.image:
            canvas_width = self.canvas.winfo_width() or 700
            canvas_height = self.canvas.winfo_height() or 500
            
            img = self.image.copy()
            new_size = (int(img.width * self.zoom_level), int(img.height * self.zoom_level))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.delete("main_image")
            self.canvas.create_image(0, 0, anchor=tk.NW,
                                    image=self.photo, tags="main_image")
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            self.update_properties()
            
    def save_image(self):
        """Salvează canvas-ul complet ca PNG"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        if not filename:
            return
        
        try:
            # Ascunde handle-urile temporar
            self.clear_selection_handles()
            self.canvas.update()
            
            # Obține zona completă a canvas-ului
            x = self.canvas.winfo_rootx()
            y = self.canvas.winfo_rooty()
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            # Face screenshot
            import PIL.ImageGrab as ImageGrab
            img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            img.save(filename, 'PNG')
            
            self.status.config(text=f"Saved: {os.path.basename(filename)}")
            messagebox.showinfo("Success", "Canvas saved!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{str(e)}")
                
    def save_image_as(self):
        self.save_image()
        
    def export_canvas(self):
        """Export entire canvas including stickers and drawings"""
        if not self.canvas.find_all():
            messagebox.showwarning("Warning", "Canvas is empty!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if filename:
            try:
                x = self.canvas.winfo_rootx()
                y = self.canvas.winfo_rooty()
                w = self.canvas.winfo_width()
                h = self.canvas.winfo_height()
                
                from PIL import ImageGrab
                ImageGrab.grab(bbox=(x, y, x+w, y+h)).save(filename)
                messagebox.showinfo("Success", "Canvas exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export canvas:\n{str(e)}")
    
    def apply_effect(self, effect_type):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
            
        try:
            self.save_state()
            if effect_type == "blur":
                self.image = self.image.filter(ImageFilter.BLUR)
            elif effect_type == "sharpen":
                self.image = self.image.filter(ImageFilter.SHARPEN)
            elif effect_type == "emboss":
                self.image = self.image.filter(ImageFilter.EMBOSS)
            elif effect_type == "contour":
                self.image = self.image.filter(ImageFilter.CONTOUR)
            elif effect_type == "edge":
                self.image = self.image.filter(ImageFilter.EDGE_ENHANCE)
            
            self.display_image()
            self.status.config(text=f"Applied: {effect_type}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply effect:\n{str(e)}")
            
    def adjust_brightness_dialog(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        value = simpledialog.askfloat("Brightness", "Enter brightness factor (0.5 = darker, 2.0 = brighter):",
                                     initialvalue=1.0, minvalue=0.1, maxvalue=3.0)
        if value:
            self.save_state()
            enhancer = ImageEnhance.Brightness(self.image)
            self.image = enhancer.enhance(value)
            self.display_image()
            
    def adjust_contrast_dialog(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        value = simpledialog.askfloat("Contrast", "Enter contrast factor (0.5 = less, 2.0 = more):",
                                     initialvalue=1.0, minvalue=0.1, maxvalue=3.0)
        if value:
            self.save_state()
            enhancer = ImageEnhance.Contrast(self.image)
            self.image = enhancer.enhance(value)
            self.display_image()
            
    def adjust_saturation_dialog(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        value = simpledialog.askfloat("Saturation", "Enter saturation factor (0 = grayscale, 2.0 = vibrant):",
                                     initialvalue=1.0, minvalue=0, maxvalue=3.0)
        if value is not None:
            self.save_state()
            enhancer = ImageEnhance.Color(self.image)
            self.image = enhancer.enhance(value)
            self.display_image()
            
    def adjust_hue(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        messagebox.showinfo("Hue Adjust", "Hue rotation coming soon!")
        
    def convert_grayscale(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        self.save_state()
        self.image = self.image.convert("L").convert("RGB")
        self.display_image()
        self.status.config(text="Converted to grayscale")
        
    def apply_sepia(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        self.save_state()
        img = self.image.convert("RGB")
        pixels = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b = pixels[x, y]
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                pixels[x, y] = (min(255, tr), min(255, tg), min(255, tb))
        self.image = img
        self.display_image()
        self.status.config(text="Applied sepia tone")
        
    def invert_colors(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        self.save_state()
        self.image = ImageOps.invert(self.image.convert("RGB"))
        self.display_image()
        self.status.config(text="Inverted colors")
        
    def posterize(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        self.save_state()
        self.image = ImageOps.posterize(self.image.convert("RGB"), 3)
        self.display_image()
        self.status.config(text="Applied posterize effect")
        
    def auto_enhance(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        self.save_state()
        self.image = ImageOps.autocontrast(self.image)
        self.display_image()
        self.status.config(text="Auto enhanced")
        
    def resize_image(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
            
        dialog = tk.Toplevel(self.rootimged)
        dialog.title("Resize Image")
        dialog.configure(bg="#c0c0c0")
        dialog.geometry("300x150")
        
        tk.Label(dialog, text="Width:", bg="#c0c0c0").grid(row=0, column=0, padx=5, pady=5)
        width_var = tk.IntVar(value=self.image.width)
        tk.Entry(dialog, textvariable=width_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(dialog, text="Height:", bg="#c0c0c0").grid(row=1, column=0, padx=5, pady=5)
        height_var = tk.IntVar(value=self.image.height)
        tk.Entry(dialog, textvariable=height_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        def do_resize():
            self.save_state()
            new_size = (width_var.get(), height_var.get())
            self.image = self.image.resize(new_size, Image.Resampling.LANCZOS)
            self.display_image()
            dialog.destroy()
            
        tk.Button(dialog, text="Resize", command=do_resize, bg="#c0c0c0", relief=tk.RAISED).grid(row=2, column=0, columnspan=2, pady=10)
        
    def rotate_image(self, angle):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        self.save_state()
        self.image = self.image.rotate(-angle, expand=True)
        self.display_image()
        self.status.config(text=f"Rotated {angle}°")
        
    def flip_horizontal(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        self.save_state()
        self.image = ImageOps.mirror(self.image)
        self.display_image()
        self.status.config(text="Flipped horizontally")
        
    def flip_vertical(self):
        if not self.image:
            messagebox.showwarning("Warning", "Please load an image first!")
            return
        self.save_state()
        self.image = ImageOps.flip(self.image)
        self.display_image()
        self.status.config(text="Flipped vertically")
        
    def crop_image(self):
        messagebox.showinfo("Crop", "Select area and use Image > Crop to Selection")
        
    def zoom_in(self):
        """Zoom in"""
        self.zoom_level *= 1.2
        self.apply_zoom()

    def zoom_out(self):
        """Zoom out"""
        self.zoom_level /= 1.2
        self.apply_zoom()

    def on_mousewheel(self, event):
        """Zoom cu mouse wheel"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def zoom_actual(self):
        """Resetează zoom la 100%"""
        self.zoom_level = 1.0
        self.apply_zoom()
        
    def apply_zoom(self):
        """Aplică zoom pe toate elementele canvas-ului"""
        # Zoom pe imaginea principală (dacă există)
        if self.image and self.photo:
            new_width = int(self.original_image.width * self.zoom_level)
            new_height = int(self.original_image.height * self.zoom_level)
            
            resized = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(resized)
            
            # Găsește și actualizează imaginea principală pe canvas
            for item in self.canvas.find_all():
                if self.canvas.type(item) == 'image' and item not in self.original_image_data:
                    self.canvas.itemconfig(item, image=self.photo)
                    break
        
        # Zoom pe toate sticker-ele și păstrează-le deasupra
        for item_id, data in self.original_image_data.items():
            original_img = data["original_image"]
            current_x, current_y = self.canvas.coords(item_id)
            
            # Calculează noua dimensiune
            new_width = int(original_img.width * self.zoom_level)
            new_height = int(original_img.height * self.zoom_level)
            
            # Redimensionează
            resized = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            new_photo = ImageTk.PhotoImage(resized)
            
            # Actualizează pe canvas
            self.canvas.itemconfig(item_id, image=new_photo)
            data["photo"] = new_photo
            data["current_size"] = (new_width, new_height)
            
            # IMPORTANT: Aduce sticker-ul în față
            self.canvas.tag_raise(item_id)
        
        # Actualizează handle-urile dacă există un item selectat
        if self.selected_item:
            self.show_selection_handles(self.selected_item)
        
        self.status.config(text=f"Zoom: {int(self.zoom_level * 100)}%")
                
    def toggle_grid(self):
        messagebox.showinfo("Grid", "Grid overlay coming soon!")
        
    def reset_image(self):
        if self.original_image:
            self.image = self.original_image.copy()
            self.save_state()
            self.display_image()
            self.status.config(text="Image reset to original")
        else:
            messagebox.showwarning("Warning", "No image loaded!")
    
    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = None
        self.original_image = None
        self.photo = None
        self.stickers = []
        self.history = []
        self.history_index = -1
        self.status.config(text="Canvas cleared")
        
    def copy_selection(self):
        messagebox.showinfo("Copy", "Copy feature coming soon!")
        
    def paste_selection(self):
        messagebox.showinfo("Paste", "Paste feature coming soon!")
        
    def delete_selected(self):
        selected = self.canvas.find_withtag("selected")
        for item in selected:
            self.canvas.delete(item)
        self.status.config(text="Deleted selected items")
    
    def create_canvas_sticker(self, sticker_type, x, y):
        """Create pre-configured stickers using Canvas drawing"""
        if sticker_type == "smiley":
            face = self.canvas.create_oval(x-30, y-30, x+30, y+30, 
                                          fill="#FFD700", outline="#000000", width=2, tags="sticker")
            eye1 = self.canvas.create_oval(x-15, y-10, x-5, y, 
                                          fill="#000000", tags="sticker")
            eye2 = self.canvas.create_oval(x+5, y-10, x+15, y, 
                                          fill="#000000", tags="sticker")
            smile = self.canvas.create_arc(x-20, y-5, x+20, y+25, 
                                          start=0, extent=-180, style=tk.ARC, 
                                          outline="#000000", width=2, tags="sticker")
            return [face, eye1, eye2, smile]
            
        elif sticker_type == "heart":
            points = [x, y+20, x-30, y-10, x-30, y-20, x-15, y-30, x, y-25,
                     x+15, y-30, x+30, y-20, x+30, y-10]
            heart = self.canvas.create_polygon(points, fill="#FF0000", 
                                              outline="#8B0000", width=2, 
                                              smooth=True, tags="sticker")
            return [heart]
            
        elif sticker_type == "star":
            points = []
            for i in range(10):
                angle = math.pi * 2 * i / 10 - math.pi / 2
                r = 30 if i % 2 == 0 else 15
                points.extend([x + r * math.cos(angle), y + r * math.sin(angle)])
            star = self.canvas.create_polygon(points, fill="#FFD700", 
                                             outline="#FF8C00", width=2, tags="sticker")
            return [star]
            
        elif sticker_type == "arrow":
            points = [x-30, y-15, x+10, y-15, x+10, y-25, x+30, y,
                     x+10, y+25, x+10, y+15, x-30, y+15]
            arrow = self.canvas.create_polygon(points, fill="#00FF00", 
                                              outline="#006400", width=2, tags="sticker")
            return [arrow]
            
        elif sticker_type == "cloud":
            c1 = self.canvas.create_oval(x-35, y-10, x-5, y+20, 
                                        fill="#FFFFFF", outline="#A0A0A0", width=2, tags="sticker")
            c2 = self.canvas.create_oval(x-20, y-20, x+10, y+10, 
                                        fill="#FFFFFF", outline="#A0A0A0", width=2, tags="sticker")
            c3 = self.canvas.create_oval(x-5, y-10, x+25, y+20, 
                                        fill="#FFFFFF", outline="#A0A0A0", width=2, tags="sticker")
            c4 = self.canvas.create_oval(x+10, y-5, x+35, y+20, 
                                        fill="#FFFFFF", outline="#A0A0A0", width=2, tags="sticker")
            return [c1, c2, c3, c4]
            
        elif sticker_type == "sun":
            items = []
            for i in range(8):
                angle = math.pi * 2 * i / 8
                x1 = x + 25 * math.cos(angle)
                y1 = y + 25 * math.sin(angle)
                x2 = x + 40 * math.cos(angle)
                y2 = y + 40 * math.sin(angle)
                ray = self.canvas.create_line(x1, y1, x2, y2, 
                                             fill="#FF6600", width=3, tags="sticker")
                items.append(ray)
            sun = self.canvas.create_oval(x-20, y-20, x+20, y+20, 
                                         fill="#FFA500", outline="#FF6600", width=2, tags="sticker")
            items.append(sun)
            return items
            
        elif sticker_type == "checkmark":
            check = self.canvas.create_line(x-20, y, x-5, y+20, x+25, y-20,
                                           fill="#00AA00", width=5, 
                                           capstyle=tk.ROUND, tags="sticker")
            return [check]
            
        elif sticker_type == "cross":
            line1 = self.canvas.create_line(x-20, y-20, x+20, y+20, 
                                           fill="#FF0000", width=5, 
                                           capstyle=tk.ROUND, tags="sticker")
            line2 = self.canvas.create_line(x-20, y+20, x+20, y-20, 
                                           fill="#FF0000", width=5, 
                                           capstyle=tk.ROUND, tags="sticker")
            return [line1, line2]
            
        elif sticker_type == "speech":
            bubble = self.canvas.create_oval(x-35, y-25, x+35, y+15, 
                                            fill="#FFFFFF", outline="#000000", width=2, tags="sticker")
            tail = self.canvas.create_polygon(x-10, y+15, x-5, y+30, x+5, y+15,
                                             fill="#FFFFFF", outline="#000000", width=2, tags="sticker")
            return [bubble, tail]
            
        elif sticker_type == "music":
            stem = self.canvas.create_line(x+10, y-25, x+10, y+15, 
                                          fill="#000000", width=3, tags="sticker")
            note1 = self.canvas.create_oval(x-5, y+10, x+10, y+25, 
                                           fill="#000000", tags="sticker")
            flag = self.canvas.create_polygon(x+10, y-25, x+25, y-20, x+25, y-10, x+10, y-15,
                                             fill="#000000", tags="sticker")
            return [stem, note1, flag]
        
        elif sticker_type == "lightning":
            points = [x, y-30, x-10, y, x+5, y, x-5, y+30, x+15, y-5, x+5, y-5]
            bolt = self.canvas.create_polygon(points, fill="#FFFF00", 
                                             outline="#FFA500", width=2, tags="sticker")
            return [bolt]
            
        elif sticker_type == "trophy":
            cup = self.canvas.create_polygon(x-20, y-20, x-25, y+10, x+25, y+10, x+20, y-20,
                                            fill="#FFD700", outline="#FFA500", width=2, tags="sticker")
            base = self.canvas.create_rectangle(x-15, y+10, x+15, y+20,
                                               fill="#FFD700", outline="#FFA500", width=2, tags="sticker")
            handle1 = self.canvas.create_arc(x-30, y-15, x-15, y+5, start=90, extent=180,
                                            outline="#FFA500", width=2, style=tk.ARC, tags="sticker")
            handle2 = self.canvas.create_arc(x+15, y-15, x+30, y+5, start=270, extent=180,
                                            outline="#FFA500", width=2, style=tk.ARC, tags="sticker")
            return [cup, base, handle1, handle2]
        
        return []
    
    def show_sticker_library(self):
        dialog = tk.Toplevel(self.rootimged)
        dialog.title("Sticker Library")
        dialog.configure(bg="#c0c0c0")
        dialog.geometry("550x450")
        
        tk.Label(dialog, text="Choose a sticker to add:", bg="#c0c0c0", 
                font=("MS Sans Serif", 10, "bold")).pack(pady=10)
        
        sticker_frame = tk.Frame(dialog, bg="#c0c0c0")
        sticker_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        stickers = [
            ("Smiley Face", "smiley"),
            ("Heart", "heart"),
            ("Star", "star"),
            ("Arrow", "arrow"),
            ("Cloud", "cloud"),
            ("Sun", "sun"),
            ("Checkmark", "checkmark"),
            ("Cross", "cross"),
            ("Speech Bubble", "speech"),
            ("Music Note", "music"),
            ("Lightning", "lightning"),
            ("Trophy", "trophy"),
        ]
        
        btn_style = {"bg": "#c0c0c0", "relief": tk.RAISED, "bd": 2,
                    "font": ("MS Sans Serif", 9), "width": 15, "pady": 5}
        
        row, col = 0, 0
        for name, sticker_type in stickers:
            cmd = lambda t=sticker_type: self.add_canvas_sticker(t, dialog)
            btn = tk.Button(sticker_frame, text=name, command=cmd, **btn_style)
            btn.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        tk.Button(dialog, text="Close", command=dialog.destroy, 
                 bg="#c0c0c0", relief=tk.RAISED, bd=2, 
                 font=("MS Sans Serif", 9)).pack(pady=10)
    
    def add_canvas_sticker(self, sticker_type, dialog=None):
        if dialog:
            dialog.destroy()
        
        canvas_width = self.canvas.winfo_width() or 700
        canvas_height = self.canvas.winfo_height() or 500
        x, y = canvas_width // 2, canvas_height // 2
        
        items = self.create_canvas_sticker(sticker_type, x, y)
        if items:
            group_tag = f"sticker_group_{len(self.stickers)}"
            for item in items:
                self.canvas.addtag_withtag(group_tag, item)
            
            self.stickers.append({"type": "canvas", "items": items, "tag": group_tag})
            self.status.config(text=f"{sticker_type.capitalize()} sticker added - drag to move")
    
    def add_sticker(self):
        filename = filedialog.askopenfilename(
            title="Select Sticker Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if filename:
            try:
                sticker_img = Image.open(filename)
                
                # Convertește la RGBA pentru a suporta transparență
                if sticker_img.mode != 'RGBA':
                    sticker_img = sticker_img.convert('RGBA')
                
                sticker_img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                sticker_photo = ImageTk.PhotoImage(sticker_img)
                
                canvas_width = self.canvas.winfo_width() or 700
                canvas_height = self.canvas.winfo_height() or 500
                x, y = canvas_width // 2, canvas_height // 2
                
                sticker_id = self.canvas.create_image(x, y, image=sticker_photo, tags="sticker")
                
                # Stochează imaginea originală pentru redimensionare
                sticker_data = {
                    "id": sticker_id, 
                    "photo": sticker_photo, 
                    "type": "image",
                    "original_image": sticker_img.copy(),
                    "current_size": (sticker_img.width, sticker_img.height)
                }
                self.stickers.append(sticker_data)
                self.original_image_data[sticker_id] = sticker_data
                
                self.status.config(text="Image sticker added - drag to move, resize, adjust transparency")
                
                # Schimbă automat la Select tool
                self.set_tool("select")
                self.selected_item = sticker_id
                self.show_selection_handles(sticker_id)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add sticker:\n{str(e)}")
    
    def update_sticker_transparency(self, value=None):
        """Update transparency of selected sticker"""
        if not self.selected_item:
            return
        
        transparency = self.transparency_var.get() / 100.0  # 0.0 to 1.0
        
        # Verifică dacă itemul selectat este un sticker de tip imagine
        sticker_data = None
        for sticker in self.stickers:
            if sticker.get("type") == "image" and sticker.get("id") == self.selected_item:
                sticker_data = sticker
                break
        
        if sticker_data:
            # Pentru imagini, modificăm canalul alpha
            original_img = sticker_data["original_image"]
            
            # Convertește la RGBA dacă nu e deja
            if original_img.mode != 'RGBA':
                img_with_alpha = original_img.convert('RGBA')
            else:
                img_with_alpha = original_img.copy()
            
            # Aplică transparența
            alpha = img_with_alpha.split()[3]  # Canal alpha
            alpha = alpha.point(lambda p: int(p * transparency))
            img_with_alpha.putalpha(alpha)
            
            # Redimensionează la dimensiunea curentă
            current_size = sticker_data.get("current_size", (original_img.width, original_img.height))
            img_with_alpha = img_with_alpha.resize(current_size, Image.Resampling.LANCZOS)
            
            # Actualizează pe canvas
            new_photo = ImageTk.PhotoImage(img_with_alpha)
            self.canvas.itemconfig(self.selected_item, image=new_photo)
            sticker_data["photo"] = new_photo
            
            self.status.config(text=f"Transparency: {int(transparency * 100)}%")
        else:
            # Pentru stickere canvas native (smiley, heart, etc.)
            sticker_group = None
            for sticker in self.stickers:
                if sticker.get("type") == "canvas":
                    # Verifică dacă vreunul din items este selectat
                    if self.selected_item in sticker.get("items", []):
                        sticker_group = sticker
                        break
            
            if sticker_group:
                # Pentru stickere canvas, convertim în imagine PNG cu transparență
                items = sticker_group.get("items", [])
                if not items:
                    return
                
                # Obține bbox-ul grupului
                all_coords = []
                for item in items:
                    bbox = self.canvas.bbox(item)
                    if bbox:
                        all_coords.extend([bbox[0], bbox[1], bbox[2], bbox[3]])
                
                if not all_coords:
                    return
                
                min_x = min(all_coords[0::4] + all_coords[2::4])
                min_y = min(all_coords[1::4] + all_coords[3::4])
                max_x = max(all_coords[0::4] + all_coords[2::4])
                max_y = max(all_coords[1::4] + all_coords[3::4])
                
                width = int(max_x - min_x) + 10
                height = int(max_y - min_y) + 10
                
                # Creează o imagine transparentă
                img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)
                
                # Desenează fiecare element cu transparență
                for item in items:
                    item_type = self.canvas.type(item)
                    coords = self.canvas.coords(item)
                    
                    # Ajustează coordonatele relative la imagine
                    adjusted_coords = [(c - min_x + 5) if i % 2 == 0 else (c - min_y + 5) 
                                     for i, c in enumerate(coords)]
                    
                    if item_type == "oval":
                        fill_color = self.canvas.itemcget(item, "fill")
                        outline_color = self.canvas.itemcget(item, "outline")
                        width_val = int(self.canvas.itemcget(item, "width") or 1)
                        
                        if fill_color:
                            rgba = self.hex_to_rgba(fill_color, transparency)
                            draw.ellipse(adjusted_coords, fill=rgba, outline=None)
                        if outline_color and outline_color != '':
                            rgba_outline = self.hex_to_rgba(outline_color, transparency)
                            draw.ellipse(adjusted_coords, outline=rgba_outline, width=width_val)
                    
                    elif item_type == "polygon":
                        fill_color = self.canvas.itemcget(item, "fill")
                        outline_color = self.canvas.itemcget(item, "outline")
                        width_val = int(self.canvas.itemcget(item, "width") or 1)
                        
                        coords_tuples = [(adjusted_coords[i], adjusted_coords[i+1]) 
                                       for i in range(0, len(adjusted_coords), 2)]
                        
                        if fill_color:
                            rgba = self.hex_to_rgba(fill_color, transparency)
                            draw.polygon(coords_tuples, fill=rgba, outline=None)
                        if outline_color and outline_color != '':
                            rgba_outline = self.hex_to_rgba(outline_color, transparency)
                            draw.polygon(coords_tuples, outline=rgba_outline, width=width_val)
                    
                    elif item_type == "line":
                        fill_color = self.canvas.itemcget(item, "fill")
                        width_val = int(self.canvas.itemcget(item, "width") or 1)
                        
                        if fill_color:
                            rgba = self.hex_to_rgba(fill_color, transparency)
                            coords_tuples = [(adjusted_coords[i], adjusted_coords[i+1]) 
                                           for i in range(0, len(adjusted_coords), 2)]
                            if len(coords_tuples) >= 2:
                                for i in range(len(coords_tuples) - 1):
                                    draw.line([coords_tuples[i], coords_tuples[i+1]], 
                                            fill=rgba, width=width_val)
                    
                    elif item_type == "rectangle":
                        fill_color = self.canvas.itemcget(item, "fill")
                        outline_color = self.canvas.itemcget(item, "outline")
                        width_val = int(self.canvas.itemcget(item, "width") or 1)
                        
                        if fill_color:
                            rgba = self.hex_to_rgba(fill_color, transparency)
                            draw.rectangle(adjusted_coords, fill=rgba, outline=None)
                        if outline_color and outline_color != '':
                            rgba_outline = self.hex_to_rgba(outline_color, transparency)
                            draw.rectangle(adjusted_coords, outline=rgba_outline, width=width_val)
                
                # Șterge vechile elemente canvas
                for item in items:
                    self.canvas.delete(item)
                
                # Creează imaginea nouă pe canvas
                photo = ImageTk.PhotoImage(img)
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                new_sticker_id = self.canvas.create_image(center_x, center_y, image=photo, tags="sticker")
                
                # Actualizează datele sticker-ului
                new_data = {
                    "id": new_sticker_id,
                    "photo": photo,
                    "type": "image",
                    "original_image": img.copy(),
                    "current_size": (width, height)
                }
                
                # Înlocuiește vechiul sticker cu noul
                self.stickers.remove(sticker_group)
                self.stickers.append(new_data)
                self.original_image_data[new_sticker_id] = new_data
                
                # Actualizează selecția
                self.selected_item = new_sticker_id
                self.show_selection_handles(new_sticker_id)
                
                self.status.config(text=f"Canvas sticker transparency: {int(transparency * 100)}%")

    def hex_to_rgba(self, hex_color, alpha):
        """Convert hex color to RGBA tuple with alpha"""
        if not hex_color or hex_color == '':
            return (0, 0, 0, 0)
        
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        if len(hex_color) == 6:
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        elif len(hex_color) == 3:
            r, g, b = tuple(int(c*2, 16) for c in hex_color)
        else:
            return (0, 0, 0, int(255 * alpha))
        
        return (r, g, b, int(255 * alpha))
            
    def show_selection_handles(self, item):
        """Show selection handles around selected item"""
        self.clear_selection_handles()
        self.selected_item = item
        
        # Obține bounding box-ul itemului
        bbox = self.canvas.bbox(item)
        if not bbox:
            return
        
        x1, y1, x2, y2 = bbox
        
        # Chenar de selecție
        self.selection_handles.append(
            self.canvas.create_rectangle(x1-2, y1-2, x2+2, y2+2, 
                                        outline="#0000FF", width=2, 
                                        dash=(4, 4), tags="selection")
        )
        
        # Handle-uri pentru colțuri (resize)
        handle_size = 8
        positions = [
            (x1, y1, "nw"),  # top-left
            (x2, y1, "ne"),  # top-right
            (x1, y2, "sw"),  # bottom-left
            (x2, y2, "se"),  # bottom-right
        ]
        
        for x, y, cursor in positions:
            handle = self.canvas.create_rectangle(
                x - handle_size//2, y - handle_size//2,
                x + handle_size//2, y + handle_size//2,
                fill="#FFFFFF", outline="#0000FF", width=2,
                tags="selection_handle"
            )
            self.selection_handles.append(handle)
            self.canvas.tag_bind(handle, "<ButtonPress-1>", 
                                lambda e, h=handle, it=item: self.start_resize(e, h, it))
            self.canvas.tag_bind(handle, "<B1-Motion>", 
                                lambda e, it=item: self.do_resize(e, it))
            self.canvas.tag_bind(handle, "<ButtonRelease-1>", 
                                lambda e, it=item: self.finish_resize(e, it))
        
        # Verifică dacă e un sticker de tip imagine și arată controalele de transparență
        is_image_sticker = False
        for sticker in self.stickers:
            if sticker.get("type") == "image" and sticker.get("id") == item:
                is_image_sticker = True
                break
        
        if is_image_sticker:
            self.show_transparency_controls()
        else:
            self.hide_transparency_controls()

    def clear_selection_handles(self):
        """Clear selection handles"""
        for handle in self.selection_handles:
            self.canvas.delete(handle)
        self.selection_handles = []
        self.selected_item = None
        
        # Ascunde controalele de transparență când nu e nimic selectat
        self.hide_transparency_controls()

    def start_resize(self, event, handle, item):
        """Start resizing operation"""
        self.resize_handle = handle
        self.drag_data["resizing"] = True
        self.drag_data["item"] = item
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
        # Salvează dimensiunea inițială
        if item in self.original_image_data:
            data = self.original_image_data[item]
            self.drag_data["original_size"] = data["current_size"]
            self.drag_data["original_pos"] = self.canvas.coords(item)

    def do_resize(self, event, item):
        """Desenează dreptunghi de previzualizare în timpul resize-ului"""
        if not self.drag_data or self.drag_data.get("item") != item:
            return
        
        data = self.original_image_data.get(item)
        if not data:
            return
        
        original_img = data["original_image"]
        img_x, img_y = self.canvas.coords(item)
        
        # Calculează handle-ul cel mai apropiat
        corners = self.calculate_corners(img_x, img_y, data["current_size"])
        min_dist = float('inf')
        handle_pos = 'se'
        
        for corner_name, (cx, cy) in corners.items():
            dist = math.sqrt((self.drag_data["x"] - cx)**2 + (self.drag_data["y"] - cy)**2)
            if dist < min_dist:
                min_dist = dist
                handle_pos = corner_name
        
        # Calculează noua dimensiune
        if handle_pos == 'se':
            new_width = abs(event.x - (img_x - data["current_size"][0]//2))
        elif handle_pos == 'sw':
            new_width = abs((img_x + data["current_size"][0]//2) - event.x)
        elif handle_pos == 'ne':
            new_width = abs(event.x - (img_x - data["current_size"][0]//2))
        else:  # 'nw'
            new_width = abs((img_x + data["current_size"][0]//2) - event.x)
        
        new_width = int(max(20, min(new_width, 2000)))
        
        # Păstrează aspect ratio
        orig_width, orig_height = original_img.width, original_img.height
        aspect_ratio = orig_width / orig_height
        new_height = int(new_width / aspect_ratio)
        
        # Șterge dreptunghiul vechi de previzualizare
        if hasattr(self, 'resize_preview_rect') and self.resize_preview_rect:
            self.canvas.delete(self.resize_preview_rect)
        
        # Desenează dreptunghi nou de previzualizare
        x1 = img_x - new_width // 2
        y1 = img_y - new_height // 2
        x2 = img_x + new_width // 2
        y2 = img_y + new_height // 2
        
        self.resize_preview_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='blue',
            dash=(5, 5),
            width=2
        )
    
    def finish_resize(self, event, item):
        """Aplică resize-ul efectiv când dai drumul la mouse"""
        if not self.drag_data or self.drag_data.get("item") != item:
            return
        
        # Șterge dreptunghiul de previzualizare
        if hasattr(self, 'resize_preview_rect') and self.resize_preview_rect:
            self.canvas.delete(self.resize_preview_rect)
            self.resize_preview_rect = None
        
        data = self.original_image_data.get(item)
        if not data:
            return
        
        original_img = data["original_image"]
        img_x, img_y = self.canvas.coords(item)
        
        # Calculează handle-ul și dimensiunea (același cod ca în do_resize)
        corners = self.calculate_corners(img_x, img_y, data["current_size"])
        min_dist = float('inf')
        handle_pos = 'se'
        
        for corner_name, (cx, cy) in corners.items():
            dist = math.sqrt((self.drag_data["x"] - cx)**2 + (self.drag_data["y"] - cy)**2)
            if dist < min_dist:
                min_dist = dist
                handle_pos = corner_name
        
        if handle_pos == 'se':
            new_width = abs(event.x - (img_x - data["current_size"][0]//2))
        elif handle_pos == 'sw':
            new_width = abs((img_x + data["current_size"][0]//2) - event.x)
        elif handle_pos == 'ne':
            new_width = abs(event.x - (img_x - data["current_size"][0]//2))
        else:
            new_width = abs((img_x + data["current_size"][0]//2) - event.x)
        
        new_width = int(max(20, min(new_width, 2000)))
        
        orig_width, orig_height = original_img.width, original_img.height
        aspect_ratio = orig_width / orig_height
        new_height = int(new_width / aspect_ratio)
        
        # ACUM redimensionează imaginea efectiv
        resized_img = original_img.copy()
        resized_img = resized_img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Aplică transparența curentă dacă slider-ul nu e la 100%
        transparency = self.transparency_var.get() / 100.0
        if transparency < 1.0 and resized_img.mode == 'RGBA':
            alpha = resized_img.split()[3]
            alpha = alpha.point(lambda p: int(p * transparency))
            resized_img.putalpha(alpha)

        new_photo = ImageTk.PhotoImage(resized_img)
        
        self.canvas.itemconfig(item, image=new_photo)
        data["photo"] = new_photo
        data["current_size"] = (new_width, new_height)
        
        self.show_selection_handles(item)
    
    def calculate_corners(self, x, y, size):
        """Calculează pozițiile colțurilor pentru resize handles"""
        width, height = size
        half_w = width // 2
        half_h = height // 2
        
        return {
            'nw': (x - half_w, y - half_h),  # top-left
            'ne': (x + half_w, y - half_h),  # top-right
            'sw': (x - half_w, y + half_h),  # bottom-left
            'se': (x + half_w, y + half_h)   # bottom-right
        }
        
    def on_press(self, event):
        # Verifică dacă e un handle de selecție
        if self.current_tool == "select":
            clicked = self.canvas.find_withtag(tk.CURRENT)
            if clicked and "selection_handle" in self.canvas.gettags(clicked[0]):
                return  # Handle-ul va gestiona resize-ul
            
            items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
            for item in items:
                tags = self.canvas.gettags(item)
                if "selection" in tags or "selection_handle" in tags:
                    continue
                    
                if "sticker" in tags or "text" in tags or "shape" in tags or "drawing" in tags:
                    # Arată handle-uri pentru imagini
                    if "sticker" in tags and item in self.original_image_data:
                        self.show_selection_handles(item)
                    else:
                        self.clear_selection_handles()
                    
                    for tag in tags:
                        if tag.startswith("sticker_group_"):
                            self.drag_data["item"] = tag
                            self.drag_data["x"] = event.x
                            self.drag_data["y"] = event.y
                            self.drag_data["resizing"] = False
                            return
                            
                    self.drag_data["item"] = item
                    self.drag_data["x"] = event.x
                    self.drag_data["y"] = event.y
                    self.drag_data["resizing"] = False
                    return
            
            # Click pe canvas gol - șterge selecția
            self.clear_selection_handles()
            
        elif self.current_tool != "text":
            self.drawing = True
            self.start_x = event.x
            self.start_y = event.y
    
    def on_drag(self, event):
        if self.drag_data.get("resizing"):
            return  # Resize-ul e gestionat separat
            
        if self.current_tool == "select" and self.drag_data["item"]:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            
            if isinstance(self.drag_data["item"], str):
                self.canvas.move(self.drag_data["item"], dx, dy)
            else:
                self.canvas.move(self.drag_data["item"], dx, dy)
                
                # Actualizează handle-urile dacă e selectat
                if self.selected_item == self.drag_data["item"]:
                    for handle in self.selection_handles:
                        self.canvas.move(handle, dx, dy)
            
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
        elif self.current_tool == "draw" and self.drawing:
            if self.start_x and self.start_y:
                self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                       fill=self.current_color, width=self.brush_size,
                                       capstyle=tk.ROUND, smooth=True, tags="drawing")
                self.start_x = event.x
                self.start_y = event.y
                
        elif self.current_tool == "eraser" and self.drawing:
            items = self.canvas.find_overlapping(event.x-self.brush_size, event.y-self.brush_size,
                                                event.x+self.brush_size, event.y+self.brush_size)
            for item in items:
                tags = self.canvas.gettags(item)
                if "main_image" not in tags and "selection" not in tags:
                    self.canvas.delete(item)
    
    def on_release(self, event):
        if self.drag_data.get("resizing"):
            self.drag_data["resizing"] = False
            self.resize_handle = None
            return
            
        if self.current_tool == "select":
            self.drag_data["item"] = None
        elif self.current_tool in ["line", "rectangle", "circle"] and self.drawing:
            if self.start_x and self.start_y:
                if self.current_tool == "line":
                    self.canvas.create_line(self.start_x, self.start_y, event.x, event.y,
                                           fill=self.current_color, width=self.brush_size, tags="shape")
                elif self.current_tool == "rectangle":
                    self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y,
                                                 outline=self.current_color, width=self.brush_size, tags="shape")
                elif self.current_tool == "circle":
                    self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y,
                                           outline=self.current_color, width=self.brush_size, tags="shape")
        elif self.current_tool == "text":
            # Salvăm coordonatele
            text_x = event.x
            text_y = event.y
            
            # Dialog complet pentru text
            text_dialog = tk.Toplevel(self.rootimged)
            text_dialog.title("Add Text")
            text_dialog.configure(bg="#c0c0c0")
            text_dialog.geometry("320x280")
            
            tk.Label(text_dialog, text="Text:", bg="#c0c0c0").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            text_var = tk.StringVar()
            text_entry = tk.Entry(text_dialog, textvariable=text_var, width=30)
            text_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
            text_entry.focus()
            
            tk.Label(text_dialog, text="Font Size:", bg="#c0c0c0").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            size_var = tk.IntVar(value=16)
            size_entry = tk.Entry(text_dialog, textvariable=size_var, width=10)
            size_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
            
            tk.Label(text_dialog, text="Font Family:", bg="#c0c0c0").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            
            # Combobox cu fonturi comune
            from tkinter import ttk
            font_var = tk.StringVar(value="Arial")
            font_combo = ttk.Combobox(text_dialog, textvariable=font_var, width=18, state="readonly")
            font_combo['values'] = ("Arial", "Helvetica", "Times New Roman", "Courier", "Comic Sans MS", 
                                    "Verdana", "Georgia", "Impact", "Trebuchet MS", "Calibri")
            font_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
            
            # Checkboxuri pentru stiluri
            bold_var = tk.BooleanVar()
            italic_var = tk.BooleanVar()
            underline_var = tk.BooleanVar()
            
            tk.Checkbutton(text_dialog, text="Bold", variable=bold_var, 
                          bg="#c0c0c0").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
            tk.Checkbutton(text_dialog, text="Italic", variable=italic_var, 
                          bg="#c0c0c0").grid(row=3, column=1, padx=5, pady=2, sticky=tk.W)
            tk.Checkbutton(text_dialog, text="Underline", variable=underline_var, 
                          bg="#c0c0c0").grid(row=3, column=2, padx=5, pady=2, sticky=tk.W)
            
            def apply_text():
                text = text_var.get()
                if text:
                    font_family = font_var.get()
                    font_size = size_var.get()
                    font_style = []
                    if bold_var.get():
                        font_style.append("bold")
                    if italic_var.get():
                        font_style.append("italic")
                    if underline_var.get():
                        font_style.append("underline")
                    
                    if font_style:
                        font_tuple = (font_family, font_size) + tuple(font_style)
                    else:
                        font_tuple = (font_family, font_size)
                    
                    self.canvas.create_text(text_x, text_y, text=text, 
                                           font=font_tuple,
                                           fill=self.current_color, tags="text")
                    text_dialog.destroy()
                    
                    self.set_tool("select")
            
            def on_enter(event):
                apply_text()
            
            text_entry.bind("<Return>", on_enter)
            
            tk.Button(text_dialog, text="OK", command=apply_text,
                     bg="#c0c0c0", relief=tk.RAISED, bd=2, width=10).grid(row=4, column=0, pady=10, padx=5)
            tk.Button(text_dialog, text="Cancel", command=text_dialog.destroy,
                     bg="#c0c0c0", relief=tk.RAISED, bd=2, width=10).grid(row=4, column=1, pady=10, padx=5)
        
        self.drawing = False
        self.start_x = None
        self.start_y = None
    
    def on_double_click(self, event):
        """Handle double click for editing text"""
        if self.current_tool == "select":
            items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
            for item in items:
                if "text" in self.canvas.gettags(item):
                    self.edit_text(item, event.x, event.y)
                    break

    def edit_text(self, text_item, x, y):
        """Edit existing text item"""
        # Obține textul și fontul curent
        current_text = self.canvas.itemcget(text_item, "text")
        current_font = self.canvas.itemcget(text_item, "font")
        current_color = self.canvas.itemcget(text_item, "fill")
        coords = self.canvas.coords(text_item)
        
        # Parse font
        try:
            if isinstance(current_font, str):
                font_parts = current_font.split()
                font_family = font_parts[0] if font_parts else "Arial"
                font_size = int(font_parts[1]) if len(font_parts) > 1 else 16
                font_styles = font_parts[2:] if len(font_parts) > 2 else []
            else:
                font_family = current_font[0] if current_font else "Arial"
                font_size = current_font[1] if len(current_font) > 1 else 16
                font_styles = list(current_font[2:]) if len(current_font) > 2 else []
        except:
            font_family = "Arial"
            font_size = 16
            font_styles = []
        
        # Dialog pentru editare
        text_dialog = tk.Toplevel(self.rootimged)
        text_dialog.title("Edit Text")
        text_dialog.configure(bg="#c0c0c0")
        text_dialog.geometry("320x280")
        
        tk.Label(text_dialog, text="Text:", bg="#c0c0c0").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        text_var = tk.StringVar(value=current_text)
        text_entry = tk.Entry(text_dialog, textvariable=text_var, width=30)
        text_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)
        text_entry.focus()
        text_entry.select_range(0, tk.END)
        
        tk.Label(text_dialog, text="Font Size:", bg="#c0c0c0").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        size_var = tk.IntVar(value=font_size)
        size_entry = tk.Entry(text_dialog, textvariable=size_var, width=10)
        size_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        tk.Label(text_dialog, text="Font Family:", bg="#c0c0c0").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        
        font_var = tk.StringVar(value=font_family)
        font_combo = ttk.Combobox(text_dialog, textvariable=font_var, width=18, state="readonly")
        font_combo['values'] = ("Arial", "Helvetica", "Times New Roman", "Courier", "Comic Sans MS", 
                                "Verdana", "Georgia", "Impact", "Trebuchet MS", "Calibri")
        font_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W, columnspan=2)
        
        bold_var = tk.BooleanVar(value="bold" in font_styles)
        italic_var = tk.BooleanVar(value="italic" in font_styles)
        underline_var = tk.BooleanVar(value="underline" in font_styles)
        
        tk.Checkbutton(text_dialog, text="Bold", variable=bold_var, 
                      bg="#c0c0c0").grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        tk.Checkbutton(text_dialog, text="Italic", variable=italic_var, 
                      bg="#c0c0c0").grid(row=3, column=1, padx=5, pady=2, sticky=tk.W)
        tk.Checkbutton(text_dialog, text="Underline", variable=underline_var, 
                      bg="#c0c0c0").grid(row=3, column=2, padx=5, pady=2, sticky=tk.W)
        
        def apply_changes():
            new_text = text_var.get()
            if new_text:
                font_family_new = font_var.get()
                font_size_new = size_var.get()
                font_style = []
                if bold_var.get():
                    font_style.append("bold")
                if italic_var.get():
                    font_style.append("italic")
                if underline_var.get():
                    font_style.append("underline")
                
                if font_style:
                    font_tuple = (font_family_new, font_size_new) + tuple(font_style)
                else:
                    font_tuple = (font_family_new, font_size_new)
                
                self.canvas.itemconfig(text_item, text=new_text, font=font_tuple)
                text_dialog.destroy()
            else:
                # Șterge textul dacă e gol
                self.canvas.delete(text_item)
                text_dialog.destroy()
        
        def on_enter(event):
            apply_changes()
        
        text_entry.bind("<Return>", on_enter)
        
        tk.Button(text_dialog, text="OK", command=apply_changes,
                 bg="#c0c0c0", relief=tk.RAISED, bd=2, width=10).grid(row=4, column=0, pady=10, padx=5)
        tk.Button(text_dialog, text="Delete", command=lambda: (self.canvas.delete(text_item), text_dialog.destroy()),
                 bg="#c0c0c0", relief=tk.RAISED, bd=2, width=10).grid(row=4, column=1, pady=10, padx=5)
        tk.Button(text_dialog, text="Cancel", command=text_dialog.destroy,
                 bg="#c0c0c0", relief=tk.RAISED, bd=2, width=10).grid(row=4, column=2, pady=10, padx=5)
    
    def show_shortcuts(self):
        shortcuts = """Keyboard Shortcuts:
        
Ctrl+N - New Canvas
Ctrl+O - Open Image
Ctrl+S - Save Image
Ctrl+Z - Undo
Ctrl+Y - Redo
Ctrl++ - Zoom In
Ctrl+- - Zoom Out
Ctrl+0 - Actual Size
Ctrl+Wheel - Zoom In/Out
        """
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def show_about(self):
        messagebox.showinfo("About", 
                           "Image Editor\n"
                           "Features:\n"
                           "- Advanced image editing tools\n"
                           "- Multiple effects and filters\n"
                           "- Drawing tools (pen, shapes, text)\n"
                           "- Sticker library with 12+ stickers\n"
                           "- Zoom and pan controls\n"
                           "- Undo/Redo support\n"
                           "- Auto-enhance and adjustments\n"
                           "- Export canvas functionality\n\n")

if __name__ == "__main__":
    rootimged = tk.Tk()
    rootimged.geometry("1200x800")
    app = Win95ImageEditor(rootimged)
    rootimged.mainloop()