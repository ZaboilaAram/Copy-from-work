import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import json
import time
from datetime import datetime
from tkinter import ttk

class QuizApp:
    def __init__(self, root_QIUIZZZ):
        self.root_QIUIZZZ = root_QIUIZZZ
        self.root_QIUIZZZ.title("Quiz Creator")
        #self.root_QIUIZZZ.geometry("800x600")
        self.root_QIUIZZZ.configure(bg='#c0c0c0')
        #self.root_QIUIZZZ.resizable(False, False)
        self.root_QIUIZZZ.resizable(True, True)
        self.root_QIUIZZZ.minsize(800, 600)
        
        # Windows 95 color scheme
        self.bg_color = '#c0c0c0'
        self.button_color = '#c0c0c0'
        self.text_color = '#000000'
        self.highlight_color = '#0000ff'
        self.entry_color = '#ffffff'
        self.shadow_color = '#808080'
        self.light_color = '#ffffff'
        
        # Quiz variables
        self.current_quiz = None
        self.current_question = 0
        self.quiz_answers = []
        self.start_time = None
        self.timer_var = None
        self.timer_after_id = None
        self.quiz_time_left = 0
        
        # Initialize database
        self.init_database()
        
        # Create main interface
        self.create_main_interface()
        
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('quiz_app.db')
        self.cursor = self.conn.cursor()
        
        # Quiz table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                timer_enabled INTEGER DEFAULT 0,
                timer_seconds INTEGER DEFAULT 0,
                questions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Results table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER,
                quiz_title TEXT,
                score INTEGER,
                total_questions INTEGER,
                time_taken INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
            )
        ''')
        
        self.conn.commit()
    
    def create_button(self, parent, text, command, width=15, height=2):
        """Create a Windows 95 style button"""
        btn = tk.Button(parent, text=text, command=command, 
                       width=width, height=height,
                       bg=self.button_color, fg=self.text_color,
                       relief=tk.RAISED, bd=2,
                       font=('MS Sans Serif', 8, 'normal'),
                       activebackground='#e0e0e0',
                       cursor='hand2')
        return btn
    
    def create_frame_3d(self, parent, relief=tk.SUNKEN, bd=2):
        """Create a 3D-style frame"""
        return tk.Frame(parent, bg=self.bg_color, relief=relief, bd=bd)
    
    def create_label_header(self, parent, text, font_size=14):
        """Create a header-style label"""
        return tk.Label(parent, text=text, 
                       font=('MS Sans Serif', font_size, 'bold'), 
                       bg=self.bg_color, fg=self.text_color)
    
    def create_main_interface(self):
        """Create main interface"""
        # Clear existing content
        for widget in self.root_QIUIZZZ.winfo_children():
            widget.destroy()
        self.root_QIUIZZZ.geometry("800x600")
        # Title bar area
        title_frame = self.create_frame_3d(self.root_QIUIZZZ, tk.RAISED, 2)
        title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = self.create_label_header(title_frame, "Quiz Creator", 16)
        title_label.pack(pady=15)
        
        # Main container with 3D effect
        main_frame = self.create_frame_3d(self.root_QIUIZZZ, tk.SUNKEN, 2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Inner container
        inner_frame = tk.Frame(main_frame, bg=self.bg_color)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Welcome message
        welcome_label = tk.Label(inner_frame, text="Welcome to Quiz Creator", 
                                font=('MS Sans Serif', 12, 'bold'),
                                bg=self.bg_color, fg=self.text_color)
        welcome_label.pack(pady=(20, 30))
        
        # Button container with 3D effect
        button_container = self.create_frame_3d(inner_frame, tk.SUNKEN, 1)
        button_container.pack(pady=20)
        
        buttons_frame = tk.Frame(button_container, bg=self.bg_color)
        buttons_frame.pack(padx=20, pady=20)
        
        # Main buttons
        self.create_button(buttons_frame, "Create New Quiz", self.create_new_quiz, width=25).pack(pady=8)
        self.create_button(buttons_frame, "Quiz List", self.show_quiz_list, width=25).pack(pady=8)
        self.create_button(buttons_frame, "View Results", self.show_results, width=25).pack(pady=8)
        
        # Separator
        separator = tk.Frame(buttons_frame, height=2, bg=self.shadow_color)
        separator.pack(fill=tk.X, pady=10)
        
        self.create_button(buttons_frame, "Exit", self.root_QIUIZZZ.quit, width=25).pack(pady=8)
        
    def create_new_quiz(self):
        """Interface for creating a new quiz"""
        for widget in self.root_QIUIZZZ.winfo_children():
            widget.destroy()
            
        # Header
        header_frame = self.create_frame_3d(self.root_QIUIZZZ, tk.RAISED, 2)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = self.create_label_header(header_frame, "Create New Quiz")
        title_label.pack(pady=10)
        
        # Main form container
        form_container = self.create_frame_3d(self.root_QIUIZZZ, tk.SUNKEN, 2)
        form_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        form_frame = tk.Frame(form_container, bg=self.bg_color)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Quiz title
        title_group = self.create_frame_3d(form_frame, tk.RAISED, 1)
        title_group.pack(fill=tk.X, pady=(0,10))
        
        title_inner = tk.Frame(title_group, bg=self.bg_color)
        title_inner.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(title_inner, text="Quiz Title:", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        self.title_entry = tk.Entry(title_inner, font=('MS Sans Serif', 9), width=60,
                                   relief=tk.SUNKEN, bd=2)
        self.title_entry.pack(pady=(2,0), fill=tk.X)
        
        # Description
        desc_group = self.create_frame_3d(form_frame, tk.RAISED, 1)
        desc_group.pack(fill=tk.X, pady=(0,10))
        
        desc_inner = tk.Frame(desc_group, bg=self.bg_color)
        desc_inner.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(desc_inner, text="Description:", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        self.desc_text = tk.Text(desc_inner, height=3, font=('MS Sans Serif', 9),
                                relief=tk.SUNKEN, bd=2)
        self.desc_text.pack(pady=(2,0), fill=tk.X)
        
        # Timer settings
        timer_group = self.create_frame_3d(form_frame, tk.RAISED, 1)
        timer_group.pack(fill=tk.X, pady=(0,10))
        
        timer_inner = tk.Frame(timer_group, bg=self.bg_color)
        timer_inner.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(timer_inner, text="Timer Settings:", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        
        timer_frame = tk.Frame(timer_inner, bg=self.bg_color)
        timer_frame.pack(fill=tk.X, pady=(2,0))
        
        self.timer_var = tk.IntVar()
        timer_check = tk.Checkbutton(timer_frame, text="Enable Timer", 
                                   variable=self.timer_var,
                                   bg=self.bg_color, fg=self.text_color,
                                   font=('MS Sans Serif', 9))
        timer_check.pack(side=tk.LEFT)
        
        tk.Label(timer_frame, text="Seconds:", font=('MS Sans Serif', 9),
                bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(20,5))
        self.timer_entry = tk.Entry(timer_frame, width=10, font=('MS Sans Serif', 9),
                                   relief=tk.SUNKEN, bd=2)
        self.timer_entry.pack(side=tk.LEFT)
        self.timer_entry.insert(0, "300")
        
        # Questions section
        questions_group = self.create_frame_3d(form_frame, tk.RAISED, 1)
        questions_group.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        
        questions_inner = tk.Frame(questions_group, bg=self.bg_color)
        questions_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(questions_inner, text="Questions:", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        
        # Questions list with scrollbar
        list_frame = tk.Frame(questions_inner, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(2,0))
        
        self.questions_list = tk.Listbox(list_frame, height=8, font=('MS Sans Serif', 9),
                                        relief=tk.SUNKEN, bd=2)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.questions_list.yview)
        self.questions_list.config(yscrollcommand=scrollbar.set)
        
        self.questions_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Question buttons
        questions_buttons_frame = tk.Frame(questions_inner, bg=self.bg_color)
        questions_buttons_frame.pack(fill=tk.X, pady=(5,0))
        
        self.create_button(questions_buttons_frame, "Add Question", self.add_question, width=15).pack(side=tk.LEFT, padx=2)
        self.create_button(questions_buttons_frame, "Edit", self.edit_question, width=15).pack(side=tk.LEFT, padx=2)
        self.create_button(questions_buttons_frame, "Delete", self.delete_question, width=15).pack(side=tk.LEFT, padx=2)
        
        # Initialize questions data
        self.questions_data = []
        
        # Bottom buttons
        bottom_frame = tk.Frame(form_frame, bg=self.bg_color)
        bottom_frame.pack(fill=tk.X, pady=(10,0))
        
        self.create_button(bottom_frame, "Save Quiz", self.save_quiz, width=15).pack(side=tk.LEFT)
        self.create_button(bottom_frame, "Back", self.create_main_interface, width=15).pack(side=tk.RIGHT)
        
    def add_question(self):
        """Add a new question"""
        self.edit_question_dialog()
        
    def edit_question(self):
        """Edit selected question"""
        selection = self.questions_list.curselection()
        if not selection:
            messagebox.showwarning("Selection", "Select a question to edit!")
            return
        
        index = selection[0]
        question_data = self.questions_data[index]
        self.edit_question_dialog(question_data, index)
        
    def delete_question(self):
        """Delete selected question"""
        selection = self.questions_list.curselection()
        if not selection:
            messagebox.showwarning("Selection", "Select a question to delete!")
            return
        
        index = selection[0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this question?"):
            del self.questions_data[index]
            self.update_questions_list()
        
    def edit_question_dialog(self, existing_data=None, edit_index=None):
        """Dialog for editing/adding a question"""
        dialog = tk.Toplevel(self.root_QIUIZZZ)
        dialog.title("Add/Edit Question")
        dialog.geometry("600x500")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root_QIUIZZZ)
        dialog.grab_set()
        
        # Position in center
        dialog.geometry("600x500+{}+{}".format(
            self.root_QIUIZZZ.winfo_root_QIUIZZZx() + 100,
            self.root_QIUIZZZ.winfo_root_QIUIZZZy() + 50
        ))
        
        # Main container
        main_container = self.create_frame_3d(dialog, tk.SUNKEN, 2)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        content_frame = tk.Frame(main_container, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Question text
        text_group = self.create_frame_3d(content_frame, tk.RAISED, 1)
        text_group.pack(fill=tk.X, pady=(0,10))
        
        text_inner = tk.Frame(text_group, bg=self.bg_color)
        text_inner.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(text_inner, text="Question Text:", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        
        question_text = tk.Text(text_inner, height=3, font=('MS Sans Serif', 9),
                               relief=tk.SUNKEN, bd=2)
        question_text.pack(fill=tk.X, pady=(2,0))
        
        # Question type
        type_group = self.create_frame_3d(content_frame, tk.RAISED, 1)
        type_group.pack(fill=tk.X, pady=(0,10))
        
        type_inner = tk.Frame(type_group, bg=self.bg_color)
        type_inner.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(type_inner, text="Question Type:", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        
        question_type = tk.StringVar(value="multiple_response")
        type_frame = tk.Frame(type_inner, bg=self.bg_color)
        type_frame.pack(fill=tk.X, pady=(2,0))
        
        tk.Radiobutton(type_frame, text="Multiple Response", variable=question_type, 
                      value="multiple_response", bg=self.bg_color, fg=self.text_color,
                      font=('MS Sans Serif', 9)).pack(side=tk.LEFT)
        tk.Radiobutton(type_frame, text="True/False", variable=question_type, 
                      value="true_false", bg=self.bg_color, fg=self.text_color,
                      font=('MS Sans Serif', 9)).pack(side=tk.LEFT, padx=(20,0))
        tk.Radiobutton(type_frame, text="Open Text", variable=question_type, 
                      value="open_text", bg=self.bg_color, fg=self.text_color,
                      font=('MS Sans Serif', 9)).pack(side=tk.LEFT, padx=(20,0))
        
        # Options frame
        options_group = self.create_frame_3d(content_frame, tk.RAISED, 1)
        options_group.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        
        options_frame = tk.Frame(options_group, bg=self.bg_color)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Variables for options
        option_entries = []
        correct_var = tk.StringVar()
        correct_answer_entry = None
        checkbox_vars = []
        
        def update_options_interface():
            # Clear existing options
            for widget in options_frame.winfo_children():
                widget.destroy()
            option_entries.clear()
            checkbox_vars.clear()  # Clear checkbox vars too
            
            qtype = question_type.get()
            
            if qtype == "multiple_response":
                tk.Label(options_frame, text="Answer Options (multiple can be correct):", 
                        font=('MS Sans Serif', 9, 'bold'),
                        bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
                
                for i in range(4):
                    option_container = self.create_frame_3d(options_frame, tk.SUNKEN, 1)
                    option_container.pack(fill=tk.X, pady=2)
                    
                    frame = tk.Frame(option_container, bg=self.bg_color)
                    frame.pack(fill=tk.X, padx=3, pady=3)
                    
                    var = tk.IntVar()
                    checkbox_vars.append(var)
                    tk.Checkbutton(frame, variable=var, bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)
                    
                    entry = tk.Entry(frame, font=('MS Sans Serif', 9), relief=tk.FLAT, bd=0)
                    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5,0))
                    option_entries.append(entry)
                
                tk.Label(options_frame, text="* Select all correct answers with checkboxes",
                        font=('MS Sans Serif', 8), bg=self.bg_color, fg='#666666').pack(anchor=tk.W, pady=(5,0))
                        
            elif qtype == "true_false":
                tk.Label(options_frame, text="Correct Answer:", font=('MS Sans Serif', 9, 'bold'),
                        bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
                
                tf_container = self.create_frame_3d(options_frame, tk.SUNKEN, 1)
                tf_container.pack(fill=tk.X, pady=5)
                
                tf_frame = tk.Frame(tf_container, bg=self.bg_color)
                tf_frame.pack(fill=tk.X, padx=5, pady=5)
                
                tk.Radiobutton(tf_frame, text="True", variable=correct_var, 
                              value="True", bg=self.bg_color, fg=self.text_color,
                              font=('MS Sans Serif', 9)).pack(side=tk.LEFT)
                tk.Radiobutton(tf_frame, text="False", variable=correct_var, 
                              value="False", bg=self.bg_color, fg=self.text_color,
                              font=('MS Sans Serif', 9)).pack(side=tk.LEFT, padx=(20,0))
                              
            elif qtype == "open_text":
                nonlocal correct_answer_entry
                tk.Label(options_frame, text="Correct Answer:", font=('MS Sans Serif', 9, 'bold'),
                        bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
                
                answer_container = self.create_frame_3d(options_frame, tk.SUNKEN, 1)
                answer_container.pack(fill=tk.X, pady=5)
                
                answer_frame = tk.Frame(answer_container, bg=self.bg_color)
                answer_frame.pack(fill=tk.X, padx=5, pady=5)
                
                correct_answer_entry = tk.Entry(answer_frame, font=('MS Sans Serif', 9), relief=tk.FLAT, bd=0)
                correct_answer_entry.pack(fill=tk.X)
                
                tk.Label(options_frame, text="* Text answers are case-sensitive",
                        font=('MS Sans Serif', 8), bg=self.bg_color, fg='#666666').pack(anchor=tk.W, pady=(5,0))
        
        # Event handler for type change
        def on_type_change():
            update_options_interface()
        
        question_type.trace('w', lambda *args: on_type_change())
        
        # Populate with existing data if editing
        if existing_data:
            question_text.insert('1.0', existing_data['question'])
            question_type.set(existing_data['type'])
            
            dialog.after(100, lambda: populate_existing_data(existing_data))
        
        def populate_existing_data(data):
            if data['type'] == 'multiple_response':
                for i, option in enumerate(data['options']):
                    if i < len(option_entries):
                        option_entries[i].insert(0, option)
                for i in data['correct_answer']:
                    if i < len(checkbox_vars):
                        checkbox_vars[i].set(1)
            elif data['type'] == 'true_false':
                correct_var.set(str(data['correct_answer']))
            elif data['type'] == 'open_text':
                if correct_answer_entry:
                    correct_answer_entry.insert(0, data['correct_answer'])
        
        # Initialize options interface
        update_options_interface()
        
        # Buttons
        buttons_frame = tk.Frame(content_frame, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X, pady=(10,0))
        
        def save_question():
            # Validation
            q_text = question_text.get('1.0', tk.END).strip()
            if not q_text:
                messagebox.showwarning("Validation", "Enter the question text!")
                return
            
            qtype = question_type.get()
            
            # Build question data
            question_data = {
                'question': q_text,
                'type': qtype
            }
            
            if qtype == 'multiple_response':
                options = [entry.get().strip() for entry in option_entries]
                if not all(options):
                    messagebox.showwarning("Validation", "Fill in all options!")
                    return
                
                correct_answers = []
                for i, var in enumerate(checkbox_vars):
                    if var.get():
                        correct_answers.append(i)
                
                if not correct_answers:
                    messagebox.showwarning("Validation", "Select at least one correct answer!")
                    return
                
                question_data['options'] = options
                question_data['correct_answer'] = correct_answers
                
            elif qtype == 'true_false':
                if not correct_var.get():
                    messagebox.showwarning("Validation", "Select the correct answer!")
                    return
                question_data['correct_answer'] = correct_var.get() == 'True'
                
            elif qtype == 'open_text':
                if not correct_answer_entry or not correct_answer_entry.get().strip():
                    messagebox.showwarning("Validation", "Enter the correct answer!")
                    return
                question_data['correct_answer'] = correct_answer_entry.get().strip()
            
            # Save question
            if edit_index is not None:
                self.questions_data[edit_index] = question_data
            else:
                self.questions_data.append(question_data)
            
            self.update_questions_list()
            dialog.destroy()
        
        self.create_button(buttons_frame, "Save", save_question, width=12).pack(side=tk.LEFT)
        self.create_button(buttons_frame, "Cancel", dialog.destroy, width=12).pack(side=tk.RIGHT)
        
    def update_questions_list(self):
        """Update questions list"""
        self.questions_list.delete(0, tk.END)
        for i, q in enumerate(self.questions_data):
            type_text = {
                "multiple_response": "Multiple Response", 
                "true_false": "True/False", 
                "open_text": "Open Text"
            }
            display_text = f"{i+1}. [{type_text[q['type']]}] {q['question'][:50]}..."
            self.questions_list.insert(tk.END, display_text)
    
    def save_quiz(self):
        """Save quiz to database"""
        title = self.title_entry.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        
        if not title:
            messagebox.showwarning("Validation", "Enter quiz title!")
            return
        
        if not self.questions_data:
            messagebox.showwarning("Validation", "Add at least one question!")
            return
        
        timer_enabled = self.timer_var.get()
        timer_seconds = 0
        
        if timer_enabled:
            try:
                timer_seconds = int(self.timer_entry.get())
                if timer_seconds <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showwarning("Validation", "Enter a valid number of seconds for timer!")
                return
        
        # Save to database
        questions_json = json.dumps(self.questions_data)
        
        self.cursor.execute("""
            INSERT INTO quizzes (title, description, timer_enabled, timer_seconds, questions)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, timer_enabled, timer_seconds, questions_json))
        
        self.conn.commit()
        
        messagebox.showinfo("Success", "Quiz saved successfully!")
        self.create_main_interface()
    
    def show_quiz_list(self):
        """Show quiz list"""
        for widget in self.root_QIUIZZZ.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = self.create_frame_3d(self.root_QIUIZZZ, tk.RAISED, 2)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = self.create_label_header(header_frame, "Quiz List")
        title_label.pack(pady=10)
        
        # Main container
        main_container = self.create_frame_3d(self.root_QIUIZZZ, tk.SUNKEN, 2)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        main_frame = tk.Frame(main_container, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Quiz list with scrollbar
        list_container = self.create_frame_3d(main_frame, tk.SUNKEN, 2)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        list_frame = tk.Frame(list_container, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.quiz_listbox = tk.Listbox(list_frame, height=15, font=('MS Sans Serif', 9),
                                      relief=tk.FLAT, bd=0)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.quiz_listbox.yview)
        self.quiz_listbox.config(yscrollcommand=scrollbar.set)
        
        self.quiz_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load quizzes
        self.load_quizzes()
        
        # Buttons
        buttons_frame = tk.Frame(main_frame, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X)
        
        self.create_button(buttons_frame, "Start Quiz", self.start_quiz, width=15).pack(side=tk.LEFT, padx=2)
        self.create_button(buttons_frame, "Edit", self.edit_quiz, width=15).pack(side=tk.LEFT, padx=2)
        self.create_button(buttons_frame, "Delete", self.delete_quiz, width=15).pack(side=tk.LEFT, padx=2)
        self.create_button(buttons_frame, "Back", self.create_main_interface, width=15).pack(side=tk.RIGHT, padx=2)
    
    def load_quizzes(self):
        """Load quizzes from database"""
        self.quiz_listbox.delete(0, tk.END)
        
        self.cursor.execute("""
            SELECT id, title, description, timer_enabled, timer_seconds, 
                   (SELECT COUNT(*) FROM json_each(questions)) as question_count
            FROM quizzes
            ORDER BY created_at DESC
        """)
        
        self.quizzes = self.cursor.fetchall()
        
        for quiz in self.quizzes:
            quiz_id, title, desc, timer_enabled, timer_seconds, q_count = quiz
            timer_text = f" ({timer_seconds}s)" if timer_enabled else ""
            display_text = f"{title} - {q_count} questions{timer_text}"
            self.quiz_listbox.insert(tk.END, display_text)
    
    def start_quiz(self):
        """Start selected quiz"""
        selection = self.quiz_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection", "Select a quiz!")
            return
        
        quiz_data = self.quizzes[selection[0]]
        self.current_quiz = {
            'id': quiz_data[0],
            'title': quiz_data[1],
            'timer_enabled': quiz_data[3],
            'timer_seconds': quiz_data[4]
        }
        
        # Load questions
        self.cursor.execute("SELECT questions FROM quizzes WHERE id = ?", (self.current_quiz['id'],))
        questions_json = self.cursor.fetchone()[0]
        self.current_quiz['questions'] = json.loads(questions_json)
        
        # Initialize quiz variables
        self.current_question = 0
        self.quiz_answers = []
        self.start_time = time.time()
        
        if self.current_quiz['timer_enabled']:
            self.quiz_time_left = self.current_quiz['timer_seconds']
        
        self.show_quiz_question()
    
    def calculate_window_size(self):
        """Calculate optimal window size based on content"""
        question = self.current_quiz['questions'][self.current_question]
        
        # Base height for header, buttons, margins
        base_height = 200
        
        # Calculate question text height (rough estimation)
        question_lines = len(question['question']) // 80 + 1
        question_height = max(60, question_lines * 20)
        
        # Calculate options height
        options_height = 0
        if question['type'] == 'multiple_response':
            for option in question['options']:
                option_lines = len(option) // 70 + 1
                options_height += max(40, option_lines * 25)
        elif question['type'] == 'true_false':
            options_height = 80
        elif question['type'] == 'open_text':
            options_height = 60
        
        total_height = base_height + question_height + options_height
        
        # Ensure minimum and maximum sizes
        height = max(600, min(total_height, self.root_QIUIZZZ.winfo_screenheight() - 100))
        width = max(800, min(1000, self.root_QIUIZZZ.winfo_screenwidth() - 100))
        
        # Center window
        x = (self.root_QIUIZZZ.winfo_screenwidth() - width) // 2
        y = (self.root_QIUIZZZ.winfo_screenheight() - height) // 2
        
        self.root_QIUIZZZ.geometry(f"{width}x{height}+{x}+{y}")
    
    def show_quiz_question(self):
        """Show current quiz question"""
        for widget in self.root_QIUIZZZ.winfo_children():
            widget.destroy()
        
        if self.current_question >= len(self.current_quiz['questions']):
            self.finish_quiz()
            return
        self.calculate_window_size()
        question = self.current_quiz['questions'][self.current_question]
        
        # Header with info
        header_frame = self.create_frame_3d(self.root_QIUIZZZ, tk.RAISED, 2)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        header_inner = tk.Frame(header_frame, bg=self.bg_color)
        header_inner.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = self.create_label_header(header_inner, self.current_quiz['title'], 12)
        title_label.config(justify=tk.LEFT, anchor="w")
        title_label.pack(fill=tk.X, pady=5)

        # Actualizare dinamică a wraplength
        def update_title_wrap(event):
            title_label.config(wraplength=header_inner.winfo_width()-20)

        header_inner.bind('<Configure>', update_title_wrap)
        
        info_frame = tk.Frame(header_inner, bg=self.bg_color)
        info_frame.pack(fill=tk.X, pady=(5,0))
        
        progress_label = tk.Label(info_frame, 
                                 text=f"Question {self.current_question + 1} of {len(self.current_quiz['questions'])}", 
                                 font=('MS Sans Serif', 9),
                                 bg=self.bg_color, fg=self.text_color)
        progress_label.pack(side=tk.LEFT)
        
        # Timer if enabled
        if self.current_quiz['timer_enabled']:
            self.timer_label = tk.Label(info_frame, text=f"Time left: {self.quiz_time_left}s",
                                       font=('MS Sans Serif', 9, 'bold'),
                                       bg=self.bg_color, fg='red')
            self.timer_label.pack(side=tk.RIGHT)
            self.update_timer()
        
        # Question container
        question_container = self.create_frame_3d(self.root_QIUIZZZ, tk.SUNKEN, 2)
        question_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollable question frame
        canvas = tk.Canvas(question_container, bg=self.bg_color, highlightthickness=0)
        question_scrollbar = tk.Scrollbar(question_container, orient=tk.VERTICAL, command=canvas.yview)
        question_frame = tk.Frame(canvas, bg=self.bg_color)

        question_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=question_frame, anchor="nw")
        canvas.configure(yscrollcommand=question_scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  
        question_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                    pass  # Canvas no longer exists

        # Bind mousewheel only to this canvas, not globally
        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Also bind to the frame so it works when hovering over content
        question_frame.bind("<MouseWheel>", _on_mousewheel)

        # Make sure the canvas can receive focus for mouse events
        canvas.focus_set()        
        # Question text
        question_text_container = self.create_frame_3d(question_frame, tk.RAISED, 1)
        question_text_container.pack(fill=tk.X, pady=(0,20))
        
        question_text_frame = tk.Frame(question_text_container, bg=self.bg_color)
        question_text_frame.pack(fill=tk.X, padx=10, pady=10)
        
        question_label = tk.Label(question_text_frame, text=question['question'],
                                 font=('MS Sans Serif', 11),
                                 bg=self.bg_color, fg=self.text_color,
                                 wraplength=700, justify=tk.LEFT)
        question_label.pack()
        
        # Answer options
        answers_container = self.create_frame_3d(question_frame, tk.SUNKEN, 1)
        answers_container.pack(fill=tk.BOTH, expand=True)
        
        answers_frame = tk.Frame(answers_container, bg=self.bg_color)
        answers_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.answer_var = tk.StringVar()
        self.answer_entry = None
        
        if question['type'] == 'multiple_response':
            tk.Label(answers_frame, text="Select all correct answers:", 
                    font=('MS Sans Serif', 10, 'bold'),
                    bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W, pady=(0,5))
            
            self.answer_checkboxes = []
            for i, option in enumerate(question['options']):
                option_container = self.create_frame_3d(answers_frame, tk.RAISED, 1)
                option_container.pack(fill=tk.X, pady=3)
                
                option_frame = tk.Frame(option_container, bg=self.bg_color)
                option_frame.pack(fill=tk.X, padx=5, pady=5)
                
                var = tk.IntVar()
                self.answer_checkboxes.append(var)
                
                cb = tk.Checkbutton(option_frame, text=f"{chr(65+i)}. {option}",
                                   variable=var, font=('MS Sans Serif', 10),
                                   bg=self.bg_color, fg=self.text_color,
                                   wraplength=600, justify=tk.LEFT)
                cb.pack(anchor=tk.W)
                
        elif question['type'] == 'true_false':
            for value, text in [("True", "True"), ("False", "False")]:
                tf_container = self.create_frame_3d(answers_frame, tk.RAISED, 1)
                tf_container.pack(fill=tk.X, pady=3)
                
                tf_frame = tk.Frame(tf_container, bg=self.bg_color)
                tf_frame.pack(fill=tk.X, padx=5, pady=5)
                
                rb = tk.Radiobutton(tf_frame, text=text, variable=self.answer_var, 
                                   value=value, font=('MS Sans Serif', 10),
                                   bg=self.bg_color, fg=self.text_color)
                rb.pack(anchor=tk.W)
                          
        elif question['type'] == 'open_text':
            text_label = tk.Label(answers_frame, text="Your answer:", font=('MS Sans Serif', 10, 'bold'),
                                bg=self.bg_color, fg=self.text_color)
            text_label.pack(anchor=tk.W, pady=(0,5))
            
            text_container = self.create_frame_3d(answers_frame, tk.SUNKEN, 2)
            text_container.pack(fill=tk.X)
            
            text_frame = tk.Frame(text_container, bg=self.bg_color)
            text_frame.pack(fill=tk.X, padx=3, pady=3)
            
            self.answer_entry = tk.Entry(text_frame, font=('MS Sans Serif', 10), 
                                        relief=tk.FLAT, bd=0, width=50)
            self.answer_entry.pack(fill=tk.X)
        
        # Navigation buttons
        nav_container = self.create_frame_3d(self.root_QIUIZZZ, tk.RAISED, 2)
        nav_container.pack(fill=tk.X, padx=10, pady=5)
        
        buttons_frame = tk.Frame(nav_container, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if self.current_question > 0:
            self.create_button(buttons_frame, "< Previous", self.previous_question, width=12).pack(side=tk.LEFT)
        
        next_text = "Finish" if self.current_question == len(self.current_quiz['questions']) - 1 else "Next >"
        self.create_button(buttons_frame, next_text, self.next_question, width=12).pack(side=tk.RIGHT)
    
    def update_timer(self):
        """Update timer"""
        if self.quiz_time_left <= 0:
            messagebox.showwarning("Time's Up", "The time allocated for this quiz has expired!")
            self.finish_quiz()
            return
        
        if hasattr(self, 'timer_label'):
            self.timer_label.config(text=f"Time left: {self.quiz_time_left}s")
            self.quiz_time_left -= 1
            self.timer_after_id = self.root_QIUIZZZ.after(1000, self.update_timer)
    
    def previous_question(self):
        """Go to previous question"""
        if self.current_question > 0:
            self.current_question -= 1
            # Cancel current timer
            if self.timer_after_id:
                self.root_QIUIZZZ.after_cancel(self.timer_after_id)
            self.show_quiz_question()
    
    def next_question(self):
        """Go to next question or finish quiz"""
        # Save current answer
        question = self.current_quiz['questions'][self.current_question]
        user_answer = None
        
        if question['type'] == 'multiple_response':
            selected_answers = []
            for i, var in enumerate(self.answer_checkboxes):
                if var.get():
                    selected_answers.append(i)
            user_answer = selected_answers
        elif question['type'] == 'true_false':
            user_answer = self.answer_var.get() if self.answer_var.get() else None
        elif question['type'] == 'open_text':
            user_answer = self.answer_entry.get().strip() if self.answer_entry else ""
        
        # Check if answer was provided
        if not user_answer:
            if not messagebox.askyesno("No Answer", "You haven't selected/entered an answer. Continue?"):
                return
        
        # Save answer
        if len(self.quiz_answers) <= self.current_question:
            self.quiz_answers.append(user_answer)
        else:
            self.quiz_answers[self.current_question] = user_answer
        
        # Cancel current timer
        if self.timer_after_id:
            self.root_QIUIZZZ.after_cancel(self.timer_after_id)
        
        self.current_question += 1
        self.show_quiz_question()
    
    def finish_quiz(self):
        """Finish quiz and show results"""
        end_time = time.time()
        time_taken = int(end_time - self.start_time)
        
        # Calculate score
        score = 0
        total_questions = len(self.current_quiz['questions'])
        
        for i, question in enumerate(self.current_quiz['questions']):
            if i < len(self.quiz_answers):
                user_answer = self.quiz_answers[i]
                correct_answer = question['correct_answer']
                
                if question['type'] == 'multiple_response':
                    if user_answer and set(user_answer) == set(correct_answer):
                        score += 1
                elif question['type'] == 'true_false':
                    if user_answer and (user_answer == 'True') == correct_answer:
                        score += 1
                elif question['type'] == 'open_text':
                    if user_answer and user_answer.lower() == correct_answer.lower():
                        score += 1
        
        # Save result to database
        self.cursor.execute("""
            INSERT INTO results (quiz_id, quiz_title, score, total_questions, time_taken)
            VALUES (?, ?, ?, ?, ?)
        """, (self.current_quiz['id'], self.current_quiz['title'], score, total_questions, time_taken))
        
        self.conn.commit()
        
        # Show results
        self.show_quiz_results(score, total_questions, time_taken)
    
    def show_quiz_results(self, score, total_questions, time_taken):
        """Show quiz results"""
        for widget in self.root_QIUIZZZ.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = self.create_frame_3d(self.root_QIUIZZZ, tk.RAISED, 2)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = self.create_label_header(header_frame, "Quiz Results")
        title_label.pack(pady=10)
        
        # Results container
        results_container = self.create_frame_3d(self.root_QIUIZZZ, tk.SUNKEN, 2)
        results_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        results_frame = tk.Frame(results_container, bg=self.bg_color)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        percentage = (score / total_questions) * 100
        
        # Quiz info
        info_container = self.create_frame_3d(results_frame, tk.RAISED, 1)
        info_container.pack(fill=tk.X, pady=(0,20))
        
        info_frame = tk.Frame(info_container, bg=self.bg_color)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        quiz_title_label = tk.Label(info_frame, text=f"Quiz: {self.current_quiz['title']}", 
                                   font=('MS Sans Serif', 12, 'bold'),
                                   bg=self.bg_color, fg=self.text_color,
                                   justify=tk.LEFT,
                                   anchor="w")
        quiz_title_label.pack(pady=5, fill=tk.X)

        # Actualizare dinamică a wraplength
        def update_quiz_title_wrap(event):
            quiz_title_label.config(wraplength=info_frame.winfo_width()-20)

        info_frame.bind('<Configure>', update_quiz_title_wrap)
        
        tk.Label(info_frame, text=f"Score: {score}/{total_questions} ({percentage:.1f}%)", 
                font=('MS Sans Serif', 16, 'bold'),
                bg=self.bg_color, fg='darkgreen' if percentage >= 70 else 'darkred').pack(pady=5)
        
        tk.Label(info_frame, text=f"Time used: {time_taken//60}:{time_taken%60:02d}", 
                font=('MS Sans Serif', 11),
                bg=self.bg_color, fg=self.text_color).pack(pady=5)
        
        # Performance message
        if percentage >= 90:
            message = "Excellent! Congratulations!"
        elif percentage >= 70:
            message = "Good! Well done!"
        elif percentage >= 50:
            message = "Satisfactory, you can improve."
        else:
            message = "Study more and try again."
        
        message_container = self.create_frame_3d(results_frame, tk.RAISED, 1)
        message_container.pack(fill=tk.X, pady=(0,20))
        
        message_frame = tk.Frame(message_container, bg=self.bg_color)
        message_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(message_frame, text=message, 
                font=('MS Sans Serif', 12),
                bg=self.bg_color, fg=self.text_color).pack()
        
        # Answer review
        review_container = self.create_frame_3d(results_frame, tk.SUNKEN, 2)
        review_container.pack(fill=tk.BOTH, expand=True)
        
        review_inner = tk.Frame(review_container, bg=self.bg_color)
        review_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(review_inner, text="Answer Review:", 
                font=('MS Sans Serif', 11, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W, pady=(0,5))
        
        # Review text with scrollbar
        text_frame = tk.Frame(review_inner, bg=self.bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        review_text = tk.Text(text_frame, height=10, font=('MS Sans Serif', 9), 
                             state=tk.DISABLED, bg='white', relief=tk.SUNKEN, bd=2)
        review_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=review_text.yview)
        review_text.config(yscrollcommand=review_scrollbar.set)
        
        review_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        review_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate review
        review_content = ""
        for i, question in enumerate(self.current_quiz['questions']):
            user_answer = self.quiz_answers[i] if i < len(self.quiz_answers) else "No answer"
            correct_answer = question['correct_answer']
            
            review_content += f"\n{i+1}. {question['question']}\n"
            
            if question['type'] == 'multiple_response':
                user_text = [question['options'][i] for i in user_answer] if user_answer else ["No answers"]
                correct_text = [question['options'][i] for i in correct_answer]
                review_content += f"   Your answers: {', '.join(user_text)}\n"
                review_content += f"   Correct answers: {', '.join(correct_text)}\n"
            elif question['type'] == 'true_false':
                user_text = "True" if user_answer == "True" else ("False" if user_answer == "False" else "No answer")
                correct_text = "True" if correct_answer else "False"
                review_content += f"   Your answer: {user_text}\n"
                review_content += f"   Correct answer: {correct_text}\n"
            elif question['type'] == 'open_text':
                review_content += f"   Your answer: {user_answer}\n"
                review_content += f"   Correct answer: {correct_answer}\n"
            
            # Mark correct/incorrect
            is_correct = False
            if question['type'] == 'multiple_response':
                is_correct = user_answer and set(user_answer) == set(correct_answer)
            elif question['type'] == 'true_false':
                is_correct = user_answer and (user_answer == 'True') == correct_answer
            elif question['type'] == 'open_text':
                is_correct = user_answer and user_answer.lower() == correct_answer.lower()
            
            review_content += f"   Result: {'Correct' if is_correct else 'Incorrect'}\n\n"
        
        review_text.config(state=tk.NORMAL)
        review_text.insert('1.0', review_content)
        review_text.config(state=tk.DISABLED)
        
        # Bottom buttons
        buttons_container = self.create_frame_3d(self.root_QIUIZZZ, tk.RAISED, 2)
        buttons_container.pack(fill=tk.X, padx=10, pady=5)
        
        buttons_frame = tk.Frame(buttons_container, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.create_button(buttons_frame, "Retry Quiz", lambda: self.start_quiz_by_id(self.current_quiz['id']), width=12).pack(side=tk.LEFT)
        self.create_button(buttons_frame, "Main Menu", self.create_main_interface, width=15).pack(side=tk.RIGHT)
    
    def start_quiz_by_id(self, quiz_id):
        """Start a quiz by ID - fixed version"""
        # Load quiz directly from database
        self.cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        quiz_data = self.cursor.fetchone()
        if not quiz_data:
            messagebox.showerror("Error", "Quiz not found!")
            self.create_main_interface()
            return
        
        self.current_quiz = {
            'id': quiz_data[0],
            'title': quiz_data[1],
            'timer_enabled': quiz_data[3],
            'timer_seconds': quiz_data[4]
        }
        
        questions_json = quiz_data[5]
        self.current_quiz['questions'] = json.loads(questions_json)
        
        self.current_question = 0
        self.quiz_answers = []
        self.start_time = time.time()
        
        if self.current_quiz['timer_enabled']:
            self.quiz_time_left = self.current_quiz['timer_seconds']
        
        self.show_quiz_question()
    
    def edit_quiz(self):
        """Edit selected quiz"""
        selection = self.quiz_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection", "Select a quiz to edit!")
            return
        
        quiz_data = self.quizzes[selection[0]]
        quiz_id = quiz_data[0]
        
        # Load complete quiz data
        self.cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
        quiz = self.cursor.fetchone()
        
        # Create edit interface (similar to create)
        for widget in self.root_QIUIZZZ.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = self.create_frame_3d(self.root_QIUIZZZ, tk.RAISED, 2)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = self.create_label_header(header_frame, "Edit Quiz")
        title_label.pack(pady=10)
        
        # Main form container
        form_container = self.create_frame_3d(self.root_QIUIZZZ, tk.SUNKEN, 2)
        form_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        form_frame = tk.Frame(form_container, bg=self.bg_color)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Quiz title
        title_group = self.create_frame_3d(form_frame, tk.RAISED, 1)
        title_group.pack(fill=tk.X, pady=(0,10))
        
        title_inner = tk.Frame(title_group, bg=self.bg_color)
        title_inner.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(title_inner, text="Quiz Title:", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        self.title_entry = tk.Entry(title_inner, font=('MS Sans Serif', 9), width=60,
                                   relief=tk.SUNKEN, bd=2)
        self.title_entry.pack(pady=(2,0), fill=tk.X)
        self.title_entry.insert(0, quiz[1])  # title
        
        # Description
        desc_group = self.create_frame_3d(form_frame, tk.RAISED, 1)
        desc_group.pack(fill=tk.X, pady=(0,10))
        
        desc_inner = tk.Frame(desc_group, bg=self.bg_color)
        desc_inner.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(desc_inner, text="Description:", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        self.desc_text = tk.Text(desc_inner, height=3, font=('MS Sans Serif', 9),
                                relief=tk.SUNKEN, bd=2)
        self.desc_text.pack(pady=(2,0), fill=tk.X)
        self.desc_text.insert('1.0', quiz[2] or "")  # description
        
        # Timer settings
        timer_group = self.create_frame_3d(form_frame, tk.RAISED, 1)
        timer_group.pack(fill=tk.X, pady=(0,10))
        
        timer_inner = tk.Frame(timer_group, bg=self.bg_color)
        timer_inner.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(timer_inner, text="Timer Settings:", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        
        timer_frame = tk.Frame(timer_inner, bg=self.bg_color)
        timer_frame.pack(fill=tk.X, pady=(2,0))
        
        self.timer_var = tk.IntVar(value=quiz[3])  # timer_enabled
        timer_check = tk.Checkbutton(timer_frame, text="Enable Timer", 
                                   variable=self.timer_var,
                                   bg=self.bg_color, fg=self.text_color,
                                   font=('MS Sans Serif', 9))
        timer_check.pack(side=tk.LEFT)
        
        tk.Label(timer_frame, text="Seconds:", font=('MS Sans Serif', 9),
                bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(20,5))
        self.timer_entry = tk.Entry(timer_frame, width=10, font=('MS Sans Serif', 9),
                                   relief=tk.SUNKEN, bd=2)
        self.timer_entry.pack(side=tk.LEFT)
        self.timer_entry.insert(0, str(quiz[4]))  # timer_seconds
        
        # Questions section
        questions_group = self.create_frame_3d(form_frame, tk.RAISED, 1)
        questions_group.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        
        questions_inner = tk.Frame(questions_group, bg=self.bg_color)
        questions_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(questions_inner, text="Questions:", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
        
        # Questions list with scrollbar
        list_frame = tk.Frame(questions_inner, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(2,0))
        
        self.questions_list = tk.Listbox(list_frame, height=8, font=('MS Sans Serif', 9),
                                        relief=tk.SUNKEN, bd=2)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.questions_list.yview)
        self.questions_list.config(yscrollcommand=scrollbar.set)
        
        self.questions_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load existing questions
        self.questions_data = json.loads(quiz[5])  # questions
        self.update_questions_list()
        
        # Question buttons
        questions_buttons_frame = tk.Frame(questions_inner, bg=self.bg_color)
        questions_buttons_frame.pack(fill=tk.X, pady=(5,0))
        
        self.create_button(questions_buttons_frame, "Add Question", self.add_question, width=15).pack(side=tk.LEFT, padx=2)
        self.create_button(questions_buttons_frame, "Edit", self.edit_question, width=15).pack(side=tk.LEFT, padx=2)
        self.create_button(questions_buttons_frame, "Delete", self.delete_question, width=15).pack(side=tk.LEFT, padx=2)
        
        # Bottom buttons
        bottom_frame = tk.Frame(form_frame, bg=self.bg_color)
        bottom_frame.pack(fill=tk.X, pady=(10,0))
        
        self.create_button(bottom_frame, "Save Changes", lambda: self.update_quiz(quiz_id), width=20).pack(side=tk.LEFT)
        self.create_button(bottom_frame, "Cancel", self.show_quiz_list, width=15).pack(side=tk.RIGHT)
    
    def update_quiz(self, quiz_id):
        """Update quiz in database"""
        title = self.title_entry.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        
        if not title:
            messagebox.showwarning("Validation", "Enter quiz title!")
            return
        
        if not self.questions_data:
            messagebox.showwarning("Validation", "Quiz must have at least one question!")
            return
        
        timer_enabled = self.timer_var.get()
        timer_seconds = 0
        
        if timer_enabled:
            try:
                timer_seconds = int(self.timer_entry.get())
                if timer_seconds <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showwarning("Validation", "Enter a valid number of seconds for timer!")
                return
        
        # Update in database
        questions_json = json.dumps(self.questions_data)
        
        self.cursor.execute("""
            UPDATE quizzes 
            SET title = ?, description = ?, timer_enabled = ?, timer_seconds = ?, questions = ?
            WHERE id = ?
        """, (title, description, timer_enabled, timer_seconds, questions_json, quiz_id))
        
        self.conn.commit()
        
        messagebox.showinfo("Success", "Quiz updated successfully!")
        self.show_quiz_list()
    
    def delete_quiz(self):
        """Delete selected quiz"""
        selection = self.quiz_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection", "Select a quiz to delete!")
            return
        
        quiz_data = self.quizzes[selection[0]]
        quiz_title = quiz_data[1]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{quiz_title}'?\n\nThis action cannot be undone."):
            quiz_id = quiz_data[0]
            
            # Delete quiz and its results
            self.cursor.execute("DELETE FROM results WHERE quiz_id = ?", (quiz_id,))
            self.cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Quiz deleted successfully!")
            self.load_quizzes()  # Refresh list
    
    def show_results(self):
        """Show quiz results history"""
        for widget in self.root_QIUIZZZ.winfo_children():
            widget.destroy()
        
        # Header
        header_frame = self.create_frame_3d(self.root_QIUIZZZ, tk.RAISED, 2)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = self.create_label_header(header_frame, "Quiz Results History")
        title_label.pack(pady=10)
        
        # Main container
        main_container = self.create_frame_3d(self.root_QIUIZZZ, tk.SUNKEN, 2)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        main_frame = tk.Frame(main_container, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Statistics frame
        stats_container = self.create_frame_3d(main_frame, tk.RAISED, 1)
        stats_container.pack(fill=tk.X, pady=(0, 10))
        
        stats_frame = tk.Frame(stats_container, bg=self.bg_color)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Load statistics
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_attempts,
                AVG(CAST(score AS FLOAT) / total_questions * 100) as avg_percentage,
                MAX(CAST(score AS FLOAT) / total_questions * 100) as best_percentage,
                AVG(time_taken) as avg_time
            FROM results
        """)
        stats = self.cursor.fetchone()
        
        if stats[0] > 0:  # If there are results
            tk.Label(stats_frame, text="Overall Statistics:", font=('MS Sans Serif', 11, 'bold'),
                    bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W)
            
            stats_text = f"Total Quiz Attempts: {stats[0]}  |  "
            stats_text += f"Average Score: {stats[1]:.1f}%  |  "
            stats_text += f"Best Score: {stats[2]:.1f}%  |  "
            stats_text += f"Average Time: {int(stats[3])//60}:{int(stats[3])%60:02d}"
            
            tk.Label(stats_frame, text=stats_text, font=('MS Sans Serif', 9),
                    bg=self.bg_color, fg=self.text_color).pack(anchor=tk.W, pady=(5,0))
        else:
            tk.Label(stats_frame, text="No quiz results found. Complete some quizzes first!",
                    font=('MS Sans Serif', 10),
                    bg=self.bg_color, fg=self.text_color).pack()
        
        # Results list container
        list_container = self.create_frame_3d(main_frame, tk.SUNKEN, 2)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        list_frame = tk.Frame(list_container, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Create Treeview for better formatting
        columns = ('Quiz', 'Score', 'Percentage', 'Time', 'Date')
        
        self.results_tree = tk.Frame(list_frame, bg=self.bg_color)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = self.create_frame_3d(self.results_tree, tk.RAISED, 1)
        header_frame.pack(fill=tk.X)
        
        header_inner = tk.Frame(header_frame, bg=self.bg_color)
        header_inner.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Label(header_inner, text="Data", font=('MS Sans Serif', 9, 'bold'),
                bg=self.bg_color, fg=self.text_color, width=25, anchor='w').pack(side=tk.LEFT, padx=2)
        # tk.Label(header_inner, text="Score", font=('MS Sans Serif', 9, 'bold'),
                # bg=self.bg_color, fg=self.text_color, width=10, anchor='w').pack(side=tk.LEFT, padx=2)
        # tk.Label(header_inner, text="Percentage", font=('MS Sans Serif', 9, 'bold'),
                # bg=self.bg_color, fg=self.text_color, width=10, anchor='w').pack(side=tk.LEFT, padx=2)
        # tk.Label(header_inner, text="Time", font=('MS Sans Serif', 9, 'bold'),
                # bg=self.bg_color, fg=self.text_color, width=8, anchor='w').pack(side=tk.LEFT, padx=2)
        # tk.Label(header_inner, text="Date", font=('MS Sans Serif', 9, 'bold'),
                # bg=self.bg_color, fg=self.text_color, width=15, anchor='w').pack(side=tk.LEFT, padx=2)
        
        # Results list with scrollbar
        results_list_frame = tk.Frame(self.results_tree, bg=self.bg_color)
        results_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview for proper table format
        columns = ('quiz', 'score', 'percentage', 'time', 'date')
        self.results_tree = ttk.Treeview(results_list_frame, columns=columns, show='headings', height=15)

        # Define column headings and widths
        self.results_tree.heading('quiz', text='Quiz Title')
        self.results_tree.heading('score', text='Score')
        self.results_tree.heading('percentage', text='Percentage')
        self.results_tree.heading('time', text='Time')
        self.results_tree.heading('date', text='Date')

        self.results_tree.column('quiz', width=250, anchor='w')
        self.results_tree.column('score', width=80, anchor='center')
        self.results_tree.column('percentage', width=80, anchor='center')
        self.results_tree.column('time', width=60, anchor='center')
        self.results_tree.column('date', width=120, anchor='center')

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar fix (legat de tree, nu de listbox inexistent)
        results_scrollbar = tk.Scrollbar(results_list_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)

        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        
        # Load results
        self.load_results()
        
        # Buttons
        buttons_frame = tk.Frame(main_frame, bg=self.bg_color)
        buttons_frame.pack(fill=tk.X)
        
        self.create_button(buttons_frame, "Clear All Results", self.clear_results, width=20).pack(side=tk.LEFT, padx=2)
        self.create_button(buttons_frame, "Back", self.create_main_interface, width=15).pack(side=tk.RIGHT, padx=2)
    
    def load_results(self):
        """Load results from database"""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.cursor.execute("""
            SELECT quiz_title, score, total_questions, time_taken, completed_at
            FROM results
            ORDER BY completed_at DESC
        """)
        
        results = self.cursor.fetchall()
        
        for result in results:
            quiz_title, score, total_questions, time_taken, completed_at = result
            percentage = (score / total_questions) * 100
            
            time_str = f"{time_taken//60}:{time_taken%60:02d}"
            
            try:
                date_obj = datetime.strptime(completed_at, '%Y-%m-%d %H:%M:%S')
                date_str = date_obj.strftime('%Y-%m-%d %H:%M')
            except:
                date_str = completed_at[:16]
            
            # Insert into treeview
            self.results_tree.insert('', 'end', values=(
                quiz_title,
                f"{score}/{total_questions}",
                f"{percentage:.1f}%",
                time_str,
                date_str
            ))
    
    def clear_results(self):
        """Clear all results"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all quiz results?\n\nThis action cannot be undone."):
            self.cursor.execute("DELETE FROM results")
            self.conn.commit()
            messagebox.showinfo("Success", "All results cleared!")
            self.load_results()  # Refresh list
    
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main function to start the application"""
    root_QIUIZZZ = tk.Tk()
    app = QuizApp(root_QIUIZZZ)
    
    # Center window on screen
    root_QIUIZZZ.update_idletasks()
    width = root_QIUIZZZ.winfo_width()
    height = root_QIUIZZZ.winfo_height()
    x = (root_QIUIZZZ.winfo_screenwidth() // 2) - (width // 2)
    y = (root_QIUIZZZ.winfo_screenheight() // 2) - (height // 2)
    root_QIUIZZZ.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the application
    try:
        root_QIUIZZZ.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(app, 'conn'):
            app.conn.close()

if __name__ == "__main__":
    main()