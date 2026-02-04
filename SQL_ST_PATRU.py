def _on_scroll(self, *args, scrollbar):
    scrollbar.set(*args)
    self.line_numbers.yview_moveto(args[0])

def _sync_scroll(self, *args):
    self.query_text.yview(*args)
    self.line_numbers.yview(*args)

def _update_line_numbers(self):
    line_count = int(self.query_text.index('end-1c').split('.')[0])
    
    self.line_numbers.config(state=tk.NORMAL)
    self.line_numbers.delete('1.0', tk.END)
    lines = self.query_text.get('1.0', tk.END).count('\n')
    for i in range(1, lines + 1):
        self.line_numbers.insert(tk.END, f"{i}\n")
    self.line_numbers.config(state=tk.DISABLED)
    
    # ADAUGĂ ACEASTĂ LINIE - sincronizează scroll-ul după update
    self.line_numbers.yview_moveto(self.query_text.yview()[0])

def _select_tab(self, tab_id):
    if self.active_tab_id and self.active_tab_id in self.query_tabs:
        # Save current content
        self.query_tabs[self.active_tab_id].content = self.query_text.get('1.0', tk.END)
        self.query_tabs[self.active_tab_id].set_active(False)
    
    self.active_tab_id = tab_id
    tab = self.query_tabs[tab_id]
    tab.set_active(True)
    
    # Load content
    self.query_text.delete('1.0', tk.END)
    self.query_text.insert('1.0', tab.content)
    self._apply_syntax_highlighting()
    self._update_line_numbers()
    
    # ADAUGĂ ACESTE LINII - forțează sincronizarea
    self.query_text.update_idletasks()
    self.line_numbers.yview_moveto(self.query_text.yview()[0])
#########################################
import tkinter as tk
from tkinter import messagebox
import calendar
from datetime import datetime
import random
import psutil
import threading
import time
import os
import getpass

dashbppvar = 0

