def OUTLOOK():
    from datetime import datetime
    import os
    import tkinter as tk
    from tkinter import messagebox
    import sqlite3

    class RetroEmailClient:
        def __init__(self, rootmailoutlook):
            self.rootmailoutlook = rootmailoutlook
            self.rootmailoutlook.title("Multiapp 95 Professional Mail Express")
            self.rootmailoutlook.geometry("1000x600")
            self.rootmailoutlook.configure(bg="#c0c0c0")
            
            self.db_path = os.path.join("Config", "emails.db")
            self.current_folder = "Inbox"
            self.folder_labels = {}
            self.show_folder_counts = True
            
            reply_to = {
                "from": "suport@muap.ro",
                "to": "Me",
                "subject": "Re: Tips and Tricks",
                "date": datetime.now().strftime("%a %m/%d/%Y %I:%M %p"),
                "body": "Quick steps after you closing this window:\n\n• Click Go to user handbook button to close this window\n• In that section, you will find a user manual for Multiapp 95 Professional.\n• Read each menu and follow the documentation at every step.\n\nIt is very important to use this software in the configured folder and not to delete anything!\n\nMuap Support Team"
            }
            
            self.initial_emails = [
                {
                    "from": "tudor.marmureanu@muap.ro",
                    "to": "Me", 
                    "subject": "Welcome to the team!",
                    "date": datetime.now().strftime("%a %m/%d/%Y %I:%M %p"),
                    "body": "Welcome to our team and thank you for choosing our services! We're excited to have you on board.\n\nPlease find attached your user handbook.\n\nBest regards,\nTudor Marmureanu\nMuap Chairman"
                },
                {
                    "from": "suport@muap.ro",
                    "to": "Me",
                    "subject": "Re: Tips and Tricks",
                    "date": datetime.now().strftime("%a %m/%d/%Y %I:%M %p"),
                    "body": (
                        f"Note: If something seems to not be working properly, use at least one of the two self-repair features. "
                        f"You can find more details in the user handbook.\n\nMuap Support Team\n\n\n"
                        f"--- Original Message ---\n"
                        f"From: {reply_to['from']}\n"
                        f"To: {reply_to['to']}\n"
                        f"Subject: {reply_to['subject']}\n"
                        f"Date: {reply_to['date']}\n\n"
                        f"{reply_to['body']}"
                    )
                },
                {
                    "from": "suport@muap.ro",
                    "to": "Me",
                    "subject": "Tips and Tricks",
                    "date": datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), 
                    "body": "Quick steps after you closing this window:\n\n• Click Go to user handbook button to close this window\n• In that section, you will find a user manual for Multiapp 95 Professional.\n• Read each menu and follow the documentation at every step.\n\nIt is very important to use this software in the configured folder and not to delete anything!\n\nMuap Support Team"
                }
            ]
            
            self.emails = []
            self.current_email = None

            self.setup_ui()
            self.init_database()
            self.load_emails_from_db('Inbox')
            
        def init_database(self):
            # Creează directorul Config dacă nu există
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_addr TEXT,
                    to_addr TEXT,
                    subject TEXT,
                    date TEXT,
                    body TEXT,
                    folder TEXT DEFAULT 'Inbox',
                    is_favorite INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
            
            cursor.execute("SELECT COUNT(*) FROM emails WHERE folder='Inbox'")
            if cursor.fetchone()[0] == 0:
                for email in self.initial_emails:
                    cursor.execute('''
                        INSERT INTO emails (from_addr, to_addr, subject, date, body, folder)
                        VALUES (?, ?, ?, ?, ?, 'Inbox')
                    ''', (email['from'], email['to'], email['subject'], email['date'], email['body']))
                conn.commit()
            
            conn.close()
            
        def setup_ui(self):
            menubar = tk.Menu(self.rootmailoutlook, bg="#c0c0c0", relief="raised", bd=1)
            self.rootmailoutlook.config(menu=menubar)
            
            file_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="New Message", command=self.new_message)
            file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.rootmailoutlook.destroy)
            
            edit_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
            menubar.add_cascade(label="Edit", menu=edit_menu)
            edit_menu.add_command(label="Select All", command=lambda: None)
            edit_menu.add_command(label="Copy", command=lambda: None)
            edit_menu.add_command(label="Paste", command=lambda: None)
            
            view_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
            menubar.add_cascade(label="View", menu=view_menu)
            view_menu.add_command(label="Refresh", command=self.refresh_emails)
            
            tools_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
            menubar.add_cascade(label="Tools", menu=tools_menu)
            tools_menu.add_command(label="Options...", command=self.show_options)
            
            help_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
            menubar.add_cascade(label="Help", menu=help_menu)
            help_menu.add_command(label="About Mail Express", command=self.show_about)
            
            toolbar = tk.Frame(self.rootmailoutlook, bg="#c0c0c0", relief="raised", bd=1)
            toolbar.pack(fill="x", padx=2, pady=2)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, "font": ("MS Sans Serif", 8)}
            
            tk.Button(toolbar, text="Send/Recv", command=self.send_receive, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="New Msg", command=self.new_message, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Reply", command=self.reply_message, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Forward", command=self.forward_message, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Delete", command=self.delete_message, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="To user handbook", command=self.rootmailoutlook.destroy, **btn_style).pack(side="left", padx=10)
            
            main_frame = tk.Frame(self.rootmailoutlook, bg="#c0c0c0")
            main_frame.pack(fill="both", expand=True, padx=4, pady=4)
            
            left_panel = tk.Frame(main_frame, bg="#c0c0c0", relief="sunken", bd=2, width=150)
            left_panel.pack(side="left", fill="y", padx=(0, 2))
            left_panel.pack_propagate(False)
            
            tk.Label(left_panel, text="Folders", bg="#c0c0c0", font=("MS Sans Serif", 8, "bold")).pack(anchor="w", padx=5, pady=2)
            
            folders_frame = tk.Frame(left_panel, bg="white", relief="sunken", bd=1)
            folders_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
            
            folders = ["Inbox", "Sent Items", "Favorites", "Drafts"]
            
            for folder in folders:
                folder_btn = tk.Label(folders_frame, text=f"  {folder}", bg="white", anchor="w", 
                                    font=("MS Sans Serif", 8), cursor="hand2")
                folder_btn.pack(fill="x")
                folder_btn.bind("<Button-1>", lambda e, f=folder: self.switch_folder(f))
                if folder == "Inbox":
                    folder_btn.configure(bg="#316ac5", fg="white")
                self.folder_labels[folder] = folder_btn
            
            middle_panel = tk.Frame(main_frame, bg="#c0c0c0", relief="sunken", bd=2)
            middle_panel.pack(side="left", fill="both", expand=True, padx=(2, 2))
            
            self.folder_title_label = tk.Label(middle_panel, text="Inbox", bg="#c0c0c0", font=("MS Sans Serif", 8, "bold"))
            self.folder_title_label.pack(anchor="w", padx=5, pady=2)
            
            headers_frame = tk.Frame(middle_panel, bg="#c0c0c0", relief="raised", bd=1)
            headers_frame.pack(fill="x", padx=2)
            
            tk.Label(headers_frame, text="From", bg="#c0c0c0", relief="raised", bd=1, 
                    font=("MS Sans Serif", 8), width=18).pack(side="left")
            tk.Label(headers_frame, text="Subject", bg="#c0c0c0", relief="raised", bd=1, 
                    font=("MS Sans Serif", 8), width=25).pack(side="left")
            tk.Label(headers_frame, text="Received", bg="#c0c0c0", relief="raised", bd=1, 
                    font=("MS Sans Serif", 8), width=15).pack(side="left")
            
            list_container = tk.Frame(middle_panel, bg="white")
            list_container.pack(fill="both", expand=True, padx=2, pady=2)
            
            scrollbar = tk.Scrollbar(list_container, bg="#c0c0c0")
            scrollbar.pack(side="right", fill="y")
            
            self.email_listbox = tk.Listbox(list_container, bg="white", font=("MS Sans Serif", 8),
                                           yscrollcommand=scrollbar.set, selectmode="single")
            self.email_listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=self.email_listbox.yview)
            
            self.email_listbox.bind("<Double-Button-1>", self.on_email_double_click)
            self.email_listbox.bind("<<ListboxSelect>>", self.on_email_select)
            self.email_listbox.bind("<Button-3>", self.show_context_menu)
            
            
            right_panel = tk.Frame(main_frame, bg="#c0c0c0", relief="sunken", bd=2)
            right_panel.pack(side="right", fill="both", expand=True, padx=(2, 0))
            
            tk.Label(right_panel, text="Message Preview", bg="#c0c0c0", font=("MS Sans Serif", 8, "bold")).pack(anchor="w", padx=5, pady=2)
            
            header_frame = tk.Frame(right_panel, bg="#f0f0f0", relief="raised", bd=1)
            header_frame.pack(fill="x", padx=2, pady=2)
            
            self.from_label = tk.Label(header_frame, text="From: ", bg="#f0f0f0", anchor="w", 
                                      font=("MS Sans Serif", 8))
            self.from_label.pack(fill="x", padx=5, pady=1)
            
            self.to_label = tk.Label(header_frame, text="To: ", bg="#f0f0f0", anchor="w", 
                                    font=("MS Sans Serif", 8))
            self.to_label.pack(fill="x", padx=5, pady=1)
            
            self.subject_label = tk.Label(header_frame, text="Subject: ", bg="#f0f0f0", anchor="w", 
                                         font=("MS Sans Serif", 8, "bold"))
            self.subject_label.pack(fill="x", padx=5, pady=1)
            
            self.date_label = tk.Label(header_frame, text="Date: ", bg="#f0f0f0", anchor="w", 
                                      font=("MS Sans Serif", 8))
            self.date_label.pack(fill="x", padx=5, pady=1)
            
            body_container = tk.Frame(right_panel, bg="#c0c0c0")
            body_container.pack(fill="both", expand=True, padx=2, pady=2)
            
            body_scrollbar = tk.Scrollbar(body_container, bg="#c0c0c0")
            body_scrollbar.pack(side="right", fill="y")
            
            self.email_body = tk.Text(body_container, bg="white", font=("MS Sans Serif", 9),
                                     yscrollcommand=body_scrollbar.set, wrap="word", state="disabled")
            self.email_body.pack(side="left", fill="both", expand=True)
            body_scrollbar.config(command=self.email_body.yview)
            
            status_bar = tk.Frame(self.rootmailoutlook, bg="#c0c0c0", relief="sunken", bd=1)
            status_bar.pack(fill="x", side="bottom")
            
            self.status_label = tk.Label(status_bar, text="", bg="#c0c0c0", 
                                        anchor="w", font=("MS Sans Serif", 8))
            self.status_label.pack(side="left", padx=5, pady=2)
            
            self.refresh_emails()
            
        def show_context_menu(self, event):
            try:
                self.email_listbox.selection_clear(0, tk.END)
                self.email_listbox.selection_set(self.email_listbox.nearest(event.y))
                self.email_listbox.activate(self.email_listbox.nearest(event.y))
                self.on_email_select()
                
                # Recreează meniul contextual în funcție de folder
                self.context_menu = tk.Menu(self.rootmailoutlook, tearoff=0, bg="#c0c0c0")
                
                # Afișează "Open/Edit" doar în Drafts
                if self.current_folder == "Drafts":
                    self.context_menu.add_command(label="Open/Edit", command=self.open_or_edit_email)
                    self.context_menu.add_separator()
                
                self.context_menu.add_command(label="Reply", command=self.reply_message)
                self.context_menu.add_command(label="Forward", command=self.forward_message)
                self.context_menu.add_separator()
                self.context_menu.add_command(label="Mark as Favorite", command=self.toggle_favorite)
                self.context_menu.add_separator()
                self.context_menu.add_command(label="Delete", command=self.delete_message)
                
                self.context_menu.post(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
                
        def load_emails_from_db(self, folder):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if folder == "Favorites":
                cursor.execute("SELECT * FROM emails WHERE is_favorite=1 ORDER BY id DESC")
            else:
                cursor.execute("SELECT * FROM emails WHERE folder=? ORDER BY id DESC", (folder,))
            
            rows = cursor.fetchall()
            conn.close()
            
            self.emails = []
            for row in rows:
                self.emails.append({
                    'id': row[0],
                    'from': row[1],
                    'to': row[2],
                    'subject': row[3],
                    'date': row[4],
                    'body': row[5],
                    'folder': row[6],
                    'is_favorite': row[7]
                })
            
            self.refresh_emails()
            self.update_folder_counts()
            
        def update_folder_counts(self):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Contorizează emailurile pentru fiecare folder
            cursor.execute("SELECT COUNT(*) FROM emails WHERE folder='Inbox'")
            inbox_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM emails WHERE folder='Sent Items'")
            sent_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM emails WHERE folder='Drafts'")
            drafts_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM emails WHERE is_favorite=1")
            fav_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Actualizează textul fiecărui folder
            if self.show_folder_counts:
                self.folder_labels["Inbox"].config(text=f"  Inbox ({inbox_count})")
                self.folder_labels["Sent Items"].config(text=f"  Sent Items ({sent_count})")
                self.folder_labels["Drafts"].config(text=f"  Drafts ({drafts_count})")
                self.folder_labels["Favorites"].config(text=f"  Favorites ({fav_count})")
            else:
                self.folder_labels["Inbox"].config(text="  Inbox")
                self.folder_labels["Sent Items"].config(text="  Sent Items")
                self.folder_labels["Drafts"].config(text="  Drafts")
                self.folder_labels["Favorites"].config(text="  Favorites")
            
        def switch_folder(self, folder):
            self.current_folder = folder
            self.folder_title_label.config(text=folder)
            
            for fname, label in self.folder_labels.items():
                if fname == folder:
                    label.configure(bg="#316ac5", fg="white")
                else:
                    label.configure(bg="white", fg="black")
            
            self.load_emails_from_db(folder)
            self.update_folder_counts()
            
        def toggle_favorite(self):
            selection = self.email_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an email to mark as favorite.")
                return
            
            index = selection[0]
            if index < len(self.emails):
                email = self.emails[index]
                email_id = email.get('id')
                
                if email_id:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    new_fav_status = 0 if email['is_favorite'] else 1
                    cursor.execute("UPDATE emails SET is_favorite=? WHERE id=?", (new_fav_status, email_id))
                    conn.commit()
                    conn.close()
                    
                    self.load_emails_from_db(self.current_folder)
                    msg = "Email marked as favorite!" if new_fav_status else "Email unmarked as favorite!"
                    messagebox.showinfo("Favorite", msg)
            
        def refresh_emails(self):
            self.email_listbox.delete(0, tk.END)
            for i, email in enumerate(self.emails):
                from_part = email["from"][:16].ljust(16)
                subject_part = email["subject"][:23].ljust(23)
                date_part = email["date"][:13]
                
                display_text = f"{from_part} {subject_part} {date_part}"
                self.email_listbox.insert(tk.END, display_text)
            
            count = len(self.emails)
            self.status_label.config(text=f"{count} message(s), 0 unread")
                
            if self.emails:
                self.email_listbox.select_set(0)
                self.show_email_preview(0)
        
        def on_email_select(self, event=None):
            selection = self.email_listbox.curselection()
            if selection:
                self.show_email_preview(selection[0])
                
        def on_email_double_click(self, event=None):
            if self.current_folder == "Drafts":
                self.open_draft()
            else:
                self.on_email_select(event)

        def open_or_edit_email(self):
            if self.current_folder == "Drafts":
                self.open_draft()
            else:
                messagebox.showinfo("Open Email", "Email opened in preview pane.")
        
        def show_email_preview(self, index):
            if 0 <= index < len(self.emails):
                email = self.emails[index]
                self.current_email = email
                
                self.from_label.config(text=f"From: {email['from']}")
                self.to_label.config(text=f"To: {email['to']}")
                self.subject_label.config(text=f"Subject: {email['subject']}")
                self.date_label.config(text=f"Date: {email['date']}")
                
                self.email_body.config(state="normal")
                self.email_body.delete(1.0, tk.END)
                self.email_body.insert(1.0, email['body'])
                self.email_body.config(state="disabled")
        
        def new_message(self):
            self.open_compose_window()
        
        def reply_message(self):
            if self.current_email:
                self.open_compose_window(reply_to=self.current_email)
            else:
                messagebox.showwarning("No Selection", "Please select an email to reply to.")
        
        def forward_message(self):
            if self.current_email:
                self.open_compose_window(forward=self.current_email)
            else:
                messagebox.showwarning("No Selection", "Please select an email to forward.")
        
        def open_compose_window(self, reply_to=None, forward=None):
            compose_window = tk.Toplevel(self.rootmailoutlook)
            compose_window.title("New Message")
            compose_window.geometry("600x400")
            compose_window.configure(bg="#c0c0c0")
            compose_window.resizable(True, True)
            
            toolbar = tk.Frame(compose_window, bg="#c0c0c0", relief="raised", bd=1)
            toolbar.pack(fill="x", padx=2, pady=2)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, "font": ("MS Sans Serif", 8)}
            tk.Button(toolbar, text="Send", command=lambda: self.send_message(compose_window), **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Save Draft", command=lambda: self.save_draft(compose_window), **btn_style).pack(side="left", padx=2)
            
            headers_frame = tk.Frame(compose_window, bg="#c0c0c0")
            headers_frame.pack(fill="x", padx=5, pady=5)
            
            tk.Label(headers_frame, text="To:", bg="#c0c0c0", font=("MS Sans Serif", 8)).grid(row=0, column=0, sticky="w", padx=(0, 5))
            to_entry = tk.Entry(headers_frame, font=("MS Sans Serif", 9))
            to_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
            
            tk.Label(headers_frame, text="Subject:", bg="#c0c0c0", font=("MS Sans Serif", 8)).grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
            subject_entry = tk.Entry(headers_frame, font=("MS Sans Serif", 9))
            subject_entry.grid(row=1, column=1, sticky="ew", pady=2)
            
            headers_frame.columnconfigure(1, weight=1)
            
            body_frame = tk.Frame(compose_window, bg="#c0c0c0")
            body_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            body_scrollbar = tk.Scrollbar(body_frame, bg="#c0c0c0")
            body_scrollbar.pack(side="right", fill="y")
            
            body_text = tk.Text(body_frame, font=("MS Sans Serif", 9), yscrollcommand=body_scrollbar.set)
            body_text.pack(side="left", fill="both", expand=True)
            body_scrollbar.config(command=body_text.yview)
            
            if reply_to:
                to_entry.insert(0, reply_to["from"])
                subject_entry.insert(0, f"Re: {reply_to['subject']}")
                body_text.insert(1.0, f"\n\n--- Original Message ---\nFrom: {reply_to['from']}\nDate: {reply_to['date']}\nSubject: {reply_to['subject']}\n\n{reply_to['body']}")
            elif forward:
                subject_entry.insert(0, f"Fwd: {forward['subject']}")
                body_text.insert(1.0, f"\n\n--- Forwarded Message ---\nFrom: {forward['from']}\nTo: {forward['to']}\nDate: {forward['date']}\nSubject: {forward['subject']}\n\n{forward['body']}")
            
            compose_window.to_entry = to_entry
            compose_window.subject_entry = subject_entry
            compose_window.body_text = body_text
            compose_window.draft_id = None
        
        def send_message(self, compose_window):
            to = compose_window.to_entry.get()
            subject = compose_window.subject_entry.get()
            body = compose_window.body_text.get(1.0, tk.END)
            
            if not to or not subject:
                messagebox.showwarning("Incomplete", "Please fill in To and Subject fields.")
                return
            
            import getpass
            current_user = getpass.getuser()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Salvează în Sent Items
            cursor.execute('''
                INSERT INTO emails (from_addr, to_addr, subject, date, body, folder)
                VALUES (?, ?, ?, ?, ?, 'Sent Items')
            ''', ("Me", to, subject, datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), body))
            
            # Dacă destinatarul este "Me", "me" sau numele utilizatorului, adaugă și în Inbox
            if to.lower() == "me" or to.lower() == current_user.lower():
                cursor.execute('''
                    INSERT INTO emails (from_addr, to_addr, subject, date, body, folder)
                    VALUES (?, ?, ?, ?, ?, 'Inbox')
                ''', ("Me", "Me", subject, datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), body))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Message Sent", f"Message sent to: {to}")
            compose_window.destroy()
            
            self.load_emails_from_db(self.current_folder)
            
        def save_draft(self, compose_window):
            to = compose_window.to_entry.get()
            subject = compose_window.subject_entry.get()
            body = compose_window.body_text.get(1.0, tk.END)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            draft_id = getattr(compose_window, 'draft_id', None)
            
            if draft_id:
                # Actualizează draft-ul existent
                cursor.execute('''
                    UPDATE emails 
                    SET to_addr=?, subject=?, body=?, date=?
                    WHERE id=?
                ''', (to, subject, body, datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), draft_id))
                msg = "Draft updated successfully!"
            else:
                # Creează un draft nou
                cursor.execute('''
                    INSERT INTO emails (from_addr, to_addr, subject, date, body, folder)
                    VALUES (?, ?, ?, ?, ?, 'Drafts')
                ''', ("Me", to, subject, datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), body))
                msg = "Draft saved successfully!"
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Draft Saved", msg)
            compose_window.destroy()
            
            self.load_emails_from_db(self.current_folder)
            
        def open_draft(self):
            if not self.current_email:
                messagebox.showwarning("No Selection", "Please select a draft to edit.")
                return
            
            if self.current_folder != "Drafts":
                messagebox.showwarning("Not a Draft", "You can only edit drafts from the Drafts folder.")
                return
            
            draft = self.current_email
            
            compose_window = tk.Toplevel(self.rootmailoutlook)
            compose_window.title("Edit Draft")
            compose_window.geometry("600x400")
            compose_window.configure(bg="#c0c0c0")
            compose_window.resizable(True, True)
            
            toolbar = tk.Frame(compose_window, bg="#c0c0c0", relief="raised", bd=1)
            toolbar.pack(fill="x", padx=2, pady=2)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, "font": ("MS Sans Serif", 8)}
            tk.Button(toolbar, text="Send", command=lambda: self.send_draft(compose_window), **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Save Draft", command=lambda: self.save_draft(compose_window), **btn_style).pack(side="left", padx=2)
            
            headers_frame = tk.Frame(compose_window, bg="#c0c0c0")
            headers_frame.pack(fill="x", padx=5, pady=5)
            
            tk.Label(headers_frame, text="To:", bg="#c0c0c0", font=("MS Sans Serif", 8)).grid(row=0, column=0, sticky="w", padx=(0, 5))
            to_entry = tk.Entry(headers_frame, font=("MS Sans Serif", 9))
            to_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
            to_entry.insert(0, draft['to'])
            
            tk.Label(headers_frame, text="Subject:", bg="#c0c0c0", font=("MS Sans Serif", 8)).grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
            subject_entry = tk.Entry(headers_frame, font=("MS Sans Serif", 9))
            subject_entry.grid(row=1, column=1, sticky="ew", pady=2)
            subject_entry.insert(0, draft['subject'])
            
            headers_frame.columnconfigure(1, weight=1)
            
            body_frame = tk.Frame(compose_window, bg="#c0c0c0")
            body_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            body_scrollbar = tk.Scrollbar(body_frame, bg="#c0c0c0")
            body_scrollbar.pack(side="right", fill="y")
            
            body_text = tk.Text(body_frame, font=("MS Sans Serif", 9), yscrollcommand=body_scrollbar.set)
            body_text.pack(side="left", fill="both", expand=True)
            body_scrollbar.config(command=body_text.yview)
            body_text.insert(1.0, draft['body'])
            
            compose_window.to_entry = to_entry
            compose_window.subject_entry = subject_entry
            compose_window.body_text = body_text
            compose_window.draft_id = draft['id']

        def send_draft(self, compose_window):
            # Trimite draft-ul și îl șterge din Drafts
            draft_id = getattr(compose_window, 'draft_id', None)
            
            if draft_id:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM emails WHERE id=?", (draft_id,))
                conn.commit()
                conn.close()
            
            self.send_message(compose_window)
        
        def delete_message(self):
            selection = self.email_listbox.curselection()
            if selection:
                if messagebox.askyesno("Delete Message", "Are you sure you want to delete this message?"):
                    index = selection[0]
                    email = self.emails[index]
                    email_id = email.get('id')
                    
                    if email_id:
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM emails WHERE id=?", (email_id,))
                        conn.commit()
                        conn.close()
                    
                    self.load_emails_from_db(self.current_folder)
            else:
                messagebox.showwarning("No Selection", "Please select an email to delete.")
        
        def send_receive(self):
            messagebox.showinfo("Send/Receive", "Checking for new messages...")
            
        def show_about(self):
            about_text = """Multiapp 95 Professional Mail Express
            
    This client is for informational purposes only.

    Copyright © 2025 Retro Computing Division
    All rights reserved."""
            
            messagebox.showinfo("About Mail Express", about_text)
            
        def show_options(self):
            options_window = tk.Toplevel(self.rootmailoutlook)
            options_window.title("Options")
            options_window.geometry("400x200")
            options_window.configure(bg="#c0c0c0")
            options_window.resizable(False, False)
            
            # Frame principal
            main_frame = tk.Frame(options_window, bg="#c0c0c0")
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Grupare opțiuni
            tk.Label(main_frame, text="Display Options", bg="#c0c0c0", 
                     font=("MS Sans Serif", 8, "bold")).pack(anchor="w", pady=(0, 10))
            
            # Checkbox pentru folder counts
            show_counts_var = tk.BooleanVar(value=self.show_folder_counts)
            
            check_frame = tk.Frame(main_frame, bg="#c0c0c0")
            check_frame.pack(anchor="w", pady=5)
            
            tk.Checkbutton(check_frame, text="Show message count in folders", 
                           variable=show_counts_var, bg="#c0c0c0",
                           font=("MS Sans Serif", 8)).pack(side="left")
            
            # Frame pentru butoane
            button_frame = tk.Frame(options_window, bg="#c0c0c0")
            button_frame.pack(side="bottom", pady=10)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, 
                         "font": ("MS Sans Serif", 8), "width": 10}
            
            def save_options():
                self.show_folder_counts = show_counts_var.get()
                self.update_folder_counts()
                messagebox.showinfo("Options", "Settings saved successfully!")
                options_window.destroy()
            
            def cancel_options():
                options_window.destroy()
            
            tk.Button(button_frame, text="OK", command=save_options, **btn_style).pack(side="left", padx=5)
            tk.Button(button_frame, text="Cancel", command=cancel_options, **btn_style).pack(side="left", padx=5)

    def mainoutlook():
        rootmailoutlook = tk.Tk()
        app = RetroEmailClient(rootmailoutlook)
        rootmailoutlook.mainloop()

    if __name__ == "__main__":
        mainoutlook()

OUTLOOK()