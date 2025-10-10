import tkinter as tk
from tkinter import messagebox, scrolledtext
import winreg
import sys

class RegistryExplorer:
    def __init__(self, rootregeditt):
        self.rootregeditt = rootregeditt
        self.rootregeditt.title("Registry Explorer")
        self.rootregeditt.geometry("800x600")
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.white = "#ffffff"
        self.black = "#000000"
        self.dark_gray = "#808080"
        self.light_gray = "#dfdfdf"
        self.highlight = "#000080"
        
        self.rootregeditt.configure(bg=self.bg_color)
        
        # Registry rootregeditt keys mapping
        self.rootregeditt_keys = {
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_USERS": winreg.HKEY_USERS,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
        }
        
        self.current_key = None
        self.current_path = ""
        
        self.create_widgets()
        self.populate_rootregeditt_keys()
        
    def create_widgets(self):
        # Menu bar frame
        menu_frame = tk.Frame(self.rootregeditt, bg=self.bg_color, relief=tk.RAISED, bd=2)
        menu_frame.pack(side=tk.TOP, fill=tk.X)
        
        # File menu button
        file_btn = tk.Button(menu_frame, text="File", bg=self.bg_color, 
                            relief=tk.RAISED, bd=1, padx=10, command=self.show_file_menu)
        file_btn.pack(side=tk.LEFT)
        
        # Help menu button
        help_btn = tk.Button(menu_frame, text="Help", bg=self.bg_color,
                            relief=tk.RAISED, bd=1, padx=10, command=self.show_help)
        help_btn.pack(side=tk.LEFT)
        
        # Toolbar frame
        toolbar_frame = tk.Frame(self.rootregeditt, bg=self.bg_color, relief=tk.RAISED, bd=2)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        # Back button
        self.back_btn = tk.Button(toolbar_frame, text="Back", bg=self.bg_color,
                                  relief=tk.RAISED, bd=2, padx=15, state=tk.DISABLED,
                                  command=self.go_back)
        self.back_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Refresh button
        refresh_btn = tk.Button(toolbar_frame, text="Refresh", bg=self.bg_color,
                               relief=tk.RAISED, bd=2, padx=15, command=self.refresh_current)
        refresh_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Address bar frame
        addr_frame = tk.Frame(self.rootregeditt, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        addr_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        addr_label = tk.Label(addr_frame, text="Address:", bg=self.bg_color)
        addr_label.pack(side=tk.LEFT, padx=5)
        
        self.address_var = tk.StringVar()
        self.address_entry = tk.Entry(addr_frame, textvariable=self.address_var,
                                      bg=self.white, relief=tk.SUNKEN, bd=1, state="readonly")
        self.address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        
        # Main container with sunken border
        main_container = tk.Frame(self.rootregeditt, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Paned window effect using frames
        left_frame = tk.Frame(main_container, bg=self.white, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        left_frame.pack_propagate(False)
        
        separator = tk.Frame(main_container, bg=self.dark_gray, width=3)
        separator.pack(side=tk.LEFT, fill=tk.Y)
        
        right_frame = tk.Frame(main_container, bg=self.white)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Tree view (left side)
        tree_label = tk.Label(left_frame, text="Registry Keys", bg=self.light_gray,
                             relief=tk.RAISED, bd=1)
        tree_label.pack(side=tk.TOP, fill=tk.X)
        
        tree_scroll = tk.Scrollbar(left_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree_listbox = tk.Listbox(left_frame, bg=self.white, 
                                       yscrollcommand=tree_scroll.set,
                                       selectmode=tk.SINGLE, relief=tk.SUNKEN, bd=1)
        self.tree_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.tree_listbox.yview)
        
        self.tree_listbox.bind('<<ListboxSelect>>', self.on_tree_select)
        self.tree_listbox.bind('<Double-Button-1>', self.on_tree_double_click)
        
        # Values view (right side) - Table style
        values_label = tk.Label(right_frame, text="Registry Values", bg=self.light_gray,
                               relief=tk.RAISED, bd=1)
        values_label.pack(side=tk.TOP, fill=tk.X)
        
        # Create table container
        table_container = tk.Frame(right_frame, bg=self.white, relief=tk.SUNKEN, bd=1)
        table_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Create canvas for table with scrollbars
        self.table_canvas = tk.Canvas(table_container, bg=self.white, highlightthickness=0)
        v_scrollbar = tk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.table_canvas.yview)
        h_scrollbar = tk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.table_canvas.xview)
        
        self.table_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.table_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create frame inside canvas for table
        self.table_frame = tk.Frame(self.table_canvas, bg=self.white)
        self.canvas_frame = self.table_canvas.create_window((0, 0), window=self.table_frame, anchor=tk.NW)
        
        # Column widths
        self.col_widths = [250, 150, 350]
        
        # Create header row
        self.header_frame = tk.Frame(self.table_frame, bg=self.light_gray, relief=tk.RAISED, bd=1)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        
        headers = ["Name", "Type", "Data"]
        for i, header in enumerate(headers):
            label = tk.Label(self.header_frame, text=header, bg=self.light_gray, 
                           width=self.col_widths[i]//7, anchor=tk.W, 
                           relief=tk.RAISED, bd=1, font=("MS Sans Serif", 8, "bold"))
            label.pack(side=tk.LEFT, fill=tk.Y)
        
        # Frame for data rows
        self.rows_frame = tk.Frame(self.table_frame, bg=self.white)
        self.rows_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Bind canvas resize
        self.table_frame.bind("<Configure>", self.on_table_configure)
        
        # Store row data for double-click access
        self.row_data = []
        
        # Status bar
        status_frame = tk.Frame(self.rootregeditt, bg=self.bg_color, relief=tk.SUNKEN, bd=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(status_frame, text="Ready", bg=self.bg_color, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Store navigation history
        self.history = []
        self.history_index = -1
        
    def on_table_configure(self, event):
        self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
        
    def populate_rootregeditt_keys(self):
        self.tree_listbox.delete(0, tk.END)
        for key_name in self.rootregeditt_keys.keys():
            self.tree_listbox.insert(tk.END, key_name)
        self.status_label.config(text="Ready - Showing rootregeditt keys")
        
    def on_tree_select(self, event):
        selection = self.tree_listbox.curselection()
        if selection:
            index = selection[0]
            selected_text = self.tree_listbox.get(index)
            
    def on_tree_double_click(self, event):
        selection = self.tree_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        selected_text = self.tree_listbox.get(index)
        
        # Check if it's a rootregeditt key
        if selected_text in self.rootregeditt_keys:
            self.open_rootregeditt_key(selected_text)
        else:
            # It's a subkey
            self.open_subkey(selected_text)
            
    def open_rootregeditt_key(self, key_name):
        try:
            self.current_key = self.rootregeditt_keys[key_name]
            self.current_path = key_name
            self.address_var.set(self.current_path)
            
            # Add to history
            self.history.append((None, ""))
            self.history_index += 1
            self.back_btn.config(state=tk.NORMAL)
            
            self.load_subkeys()
            self.load_values()
            self.status_label.config(text=f"Opened: {key_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open key: {str(e)}")
            
    def open_subkey(self, subkey_name):
        if self.current_key is None:
            return
            
        try:
            new_path = self.current_path + "\\" + subkey_name
            
            # Try to open the key
            key_handle = winreg.OpenKey(self.current_key, subkey_name, 0, winreg.KEY_READ)
            
            # Store previous state in history
            self.history = self.history[:self.history_index + 1]
            self.history.append((self.current_key, self.current_path))
            self.history_index += 1
            self.back_btn.config(state=tk.NORMAL)
            
            # Update current state
            self.current_key = key_handle
            self.current_path = new_path
            self.address_var.set(self.current_path)
            
            self.load_subkeys()
            self.load_values()
            self.status_label.config(text=f"Opened: {subkey_name}")
        except WindowsError as e:
            messagebox.showerror("Error", f"Cannot open subkey: {str(e)}")
            
    def load_subkeys(self):
        self.tree_listbox.delete(0, tk.END)
        
        if self.current_key is None:
            return
            
        try:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(self.current_key, i)
                    self.tree_listbox.insert(tk.END, subkey_name)
                    i += 1
                except WindowsError:
                    break
        except Exception as e:
            self.status_label.config(text=f"Error loading subkeys: {str(e)}")
            
    def load_values(self):
        # Clear existing rows
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        
        self.row_data = []
        
        if self.current_key is None:
            return
            
        try:
            i = 0
            while True:
                try:
                    name, data, type_id = winreg.EnumValue(self.current_key, i)
                    
                    # Format value name
                    display_name = name if name else "(Default)"
                    
                    # Get type string
                    type_str = self.get_type_string(type_id)
                    
                    # Format data for display
                    data_str = self.format_value_data(data, type_id)
                    
                    # Store original data
                    self.row_data.append((name, data, type_id))
                    
                    # Create row frame
                    row_frame = tk.Frame(self.rows_frame, bg=self.white, relief=tk.FLAT, bd=1)
                    row_frame.pack(side=tk.TOP, fill=tk.X)
                    
                    # Create cells
                    name_label = tk.Label(row_frame, text=display_name, bg=self.white,
                                        width=self.col_widths[0]//7, anchor=tk.W,
                                        relief=tk.GROOVE, bd=1, padx=2, pady=2)
                    name_label.pack(side=tk.LEFT, fill=tk.Y)
                    
                    type_label = tk.Label(row_frame, text=type_str, bg=self.white,
                                        width=self.col_widths[1]//7, anchor=tk.W,
                                        relief=tk.GROOVE, bd=1, padx=2, pady=2)
                    type_label.pack(side=tk.LEFT, fill=tk.Y)
                    
                    data_label = tk.Label(row_frame, text=data_str, bg=self.white,
                                        width=self.col_widths[2]//7, anchor=tk.W,
                                        relief=tk.GROOVE, bd=1, padx=2, pady=2)
                    data_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                    
                    # Bind double-click to all cells in the row
                    row_index = i
                    for widget in [row_frame, name_label, type_label, data_label]:
                        widget.bind('<Double-Button-1>', lambda e, idx=row_index: self.on_row_double_click(idx))
                        widget.bind('<Enter>', lambda e, w=row_frame: w.configure(bg=self.light_gray))
                        widget.bind('<Leave>', lambda e, w=row_frame: w.configure(bg=self.white))
                    
                    i += 1
                except WindowsError:
                    break
                    
            # Update scroll region
            self.table_frame.update_idletasks()
            self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
            
        except Exception as e:
            self.status_label.config(text=f"Error loading values: {str(e)}")
            
    def get_type_string(self, type_id):
        types = {
            winreg.REG_SZ: "REG_SZ",
            winreg.REG_EXPAND_SZ: "REG_EXPAND_SZ",
            winreg.REG_BINARY: "REG_BINARY",
            winreg.REG_DWORD: "REG_DWORD",
            winreg.REG_DWORD_BIG_ENDIAN: "REG_DWORD_BE",
            winreg.REG_LINK: "REG_LINK",
            winreg.REG_MULTI_SZ: "REG_MULTI_SZ",
            winreg.REG_QWORD: "REG_QWORD",
        }
        return types.get(type_id, f"Unknown({type_id})")
        
    def format_value_data(self, data, type_id):
        try:
            if type_id == winreg.REG_BINARY:
                if isinstance(data, bytes):
                    hex_str = ' '.join(f'{b:02X}' for b in data[:16])
                    if len(data) > 16:
                        hex_str += "..."
                    return hex_str
                return str(data)
            elif type_id == winreg.REG_MULTI_SZ:
                if isinstance(data, list):
                    return " | ".join(str(d) for d in data[:3])
                return str(data)
            elif type_id in (winreg.REG_DWORD, winreg.REG_QWORD):
                return f"0x{data:08X} ({data})"
            else:
                data_str = str(data)
                return data_str[:50] + "..." if len(data_str) > 50 else data_str
        except:
            return str(data)[:50]
            
    def on_row_double_click(self, index):
        if index >= len(self.row_data):
            return
            
        try:
            name, data, type_id = self.row_data[index]
            display_name = name if name else "(Default)"
            type_str = self.get_type_string(type_id)
            
            # Create detail window
            detail_window = tk.Toplevel(self.rootregeditt)
            detail_window.title(f"Registry Value - {display_name}")
            detail_window.geometry("500x400")
            detail_window.configure(bg=self.bg_color)
            
            # Info frame
            info_frame = tk.Frame(detail_window, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
            info_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            
            tk.Label(info_frame, text="Name:", bg=self.bg_color, anchor=tk.W).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            tk.Label(info_frame, text=display_name, bg=self.white, relief=tk.SUNKEN, bd=1, anchor=tk.W).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
            
            tk.Label(info_frame, text="Type:", bg=self.bg_color, anchor=tk.W).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
            tk.Label(info_frame, text=type_str, bg=self.white, relief=tk.SUNKEN, bd=1, anchor=tk.W).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
            
            info_frame.columnconfigure(1, weight=1)
            
            # Data frame
            data_frame = tk.Frame(detail_window, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
            data_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            tk.Label(data_frame, text="Data:", bg=self.bg_color, anchor=tk.W).pack(side=tk.TOP, anchor=tk.W, padx=5, pady=2)
            
            data_text = scrolledtext.ScrolledText(data_frame, bg=self.white, height=15, wrap=tk.WORD)
            data_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Format and insert data
            if type_id == winreg.REG_BINARY:
                if isinstance(data, bytes):
                    hex_lines = []
                    for i in range(0, len(data), 16):
                        hex_part = ' '.join(f'{b:02X}' for b in data[i:i+16])
                        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
                        hex_lines.append(f"{i:08X}  {hex_part:<48}  {ascii_part}")
                    data_text.insert(tk.END, '\n'.join(hex_lines))
            elif type_id == winreg.REG_MULTI_SZ:
                if isinstance(data, list):
                    data_text.insert(tk.END, '\n'.join(str(d) for d in data))
                else:
                    data_text.insert(tk.END, str(data))
            else:
                data_text.insert(tk.END, str(data))
                
            data_text.config(state=tk.DISABLED)
            
            # Button frame
            btn_frame = tk.Frame(detail_window, bg=self.bg_color)
            btn_frame.pack(side=tk.BOTTOM, pady=5)
            
            close_btn = tk.Button(btn_frame, text="Close", bg=self.bg_color,
                                 relief=tk.RAISED, bd=2, padx=20, command=detail_window.destroy)
            close_btn.pack()
            
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read value: {str(e)}")
            
    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            prev_key, prev_path = self.history[self.history_index]
            
            if prev_key is None:
                # Go back to rootregeditt
                self.current_key = None
                self.current_path = ""
                self.address_var.set("")
                self.populate_rootregeditt_keys()
                for widget in self.rows_frame.winfo_children():
                    widget.destroy()
                self.row_data = []
                self.back_btn.config(state=tk.DISABLED)
            else:
                self.current_key = prev_key
                self.current_path = prev_path
                self.address_var.set(self.current_path)
                self.load_subkeys()
                self.load_values()
                
            if self.history_index == 0:
                self.back_btn.config(state=tk.DISABLED)
                
    def refresh_current(self):
        if self.current_key is None:
            self.populate_rootregeditt_keys()
        else:
            self.load_subkeys()
            self.load_values()
        self.status_label.config(text="Refreshed")
        
    def show_file_menu(self):
        menu = tk.Menu(self.rootregeditt, tearoff=0, bg=self.bg_color)
        menu.add_command(label="Exit", command=self.rootregeditt.quit)
        menu.post(self.rootregeditt.winfo_pointerx(), self.rootregeditt.winfo_pointery())
        
    def show_help(self):
        messagebox.showinfo("About Registry Explorer",
                          "Registry Explorer - Read Only Mode\n\n"
                          "This tool allows you to browse the Windows Registry safely.\n"
                          "All operations are READ-ONLY.\n\n"
                          "Double-click on keys to expand them.\n"
                          "Double-click on values to view details.\n\n"
                          )

if __name__ == "__main__":
    rootregeditt = tk.Tk()
    app = RegistryExplorer(rootregeditt)
    rootregeditt.mainloop()