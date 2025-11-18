import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import shutil
import difflib
from datetime import datetime

class RetroVersionControl:
    def __init__(self, rootverscontr):
        self.rootverscontr = rootverscontr
        self.rootverscontr.title("Version Controln")
        self.rootverscontr.geometry("900x650")
        
        # Windows 95 colors
        self.bg_color = "#c0c0c0"
        self.button_bg = "#c0c0c0"
        self.text_bg = "#ffffff"
        self.dark_shadow = "#808080"
        self.light_shadow = "#dfdfdf"
        self.active_bg = "#000080"
        self.active_fg = "#ffffff"
        
        self.rootverscontr.configure(bg=self.bg_color)
        
        # Storage directory - va fi setat pentru fiecare folder
        self.storage_dir = None
        self.snapshots_dir = None
        self.branches_file = None
        self.current_branch_file = None
        
        self.working_dir = None
        self.current_branch = "main"
        self.branches = {"main": []}
        
        self.create_ui()
        self.load_last_folder()  # Încearcă să încarce ultimul folder folosit
        
    def init_storage(self):
        """Inițializează storage-ul pentru folderul curent de lucru"""
        if not self.working_dir:
            return
        
        # Storage-ul e ÎNĂUNTRUL folderului de lucru
        self.storage_dir = os.path.join(self.working_dir, ".version_control")
        self.snapshots_dir = os.path.join(self.storage_dir, "snapshots")
        self.branches_file = os.path.join(self.storage_dir, "branches.json")
        self.current_branch_file = os.path.join(self.storage_dir, "current_branch.txt")
        
        if not os.path.exists(self.storage_dir):
            # Folder nou - creează structura
            os.makedirs(self.storage_dir)
            os.makedirs(self.snapshots_dir)
            self.current_branch = "main"
            self.branches = {"main": []}
            self.save_branches()
            with open(self.current_branch_file, 'w') as f:
                f.write(self.current_branch)
        else:
            # Folder existent - încarcă datele salvate
            self.load_branches()
            if os.path.exists(self.current_branch_file):
                with open(self.current_branch_file, 'r') as f:
                    self.current_branch = f.read().strip()
            else:
                self.current_branch = "main"
        
        # Update UI
        self.branch_label.config(text=self.current_branch)
    
    def save_branches(self):
        if self.branches_file:
            with open(self.branches_file, 'w') as f:
                json.dump(self.branches, f, indent=2)

    def load_branches(self):
        if self.branches_file and os.path.exists(self.branches_file):
            with open(self.branches_file, 'r') as f:
                self.branches = json.load(f)
        else:
            self.branches = {"main": []}
        
        if self.current_branch not in self.branches:
            self.branches[self.current_branch] = []
            
    def get_config_dir(self):
        """Returnează directorul de configurare al aplicației"""
        if os.name == 'nt':  # Windows
            config_dir = os.path.join(os.environ.get('APPDATA', ''), 'RetroVersionControl')
        else:  # Linux/Mac
            config_dir = os.path.join(os.path.expanduser('~'), '.version_control_config')
        return config_dir

    def save_last_folder(self):
        """Salvează ultimul folder folosit"""
        try:
            config_dir = self.get_config_dir()
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            config_file = os.path.join(config_dir, 'last_folder.txt')
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(self.working_dir)
        except:
            pass  # Ignoră erorile

    def load_last_folder(self):
        """Încarcă ultimul folder folosit la pornirea aplicației"""
        try:
            config_dir = self.get_config_dir()
            config_file = os.path.join(config_dir, 'last_folder.txt')
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_dir = f.read().strip()
                    if saved_dir and os.path.exists(saved_dir):
                        self.working_dir = saved_dir
                        self.folder_label.config(text=saved_dir)
                        self.init_storage()
                        self.refresh_file_list()
                        self.refresh_timeline()
                        self.refresh_branches_list()
        except:
            pass  # Ignoră erorile
    
    def create_button(self, parent, text, command, row=None, col=None, colspan=1, use_pack=False):
        frame = tk.Frame(parent, bg=self.button_bg, relief=tk.RAISED, bd=3)
        
        if use_pack:
            frame.pack(side=tk.LEFT, padx=8, pady=5)
        else:
            frame.grid(row=row, column=col, columnspan=colspan, padx=8, pady=5, sticky="ew")
        
        btn = tk.Label(frame, text=text, bg=self.button_bg, fg="black", 
                      font=("MS Sans Serif", 9, "bold"), cursor="hand2", padx=20, pady=8)
        btn.pack(fill=tk.BOTH, expand=True)
        
        def on_click(e):
            frame.config(relief=tk.SUNKEN, bd=3)
            def reset_button():
                if frame.winfo_exists():  # Verifică dacă frame-ul mai există
                    frame.config(relief=tk.RAISED, bd=3)
            self.rootverscontr.after(100, reset_button)
            command()
        
        btn.bind("<Button-1>", on_click)
        
        return frame
    
    def create_ui(self):
        # Title bar
        title_frame = tk.Frame(self.rootverscontr, bg=self.active_bg, height=30)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="Version Control", 
                              bg=self.active_bg, fg=self.active_fg, 
                              font=("MS Sans Serif", 10, "bold"), anchor="w", padx=10)
        title_label.pack(fill=tk.BOTH, expand=True)
        
        # Main container
        main_frame = tk.Frame(self.rootverscontr, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top control panel
        control_panel = tk.Frame(main_frame, bg=self.bg_color, relief=tk.GROOVE, bd=2)
        control_panel.pack(fill=tk.X, pady=(0, 10))
        
        # Folder selection
        folder_frame = tk.Frame(control_panel, bg=self.bg_color)
        folder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(folder_frame, text="Working Folder:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=5)
        
        self.folder_label = tk.Label(folder_frame, text="No folder selected", 
                                     bg=self.text_bg, relief=tk.SUNKEN, bd=2, 
                                     anchor="w", font=("MS Sans Serif", 8))
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.create_button(folder_frame, "Browse...", self.select_folder, use_pack=True)
        
        # Branch info
        branch_frame = tk.Frame(control_panel, bg=self.bg_color)
        branch_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(branch_frame, text="Current Branch:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=5)
        
        self.branch_label = tk.Label(branch_frame, text=self.current_branch, 
                                     bg=self.text_bg, relief=tk.SUNKEN, bd=2, 
                                     anchor="w", font=("MS Sans Serif", 8, "bold"),
                                     width=20)
        self.branch_label.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        btn_frame = tk.Frame(control_panel, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        
        self.create_button(btn_frame, "Save Snapshot", self.save_snapshot, 0, 0)
        self.create_button(btn_frame, "View Timeline", self.view_timeline, 0, 1)
        self.create_button(btn_frame, "Manage Branches", self.manage_branches, 0, 2)
        
        # Content area with tabs
        content_frame = tk.Frame(main_frame, bg=self.bg_color, relief=tk.GROOVE, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tab buttons
        tab_frame = tk.Frame(content_frame, bg=self.bg_color)
        tab_frame.pack(fill=tk.X)
        
        self.tab_buttons = {}
        tabs = ["Files", "Timeline", "Branches", "Compare"]
        for i, tab in enumerate(tabs):
            btn_frame = tk.Frame(tab_frame, bg=self.button_bg, relief=tk.RAISED, bd=2)
            btn_frame.pack(side=tk.LEFT, padx=2, pady=2)
            
            btn = tk.Label(btn_frame, text=tab, bg=self.button_bg, fg="black",
                          font=("MS Sans Serif", 8, "bold"), cursor="hand2", padx=15, pady=5)
            btn.pack()
            
            btn.bind("<Button-1>", lambda e, t=tab: self.switch_tab(t))
            self.tab_buttons[tab] = btn_frame
        
        # Content panels
        self.content_container = tk.Frame(content_frame, bg=self.text_bg)
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.panels = {}
        self.create_files_panel()
        self.create_timeline_panel()
        self.create_branches_panel()
        self.create_compare_panel()
        
        self.switch_tab("Files")
        
        # Status bar
        status_frame = tk.Frame(self.rootverscontr, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status label on the left
        self.status_label = tk.Label(status_frame, text="Ready", bg=self.bg_color, 
                                     font=("MS Sans Serif", 8), anchor="w")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=2)
        
        # Progress bar on the right
        self.progress_frame = tk.Frame(status_frame, bg=self.bg_color)
        self.progress_frame.pack(side=tk.RIGHT, padx=5, pady=2)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, length=150, mode='indeterminate')
        self.progress_label = tk.Label(self.progress_frame, text="", bg=self.bg_color,
                                       font=("MS Sans Serif", 7), fg=self.dark_shadow)
    
    def create_files_panel(self):
        panel = tk.Frame(self.content_container, bg=self.text_bg)
        
        # File tree
        tree_frame = tk.Frame(panel, bg=self.text_bg, relief=tk.SUNKEN, bd=2)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(tree_frame, bg=self.text_bg, fg="black",
                                       font=("Courier New", 9),
                                       yscrollcommand=scrollbar.set,
                                       selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        self.file_listbox.bind("<Double-Button-1>", self.edit_file)
        
        self.panels["Files"] = panel
    
    def create_timeline_panel(self):
        panel = tk.Frame(self.content_container, bg=self.text_bg)
        
        list_frame = tk.Frame(panel, bg=self.text_bg, relief=tk.SUNKEN, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.timeline_listbox = tk.Listbox(list_frame, bg=self.text_bg, fg="black",
                                          font=("Courier New", 9),
                                          yscrollcommand=scrollbar.set)
        self.timeline_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.timeline_listbox.yview)
        
        self.timeline_listbox.bind("<Double-Button-1>", self.restore_snapshot)
        
        # Buttons
        btn_frame = tk.Frame(panel, bg=self.text_bg)
        btn_frame.pack(fill=tk.X, pady=5)
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        self.create_button(btn_frame, "Restore Selected", self.restore_snapshot, 0, 0)
        self.create_button(btn_frame, "Delete Selected", self.delete_snapshot, 0, 1)
        
        self.panels["Timeline"] = panel
    
    def create_branches_panel(self):
        panel = tk.Frame(self.content_container, bg=self.text_bg)
        
        list_frame = tk.Frame(panel, bg=self.text_bg, relief=tk.SUNKEN, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.branches_listbox = tk.Listbox(list_frame, bg=self.text_bg, fg="black",
                                          font=("Courier New", 10),
                                          yscrollcommand=scrollbar.set)
        self.branches_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.branches_listbox.yview)
        
        btn_frame = tk.Frame(panel, bg=self.text_bg)
        btn_frame.pack(fill=tk.X, pady=5)
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        btn_frame.grid_columnconfigure(3, weight=1)
        
        self.create_button(btn_frame, "Switch", lambda: self.switch_to_selected_branch(), 0, 0)
        self.create_button(btn_frame, "New Branch", self.create_new_branch, 0, 1)
        self.create_button(btn_frame, "Rename", self.rename_branch, 0, 2)  # ADAUGĂ ACEASTĂ LINIE
        self.create_button(btn_frame, "Delete", self.delete_branch, 0, 3)
        
        self.panels["Branches"] = panel
    
    def create_compare_panel(self):
        panel = tk.Frame(self.content_container, bg=self.text_bg)
        
        # Selection frame
        select_frame = tk.Frame(panel, bg=self.text_bg)
        select_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(select_frame, text="Compare snapshots:", bg=self.text_bg,
                font=("MS Sans Serif", 8, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.compare_var1 = tk.StringVar()
        self.compare_var2 = tk.StringVar()
        
        self.compare_dropdown1 = tk.OptionMenu(select_frame, self.compare_var1, "")
        self.compare_dropdown1.config(bg=self.button_bg, font=("MS Sans Serif", 8))
        self.compare_dropdown1.pack(side=tk.LEFT, padx=5)
        
        tk.Label(select_frame, text="vs", bg=self.text_bg,
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=5)
        
        self.compare_dropdown2 = tk.OptionMenu(select_frame, self.compare_var2, "")
        self.compare_dropdown2.config(bg=self.button_bg, font=("MS Sans Serif", 8))
        self.compare_dropdown2.pack(side=tk.LEFT, padx=5)
        
        self.create_button(select_frame, "Show Differences", self.show_differences, use_pack=True)
        
        # Diff display
        diff_frame = tk.Frame(panel, bg=self.text_bg, relief=tk.SUNKEN, bd=2)
        diff_frame.pack(fill=tk.BOTH, expand=True)
        
        self.diff_text = scrolledtext.ScrolledText(diff_frame, bg=self.text_bg, 
                                                   fg="black", font=("Courier New", 9),
                                                   wrap=tk.NONE, state=tk.DISABLED)
        self.diff_text.pack(fill=tk.BOTH, expand=True)
        
        # Color tags for diff
        self.diff_text.tag_config("added", background="#90EE90", foreground="darkgreen")
        self.diff_text.tag_config("removed", background="#FFB6C1", foreground="darkred")
        self.diff_text.tag_config("header", foreground="blue", font=("Courier New", 9, "bold"))
        
        self.panels["Compare"] = panel
    
    def switch_tab(self, tab_name):
        # Update button styles
        for name, btn_frame in self.tab_buttons.items():
            if name == tab_name:
                btn_frame.config(relief=tk.SUNKEN, bd=2)
            else:
                btn_frame.config(relief=tk.RAISED, bd=2)
        
        # Show selected panel
        for name, panel in self.panels.items():
            if name == tab_name:
                panel.pack(fill=tk.BOTH, expand=True)
                if name == "Timeline":
                    self.refresh_timeline()
                elif name == "Branches":
                    self.refresh_branches_list()
                elif name == "Compare":
                    self.refresh_compare_dropdowns()
            else:
                panel.pack_forget()
    
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.working_dir = folder
            self.folder_label.config(text=folder)
            
            # Inițializează storage pentru acest folder
            self.init_storage()
            
            # Salvează ca ultimul folder folosit
            self.save_last_folder()
            
            # Refresh UI cu datele noului folder
            self.refresh_file_list()
            self.refresh_timeline()
            self.refresh_branches_list()
            
            # Resetează compare
            if hasattr(self, 'compare_var1'):
                self.compare_var1.set("")
                self.compare_var2.set("")
            if hasattr(self, 'diff_text'):
                self.diff_text.config(state=tk.NORMAL)
                self.diff_text.delete(1.0, tk.END)
                self.diff_text.config(state=tk.DISABLED)
            if hasattr(self, 'compare_dropdown1'):
                menu1 = self.compare_dropdown1["menu"]
                menu1.delete(0, "end")
                menu2 = self.compare_dropdown2["menu"]
                menu2.delete(0, "end")
            
            self.status_label.config(text=f"Working folder: {folder} | Branch: {self.current_branch}")
    
    def refresh_file_list(self):
        if not self.working_dir:
            self.file_listbox.delete(0, tk.END)  # ADAUGĂ această linie
            return
        
        self.file_listbox.delete(0, tk.END)
        
        for root, dirs, files in os.walk(self.working_dir):
            # Skip version control directory
            dirs[:] = [d for d in dirs if d != ".version_control"]
            
            level = root.replace(self.working_dir, '').count(os.sep)
            indent = '|   ' * level
            folder_name = os.path.basename(root)
            
            if level > 0:
                self.file_listbox.insert(tk.END, f"{indent}+-- [DIR] {folder_name}/")
            
            sub_indent = '|   ' * (level + 1)
            for file in sorted(files):
                self.file_listbox.insert(tk.END, f"{sub_indent}+-- {file}")
    
    def save_snapshot(self):
        if not self.working_dir:
            messagebox.showwarning("Warning", "Please select a working folder first!")
            return
        
        # Create snapshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"{self.current_branch}_{timestamp}"
        snapshot_path = os.path.join(self.snapshots_dir, snapshot_id)
        
        try:
            # Copy all files (exclude .retro_version_control)
            shutil.copytree(self.working_dir, snapshot_path, 
                          ignore=shutil.ignore_patterns(".version_control"))
            
            # Save metadata
            metadata = {
                "id": snapshot_id,
                "timestamp": timestamp,
                "branch": self.current_branch,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(os.path.join(snapshot_path, "metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Add to branch history
            if self.current_branch not in self.branches:
                self.branches[self.current_branch] = []
            self.branches[self.current_branch].append(snapshot_id)
            self.save_branches()
            
            self.status_label.config(text=f"Snapshot saved: {timestamp}")
            messagebox.showinfo("Success", f"Snapshot saved successfully!\n\nTime: {metadata['datetime']}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save snapshot:\n{str(e)}")
    
    def view_timeline(self):
        self.switch_tab("Timeline")
    
    def refresh_timeline(self):
        self.timeline_listbox.delete(0, tk.END)
        
        if not self.snapshots_dir:
            return
        
        if self.current_branch in self.branches:
            snapshots = self.branches[self.current_branch]
            for snapshot_id in reversed(snapshots):
                snapshot_path = os.path.join(self.snapshots_dir, snapshot_id)
                if os.path.exists(snapshot_path):
                    metadata_file = os.path.join(snapshot_path, "metadata.json")
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        display_text = f"[{metadata['datetime']}] {snapshot_id}"
                        self.timeline_listbox.insert(tk.END, display_text)
    
    def restore_snapshot(self, event=None):
        selection = self.timeline_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a snapshot to restore!")
            return
        
        if not self.working_dir:
            messagebox.showwarning("Warning", "Please select a working folder first!")
            return
        
        selected_text = self.timeline_listbox.get(selection[0])
        snapshot_id = selected_text.split("] ")[1]
        snapshot_path = os.path.join(self.snapshots_dir, snapshot_id)
        
        if messagebox.askyesno("Confirm", "This will replace all files in your working folder.\n\nContinue?"):
            try:
                # Clear working directory (except version control)
                for item in os.listdir(self.working_dir):
                    if item != ".version_control":
                        item_path = os.path.join(self.working_dir, item)
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                
                # Restore from snapshot
                for item in os.listdir(snapshot_path):
                    if item != "metadata.json":
                        src = os.path.join(snapshot_path, item)
                        dst = os.path.join(self.working_dir, item)
                        if os.path.isdir(src):
                            shutil.copytree(src, dst)
                        else:
                            shutil.copy2(src, dst)
                
                self.refresh_file_list()
                self.status_label.config(text=f"Restored snapshot: {snapshot_id}")
                messagebox.showinfo("Success", "Snapshot restored successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restore snapshot:\n{str(e)}")
    
    def delete_snapshot(self):
        selection = self.timeline_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a snapshot to delete!")
            return
        
        selected_text = self.timeline_listbox.get(selection[0])
        snapshot_id = selected_text.split("] ")[1]
        snapshot_path = os.path.join(self.snapshots_dir, snapshot_id)
        
        if messagebox.askyesno("Confirm", f"Delete this snapshot?\n\n{selected_text}"):
            try:
                shutil.rmtree(snapshot_path)
                self.branches[self.current_branch].remove(snapshot_id)
                self.save_branches()
                self.refresh_timeline()
                self.status_label.config(text=f"Deleted snapshot: {snapshot_id}")
                messagebox.showinfo("Success", "Snapshot deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete snapshot:\n{str(e)}")
    
    def create_new_branch(self):
        dialog = tk.Toplevel(self.rootverscontr)
        dialog.title("Create New Branch")
        dialog.geometry("400x150")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.rootverscontr)
        dialog.grab_set()
        
        tk.Label(dialog, text="Enter branch name:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).pack(pady=10)
        
        entry = tk.Entry(dialog, font=("MS Sans Serif", 10), width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def create():
            branch_name = entry.get().strip()
            if not branch_name:
                messagebox.showwarning("Warning", "Branch name cannot be empty!")
                return
            
            if branch_name in self.branches:
                messagebox.showwarning("Warning", "Branch already exists!")
                return
            
            # Create new branch from current branch
            self.branches[branch_name] = self.branches[self.current_branch].copy()
            self.current_branch = branch_name
            self.branch_label.config(text=self.current_branch)
            
            with open(self.current_branch_file, 'w') as f:
                f.write(self.current_branch)
            
            self.save_branches()
            dialog.destroy()
            
            self.status_label.config(text=f"Created and switched to branch: {branch_name}")
            messagebox.showinfo("Success", f"Branch '{branch_name}' created successfully!")
        
        btn_frame = tk.Frame(dialog, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        self.create_button(btn_frame, "Create", create, 0, 0)
        self.create_button(btn_frame, "Cancel", dialog.destroy, 0, 1)
        
        entry.bind("<Return>", lambda e: create())
    
    def manage_branches(self):
        self.switch_tab("Branches")
    
    def refresh_branches_list(self):
        self.branches_listbox.delete(0, tk.END)
        
        for branch_name in sorted(self.branches.keys()):
            snapshot_count = len(self.branches[branch_name])
            if branch_name == self.current_branch:
                display_text = f"> {branch_name} ({snapshot_count} snapshots) [CURRENT]"
            else:
                display_text = f"  {branch_name} ({snapshot_count} snapshots)"
            self.branches_listbox.insert(tk.END, display_text)
    
    def switch_to_selected_branch(self):
        selection = self.branches_listbox.curselection()
        if not selection:
            return
        
        selected_text = self.branches_listbox.get(selection[0])
        branch_name = selected_text.split(" (")[0].strip().replace("> ", "").strip()
        
        if branch_name == self.current_branch:
            return
        
        self.current_branch = branch_name
        self.branch_label.config(text=self.current_branch)
        
        with open(self.current_branch_file, 'w') as f:
            f.write(self.current_branch)
        
        self.refresh_branches_list()
        self.refresh_timeline()
        self.status_label.config(text=f"Switched to branch: {branch_name}")
    
    def delete_branch(self):
        selection = self.branches_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a branch to delete!")
            return
        
        selected_text = self.branches_listbox.get(selection[0])
        branch_name = selected_text.split(" (")[0].strip().replace("> ", "").strip()
        
        if branch_name == self.current_branch:
            messagebox.showwarning("Warning", "Cannot delete the current branch!\n\nSwitch to another branch first.")
            return
        
        if branch_name == "main":
            messagebox.showwarning("Warning", "Cannot delete the 'main' branch!")
            return
        
        if messagebox.askyesno("Confirm", f"Delete branch '{branch_name}' and all its snapshots?\n\nThis action cannot be undone!"):
            try:
                # Delete all snapshots from this branch
                if branch_name in self.branches:
                    for snapshot_id in self.branches[branch_name]:
                        snapshot_path = os.path.join(self.snapshots_dir, snapshot_id)
                        if os.path.exists(snapshot_path):
                            shutil.rmtree(snapshot_path)
                    
                    # Remove branch
                    del self.branches[branch_name]
                    self.save_branches()
                    self.refresh_branches_list()
                    self.status_label.config(text=f"Deleted branch: {branch_name}")
                    messagebox.showinfo("Success", f"Branch '{branch_name}' deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete branch:\n{str(e)}")
    
    def rename_branch(self):
        selection = self.branches_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a branch to rename!")
            return
        
        selected_text = self.branches_listbox.get(selection[0])
        old_branch_name = selected_text.split(" (")[0].strip().replace("> ", "").strip()
        
        if old_branch_name == "main":
            messagebox.showwarning("Warning", "Cannot rename the 'main' branch!")
            return
        
        dialog = tk.Toplevel(self.rootverscontr)
        dialog.title("Rename Branch")
        dialog.geometry("400x150")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.rootverscontr)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Rename '{old_branch_name}' to:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).pack(pady=10)
        
        entry = tk.Entry(dialog, font=("MS Sans Serif", 10), width=30)
        entry.insert(0, old_branch_name)
        entry.pack(pady=5)
        entry.focus()
        entry.select_range(0, tk.END)
        
        def rename():
            new_branch_name = entry.get().strip()
            if not new_branch_name:
                messagebox.showwarning("Warning", "Branch name cannot be empty!")
                return
            
            if new_branch_name in self.branches:
                messagebox.showwarning("Warning", "Branch name already exists!")
                return
            
            # Rename branch
            self.branches[new_branch_name] = self.branches[old_branch_name]
            del self.branches[old_branch_name]
            
            # Update snapshot IDs
            for i, snapshot_id in enumerate(self.branches[new_branch_name]):
                old_snapshot_path = os.path.join(self.snapshots_dir, snapshot_id)
                new_snapshot_id = snapshot_id.replace(f"{old_branch_name}_", f"{new_branch_name}_")
                new_snapshot_path = os.path.join(self.snapshots_dir, new_snapshot_id)
                
                if os.path.exists(old_snapshot_path):
                    os.rename(old_snapshot_path, new_snapshot_path)
                    self.branches[new_branch_name][i] = new_snapshot_id
            
            # Update current branch if necessary
            if self.current_branch == old_branch_name:
                self.current_branch = new_branch_name
                self.branch_label.config(text=self.current_branch)
                with open(self.current_branch_file, 'w') as f:
                    f.write(self.current_branch)
            
            self.save_branches()
            self.refresh_branches_list()
            dialog.destroy()
            
            self.status_label.config(text=f"Renamed branch: {old_branch_name} → {new_branch_name}")
            messagebox.showinfo("Success", f"Branch renamed successfully!")
        
        btn_frame = tk.Frame(dialog, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        self.create_button(btn_frame, "Rename", rename, 0, 0)
        self.create_button(btn_frame, "Cancel", dialog.destroy, 0, 1)
        
        entry.bind("<Return>", lambda e: rename())
    
    def refresh_compare_dropdowns(self):
        if not self.snapshots_dir:
            return
            
        if self.current_branch not in self.branches:
            return
            
        if self.current_branch not in self.branches:
            return
        
        snapshots = self.branches[self.current_branch]
        if not snapshots:
            return
        
        # Clear and repopulate dropdowns
        menu1 = self.compare_dropdown1["menu"]
        menu1.delete(0, "end")
        
        menu2 = self.compare_dropdown2["menu"]
        menu2.delete(0, "end")
        
        for snapshot_id in reversed(snapshots):
            snapshot_path = os.path.join(self.snapshots_dir, snapshot_id)
            if os.path.exists(snapshot_path):
                metadata_file = os.path.join(snapshot_path, "metadata.json")
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    display = f"{metadata['datetime']}"
                    menu1.add_command(label=display, 
                                     command=lambda v=snapshot_id: self.compare_var1.set(v))
                    menu2.add_command(label=display,
                                     command=lambda v=snapshot_id: self.compare_var2.set(v))
        
        if snapshots:
            if len(snapshots) >= 2:
                self.compare_var1.set(snapshots[-2])
                self.compare_var2.set(snapshots[-1])
            else:
                self.compare_var1.set(snapshots[0])
                self.compare_var2.set(snapshots[0])
    
    def show_differences(self):
        snapshot1 = self.compare_var1.get()
        snapshot2 = self.compare_var2.get()
        
        if not snapshot1 or not snapshot2:
            messagebox.showwarning("Warning", "Please select two snapshots to compare!")
            return
        
        path1 = os.path.join(self.snapshots_dir, snapshot1)
        path2 = os.path.join(self.snapshots_dir, snapshot2)
        
        if not os.path.exists(path1) or not os.path.exists(path2):
            messagebox.showerror("Error", "Snapshot not found!")
            return
        
        # Show progress bar
        self.progress_label.config(text="Comparing...")
        self.progress_label.pack(side=tk.LEFT, padx=(0, 5))
        self.progress_bar.pack(side=tk.LEFT)
        self.progress_bar.start(10)
        self.rootverscontr.update()
        
        self.diff_text.config(state=tk.NORMAL)
        self.diff_text.delete(1.0, tk.END)
        
        # Get all files from both snapshots
        files1 = set()
        files2 = set()
        
        for root, dirs, files in os.walk(path1):
            for file in files:
                if file != "metadata.json":
                    rel_path = os.path.relpath(os.path.join(root, file), path1)
                    files1.add(rel_path)
        
        for root, dirs, files in os.walk(path2):
            for file in files:
                if file != "metadata.json":
                    rel_path = os.path.relpath(os.path.join(root, file), path2)
                    files2.add(rel_path)
        
        all_files = files1.union(files2)
        
        for file in sorted(all_files):
            file1_path = os.path.join(path1, file)
            file2_path = os.path.join(path2, file)
            
            self.diff_text.insert(tk.END, f"\n{'='*70}\n", "header")
            self.diff_text.insert(tk.END, f"File: {file}\n", "header")
            self.diff_text.insert(tk.END, f"{'='*70}\n\n", "header")
            
            if not os.path.exists(file1_path):
                self.diff_text.insert(tk.END, "[FILE ADDED]\n\n", "added")
                try:
                    with open(file2_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    for line in content.split('\n')[:50]:
                        self.diff_text.insert(tk.END, f"+ {line}\n", "added")
                except:
                    self.diff_text.insert(tk.END, "[Binary file]\n", "header")
                continue
            
            if not os.path.exists(file2_path):
                self.diff_text.insert(tk.END, "[FILE REMOVED]\n\n", "removed")
                try:
                    with open(file1_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    for line in content.split('\n')[:50]:
                        self.diff_text.insert(tk.END, f"- {line}\n", "removed")
                except:
                    self.diff_text.insert(tk.END, "[Binary file]\n", "header")
                continue
            
            # Compare files
            try:
                with open(file1_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines1 = f.readlines()
                with open(file2_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines2 = f.readlines()
                
                diff = difflib.unified_diff(lines1, lines2, lineterm='', n=3)
                diff_lines = list(diff)
                
                if not diff_lines:
                    self.diff_text.insert(tk.END, "[No changes]\n\n")
                else:
                    for line in diff_lines[:200]:
                        if line.startswith('+') and not line.startswith('+++'):
                            self.diff_text.insert(tk.END, line + "\n", "added")
                        elif line.startswith('-') and not line.startswith('---'):
                            self.diff_text.insert(tk.END, line + "\n", "removed")
                        elif line.startswith('@@'):
                            self.diff_text.insert(tk.END, line + "\n", "header")
                        else:
                            self.diff_text.insert(tk.END, line + "\n")
            except:
                self.diff_text.insert(tk.END, "[Binary file or comparison error]\n\n")
        
        self.diff_text.config(state=tk.DISABLED)
        
        # Hide progress bar
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()
        
        self.status_label.config(text="Comparison complete")
    
    def edit_file(self, event=None):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        
        selected = self.file_listbox.get(selection[0])
        
        if "[DIR]" in selected:
            return
        
        # Extract filename after the tree structure
        if "+--" in selected:
            filename = selected.split("+--")[-1].strip()
        else:
            filename = selected.strip()
        
        # Find full path
        filepath = None
        for root, dirs, files in os.walk(self.working_dir):
            if filename in files:
                filepath = os.path.join(root, filename)
                break
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read file:\n{str(e)}")
            return
        
        # Create editor window
        editor = tk.Toplevel(self.rootverscontr)
        editor.title(f"Edit: {filename}")
        editor.geometry("800x600")
        editor.configure(bg=self.bg_color)
        
        # Title bar
        title_frame = tk.Frame(editor, bg=self.active_bg, height=30)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text=f"Editing: {filename}", 
                              bg=self.active_bg, fg=self.active_fg, 
                              font=("MS Sans Serif", 10, "bold"), anchor="w", padx=10)
        title_label.pack(fill=tk.BOTH, expand=True)
        
        # Text editor
        text_frame = tk.Frame(editor, bg=self.bg_color, relief=tk.GROOVE, bd=2)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame pentru line numbers și text
        editor_container = tk.Frame(text_frame, bg=self.text_bg)
        editor_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Line numbers
        line_numbers = tk.Text(editor_container, width=4, bg="#e0e0e0", fg="black",
                               font=("Courier New", 10), state=tk.DISABLED,
                               relief=tk.FLAT, padx=5)
        line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Scrollbar
        scrollbar = tk.Scrollbar(editor_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text widget
        text_widget = tk.Text(editor_container, bg=self.text_bg, 
                             fg="black", font=("Courier New", 10),
                             wrap=tk.NONE, undo=True,
                             yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        text_widget.insert(1.0, content)
        text_widget.focus()

        # Funcție pentru actualizarea numerelor de linie
        def update_line_numbers(event=None):
            # Salvează poziția curentă de scroll
            current_pos = text_widget.yview()[0]
            
            line_numbers.config(state=tk.NORMAL)
            line_numbers.delete(1.0, tk.END)
            
            # Numără liniile
            line_count = int(text_widget.index('end-1c').split('.')[0])
            line_nums = "\n".join(str(i) for i in range(1, line_count + 1))
            line_numbers.insert(1.0, line_nums)
            line_numbers.config(state=tk.DISABLED)
            
            # Restaurează poziția de scroll
            line_numbers.yview_moveto(current_pos)

        # Sincronizează scroll-ul între text și line numbers
        def on_text_scroll(*args):
            line_numbers.yview_moveto(args[0])
            scrollbar.set(*args)

        def on_scrollbar(*args):
            text_widget.yview(*args)
            line_numbers.yview(*args)

        text_widget.config(yscrollcommand=on_text_scroll)
        scrollbar.config(command=on_scrollbar)

        # Sincronizează și scroll-ul cu mouse wheel
        def on_mouse_scroll(event):
            text_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
            update_line_numbers()
            return "break"

        # Actualizează numerele când textul se schimbă
        text_widget.bind('<KeyRelease>', update_line_numbers)
        text_widget.bind('<Button-1>', lambda e: text_widget.after(1, update_line_numbers))

        # Mouse wheel pentru sincronizare
        text_widget.bind("<MouseWheel>", on_mouse_scroll)
        line_numbers.bind("<MouseWheel>", on_mouse_scroll)

        # Inițializează numerele de linie
        update_line_numbers()
        
        line_numbers.config(cursor="arrow")
        line_numbers.bind("<Button-1>", lambda e: "break")
        
        # Button bar
        btn_bar = tk.Frame(editor, bg=self.bg_color)
        btn_bar.pack(fill=tk.X, padx=5, pady=5)
        
        btn_bar.grid_columnconfigure(0, weight=1)
        btn_bar.grid_columnconfigure(1, weight=1)
        btn_bar.grid_columnconfigure(2, weight=1)
        btn_bar.grid_columnconfigure(3, weight=1)  # ADAUGĂ ACEASTĂ LINIE
        btn_bar.grid_columnconfigure(4, weight=1)
        
        def save_file():
            try:
                new_content = text_widget.get(1.0, tk.END)
                if new_content.endswith('\n'):
                    new_content = new_content[:-1]
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.status_label.config(text=f"Saved: {filename}")
                messagebox.showinfo("Success", f"File saved successfully!\n\n{filename}")
                editor.destroy()
                self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
        
        def save_and_continue():
            try:
                new_content = text_widget.get(1.0, tk.END)
                if new_content.endswith('\n'):
                    new_content = new_content[:-1]
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.status_label.config(text=f"Saved: {filename}")
                self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

        def delete_file():
            if messagebox.askyesno("Confirm", f"Delete this file?\n\n{filename}\n\nThis action cannot be undone!"):
                try:
                    os.remove(filepath)
                    self.status_label.config(text=f"Deleted: {filename}")
                    messagebox.showinfo("Success", f"File deleted successfully!\n\n{filename}")
                    editor.destroy()
                    self.refresh_file_list()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete file:\n{str(e)}")

        def rename_file():
            rename_dialog = tk.Toplevel(editor)
            rename_dialog.title("Rename File")
            rename_dialog.geometry("400x150")
            rename_dialog.configure(bg=self.bg_color)
            rename_dialog.transient(editor)
            rename_dialog.grab_set()
            
            tk.Label(rename_dialog, text="New filename:", bg=self.bg_color,
                    font=("MS Sans Serif", 8)).pack(pady=10)
            
            rename_entry = tk.Entry(rename_dialog, font=("MS Sans Serif", 10), width=30)
            rename_entry.insert(0, filename)
            rename_entry.pack(pady=5)
            rename_entry.focus()
            rename_entry.select_range(0, tk.END)
            
            def do_rename():
                new_filename = rename_entry.get().strip()
                if not new_filename:
                    messagebox.showwarning("Warning", "Filename cannot be empty!")
                    return
                
                new_filepath = os.path.join(os.path.dirname(filepath), new_filename)
                
                if os.path.exists(new_filepath):
                    messagebox.showwarning("Warning", "A file with this name already exists!")
                    return
                
                try:
                    os.rename(filepath, new_filepath)
                    self.status_label.config(text=f"Renamed: {filename} → {new_filename}")
                    messagebox.showinfo("Success", f"File renamed successfully!")
                    rename_dialog.destroy()
                    editor.destroy()
                    self.refresh_file_list()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to rename file:\n{str(e)}")
            
            rbtn_frame = tk.Frame(rename_dialog, bg=self.bg_color)
            rbtn_frame.pack(pady=10)
            rbtn_frame.grid_columnconfigure(0, weight=1)
            rbtn_frame.grid_columnconfigure(1, weight=1)
            
            self.create_button(rbtn_frame, "Rename", do_rename, 0, 0)
            self.create_button(rbtn_frame, "Cancel", rename_dialog.destroy, 0, 1)
            
            rename_entry.bind("<Return>", lambda e: do_rename())

        # Acum creează butoanele - funcțiile sunt deja definite
        self.create_button(btn_bar, "Save & Close", save_file, 0, 0)
        self.create_button(btn_bar, "Save", save_and_continue, 0, 1)
        self.create_button(btn_bar, "Rename", rename_file, 0, 2)
        self.create_button(btn_bar, "Delete", delete_file, 0, 3)
        self.create_button(btn_bar, "Cancel", editor.destroy, 0, 4)

        # Keyboard shortcuts
        text_widget.bind("<Control-s>", lambda e: save_and_continue())
        text_widget.bind("<Control-w>", lambda e: editor.destroy())
    
if __name__ == "__main__":
    rootverscontr = tk.Tk()
    app = RetroVersionControl(rootverscontr)
    rootverscontr.mainloop()