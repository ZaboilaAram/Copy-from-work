import tkinter as tk
from tkinter import Canvas, Frame, Label, Button, Entry
import colorsys

class Win95ColorPicker:
    def __init__(self, rootclpicker):
        self.rootclpicker = rootclpicker
        self.rootclpicker.title("Color Picker")
        self.rootclpicker.geometry("480x360")
        self.rootclpicker.resizable(False, False)
        self.rootclpicker.configure(bg="#c0c0c0")
        
        self.current_color = "#0000ff"
        
        # Title bar style
        title_frame = Frame(rootclpicker, bg="#000080", height=25)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        title_label = Label(title_frame, text="Color Picker", bg="#000080", 
                           fg="white", font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side="left", padx=5)
        
        # Main container
        main_frame = Frame(rootclpicker, bg="#c0c0c0", relief="raised", borderwidth=2)
        main_frame.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Left side - Color palette
        left_frame = Frame(main_frame, bg="#c0c0c0")
        left_frame.pack(side="left", padx=10, pady=10)
        
        palette_label = Label(left_frame, text="Basic colors:", bg="#c0c0c0", 
                             font=("MS Sans Serif", 8))
        palette_label.pack(anchor="w")
        
        self.create_color_palette(left_frame)
        
        # RGB Sliders
        slider_frame = Frame(left_frame, bg="#c0c0c0")
        slider_frame.pack(pady=15)
        
        self.r_var = tk.IntVar(value=0)
        self.g_var = tk.IntVar(value=0)
        self.b_var = tk.IntVar(value=255)
        
        self.create_slider(slider_frame, "Red:", self.r_var, 0)
        self.create_slider(slider_frame, "Green:", self.g_var, 1)
        self.create_slider(slider_frame, "Blue:", self.b_var, 2)
        
        # Right side - Preview and values
        right_frame = Frame(main_frame, bg="#c0c0c0")
        right_frame.pack(side="right", padx=10, pady=10, fill="y")
        
        preview_label = Label(right_frame, text="Color preview:", bg="#c0c0c0",
                             font=("MS Sans Serif", 8))
        preview_label.pack(anchor="w", pady=(0, 5))
        
        preview_container = Frame(right_frame, bg="#808080", relief="sunken", borderwidth=2)
        preview_container.pack()
        
        self.preview = Canvas(preview_container, width=120, height=120, 
                            bg=self.current_color, highlightthickness=0)
        self.preview.pack(padx=2, pady=2)
        
        # Color values frame
        values_frame = Frame(right_frame, bg="#c0c0c0")
        values_frame.pack(pady=10, fill="x")
        
        # Hex value
        hex_frame = Frame(values_frame, bg="#c0c0c0")
        hex_frame.pack(fill="x", pady=2)
        
        hex_label = Label(hex_frame, text="Hex:", bg="#c0c0c0", width=5,
                         font=("MS Sans Serif", 8), anchor="w")
        hex_label.pack(side="left")
        
        self.hex_entry = Entry(hex_frame, width=12, font=("MS Sans Serif", 8),
                              relief="sunken", borderwidth=2)
        self.hex_entry.pack(side="left", padx=2)
        self.hex_entry.insert(0, self.current_color)
        self.hex_entry.bind("<Return>", self.on_hex_change)
        
        # RGB value (display only)
        rgb_frame = Frame(values_frame, bg="#c0c0c0")
        rgb_frame.pack(fill="x", pady=2)
        
        rgb_label = Label(rgb_frame, text="RGB:", bg="#c0c0c0", width=5,
                         font=("MS Sans Serif", 8), anchor="w")
        rgb_label.pack(side="left")
        
        self.rgb_value = Label(rgb_frame, text="0, 0, 255", bg="#ffffff",
                              font=("MS Sans Serif", 8), relief="sunken",
                              borderwidth=2, anchor="w", width=15)
        self.rgb_value.pack(side="left", padx=2, fill="x", expand=True)
        
        # HSL value
        hsl_frame = Frame(values_frame, bg="#c0c0c0")
        hsl_frame.pack(fill="x", pady=2)
        
        hsl_label = Label(hsl_frame, text="HSL:", bg="#c0c0c0", width=5,
                         font=("MS Sans Serif", 8), anchor="w")
        hsl_label.pack(side="left")
        
        self.hsl_value = Label(hsl_frame, text="240°, 100%, 50%", bg="#ffffff",
                              font=("MS Sans Serif", 8), relief="sunken",
                              borderwidth=2, anchor="w", width=15)
        self.hsl_value.pack(side="left", padx=2, fill="x", expand=True)
        
        # HSV value
        hsv_frame = Frame(values_frame, bg="#c0c0c0")
        hsv_frame.pack(fill="x", pady=2)
        
        hsv_label = Label(hsv_frame, text="HSV:", bg="#c0c0c0", width=5,
                         font=("MS Sans Serif", 8), anchor="w")
        hsv_label.pack(side="left")
        
        self.hsv_value = Label(hsv_frame, text="240°, 100%, 100%", bg="#ffffff",
                              font=("MS Sans Serif", 8), relief="sunken",
                              borderwidth=2, anchor="w", width=15)
        self.hsv_value.pack(side="left", padx=2, fill="x", expand=True)
        
        # Buttons
        button_frame = Frame(right_frame, bg="#c0c0c0")
        button_frame.pack(pady=1)
        
        ok_btn = Button(button_frame, text="Exit", width=10, 
                       font=("MS Sans Serif", 8), relief="raised", borderwidth=2,
                       bg="#c0c0c0", activebackground="#c0c0c0",
                       command=self.on_ok)
        ok_btn.pack(pady=1)
        
        # cancel_btn = Button(button_frame, text="Exit", width=10,
                           # font=("MS Sans Serif", 8), relief="raised", borderwidth=2,
                           # bg="#c0c0c0", activebackground="#c0c0c0",
                           # command=rootclpicker.destroy)
        # cancel_btn.pack(pady=10)
        
        # Initialize color values
        self.update_color_values()
        
    def create_color_palette(self, parent):
        palette_frame = Frame(parent, bg="#808080", relief="sunken", borderwidth=2)
        palette_frame.pack(pady=5)
        
        colors = [
            "#000000", "#808080", "#800000", "#ff0000", "#808000", "#ffff00", "#008000", "#00ff00",
            "#008080", "#00ffff", "#000080", "#0000ff", "#800080", "#ff00ff", "#808040", "#ffff80",
            "#004040", "#00ff80", "#004080", "#0080ff", "#400040", "#ff0080", "#400000", "#ff8080",
        ]
        
        grid_frame = Frame(palette_frame, bg="#c0c0c0")
        grid_frame.pack(padx=3, pady=3)
        
        for i, color in enumerate(colors):
            row = i // 8
            col = i % 8
            btn = Canvas(grid_frame, width=20, height=20, bg=color,
                        highlightbackground="#808080", highlightthickness=1)
            btn.grid(row=row, column=col, padx=1, pady=1)
            btn.bind("<Button-1>", lambda e, c=color: self.select_color(c))
    
    def create_slider(self, parent, label_text, variable, row):
        frame = Frame(parent, bg="#c0c0c0")
        frame.pack(fill="x", pady=3)
        
        label = Label(frame, text=label_text, bg="#c0c0c0", width=6,
                     font=("MS Sans Serif", 8), anchor="w")
        label.pack(side="left")
        
        slider = tk.Scale(frame, from_=0, to=255, orient="horizontal",
                         variable=variable, bg="#c0c0c0", length=150,
                         troughcolor="#808080", font=("MS Sans Serif", 7),
                         command=self.on_slider_change, sliderlength=20,
                         relief="raised", borderwidth=2, showvalue=False)
        slider.pack(side="left", padx=5)
        
        value_label = Label(frame, textvariable=variable, bg="#c0c0c0",
                           width=3, font=("MS Sans Serif", 8))
        value_label.pack(side="left")
    
    def rgb_to_hsl(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return int(h * 360), int(s * 100), int(l * 100)
    
    def rgb_to_hsv(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return int(h * 360), int(s * 100), int(v * 100)
    
    def update_color_values(self):
        r = self.r_var.get()
        g = self.g_var.get()
        b = self.b_var.get()
        
        # Update RGB display
        self.rgb_value.config(text=f"{r}, {g}, {b}")
        
        # Update HSL display
        h, s, l = self.rgb_to_hsl(r, g, b)
        self.hsl_value.config(text=f"{h}°, {s}%, {l}%")
        
        # Update HSV display
        h, s, v = self.rgb_to_hsv(r, g, b)
        self.hsv_value.config(text=f"{h}°, {s}%, {v}%")
    
    def on_slider_change(self, *args):
        r = self.r_var.get()
        g = self.g_var.get()
        b = self.b_var.get()
        self.current_color = f"#{r:02x}{g:02x}{b:02x}"
        self.preview.configure(bg=self.current_color)
        self.hex_entry.delete(0, tk.END)
        self.hex_entry.insert(0, self.current_color)
        self.update_color_values()
    
    def select_color(self, color):
        self.current_color = color
        self.preview.configure(bg=color)
        self.hex_entry.delete(0, tk.END)
        self.hex_entry.insert(0, color)
        
        # Update sliders
        rgb = self.hex_to_rgb(color)
        self.r_var.set(rgb[0])
        self.g_var.set(rgb[1])
        self.b_var.set(rgb[2])
        
        self.update_color_values()
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def on_hex_change(self, event):
        try:
            hex_val = self.hex_entry.get()
            if not hex_val.startswith('#'):
                hex_val = '#' + hex_val
            rgb = self.hex_to_rgb(hex_val)
            self.select_color(hex_val)
        except:
            pass
    
    def on_ok(self):
        r = self.r_var.get()
        g = self.g_var.get()
        b = self.b_var.get()
        h_hsl, s_hsl, l = self.rgb_to_hsl(r, g, b)
        h_hsv, s_hsv, v = self.rgb_to_hsv(r, g, b)
        
        # print(f"Selected color:")
        # print(f"  Hex: {self.current_color}")
        # print(f"  RGB: {r}, {g}, {b}")
        # print(f"  HSL: {h_hsl}°, {s_hsl}%, {l}%")
        # print(f"  HSV: {h_hsv}°, {s_hsv}%, {v}%")
        self.rootclpicker.quit()

if __name__ == "__main__":
    rootclpicker = tk.Tk()
    app = Win95ColorPicker(rootclpicker)
    rootclpicker.mainloop()