class BitpackDashboard:
    def __init__(self, rootRFS):
        self.rootRFS = rootRFS
        self.rootRFS.title("Bitpack Dashboard")
        self.rootRFS.geometry("640x480")
        self.rootRFS.configure(bg="#008080")
        #self.rootRFS.resizable(False, False)
        
        # Colors
        self.bg_color = "#c0c0c0"
        self.btn_color = "#c0c0c0"
        self.text_color = "#000000"
        self.border_dark = "#808080"
        self.border_light = "#ffffff"
        
        # Calendar state
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        
        # Main container
        self.main_frame = tk.Frame(rootRFS, bg=self.bg_color, relief="raised", bd=2)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title bar
        self.create_title_bar()
        
        # Content area
        self.create_content_area()
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.update_system_info, daemon=True)
        self.monitor_thread.start()
        
        self.rootRFS.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def create_title_bar(self):
        title_frame = tk.Frame(self.main_frame, bg="#000080", height=30)
        title_frame.pack(fill="x", padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Bitpack Dashboard", 
                              bg="#000080", fg="white", 
                              font=("MS Sans Serif", 10, "bold"))
        title_label.pack(side="left", padx=5)
        
    def create_content_area(self):
        content = tk.Frame(self.main_frame, bg=self.bg_color)
        content.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel
        left_panel = tk.Frame(content, bg=self.bg_color, width=300)
        left_panel.pack(side="left", fill="both", padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # Product Key Section
        self.create_product_key_section(left_panel)
        
        # System Info Section
        self.create_system_info_section(left_panel)
        
        # Buttons Section
        self.create_buttons_section(left_panel)
        
        # Right panel
        right_panel = tk.Frame(content, bg=self.bg_color)
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Calendar Section
        self.create_calendar_section(right_panel)
        
        # Status Section
        self.create_status_section(right_panel)
        
    def create_product_key_section(self, parent):
        frame = tk.LabelFrame(parent, text="Product Registration", 
                             bg=self.bg_color, fg=self.text_color,
                             font=("MS Sans Serif", 8, "bold"),
                             relief="groove", bd=2)
        frame.pack(fill="x", pady=5)
        
        tk.Label(frame, text="Product Key:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(anchor="w", padx=5, pady=2)
        
        key_frame = tk.Frame(frame, bg="white", relief="sunken", bd=2)
        key_frame.pack(fill="x", padx=5, pady=2)
        
        product_key = self.generate_product_key()
        tk.Label(key_frame, text=product_key, bg="white", 
                font=("Courier New", 10, "bold"), fg="#000080").pack(pady=5)
        
        tk.Label(frame, text="Licensed to:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(anchor="w", padx=5, pady=2)
        
        user_frame = tk.Frame(frame, bg="white", relief="sunken", bd=2)
        user_frame.pack(fill="x", padx=5, pady=2)
        
        #tk.Label(user_frame, text="Registered User", bg="white", font=("MS Sans Serif", 8)).pack(pady=3)
        try:
            username = getpass.getuser()
        except:
            username = os.getenv('USERNAME', 'Registered User')

        tk.Label(user_frame, text=username, bg="white", 
                font=("MS Sans Serif", 8)).pack(pady=3)
        
    def create_system_info_section(self, parent):
        frame = tk.LabelFrame(parent, text="System Information", 
                             bg=self.bg_color, fg=self.text_color,
                             font=("MS Sans Serif", 8, "bold"),
                             relief="groove", bd=2)
        frame.pack(fill="x", pady=5)
        
        # RAM Section
        ram_frame = tk.Frame(frame, bg=self.bg_color)
        ram_frame.pack(fill="x", padx=5, pady=3)
        
        tk.Label(ram_frame, text="Memory (RAM):", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(anchor="w")
        
        self.ram_label = tk.Label(ram_frame, text="", bg=self.bg_color, 
                                 font=("MS Sans Serif", 8))
        self.ram_label.pack(anchor="w")
        
        self.ram_bar_canvas = tk.Canvas(ram_frame, height=20, bg="white", 
                                        relief="sunken", bd=2, highlightthickness=0)
        self.ram_bar_canvas.pack(fill="x", pady=2)
        
        # Disk Section
        disk_frame = tk.Frame(frame, bg=self.bg_color)
        disk_frame.pack(fill="x", padx=5, pady=3)
        
        tk.Label(disk_frame, text="Disk Space (C:):", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(anchor="w")
        
        self.disk_label = tk.Label(disk_frame, text="", bg=self.bg_color, 
                                  font=("MS Sans Serif", 8))
        self.disk_label.pack(anchor="w")
        
        self.disk_bar_canvas = tk.Canvas(disk_frame, height=20, bg="white", 
                                         relief="sunken", bd=2, highlightthickness=0)
        self.disk_bar_canvas.pack(fill="x", pady=2)
    
    def create_buttons_section(self, parent):
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill="x", pady=10)
        
        buttons = [
            ("Dashboard++", self.dashboardpp),
            #("Help", self.on_help),
            ("Exit", self.on_close)
        ]
        
        for text, command in buttons:
            btn = tk.Button(frame, text=text, command=command,
                          bg=self.btn_color, relief="raised", bd=2,
                          font=("MS Sans Serif", 8),
                          width=15, height=1,
                          activebackground="#e0e0e0")
            btn.pack(pady=2)
    
    def create_calendar_section(self, parent):
        frame = tk.LabelFrame(parent, text="Calendar", 
                             bg=self.bg_color, fg=self.text_color,
                             font=("MS Sans Serif", 8, "bold"),
                             relief="groove", bd=2)
        frame.pack(fill="both", expand=True, pady=5)
        
        # Navigation controls
        nav_frame = tk.Frame(frame, bg=self.bg_color)
        nav_frame.pack(fill="x", padx=5, pady=5)
        
        # Previous month button
        tk.Button(nav_frame, text="<", command=self.prev_month,
                 bg=self.btn_color, relief="raised", bd=2,
                 font=("MS Sans Serif", 8, "bold"), width=3).pack(side="left", padx=2)
        
        # Month/Year display and controls
        center_frame = tk.Frame(nav_frame, bg=self.bg_color)
        center_frame.pack(side="left", expand=True, fill="x")
        
        self.month_year_label = tk.Label(center_frame, text="", 
                                         bg=self.bg_color, 
                                         font=("MS Sans Serif", 10, "bold"))
        self.month_year_label.pack()
        
        # Year/Month selectors
        selector_frame = tk.Frame(center_frame, bg=self.bg_color)
        selector_frame.pack()
        
        tk.Label(selector_frame, text="Year:", bg=self.bg_color, 
                font=("MS Sans Serif", 7)).pack(side="left", padx=2)
        
        self.year_var = tk.StringVar(value=str(self.current_year))
        year_entry = tk.Entry(selector_frame, textvariable=self.year_var, 
                             width=6, font=("MS Sans Serif", 7),
                             relief="sunken", bd=2)
        year_entry.pack(side="left", padx=2)
        year_entry.bind('<Return>', lambda e: self.goto_date())
        
        tk.Label(selector_frame, text="Month:", bg=self.bg_color, 
                font=("MS Sans Serif", 7)).pack(side="left", padx=2)
        
        self.month_var = tk.StringVar(value=str(self.current_month))
        month_entry = tk.Entry(selector_frame, textvariable=self.month_var, 
                              width=4, font=("MS Sans Serif", 7),
                              relief="sunken", bd=2)
        month_entry.pack(side="left", padx=2)
        month_entry.bind('<Return>', lambda e: self.goto_date())
        
        tk.Button(selector_frame, text="Go", command=self.goto_date,
                 bg=self.btn_color, relief="raised", bd=2,
                 font=("MS Sans Serif", 7), width=4).pack(side="left", padx=2)
        
        # Next month button
        tk.Button(nav_frame, text=">", command=self.next_month,
                 bg=self.btn_color, relief="raised", bd=2,
                 font=("MS Sans Serif", 8, "bold"), width=3).pack(side="left", padx=2)
        
        # Calendar grid container
        self.cal_container = tk.Frame(frame, bg=self.bg_color)
        self.cal_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.update_calendar()
    
    def update_calendar(self):
        # Clear existing calendar
        for widget in self.cal_container.winfo_children():
            widget.destroy()
        
        # Update month/year label
        month_name = calendar.month_name[self.current_month]
        self.month_year_label.config(text=f"{month_name} {self.current_year}")
        
        # Update entry fields
        self.year_var.set(str(self.current_year))
        self.month_var.set(str(self.current_month))
        
        # Calendar grid
        cal_frame = tk.Frame(self.cal_container, bg="white", relief="sunken", bd=2)
        cal_frame.pack(fill="both", expand=True)
        
        # Configure grid weights for even distribution
        for i in range(7):
            cal_frame.grid_columnconfigure(i, weight=1, uniform="col")
        
        # Day headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            tk.Label(cal_frame, text=day, bg="#000080", fg="white",
                    font=("MS Sans Serif", 7, "bold")).grid(row=0, column=i, sticky="nsew")
        
        # Calendar days
        now = datetime.now()
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for row_num, week in enumerate(cal, start=1):
            for col_num, day in enumerate(week):
                if day == 0:
                    day_text = ""
                else:
                    day_text = str(day)
                
                bg_color = "white"
                fg_color = "black"
                font_style = ("MS Sans Serif", 8)
                
                # Highlight today's date
                if (day == now.day and 
                    self.current_month == now.month and 
                    self.current_year == now.year):
                    bg_color = "#000080"
                    fg_color = "white"
                    font_style = ("MS Sans Serif", 8, "bold")
                
                tk.Label(cal_frame, text=day_text, bg=bg_color, fg=fg_color,
                        font=font_style, height=2).grid(row=row_num, column=col_num, 
                                                         sticky="nsew", padx=0, pady=0)
    
    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_calendar()
    
    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_calendar()
    
    def goto_date(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            
            #if 1 <= month <= 12 and 1900 <= year <= 2100:
            if 1 <= month <= 12:
                self.current_year = year
                self.current_month = month
                self.update_calendar()
            else:
                messagebox.showerror("Invalid Date", 
                                   #"Please enter a valid month (1-12) and year (1900-2100).")
                                   "Please enter a valid month (1-12).")
        except ValueError:
            messagebox.showerror("Invalid Input", 
                               "Please enter numeric values for year and month.")
    
    def create_status_section(self, parent):
        frame = tk.LabelFrame(parent, text="Status", 
                             bg=self.bg_color, fg=self.text_color,
                             font=("MS Sans Serif", 8, "bold"),
                             relief="groove", bd=2)
        frame.pack(fill="x", pady=5)
        
        status_items = [
            ("Status:", "Ok", "#008000"),
            ("Last Update:", datetime.now().strftime("%m/%d/%Y"), "#000000"),
            ("Configuration:", "Offline", "#FF0000")
        ]
        
        for label, value, color in status_items:
            item_frame = tk.Frame(frame, bg=self.bg_color)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            tk.Label(item_frame, text=label, bg=self.bg_color, 
                    font=("MS Sans Serif", 8), width=15, anchor="w").pack(side="left")
            tk.Label(item_frame, text=value, bg=self.bg_color, 
                    font=("MS Sans Serif", 8, "bold"), fg=color, anchor="w").pack(side="left")
    
    def draw_progress_bar(self, canvas, percentage):
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1:
            width = 200
        if height <= 1:
            height = 20
        
        # Background
        canvas.create_rectangle(0, 0, width, height, fill="white", outline="")
        
        # Progress bar
        bar_width = int((width - 4) * (percentage / 100.0))
        if bar_width > 0:
            # Windows 95 style progress bar with blocks
            block_width = 8
            gap = 2
            x = 2
            while x < bar_width:
                block_end = min(x + block_width, bar_width)
                canvas.create_rectangle(x, 2, block_end, height - 2, 
                                      fill="#000080", outline="")
                x += block_width + gap
    
    def update_system_info(self):
        while self.monitoring:
            try:
                # Get RAM info
                ram = psutil.virtual_memory()
                ram_used_gb = ram.used / (1024**3)
                ram_total_gb = ram.total / (1024**3)
                ram_percent = ram.percent
                
                # Get Disk info
                disk = psutil.disk_usage('/')
                disk_used_gb = disk.used / (1024**3)
                disk_total_gb = disk.total / (1024**3)
                disk_percent = disk.percent
                
                # Update UI in main thread
                self.rootRFS.after(0, self.update_ram_display, ram_used_gb, ram_total_gb, ram_percent)
                self.rootRFS.after(0, self.update_disk_display, disk_used_gb, disk_total_gb, disk_percent)
                
            except Exception as e:
                print(f"Error updating system info: {e}")
            
            time.sleep(2)  # Update every 2 seconds
    
    def update_ram_display(self, used, total, percent):
        if percent >= 95:
            color = "#FF0000"  # Red
            font_style = ("MS Sans Serif", 8, "bold")
        elif percent >= 85:
            color = "#FF8000"  # Orange
            font_style = ("MS Sans Serif", 8, "bold")
        else:
            color = "#000000"  # Black
            font_style = ("MS Sans Serif", 8)
        self.ram_label.config(text=f"{used:.1f} GB / {total:.1f} GB ({percent:.1f}%)", 
                             fg=color, font=font_style)
        self.draw_progress_bar(self.ram_bar_canvas, percent)

    def update_disk_display(self, used, total, percent):
        if percent >= 95:
            color = "#FF0000"  # Red
            font_style = ("MS Sans Serif", 8, "bold")
        elif percent >= 85:
            color = "#FF8000"  # Orange
            font_style = ("MS Sans Serif", 8, "bold")
        else:
            color = "#000000"  # Black
            font_style = ("MS Sans Serif", 8)
        self.disk_label.config(text=f"{used:.1f} GB / {total:.1f} GB ({percent:.1f}%)", 
                             fg=color, font=font_style)
        self.draw_progress_bar(self.disk_bar_canvas, percent)
    
    def generate_product_key(self):
        # parts = []
        # for _ in range(5):
            # part = ''.join([str(random.randint(0, 9)) for _ in range(5)])
            # parts.append(part)
        # return '-'.join(parts)
        return "R46BX-JHR2J-PG7ER-24QFG-MWKVR"
    
    def on_help(self):
        messagebox.showinfo("Help", 
                          "Bitpack Dashboard Help\n\n" +
                          "For assistance, please refer to the user manual.\nFor more informations, click the Dashboard++ button.")
    def dashboardpp(self):
        global dashbppvar
        dashbppvar = 2
        self.monitoring = False
        self.rootRFS.destroy()
    
    def on_close(self):
        global dashbppvar
        dashbppvar = 1
        self.monitoring = False
        self.rootRFS.destroy()

if __name__ == "__main__":
    while dashbppvar == 0:
        rootRFS = tk.Tk()
        app = BitpackDashboard(rootRFS)
        rootRFS.mainloop()
    if dashbppvar == 2:
        print(2) #interfata noua in loc de print(2)
#####################################################################
import tkinter as tk
from tkinter import messagebox
import calendar
from datetime import datetime
import random
import psutil
import threading
import time

class BitpackManagerSetup:
    def __init__(self, rootRFSsetup):
        self.rootRFSsetup = rootRFSsetup
        self.rootRFSsetup.title("Bitpack Manager")
        self.rootRFSsetup.geometry("640x480")
        self.rootRFSsetup.configure(bg="#008080")
        #self.rootRFSsetup.resizable(False, False)
        
        # Colors
        self.bg_color = "#c0c0c0"
        self.btn_color = "#c0c0c0"
        self.text_color = "#000000"
        self.border_dark = "#808080"
        self.border_light = "#ffffff"
        
        # Calendar state
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        
        # Main container
        self.main_frame = tk.Frame(rootRFSsetup, bg=self.bg_color, relief="raised", bd=2)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title bar
        self.create_title_bar()
        
        # Content area
        self.create_content_area()
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.update_system_info, daemon=True)
        self.monitor_thread.start()
        
        self.rootRFSsetup.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def create_title_bar(self):
        title_frame = tk.Frame(self.main_frame, bg="#000080", height=30)
        title_frame.pack(fill="x", padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Bitpack Manager", 
                              bg="#000080", fg="white", 
                              font=("MS Sans Serif", 10, "bold"))
        title_label.pack(side="left", padx=5)
        
    def create_content_area(self):
        content = tk.Frame(self.main_frame, bg=self.bg_color)
        content.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Left panel
        left_panel = tk.Frame(content, bg=self.bg_color, width=300)
        left_panel.pack(side="left", fill="both", padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # Product Key Section
        self.create_product_key_section(left_panel)
        
        # System Info Section
        self.create_system_info_section(left_panel)
        
        # Buttons Section
        self.create_buttons_section(left_panel)
        
        # Right panel
        right_panel = tk.Frame(content, bg=self.bg_color)
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Calendar Section
        self.create_calendar_section(right_panel)
        
        # Status Section
        self.create_status_section(right_panel)
        
    def create_product_key_section(self, parent):
        frame = tk.LabelFrame(parent, text="Product Registration", 
                             bg=self.bg_color, fg=self.text_color,
                             font=("MS Sans Serif", 8, "bold"),
                             relief="groove", bd=2)
        frame.pack(fill="x", pady=5)
        
        tk.Label(frame, text="Product Key:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(anchor="w", padx=5, pady=2)
        
        key_frame = tk.Frame(frame, bg="white", relief="sunken", bd=2)
        key_frame.pack(fill="x", padx=5, pady=2)
        
        product_key = self.generate_product_key()
        tk.Label(key_frame, text=product_key, bg="white", 
                font=("Courier New", 10, "bold"), fg="#000080").pack(pady=5)
        
        tk.Label(frame, text="Licensed to:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(anchor="w", padx=5, pady=2)
        
        user_frame = tk.Frame(frame, bg="white", relief="sunken", bd=2)
        user_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(user_frame, text="Not configured", bg="white", font=("MS Sans Serif", 8)).pack(pady=3)
    def create_system_info_section(self, parent):
        frame = tk.LabelFrame(parent, text="System Information", 
                             bg=self.bg_color, fg=self.text_color,
                             font=("MS Sans Serif", 8, "bold"),
                             relief="groove", bd=2)
        frame.pack(fill="x", pady=5)
        
        # RAM Section
        ram_frame = tk.Frame(frame, bg=self.bg_color)
        ram_frame.pack(fill="x", padx=5, pady=3)
        
        tk.Label(ram_frame, text="Memory (RAM):", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(anchor="w")
        
        self.ram_label = tk.Label(ram_frame, text="", bg=self.bg_color, 
                                 font=("MS Sans Serif", 8))
        self.ram_label.pack(anchor="w")
        
        self.ram_bar_canvas = tk.Canvas(ram_frame, height=20, bg="white", 
                                        relief="sunken", bd=2, highlightthickness=0)
        self.ram_bar_canvas.pack(fill="x", pady=2)
        
        # Disk Section
        disk_frame = tk.Frame(frame, bg=self.bg_color)
        disk_frame.pack(fill="x", padx=5, pady=3)
        
        tk.Label(disk_frame, text="Disk Space (C:):", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(anchor="w")
        
        self.disk_label = tk.Label(disk_frame, text="", bg=self.bg_color, 
                                  font=("MS Sans Serif", 8))
        self.disk_label.pack(anchor="w")
        
        self.disk_bar_canvas = tk.Canvas(disk_frame, height=20, bg="white", 
                                         relief="sunken", bd=2, highlightthickness=0)
        self.disk_bar_canvas.pack(fill="x", pady=2)
    
    def create_buttons_section(self, parent):
        frame = tk.Frame(parent, bg=self.bg_color)
        frame.pack(fill="x", pady=10)
        
        buttons = [
            ("Configure", self.on_install),
            ("Exit", self.on_close)
        ]
        
        for text, command in buttons:
            btn = tk.Button(frame, text=text, command=command,
                          bg=self.btn_color, relief="raised", bd=2,
                          font=("MS Sans Serif", 8),
                          width=15, height=1,
                          activebackground="#e0e0e0")
            btn.pack(pady=2)
    
    def create_calendar_section(self, parent):
        frame = tk.LabelFrame(parent, text="Calendar", 
                             bg=self.bg_color, fg=self.text_color,
                             font=("MS Sans Serif", 8, "bold"),
                             relief="groove", bd=2)
        frame.pack(fill="both", expand=True, pady=5)
        
        # Navigation controls
        nav_frame = tk.Frame(frame, bg=self.bg_color)
        nav_frame.pack(fill="x", padx=5, pady=5)
        
        # Previous month button
        # tk.Button(nav_frame, text="<", command=self.prev_month,
                 # bg=self.btn_color, relief="raised", bd=2,
                 # font=("MS Sans Serif", 8, "bold"), width=3).pack(side="left", padx=2)
        
        # Month/Year display and controls
        center_frame = tk.Frame(nav_frame, bg=self.bg_color)
        center_frame.pack(side="left", expand=True, fill="x")
        
        self.month_year_label = tk.Label(center_frame, text="", 
                                         bg=self.bg_color, 
                                         font=("MS Sans Serif", 10, "bold"))
        self.month_year_label.pack()
        
        # Year/Month selectors
        selector_frame = tk.Frame(center_frame, bg=self.bg_color)
        selector_frame.pack()
        
        # tk.Label(selector_frame, text="Year:", bg=self.bg_color, 
                # font=("MS Sans Serif", 7)).pack(side="left", padx=2)
        
        self.year_var = tk.StringVar(value=str(self.current_year))
        # year_entry = tk.Entry(selector_frame, textvariable=self.year_var, 
                             # width=6, font=("MS Sans Serif", 7),
                             # relief="sunken", bd=2)
        # year_entry.pack(side="left", padx=2)
        # year_entry.bind('<Return>', lambda e: self.goto_date())
        
        # tk.Label(selector_frame, text="Month:", bg=self.bg_color, 
                # font=("MS Sans Serif", 7)).pack(side="left", padx=2)
        
        self.month_var = tk.StringVar(value=str(self.current_month))
        # month_entry = tk.Entry(selector_frame, textvariable=self.month_var, 
                              # width=4, font=("MS Sans Serif", 7),
                              # relief="sunken", bd=2)
        # month_entry.pack(side="left", padx=2)
        # month_entry.bind('<Return>', lambda e: self.goto_date())
        
        # tk.Button(selector_frame, text="Go", command=self.goto_date,
                 # bg=self.btn_color, relief="raised", bd=2,
                 # font=("MS Sans Serif", 7), width=4).pack(side="left", padx=2)
        
        # Next month button
        # tk.Button(nav_frame, text=">", command=self.next_month,
                 # bg=self.btn_color, relief="raised", bd=2,
                 # font=("MS Sans Serif", 8, "bold"), width=3).pack(side="left", padx=2)
        
        # Calendar grid container
        self.cal_container = tk.Frame(frame, bg=self.bg_color)
        self.cal_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.update_calendar()
    
    def update_calendar(self):
        # Clear existing calendar
        for widget in self.cal_container.winfo_children():
            widget.destroy()
        
        # Update month/year label
        month_name = calendar.month_name[self.current_month]
        self.month_year_label.config(text=f"{month_name} {self.current_year}")
        
        # Update entry fields
        self.year_var.set(str(self.current_year))
        self.month_var.set(str(self.current_month))
        
        # Calendar grid
        cal_frame = tk.Frame(self.cal_container, bg="white", relief="sunken", bd=2)
        cal_frame.pack(fill="both", expand=True)
        
        # Configure grid weights for even distribution
        for i in range(7):
            cal_frame.grid_columnconfigure(i, weight=1, uniform="col")
        
        # Day headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            tk.Label(cal_frame, text=day, bg="#000080", fg="white",
                    font=("MS Sans Serif", 7, "bold")).grid(row=0, column=i, sticky="nsew")
        
        # Calendar days
        now = datetime.now()
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        for row_num, week in enumerate(cal, start=1):
            for col_num, day in enumerate(week):
                if day == 0:
                    day_text = ""
                else:
                    day_text = str(day)
                
                bg_color = "white"
                fg_color = "black"
                font_style = ("MS Sans Serif", 8)
                
                # Highlight today's date
                if (day == now.day and 
                    self.current_month == now.month and 
                    self.current_year == now.year):
                    bg_color = "#000080"
                    fg_color = "white"
                    font_style = ("MS Sans Serif", 8, "bold")
                
                tk.Label(cal_frame, text=day_text, bg=bg_color, fg=fg_color,
                        font=font_style, height=2).grid(row=row_num, column=col_num, 
                                                         sticky="nsew", padx=0, pady=0)
    
    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_calendar()
    
    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_calendar()
    
    def goto_date(self):
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            
            #if 1 <= month <= 12 and 1900 <= year <= 2100:
            if 1 <= month <= 12:
                self.current_year = year
                self.current_month = month
                self.update_calendar()
            else:
                messagebox.showerror("Invalid Date", 
                                   #"Please enter a valid month (1-12) and year (1900-2100).")
                                   "Please enter a valid month (1-12).")
        except ValueError:
            messagebox.showerror("Invalid Input", 
                               "Please enter numeric values for year and month.")
    
    def create_status_section(self, parent):
        frame = tk.LabelFrame(parent, text="Status", 
                             bg=self.bg_color, fg=self.text_color,
                             font=("MS Sans Serif", 8, "bold"),
                             relief="groove", bd=2)
        frame.pack(fill="x", pady=5)
        
        status_items = [
            ("Package Status:", "Ready", "#008000"),
            ("Last Update:", datetime.now().strftime("%m/%d/%Y"), "#000000"),
            ("Configuration:", "Offline", "#FF0000")
        ]
        
        for label, value, color in status_items:
            item_frame = tk.Frame(frame, bg=self.bg_color)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            tk.Label(item_frame, text=label, bg=self.bg_color, 
                    font=("MS Sans Serif", 8), width=15, anchor="w").pack(side="left")
            tk.Label(item_frame, text=value, bg=self.bg_color, 
                    font=("MS Sans Serif", 8, "bold"), fg=color, anchor="w").pack(side="left")
    
    def draw_progress_bar(self, canvas, percentage):
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1:
            width = 200
        if height <= 1:
            height = 20
        
        # Background
        canvas.create_rectangle(0, 0, width, height, fill="white", outline="")
        
        # Progress bar
        bar_width = int((width - 4) * (percentage / 100.0))
        if bar_width > 0:
            # Windows 95 style progress bar with blocks
            block_width = 8
            gap = 2
            x = 2
            while x < bar_width:
                block_end = min(x + block_width, bar_width)
                canvas.create_rectangle(x, 2, block_end, height - 2, 
                                      fill="#000080", outline="")
                x += block_width + gap
    
    def update_system_info(self):
        while self.monitoring:
            try:
                # Get RAM info
                ram = psutil.virtual_memory()
                ram_used_gb = ram.used / (1024**3)
                ram_total_gb = ram.total / (1024**3)
                ram_percent = ram.percent
                
                # Get Disk info
                disk = psutil.disk_usage('/')
                disk_used_gb = disk.used / (1024**3)
                disk_total_gb = disk.total / (1024**3)
                disk_percent = disk.percent
                
                # Update UI in main thread
                self.rootRFSsetup.after(0, self.update_ram_display, ram_used_gb, ram_total_gb, ram_percent)
                self.rootRFSsetup.after(0, self.update_disk_display, disk_used_gb, disk_total_gb, disk_percent)
                
            except Exception as e:
                print(f"Error updating system info: {e}")
            
            time.sleep(2)  # Update every 2 seconds
    
    def update_ram_display(self, used, total, percent):
        if percent >= 95:
            color = "#FF0000"  # Red
            font_style = ("MS Sans Serif", 8, "bold")
        elif percent >= 85:
            color = "#FF8000"  # Orange
            font_style = ("MS Sans Serif", 8, "bold")
        else:
            color = "#000000"  # Black
            font_style = ("MS Sans Serif", 8)
        self.ram_label.config(text=f"{used:.1f} GB / {total:.1f} GB ({percent:.1f}%)", 
                             fg=color, font=font_style)
        self.draw_progress_bar(self.ram_bar_canvas, percent)

    def update_disk_display(self, used, total, percent):
        if percent >= 95:
            color = "#FF0000"  # Red
            font_style = ("MS Sans Serif", 8, "bold")
        elif percent >= 85:
            color = "#FF8000"  # Orange
            font_style = ("MS Sans Serif", 8, "bold")
        else:
            color = "#000000"  # Black
            font_style = ("MS Sans Serif", 8)
        self.disk_label.config(text=f"{used:.1f} GB / {total:.1f} GB ({percent:.1f}%)", 
                             fg=color, font=font_style)
        self.draw_progress_bar(self.disk_bar_canvas, percent)
    
    def generate_product_key(self):
        # parts = []
        # for _ in range(5):
            # part = ''.join([str(random.randint(0, 9)) for _ in range(5)])
            # parts.append(part)
        # return '-'.join(parts)
        return "Not configured"
    
    def on_install(self):
        self.monitoring = False
        self.rootRFSsetup.destroy()
        
    def on_close(self):
        self.monitoring = False
        self.rootRFSsetup.destroy()

if __name__ == "__main__":
    rootRFSsetup = tk.Tk()
    app = BitpackManagerSetup(rootRFSsetup)
    rootRFSsetup.mainloop()
