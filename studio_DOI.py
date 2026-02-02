tools_menu.add_command(label="View Designer...", command=self._create_view)

def _table_designer(self):
        """Visual Table Designer - create or modify tables."""
        if not self.connection:
            messagebox.showwarning("No Database", "Connect to a database first.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Table Designer")
        dialog.geometry("900x800")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables
        mode_var = tk.StringVar(value="create")
        original_table = ""
        original_cols = []
        column_rows = []
        
        data_types = ["INTEGER", "TEXT", "REAL", "BLOB", "NUMERIC", 
                      "VARCHAR(255)", "VARCHAR(100)", "BOOLEAN", 
                      "DATE", "DATETIME", "TIMESTAMP"]
        
        # ==================== TOP FRAME ====================
        top_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        top_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(top_frame, text="Mode:", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        rb_create = tk.Radiobutton(top_frame, text="Create New Table", variable=mode_var, value="create",
                                    bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    selectcolor=self.colors['bg_medium'], font=('Segoe UI', 10),
                                    activebackground=self.colors['bg_dark'],
                                    command=lambda: switch_mode("create"))
        rb_create.pack(side=tk.LEFT, padx=(15, 10))
        
        rb_modify = tk.Radiobutton(top_frame, text="Modify Existing", variable=mode_var, value="modify",
                                    bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    selectcolor=self.colors['bg_medium'], font=('Segoe UI', 10),
                                    activebackground=self.colors['bg_dark'],
                                    command=lambda: switch_mode("modify"))
        rb_modify.pack(side=tk.LEFT)
        
        # ==================== NAME FRAME ====================
        name_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        name_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Create mode widgets
        create_widgets = tk.Frame(name_frame, bg=self.colors['bg_dark'])
        
        tk.Label(create_widgets, text="Table Name:", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        table_name_entry = tk.Entry(create_widgets, bg=self.colors['bg_medium'],
                                     fg=self.colors['text'], insertbackground=self.colors['text'],
                                     font=('Segoe UI', 11), relief=tk.FLAT, width=30)
        table_name_entry.pack(side=tk.LEFT, padx=(10, 0), ipady=5)
        table_name_entry.bind('<KeyRelease>', lambda e: refresh_preview())
        
        # Modify mode widgets
        modify_widgets = tk.Frame(name_frame, bg=self.colors['bg_dark'])
        
        tk.Label(modify_widgets, text="Select Table:", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        table_var = tk.StringVar(value="")
        tables_list = self.tables_cache if self.tables_cache else [""]
        table_dropdown = tk.OptionMenu(modify_widgets, table_var, *tables_list)
        table_dropdown.configure(bg=self.colors['bg_lighter'], fg=self.colors['text'],
                                  activebackground=self.colors['accent'], font=('Segoe UI', 10),
                                  highlightthickness=0, relief=tk.FLAT, width=20)
        table_dropdown["menu"].configure(bg=self.colors['bg_medium'], fg=self.colors['text'])
        table_dropdown.pack(side=tk.LEFT, padx=(10, 0))
        
        load_btn = tk.Button(modify_widgets, text="Load", command=lambda: load_table(),
                              bg=self.colors['accent'], fg='white',
                              font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, padx=15)
        load_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # ==================== INFO LABEL ====================
        info_var = tk.StringVar(value="")
        info_label = tk.Label(dialog, textvariable=info_var, bg=self.colors['bg_dark'],
                              fg=self.colors['warning'], font=('Segoe UI', 9, 'italic'))
        info_label.pack(fill=tk.X, padx=15)
        
        # ==================== COLUMNS FRAME ====================
        cols_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        cols_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tk.Label(cols_frame, text="Columns:", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        # Header
        header = tk.Frame(cols_frame, bg=self.colors['grid_header'])
        header.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(header, text="Column Name", width=20, anchor='w', padx=5, pady=5,
                 bg=self.colors['grid_header'], fg=self.colors['text'],
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        tk.Label(header, text="Type", width=15, anchor='w', padx=5,
                 bg=self.colors['grid_header'], fg=self.colors['text'],
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        tk.Label(header, text="PK", width=4, anchor='center', padx=5,
                 bg=self.colors['grid_header'], fg=self.colors['text'],
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        tk.Label(header, text="NN", width=4, anchor='center', padx=5,
                 bg=self.colors['grid_header'], fg=self.colors['text'],
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        tk.Label(header, text="UQ", width=4, anchor='center', padx=5,
                 bg=self.colors['grid_header'], fg=self.colors['text'],
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        tk.Label(header, text="Default", width=15, anchor='w', padx=5,
                 bg=self.colors['grid_header'], fg=self.colors['text'],
                 font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT)
        tk.Label(header, text="", width=6,
                 bg=self.colors['grid_header']).pack(side=tk.LEFT)
        
        # Scrollable list
        list_frame = tk.Frame(cols_frame, bg=self.colors['bg_dark'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(list_frame, bg=self.colors['bg_dark'], highlightthickness=0)
        scrollbar_y = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_x = tk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        inner_frame = tk.Frame(canvas, bg=self.colors['bg_dark'])
        canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor='nw')
        
        def on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        def on_canvas_configure(e):
            canvas.itemconfig(canvas_window, width=e.width)
        
        inner_frame.bind('<Configure>', on_frame_configure)
        canvas.bind('<Configure>', on_canvas_configure)
        canvas.bind('<MouseWheel>', lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), 'units'))
        
        # ==================== COLUMN BUTTONS ====================
        btn_frame = tk.Frame(cols_frame, bg=self.colors['bg_dark'])
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(btn_frame, text="+ Add Column", command=lambda: add_row(),
                  bg=self.colors['accent'], fg='white',
                  font=('Segoe UI', 9), relief=tk.FLAT, padx=12, pady=4).pack(side=tk.LEFT)
        
        tk.Button(btn_frame, text="+ ID Column", 
                  command=lambda: add_row('id', 'INTEGER', True, False, False, ''),
                  bg=self.colors['bg_lighter'], fg=self.colors['text'],
                  font=('Segoe UI', 9), relief=tk.FLAT, padx=12, pady=4).pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Button(btn_frame, text="+ Timestamp",
                  command=lambda: add_row('created_at', 'DATETIME', False, False, False, 'CURRENT_TIMESTAMP'),
                  bg=self.colors['bg_lighter'], fg=self.colors['text'],
                  font=('Segoe UI', 9), relief=tk.FLAT, padx=12, pady=4).pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Button(btn_frame, text="Clear All", command=lambda: clear_all(),
                  bg=self.colors['bg_lighter'], fg=self.colors['text'],
                  font=('Segoe UI', 9), relief=tk.FLAT, padx=12, pady=4).pack(side=tk.LEFT, padx=(5, 0))
        
        # ==================== SQL PREVIEW ====================
        preview_label = tk.Label(dialog, text="Generated SQL:", bg=self.colors['bg_dark'],
                                  fg=self.colors['text'], font=('Segoe UI', 10, 'bold'))
        preview_label.pack(anchor='w', padx=15, pady=(10, 5))
        
        preview_container = tk.Frame(dialog, bg=self.colors['border'])
        preview_container.pack(fill=tk.X, padx=15)
        
        preview_text = tk.Text(preview_container, bg=self.colors['bg_medium'],
                                fg=self.colors['success'], font=('Consolas', 10),
                                height=8, wrap=tk.NONE, relief=tk.FLAT, padx=10, pady=10)
        
        prev_scroll_y = tk.Scrollbar(preview_container, orient=tk.VERTICAL, command=preview_text.yview)
        prev_scroll_x = tk.Scrollbar(preview_container, orient=tk.HORIZONTAL, command=preview_text.xview)
        preview_text.configure(yscrollcommand=prev_scroll_y.set, xscrollcommand=prev_scroll_x.set)
        
        prev_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        prev_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # ==================== BOTTOM BUTTONS ====================
        bottom_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        bottom_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Button(bottom_frame, text="Cancel", command=dialog.destroy,
                  bg=self.colors['bg_lighter'], fg=self.colors['text'],
                  font=('Segoe UI', 10), relief=tk.FLAT, padx=20, pady=6).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(bottom_frame, text="Execute SQL", command=lambda: execute_sql(),
                  bg=self.colors['accent'], fg='white',
                  font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, padx=20, pady=6).pack(side=tk.RIGHT)
        
        # ==================== FUNCTIONS ====================
        
        def add_row(name='', dtype='TEXT', pk=False, nn=False, uq=False, default=''):
            row_num = len(column_rows)
            bg = self.colors['bg_dark'] if row_num % 2 == 0 else self.colors['grid_row_alt']
            
            row = tk.Frame(inner_frame, bg=bg)
            row.pack(fill=tk.X)
            
            # Name
            name_e = tk.Entry(row, bg=self.colors['bg_medium'], fg=self.colors['text'],
                              insertbackground=self.colors['text'], font=('Consolas', 10),
                              relief=tk.FLAT, width=20)
            name_e.pack(side=tk.LEFT, padx=2, pady=2, ipady=3)
            name_e.insert(0, name)
            name_e.bind('<KeyRelease>', lambda e: refresh_preview())
            
            # Type
            type_v = tk.StringVar(value=dtype)
            type_m = tk.OptionMenu(row, type_v, *data_types)
            type_m.configure(bg=self.colors['bg_lighter'], fg=self.colors['text'],
                             activebackground=self.colors['accent'], font=('Segoe UI', 9),
                             highlightthickness=0, relief=tk.FLAT, width=11)
            type_m["menu"].configure(bg=self.colors['bg_medium'], fg=self.colors['text'])
            type_m.pack(side=tk.LEFT, padx=2)
            type_v.trace_add('write', lambda *a: refresh_preview())
            
            # PK
            pk_v = tk.BooleanVar(value=pk)
            pk_c = tk.Checkbutton(row, variable=pk_v, bg=bg, selectcolor=self.colors['bg_medium'], fg="white", 
                                   activebackground=bg, command=refresh_preview)
            pk_c.pack(side=tk.LEFT, padx=8)
            
            # NN
            nn_v = tk.BooleanVar(value=nn)
            nn_c = tk.Checkbutton(row, variable=nn_v, bg=bg, selectcolor=self.colors['bg_medium'], fg="white", 
                                   activebackground=bg, command=refresh_preview)
            nn_c.pack(side=tk.LEFT, padx=8)
            
            # UQ
            uq_v = tk.BooleanVar(value=uq)
            uq_c = tk.Checkbutton(row, variable=uq_v, bg=bg, selectcolor=self.colors['bg_medium'], fg="white", 
                                   activebackground=bg, command=refresh_preview)
            uq_c.pack(side=tk.LEFT, padx=8)
            
            # Default
            def_e = tk.Entry(row, bg=self.colors['bg_medium'], fg=self.colors['text'],
                              insertbackground=self.colors['text'], font=('Consolas', 10),
                              relief=tk.FLAT, width=15)
            def_e.pack(side=tk.LEFT, padx=2, pady=2, ipady=3)
            def_e.insert(0, default)
            def_e.bind('<KeyRelease>', lambda e: refresh_preview())
            
            # Delete button
            def delete_this():
                nonlocal column_rows
                for i, r in enumerate(column_rows):
                    if r['frame'] == row:
                        column_rows.pop(i)
                        break
                row.destroy()
                refresh_preview()
            
            del_b = tk.Button(row, text="X", command=delete_this,
                              bg=self.colors['error'], fg='white',
                              font=('Segoe UI', 8, 'bold'), relief=tk.FLAT, padx=5)
            del_b.pack(side=tk.LEFT, padx=(10, 2))
            
            column_rows.append({
                'frame': row,
                'name': name_e,
                'type': type_v,
                'pk': pk_v,
                'nn': nn_v,
                'uq': uq_v,
                'default': def_e
            })
            
            # Focus if empty
            if not name:
                name_e.focus_set()
            
            refresh_preview()
        
        def clear_all():
            nonlocal column_rows, original_cols, original_table
            for r in column_rows:
                r['frame'].destroy()
            column_rows = []
            original_cols = []
            original_table = ""
            refresh_preview()
        
        def load_table():
            nonlocal original_table, original_cols
            
            tbl = table_var.get()
            if not tbl:
                messagebox.showwarning("Error", "Select a table first.", parent=dialog)
                return
            
            # Clear current
            for r in column_rows:
                r['frame'].destroy()
            column_rows.clear()
            
            original_table = tbl
            original_cols = []
            
            try:
                cursor = self.connection.cursor()
                
                # Get columns
                cursor.execute(f"PRAGMA table_info('{tbl}')")
                cols = cursor.fetchall()
                
                # Get unique indexes
                cursor.execute(f"PRAGMA index_list('{tbl}')")
                indexes = cursor.fetchall()
                unique_cols = set()
                for idx in indexes:
                    if idx[2] == 1:
                        cursor.execute(f"PRAGMA index_info('{idx[1]}')")
                        for info in cursor.fetchall():
                            unique_cols.add(info[2])
                
                for col in cols:
                    cid, cname, ctype, notnull, dflt, is_pk = col
                    
                    original_cols.append(cname)
                    
                    add_row(
                        name=cname,
                        dtype=ctype if ctype else 'TEXT',
                        pk=(is_pk == 1),
                        nn=(notnull == 1),
                        uq=(cname in unique_cols),
                        default=str(dflt) if dflt else ''
                    )
                
                info_var.set(f"Loaded table '{tbl}' with {len(cols)} columns. Modify and click Execute.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load table:\n{e}", parent=dialog)
        
        def get_column_defs():
            defs = []
            names = []
            
            for r in column_rows:
                n = r['name'].get().strip()
                if not n:
                    continue
                
                t = r['type'].get()
                pk = r['pk'].get()
                nn = r['nn'].get()
                uq = r['uq'].get()
                d = r['default'].get().strip()
                
                line = f"    {n} {t}"
                
                if pk:
                    if t == "INTEGER":
                        line += " PRIMARY KEY AUTOINCREMENT"
                    else:
                        line += " PRIMARY KEY"
                
                if nn and not pk:
                    line += " NOT NULL"
                
                if uq and not pk:
                    line += " UNIQUE"
                
                if d:
                    if d.upper() in ('NULL', 'CURRENT_TIMESTAMP', 'CURRENT_DATE', 'CURRENT_TIME'):
                        line += f" DEFAULT {d.upper()}"
                    elif d.replace('.', '').replace('-', '').isdigit():
                        line += f" DEFAULT {d}"
                    else:
                        line += f" DEFAULT '{d}'"
                
                defs.append(line)
                names.append(n)
            
            return defs, names
        
        def refresh_preview():
            defs, names = get_column_defs()
            
            if mode_var.get() == "create":
                tbl = table_name_entry.get().strip()
                if not tbl:
                    preview_text.delete('1.0', tk.END)
                    preview_text.insert('1.0', "-- Enter table name above")
                    return
                if not defs:
                    preview_text.delete('1.0', tk.END)
                    preview_text.insert('1.0', "-- Add at least one column")
                    return
                
                sql = f"CREATE TABLE {tbl} (\n"
                sql += ",\n".join(defs)
                sql += "\n);"
                
            else:  # modify
                if not original_table:
                    preview_text.delete('1.0', tk.END)
                    preview_text.insert('1.0', "-- Click 'Load' to load a table first")
                    return
                if not defs:
                    preview_text.delete('1.0', tk.END)
                    preview_text.insert('1.0', "-- Add at least one column")
                    return
                
                # Find common columns for data migration
                common = [n for n in names if n in original_cols]
                
                sql = f"-- Modify table: {original_table}\n"
                sql += f"-- Common columns (data preserved): {', '.join(common) if common else 'NONE'}\n\n"
                sql += f"PRAGMA foreign_keys=OFF;\n\n"
                sql += f"BEGIN TRANSACTION;\n\n"
                sql += f"ALTER TABLE {original_table} RENAME TO _old_{original_table};\n\n"
                sql += f"CREATE TABLE {original_table} (\n"
                sql += ",\n".join(defs)
                sql += "\n);\n\n"
                
                if common:
                    c = ", ".join(common)
                    sql += f"INSERT INTO {original_table} ({c})\n"
                    sql += f"SELECT {c} FROM _old_{original_table};\n\n"
                
                sql += f"DROP TABLE _old_{original_table};\n\n"
                sql += f"COMMIT;\n\n"
                sql += f"PRAGMA foreign_keys=ON;"
            
            preview_text.delete('1.0', tk.END)
            preview_text.insert('1.0', sql)
        
        def execute_sql():
            sql = preview_text.get('1.0', tk.END).strip()
            
            # Remove comments and check if there's actual SQL
            sql_lines = [line.strip() for line in sql.split('\n') if line.strip() and not line.strip().startswith('--')]
            
            if not sql_lines:
                messagebox.showwarning("Error", "No valid SQL to execute.", parent=dialog)
                return
            
            # Check for multiple primary keys
            pk_count = sum(1 for r in column_rows if r['pk'].get() and r['name'].get().strip())
            if pk_count > 1:
                messagebox.showwarning("Error", "Only one PRIMARY KEY is allowed per table.", parent=dialog)
                return
            
            # Check for duplicate column names
            col_names = [r['name'].get().strip().lower() for r in column_rows if r['name'].get().strip()]
            if len(col_names) != len(set(col_names)):
                messagebox.showwarning("Error", "Duplicate column names are not allowed.", parent=dialog)
                return
            
            # Validate
            if mode_var.get() == "create":
                tbl = table_name_entry.get().strip()
                if not tbl:
                    messagebox.showwarning("Error", "Enter a table name.", parent=dialog)
                    return
                if not tbl.replace('_', '').isalnum():
                    messagebox.showwarning("Error", "Invalid table name.", parent=dialog)
                    return
                
                # Check if exists
                if tbl in self.tables_cache:
                    if not messagebox.askyesno("Confirm", f"Table '{tbl}' exists. Drop and recreate?", parent=dialog):
                        return
                    try:
                        self.connection.execute(f"DROP TABLE {tbl}")
                        self.connection.commit()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to drop table:\n{e}", parent=dialog)
                        return
            else:
                if not original_table:
                    messagebox.showwarning("Error", "Load a table first.", parent=dialog)
                    return
                
                if not messagebox.askyesno("Confirm", 
                    f"This will recreate table '{original_table}'.\n"
                    "Data in common columns will be preserved.\n\nContinue?", parent=dialog):
                    return
            
            try:
                cursor = self.connection.cursor()
                
                # Split and execute statements
                statements = sql.split(';')
                for stmt in statements:
                    stmt = stmt.strip()
                    if stmt and not stmt.startswith('--'):
                        cursor.execute(stmt)
                
                self.connection.commit()
                
                tbl = table_name_entry.get().strip() if mode_var.get() == "create" else original_table
                action = "created" if mode_var.get() == "create" else "modified"
                
                messagebox.showinfo("Success", f"Table '{tbl}' {action} successfully!", parent=dialog)
                dialog.destroy()
                self._refresh_object_explorer()
                self._update_schema_cache()
                self._add_message(f"Table '{tbl}' {action}", 'success')
                
            except Exception as e:
                # Try to rollback on modify
                if mode_var.get() == "modify":
                    try:
                        self.connection.execute("ROLLBACK")
                        # Restore if backup exists
                        cursor = self.connection.cursor()
                        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='_old_{original_table}'")
                        if cursor.fetchone():
                            cursor.execute(f"DROP TABLE IF EXISTS {original_table}")
                            cursor.execute(f"ALTER TABLE _old_{original_table} RENAME TO {original_table}")
                            self.connection.commit()
                    except:
                        pass
                
                messagebox.showerror("Error", f"Failed to execute SQL:\n{e}", parent=dialog)
        
        def switch_mode(m):
            if m == "create":
                modify_widgets.pack_forget()
                create_widgets.pack(fill=tk.X)
                clear_all()
                add_row('id', 'INTEGER', True, False, False, '')
                info_var.set("")
            else:
                create_widgets.pack_forget()
                modify_widgets.pack(fill=tk.X)
                clear_all()
                info_var.set("Select a table and click 'Load' to begin editing.")
        
        # ==================== INITIALIZE ====================
        create_widgets.pack(fill=tk.X)
        add_row('id', 'INTEGER', True, False, False, '')
        table_name_entry.focus_set()
    

#dupa def _analyze_database(self):
def _create_view(self):
        """Visual View Designer - create or modify views without writing SQL."""
        if not self.connection:
            messagebox.showwarning("No Database", "Connect to a database first.")
            return
        
        if not self.tables_cache:
            messagebox.showwarning("No Tables", "No tables found in database.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("View Designer")
        dialog.geometry("850x700")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables
        mode_var = tk.StringVar(value="create")
        current_table = tk.StringVar(value="")
        original_view = [""]  # Using list to allow modification in nested functions
        
        # Get existing views
        views_list = []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
            views_list = [row[0] for row in cursor.fetchall()]
        except:
            pass
        
        # ==================== FUNCTIONS (defined first) ====================
        
        def on_table_select(event=None):
            selection = table_listbox.curselection()
            if selection:
                table = table_listbox.get(selection[0])
                current_table.set(table)
                
                columns_listbox.delete(0, tk.END)
                if table in self.columns_cache:
                    for col in self.columns_cache[table]:
                        columns_listbox.insert(tk.END, col)
                
                update_preview()
        
        def select_all_columns():
            columns_listbox.select_set(0, tk.END)
            update_preview()
        
        def select_no_columns():
            columns_listbox.selection_clear(0, tk.END)
            update_preview()
        
        def update_preview(event=None):
            table = current_table.get()
            
            if mode_var.get() == "create":
                view_name = view_name_entry.get().strip()
            else:
                view_name = original_view[0]
            
            if not view_name:
                preview_text.delete('1.0', tk.END)
                preview_text.insert('1.0', "-- Enter a view name")
                return
            
            if not table:
                preview_text.delete('1.0', tk.END)
                preview_text.insert('1.0', "-- Select a source table")
                return
            
            # Get selected columns
            selected_indices = columns_listbox.curselection()
            if selected_indices:
                selected_cols = [columns_listbox.get(i) for i in selected_indices]
                cols_str = ",\n       ".join(selected_cols)
            else:
                cols_str = "*"
            
            # Build SELECT
            distinct = "DISTINCT " if distinct_var.get() else ""
            sql = f"SELECT {distinct}{cols_str}\nFROM {table}"
            
            where = where_entry.get().strip()
            if where:
                sql += f"\nWHERE {where}"
            
            group = group_entry.get().strip()
            if group:
                sql += f"\nGROUP BY {group}"
            
            order = order_entry.get().strip()
            if order:
                sql += f"\nORDER BY {order} {order_dir.get()}"
            
            # Build full CREATE VIEW statement
            if mode_var.get() == "modify":
                full_sql = f"-- Modifying view: {view_name}\n"
                full_sql += f"DROP VIEW IF EXISTS {view_name};\n\n"
                full_sql += f"CREATE VIEW {view_name} AS\n{sql};"
            else:
                full_sql = f"CREATE VIEW {view_name} AS\n{sql};"
            
            preview_text.delete('1.0', tk.END)
            preview_text.insert('1.0', full_sql)
        
        def load_view():
            vname = view_var.get()
            if not vname:
                messagebox.showwarning("Error", "Select a view first.", parent=dialog)
                return
            
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='view' AND name='{vname}'")
                result = cursor.fetchone()
                
                if not result:
                    messagebox.showerror("Error", f"View '{vname}' not found.", parent=dialog)
                    return
                
                original_view[0] = vname
                view_sql = result[0]
                
                # Reset all fields
                distinct_var.set(False)
                where_entry.delete(0, tk.END)
                order_entry.delete(0, tk.END)
                group_entry.delete(0, tk.END)
                columns_listbox.selection_clear(0, tk.END)
                
                # Extract SELECT part (after AS)
                match = re.search(r'AS\s+SELECT\s+(.*)', view_sql, re.IGNORECASE | re.DOTALL)
                if not match:
                    info_var.set(f"Loaded view '{vname}'. Could not fully parse - edit manually in preview.")
                    preview_text.delete('1.0', tk.END)
                    preview_text.insert('1.0', f"-- Modifying view: {vname}\nDROP VIEW IF EXISTS {vname};\n\n{view_sql};")
                    return
                
                select_part = match.group(1).strip()
                
                # Check for DISTINCT
                if select_part.upper().startswith('DISTINCT'):
                    distinct_var.set(True)
                    select_part = select_part[8:].strip()
                
                # Try to find FROM clause
                from_match = re.search(r'\bFROM\s+(\w+)', select_part, re.IGNORECASE)
                if from_match:
                    table_name = from_match.group(1)
                    
                    # Select table in listbox
                    for i in range(table_listbox.size()):
                        if table_listbox.get(i).lower() == table_name.lower():
                            table_listbox.selection_clear(0, tk.END)
                            table_listbox.selection_set(i)
                            table_listbox.see(i)
                            current_table.set(table_name)
                            
                            # Load columns for this table
                            columns_listbox.delete(0, tk.END)
                            if table_name in self.columns_cache:
                                for col in self.columns_cache[table_name]:
                                    columns_listbox.insert(tk.END, col)
                            break
                    
                    # Try to find columns (between SELECT and FROM)
                    cols_match = re.search(r'^(.*?)\s+FROM\s+', select_part, re.IGNORECASE | re.DOTALL)
                    if cols_match:
                        cols_str = cols_match.group(1).strip()
                        if cols_str != '*':
                            cols = [c.strip() for c in cols_str.split(',')]
                            
                            columns_listbox.selection_clear(0, tk.END)
                            for i in range(columns_listbox.size()):
                                col_name = columns_listbox.get(i)
                                for c in cols:
                                    if col_name.lower() == c.lower() or c.lower().endswith(col_name.lower()):
                                        columns_listbox.selection_set(i)
                                        break
                
                # Try to find WHERE clause
                where_match = re.search(r'\bWHERE\s+(.*?)(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|$)', select_part, re.IGNORECASE | re.DOTALL)
                if where_match:
                    where_entry.delete(0, tk.END)
                    where_entry.insert(0, where_match.group(1).strip())
                
                # Try to find GROUP BY clause
                group_match = re.search(r'\bGROUP\s+BY\s+(.*?)(?:\bHAVING\b|\bORDER\b|\bLIMIT\b|$)', select_part, re.IGNORECASE | re.DOTALL)
                if group_match:
                    group_entry.delete(0, tk.END)
                    group_entry.insert(0, group_match.group(1).strip())
                
                # Try to find ORDER BY clause
                order_match = re.search(r'\bORDER\s+BY\s+(.*?)(?:\bLIMIT\b|$)', select_part, re.IGNORECASE | re.DOTALL)
                if order_match:
                    order_str = order_match.group(1).strip()
                    if order_str.upper().endswith(' DESC'):
                        order_dir.set("DESC")
                        order_str = order_str[:-5].strip()
                    elif order_str.upper().endswith(' ASC'):
                        order_dir.set("ASC")
                        order_str = order_str[:-4].strip()
                    order_entry.delete(0, tk.END)
                    order_entry.insert(0, order_str)
                
                info_var.set(f"Loaded view '{vname}'. Modify options and click Execute.")
                update_preview()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load view:\n{e}", parent=dialog)
        
        def test_query():
            table = current_table.get()
            if not table:
                messagebox.showwarning("Error", "Select a source table first.", parent=dialog)
                return
            
            selected_indices = columns_listbox.curselection()
            if selected_indices:
                selected_cols = [columns_listbox.get(i) for i in selected_indices]
                cols_str = ", ".join(selected_cols)
            else:
                cols_str = "*"
            
            distinct = "DISTINCT " if distinct_var.get() else ""
            sql = f"SELECT {distinct}{cols_str} FROM {table}"
            
            where = where_entry.get().strip()
            if where:
                sql += f" WHERE {where}"
            
            group = group_entry.get().strip()
            if group:
                sql += f" GROUP BY {group}"
            
            order = order_entry.get().strip()
            if order:
                sql += f" ORDER BY {order} {order_dir.get()}"
            
            sql += " LIMIT 100"
            
            try:
                cursor = self.connection.cursor()
                cursor.execute(sql)
                rows = cursor.fetchall()
                cols = [desc[0] for desc in cursor.description] if cursor.description else []
                
                msg = f"Query executed successfully!\n\n"
                msg += f"Columns: {len(cols)}\n"
                msg += f"Rows returned: {len(rows)} (limited to 100)\n\n"
                if cols:
                    msg += f"Column names:\n{', '.join(cols)}"
                
                messagebox.showinfo("Test Result", msg, parent=dialog)
            except Exception as e:
                messagebox.showerror("Test Failed", f"Query error:\n\n{e}", parent=dialog)
        
        def execute_sql():
            if mode_var.get() == "create":
                view_name = view_name_entry.get().strip()
                if not view_name:
                    messagebox.showwarning("Error", "Enter a view name.", parent=dialog)
                    return
                if not view_name.replace('_', '').isalnum():
                    messagebox.showwarning("Error", "Invalid view name.", parent=dialog)
                    return
            else:
                if not original_view[0]:
                    messagebox.showwarning("Error", "Load a view first.", parent=dialog)
                    return
                view_name = original_view[0]
            
            table = current_table.get()
            if not table:
                messagebox.showwarning("Error", "Select a source table.", parent=dialog)
                return
            
            # Check if name exists as table (not allowed)
            try:
                cursor = self.connection.cursor()
                cursor.execute(f"SELECT type FROM sqlite_master WHERE name='{view_name}'")
                result = cursor.fetchone()
                if result and result[0] == 'table':
                    messagebox.showerror("Error", f"'{view_name}' already exists as a TABLE.\nChoose a different name.", parent=dialog)
                    return
            except:
                pass
            
            # Confirm
            if mode_var.get() == "create":
                if view_name in views_list:
                    if not messagebox.askyesno("Confirm", f"View '{view_name}' exists. Replace it?", parent=dialog):
                        return
            else:
                if not messagebox.askyesno("Confirm", f"Replace view '{view_name}'?", parent=dialog):
                    return
            
            # Build the SELECT query
            selected_indices = columns_listbox.curselection()
            if selected_indices:
                selected_cols = [columns_listbox.get(i) for i in selected_indices]
                cols_str = ", ".join(selected_cols)
            else:
                cols_str = "*"
            
            distinct = "DISTINCT " if distinct_var.get() else ""
            select_sql = f"SELECT {distinct}{cols_str} FROM {table}"
            
            where = where_entry.get().strip()
            if where:
                select_sql += f" WHERE {where}"
            
            group = group_entry.get().strip()
            if group:
                select_sql += f" GROUP BY {group}"
            
            order = order_entry.get().strip()
            if order:
                select_sql += f" ORDER BY {order} {order_dir.get()}"
            
            try:
                cursor = self.connection.cursor()
                
                # Drop existing view first
                cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
                
                # Create new view
                create_sql = f"CREATE VIEW {view_name} AS {select_sql}"
                cursor.execute(create_sql)
                
                self.connection.commit()
                
                action = "created" if mode_var.get() == "create" else "modified"
                messagebox.showinfo("Success", f"View '{view_name}' {action} successfully!", parent=dialog)
                dialog.destroy()
                self._refresh_object_explorer()
                self._add_message(f"View '{view_name}' {action}", 'success')
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to execute SQL:\n{e}", parent=dialog)
        
        def switch_mode(m):
            if m == "create":
                modify_widgets.pack_forget()
                create_widgets.pack(fill=tk.X)
                original_view[0] = ""
                info_var.set("")
                view_name_entry.delete(0, tk.END)
                view_name_entry.focus_set()
            else:
                create_widgets.pack_forget()
                modify_widgets.pack(fill=tk.X)
                original_view[0] = ""
                if views_list:
                    info_var.set("Select a view and click 'Load' to begin editing.")
                else:
                    info_var.set("No views found in database.")
            
            update_preview()
        
        # ==================== TOP - MODE SELECTION ====================
        top_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        top_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(top_frame, text="Mode:", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        
        rb_create = tk.Radiobutton(top_frame, text="Create New View", variable=mode_var, value="create",
                                    bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    selectcolor=self.colors['bg_medium'], font=('Segoe UI', 10),
                                    activebackground=self.colors['bg_dark'],
                                    command=lambda: switch_mode("create"))
        rb_create.pack(side=tk.LEFT, padx=(15, 10))
        
        rb_modify = tk.Radiobutton(top_frame, text="Modify Existing View", variable=mode_var, value="modify",
                                    bg=self.colors['bg_dark'], fg=self.colors['text'],
                                    selectcolor=self.colors['bg_medium'], font=('Segoe UI', 10),
                                    activebackground=self.colors['bg_dark'],
                                    command=lambda: switch_mode("modify"))
        rb_modify.pack(side=tk.LEFT)
        
        # ==================== NAME FRAME ====================
        name_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        name_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        create_widgets = tk.Frame(name_frame, bg=self.colors['bg_dark'])
        
        tk.Label(create_widgets, text="View Name:", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        view_name_entry = tk.Entry(create_widgets, bg=self.colors['bg_medium'],
                                    fg=self.colors['text'], insertbackground=self.colors['text'],
                                    font=('Segoe UI', 11), relief=tk.FLAT, width=30)
        view_name_entry.pack(side=tk.LEFT, padx=(10, 0), ipady=5)
        view_name_entry.bind('<KeyRelease>', lambda e: update_preview())
        
        modify_widgets = tk.Frame(name_frame, bg=self.colors['bg_dark'])
        
        tk.Label(modify_widgets, text="Select View:", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        view_var = tk.StringVar(value="")
        if views_list:
            view_dropdown = tk.OptionMenu(modify_widgets, view_var, *views_list)
        else:
            view_dropdown = tk.OptionMenu(modify_widgets, view_var, "")
        view_dropdown.configure(bg=self.colors['bg_lighter'], fg=self.colors['text'],
                                 activebackground=self.colors['accent'], font=('Segoe UI', 10),
                                 highlightthickness=0, relief=tk.FLAT, width=20)
        view_dropdown["menu"].configure(bg=self.colors['bg_medium'], fg=self.colors['text'])
        view_dropdown.pack(side=tk.LEFT, padx=(10, 0))
        
        load_btn = tk.Button(modify_widgets, text="Load", command=load_view,
                              bg=self.colors['accent'], fg='white',
                              font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, padx=15)
        load_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # ==================== INFO LABEL ====================
        info_var = tk.StringVar(value="")
        info_label = tk.Label(dialog, textvariable=info_var, bg=self.colors['bg_dark'],
                              fg=self.colors['warning'], font=('Segoe UI', 9, 'italic'))
        info_label.pack(fill=tk.X, padx=15)
        
        # ==================== MAIN CONTENT ====================
        content_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15)
        
        # ==================== LEFT PANEL ====================
        left_frame = tk.Frame(content_frame, bg=self.colors['bg_medium'], width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="Source Table:", bg=self.colors['bg_medium'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        
        table_frame = tk.Frame(left_frame, bg=self.colors['bg_medium'])
        table_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        table_listbox = tk.Listbox(table_frame, bg=self.colors['bg_dark'],
                                    fg=self.colors['text'], font=('Consolas', 10),
                                    selectmode=tk.SINGLE, relief=tk.FLAT,
                                    selectbackground=self.colors['accent'],
                                    selectforeground='white', height=5,
                                    highlightthickness=0, borderwidth=0,
                                    exportselection=False)
        table_scroll = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table_listbox.yview)
        table_listbox.configure(yscrollcommand=table_scroll.set)
        
        table_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        table_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        for table in self.tables_cache:
            table_listbox.insert(tk.END, table)
        
        table_listbox.bind('<<ListboxSelect>>', on_table_select)
        
        tk.Label(left_frame, text="Select Columns:", bg=self.colors['bg_medium'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 5))
        
        sel_btn_frame = tk.Frame(left_frame, bg=self.colors['bg_medium'])
        sel_btn_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        tk.Button(sel_btn_frame, text="All", command=select_all_columns,
                  bg=self.colors['bg_lighter'], fg=self.colors['text'],
                  font=('Segoe UI', 8), relief=tk.FLAT, padx=8, pady=2).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(sel_btn_frame, text="None", command=select_no_columns,
                  bg=self.colors['bg_lighter'], fg=self.colors['text'],
                  font=('Segoe UI', 8), relief=tk.FLAT, padx=8, pady=2).pack(side=tk.LEFT)
        
        columns_frame = tk.Frame(left_frame, bg=self.colors['bg_dark'])
        columns_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        columns_listbox = tk.Listbox(columns_frame, bg=self.colors['bg_dark'],
                                      fg=self.colors['text'], font=('Consolas', 10),
                                      selectmode=tk.MULTIPLE, relief=tk.FLAT,
                                      selectbackground=self.colors['accent'],
                                      selectforeground='white',
                                      highlightthickness=0, borderwidth=0,
                                      exportselection=False)
        columns_scroll = tk.Scrollbar(columns_frame, orient=tk.VERTICAL, command=columns_listbox.yview)
        columns_listbox.configure(yscrollcommand=columns_scroll.set)
        
        columns_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        columns_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        columns_listbox.bind('<<ListboxSelect>>', lambda e: update_preview())
        
        # ==================== RIGHT PANEL ====================
        right_frame = tk.Frame(content_frame, bg=self.colors['bg_dark'])
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        distinct_var = tk.BooleanVar(value=False)
        tk.Checkbutton(right_frame, text="DISTINCT (remove duplicate rows)", 
                       variable=distinct_var,
                       bg=self.colors['bg_dark'], fg=self.colors['text'],
                       selectcolor=self.colors['bg_medium'],
                       activebackground=self.colors['bg_dark'],
                       activeforeground=self.colors['text'],
                       font=('Segoe UI', 10),
                       command=update_preview).pack(anchor='w', pady=(0, 15))
        
        tk.Label(right_frame, text="WHERE Condition (optional):", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        tk.Label(right_frame, text="Example: age > 18 AND status = 'active'", bg=self.colors['bg_dark'],
                 fg=self.colors['text_dim'], font=('Segoe UI', 9)).pack(anchor='w', pady=(0, 5))
        
        where_entry = tk.Entry(right_frame, bg=self.colors['bg_medium'],
                               fg=self.colors['text'], insertbackground=self.colors['text'],
                               font=('Consolas', 11), relief=tk.FLAT)
        where_entry.pack(fill=tk.X, ipady=5, pady=(0, 15))
        where_entry.bind('<KeyRelease>', lambda e: update_preview())
        
        tk.Label(right_frame, text="ORDER BY (optional):", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        order_frame = tk.Frame(right_frame, bg=self.colors['bg_dark'])
        order_frame.pack(fill=tk.X, pady=(0, 15))
        
        order_entry = tk.Entry(order_frame, bg=self.colors['bg_medium'],
                               fg=self.colors['text'], insertbackground=self.colors['text'],
                               font=('Consolas', 11), relief=tk.FLAT)
        order_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        order_entry.bind('<KeyRelease>', lambda e: update_preview())
        
        order_dir = tk.StringVar(value="ASC")
        order_menu = tk.OptionMenu(order_frame, order_dir, "ASC", "DESC")
        order_menu.configure(bg=self.colors['bg_lighter'], fg=self.colors['text'],
                             activebackground=self.colors['accent'], font=('Segoe UI', 9),
                             highlightthickness=0, relief=tk.FLAT, width=6)
        order_menu["menu"].configure(bg=self.colors['bg_medium'], fg=self.colors['text'])
        order_menu.pack(side=tk.LEFT, padx=(10, 0))
        order_dir.trace_add('write', lambda *args: update_preview())
        
        tk.Label(right_frame, text="GROUP BY (optional):", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        group_entry = tk.Entry(right_frame, bg=self.colors['bg_medium'],
                               fg=self.colors['text'], insertbackground=self.colors['text'],
                               font=('Consolas', 11), relief=tk.FLAT)
        group_entry.pack(fill=tk.X, ipady=5, pady=(0, 15))
        group_entry.bind('<KeyRelease>', lambda e: update_preview())
        
        tk.Label(right_frame, text="Generated SQL Preview:", bg=self.colors['bg_dark'],
                 fg=self.colors['text'], font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        preview_frame = tk.Frame(right_frame, bg=self.colors['border'])
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        preview_text = tk.Text(preview_frame, bg=self.colors['bg_medium'], 
                               fg=self.colors['success'],
                               font=('Consolas', 11), relief=tk.FLAT, 
                               height=8, padx=10, pady=10, wrap=tk.NONE)
        
        preview_scroll_y = tk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_text.yview)
        preview_scroll_x = tk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=preview_text.xview)
        preview_text.configure(yscrollcommand=preview_scroll_y.set, xscrollcommand=preview_scroll_x.set)
        
        preview_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        preview_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # ==================== BOTTOM BUTTONS ====================
        btn_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        btn_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                  bg=self.colors['bg_lighter'], fg=self.colors['text'],
                  font=('Segoe UI', 10), relief=tk.FLAT, padx=25, pady=8).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(btn_frame, text="Execute", command=execute_sql,
                  bg=self.colors['accent'], fg='white',
                  font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, padx=25, pady=8).pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="Test Query", command=test_query,
                  bg='#2e7d32', fg='white',
                  font=('Segoe UI', 10), relief=tk.FLAT, padx=25, pady=8).pack(side=tk.RIGHT, padx=(0, 10))
        
        # ==================== INITIALIZE ====================
        create_widgets.pack(fill=tk.X)
        
        if self.tables_cache:
            table_listbox.select_set(0)
            on_table_select()
        
        view_name_entry.focus_set()
    
