import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import calendar
import sqlite3

class ProjectManager:
    def __init__(self, rootprojectmngr45):
        self.rootprojectmngr45 = rootprojectmngr45
        self.rootprojectmngr45.title("Project Manager")
        self.rootprojectmngr45.geometry("1000x700")
        self.rootprojectmngr45.configure(bg="#c0c0c0")
        
        # Data storage
        self.selected_project_id = None
        self.selected_date = None
        self.current_month = datetime.now().month
        self.current_year = datetime.now().year
        
        # Win95 colors
        self.bg_color = "#c0c0c0"
        self.btn_color = "#c0c0c0"
        self.text_color = "#000000"
        self.highlight = "#000080"
        
        # Initialize database
        self.init_database()
        
        self.create_menu()
        self.create_widgets()
        self.update_button_states()
        self.load_projects()
        
    def init_database(self):
        self.conn = sqlite3.connect('projects.db')
        self.cursor = self.conn.cursor()
        
        # Create projects table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                description TEXT,
                created TEXT NOT NULL
            )
        ''')
        
        # Create tasks table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
            )
        ''')
        
        self.conn.commit()
        
    def create_menu(self):
        menubar = tk.Menu(self.rootprojectmngr45, bg=self.bg_color)
        self.rootprojectmngr45.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_widgets(self):
        # Title bar style frame
        title_frame = tk.Frame(self.rootprojectmngr45, bg="#000080", height=30)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        
        title_label = tk.Label(title_frame, text="Project Manager", 
                              bg="#000080", fg="white", 
                              font=("MS Sans Serif", 10, "bold"))
        title_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Main container
        main_frame = tk.Frame(self.rootprojectmngr45, bg=self.bg_color, relief=tk.RAISED, bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Top container for calendar and main content
        top_container = tk.Frame(main_frame, bg=self.bg_color)
        top_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Project list
        left_panel = tk.Frame(top_container, bg=self.bg_color, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        list_label = tk.Label(left_panel, text="Projects:", 
                             bg=self.bg_color, fg=self.text_color,
                             font=("MS Sans Serif", 8, "bold"))
        list_label.pack(anchor=tk.W)
        
        list_frame = tk.Frame(left_panel, relief=tk.SUNKEN, bd=2)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        xscrollbar = tk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.project_listbox = tk.Listbox(list_frame, 
                                         bg="white", 
                                         fg=self.text_color,
                                         font=("MS Sans Serif", 8),
                                         selectmode=tk.SINGLE,
                                         exportselection=False,
                                         yscrollcommand=scrollbar.set,
                                         xscrollcommand=xscrollbar.set)
        self.project_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.project_listbox.yview)
        xscrollbar.config(command=self.project_listbox.xview)
        self.project_listbox.bind("<<ListboxSelect>>", self.on_project_select)
        
        # Buttons for project list
        btn_frame = tk.Frame(left_panel, bg=self.bg_color)
        btn_frame.pack(fill=tk.X)
        
        add_btn = tk.Button(btn_frame, text="Add", 
                           command=self.new_project,
                           bg=self.btn_color, relief=tk.RAISED, bd=2,
                           font=("MS Sans Serif", 8))
        add_btn.pack(side=tk.LEFT, padx=2)
        
        delete_btn = tk.Button(btn_frame, text="Delete", 
                              command=self.delete_project,
                              bg=self.btn_color, relief=tk.RAISED, bd=2,
                              font=("MS Sans Serif", 8))
        delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Middle panel - Project details
        middle_panel = tk.Frame(top_container, bg=self.bg_color)
        middle_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        details_label = tk.Label(middle_panel, text="Project Details:", 
                                bg=self.bg_color, fg=self.text_color,
                                font=("MS Sans Serif", 8, "bold"))
        details_label.pack(anchor=tk.W)
        
        # Project name
        name_frame = tk.Frame(middle_panel, bg=self.bg_color)
        name_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(name_frame, text="Name:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT)
        
        self.name_entry = tk.Entry(name_frame, font=("MS Sans Serif", 8),
                                   relief=tk.SUNKEN, bd=2)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Status
        status_frame = tk.Frame(middle_panel, bg=self.bg_color)
        status_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(status_frame, text="Status:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="Not Started")
        statuses = ["Not Started", "In Progress", "Completed", "On Hold"]
        
        self.status_radios = []
        for status in statuses:
            rb = tk.Radiobutton(status_frame, text=status, 
                               variable=self.status_var,
                               value=status, bg=self.bg_color,
                               font=("MS Sans Serif", 8))
            rb.pack(side=tk.LEFT, padx=5)
            self.status_radios.append(rb)
        
        # Description
        desc_label = tk.Label(middle_panel, text="Description:", 
                             bg=self.bg_color,
                             font=("MS Sans Serif", 8))
        desc_label.pack(anchor=tk.W, pady=(10, 0))
        
        desc_frame = tk.Frame(middle_panel, relief=tk.SUNKEN, bd=2)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        desc_scroll = tk.Scrollbar(desc_frame)
        desc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.desc_text = tk.Text(desc_frame, 
                                bg="white",
                                font=("MS Sans Serif", 8),
                                yscrollcommand=desc_scroll.set,
                                wrap=tk.WORD,
                                height=6)
        self.desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scroll.config(command=self.desc_text.yview)
        
        # Save button
        self.save_btn = tk.Button(middle_panel, text="Save Changes", 
                           command=self.save_changes,
                           bg=self.btn_color, relief=tk.RAISED, bd=2,
                           font=("MS Sans Serif", 8),
                           width=15)
        self.save_btn.pack(pady=10)
        
        # Right panel - Calendar and Tasks
        right_panel = tk.Frame(top_container, bg=self.bg_color, width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        right_panel.pack_propagate(False)
        
        # Calendar widget
        cal_frame = tk.Frame(right_panel, bg=self.bg_color, relief=tk.RIDGE, bd=2)
        cal_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Calendar header
        cal_header = tk.Frame(cal_frame, bg="#000080")
        cal_header.pack(fill=tk.X)
        
        self.prev_btn = tk.Button(cal_header, text="<", 
                                  command=self.prev_month,
                                  bg=self.btn_color, relief=tk.RAISED, bd=1,
                                  font=("MS Sans Serif", 8),
                                  width=2)
        self.prev_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        self.month_label = tk.Label(cal_header, text="", 
                                    bg="#000080", fg="white",
                                    font=("MS Sans Serif", 9, "bold"))
        self.month_label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.next_btn = tk.Button(cal_header, text=">", 
                                  command=self.next_month,
                                  bg=self.btn_color, relief=tk.RAISED, bd=1,
                                  font=("MS Sans Serif", 8),
                                  width=2)
        self.next_btn.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Calendar grid
        self.cal_grid = tk.Frame(cal_frame, bg="white")
        self.cal_grid.pack(fill=tk.BOTH, padx=2, pady=2)
        
        # Day headers
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for i, day in enumerate(days):
            lbl = tk.Label(self.cal_grid, text=day, bg="#c0c0c0", 
                          font=("MS Sans Serif", 7, "bold"),
                          width=3, relief=tk.RAISED, bd=1)
            lbl.grid(row=0, column=i, padx=1, pady=1)
        
        # Calendar day buttons
        self.day_buttons = []
        for row in range(6):
            for col in range(7):
                btn = tk.Button(self.cal_grid, text="", 
                               bg="white",
                               font=("MS Sans Serif", 7),
                               width=3, height=1,
                               relief=tk.RAISED, bd=1,
                               command=lambda r=row, c=col: self.select_day(r, c))
                btn.grid(row=row+1, column=col, padx=1, pady=1)
                btn.bind("<Button-3>", lambda e, r=row, c=col: self.show_day_context_menu(e, r, c))
                self.day_buttons.append(btn)
        
        # Tasks section
        task_header = tk.Frame(right_panel, bg=self.bg_color)
        task_header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(task_header, text="Tasks:", 
                bg=self.bg_color, fg=self.text_color,
                font=("MS Sans Serif", 8, "bold")).pack(side=tk.LEFT)
        
        self.add_task_btn = tk.Button(task_header, text="Add Task", 
                                command=self.add_task,
                                bg=self.btn_color, relief=tk.RAISED, bd=2,
                                font=("MS Sans Serif", 7))
        self.add_task_btn.pack(side=tk.RIGHT)
        
        # Tasks list
        task_frame = tk.Frame(right_panel, relief=tk.SUNKEN, bd=2)
        task_frame.pack(fill=tk.BOTH, expand=True)

        task_scroll = tk.Scrollbar(task_frame)
        task_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        xtask_scroll = tk.Scrollbar(task_frame, orient=tk.HORIZONTAL)
        xtask_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.task_listbox = tk.Listbox(task_frame, 
                                       bg="white",
                                       font=("MS Sans Serif", 7),
                                       yscrollcommand=task_scroll.set,
                                       xscrollcommand=xtask_scroll.set)
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        task_scroll.config(command=self.task_listbox.yview)
        xtask_scroll.config(command=self.task_listbox.xview)
        self.task_listbox.bind("<Double-Button-1>", self.toggle_task)
        
        # Delete task button
        self.del_task_btn = tk.Button(right_panel, text="Delete Task", 
                                command=self.delete_task,
                                bg=self.btn_color, relief=tk.RAISED, bd=2,
                                font=("MS Sans Serif", 7))
        self.del_task_btn.pack(pady=5)
        
        # Status bar
        status_bar = tk.Frame(self.rootprojectmngr45, bg=self.bg_color, relief=tk.SUNKEN, bd=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(status_bar, text="Ready", 
                                    bg=self.bg_color,
                                    font=("MS Sans Serif", 8),
                                    anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Initialize calendar
        self.update_calendar()
        
    def update_button_states(self):
        state = tk.NORMAL if self.selected_project_id else tk.DISABLED
        
        self.save_btn.config(state=state)
        self.add_task_btn.config(state=state)
        self.del_task_btn.config(state=state)
        self.name_entry.config(state=state)
        self.desc_text.config(state=state)
        
        for rb in self.status_radios:
            rb.config(state=state)
        
    def load_projects(self):
        self.project_listbox.delete(0, tk.END)
        self.cursor.execute('SELECT id, name, status FROM projects ORDER BY created DESC')
        projects = self.cursor.fetchall()
        
        for project_id, name, status in projects:
            display = f"{name} [{status}]"
            self.project_listbox.insert(tk.END, display)
            
        # Restore selection if a project was selected
        if self.selected_project_id:
            self.cursor.execute('SELECT id FROM projects ORDER BY created DESC')
            project_ids = [row[0] for row in self.cursor.fetchall()]
            if self.selected_project_id in project_ids:
                idx = project_ids.index(self.selected_project_id)
                self.project_listbox.selection_set(idx)
                self.project_listbox.see(idx)
                
    def update_calendar(self):
        month_name = calendar.month_name[self.current_month]
        self.month_label.config(text=f"{month_name} {self.current_year}")
        
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        
        # Get tasks for current month if project is selected
        tasks_this_month = []
        if self.selected_project_id:
            self.cursor.execute('''
                SELECT date FROM tasks 
                WHERE project_id = ? AND date LIKE ?
            ''', (self.selected_project_id, f"{self.current_year}-{self.current_month:02d}%"))
            tasks_this_month = [row[0] for row in self.cursor.fetchall()]
        
        idx = 0
        for week in cal:
            for day in week:
                if day == 0:
                    self.day_buttons[idx].config(text="", state=tk.DISABLED, bg="#c0c0c0")
                else:
                    self.day_buttons[idx].config(text=str(day), state=tk.NORMAL, bg="white")
                    
                    # Highlight today
                    today = datetime.now()
                    if (day == today.day and 
                        self.current_month == today.month and 
                        self.current_year == today.year):
                        self.day_buttons[idx].config(bg="#ffff00")
                    
                    # Highlight days with tasks
                    date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                    if date_str in tasks_this_month:
                        self.day_buttons[idx].config(fg="#ff0000", font=("MS Sans Serif", 7, "bold"))
                    else:
                        self.day_buttons[idx].config(fg="#000000", font=("MS Sans Serif", 7))
                
                idx += 1
        
        self.refresh_task_list()
        
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
        
    def select_day(self, row, col):
        if not self.selected_project_id:
            return
            
        idx = row * 7 + col
        day_text = self.day_buttons[idx].cget("text")
        
        if day_text:
            day = int(day_text)
            self.selected_date = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
            self.status_label.config(text=f"Selected: {self.selected_date}")
            self.refresh_task_list()
    
    def show_day_context_menu(self, event, row, col):
        if not self.selected_project_id:
            return
            
        idx = row * 7 + col
        day_text = self.day_buttons[idx].cget("text")
        
        if day_text:
            day = int(day_text)
            self.selected_date = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
            
            context_menu = tk.Menu(self.rootprojectmngr45, tearoff=0, bg=self.bg_color)
            context_menu.add_command(label="Add Task", command=self.add_task)
            context_menu.add_separator()
            
            self.cursor.execute('''
                SELECT COUNT(*) FROM tasks 
                WHERE project_id = ? AND date = ?
            ''', (self.selected_project_id, self.selected_date))
            task_count = self.cursor.fetchone()[0]
            
            if task_count > 0:
                context_menu.add_command(label=f"View Tasks ({task_count})", 
                                       command=lambda: self.refresh_task_list())
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
            
    def add_task(self):
        if not self.selected_project_id:
            messagebox.showwarning("Warning", "Please select a project first")
            return
            
        if not self.selected_date:
            messagebox.showwarning("Warning", "Please select a date first")
            return
            
        task_name = simpledialog.askstring("New Task", "Enter task description:")
        if task_name:
            self.cursor.execute('''
                INSERT INTO tasks (project_id, name, date, completed)
                VALUES (?, ?, ?, 0)
            ''', (self.selected_project_id, task_name, self.selected_date))
            self.conn.commit()
            self.update_calendar()
            self.status_label.config(text=f"Task added for {self.selected_date}")
            
    def delete_task(self):
        if not self.selected_project_id:
            return
            
        selection = self.task_listbox.curselection()
        if selection:
            idx = selection[0]
            
            self.cursor.execute('''
                SELECT id FROM tasks 
                WHERE project_id = ? AND date = ?
                ORDER BY id
            ''', (self.selected_project_id, self.selected_date))
            tasks = self.cursor.fetchall()
            
            if idx < len(tasks):
                task_id = tasks[idx][0]
                self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                self.conn.commit()
                self.update_calendar()
                self.status_label.config(text="Task deleted")
        else:
            messagebox.showwarning("Warning", "Please select a task to delete")
            
    def toggle_task(self, event):
        if not self.selected_project_id:
            return
            
        selection = self.task_listbox.curselection()
        if selection:
            idx = selection[0]
            
            self.cursor.execute('''
                SELECT id, completed FROM tasks 
                WHERE project_id = ? AND date = ?
                ORDER BY id
            ''', (self.selected_project_id, self.selected_date))
            tasks = self.cursor.fetchall()
            
            if idx < len(tasks):
                task_id, completed = tasks[idx]
                new_status = 0 if completed else 1
                self.cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', 
                                  (new_status, task_id))
                self.conn.commit()
                self.refresh_task_list()
                
    def refresh_task_list(self):
        self.task_listbox.delete(0, tk.END)
        if self.selected_date and self.selected_project_id:
            self.cursor.execute('''
                SELECT name, completed FROM tasks 
                WHERE project_id = ? AND date = ?
                ORDER BY id
            ''', (self.selected_project_id, self.selected_date))
            tasks = self.cursor.fetchall()
            
            for name, completed in tasks:
                status = "[X]" if completed else "[ ]"
                self.task_listbox.insert(tk.END, f"{status} {name}")
        
    def new_project(self):
        name = simpledialog.askstring("New Project", "Enter project name:")
        if name:
            created = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.cursor.execute('''
                INSERT INTO projects (name, status, description, created)
                VALUES (?, ?, ?, ?)
            ''', (name, "Not Started", "", created))
            self.conn.commit()
            
            self.selected_project_id = self.cursor.lastrowid
            self.load_projects()
            self.update_button_states()
            self.update_calendar()
            self.status_label.config(text=f"Project '{name}' created")
            
    def delete_project(self):
        selection = self.project_listbox.curselection()
        if selection:
            idx = selection[0]
            
            self.cursor.execute('SELECT id, name FROM projects ORDER BY created DESC')
            projects = self.cursor.fetchall()
            
            if idx < len(projects):
                project_id, name = projects[idx]
                if messagebox.askyesno("Delete Project", 
                                      f"Delete project '{name}' and all its tasks?"):
                    self.cursor.execute('DELETE FROM tasks WHERE project_id = ?', (project_id,))
                    self.cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
                    self.conn.commit()
                    
                    if self.selected_project_id == project_id:
                        self.selected_project_id = None
                        self.clear_details()
                        self.update_button_states()
                    
                    self.load_projects()
                    self.update_calendar()
                    self.status_label.config(text="Project deleted")
                
    def on_project_select(self, event):
        selection = self.project_listbox.curselection()
        if selection:
            idx = selection[0]
            
            self.cursor.execute('SELECT id FROM projects ORDER BY created DESC')
            projects = self.cursor.fetchall()
            
            if idx < len(projects):
                self.selected_project_id = projects[idx][0]
                self.load_project_details()
                self.update_button_states()
                self.update_calendar()
            
    def load_project_details(self):
        if not self.selected_project_id:
            return
            
        self.cursor.execute('''
            SELECT name, status, description FROM projects WHERE id = ?
        ''', (self.selected_project_id,))
        result = self.cursor.fetchone()
        
        if result:
            name, status, description = result
            
            self.name_entry.config(state=tk.NORMAL)
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name)
            
            self.status_var.set(status)
            
            self.desc_text.config(state=tk.NORMAL)
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", description if description else "")
        
    def save_changes(self):
        if not self.selected_project_id:
            messagebox.showwarning("Warning", "No project selected")
            return
            
        name = self.name_entry.get()
        status = self.status_var.get()
        description = self.desc_text.get("1.0", tk.END).strip()
        
        self.cursor.execute('''
            UPDATE projects 
            SET name = ?, status = ?, description = ?
            WHERE id = ?
        ''', (name, status, description, self.selected_project_id))
        self.conn.commit()
        
        self.load_projects()
        self.status_label.config(text="Changes saved")
        messagebox.showinfo("Success", "Project updated successfully!")
            
    def clear_details(self):
        self.name_entry.config(state=tk.NORMAL)
        self.name_entry.delete(0, tk.END)
        self.status_var.set("Not Started")
        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.delete("1.0", tk.END)
        self.task_listbox.delete(0, tk.END)
        self.selected_date = None
        
    def show_about(self):
        messagebox.showinfo("About", 
                          "Project Manager v1.0\n\nManage your projects with style!")
    
    def on_closing(self):
        self.conn.close()
        self.rootprojectmngr45.quit()

if __name__ == "__main__":
    rootprojectmngr45 = tk.Tk()
    app = ProjectManager(rootprojectmngr45)
    rootprojectmngr45.protocol("WM_DELETE_WINDOW", app.on_closing)
    rootprojectmngr45.mainloop()