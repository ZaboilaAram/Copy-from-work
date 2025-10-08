import os
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

def EXTENSIONS():
    # Verifică și creează Config folder
    config_dir = "Config"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"Created {config_dir} directory")
    
    # Inițializează baza de date pentru extensii
    db_path = os.path.join(config_dir, "extensions.db")
    
    class ExtensionManager:
        def __init__(self, rootextensionsS):
            self.rootextensionsS = rootextensionsS
            self.rootextensionsS.title("Multiapp 95 Professional - Extension Manager")
            self.rootextensionsS.geometry("700x500")
            self.rootextensionsS.configure(bg="#c0c0c0")
            self.rootextensionsS.resizable(False, False)
            
            self.db_path = db_path
            self.init_database()
            self.setup_ui()
            self.load_extensions()
        
        def init_database(self):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS extensions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    author TEXT NOT NULL,
                    description TEXT,
                    enabled INTEGER DEFAULT 1,
                    install_date TEXT,
                    extension_id TEXT UNIQUE NOT NULL
                )
            ''')
            conn.commit()
            
            # Adaugă extensii implicite dacă nu există
            cursor.execute("SELECT COUNT(*) FROM extensions")
            if cursor.fetchone()[0] == 0:
                from datetime import datetime
                default_extensions = [
                    ("AI Chatbot Assistant", "1.0.0", "Muap Team", "AI chatbot assistant", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00055"),
                    ("Application Launcher", "1.0.0", "Muap Team", "Application launcher interface", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00056"),
                    ("Archive Manager", "2.0.0", "Muap Team", "Archive compression and management", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00057"),
                    ("Backup Manager", "1.5.0", "Muap Team", "File backup management", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00058"),
                    ("Bandwidth Monitor", "1.3.0", "Muap Team", "Network bandwidth monitoring", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00059"),
                    ("Calculator", "1.0.0", "Muap Team", "Simple & scientific calculator", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00060"),
                    ("Calendar", "1.2.0", "Muap Team", "Calendar display & event planning", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00061"),
                    ("Clipboard History", "1.0.0", "Muap Team", "Clipboard history", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00062"),
                    ("Contact Manager", "1.4.0", "Muap Team", "Contact management system", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00063"),
                    ("CSV Reader", "1.1.0", "Muap Team", "CSV reader", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00064"),
                    ("DEV Tools", "2.0.0", "Muap Team", "Developer tools and utilities", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00065"),
                    ("Device Checker", "1.0.0", "Muap Team", "Online device checker", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00066"),
                    ("Device Manager", "1.5.0", "Muap Team", "Device manager", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00067"),
                    ("Diagram Beta", "0.9.0", "Muap Team", "Diagram creation and editing (beta version)", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00068"),
                    ("Disk Utility", "1.2.0", "Muap Team", "Disk utility visualizer", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00069"),
                    ("Document to PDF", "1.0.0", "Muap Team", "Document converter to PDF (plain text)", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00070"),
                    ("Enhanced User", "1.0.0", "Muap Team", "Enhanced user functionality (user++)", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00071"),
                    ("Event Viewer", "1.3.0", "Muap Team", "System event monitoring", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00072"),
                    ("Excel Lite", "1.0.0", "Muap Team", "Lightweight spreadsheet editor", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00073"),
                    ("Expense Tracker", "1.2.0", "Muap Team", "Expense tracker with diagrams", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00074"),
                    ("File Comparator", "1.0.0", "Muap Team", "File comparison tool", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00075"),
                    ("File Copy Operations", "1.0.0", "Muap Team", "File copying operations only", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00076"),
                    ("File History", "1.1.0", "Muap Team", "File history management tools", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00077"),
                    ("File Recovery", "2.0.0", "Muap Team", "Advanced file recovery tool", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00078"),
                    ("File Renamer", "1.0.0", "Muap Team", "File renaming utility", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00079"),
                    ("File Encryption", "2.0.0", "Muap Team", "File encryption and security tools", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00080"),
                    ("File Search", "1.3.0", "Muap Team", "Searching files tool", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00081"),
                    ("Hardware Alert", "1.0.0", "Muap Team", "Hardware alert monitoring system", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00082"),
                    ("Hardware Monitor", "1.5.0", "Muap Team", "Hardware monitoring live kit", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00083"),
                    ("Junk Manager", "1.2.0", "Muap Team", "Junk file management and cleanup", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00084"),
                    ("Knowledge Base", "1.0.0", "Muap Team", "Knowledge base management", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00085"),
                    ("Knowledge Base Retro", "1.0.0", "Muap Team", "Retro knowledge base manager", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00086"),
                    ("Mail Express", "1.0.0", "Muap Team", "Professional email client with folder management", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00087"),
                    ("Markdown Viewer", "1.0.0", "Muap Team", "Markdown file viewer and editor", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00088"),
                    ("Mindmap Diagram", "1.1.0", "Muap Team", "Diagram creation and editing", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00089"),
                    ("Multiapp Auto Repair", "1.0.0", "Muap Team", "Multiapp auto repair utility", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00090"),
                    ("Multiapp Manual Repair", "1.0.0", "Muap Team", "Multiapp manual repair utility", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00091"),
                    ("Multifile Editor", "1.2.0", "Muap Team", "Configuration file editing for various formats", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00092"),
                    ("Network Topology", "1.0.0", "Muap Team", "Network topology tool", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00093"),
                    ("Network Traffic", "1.2.0", "Muap Team", "Network traffic monitoring", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00094"),
                    ("Notepad", "1.5.0", "Muap Team", "Advanced text editor", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00095"),
                    ("Office Reader", "1.0.0", "Muap Team", "Office document reader", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00096"),
                    ("Paint", "1.0.0", "Muap Team", "Digital drawing tool", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00097"),
                    ("Password Generator", "1.0.0", "Muap Team", "Password generator utility", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00098"),
                    ("Password Generator V2", "2.0.0", "Muap Team", "Advanced password generator", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00099"),
                    ("Password Manager", "1.5.0", "Muap Team", "Password storage and management", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00100"),
                    ("Pause Manager", "1.0.0", "Muap Team", "Team break manager", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00101"),
                    ("PDF to Excel/CSV", "1.0.0", "Muap Team", "PDF to Excel/CSV document converter", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00102"),
                    ("PDF to Word", "1.0.0", "Muap Team", "PDF to Word document converter", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00103"),
                    ("PDF Tools", "2.0.0", "Muap Team", "Comprehensive PDF manipulation tools", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00104"),
                    ("PDF Viewer", "1.0.0", "Muap Team", "Simple PDF viewer", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00105"),
                    ("Process Viewer", "1.3.0", "Muap Team", "CPU and GPU process monitoring", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00106"),
                    ("Python IDE (PyCharm)", "1.0.0", "Muap Team", "Python integrated development environment", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00107"),
                    ("Python IDE (VSCode)", "1.0.0", "Muap Team", "Python integrated development environment", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00108"),
                    ("Quick File Finder", "1.0.0", "Muap Team", "Quick file finder", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00109"),
                    ("Quiz Maker", "1.0.0", "Muap Team", "Quiz creation and editing tool", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00110"),
                    ("Quiz Test", "1.0.0", "Muap Team", "Quiz testing and evaluation system", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00111"),
                    ("Real-time System Monitor", "1.4.0", "Muap Team", "Real-time system resource monitoring", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00112"),
                    ("Safety Checker", "1.0.0", "Muap Team", "Safety tool for avoiding vulnerabilities on your system", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00113"),
                    ("Screen Recorder", "1.2.0", "Muap Team", "Screen recording application", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00114"),
                    ("Script Agent", "1.0.0", "Muap Team", "Script runner for daily tasks", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00115"),
                    ("SQL Editor", "1.3.0", "Muap Team", "SQLite database editor and query tool", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00116"),
                    ("Task Manager", "2.0.0", "Muap Team", "Advanced task manager", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00117"),
                    ("Terminal", "1.5.0", "Muap Team", "Command line terminal interface", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00118"),
                    ("Text Replace", "1.0.0", "Muap Team", "Text search and replace utility", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00119"),
                    ("Todo Manager", "1.2.0", "Muap Team", "Todo manager", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00120"),
                    ("Total Commander", "2.0.0", "Muap Team", "Total commander file manager", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00121"),
                    ("Whiteboard", "1.0.0", "Muap Team", "Whiteboard & presentation tools", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00122"),
                    ("XML Editor", "1.0.0", "Muap Team", "XML file editor and validator for Config", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00123"),
                    ("ZIP Password Recovery", "1.0.0", "Muap Team", "ZIP password recovery tool", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "0x00124"),
                ]
                
                for ext in default_extensions:
                    cursor.execute('''
                        INSERT INTO extensions (name, version, author, description, enabled, install_date, extension_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', ext)
                conn.commit()
            
            conn.close()
        
        def setup_ui(self):
            # Menu Bar
            menubar = tk.Menu(self.rootextensionsS, bg="#c0c0c0", relief="raised", bd=1)
            self.rootextensionsS.config(menu=menubar)
            
            file_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="Install Extension...", command=self.install_extension, state="disabled")
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.rootextensionsS.destroy)
            
            tools_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
            menubar.add_cascade(label="Tools", menu=tools_menu)
            tools_menu.add_command(label="Refresh List", command=self.load_extensions)
            tools_menu.add_command(label="Check for Updates", command=self.check_updates, state="disabled")
            
            help_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
            menubar.add_cascade(label="Help", menu=help_menu)
            help_menu.add_command(label="About Extension Manager", command=self.show_about)
            
            # Toolbar
            toolbar = tk.Frame(self.rootextensionsS, bg="#c0c0c0", relief="raised", bd=1)
            toolbar.pack(fill="x", padx=2, pady=2)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, "font": ("MS Sans Serif", 8)}
            
            tk.Button(toolbar, text="Install", command=self.install_extension, state="disabled", **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Remove", command=self.remove_extension, state="disabled", **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Enable", command=self.enable_extension, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Disable", command=self.disable_extension, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Properties", command=self.show_properties, **btn_style).pack(side="left", padx=2)
            
            # Main Frame
            main_frame = tk.Frame(self.rootextensionsS, bg="#c0c0c0")
            main_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Label
            tk.Label(main_frame, text="Installed Extensions:", bg="#c0c0c0", 
                    font=("MS Sans Serif", 8, "bold")).pack(anchor="w", pady=(0, 5))
            
            # Treeview Frame
            tree_frame = tk.Frame(main_frame, bg="white", relief="sunken", bd=2)
            tree_frame.pack(fill="both", expand=True)
            
            # Scrollbar
            scrollbar = tk.Scrollbar(tree_frame, bg="#c0c0c0")
            scrollbar.pack(side="right", fill="y")
            
            # Treeview
            columns = ("Name", "Version", "Author", "Status")
            self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                                    yscrollcommand=scrollbar.set, height=15)
            
            # Configure columns
            self.tree.heading("Name", text="Extension Name")
            self.tree.heading("Version", text="Version")
            self.tree.heading("Author", text="Author")
            self.tree.heading("Status", text="Status")
            
            self.tree.column("Name", width=250)
            self.tree.column("Version", width=100)
            self.tree.column("Author", width=150)
            self.tree.column("Status", width=100)
            
            self.tree.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=self.tree.yview)
            
            # Bind double-click
            self.tree.bind("<Double-Button-1>", lambda e: self.show_properties())
            
            # Status Bar
            status_bar = tk.Frame(self.rootextensionsS, bg="#c0c0c0", relief="sunken", bd=1)
            status_bar.pack(fill="x", side="bottom")
            
            self.status_label = tk.Label(status_bar, text="Ready", bg="#c0c0c0", 
                                        anchor="w", font=("MS Sans Serif", 8))
            self.status_label.pack(side="left", padx=5, pady=2)
        
        def load_extensions(self):
            # Clear treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Load from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, version, author, enabled FROM extensions ORDER BY name")
            extensions = cursor.fetchall()
            conn.close()
            
            for ext in extensions:
                ext_id, name, version, author, enabled = ext
                status = "Enabled" if enabled else "Disabled"
                self.tree.insert("", "end", iid=ext_id, values=(name, version, author, status))
            
            count = len(extensions)
            enabled_count = sum(1 for ext in extensions if ext[4])
            self.status_label.config(text=f"{count} extension(s) installed, {enabled_count} enabled")
        
        def install_extension(self):
            messagebox.showinfo("Install Extension", 
                              "Extension installation feature.\n\n"
                              "In a full implementation, this would open a file dialog "
                              "to select .ext95 extension packages.")
        
        def remove_extension(self):
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an extension to remove.")
                return
            
            item_id = selection[0]
            item = self.tree.item(item_id)
            ext_name = item['values'][0]
            
            if messagebox.askyesno("Remove Extension", 
                                   f"Are you sure you want to remove '{ext_name}'?\n\n"
                                   "This action cannot be undone."):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM extensions WHERE id=?", (item_id,))
                conn.commit()
                conn.close()
                
                self.load_extensions()
                messagebox.showinfo("Extension Removed", f"'{ext_name}' has been removed successfully.")
        
        def enable_extension(self):
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an extension to enable.")
                return
            
            item_id = selection[0]
            item = self.tree.item(item_id)
            ext_name = item['values'][0]
            current_status = item['values'][3]
            
            # Verifică dacă extensia este deja activată
            if current_status == "Enabled":
                messagebox.showinfo("Already Enabled", 
                                   f"'{ext_name}' is already enabled.")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE extensions SET enabled=1 WHERE id=?", (item_id,))
            conn.commit()
            conn.close()
            
            self.load_extensions()
            messagebox.showinfo("Extension Enabled", f"'{ext_name}' has been enabled successfully.")
        
        def disable_extension(self):
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an extension to disable.")
                return
            
            item_id = selection[0]
            item = self.tree.item(item_id)
            ext_name = item['values'][0]
            current_status = item['values'][3]
            
            # Verifică dacă extensia este deja dezactivată
            if current_status == "Disabled":
                messagebox.showinfo("Already Disabled", 
                                   f"'{ext_name}' is already disabled.")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE extensions SET enabled=0 WHERE id=?", (item_id,))
            conn.commit()
            conn.close()
            
            self.load_extensions()
            messagebox.showinfo("Extension Disabled", f"'{ext_name}' has been disabled successfully.")
        
        def show_properties(self):
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an extension to view properties.")
                return
            
            item_id = selection[0]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM extensions WHERE id=?", (item_id,))
            ext = cursor.fetchone()
            conn.close()
            
            if not ext:
                return
            
            # Properties window
            prop_window = tk.Toplevel(self.rootextensionsS)
            prop_window.title("Extension Properties")
            prop_window.geometry("450x350")
            prop_window.configure(bg="#c0c0c0")
            prop_window.resizable(False, False)
            
            main_frame = tk.Frame(prop_window, bg="#c0c0c0")
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Extension info
            info = [
                ("Name:", ext[1]),
                ("Version:", ext[2]),
                ("Author:", ext[3]),
                ("Extension ID:", ext[7]),
                ("Install Date:", ext[6]),
                ("Status:", "Enabled" if ext[5] else "Disabled"),
            ]
            
            for label, value in info:
                frame = tk.Frame(main_frame, bg="#c0c0c0")
                frame.pack(fill="x", pady=3)
                
                tk.Label(frame, text=label, bg="#c0c0c0", 
                        font=("MS Sans Serif", 8, "bold"), width=15, anchor="w").pack(side="left")
                tk.Label(frame, text=value, bg="#c0c0c0", 
                        font=("MS Sans Serif", 8), anchor="w").pack(side="left", fill="x", expand=True)
            
            # Description
            tk.Label(main_frame, text="Description:", bg="#c0c0c0", 
                    font=("MS Sans Serif", 8, "bold"), anchor="w").pack(anchor="w", pady=(10, 5))
            
            desc_frame = tk.Frame(main_frame, bg="white", relief="sunken", bd=1)
            desc_frame.pack(fill="both", expand=True)
            
            desc_text = tk.Text(desc_frame, bg="white", font=("MS Sans Serif", 8),
                               wrap="word", height=6)
            desc_text.pack(fill="both", expand=True, padx=2, pady=2)
            desc_text.insert(1.0, ext[4] or "No description available.")
            desc_text.config(state="disabled")
            
            # Close button
            btn_frame = tk.Frame(prop_window, bg="#c0c0c0")
            btn_frame.pack(side="bottom", pady=10)
            
            tk.Button(btn_frame, text="Close", command=prop_window.destroy,
                     bg="#c0c0c0", relief="raised", bd=2, 
                     font=("MS Sans Serif", 8), width=10).pack()
        
        def check_updates(self):
            messagebox.showinfo("Check for Updates", 
                              "No updates available.\n\n"
                              "All extensions are up to date.")
        
        def show_about(self):
            about_text = """Multiapp 95 Professional
Extension Manager

Version 1.0.0

Manage and configure extensions for 
Multiapp 95 Professional suite.

Copyright © 2025 Muap Team
All rights reserved."""
            
            messagebox.showinfo("About Extension Manager", about_text)
    
    # Launch Extension Manager
    rootextensionsS = tk.Tk()
    app = ExtensionManager(rootextensionsS)
    rootextensionsS.mainloop()

if __name__ == "__main__":
    EXTENSIONS()