import tkinter as tk
from tkinter import messagebox
import os

class PathsEditor:
    def __init__(self, rootpthsed):
        self.rootpthsed = rootpthsed
        self.rootpthsed.title("Paths Editor")
        self.rootpthsed.geometry("600x500")
        self.rootpthsed.configure(bg='#c0c0c0')
        self.rootpthsed.resizable(False, False)
        
        self.filename = "paths.txt"
        self.paths = []
        
        # Check and load file
        self.check_and_load_file()
        
        # Create UI
        self.create_widgets()
        
    def check_and_load_file(self):
        if not os.path.exists(self.filename):
            try:
                with open(self.filename, 'w') as f:
                    pass
                messagebox.showinfo("Info", f"File {self.filename} created successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {str(e)}")
        else:
            self.load_file()
    
    def load_file(self):
        try:
            with open(self.filename, 'r') as f:
                content = f.read()
                self.parse_file(content)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {str(e)}")
    
    def parse_file(self, content):
        self.paths = []
        lines = content.strip().split('\n')
        for line in lines:
            if line.strip():
                # Check if it's a network path (contains : separator)
                if line.count(':') >= 2:  # Network path has : in both separator and path
                    colon_index = line.index(':')
                    name = line[:colon_index].strip()
                    path = line[colon_index + 1:].strip()
                    self.paths.append({'name': name, 'path': path})
                elif ' ' in line:  # Local path with space separator
                    space_index = line.index(' ')
                    name = line[:space_index].strip()
                    path = line[space_index + 1:].strip()
                    self.paths.append({'name': name, 'path': path})
    
    def validate_path(self, path):
        # Network path
        if path.startswith('\\\\'):
            return True, ""
        
        # Local path
        if len(path) >= 3 and path[1] == ':' and path[2] == '\\' and path[0].isupper():
            if ' ' in path:
                return False, "Local paths cannot contain spaces"
            return True, ""
        
        return False, "Invalid path format. Use \\\\server\\share for network or C:\\folder for local"
    
    def add_path(self):
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Name cannot be empty")
            return
        
        if not path:
            messagebox.showerror("Error", "Path cannot be empty")
            return
        
        valid, error_msg = self.validate_path(path)
        if not valid:
            messagebox.showerror("Error", error_msg)
            return
        
        # Add to list
        self.paths.append({'name': name, 'path': path})
        
        # Save to file
        self.save_file()
        
        # Clear entries
        self.name_entry.delete(0, tk.END)
        self.path_entry.delete(0, tk.END)
        
        # Refresh list
        self.refresh_listbox()
        
        messagebox.showinfo("Success", "Path added successfully")
    
    def save_file(self):
        try:
            with open(self.filename, 'w') as f:
                for item in self.paths:
                    # Network path uses : separator, local path uses space
                    if item['path'].startswith('\\\\'):
                        f.write(f"{item['name']}: {item['path']}\n")
                    else:
                        f.write(f"{item['name']} {item['path']}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def delete_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        index = selection[0]
        del self.paths[index]
        self.save_file()
        self.refresh_listbox()
        messagebox.showinfo("Success", "Path deleted successfully")
    
    def edit_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        index = selection[0]
        item = self.paths[index]
        
        # Populate entries with selected values
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, item['name'])
        
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, item['path'])
        
        # Delete the old entry
        del self.paths[index]
        self.save_file()
        self.refresh_listbox()
    
    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for item in self.paths:
            # Display with appropriate separator
            if item['path'].startswith('\\\\'):
                self.listbox.insert(tk.END, f"{item['name']}: {item['path']}")
            else:
                self.listbox.insert(tk.END, f"{item['name']} {item['path']}")
    
    def create_widgets(self):
        # Title frame
        title_frame = tk.Frame(self.rootpthsed, bg='#000080', height=25)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="Paths Configuration", 
                              bg='#000080', fg='white', 
                              font=('MS Sans Serif', 9, 'bold'))
        title_label.pack(pady=3)
        
        # Main frame
        main_frame = tk.Frame(self.rootpthsed, bg='#c0c0c0', relief=tk.RIDGE, bd=3)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = tk.Frame(main_frame, bg='#c0c0c0')
        input_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Name
        name_label = tk.Label(input_frame, text="Name:", bg='#c0c0c0', 
                             font=('MS Sans Serif', 8))
        name_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = tk.Entry(input_frame, width=50, font=('MS Sans Serif', 8), bd=3)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Path
        path_label = tk.Label(input_frame, text="Path:", bg='#c0c0c0', 
                             font=('MS Sans Serif', 8))
        path_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.path_entry = tk.Entry(input_frame, width=50, font=('MS Sans Serif', 8), bd=3)
        self.path_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg='#c0c0c0')
        button_frame.pack(pady=5)
        
        add_button = tk.Button(button_frame, text="Add Path", command=self.add_path,
                              width=12, font=('MS Sans Serif', 8), relief=tk.RAISED, bd=5)
        add_button.grid(row=0, column=0, padx=5)
        
        edit_button = tk.Button(button_frame, text="Edit Selected", 
                               command=self.edit_selected,
                               width=12, font=('MS Sans Serif', 8), relief=tk.RAISED, bd=5)
        edit_button.grid(row=0, column=1, padx=5)
        
        delete_button = tk.Button(button_frame, text="Delete Selected", 
                                 command=self.delete_selected,
                                 width=12, font=('MS Sans Serif', 8), relief=tk.RAISED, bd=5)
        delete_button.grid(row=0, column=2, padx=5)
        
        # List section
        list_frame = tk.Frame(main_frame, bg='#c0c0c0', relief=tk.SUNKEN, bd=3)
        list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        list_label = tk.Label(list_frame, text="Current Paths:", bg='#c0c0c0',
                             font=('MS Sans Serif', 8, 'bold'))
        list_label.pack(anchor=tk.W, padx=5, pady=5)
        
        # Scrollbar and Listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                 font=('Courier New', 9), bg='white',
                                 selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.listbox.yview)
        
        # Populate listbox
        self.refresh_listbox()
        
        # Info label
        info_label = tk.Label(main_frame, 
                            text="Network: name: \\\\server\\share | Local: name C:\\folder (no spaces in path name)",
                            bg='#c0c0c0', font=('MS Sans Serif', 7), fg='#000080')
        info_label.pack(pady=5)

if __name__ == "__main__":
    rootpthsed = tk.Tk()
    app = PathsEditor(rootpthsed)
    rootpthsed.mainloop()