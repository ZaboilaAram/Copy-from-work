if emailvariable == 11002200:
    # Definirea numele fișierului pentru salvarea cheii
    FOLDER_NAME = "Serial"
    FILE_NAME = "product_key.lic95"
    cale_fis = "file_paths.txt"
    cale_fldr = "folder_paths.txt"

    # Definirea cheii de validare
    KEY = "R46BX-JHR2J-PG7ER-24QFG-MWKVR"
    
    key_is_valid = False
    file_path = os.path.join(FOLDER_NAME, FILE_NAME)

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, "r") as file:
                saved_key = file.read().strip()
                if saved_key == KEY:
                    key_is_valid = True
        except Exception as e:
            print(f"Error checking key: {e}")
    if not key_is_valid:
        # Verifică și creează folderul Serial dacă nu există
        if not os.path.exists(FOLDER_NAME):
            try:
                os.makedirs(FOLDER_NAME)
                print(f"Folder '{FOLDER_NAME}' created successfully.")
            except Exception as e:
                print(f"Error creating folder '{FOLDER_NAME}': {e}")

        def validate_key(event=None):
            # Funcția pentru validarea cheii
            global xx
            if text_box.get("1.0", "end-1c").strip() == KEY:
                xx = 2
                validate_button.config(state=tk.NORMAL)
                no_key_button.config(state=tk.DISABLED)
                
                # Calea completă către fișier în folderul Serial
                file_path = os.path.join(FOLDER_NAME, FILE_NAME)
                
                # Salvarea cheii în fișier text
                with open(file_path, "w") as file:
                    file.write(KEY)
                try:
                    if not os.path.exists("file_paths.txt"):
                        with open("file_paths.txt", "w") as file:
                            file.write("")
                except Exception as e:
                    print(f"An error occurred while creating the file file_paths.txt: {e}")

                try:
                    if not os.path.exists("folder_paths.txt"):
                        with open("folder_paths.txt", "w") as file:
                            file.write("")
                except Exception as e:
                    print(f"An error occurred while creating the file folder_paths.txt: {e}")
            else:
                xx = 0
                validate_button.config(state=tk.DISABLED)
                no_key_button.config(state=tk.NORMAL)

        def load_key():
            try:
                # Calea completă către fișier în folderul Serial
                file_path = os.path.join(FOLDER_NAME, FILE_NAME)
                
                # Încărcarea cheii din fișier text
                with open(file_path, "r") as file:
                    key = file.read().strip()
                    text_box.delete("1.0", "end")
                    text_box.insert("1.0", key)
                    validate_key()  # Validarea automată a cheii încărcate
            except FileNotFoundError:
                pass

        def nokey():
            messagebox.showinfo(title="Unlicensed Product", message="Secure connection.\nWelcome to Multiapp 95 Professional!\nFor full access, please contact the administrator (Tudor Marmureanu).")
            sys.exit()

        def valkey():
            messagebox.showinfo(title="Product Activated (professional version)", message="Secure connection.\nWelcome to Multiapp 95 Professional!")
            validation.destroy()

        def on_closing():
            #pass
            messagebox.showwarning("Warning", "Close the program from the Command Prompt to stop all processes!")

        # Crearea ferestrei principale pentru validare
        validation = tk.Tk()
        validation.protocol("WM_DELETE_WINDOW", on_closing)
        validation.title("Product key validation")
        validation.geometry("260x260")  # Setarea dimensiunilor ferestrei principale
        validation.config(bg="gray20")
        #image_icon52 = PhotoImage(file = "img/keylogo.png")
        #validation.iconphoto(False, image_icon52)

        # Crearea obiectului Text editabil
        text_box = tk.Text(validation, height=1, width=30)  # Setarea wrap="none" pentru a face obiectul Text dreptunghiular
        text_box.config(bd=4)
        text_box.pack(pady=10)
        text_box.bind("<KeyRelease>", validate_key)  # Legarea funcției validate_key() de evenimentul de eliberare a tastelor

        # Crearea butonului "I don't have a product key"
        no_key_button = tk.Button(validation, text="I don't have a product key", bg="black", fg="lime green", bd=5, command=nokey)
        no_key_button.pack(pady=5)

        # Crearea butonului "Validate key"
        validate_button = tk.Button(validation, text="Validate key" ,bg="black", fg="lime green", bd=5, command=valkey, state=tk.DISABLED)
        validate_button.pack(pady=5)

        # Încărcarea cheii la deschiderea programului (dacă există)
        load_key()

        # Rularea buclei principale
        validation.mainloop()
    #
    #import os
    import sqlite3
    import xml.etree.ElementTree as ET
    #from tkinter import messagebox

    try:
        conn = sqlite3.connect(os.path.join("Config", "extensions.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT enabled FROM extensions WHERE extension_id='0x00087'")
        result = cursor.fetchone()
        conn.close()
        
        if not result or not result[0]:
            messagebox.showerror("Extension Required", "0x00087 extension is not enabled.")
            exit()
    except:
        messagebox.showerror("Error", "Could not verify extension.")
        exit()
    #
    from datetime import datetime

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
            self.custom_folders = []
            self.user_name = "Me"
            self.signature = ""
            
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
                    "subject": "Tips and Tricks",
                    "date": datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), 
                    "body": "Quick steps after you closing this window:\n\n• Click Go to user handbook button to close this window\n• In that section, you will find a user manual for Multiapp 95 Professional.\n• Read each menu and follow the documentation at every step.\n\nIt is very important to use this software in the configured folder and not to delete anything!\n\nMuap Support Team"
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
                    "subject": "Product key",
                    "date": datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), 
                    "body": "Here is the serial number for your product:\n\nR46BX-JHR2J-PG7ER-24QFG-MWKVR\n\n• It is recommended that this information remain confidential. Thank you for your understanding.\n\nMuap Support Team"
                },
            ]
            
            self.emails = []
            self.current_email = None

            self.init_database()
            self.setup_ui()
            self.load_custom_folders()
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    folder_name TEXT UNIQUE NOT NULL
                )
            ''')
            # cursor.execute('''
                # CREATE TABLE IF NOT EXISTS settings (
                    # id INTEGER PRIMARY KEY CHECK (id = 1),
                    # user_name TEXT DEFAULT 'Me'
                # )
            # ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    user_name TEXT DEFAULT 'Me',
                    signature TEXT DEFAULT ''
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id INTEGER,
                    file_name TEXT,
                    file_content TEXT,
                    FOREIGN KEY (email_id) REFERENCES emails (id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_id INTEGER,
                    file_name TEXT,
                    file_content TEXT,
                    is_binary INTEGER DEFAULT 0,
                    FOREIGN KEY (email_id) REFERENCES emails (id) ON DELETE CASCADE
                )
            ''')
            
            # Verifică și adaugă coloana is_binary dacă nu există
            cursor.execute("PRAGMA table_info(attachments)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'is_binary' not in columns:
                cursor.execute("ALTER TABLE attachments ADD COLUMN is_binary INTEGER DEFAULT 0")
            
            conn.commit()
            
            # cursor.execute("SELECT user_name FROM settings WHERE id=1")
            # result = cursor.fetchone()
            # if result:
                # self.user_name = result[0]
            # else:
                # cursor.execute("INSERT INTO settings (id, user_name) VALUES (1, 'Me')")
                # conn.commit()
            # Verifică și adaugă coloana signature dacă nu există
            cursor.execute("PRAGMA table_info(settings)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'signature' not in columns:
                cursor.execute("ALTER TABLE settings ADD COLUMN signature TEXT DEFAULT ''")
            
            conn.commit()
            
            cursor.execute("SELECT user_name, signature FROM settings WHERE id=1")
            result = cursor.fetchone()
            if result:
                self.user_name = result[0]
                self.signature = result[1] if result[1] else ""
            else:
                cursor.execute("INSERT INTO settings (id, user_name, signature) VALUES (1, 'Me', '')")
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
            #self.email_body.insert(1.0, f"=== Viewing Attachment: {file_name} ===\n\n{file_content}")
            self.email_body.config(state="disabled")
            
            # Afișează butonul "Back to Email"
            self.back_to_email_btn.pack(side="left", padx=2)

        def show_email_content(self):
            """Revine la afișarea conținutului email-ului"""
            if self.current_email:
                # ASCUNDE SCROLLBAR-UL ORIZONTAL și resetează wrap
                self.body_scrollbar_x.pack_forget()
                self.email_body.config(wrap="word")
                    
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
            
            import base64
            from tkinter import filedialog
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT file_content, is_binary FROM attachments WHERE email_id=? AND file_name=?", 
                           (self.current_email['id'], file_name))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                messagebox.showerror("Error", "Attachment not found!")
                return
            
            file_content = result[0]
            is_binary = result[1] if len(result) > 1 else 0
            
            save_path = filedialog.asksaveasfilename(
                defaultextension="",
                initialfile=file_name,
                filetypes=[("All Files", "*.*")]
            )
            
            if save_path:
                try:
                    if is_binary:
                        # Decodifică din base64 și scrie binar
                        file_bytes = base64.b64decode(file_content)
                        with open(save_path, 'wb') as f:
                            f.write(file_bytes)
                    else:
                        # Scrie ca text
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
            
        def load_custom_folders(self):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT folder_name FROM custom_folders ORDER BY folder_name")
            rows = cursor.fetchall()
            conn.close()
            
            self.custom_folders = [row[0] for row in rows]
            self.refresh_folder_list()

        def refresh_folder_list(self):
            for widget in self.folders_container.winfo_children():
                widget.destroy()
            
            self.folder_labels = {}
            
            default_folders = ["Inbox", "Sent Items", "Favorites", "Drafts"]
            
            for folder in default_folders:
                folder_frame = tk.Frame(self.folders_container, bg="white")
                folder_frame.pack(fill="x")
                
                folder_btn = tk.Label(folder_frame, text=f"  {folder}", bg="white", anchor="w", 
                                    font=("MS Sans Serif", 8), cursor="hand2")
                folder_btn.pack(side="left", fill="x", expand=True)
                folder_btn.bind("<Button-1>", lambda e, f=folder: self.switch_folder(f))
                
                if folder == self.current_folder:
                    folder_btn.configure(bg="#316ac5", fg="white")
                
                self.folder_labels[folder] = folder_btn
            
            if self.custom_folders:
                separator = tk.Frame(self.folders_container, bg="#c0c0c0", height=2)
                separator.pack(fill="x", pady=2)
                
                for folder in self.custom_folders:
                    folder_frame = tk.Frame(self.folders_container, bg="white")
                    folder_frame.pack(fill="x")
                    
                    folder_btn = tk.Label(folder_frame, text=f"  {folder}", bg="white", anchor="w", 
                                        font=("MS Sans Serif", 8), cursor="hand2")
                    folder_btn.pack(side="left", fill="x", expand=True)
                    folder_btn.bind("<Button-1>", lambda e, f=folder: self.switch_folder(f))
                    folder_btn.bind("<Button-3>", lambda e, f=folder: self.show_folder_context_menu(e, f))
                    
                    if folder == self.current_folder:
                        folder_btn.configure(bg="#316ac5", fg="white")
                    
                    self.folder_labels[folder] = folder_btn
            
            self.update_folder_counts()

        def create_new_folder(self):
            from tkinter import simpledialog
            folder_name = simpledialog.askstring("New Folder", "Enter folder name:", parent=self.rootmailoutlook)
            
            if folder_name:
                folder_name = folder_name.strip()
                
                if not folder_name:
                    messagebox.showwarning("Invalid Name", "Folder name cannot be empty.")
                    return
                
                default_folders = ["Inbox", "Sent Items", "Favorites", "Drafts"]
                if folder_name in default_folders or folder_name in self.custom_folders:
                    messagebox.showwarning("Duplicate Folder", "A folder with this name already exists.")
                    return
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO custom_folders (folder_name) VALUES (?)", (folder_name,))
                    conn.commit()
                    self.custom_folders.append(folder_name)
                    self.refresh_folder_list()
                    messagebox.showinfo("Folder Created", f"Folder '{folder_name}' created successfully!")
                except sqlite3.IntegrityError:
                    messagebox.showwarning("Duplicate Folder", "A folder with this name already exists.")
                finally:
                    conn.close()

        def show_folder_context_menu(self, event, folder_name):
            menu = tk.Menu(self.rootmailoutlook, tearoff=0, bg="#c0c0c0")
            menu.add_command(label="Delete Folder", command=lambda: self.delete_custom_folder(folder_name))
            menu.post(event.x_root, event.y_root)

        def delete_custom_folder(self, folder_name):
            if messagebox.askyesno("Delete Folder", f"Are you sure you want to delete folder '{folder_name}'?\n\nAll emails in this folder will be moved to Inbox."):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("UPDATE emails SET folder='Inbox' WHERE folder=?", (folder_name,))
                cursor.execute("DELETE FROM custom_folders WHERE folder_name=?", (folder_name,))
                
                conn.commit()
                conn.close()
                
                self.custom_folders.remove(folder_name)
                self.refresh_folder_list()
                
                if self.current_folder == folder_name:
                    self.switch_folder("Inbox")
                else:
                    self.load_emails_from_db(self.current_folder)
                
                messagebox.showinfo("Folder Deleted", f"Folder '{folder_name}' deleted successfully!")

        def move_email_to_folder(self, target_folder):
            selection = self.email_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an email to move.")
                return
            
            index = selection[0]
            if index < len(self.emails):
                email = self.emails[index]
                email_id = email.get('id')
                
                if email_id:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE emails SET folder=? WHERE id=?", (target_folder, email_id))
                    conn.commit()
                    conn.close()
                    
                    self.load_emails_from_db(self.current_folder)
                    messagebox.showinfo("Email Moved", f"Email moved to '{target_folder}' successfully!")
            
        def setup_ui(self):
            menubar = tk.Menu(self.rootmailoutlook, bg="#c0c0c0", relief="raised", bd=1)
            self.rootmailoutlook.config(menu=menubar)
            
            file_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
            menubar.add_cascade(label="File", menu=file_menu)
            file_menu.add_command(label="New Message", command=self.new_message)
            file_menu.add_command(label="New Folder", command=self.create_new_folder)
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
            tools_menu.add_command(label="Signature...", command=self.show_signature_editor)
            
            help_menu = tk.Menu(menubar, tearoff=0, bg="#c0c0c0")
            menubar.add_cascade(label="Help", menu=help_menu)
            help_menu.add_command(label="About Mail Express", command=self.show_about)
            
            toolbar = tk.Frame(self.rootmailoutlook, bg="#c0c0c0", relief="raised", bd=1)
            toolbar.pack(fill="x", padx=2, pady=2)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, "font": ("MS Sans Serif", 8)}
            
            tk.Button(toolbar, text="Send/Recv", command=self.send_receive, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="New Msg", command=self.new_message, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="New Fld", command=self.create_new_folder, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Reply", command=self.reply_message, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Forward", command=self.forward_message, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Delete", command=self.delete_message, **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Signature", command=self.show_signature_editor, **btn_style).pack(side="left", padx=2)
            self.back_to_email_btn = tk.Button(toolbar, text="Back to Email", command=self.show_email_content, **btn_style)
            tk.Button(toolbar, text="To user handbook", command=self.rootmailoutlook.destroy, **btn_style).pack(side="left", padx=10)
            
            main_frame = tk.Frame(self.rootmailoutlook, bg="#c0c0c0")
            main_frame.pack(fill="both", expand=True, padx=4, pady=4)
            
            left_panel = tk.Frame(main_frame, bg="#c0c0c0", relief="sunken", bd=2, width=150)
            left_panel.pack(side="left", fill="y", padx=(0, 2))
            left_panel.pack_propagate(False)
            
            tk.Label(left_panel, text="Folders", bg="#c0c0c0", font=("MS Sans Serif", 8, "bold")).pack(anchor="w", padx=5, pady=2)
            
            self.folders_container = tk.Frame(left_panel, bg="white", relief="sunken", bd=1)
            self.folders_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))

            self.refresh_folder_list()
            
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
            self.body_container = body_container

            # Scrollbar vertical (păstrăm numele original)
            body_scrollbar = tk.Scrollbar(body_container, bg="#c0c0c0", orient="vertical")
            body_scrollbar.pack(side="right", fill="y")

            # Scrollbar orizontal (ascuns inițial)
            self.body_scrollbar_x = tk.Scrollbar(body_container, bg="#c0c0c0", orient="horizontal")
            # Nu facem pack() încă - va fi afișat doar pentru .mo95

            self.email_body = tk.Text(body_container, bg="white", font=("MS Sans Serif", 9),
                                     yscrollcommand=body_scrollbar.set,
                                     xscrollcommand=self.body_scrollbar_x.set,
                                     wrap="word", state="disabled")
            self.email_body.pack(side="top", fill="both", expand=True)

            body_scrollbar.config(command=self.email_body.yview)
            self.body_scrollbar_x.config(command=self.email_body.xview)
            
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

                move_menu = tk.Menu(self.context_menu, tearoff=0, bg="#c0c0c0")
                self.context_menu.add_cascade(label="Move to Folder", menu=move_menu)

                all_folders = ["Inbox", "Sent Items", "Favorites", "Drafts"] + self.custom_folders
                for folder in all_folders:
                    if folder != self.current_folder:
                        move_menu.add_command(label=folder, command=lambda f=folder: self.move_email_to_folder(f))
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
            
            self.emails = []
            for row in rows:
                email_id = row[0]
                # Încarcă atașamentele pentru acest email
                cursor.execute("SELECT file_name FROM attachments WHERE email_id=?", (email_id,))
                att_rows = cursor.fetchall()
                attachments = [att[0] for att in att_rows]
                self.emails.append({
                    'id': row[0],
                    'from': row[1],
                    'to': row[2],
                    'subject': row[3],
                    'date': row[4],
                    'body': row[5],
                    'folder': row[6],
                    'is_favorite': row[7],
                    'attachments': attachments
                })
                    
            conn.close()
            
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
            
            folder_counts = {}
            for folder in self.custom_folders:
                cursor.execute("SELECT COUNT(*) FROM emails WHERE folder=?", (folder,))
                folder_counts[folder] = cursor.fetchone()[0]
    
            conn.close()
            
            # Actualizează textul fiecărui folder
            if self.show_folder_counts:
                if "Inbox" in self.folder_labels:
                    self.folder_labels["Inbox"].config(text=f"  Inbox ({inbox_count})")
                if "Sent Items" in self.folder_labels:
                    self.folder_labels["Sent Items"].config(text=f"  Sent Items ({sent_count})")
                if "Drafts" in self.folder_labels:
                    self.folder_labels["Drafts"].config(text=f"  Drafts ({drafts_count})")
                if "Favorites" in self.folder_labels:
                    self.folder_labels["Favorites"].config(text=f"  Favorites ({fav_count})")
                
                for folder in self.custom_folders:
                    if folder in self.folder_labels:
                        self.folder_labels[folder].config(text=f"  {folder} ({folder_counts[folder]})")
            else:
                if "Inbox" in self.folder_labels:
                    self.folder_labels["Inbox"].config(text="  Inbox")
                if "Sent Items" in self.folder_labels:
                    self.folder_labels["Sent Items"].config(text="  Sent Items")
                if "Drafts" in self.folder_labels:
                    self.folder_labels["Drafts"].config(text="  Drafts")
                if "Favorites" in self.folder_labels:
                    self.folder_labels["Favorites"].config(text="  Favorites")
                
                for folder in self.custom_folders:
                    if folder in self.folder_labels:
                        self.folder_labels[folder].config(text=f"  {folder}")
            
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
                
                self.back_to_email_btn.pack_forget()
                
                # ASCUNDE SCROLLBAR-UL ORIZONTAL și resetează wrap
                self.body_scrollbar_x.pack_forget()
                self.email_body.config(wrap="word")
                
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
                            text=f"📄 {att}",
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
                
                self.email_body.config(state="normal")
                self.email_body.delete(1.0, tk.END)
                self.email_body.insert(1.0, email['body'])
                self.email_body.config(state="disabled")
        
        def view_attachment_by_index(self, index):
            """Vizualizează atașamentul după index"""
            if not self.current_email or not self.current_email.get('attachments'):
                return
            
            if index >= len(self.current_email['attachments']):
                return
            
            import base64
            from tkinter import filedialog
            
            file_name = self.current_email['attachments'][index]
            
            # Încarcă conținutul din baza de date
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT file_content, is_binary FROM attachments WHERE email_id=? AND file_name=?", 
                           (self.current_email['id'], file_name))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                messagebox.showerror("Error", "Attachment not found!")
                return
            
            file_content = result[0]
            # Verifică dacă a returnat is_binary
            is_binary = 0
            if len(result) > 1 and result[1] is not None:
                is_binary = result[1]
            else:
                # Dacă nu avem info, detectăm după extensie
                image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.pdf']
                file_ext = os.path.splitext(file_name)[1].lower()
                if file_ext in image_extensions:
                    is_binary = 1
            
            # Verifică dacă e imagine
            image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico']
            file_ext = os.path.splitext(file_name)[1].lower()
            
            if is_binary and file_ext in image_extensions:
                # Afișează imaginea
                self.show_image_preview(file_name, file_content)
            elif file_name.lower().endswith('.mo95'):
                self.render_mo95_file(file_name, file_content)
            else:
                # ASCUNDE scrollbar-ul pentru alte tipuri de fișiere
                self.body_scrollbar_x.pack_forget()
                self.email_body.config(wrap="word")
                
                # Afișare normală
                self.email_body.config(state="normal")
                self.email_body.delete(1.0, tk.END)
                
                if is_binary:
                    self.email_body.insert(1.0, f"[Binary file: {file_name}]\n\nThis is a binary file. Right-click and select 'Save As...' to download it.")
                else:
                    self.email_body.insert(1.0, file_content)
                
                self.email_body.config(state="disabled")
            
            # Afișează butonul "Back to Email"
            self.back_to_email_btn.pack(side="left", padx=2)
        
        def show_image_preview(self, file_name, base64_content):
            """Afișează o imagine în panoul de preview"""
            try:
                import base64
                from PIL import Image, ImageTk
                import io
                
                # Decodifică base64
                image_bytes = base64.b64decode(base64_content)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Redimensionează dacă e prea mare
                max_width = 600
                max_height = 400
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Convertește pentru Tkinter
                photo = ImageTk.PhotoImage(image)
                
                # ASCUNDE scrollbar-ul orizontal
                self.body_scrollbar_x.pack_forget()
                self.email_body.config(wrap="word")
                
                # Afișează imaginea
                self.email_body.config(state="normal")
                self.email_body.delete(1.0, tk.END)
                self.email_body.insert(1.0, f"[Image: {file_name}]\n\n")
                self.email_body.image_create(tk.END, image=photo)
                self.email_body.insert(tk.END, f"\n\nDimensions: {image.size[0]}x{image.size[1]}")
                self.email_body.config(state="disabled")
                
                # Păstrează referința la imagine pentru a nu fi garbage collected
                self.email_body.image = photo
                
            except ImportError:
                self.email_body.config(state="normal")
                self.email_body.delete(1.0, tk.END)
                self.email_body.insert(1.0, f"[Image: {file_name}]\n\nPillow library not installed. Cannot display image.\nRight-click and select 'Save As...' to download.")
                self.email_body.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to display image: {str(e)}")

        # Adaugă această metodă nouă în clasa RetroEmailClient:
        def render_mo95_file(self, file_name, xml_content):
            """Renderizează un fișier .mo95 cu formatare vizuală completă"""
            try:
                # AFIȘEAZĂ SCROLLBAR-UL ORIZONTAL
                self.body_scrollbar_x.pack(side="bottom", fill="x")
                
                # Schimbă wrap pe "none" pentru a permite scroll orizontal
                self.email_body.config(wrap="none")
                
                # Parsează XML-ul
                root = ET.fromstring(xml_content)
                
                # Resetează body-ul
                self.email_body.config(state="normal")
                self.email_body.delete(1.0, tk.END)
                
                # Header
                #self.email_body.insert(1.0, f"=== Viewing Document: {file_name} ===\n\n")
                
                # Extrage conținutul
                content_elem = root.find('content')
                if content_elem is not None and content_elem.text:
                    content_start = self.email_body.index(tk.END)
                    self.email_body.insert(tk.END, content_elem.text)
                    
                    # Configurează tag-urile pentru formatare
                    self.email_body.tag_configure("bold", font=("MS Sans Serif", 9, "bold"))
                    self.email_body.tag_configure("italic", font=("MS Sans Serif", 9, "italic"))
                    self.email_body.tag_configure("underline", underline=True)
                    self.email_body.tag_configure("bold_italic", font=("MS Sans Serif", 9, "bold italic"))
                    
                    self.email_body.tag_configure("left", justify=tk.LEFT)
                    self.email_body.tag_configure("center", justify=tk.CENTER)
                    self.email_body.tag_configure("right", justify=tk.RIGHT)
                    self.email_body.tag_configure("justify", justify=tk.LEFT)
                    
                    # Aplică formatările
                    formatting_elem = root.find('formatting')
                    if formatting_elem is not None:
                        for fmt in formatting_elem.findall('format'):
                            start_idx = fmt.get('start')
                            end_idx = fmt.get('end')
                            tags_str = fmt.get('tags', '')
                            
                            if tags_str:
                                tags = tags_str.split(',')
                                for tag in tags:
                                    tag = tag.strip()
                                    
                                    # Culori text
                                    if tag.startswith("color_"):
                                        color = tag.replace("color_", "")
                                        self.email_body.tag_configure(tag, foreground=color)
                                    # Culori fundal
                                    elif tag.startswith("bg_"):
                                        color = tag.replace("bg_", "")
                                        self.email_body.tag_configure(tag, background=color)
                                    
                                    # Aplică tag-ul
                                    try:
                                        self.email_body.tag_add(tag, start_idx, end_idx)
                                    except:
                                        pass
                    
                    # Renderizează tabelele
                    tables_elem = root.find('tables')
                    if tables_elem is not None:
                        for table in tables_elem.findall('table'):
                            try:
                                position = table.get('position')
                                rows = int(table.get('rows'))
                                cols = int(table.get('cols'))
                                
                                # Creează frame-ul tabelului
                                table_frame = tk.Frame(self.email_body, bg="black", 
                                                      relief=tk.SOLID, bd=1)
                                
                                for r in range(rows):
                                    row_frame = tk.Frame(table_frame, bg="white")
                                    row_frame.grid(row=r, column=0, sticky="ew")
                                    
                                    for c in range(cols):
                                        cell_text = tk.Text(row_frame, width=15, height=1,
                                                           relief=tk.SOLID, bd=1, wrap=tk.WORD,
                                                           font=("MS Sans Serif", 9),
                                                           state="disabled")  # Read-only
                                        cell_text.grid(row=0, column=c, padx=0, pady=0)
                                        
                                        # Găsește și inserează conținutul celulei
                                        for cell in table.findall('cell'):
                                            if int(cell.get('row')) == r and int(cell.get('col')) == c:
                                                if cell.text:
                                                    cell_text.config(state="normal")
                                                    cell_text.insert("1.0", cell.text)
                                                    cell_text.config(state="disabled")
                                                break
                                
                                # Inserează tabelul în body
                                try:
                                    self.email_body.window_create(position, window=table_frame)
                                except:
                                    # Dacă poziția nu e validă, inserează la sfârșit
                                    self.email_body.window_create(tk.END, window=table_frame)
                                    self.email_body.insert(tk.END, "\n")
                            except Exception as e:
                                print(f"Error rendering table: {e}")
                    
                    # Informații despre document la final
                    self.email_body.insert(tk.END, "\n\n" + "─" * 50 + "\n")
                    
                    font_elem = root.find('font_settings')
                    if font_elem is not None:
                        font_family = font_elem.get('family', 'N/A')
                        font_size = font_elem.get('size', 'N/A')
                        self.email_body.insert(tk.END, f"Font: {font_family}, Size: {font_size}\n")
                    
                    page_setup = root.find('page_setup')
                    if page_setup is not None:
                        left = page_setup.get('left_margin', 'N/A')
                        right = page_setup.get('right_margin', 'N/A')
                        self.email_body.insert(tk.END, f"Margins: L={left}\" R={right}\"\n")
                
                self.email_body.config(state="disabled")
                
            except ET.ParseError as e:
                # Dacă XML-ul e invalid, afișează ca text simplu
                self.email_body.config(state="normal")
                self.email_body.delete(1.0, tk.END)
                #self.email_body.insert(1.0, f"=== Viewing Attachment: {file_name} ===\n\n")
                self.email_body.insert(tk.END, "[Error parsing .mo95 file - showing raw content]\n\n")
                self.email_body.insert(tk.END, xml_content)
                self.email_body.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to render .mo95 file:\n{str(e)}")

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
            compose_window.geometry("600x450")
            compose_window.configure(bg="#c0c0c0")
            compose_window.resizable(True, True)
            
            toolbar = tk.Frame(compose_window, bg="#c0c0c0", relief="raised", bd=1)
            toolbar.pack(fill="x", padx=2, pady=2)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, "font": ("MS Sans Serif", 8)}
            tk.Button(toolbar, text="Send", command=lambda: self.send_message(compose_window), **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Save Draft", command=lambda: self.save_draft(compose_window), **btn_style).pack(side="left", padx=2)
            tk.Button(toolbar, text="Insert Signature", command=lambda: self.insert_signature(compose_window), **btn_style).pack(side="left", padx=2)
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
                body_text.mark_set("original_start", "1.0")
            elif forward:
                subject_entry.insert(0, f"Fwd: {forward['subject']}")
                body_text.insert(1.0, f"\n\n--- Forwarded Message ---\nFrom: {forward['from']}\nTo: {forward['to']}\nDate: {forward['date']}\nSubject: {forward['subject']}\n\n{forward['body']}")
                body_text.mark_set("original_start", "1.0")
                # Atașează automat fișierele din email-ul forward
                if forward.get('attachments'):
                    for att_name in forward['attachments']:
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT file_content, is_binary FROM attachments WHERE email_id=? AND file_name=?", 
                                      (forward['id'], att_name))
                        result = cursor.fetchone()
                        conn.close()
                        
                        if result:
                            if not hasattr(compose_window, 'attachments'):
                                compose_window.attachments = []
                            compose_window.attachments.append({
                                'name': att_name,
                                'content': result[0],
                                'is_binary': result[1] if len(result) > 1 else 0
                            })
                            
                            # Adaugă label-ul
                            self.add_attachment_label(compose_window, att_name, attachments_inner_frame, attachments_canvas)
            
            compose_window.to_entry = to_entry
            compose_window.subject_entry = subject_entry
            compose_window.body_text = body_text
            compose_window.attachments_inner_frame = attachments_inner_frame #ADAUGAT
            compose_window.attachments_canvas = attachments_canvas #ADAUGAT
            compose_window.draft_id = None
            compose_window.attachments = []
        
        def add_attachment_label(self, compose_window, att_name, inner_frame, canvas):
            """Adaugă un label pentru atașament în fereastra de compose"""
            att_label = tk.Label(
                inner_frame,
                text=f"📄 {att_name}",
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
            
        def attach_file(self, compose_window):
            """Atașează un fișier la email"""
            from tkinter import filedialog
            import base64
            
            file_path = filedialog.askopenfilename(
                title="Select File to Attach",
                filetypes=[
                    ("Multiapp 95 Office", "*.mo95"),
                    ("Text Files", "*.txt"),
                    ("Python Files", "*.py"),
                    ("C Files", "*.c"),
                    ("C Header Files", "*.h"),
                    ("C++ Files", "*.cpp"),
                    ("C++ Header Files", "*.hpp"),
                    ("CSS Files", "*.css"),
                    ("CSV Files", "*.csv"),
                    ("HTML Files", "*.html"),
                    ("INI Files", "*.ini"),
                    ("Java Files", "*.java"),
                    ("JavaScript Files", "*.js"),
                    ("JSON Files", "*.json"),
                    ("Log Files", "*.log"),
                    ("Markdown Files", "*.md"),
                    ("PHP Files", "*.php"),
                    ("Shell Scripts", "*.sh"),
                    ("SQL Files", "*.sql"),
                    ("XML Files", "*.xml"),
                    ("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.ico"),
                    ("PDF Files", "*.pdf"),
                    ("All Files", "*.*")
                ]
            )
            
            if file_path:
                try:
                    file_name = os.path.basename(file_path)
                    
                    # Verifică dacă fișierul e deja atașat
                    for att in compose_window.attachments:
                        if att['name'] == file_name:
                            messagebox.showwarning("Duplicate", "This file is already attached!")
                            return
                    
                    # Extensii text - citește ca text
                    text_extensions = ['.txt', '.py', '.c', '.h', '.cpp', '.hpp', '.css', '.csv', 
                                      '.html', '.ini', '.java', '.js', '.json', '.log', '.md', 
                                      '.mo95', '.php', '.sh', '.sql', '.xml']
                    
                    file_ext = os.path.splitext(file_name)[1].lower()
                    
                    if file_ext in text_extensions:
                        # Citește ca text
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        is_binary = False
                    else:
                        # Citește ca binar și convertește la base64
                        with open(file_path, 'rb') as f:
                            file_bytes = f.read()
                        file_content = base64.b64encode(file_bytes).decode('utf-8')
                        is_binary = True
                    
                    compose_window.attachments.append({
                        'name': file_name,
                        'content': file_content,
                        'is_binary': is_binary
                    })
                    
                    # Adaugă label-ul
                    self.add_attachment_label(compose_window, file_name, 
                                             compose_window.attachments_inner_frame, 
                                             compose_window.attachments_canvas)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to attach file: {str(e)}")
                    
        def show_compose_attachment_menu(self, event, compose_window):
            """Meniu contextual pentru atașamente în fereastra de compose"""
            selection = compose_window.attachments_listbox.curselection()
            if not selection:
                return
            
            menu = tk.Menu(self.rootmailoutlook, tearoff=0, bg="#c0c0c0")
            menu.add_command(label="Remove Attachment", 
                             command=lambda: self.remove_attachment(compose_window))
            menu.post(event.x_root, event.y_root)
            
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
            
        def remove_attachment(self, compose_window):
            """Elimină un atașament din lista de compose"""
            selection = compose_window.attachments_listbox.curselection()
            if not selection:
                return
            
            index = selection[0]
            compose_window.attachments.pop(index)
            compose_window.attachments_listbox.delete(index)
            
        def show_signature_editor(self):
            sig_window = tk.Toplevel(self.rootmailoutlook)
            sig_window.title("Email Signature")
            sig_window.geometry("500x350")
            sig_window.configure(bg="#c0c0c0")
            sig_window.resizable(False, False)
            
            main_frame = tk.Frame(sig_window, bg="#c0c0c0")
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            tk.Label(main_frame, text="Edit your email signature:", bg="#c0c0c0", 
                     font=("MS Sans Serif", 8, "bold")).pack(anchor="w", pady=(0, 5))
            
            text_frame = tk.Frame(main_frame, bg="#c0c0c0")
            text_frame.pack(fill="both", expand=True, pady=5)
            
            scrollbar = tk.Scrollbar(text_frame, bg="#c0c0c0")
            scrollbar.pack(side="right", fill="y")
            
            sig_text = tk.Text(text_frame, font=("MS Sans Serif", 9), 
                               yscrollcommand=scrollbar.set, wrap="word", height=10)
            sig_text.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=sig_text.yview)
            
            sig_text.insert(1.0, self.signature)
            
            button_frame = tk.Frame(sig_window, bg="#c0c0c0")
            button_frame.pack(side="bottom", pady=10)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, 
                         "font": ("MS Sans Serif", 8), "width": 10}
            
            def save_signature():
                self.signature = sig_text.get(1.0, tk.END).strip()
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE settings SET signature=? WHERE id=1", (self.signature,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Signature", "Signature saved successfully!")
                sig_window.destroy()
            
            tk.Button(button_frame, text="Save", command=save_signature, **btn_style).pack(side="left", padx=5)
            tk.Button(button_frame, text="Cancel", command=sig_window.destroy, **btn_style).pack(side="left", padx=5)

        def insert_signature(self, compose_window):
            if self.signature:
                body_text = compose_window.body_text
                
                # Verifică dacă există un marcaj pentru mesajul original
                if "original_start" in body_text.mark_names():
                    # Inserează semnătura ÎNAINTE de mesajul original
                    body_text.insert("original_start", f"\n\n{self.signature}\n")  # Schimbat aici
                else:
                    # Dacă nu e reply/forward, adaugă la sfârșit
                    current_content = body_text.get(1.0, tk.END)
                    if not current_content.strip().endswith(self.signature):
                        body_text.insert(tk.END, f"\n\n{self.signature}")
            else:
                messagebox.showinfo("No Signature", "No signature configured. Please set one in Tools > Signature.")
                
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
                    is_binary = 1 if att.get('is_binary', False) else 0
                    cursor.execute('''
                        INSERT INTO attachments (email_id, file_name, file_content, is_binary)
                        VALUES (?, ?, ?, ?)
                    ''', (sent_email_id, att['name'], att['content'], is_binary))
                    
            if to.lower() == "me" or to.lower() == current_user.lower() or to.lower() == self.user_name.lower():
                cursor.execute('''
                    INSERT INTO emails (from_addr, to_addr, subject, date, body, folder)
                    VALUES (?, ?, ?, ?, ?, 'Inbox')
                ''', (self.user_name, self.user_name, subject, datetime.now().strftime("%a %m/%d/%Y %I:%M %p"), body))
                
                # OBȚINE ID-ul emailului din Inbox
                inbox_email_id = cursor.lastrowid
                
                # Salvează atașamentele și pentru Inbox
                if hasattr(compose_window, 'attachments') and compose_window.attachments:
                    for att in compose_window.attachments:
                        is_binary = 1 if att.get('is_binary', False) else 0
                        cursor.execute('''
                            INSERT INTO attachments (email_id, file_name, file_content, is_binary)
                            VALUES (?, ?, ?, ?)
                        ''', (inbox_email_id, att['name'], att['content'], is_binary))
            
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
                    is_binary = 1 if att.get('is_binary', False) else 0
                    cursor.execute('''
                        INSERT INTO attachments (email_id, file_name, file_content, is_binary)
                        VALUES (?, ?, ?, ?)
                    ''', (draft_id, att['name'], att['content'], is_binary))
            
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
                    cursor.execute("SELECT file_content, is_binary FROM attachments WHERE email_id=? AND file_name=?", 
                                  (draft['id'], att_name))
                    result = cursor.fetchone()
                    if result:
                        compose_window.attachments.append({
                            'name': att_name,
                            'content': result[0],
                            'is_binary': result[1] if len(result) > 1 else 0
                        })
                        self.add_attachment_label(compose_window, att_name, 
                                                 attachments_inner_frame, 
                                                 attachments_canvas)
                conn.close()

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

Copyright © 2026 Retro Computing Division
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
                           
            # User Settings
            tk.Label(main_frame, text="User Settings", bg="#c0c0c0", 
                     font=("MS Sans Serif", 8, "bold")).pack(anchor="w", pady=(15, 10))
            
            name_frame = tk.Frame(main_frame, bg="#c0c0c0")
            name_frame.pack(anchor="w", pady=5)
            
            tk.Label(name_frame, text="Display Name:", bg="#c0c0c0",
                     font=("MS Sans Serif", 8)).pack(side="left", padx=(0, 5))
            
            user_name_entry = tk.Entry(name_frame, font=("MS Sans Serif", 9), width=20)
            user_name_entry.pack(side="left")
            user_name_entry.insert(0, self.user_name)
            
            # Frame pentru butoane
            button_frame = tk.Frame(options_window, bg="#c0c0c0")
            button_frame.pack(side="bottom", pady=10)
            
            btn_style = {"bg": "#c0c0c0", "relief": "raised", "bd": 2, 
                         "font": ("MS Sans Serif", 8), "width": 10}
            
            def save_options():
                self.show_folder_counts = show_counts_var.get()
                new_name = user_name_entry.get().strip()
                
                # Dacă e gol, setează "Me"
                if not new_name:
                    new_name = "Me"
                
                self.user_name = new_name
                
                # Salvează în baza de date
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("UPDATE settings SET user_name=? WHERE id=1", (new_name,))
                conn.commit()
                conn.close()
                
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
