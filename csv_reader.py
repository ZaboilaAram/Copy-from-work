import tkinter as tk
from tkinter import filedialog, messagebox
import csv

class Windows95CSVReader:
    def __init__(self, rootCSV):
        self.rootCSV = rootCSV
        self.rootCSV.title("CSV Reader")
        self.rootCSV.geometry("800x600")
        
        # Tema Windows 95
        self.bg_color = "#c0c0c0"
        self.dark_shadow = "#808080"
        self.light_shadow = "#ffffff"
        self.button_bg = "#c0c0c0"
        self.text_color = "#000000"
        
        self.rootCSV.configure(bg=self.bg_color)
        
        # Variabile
        self.csv_data = []
        self.headers = []
        self.column_widths = {}
        self.resizing_col = None
        self.resize_start_x = 0
        self.resize_start_width = 0
        self.cell_labels = {}
        self.header_labels = {}
        
        self.create_widgets()
    
    def create_3d_frame(self, parent, sunken=False):
        """Creează un frame cu efect 3D specific Windows 95"""
        frame = tk.Frame(parent, bg=self.bg_color)
        
        if sunken:
            frame.config(relief=tk.SUNKEN, borderwidth=2)
        else:
            frame.config(relief=tk.RAISED, borderwidth=2)
        
        return frame
    
    def create_widgets(self):
        # Bara de meniu
        menubar = tk.Menu(self.rootCSV, bg=self.bg_color)
        self.rootCSV.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open CSV...", command=self.open_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.rootCSV.quit)
        
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Auto-fit Columns", command=self.autofit_columns)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Frame principal
        main_frame = self.create_3d_frame(self.rootCSV)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar
        toolbar = self.create_3d_frame(main_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        btn_open = tk.Button(
            toolbar,
            text="Open CSV",
            command=self.open_csv,
            bg=self.button_bg,
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=2,
            font=("MS Sans Serif", 8)
        )
        btn_open.pack(side=tk.LEFT, padx=2, pady=2)
        
        btn_autofit = tk.Button(
            toolbar,
            text="Auto-fit",
            command=self.autofit_columns,
            bg=self.button_bg,
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=2,
            font=("MS Sans Serif", 8)
        )
        btn_autofit.pack(side=tk.LEFT, padx=2, pady=2)
        
        btn_clear = tk.Button(
            toolbar,
            text="Clear",
            command=self.clear_data,
            bg=self.button_bg,
            relief=tk.RAISED,
            borderwidth=2,
            padx=10,
            pady=2,
            font=("MS Sans Serif", 8)
        )
        btn_clear.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Frame pentru informații
        info_frame = self.create_3d_frame(main_frame, sunken=True)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.info_label = tk.Label(
            info_frame,
            text="No file loaded | Tip: Drag column edges to resize",
            bg=self.bg_color,
            fg=self.text_color,
            font=("MS Sans Serif", 8),
            anchor=tk.W,
            padx=5,
            pady=3
        )
        self.info_label.pack(fill=tk.X)
        
        # Frame pentru tabel
        table_frame = self.create_3d_frame(main_frame, sunken=True)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame pentru canvas și scrollbars
        canvas_container = tk.Frame(table_frame, bg="#ffffff")
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = tk.Scrollbar(canvas_container, orient="vertical", bg=self.bg_color)
        hsb = tk.Scrollbar(canvas_container, orient="horizontal", bg=self.bg_color)
        
        # Canvas pentru tabel
        self.canvas = tk.Canvas(
            canvas_container,
            bg="#ffffff",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            highlightthickness=0
        )
        
        vsb.config(command=self.canvas.yview)
        hsb.config(command=self.canvas.xview)
        
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame interior pentru tabel
        self.table_frame = tk.Frame(self.canvas, bg="#ffffff")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.table_frame, anchor=tk.NW)
        
        # Bind pentru actualizare scroll region
        self.table_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Status bar
        status_frame = self.create_3d_frame(main_frame, sunken=True)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            bg=self.bg_color,
            fg=self.text_color,
            font=("MS Sans Serif", 8),
            anchor=tk.W,
            padx=5,
            pady=2
        )
        self.status_label.pack(fill=tk.X)
    
    def on_frame_configure(self, event=None):
        """Actualizează scroll region când frame-ul se schimbă"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Ajustează lățimea frame-ului interior când canvas-ul se redimensionează"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def calculate_text_width(self, text, font_family="MS Sans Serif", font_size=8):
        """Calculează lățimea necesară pentru text"""
        temp_label = tk.Label(self.rootCSV, text=text, font=(font_family, font_size))
        temp_label.update_idletasks()
        width = temp_label.winfo_reqwidth()
        temp_label.destroy()
        return width
    
    def get_column_optimal_width(self, col_idx):
        """Calculează lățimea optimă pentru o coloană"""
        max_width = 100
        
        if col_idx < len(self.headers):
            header_width = self.calculate_text_width(self.headers[col_idx], font_size=8) + 40
            max_width = max(max_width, header_width)
        
        for row_data in self.csv_data:
            if col_idx < len(row_data):
                cell_width = self.calculate_text_width(row_data[col_idx], font_size=8) + 40
                max_width = max(max_width, min(cell_width, 400))
        
        return max_width
    
    def autofit_columns(self):
        """Ajustează automat lățimea coloanelor"""
        if not self.headers:
            return
        
        for col_idx in range(len(self.headers)):
            optimal_width = self.get_column_optimal_width(col_idx)
            self.column_widths[col_idx] = optimal_width
            self.update_column_width(col_idx, optimal_width)
        
        self.status_label.config(text="Columns auto-fitted")
    
    def update_column_width(self, col_idx, new_width):
        """Actualizează lățimea unei coloane și aplică wrap text"""
        self.column_widths[col_idx] = new_width
        
        if col_idx in self.header_labels:
            self.header_labels[col_idx].config(width=max(1, new_width // 8))
        
        for row_idx in range(len(self.csv_data)):
            key = (row_idx, col_idx)
            if key in self.cell_labels:
                label = self.cell_labels[key]
                label.config(width=max(1, new_width // 8), wraplength=new_width - 10)
        
        self.table_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_header_press(self, event, col_idx):
        """Detectează dacă se face click pe marginea header-ului pentru resize"""
        widget = event.widget
        x = event.x
        widget_width = widget.winfo_width()
        
        if widget_width - 5 <= x <= widget_width:
            self.resizing_col = col_idx
            self.resize_start_x = event.x_root
            self.resize_start_width = self.column_widths.get(col_idx, 120)
            widget.config(cursor="sb_h_double_arrow")
    
    def on_header_motion(self, event, col_idx):
        """Schimbă cursorul când e pe marginea header-ului"""
        if self.resizing_col is not None:
            return
        
        widget = event.widget
        x = event.x
        widget_width = widget.winfo_width()
        
        if widget_width - 5 <= x <= widget_width:
            widget.config(cursor="sb_h_double_arrow")
        else:
            widget.config(cursor="")
    
    def on_header_drag(self, event):
        """Redimensionează coloana în timp ce se trage"""
        if self.resizing_col is not None:
            delta = event.x_root - self.resize_start_x
            new_width = max(50, self.resize_start_width + delta)
            self.update_column_width(self.resizing_col, new_width)
    
    def on_header_release(self, event):
        """Finalizează redimensionarea"""
        if self.resizing_col is not None:
            self.resizing_col = None
            event.widget.config(cursor="")
    
    def open_csv(self):
        filename = filedialog.askopenfilename(
            title="Open CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.load_csv(filename)
                self.status_label.config(text=f"Loaded: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")
                self.status_label.config(text="Error loading file")
    
    def load_csv(self, filename):
        # Șterge datele anterioare
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        self.cell_labels.clear()
        self.header_labels.clear()
        self.column_widths.clear()
        
        # Citește CSV
        with open(filename, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            self.headers = next(csv_reader)
            self.csv_data = list(csv_reader)
        
        # Calculează lățimi inițiale
        for col_idx in range(len(self.headers)):
            self.column_widths[col_idx] = self.get_column_optimal_width(col_idx)
        
        # Creează header-ele
        for col, header in enumerate(self.headers):
            col_width = self.column_widths.get(col, 120)
            
            header_label = tk.Label(
                self.table_frame,
                text=header,
                bg=self.bg_color,
                fg=self.text_color,
                font=("MS Sans Serif", 8, "bold"),
                relief=tk.RAISED,
                borderwidth=2,
                padx=5,
                pady=3,
                width=col_width // 8,
                anchor=tk.W
            )
            header_label.grid(row=0, column=col, sticky="ew", padx=1, pady=1)
            
            self.header_labels[col] = header_label
            
            header_label.bind("<Button-1>", lambda e, c=col: self.on_header_press(e, c))
            header_label.bind("<B1-Motion>", self.on_header_drag)
            header_label.bind("<ButtonRelease-1>", self.on_header_release)
            header_label.bind("<Motion>", lambda e, c=col: self.on_header_motion(e, c))
        
        # Adaugă datele
        for row_idx, row_data in enumerate(self.csv_data, start=1):
            for col_idx, cell_data in enumerate(row_data):
                bg = "#ffffff" if row_idx % 2 == 1 else "#f0f0f0"
                col_width = self.column_widths.get(col_idx, 120)
                
                cell_label = tk.Label(
                    self.table_frame,
                    text=cell_data,
                    bg=bg,
                    fg=self.text_color,
                    font=("MS Sans Serif", 8),
                    relief=tk.FLAT,
                    borderwidth=1,
                    padx=5,
                    pady=2,
                    width=col_width // 8,
                    wraplength=col_width - 10,
                    anchor=tk.W,
                    justify=tk.LEFT
                )
                cell_label.grid(row=row_idx, column=col_idx, sticky="ew", padx=1, pady=0)
                
                self.cell_labels[(row_idx - 1, col_idx)] = cell_label
        
        # Actualizează info
        self.info_label.config(
            text=f"Rows: {len(self.csv_data)} | Columns: {len(self.headers)} | Tip: Drag column edges to resize"
        )
        
        # Actualizează scroll region
        self.table_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def clear_data(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        self.csv_data = []
        self.headers = []
        self.column_widths.clear()
        self.cell_labels.clear()
        self.header_labels.clear()
        self.info_label.config(text="No file loaded | Tip: Drag column edges to resize")
        self.status_label.config(text="Data cleared")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def show_about(self):
        messagebox.showinfo(
            "About CSV Reader",
            "CSV Reader\n\nVersion 1.1\n\nFeatures:\n- Resizable columns\n- Auto-fit columns\n- Text wrapping\n\n© 2025 Tudor Marmureanu"
        )

if __name__ == "__main__":
    rootCSV = tk.Tk()
    app = Windows95CSVReader(rootCSV)
    rootCSV.mainloop()