def init_database(self):
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_name TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            user_name TEXT DEFAULT 'Me'
        )
    ''')
    # NOUĂ TABELĂ PENTRU ATAȘAMENTE
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id INTEGER,
            file_name TEXT,
            file_content TEXT,
            FOREIGN KEY (email_id) REFERENCES emails (id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    # ... restul codului

############################################################

# În metoda setup_ui(), în secțiunea toolbar, după butonul "Delete":

self.back_to_email_btn = tk.Button(toolbar, text="Back to Email", 
                                    command=self.show_email_content, **btn_style)
# Nu îl afișăm încă, îl vom afișa doar când e nevoie

# În setup_ui(), după self.date_label.pack():
# FRAME PENTRU ATAȘAMENTE
self.attachments_frame = tk.Frame(right_panel, bg="#f0f0f0", relief="raised", bd=1)
self.attachments_frame.pack(fill="x", padx=2, pady=0)

tk.Label(self.attachments_frame, text="Attachments: ", bg="#f0f0f0", 
         font=("MS Sans Serif", 8)).pack(side="left", padx=5, pady=2)

# Container pentru canvas + scrollbar
attachments_container = tk.Frame(self.attachments_frame, bg="white", height=25)
attachments_container.pack(side="left", fill="x", expand=True, padx=5, pady=2)

# Canvas pentru scroll orizontal
self.attachments_canvas = tk.Canvas(attachments_container, bg="white", height=20, 
                                     highlightthickness=0)
self.attachments_canvas.pack(side="top", fill="x", expand=True)

# Scrollbar orizontal
attachments_scrollbar = tk.Scrollbar(attachments_container, orient="horizontal", 
                                      bg="#c0c0c0")
attachments_scrollbar.pack(side="bottom", fill="x")

# Frame interior pentru labels
self.attachments_inner_frame = tk.Frame(self.attachments_canvas, bg="white")
self.attachments_canvas_window = self.attachments_canvas.create_window(
    (0, 0), window=self.attachments_inner_frame, anchor="nw"
)

# Conectează scrollbar-ul
self.attachments_canvas.config(xscrollcommand=attachments_scrollbar.set)
attachments_scrollbar.config(command=self.attachments_canvas.xview)

# Update scroll region când se schimbă dimensiunea
self.attachments_inner_frame.bind("<Configure>", 
    lambda e: self.attachments_canvas.configure(scrollregion=self.attachments_canvas.bbox("all"))
)

# Apoi continuă cu body_container...
body_container = tk.Frame(right_panel, bg="#c0c0c0")
body_container.pack(fill="both", expand=True, padx=2, pady=2)
self.body_container = body_container #ADAUGAT

############################################################
def load_emails_from_db(self, folder):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if folder == "Favorites":
                cursor.execute("SELECT * FROM emails WHERE is_favorite=1 ORDER BY id DESC")
            else:
                cursor.execute("SELECT * FROM emails WHERE folder=? ORDER BY id DESC", (folder,))
            
            rows = cursor.fetchall()
            
            self.emails = []
            for row in rows:
                email_id = row[0]
                # Încarcă atașamentele pentru acest email
                cursor.execute("SELECT file_name FROM attachments WHERE email_id=?", (email_id,))
                att_rows = cursor.fetchall()  # SCHIMBAT: salvăm rezultatul în att_rows
                attachments = [att[0] for att in att_rows]  # ADĂUGAT: creăm lista de atașamente
                self.emails.append({
                    'id': row[0],
                    'from': row[1],
                    'to': row[2],
                    'subject': row[3],
                    'date': row[4],
                    'body': row[5],
                    'folder': row[6],
                    'is_favorite': row[7],
                    'attachments': attachments #ADAUGAT
                })
                
            conn.close()
            
            self.refresh_emails()
            self.update_folder_counts()

############################################################

def show_email_preview(self, index):
    if 0 <= index < len(self.emails):
        email = self.emails[index]
        self.current_email = email
        
        self.from_label.config(text=f"From: {email['from']}")
        self.to_label.config(text=f"To: {email['to']}")
        self.subject_label.config(text=f"Subject: {email['subject']}")
        self.date_label.config(text=f"Date: {email['date']}")
        
        # ACTUALIZEAZĂ LISTA DE ATAȘAMENTE - ORIZONTAL CA LABELS
        # Șterge labels-urile vechi
        for widget in self.attachments_inner_frame.winfo_children():
            widget.destroy()
        
        # Arată sau ascunde frame-ul de atașamente
        if email.get('attachments'):
            # Ascunde mai întâi pentru a reseta poziția
            self.attachments_frame.pack_forget()
            # Apoi afișează înainte de body_container
            self.attachments_frame.pack(fill="x", padx=2, pady=0, before=self.body_container)
            
            for i, att in enumerate(email['attachments']):
                # Creează un label pentru fiecare atașament
                att_label = tk.Label(
                    self.attachments_inner_frame,
                    text=f"📎 {att}",
                    bg="white",
                    fg="black",
                    font=("MS Sans Serif", 8, "underline"),
                    cursor="hand2",
                    padx=5
                )
                att_label.pack(side="left", padx=2)
                
                # Double-click pentru a vizualiza
                att_label.bind("<Double-Button-1>", lambda e, idx=i: self.view_attachment_by_index(idx))
                
                # Right-click pentru meniu contextual
                att_label.bind("<Button-3>", lambda e, idx=i: self.show_attachment_context_menu_by_index(e, idx))
            
            # Update scroll region
            self.attachments_inner_frame.update_idletasks()
            self.attachments_canvas.configure(scrollregion=self.attachments_canvas.bbox("all"))
        else:
            self.attachments_frame.pack_forget()  # Ascunde frame-ul dacă nu sunt atașamente
        
        ###
        
        self.email_body.config(state="normal")
        self.email_body.delete(1.0, tk.END)
        self.email_body.insert(1.0, email['body'])
        self.email_body.config(state="disabled")

############################################################
ADAUGA:
def view_attachment_by_index(self, index):
    """Vizualizează atașamentul după index"""
    if not self.current_email or not self.current_email.get('attachments'):
        return
    
    if index >= len(self.current_email['attachments']):
        return
    
    file_name = self.current_email['attachments'][index]
    
    # Încarcă conținutul din baza de date
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT file_content FROM attachments WHERE email_id=? AND file_name=?", 
                   (self.current_email['id'], file_name))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        messagebox.showerror("Error", "Attachment not found!")
        return
    
    file_content = result[0]
    
    # Afișează în panoul de body
    self.email_body.config(state="normal")
    self.email_body.delete(1.0, tk.END)
    self.email_body.insert(1.0, f"=== Viewing Attachment: {file_name} ===\n\n{file_content}")
    self.email_body.config(state="disabled")
    
    # Afișează butonul "Back to Email"
    self.back_to_email_btn.pack(side="left", padx=2)

def show_attachment_context_menu_by_index(self, event, index):
    """Meniu contextual pentru atașamente (varianta cu butoane)"""
    if not self.current_email or not self.current_email.get('attachments'):
        return
    
    if index >= len(self.current_email['attachments']):
        return
    
    file_name = self.current_email['attachments'][index]
    
    menu = tk.Menu(self.rootmailoutlook, tearoff=0, bg="#c0c0c0")
    menu.add_command(label="View", command=lambda: self.view_attachment_by_index(index))
    menu.add_command(label="Save As...", command=lambda: self.save_attachment(file_name))
    menu.post(event.x_root, event.y_root)

######################################################
Class RetroMailClient
ADAUGA:
  def view_attachment(self, event=None):
            """Afișează atașamentul în panoul de preview"""
            selection = self.attachments_listbox.curselection()
            if not selection or not self.current_email:
                return
            
            index = selection[0]
            file_name = self.current_email['attachments'][index]
            
            # Încarcă conținutul din baza de date
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT file_content FROM attachments WHERE email_id=? AND file_name=?", 
                           (self.current_email['id'], file_name))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                messagebox.showerror("Error", "Attachment not found!")
                return
            
            file_content = result[0]
            
            # Afișează în panoul de body
            self.email_body.config(state="normal")
            self.email_body.delete(1.0, tk.END)
            self.email_body.insert(1.0, f"=== Viewing Attachment: {file_name} ===\n\n{file_content}")
            self.email_body.config(state="disabled")
            
            # Afișează butonul "Back to Email"
            self.back_to_email_btn.pack(side="left", padx=2)

        def show_email_content(self):
            """Revine la afișarea conținutului email-ului"""
            if self.current_email:
                self.email_body.config(state="normal")
                self.email_body.delete(1.0, tk.END)
                self.email_body.insert(1.0, self.current_email['body'])
                self.email_body.config(state="disabled")
                
                # Ascunde butonul "Back to Email"
                self.back_to_email_btn.pack_forget()

def show_attachment_context_menu(self, event):
    """Meniu contextual pentru atașamente"""
    selection = self.attachments_listbox.curselection()
    if not selection or not self.current_email:
        return
    
    index = selection[0]
    file_name = self.current_email['attachments'][index]
    
    menu = tk.Menu(self.rootmailoutlook, tearoff=0, bg="#c0c0c0")
    menu.add_command(label="View", command=self.view_attachment)
    menu.add_command(label="Save As...", 
                     command=lambda: self.save_attachment(file_name))
    menu.post(event.x_root, event.y_root)

def save_attachment(self, file_name):
    """Salvează atașamentul pe disk"""
    if not self.current_email:
        return
    
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT file_content FROM attachments WHERE email_id=? AND file_name=?", 
                   (self.current_email['id'], file_name))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        messagebox.showerror("Error", "Attachment not found!")
        return
    
    file_content = result[0]
    
    from tkinter import filedialog
    save_path = filedialog.asksaveasfilename(
        defaultextension="",
        initialfile=file_name,
        filetypes=[("All Files", "*.*"), ("Text Files", "*.txt")]
    )
    
    if save_path:
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            messagebox.showinfo("Success", f"File saved to: {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

def save_attachment_from_viewer(self, file_name, file_content):
    """Salvează atașamentul din fereastra de vizualizare"""
    from tkinter import filedialog
    save_path = filedialog.asksaveasfilename(
        defaultextension="",
        initialfile=file_name,
        filetypes=[("All Files", "*.*"), ("Text Files", "*.txt")]
    )
    
    if save_path:
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            messagebox.showinfo("Success", f"File saved to: {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

############################################################

def open_compose_window(self, reply_to=None, forward=None):
            compose_window = tk.Toplevel(self.rootmailoutlook)
            compose_window.title("New Message")
            compose_window.geometry("600x450")
            compose_window.configure(bg="#c0c0c0")
            compose_window.resizable(True, True)
            
            toolbar = tk.Frame(compose_window, bg="#c0c0c0", relief="raised", bd=1)
            toolbar.pack(fill="x", padx=2, pady=2)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, "font": ("MS Sans Serif", 8)}
            tk.Button(toolbar, text="Send", command=lambda: self.send_message(compose_window), **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Save Draft", command=lambda: self.save_draft(compose_window), **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Attach File", command=lambda: self.attach_file(compose_window), **btn_style).pack(side="left", padx=2)
            
            headers_frame = tk.Frame(compose_window, bg="#c0c0c0")
            headers_frame.pack(fill="x", padx=5, pady=5)
            
            tk.Label(headers_frame, text="To:", bg="#c0c0c0", font=("MS Sans Serif", 8)).grid(row=0, column=0, sticky="w", padx=(0, 5))
            to_entry = tk.Entry(headers_frame, font=("MS Sans Serif", 9))
            to_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
            
            tk.Label(headers_frame, text="Subject:", bg="#c0c0c0", font=("MS Sans Serif", 8)).grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
            subject_entry = tk.Entry(headers_frame, font=("MS Sans Serif", 9))
            subject_entry.grid(row=1, column=1, sticky="ew", pady=2)
            
            headers_frame.columnconfigure(1, weight=1)
            
            # FRAME PENTRU ATAȘAMENTE - ORIZONTAL
            attachments_outer_frame = tk.Frame(compose_window, bg="#c0c0c0", relief="sunken", bd=0)
            attachments_outer_frame.pack(fill="x", padx=5, pady=(0, 5))
            
            tk.Label(attachments_outer_frame, text="Attachments:", bg="#c0c0c0", 
                     font=("MS Sans Serif", 8)).pack(side="left", padx=5, pady=2)
            
            # Container pentru canvas + scrollbar
            attachments_container = tk.Frame(attachments_outer_frame, bg="white", height=25)
            attachments_container.pack(side="left", fill="x", expand=True, padx=5, pady=2)
            
            # Canvas pentru scroll orizontal
            attachments_canvas = tk.Canvas(attachments_container, bg="white", height=20, 
                                            highlightthickness=0)
            attachments_canvas.pack(side="top", fill="x", expand=True)
            
            # Scrollbar orizontal
            attachments_scrollbar = tk.Scrollbar(attachments_container, orient="horizontal", 
                                                  bg="#c0c0c0")
            attachments_scrollbar.pack(side="bottom", fill="x")
            
            # Frame interior pentru labels
            attachments_inner_frame = tk.Frame(attachments_canvas, bg="white")
            attachments_canvas_window = attachments_canvas.create_window(
                (0, 0), window=attachments_inner_frame, anchor="nw"
            )
            
            # Conectează scrollbar-ul
            attachments_canvas.config(xscrollcommand=attachments_scrollbar.set)
            attachments_scrollbar.config(command=attachments_canvas.xview)
            
            # Update scroll region când se schimbă dimensiunea
            attachments_inner_frame.bind("<Configure>", 
                lambda e: attachments_canvas.configure(scrollregion=attachments_canvas.bbox("all"))
            )
            
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
                # Atașează automat fișierele din email-ul forward
                if forward.get('attachments'):
                    for att_name in forward['attachments']:
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT file_content FROM attachments WHERE email_id=? AND file_name=?", 
                                      (forward['id'], att_name))
                        result = cursor.fetchone()
                        conn.close()
                        
                        if result:
                            if not hasattr(compose_window, 'attachments'):
                                compose_window.attachments = []
                            compose_window.attachments.append({
                                'name': att_name,
                                'content': result[0]
                            })
                            
                            # Adaugă label-ul
                            self.add_attachment_label(compose_window, att_name, attachments_inner_frame, attachments_canvas)
            
            compose_window.to_entry = to_entry
            compose_window.subject_entry = subject_entry
            compose_window.body_text = body_text
            compose_window.attachments_inner_frame = attachments_inner_frame #ADAUGAT
            compose_window.attachments_canvas = attachments_canvas #ADAUGAT
            compose_window.draft_id = None
            
            if not hasattr(compose_window, 'attachments'):
                compose_window.attachments = []

ADAUGA:
def add_attachment_label(self, compose_window, att_name, inner_frame, canvas):
    """Adaugă un label pentru atașament în fereastra de compose"""
    att_label = tk.Label(
        inner_frame,
        text=f"📎 {att_name}",
        bg="white",
        fg="black",
        font=("MS Sans Serif", 8),
        cursor="hand2",
        padx=5
    )
    att_label.pack(side="left", padx=2)
    
    # Right-click pentru a șterge
    att_label.bind("<Button-3>", lambda e: self.show_compose_attachment_menu_for_label(e, compose_window, att_name, att_label))
    
    # Hover effect
    #att_label.bind("<Enter>", lambda e: att_label.config(bg="#e0e0e0"))
    #att_label.bind("<Leave>", lambda e: att_label.config(bg="white"))
    
    # Update scroll region
    inner_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
############################################################

dupa functia de mai sus:

def attach_file(self, compose_window):
            """Atașează un fișier la email"""
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title="Select File to Attach",
                filetypes=[
                    ("Text Files", "*.txt"),
                    ("Log Files", "*.log"),
                    ("Configuration Files", "*.ini *.cfg *.conf"),
                    ("CSV Files", "*.csv"),
                    ("XML Files", "*.xml"),
                    ("JSON Files", "*.json"),
                    ("Python Files", "*.py"),
                    ("All Files", "*.*")
                ]
            )
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    file_name = os.path.basename(file_path)
                    
                    # Verifică dacă fișierul e deja atașat
                    for att in compose_window.attachments:
                        if att['name'] == file_name:
                            messagebox.showwarning("Duplicate", "This file is already attached!")
                            return
                    
                    compose_window.attachments.append({
                        'name': file_name,
                        'content': file_content
                    })
                    
                    # Adaugă label-ul
                    self.add_attachment_label(compose_window, file_name, 
                                             compose_window.attachments_inner_frame, 
                                             compose_window.attachments_canvas)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to attach file: {str(e)}\n\nMake sure the file is a text file that can be opened without special tools.")

ADAUGA:
def show_compose_attachment_menu_for_label(self, event, compose_window, att_name, att_label):
    """Meniu contextual pentru atașamente în fereastra de compose (varianta cu labels)"""
    menu = tk.Menu(self.rootmailoutlook, tearoff=0, bg="#c0c0c0")
    menu.add_command(label="Remove Attachment", 
                     command=lambda: self.remove_attachment_by_name(compose_window, att_name, att_label))
    menu.post(event.x_root, event.y_root)

ADAUGA:
def remove_attachment_by_name(self, compose_window, att_name, att_label):
    """Elimină un atașament din lista de compose după nume"""
    # Găsește și elimină din lista de attachments
    for i, att in enumerate(compose_window.attachments):
        if att['name'] == att_name:
            compose_window.attachments.pop(i)
            break
    
    # Elimină label-ul
    att_label.destroy()
    
    # Update scroll region
    compose_window.attachments_inner_frame.update_idletasks()
    compose_window.attachments_canvas.configure(scrollregion=compose_window.attachments_canvas.bbox("all"))
    
def show_compose_attachment_menu(self, event, compose_window):
    """Meniu contextual pentru atașamente în fereastra de compose"""
    selection = compose_window.attachments_listbox.curselection()
    if not selection:
        return
    
    menu = tk.Menu(self.rootmailoutlook, tearoff=0, bg="#c0c0c0")
    menu.add_command(label="Remove Attachment", 
                     command=lambda: self.remove_attachment(compose_window))
    menu.post(event.x_root, event.y_root)

def remove_attachment(self, compose_window):
    """Elimină un atașament din lista de compose"""
    selection = compose_window.attachments_listbox.curselection()
    if not selection:
        return
    
    index = selection[0]
    compose_window.attachments.pop(index)
    compose_window.attachments_listbox.delete(index)

############################################################

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
            ''', (self.user_name, to, subject, datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), body))
            sent_email_id = cursor.lastrowid
            
            # Salvează atașamentele pentru Sent Items
            if hasattr(compose_window, 'attachments') and compose_window.attachments:
                for att in compose_window.attachments:
                    cursor.execute('''
                        INSERT INTO attachments (email_id, file_name, file_content)
                        VALUES (?, ?, ?)
                    ''', (sent_email_id, att['name'], att['content']))
            
            # Dacă destinatarul este "Me", salvează și în Inbox
            if to.lower() == "me" or to.lower() == current_user.lower() or to.lower() == self.user_name.lower():
                cursor.execute('''
                    INSERT INTO emails (from_addr, to_addr, subject, date, body, folder)
                    VALUES (?, ?, ?, ?, ?, 'Inbox')
                ''', (self.user_name, self.user_name, subject, datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), body))
                
                inbox_email_id = cursor.lastrowid
                
                # Salvează atașamentele și pentru Inbox
                if hasattr(compose_window, 'attachments') and compose_window.attachments:
                    for att in compose_window.attachments:
                        cursor.execute('''
                            INSERT INTO attachments (email_id, file_name, file_content)
                            VALUES (?, ?, ?)
                        ''', (inbox_email_id, att['name'], att['content']))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Message Sent", f"Message sent to: {to}")
            compose_window.destroy()
            
            self.load_emails_from_db(self.current_folder)

