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
