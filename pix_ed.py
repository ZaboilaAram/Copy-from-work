import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import json

class PixelEditor:
    def __init__(self, rootpx95):
        self.rootpx95 = rootpx95
        self.rootpx95.title("Pixel Editor")
        self.rootpx95.configure(bg='#c0c0c0')
        self.rootpx95.geometry("900x700")
        
        # Canvas settings
        self.canvas_width = 32
        self.canvas_height = 32
        self.pixel_size = 15
        self.current_color = '#000000'
        self.pixels = {}
        
        # Tools
        self.current_tool = 'pencil'
        self.is_drawing = False
        
        # Create UI
        self.create_menu()
        self.create_toolbar()
        self.create_main_area()
        
        # Initialize empty canvas
        self.clear_canvas()
        
        # Bind resize event
        self.rootpx95.bind('<Configure>', self.on_window_resize)
        
    def create_menu(self):
        menubar = tk.Menu(self.rootpx95)
        self.rootpx95.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Export PNG", command=self.export_png)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.rootpx95.quit)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear", command=self.clear_canvas)
        edit_menu.add_command(label="Resize Canvas", command=self.resize_canvas)
        
    def create_toolbar(self):
        toolbar = tk.Frame(self.rootpx95, bg='#c0c0c0', relief=tk.RAISED, bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        # Tool buttons
        pencil_btn = tk.Button(toolbar, text="Pencil", width=8, 
                              command=lambda: self.set_tool('pencil'),
                              relief=tk.SUNKEN if self.current_tool == 'pencil' else tk.RAISED)
        pencil_btn.pack(side=tk.LEFT, padx=2)
        
        eraser_btn = tk.Button(toolbar, text="Eraser", width=8,
                              command=lambda: self.set_tool('eraser'))
        eraser_btn.pack(side=tk.LEFT, padx=2)
        
        fill_btn = tk.Button(toolbar, text="Fill", width=8,
                            command=lambda: self.set_tool('fill'))
        fill_btn.pack(side=tk.LEFT, padx=2)
        
        # Color picker
        color_btn = tk.Button(toolbar, text="Pick Color", width=10,
                             command=self.pick_color)
        color_btn.pack(side=tk.LEFT, padx=10)
        
        # Current color display
        self.color_display = tk.Canvas(toolbar, width=30, height=30, 
                                      bg=self.current_color, relief=tk.SUNKEN, bd=2)
        self.color_display.pack(side=tk.LEFT, padx=2)
        
        # Canvas size label
        self.size_label = tk.Label(toolbar, text=f"Size: {self.canvas_width}x{self.canvas_height}", 
                                   bg='#c0c0c0', font=('MS Sans Serif', 8))
        self.size_label.pack(side=tk.RIGHT, padx=10)
        
        self.tool_buttons = {'pencil': pencil_btn, 'eraser': eraser_btn, 'fill': fill_btn}
        
    def create_main_area(self):
        # Main container
        self.main_container = tk.Frame(self.rootpx95, bg='#c0c0c0')
        self.main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side - canvas
        self.canvas_container = tk.Frame(self.main_container, bg='#c0c0c0')
        self.canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_canvas()
        
        # Right side - color palette
        self.create_color_palette()
        
    def create_canvas(self):
        # Clear old canvas if exists
        if hasattr(self, 'canvas_frame'):
            self.canvas_frame.destroy()
        
        self.canvas_frame = tk.Frame(self.canvas_container, bg='#c0c0c0', relief=tk.SUNKEN, bd=2)
        self.canvas_frame.pack(expand=False)
        
        # Calculate canvas display size (max 600x600, but adjust to content)
        display_width = min(self.canvas_width * self.pixel_size, 600)
        display_height = min(self.canvas_height * self.pixel_size, 600)
        
        # Create scrollbars
        h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        
        # Create canvas
        self.canvas = tk.Canvas(self.canvas_frame, 
                               width=display_width,
                               height=display_height,
                               bg='white', highlightthickness=0,
                               xscrollcommand=h_scrollbar.set,
                               yscrollcommand=v_scrollbar.set)
        
        # Pack scrollbars and canvas
        self.canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Configure scrollbars
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        # Set scroll region
        self.canvas.config(scrollregion=(0, 0, 
                                         self.canvas_width * self.pixel_size,
                                         self.canvas_height * self.pixel_size))
        
        # Bind mouse wheel for vertical scrolling
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Button-4>', self._on_mousewheel)
        self.canvas.bind('<Button-5>', self._on_mousewheel)
        
        # Draw grid
        self.draw_grid()
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
    def _on_mousewheel(self, event):
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        
    def draw_grid(self):
        for i in range(self.canvas_width + 1):
            x = i * self.pixel_size
            self.canvas.create_line(x, 0, x, self.canvas_height * self.pixel_size, 
                                   fill='#d0d0d0', tags='grid')
        for i in range(self.canvas_height + 1):
            y = i * self.pixel_size
            self.canvas.create_line(0, y, self.canvas_width * self.pixel_size, y, 
                                   fill='#d0d0d0', tags='grid')
        
    def create_color_palette(self):
        if hasattr(self, 'palette_frame'):
            self.palette_frame.destroy()
            
        self.palette_frame = tk.Frame(self.main_container, bg='#c0c0c0', relief=tk.SUNKEN, bd=2)
        self.palette_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        tk.Label(self.palette_frame, text="Color Palette", bg='#c0c0c0', 
                font=('MS Sans Serif', 8, 'bold')).pack(pady=5)
        
        # Create a container frame for the grid
        grid_frame = tk.Frame(self.palette_frame, bg='#c0c0c0')
        grid_frame.pack(padx=5, pady=5)
        
        colors = [
            '#000000', '#FFFFFF', '#FF0000', '#00FF00', '#0000FF', '#FFFF00',
            '#FF00FF', '#00FFFF', '#800000', '#008000', '#000080', '#808000',
            '#800080', '#008080', '#C0C0C0', '#808080', '#FF8080', '#80FF80',
            '#8080FF', '#FFFF80', '#FF80FF', '#80FFFF', '#FFC080', '#C0FFC0'
        ]
        
        colors_per_row = 4
        for i, color in enumerate(colors):
            row = i // colors_per_row
            col = i % colors_per_row
            
            btn = tk.Canvas(grid_frame, width=25, height=25, bg=color, 
                           relief=tk.RAISED, bd=2, highlightthickness=1)
            btn.grid(row=row, column=col, padx=2, pady=2)
            btn.bind('<Button-1>', lambda e, c=color: self.set_color(c))
    
    def on_window_resize(self, event):
        # This ensures the canvas stays centered when window is resized
        pass
        
    def resize_canvas(self):
        dialog = tk.Toplevel(self.rootpx95)
        dialog.title("Resize Canvas")
        dialog.configure(bg='#c0c0c0')
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.rootpx95)
        dialog.grab_set()
        
        tk.Label(dialog, text="New Canvas Size", bg='#c0c0c0', 
                font=('MS Sans Serif', 8, 'bold')).pack(pady=10)
        
        frame = tk.Frame(dialog, bg='#c0c0c0')
        frame.pack(pady=10)
        
        tk.Label(frame, text="Width:", bg='#c0c0c0').grid(row=0, column=0, padx=5, pady=5)
        width_entry = tk.Entry(frame, width=10)
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        width_entry.insert(0, str(self.canvas_width))
        
        tk.Label(frame, text="Height:", bg='#c0c0c0').grid(row=1, column=0, padx=5, pady=5)
        height_entry = tk.Entry(frame, width=10)
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        height_entry.insert(0, str(self.canvas_height))
        
        def apply_resize():
            try:
                new_width = int(width_entry.get())
                new_height = int(height_entry.get())
                
                if new_width < 1 or new_height < 1 or new_width > 128 or new_height > 128:
                    messagebox.showerror("Error", "Size must be between 1 and 128")
                    return
                
                # Save current pixels
                old_pixels = {}
                for (x, y), rect in self.pixels.items():
                    color = self.canvas.itemcget(rect, 'fill')
                    old_pixels[(x, y)] = color
                
                # Update dimensions
                self.canvas_width = new_width
                self.canvas_height = new_height
                self.pixels.clear()
                
                # Recreate canvas
                self.create_canvas()
                
                # Restore pixels that fit
                for (x, y), color in old_pixels.items():
                    if x < new_width and y < new_height:
                        self.draw_pixel(x, y, color)
                
                # Update size label
                self.size_label.config(text=f"Size: {self.canvas_width}x{self.canvas_height}")
                
                # ADAUGĂ ACEASTĂ LINIE - actualizează scroll region
                self.canvas.config(scrollregion=(0, 0, 
                                                 self.canvas_width * self.pixel_size,
                                                 self.canvas_height * self.pixel_size))
                
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        
        btn_frame = tk.Frame(dialog, bg='#c0c0c0')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="OK", width=8, command=apply_resize).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", width=8, command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
    def set_tool(self, tool):
        self.current_tool = tool
        for t, btn in self.tool_buttons.items():
            btn.config(relief=tk.SUNKEN if t == tool else tk.RAISED)
    
    def set_color(self, color):
        self.current_color = color
        self.color_display.config(bg=color)
        
    def pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.current_color)[1]
        if color:
            self.set_color(color)
    
    def get_pixel_coords(self, event):
        # Ajustează coordonatele pentru scroll
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        x = int(canvas_x) // self.pixel_size
        y = int(canvas_y) // self.pixel_size
        
        if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
            return (x, y)
        return None
    
    def draw_pixel(self, x, y, color):
        x1 = x * self.pixel_size + 1
        y1 = y * self.pixel_size + 1
        x2 = (x + 1) * self.pixel_size - 1
        y2 = (y + 1) * self.pixel_size - 1
        
        if (x, y) in self.pixels:
            self.canvas.delete(self.pixels[(x, y)])
        
        if color != 'white':
            rect = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                               fill=color, outline='')
            self.pixels[(x, y)] = rect
        elif (x, y) in self.pixels:
            del self.pixels[(x, y)]
    
    def flood_fill(self, x, y, target_color, replacement_color):
        if target_color == replacement_color:
            return
        
        stack = [(x, y)]
        visited = set()
        
        while stack:
            cx, cy = stack.pop()
            
            if (cx, cy) in visited:
                continue
            if cx < 0 or cx >= self.canvas_width or cy < 0 or cy >= self.canvas_height:
                continue
                
            current = self.pixels.get((cx, cy))
            if current:
                current_color = self.canvas.itemcget(current, 'fill')
            else:
                current_color = 'white'
            
            if current_color != target_color:
                continue
            
            visited.add((cx, cy))
            self.draw_pixel(cx, cy, replacement_color)
            
            stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
    
    def on_mouse_down(self, event):
        coords = self.get_pixel_coords(event)
        if coords:
            x, y = coords
            self.is_drawing = True
            
            if self.current_tool == 'pencil':
                self.draw_pixel(x, y, self.current_color)
            elif self.current_tool == 'eraser':
                self.draw_pixel(x, y, 'white')
            elif self.current_tool == 'fill':
                current = self.pixels.get((x, y))
                if current:
                    target_color = self.canvas.itemcget(current, 'fill')
                else:
                    target_color = 'white'
                self.flood_fill(x, y, target_color, self.current_color)
    
    def on_mouse_drag(self, event):
        if self.is_drawing and self.current_tool in ['pencil', 'eraser']:
            coords = self.get_pixel_coords(event)
            if coords:
                x, y = coords
                color = self.current_color if self.current_tool == 'pencil' else 'white'
                self.draw_pixel(x, y, color)
    
    def on_mouse_up(self, event):
        self.is_drawing = False
    
    def clear_canvas(self):
        for pixel in list(self.pixels.values()):
            self.canvas.delete(pixel)
        self.pixels.clear()
    
    def new_file(self):
        if messagebox.askyesno("New File", "Clear current canvas?"):
            self.clear_canvas()
    
    def save_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".px95",
            filetypes=[("Pixel Art Files", "*.px95"), ("All Files", "*.*")]
        )
        if filename:
            data = {
                'width': self.canvas_width,
                'height': self.canvas_height,
                'pixels': {}
            }
            for (x, y), rect in self.pixels.items():
                color = self.canvas.itemcget(rect, 'fill')
                data['pixels'][f"{x},{y}"] = color
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
    
    def open_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Pixel Art Files", "*.px95"), ("All Files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Update canvas dimensions
                self.canvas_width = data.get('width', 32)
                self.canvas_height = data.get('height', 32)
                self.pixels.clear()
                
                # Recreate canvas
                self.create_canvas()
                
                # Load pixels
                pixels_data = data.get('pixels', {})
                for coords_str, color in pixels_data.items():
                    x, y = map(int, coords_str.split(','))
                    self.draw_pixel(x, y, color)
                
                # Update size label
                self.size_label.config(text=f"Size: {self.canvas_width}x{self.canvas_height}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def export_png(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        if filename:
            img = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
            pixels_data = img.load()
            
            for (x, y), rect in self.pixels.items():
                color = self.canvas.itemcget(rect, 'fill')
                rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                pixels_data[x, y] = rgb
            
            img.save(filename)
            messagebox.showinfo("Export", "Image exported successfully")

if __name__ == "__main__":
    rootpx95 = tk.Tk()
    app = PixelEditor(rootpx95)
    rootpx95.mainloop()