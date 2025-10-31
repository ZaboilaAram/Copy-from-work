import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

class ProfilesEditor:
    def __init__(self, rootprofed):
        self.rootprofed = rootprofed
        self.rootprofed.title("Profiles Editor")
        self.rootprofed.geometry("700x500")
        self.rootprofed.configure(bg='#c0c0c0')
        self.rootprofed.resizable(False, False)
        
        self.paths_file = "paths.txt"
        self.profiles_file = "profiles.json"
        self.available_items = []
        self.profiles = {}
        self.current_profile = None
        
        # Load paths.txt
        self.load_paths()
        
        # Check and load profiles.json
        self.check_and_load_profiles()
        
        # Create UI
        self.create_widgets()
        
    def load_paths(self):
        if not os.path.exists(self.paths_file):
            messagebox.showerror("Error", f"{self.paths_file} not found!")
            self.rootprofed.destroy()
            return
        
        try:
            with open(self.paths_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.strip().split('\n')
                for line in lines:
                    if line.strip():
                        # Extract name before : or space
                        if ':' in line:
                            name = line.split(':')[0].strip()
                        elif ' ' in line:
                            name = line.split(' ')[0].strip()
                        else:
                            name = line.strip()
                        
                        if name and name not in self.available_items:
                            self.available_items.append(name)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read {self.paths_file}: {str(e)}")
            self.rootprofed.destroy()
    
    def check_and_load_profiles(self):
        if not os.path.exists(self.profiles_file):
            # Ask how many profiles to create
            num_profiles = simpledialog.askinteger(
                "Create Profiles", 
                "How many profiles do you want to create?",
                minvalue=1, maxvalue=50
            )
            
            if num_profiles:
                self.create_initial_profiles(num_profiles)
            else:
                messagebox.showwarning("Warning", "No profiles created. Creating empty file.")
                self.profiles = {}
                self.save_profiles()
        else:
            self.load_profiles()
    
    def create_initial_profiles(self, count):
        for i in range(count):
            profile_name = simpledialog.askstring(
                "Profile Name",
                f"Enter name for profile {i+1}:"
            )
            
            if profile_name:
                self.profiles[profile_name] = {"checkboxes": []}
            else:
                messagebox.showwarning("Warning", f"Skipped profile {i+1}")
        
        self.save_profiles()
        messagebox.showinfo("Success", f"{len(self.profiles)} profiles created!")
    
    def load_profiles(self):
        try:
            with open(self.profiles_file, 'r', encoding='utf-8') as f:
                self.profiles = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load {self.profiles_file}: {str(e)}")
            self.profiles = {}
    
    def save_profiles(self):
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save {self.profiles_file}: {str(e)}")
    
    def on_profile_select(self, event):
        selection = self.profile_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_profile = list(self.profiles.keys())[index]
            self.refresh_selected_items()
    
    def refresh_selected_items(self):
        self.selected_listbox.delete(0, tk.END)
        if self.current_profile and self.current_profile in self.profiles:
            for item in self.profiles[self.current_profile]["checkboxes"]:
                self.selected_listbox.insert(tk.END, item)
    
    def add_items_to_profile(self):
        if not self.current_profile:
            messagebox.showwarning("Warning", "Please select a profile first")
            return
        
        # Create selection window
        selection_window = tk.Toplevel(self.rootprofed)
        selection_window.title(f"Add Items to {self.current_profile}")
        selection_window.geometry("400x500")
        selection_window.configure(bg='#c0c0c0')
        selection_window.transient(self.rootprofed)
        selection_window.grab_set()
        
        # Title
        title_label = tk.Label(selection_window, text=f"Select items for: {self.current_profile}",
                              bg='#c0c0c0', font=('MS Sans Serif', 9, 'bold'))
        title_label.pack(pady=10)
        
        # Frame for listbox
        frame = tk.Frame(selection_window, bg='#c0c0c0', relief=tk.SUNKEN, bd=2)
        frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        items_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set,
                                   font=('MS Sans Serif', 9),
                                   selectmode=tk.MULTIPLE, bg='white')
        items_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=items_listbox.yview)
        
        # Populate with available items
        current_items = self.profiles[self.current_profile]["checkboxes"]
        for item in self.available_items:
            items_listbox.insert(tk.END, item)
            # Pre-select items already in profile
            if item in current_items:
                index = self.available_items.index(item)
                items_listbox.selection_set(index)
        
        # Buttons
        button_frame = tk.Frame(selection_window, bg='#c0c0c0')
        button_frame.pack(pady=10)
        
        def save_selection():
            selected_indices = items_listbox.curselection()
            selected_items = [self.available_items[i] for i in selected_indices]
            self.profiles[self.current_profile]["checkboxes"] = selected_items
            self.save_profiles()
            self.refresh_selected_items()
            messagebox.showinfo("Success", f"Items updated for {self.current_profile}")
            selection_window.destroy()
        
        save_btn = tk.Button(button_frame, text="Save", command=save_selection,
                           width=12, font=('MS Sans Serif', 8), relief=tk.RAISED, bd=2)
        save_btn.grid(row=0, column=0, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=selection_window.destroy,
                             width=12, font=('MS Sans Serif', 8), relief=tk.RAISED, bd=2)
        cancel_btn.grid(row=0, column=1, padx=5)
    
    def add_new_profile(self):
        profile_name = simpledialog.askstring("New Profile", "Enter profile name:")
        
        if profile_name:
            if profile_name in self.profiles:
                messagebox.showwarning("Warning", "Profile already exists!")
                return
            
            self.profiles[profile_name] = {"checkboxes": []}
            self.save_profiles()
            self.refresh_profile_list()
            messagebox.showinfo("Success", f"Profile '{profile_name}' created!")
    
    def delete_profile(self):
        if not self.current_profile:
            messagebox.showwarning("Warning", "Please select a profile first")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", 
                                     f"Delete profile '{self.current_profile}'?")
        if confirm:
            del self.profiles[self.current_profile]
            self.save_profiles()
            self.current_profile = None
            self.refresh_profile_list()
            self.selected_listbox.delete(0, tk.END)
            messagebox.showinfo("Success", "Profile deleted!")
    
    def refresh_profile_list(self):
        self.profile_listbox.delete(0, tk.END)
        for profile_name in self.profiles.keys():
            self.profile_listbox.insert(tk.END, profile_name)
    
    def create_widgets(self):
        # Title frame
        title_frame = tk.Frame(self.rootprofed, bg='#000080', height=25)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="Profiles Configuration Manager", 
                              bg='#000080', fg='white', 
                              font=('MS Sans Serif', 9, 'bold'))
        title_label.pack(pady=3)
        
        # Main frame
        main_frame = tk.Frame(self.rootprofed, bg='#c0c0c0', relief=tk.RIDGE, bd=3)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Top buttons
        button_frame = tk.Frame(main_frame, bg='#c0c0c0')
        button_frame.pack(pady=10)
        
        add_profile_btn = tk.Button(button_frame, text="New Profile", 
                                   command=self.add_new_profile,
                                   width=15, font=('MS Sans Serif', 8), 
                                   relief=tk.RAISED, bd=5)
        add_profile_btn.grid(row=0, column=0, padx=5)
        
        delete_profile_btn = tk.Button(button_frame, text="Delete Profile", 
                                      command=self.delete_profile,
                                      width=15, font=('MS Sans Serif', 8), 
                                      relief=tk.RAISED, bd=5)
        delete_profile_btn.grid(row=0, column=1, padx=5)
        
        add_items_btn = tk.Button(button_frame, text="Add/Edit Items", 
                                 command=self.add_items_to_profile,
                                 width=15, font=('MS Sans Serif', 8), 
                                 relief=tk.RAISED, bd=5, bg='#ffff00')
        add_items_btn.grid(row=0, column=2, padx=5)
        
        # Content frame with two columns
        content_frame = tk.Frame(main_frame, bg='#c0c0c0')
        content_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Left column - Profiles list
        left_frame = tk.Frame(content_frame, bg='#c0c0c0', relief=tk.SUNKEN, bd=3)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        profiles_label = tk.Label(left_frame, text="Profiles:", bg='#c0c0c0',
                                 font=('MS Sans Serif', 8, 'bold'))
        profiles_label.pack(anchor=tk.W, padx=5, pady=5)
        
        scrollbar1 = tk.Scrollbar(left_frame)
        scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.profile_listbox = tk.Listbox(left_frame, yscrollcommand=scrollbar1.set,
                                         font=('MS Sans Serif', 9), bg='white',
                                         selectmode=tk.SINGLE)
        self.profile_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.profile_listbox.bind('<<ListboxSelect>>', self.on_profile_select)
        scrollbar1.config(command=self.profile_listbox.yview)
        
        # Right column - Selected items
        right_frame = tk.Frame(content_frame, bg='#c0c0c0', relief=tk.SUNKEN, bd=3)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        selected_label = tk.Label(right_frame, text="Selected Items:", bg='#c0c0c0',
                                 font=('MS Sans Serif', 8, 'bold'))
        selected_label.pack(anchor=tk.W, padx=5, pady=5)
        
        scrollbar2 = tk.Scrollbar(right_frame)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.selected_listbox = tk.Listbox(right_frame, yscrollcommand=scrollbar2.set,
                                          font=('MS Sans Serif', 9), bg='white')
        self.selected_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar2.config(command=self.selected_listbox.yview)
        
        # Info label
        info_label = tk.Label(main_frame, 
                            text="Select profile -> Click 'Add/Edit Items' -> Select items -> Save",
                            bg='#c0c0c0', font=('MS Sans Serif', 7), fg='#000080')
        info_label.pack(pady=5)
        
        # Populate profiles list
        self.refresh_profile_list()

if __name__ == "__main__":
    rootprofed = tk.Tk()
    app = ProfilesEditor(rootprofed)
    rootprofed.mainloop()