############################################################

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
                # Șterge atașamentele vechi
                cursor.execute("DELETE FROM attachments WHERE email_id=?", (draft_id,))
                msg = "Draft updated successfully!"
            else:
                # Creează un draft nou
                cursor.execute('''
                    INSERT INTO emails (from_addr, to_addr, subject, date, body, folder)
                    VALUES (?, ?, ?, ?, ?, 'Drafts')
                ''', (self.user_name, to, subject, datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), body))
                draft_id = cursor.lastrowid
                msg = "Draft saved successfully!"
            
            # Salvează atașamentele
            if hasattr(compose_window, 'attachments') and compose_window.attachments:
                for att in compose_window.attachments:
                    cursor.execute('''
                        INSERT INTO attachments (email_id, file_name, file_content)
                        VALUES (?, ?, ?)
                    ''', (draft_id, att['name'], att['content']))
                    
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Draft Saved", msg)
            compose_window.destroy()
            
            self.load_emails_from_db(self.current_folder)

############################################################

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
            compose_window.geometry("600x450")
            compose_window.configure(bg="#c0c0c0")
            compose_window.resizable(True, True)
            
            toolbar = tk.Frame(compose_window, bg="#c0c0c0", relief="raised", bd=1)
            toolbar.pack(fill="x", padx=2, pady=2)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, "font": ("MS Sans Serif", 8)}
            tk.Button(toolbar, text="Send", command=lambda: self.send_draft(compose_window), **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Save Draft", command=lambda: self.save_draft(compose_window), **btn_style).pack(side="left", padx=2)
            
            headers_frame = tk.Frame(compose_window, bg="#c0c0c0")
            headers_frame.pack(fill="x", padx=5, pady=5)
            
            # FRAME PENTRU ATAȘAMENTE - ORIZONTAL
            attachments_outer_frame = tk.Frame(compose_window, bg="#c0c0c0", relief="sunken", bd=0)
            attachments_outer_frame.pack(fill="x", padx=5, pady=(0, 5))
            
            tk.Label(attachments_outer_frame, text="Attachments:", bg="#c0c0c0", 
                     font=("MS Sans Serif", 8)).pack(side="left", padx=5, pady=2)
            
            # Container pentru canvas + scrollbar
            attachments_container = tk.Frame(attachments_outer_frame, bg="white", height=25)
            attachments_container.pack(side="left", fill="x", expand=True, padx=5, pady=2)
            
            # Canvas pentru scroll orizontal
            attachments_canvas = tk.Canvas(attachments_container, bg="white", height=20, 
                                            highlightthickness=0)
            attachments_canvas.pack(side="top", fill="x", expand=True)
            
            # Scrollbar orizontal
            attachments_scrollbar = tk.Scrollbar(attachments_container, orient="horizontal", 
                                                  bg="#c0c0c0")
            attachments_scrollbar.pack(side="bottom", fill="x")
            
            # Frame interior pentru labels
            attachments_inner_frame = tk.Frame(attachments_canvas, bg="white")
            attachments_canvas_window = attachments_canvas.create_window(
                (0, 0), window=attachments_inner_frame, anchor="nw"
            )
            
            # Conectează scrollbar-ul
            attachments_canvas.config(xscrollcommand=attachments_scrollbar.set)
            attachments_scrollbar.config(command=attachments_canvas.xview)
            
            # Update scroll region când se schimbă dimensiunea
            attachments_inner_frame.bind("<Configure>", 
                lambda e: attachments_canvas.configure(scrollregion=attachments_canvas.bbox("all"))
            )
            
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
            compose_window.attachments_inner_frame = attachments_inner_frame #ADAUGAT
            compose_window.attachments_canvas = attachments_canvas #ADAUGAT
            compose_window.draft_id = draft['id']
            compose_window.attachments = []
    
            # Încarcă atașamentele existente
            if draft.get('attachments'):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                for att_name in draft['attachments']:
                    cursor.execute("SELECT file_content FROM attachments WHERE email_id=? AND file_name=?", 
                                  (draft['id'], att_name))
                    result = cursor.fetchone()
                    if result:
                        compose_window.attachments.append({
                            'name': att_name,
                            'content': result[0]
                        })
                        # Add label for the attachment
                        self.add_attachment_label(compose_window, att_name, 
                                                 attachments_inner_frame, 
                                                 attachments_canvas)
                conn.close()
