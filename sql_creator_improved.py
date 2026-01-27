import tkinter as tk
from tkinter import messagebox, scrolledtext
import re

class SQLCreator:
    def __init__(self, rootsqlquerycr):
        self.rootsqlquerycr = rootsqlquerycr
        self.rootsqlquerycr.title("SQL Query Creator")
        self.rootsqlquerycr.geometry("950x700")
        self.rootsqlquerycr.configure(bg="#c0c0c0")
        
        # Tables and columns data structure
        self.tables = {}
        self.current_query_type = "SELECT"
        self.selected_columns = []
        self.selected_table = None
        self.where_conditions = []
        self.join_conditions = []
        self.order_by = []
        self.group_by = []
        
        self.setup_ui()
    
    def get_column_type(self, column_name):
        """Get the data type of a column from the selected table"""
        if not self.selected_table or self.selected_table not in self.tables:
            return None
        
        # Suportă atât 'column' cât și 'table.column'
        col_name = column_name.split('.')[-1]
        
        for col in self.tables[self.selected_table]:
            if col['name'] == col_name:
                return col['type']
        return None

    def is_numeric_type(self, data_type):
        """Check if a data type is numeric"""
        if not data_type:
            return False
        data_type = data_type.upper()
        numeric_types = ['INT', 'INTEGER', 'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL', 'BOOLEAN', 'BOOL']
        return any(nt in data_type for nt in numeric_types)

    def auto_format_value(self, value, column_name):
        """Automatically format value based on column type"""
        col_type = self.get_column_type(column_name)
        
        # Dacă e tip numeric, verifică dacă valoarea e număr
        if col_type and self.is_numeric_type(col_type):
            # Verifică dacă valoarea e boolean
            if value.upper() in ['TRUE', 'FALSE', '1', '0']:
                return value.upper() if value.upper() in ['TRUE', 'FALSE'] else value
            
            # Verifică dacă e număr
            try:
                float(value)
                return value  # E număr valid, nu pune ghilimele
            except ValueError:
                # Nu e număr valid, pune ghilimele
                return f"'{self.escape_sql_string(value)}'"
        else:
            # Nu e tip numeric sau tip necunoscut, pune ghilimele
            return f"'{self.escape_sql_string(value)}'"

    def get_columns_for_table(self):
        """Get list of column names for the selected table"""
        if not self.selected_table or self.selected_table not in self.tables:
            return ['<no columns>']
        
        columns = [col['name'] for col in self.tables[self.selected_table]]
        return columns if columns else ['<no columns>']

    def update_where_dropdowns(self):
        """Update WHERE column dropdowns with available columns"""
        columns = self.get_columns_for_table()
        
        # Update SELECT WHERE dropdown
        menu1 = self.where_column_menu['menu']
        menu1.delete(0, 'end')
        for col in columns:
            menu1.add_command(label=col, command=lambda c=col: self.where_column_var.set(c))
        # NU mai seta valoarea automată aici - păstrează ce a selectat userul
        if not self.where_column_var.get() or self.where_column_var.get() not in columns:
            if columns and columns[0] != '<no columns>':
                self.where_column_var.set(columns[0])
            else:
                self.where_column_var.set('')
        
        # Update UPDATE WHERE dropdown
        menu2 = self.where_column_menu2['menu']
        menu2.delete(0, 'end')
        for col in columns:
            menu2.add_command(label=col, command=lambda c=col: self.where_column_var2.set(c))
        if not self.where_column_var2.get() or self.where_column_var2.get() not in columns:
            if columns and columns[0] != '<no columns>':
                self.where_column_var2.set(columns[0])
            else:
                self.where_column_var2.set('')
        
        # Update DELETE WHERE dropdown
        menu3 = self.where_column_menu3['menu']
        menu3.delete(0, 'end')
        for col in columns:
            menu3.add_command(label=col, command=lambda c=col: self.where_column_var3.set(c))
        if not self.where_column_var3.get() or self.where_column_var3.get() not in columns:
            if columns and columns[0] != '<no columns>':
                self.where_column_var3.set(columns[0])
            else:
                self.where_column_var3.set('')
            
    def validate_sql_identifier(self, name):
        """Validate SQL identifier to prevent SQL injection"""
        if not name:
            return False
            
        parts = name.split('.')
        if len(parts) > 2:  # Max table.column
            return False
            
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        return all(bool(re.match(pattern, part.strip())) for part in parts)
    
        # Allow alphanumeric, underscores, dots (for table.column), and spaces
        #pattern = r'^[a-zA-Z_][a-zA-Z0-9_. ]*$'
        #return bool(re.match(pattern, name))
    
    def sanitize_value(self, value, use_quotes=True):
        """Sanitize user input values"""
        if not use_quotes:
            # For numeric values, ensure it's actually a number
            try:
                float(value)
                return value
            except ValueError:
                return f"'{self.escape_sql_string(value)}'"
        return f"'{self.escape_sql_string(value)}'"
    
    def validate_like_pattern(self, pattern):
        """Validate and escape LIKE patterns"""
        # Escapare pentru % și _ dacă nu sunt wildcard-uri intenționate
        # Acest lucru depinde de cerințele tale
        return self.escape_sql_string(pattern)
    
    def escape_sql_string(self, value):
        """Escape single quotes in SQL strings"""
        value = value.replace('\\', '\\\\')  # Backslash mai întâi
        value = value.replace("'", "''")      # Single quotes
        return value
        #return value.replace("'", "''")
    
    def is_numeric_value(self, value):
        """Check if value is numeric"""
        try:
            float(value)
            return True
        except ValueError:
            return False
        
    def setup_ui(self):
        # Menu Bar
        menubar = tk.Menu(self.rootsqlquerycr)
        self.rootsqlquerycr.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Query", command=self.reset_query)
        file_menu.add_command(label="Exit", command=self.rootsqlquerycr.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main container
        main_frame = tk.Frame(self.rootsqlquerycr, bg="#c0c0c0", relief=tk.RAISED, bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top section - Query Type Selection
        query_type_frame = tk.LabelFrame(main_frame, text="Query Type", 
                                         bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        query_type_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.query_type_var = tk.StringVar(value="SELECT")
        query_types = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE TABLE"]
        
        for qt in query_types:
            rb = tk.Radiobutton(query_type_frame, text=qt, variable=self.query_type_var,
                               value=qt, bg="#c0c0c0", command=self.on_query_type_change)
            rb.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Middle section - 3 panels
        middle_frame = tk.Frame(main_frame, bg="#c0c0c0")
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Table Manager
        left_panel = tk.LabelFrame(middle_frame, text="Table Manager", 
                                   bg="#c0c0c0", relief=tk.GROOVE, bd=2, width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        left_panel.pack_propagate(False)
        
        # Table creation
        tk.Label(left_panel, text="New Table Name:", bg="#c0c0c0").pack(pady=5)
        self.table_name_entry = tk.Entry(left_panel, relief=tk.SUNKEN, bd=2)
        self.table_name_entry.pack(padx=5, fill=tk.X)
        self.table_name_entry.bind('<Return>', lambda e: self.add_table())
        
        tk.Button(left_panel, text="Add Table", command=self.add_table,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0").pack(pady=5)
        
        tk.Label(left_panel, text="Tables (double-click to select, Del to remove):", bg="#c0c0c0", font=("Arial", 8)).pack(pady=5)
        
        # Tables listbox with scrollbar
        tables_frame = tk.Frame(left_panel, bg="#c0c0c0")
        tables_frame.pack(padx=5, fill=tk.BOTH, expand=True)
        
        tables_scrollbar = tk.Scrollbar(tables_frame, relief=tk.SUNKEN, bd=2)
        tables_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tables_listbox = tk.Listbox(tables_frame, relief=tk.SUNKEN, bd=2, height=10,
                                         yscrollcommand=tables_scrollbar.set)
        self.tables_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tables_scrollbar.config(command=self.tables_listbox.yview)
        
        self.tables_listbox.bind('<<ListboxSelect>>', self.on_table_select)
        self.tables_listbox.bind('<Double-Button-1>', self.on_table_double_click)
        self.tables_listbox.bind('<Delete>', lambda e: self.remove_table())
        
        tk.Button(left_panel, text="Remove Table", command=self.remove_table,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0").pack(pady=5)
        tk.Button(left_panel, text="Clear All Tables", command=self.clear_all_tables,
                 relief=tk.RAISED, bd=2, bg="#ffcccc").pack(pady=2)
        
        # Center panel - Column Manager
        center_panel = tk.LabelFrame(middle_frame, text="Column Manager", 
                                     bg="#c0c0c0", relief=tk.GROOVE, bd=2, width=250)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        center_panel.pack_propagate(False)
        
        tk.Label(center_panel, text="Column Name:", bg="#c0c0c0").pack(pady=5)
        self.column_name_entry = tk.Entry(center_panel, relief=tk.SUNKEN, bd=2)
        self.column_name_entry.pack(padx=5, fill=tk.X)
        self.column_name_entry.bind('<Return>', lambda e: self.add_column())
        
        tk.Label(center_panel, text="Data Type:", bg="#c0c0c0").pack()
        self.column_type_var = tk.StringVar(value="VARCHAR(255)")
        type_frame = tk.Frame(center_panel, bg="#c0c0c0")
        type_frame.pack()
        
        types = ["VARCHAR(255)", "INT", "TEXT", "DATE", "DATETIME", "DECIMAL(10,2)", "BOOLEAN"]
        for i, dtype in enumerate(types):
            if i % 2 == 0:
                row_frame = tk.Frame(type_frame, bg="#c0c0c0")
                row_frame.pack()
            tk.Radiobutton(row_frame, text=dtype, variable=self.column_type_var,
                          value=dtype, bg="#c0c0c0").pack(side=tk.LEFT, padx=5)
        
        tk.Button(center_panel, text="Add Column to Selected Table", 
                 command=self.add_column, relief=tk.RAISED, bd=2, bg="#c0c0c0").pack(pady=5)
        
        tk.Label(center_panel, text="Columns (double-click to SELECT, Del to remove):", bg="#c0c0c0", font=("Arial", 8)).pack(pady=5)
        
        # Columns listbox with scrollbar
        columns_frame = tk.Frame(center_panel, bg="#c0c0c0")
        columns_frame.pack(padx=5, fill=tk.BOTH, expand=True)
        
        columns_scrollbar = tk.Scrollbar(columns_frame, relief=tk.SUNKEN, bd=2)
        columns_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.columns_listbox = tk.Listbox(columns_frame, relief=tk.SUNKEN, bd=2, height=8,
                                          yscrollcommand=columns_scrollbar.set)
        self.columns_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        columns_scrollbar.config(command=self.columns_listbox.yview)
        
        self.columns_listbox.bind('<Double-Button-1>', self.on_column_double_click)
        self.columns_listbox.bind('<Delete>', lambda e: self.remove_column())
        
        tk.Button(center_panel, text="Remove Column", command=self.remove_column,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0").pack(pady=5)
        tk.Button(center_panel, text="Clear All Columns", command=self.clear_all_columns,
                 relief=tk.RAISED, bd=2, bg="#ffcccc").pack(pady=2)
        
        # Right panel - Query Builder
        right_panel = tk.LabelFrame(middle_frame, text="Query Builder", 
                                    bg="#c0c0c0", relief=tk.GROOVE, bd=2, width=350)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        right_panel.pack_propagate(False)
        
        # Create a notebook-style container for different query types
        self.query_builder_container = tk.Frame(right_panel, bg="#c0c0c0")
        self.query_builder_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # SELECT Query Builder
        self.select_builder = tk.Frame(self.query_builder_container, bg="#c0c0c0")
        
        # Step 1: Select Columns
        step1_frame = tk.LabelFrame(self.select_builder, text="Step 1: Select Columns", 
                                    bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        step1_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        
        tk.Label(step1_frame, text="Double-click columns from the middle panel", 
                bg="#c0c0c0", font=("Arial", 8, "italic")).pack(pady=2)
        
        select_frame = tk.Frame(step1_frame, bg="#c0c0c0")
        select_frame.pack(padx=5, fill=tk.BOTH, expand=True)
        
        select_scrollbar = tk.Scrollbar(select_frame, relief=tk.SUNKEN, bd=2)
        select_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.select_columns_listbox = tk.Listbox(select_frame, relief=tk.SUNKEN, 
                                                 bd=2, height=3, bg="#ffffff",
                                                 yscrollcommand=select_scrollbar.set)
        self.select_columns_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        select_scrollbar.config(command=self.select_columns_listbox.yview)
        self.select_columns_listbox.bind('<Double-Button-1>', self.on_select_double_click)
        
        btn_frame = tk.Frame(step1_frame, bg="#c0c0c0")
        btn_frame.pack(pady=2)
        
        tk.Button(btn_frame, text="Add Selected Column", command=self.add_to_select,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0", width=15).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Clear All", command=self.clear_select,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0", width=10).pack(side=tk.LEFT, padx=2)
        
        # Step 2: WHERE Conditions
        step2_frame = tk.LabelFrame(self.select_builder, text="Step 2: Add WHERE Conditions (Optional)", 
                                    bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        step2_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        
        tk.Label(step2_frame, text="Build your filter conditions:", 
                bg="#c0c0c0", font=("Arial", 8, "italic")).pack(pady=2)
        
        where_input_frame = tk.Frame(step2_frame, bg="#c0c0c0")
        where_input_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(where_input_frame, text="Column:", bg="#c0c0c0", width=7).pack(side=tk.LEFT)
        self.where_column_var = tk.StringVar(value='')
        self.where_column_menu = tk.OptionMenu(where_input_frame, self.where_column_var, '')
        self.where_column_menu.config(relief=tk.RAISED, bd=2, bg="#c0c0c0", width=10)
        self.where_column_menu.pack(side=tk.LEFT, padx=2)
        
        self.where_op_var = tk.StringVar(value="=")
        ops = ["=", "!=", ">", "<", ">=", "<=", "LIKE"]
        self.where_op = tk.OptionMenu(where_input_frame, self.where_op_var, *ops)
        self.where_op.config(relief=tk.RAISED, bd=2, bg="#c0c0c0", width=4)
        self.where_op.pack(side=tk.LEFT, padx=2)
        
        tk.Label(where_input_frame, text="Value:", bg="#c0c0c0").pack(side=tk.LEFT)
        self.where_value = tk.Entry(where_input_frame, relief=tk.SUNKEN, bd=2, width=10)
        self.where_value.pack(side=tk.LEFT, padx=2)
        
        self.where_value.bind('<Return>', lambda e: self.add_where_condition())
        
        tk.Button(where_input_frame, text="Add", command=self.add_where_condition,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0", width=5).pack(side=tk.LEFT, padx=2)
        
        where_list_frame = tk.Frame(step2_frame, bg="#c0c0c0")
        where_list_frame.pack(padx=5, fill=tk.BOTH, expand=True, pady=2)
        
        where_list_scrollbar = tk.Scrollbar(where_list_frame, relief=tk.SUNKEN, bd=2)
        where_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.where_listbox = tk.Listbox(where_list_frame, relief=tk.SUNKEN, bd=2, height=2,
                                        yscrollcommand=where_list_scrollbar.set)
        self.where_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        where_list_scrollbar.config(command=self.where_listbox.yview)
        self.where_listbox.bind('<Double-Button-1>', self.on_where_double_click)
        
        # Step 3: ORDER BY
        step3_frame = tk.LabelFrame(self.select_builder, text="Step 3: Sort Results (Optional)", 
                                    bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        step3_frame.pack(fill=tk.X, pady=2)
        
        order_input_frame = tk.Frame(step3_frame, bg="#c0c0c0")
        order_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(order_input_frame, text="Column:", bg="#c0c0c0").pack(side=tk.LEFT, padx=2)
        self.order_by_entry = tk.Entry(order_input_frame, relief=tk.SUNKEN, bd=2, width=12)
        self.order_by_entry.pack(side=tk.LEFT, padx=2)
        self.order_by_entry.bind('<Return>', lambda e: self.add_order_by())
        
        self.order_dir_var = tk.StringVar(value="ASC")
        tk.Radiobutton(order_input_frame, text="ASC", variable=self.order_dir_var,
                      value="ASC", bg="#c0c0c0").pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(order_input_frame, text="DESC", variable=self.order_dir_var,
                      value="DESC", bg="#c0c0c0").pack(side=tk.LEFT, padx=2)
        
        tk.Button(order_input_frame, text="Add", command=self.add_order_by,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0", width=5).pack(side=tk.LEFT, padx=2)
        
        # ORDER BY list
        order_list_frame = tk.Frame(step3_frame, bg="#c0c0c0")
        order_list_frame.pack(padx=5, fill=tk.X, pady=2)
        
        order_list_scrollbar = tk.Scrollbar(order_list_frame, relief=tk.SUNKEN, bd=2, orient=tk.HORIZONTAL)
        order_list_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.order_listbox = tk.Listbox(order_list_frame, relief=tk.SUNKEN, bd=2, height=2,
                                        xscrollcommand=order_list_scrollbar.set)
        self.order_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        order_list_scrollbar.config(command=self.order_listbox.xview)
        self.order_listbox.bind('<Double-Button-1>', self.on_order_double_click)
        
        # Step 4: GROUP BY
        step4_frame = tk.LabelFrame(self.select_builder, text="Step 4: Group Results (Optional)", 
                                    bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        step4_frame.pack(fill=tk.X, pady=2)
        
        group_input_frame = tk.Frame(step4_frame, bg="#c0c0c0")
        group_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(group_input_frame, text="Group by:", bg="#c0c0c0").pack(side=tk.LEFT, padx=2)
        self.group_by_entry = tk.Entry(group_input_frame, relief=tk.SUNKEN, bd=2, width=20)
        self.group_by_entry.pack(side=tk.LEFT, padx=2)
        
        # Step 5: LIMIT
        step5_frame = tk.Frame(self.select_builder, bg="#c0c0c0")
        step5_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(step5_frame, text="Limit:", bg="#c0c0c0").pack(side=tk.LEFT, padx=5)
        self.limit_var = tk.StringVar(value="")
        self.limit_entry = tk.Entry(step5_frame, textvariable=self.limit_var, 
                                    relief=tk.SUNKEN, bd=2, width=8)
        self.limit_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(step5_frame, text="rows", bg="#c0c0c0", font=("Arial", 8, "italic")).pack(side=tk.LEFT)
        
        # INSERT Builder
        self.insert_builder = tk.Frame(self.query_builder_container, bg="#c0c0c0")
        
        insert_info = tk.LabelFrame(self.insert_builder, text="INSERT Query Info", 
                                   bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        insert_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(insert_info, text="1. Select a table from the left panel", 
                bg="#c0c0c0", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=5)
        tk.Label(insert_info, text="2. Make sure the table has columns defined", 
                bg="#c0c0c0", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=5)
        tk.Label(insert_info, text="3. Click 'Generate SQL' to create INSERT template", 
                bg="#c0c0c0", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=5)
        tk.Label(insert_info, text="4. Replace ? placeholders with actual values", 
                bg="#c0c0c0", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=5)
        
        # UPDATE Builder
        self.update_builder = tk.Frame(self.query_builder_container, bg="#c0c0c0")
        
        update_step1 = tk.LabelFrame(self.update_builder, text="Step 1: Select Table", 
                                    bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        update_step1.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(update_step1, text="Select the table to update from the left panel", 
                bg="#c0c0c0", font=("Arial", 9)).pack(padx=10, pady=5)
        
        update_step2 = tk.LabelFrame(self.update_builder, text="Step 2: Add WHERE Conditions", 
                                    bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        update_step2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(update_step2, text="IMPORTANT: Add WHERE conditions!", 
                bg="#c0c0c0", font=("Arial", 9, "bold"), fg="#800000").pack(padx=10, pady=5)
        
        where_input_frame2 = tk.Frame(update_step2, bg="#c0c0c0")
        where_input_frame2.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(where_input_frame2, text="Column:", bg="#c0c0c0", width=7).pack(side=tk.LEFT)
        self.where_column_var2 = tk.StringVar(value='')
        self.where_column_menu2 = tk.OptionMenu(where_input_frame2, self.where_column_var2, '')
        self.where_column_menu2.config(relief=tk.RAISED, bd=2, bg="#c0c0c0", width=10)
        self.where_column_menu2.pack(side=tk.LEFT, padx=2)
        
        self.where_op_var2 = tk.StringVar(value="=")
        self.where_op2 = tk.OptionMenu(where_input_frame2, self.where_op_var2, *ops)
        self.where_op2.config(relief=tk.RAISED, bd=2, bg="#c0c0c0", width=4)
        self.where_op2.pack(side=tk.LEFT, padx=2)
        
        tk.Label(where_input_frame2, text="Value:", bg="#c0c0c0").pack(side=tk.LEFT)
        self.where_value2 = tk.Entry(where_input_frame2, relief=tk.SUNKEN, bd=2, width=10)
        self.where_value2.pack(side=tk.LEFT, padx=2)
        
        tk.Button(where_input_frame2, text="Add", command=self.add_where_condition_update,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0", width=5).pack(side=tk.LEFT, padx=2)
        
        where_list_frame2 = tk.Frame(update_step2, bg="#c0c0c0")
        where_list_frame2.pack(padx=5, fill=tk.BOTH, expand=True, pady=2)
        
        where_list_scrollbar2 = tk.Scrollbar(where_list_frame2, relief=tk.SUNKEN, bd=2)
        where_list_scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.where_listbox2 = tk.Listbox(where_list_frame2, relief=tk.SUNKEN, bd=2, height=3,
                                         yscrollcommand=where_list_scrollbar2.set)
        self.where_listbox2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        where_list_scrollbar2.config(command=self.where_listbox2.yview)
        self.where_listbox2.bind('<Double-Button-1>', self.on_where_double_click_update)
        
        # DELETE Builder
        self.delete_builder = tk.Frame(self.query_builder_container, bg="#c0c0c0")
        
        delete_step1 = tk.LabelFrame(self.delete_builder, text="Step 1: Select Table", 
                                    bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        delete_step1.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(delete_step1, text="Select the table to delete from (left panel)", 
                bg="#c0c0c0", font=("Arial", 9)).pack(padx=10, pady=5)
        
        delete_step2 = tk.LabelFrame(self.delete_builder, text="Step 2: Add WHERE Conditions", 
                                    bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        delete_step2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(delete_step2, text="WARNING: Without WHERE, ALL ROWS will be deleted!", 
                bg="#c0c0c0", font=("Arial", 9, "bold"), fg="#ff0000").pack(padx=10, pady=5)
        
        where_input_frame3 = tk.Frame(delete_step2, bg="#c0c0c0")
        where_input_frame3.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(where_input_frame3, text="Column:", bg="#c0c0c0", width=7).pack(side=tk.LEFT)
        self.where_column_var3 = tk.StringVar(value='')
        self.where_column_menu3 = tk.OptionMenu(where_input_frame3, self.where_column_var3, '')
        self.where_column_menu3.config(relief=tk.RAISED, bd=2, bg="#c0c0c0", width=10)
        self.where_column_menu3.pack(side=tk.LEFT, padx=2)
        
        self.where_op_var3 = tk.StringVar(value="=")
        self.where_op3 = tk.OptionMenu(where_input_frame3, self.where_op_var3, *ops)
        self.where_op3.config(relief=tk.RAISED, bd=2, bg="#c0c0c0", width=4)
        self.where_op3.pack(side=tk.LEFT, padx=2)
        
        tk.Label(where_input_frame3, text="Value:", bg="#c0c0c0").pack(side=tk.LEFT)
        self.where_value3 = tk.Entry(where_input_frame3, relief=tk.SUNKEN, bd=2, width=10)
        self.where_value3.pack(side=tk.LEFT, padx=2)
        
        tk.Button(where_input_frame3, text="Add", command=self.add_where_condition_delete,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0", width=5).pack(side=tk.LEFT, padx=2)
        
        where_list_frame3 = tk.Frame(delete_step2, bg="#c0c0c0")
        where_list_frame3.pack(padx=5, fill=tk.BOTH, expand=True, pady=2)
        
        where_list_scrollbar3 = tk.Scrollbar(where_list_frame3, relief=tk.SUNKEN, bd=2)
        where_list_scrollbar3.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.where_listbox3 = tk.Listbox(where_list_frame3, relief=tk.SUNKEN, bd=2, height=3,
                                         yscrollcommand=where_list_scrollbar3.set)
        self.where_listbox3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        where_list_scrollbar3.config(command=self.where_listbox3.yview)
        self.where_listbox3.bind('<Double-Button-1>', self.on_where_double_click_delete)
        
        # CREATE TABLE Builder
        self.create_builder = tk.Frame(self.query_builder_container, bg="#c0c0c0")
        
        create_info = tk.LabelFrame(self.create_builder, text="CREATE TABLE Instructions", 
                                   bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        create_info.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(create_info, text="How to create a table:", 
                bg="#c0c0c0", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10, pady=5)
        tk.Label(create_info, text="1. Enter table name in the left panel", 
                bg="#c0c0c0", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=3)
        tk.Label(create_info, text="2. Click 'Add Table' button", 
                bg="#c0c0c0", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=3)
        tk.Label(create_info, text="3. Select the table from the list", 
                bg="#c0c0c0", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=3)
        tk.Label(create_info, text="4. In the center panel, add columns with types", 
                bg="#c0c0c0", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=3)
        tk.Label(create_info, text="5. Click 'Generate SQL' to see CREATE TABLE statement", 
                bg="#c0c0c0", font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=3)
        
        # Show SELECT builder by default
        self.select_builder.pack(fill=tk.BOTH, expand=True)
        
        # Bottom section - Generated SQL
        bottom_frame = tk.LabelFrame(main_frame, text="Generated SQL Query", 
                                     bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.sql_output = scrolledtext.ScrolledText(bottom_frame, height=8, 
                                                    relief=tk.SUNKEN, bd=2,
                                                    font=("Courier", 10))
        self.sql_output.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        # Button bar
        button_bar = tk.Frame(main_frame, bg="#c0c0c0")
        button_bar.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(button_bar, text="Generate SQL (F5)", command=self.generate_sql,
                 relief=tk.RAISED, bd=3, bg="#c0c0c0", width=18, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(button_bar, text="Copy to Clipboard (F6)", command=self.copy_to_clipboard,
                 relief=tk.RAISED, bd=3, bg="#c0c0c0", width=18, height=2).pack(side=tk.LEFT, padx=5)
        tk.Button(button_bar, text="Clear Query (F7)", command=self.reset_query,
                 relief=tk.RAISED, bd=3, bg="#c0c0c0", width=18, height=2).pack(side=tk.LEFT, padx=5)
        
        # Add keyboard shortcuts
        self.rootsqlquerycr.bind('<F5>', lambda e: self.generate_sql())
        self.rootsqlquerycr.bind('<F6>', lambda e: self.copy_to_clipboard())
        self.rootsqlquerycr.bind('<F7>', lambda e: self.reset_query())
        
        # Status bar
        self.status_bar = tk.Label(main_frame, text="Ready", bg="#c0c0c0", 
                                   relief=tk.SUNKEN, bd=1, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=5, pady=2)
        
    def set_status(self, message):
        self.status_bar.config(text=message)
        self.rootsqlquerycr.update_idletasks()
        
    def add_table(self):
        table_name = self.table_name_entry.get().strip()
        if not table_name:
            messagebox.showwarning("Warning", "Please enter a table name")
            return
        
        if not self.validate_sql_identifier(table_name):
            messagebox.showerror("Invalid Name", 
                               "Table name must start with a letter or underscore\n"
                               "and contain only letters, numbers, and underscores.")
            return
        
        if table_name in self.tables:
            messagebox.showwarning("Warning", "Table already exists")
            return
        
        self.tables[table_name] = []
        self.tables_listbox.insert(tk.END, table_name)
        self.table_name_entry.delete(0, tk.END)
        self.set_status(f"Table '{table_name}' added successfully")
        self.table_name_entry.focus()
        
    def remove_table(self):
        selection = self.tables_listbox.curselection()
        if not selection:
            self.set_status("No table selected to remove")
            return
        
        table_name = self.tables_listbox.get(selection[0])
        del self.tables[table_name]
        self.tables_listbox.delete(selection[0])
        self.columns_listbox.delete(0, tk.END)
        self.set_status(f"Table '{table_name}' removed")
        
    def on_table_select(self, event):
        selection = self.tables_listbox.curselection()
        if not selection:
            return
        
        self.selected_table = self.tables_listbox.get(selection[0])
        self.update_columns_list()
        self.set_status(f"Selected table: {self.selected_table}")
    
    def on_table_double_click(self, event):
        self.on_table_select(event)
        
    def on_column_double_click(self, event):
        self.add_to_select()
        
    def on_select_double_click(self, event):
        self.remove_from_select()
        
    def on_where_double_click(self, event):
        self.remove_where_condition()
    
    def on_order_double_click(self, event):
        selection = self.order_listbox.curselection()
        if selection:
            self.order_listbox.delete(selection[0])
            self.set_status("Removed ORDER BY column")
        
    def update_columns_list(self):
        self.columns_listbox.delete(0, tk.END)
        if self.selected_table and self.selected_table in self.tables:
            for col in self.tables[self.selected_table]:
                self.columns_listbox.insert(tk.END, f"{col['name']} ({col['type']})")
        
        # Actualizează dropdown-urile WHERE
        self.update_where_dropdowns()
        
    def add_column(self):
        if not self.selected_table:
            messagebox.showwarning("Warning", "Please select a table first")
            return
        
        col_name = self.column_name_entry.get().strip()
        if not col_name:
            messagebox.showwarning("Warning", "Please enter a column name")
            return
        
        if not self.validate_sql_identifier(col_name):
            messagebox.showerror("Invalid Name", 
                               "Column name must start with a letter or underscore\n"
                               "and contain only letters, numbers, and underscores.")
            return
        
        col_type = self.column_type_var.get()
        self.tables[self.selected_table].append({
            'name': col_name,
            'type': col_type
        })
        
        self.update_columns_list()
        self.column_name_entry.delete(0, tk.END)
        self.set_status(f"Column '{col_name}' added to table '{self.selected_table}'")
        self.column_name_entry.focus()
        
    def remove_column(self):
        selection = self.columns_listbox.curselection()
        if not selection or not self.selected_table:
            self.set_status("No column selected to remove")
            return
        
        idx = selection[0]
        col_name = self.tables[self.selected_table][idx]['name']
        del self.tables[self.selected_table][idx]
        self.update_columns_list()
        self.set_status(f"Column '{col_name}' removed")
        
    def add_to_select(self):
        selection = self.columns_listbox.curselection()
        if not selection or not self.selected_table:
            self.set_status("No column selected")
            return
        
        idx = selection[0]
        col = self.tables[self.selected_table][idx]
        # Permite atât cu cât și fără prefix de tabel
        col_str = f"{self.selected_table}.{col['name']}"
        
        # Nu mai validăm aici pentru că știm că coloana e validă
        current_items = self.select_columns_listbox.get(0, tk.END)
        if col_str not in current_items:
            self.select_columns_listbox.insert(tk.END, col_str)
            self.set_status(f"Added '{col_str}' to SELECT")
        else:
            self.set_status(f"Column '{col_str}' already in SELECT")
        
    def remove_from_select(self):
        selection = self.select_columns_listbox.curselection()
        if selection:
            col = self.select_columns_listbox.get(selection[0])
            self.select_columns_listbox.delete(selection[0])
            self.set_status(f"Removed '{col}' from SELECT")
        else:
            self.set_status("No column selected to remove")
        
    def clear_select(self):
        count = self.select_columns_listbox.size()
        self.select_columns_listbox.delete(0, tk.END)
        self.set_status(f"Cleared {count} column(s) from SELECT")
        
    def add_where_condition(self):
        col = self.where_column_var.get().strip()
        op = self.where_op_var.get()
        val = self.where_value.get().strip()
        
        if not col or not val or col == '<no columns>':
            messagebox.showwarning("Warning", "Please fill all WHERE condition fields")
            return
        
        col_parts = col.split('.')
        col_to_validate = col_parts[-1].strip()

        if not self.validate_sql_identifier(col_to_validate):
            messagebox.showerror("Invalid Column", "Column name contains invalid characters")
            return
        
        formatted_val = self.auto_format_value(val, col_to_validate)
        condition = f"{col} {op} {formatted_val}"
        
        print(f"ÎNAINTE de insert: {list(self.where_listbox.get(0, tk.END))}")  # DEBUG
        self.where_listbox.insert(tk.END, condition)
        print(f"DUPĂ insert: {list(self.where_listbox.get(0, tk.END))}")  # DEBUG
        
        self.where_value.delete(0, tk.END)
        self.set_status(f"Added WHERE condition: {condition}")
        self.where_value.focus()
    
    def add_where_condition_update(self):
        col = self.where_column_var2.get().strip()  # SCHIMBAT
        op = self.where_op_var2.get()
        val = self.where_value2.get().strip()
        
        if not col or not val or col == '<no columns>':
            messagebox.showwarning("Warning", "Please fill all WHERE condition fields")
            return
        
        col_parts = col.split('.')
        col_to_validate = col_parts[-1].strip()
        
        if not self.validate_sql_identifier(col_to_validate):
            messagebox.showerror("Invalid Column", "Column name contains invalid characters")
            return
        
        # AUTO-FORMATARE bazată pe tipul coloanei
        formatted_val = self.auto_format_value(val, col_to_validate)
        
        condition = f"{col} {op} {formatted_val}"
        self.where_listbox2.insert(tk.END, condition)
        
        self.where_value2.delete(0, tk.END)
        self.set_status(f"Added WHERE condition for UPDATE: {condition}")
        self.where_value2.focus()  # SCHIMBAT
    
    def add_where_condition_delete(self):
        col = self.where_column_var3.get().strip()  # SCHIMBAT
        op = self.where_op_var3.get()
        val = self.where_value3.get().strip()
        
        if not col or not val or col == '<no columns>':
            messagebox.showwarning("Warning", "Please fill all WHERE condition fields")
            return
        
        col_parts = col.split('.')
        col_to_validate = col_parts[-1].strip()
        
        if not self.validate_sql_identifier(col_to_validate):
            messagebox.showerror("Invalid Column", "Column name contains invalid characters")
            return
        
        # AUTO-FORMATARE bazată pe tipul coloanei
        formatted_val = self.auto_format_value(val, col_to_validate)
        
        condition = f"{col} {op} {formatted_val}"
        self.where_listbox3.insert(tk.END, condition)
        
        self.where_value3.delete(0, tk.END)
        self.set_status(f"Added WHERE condition for DELETE: {condition}")
        self.where_value3.focus()  # SCHIMBAT
        
    def remove_where_condition(self):
        selection = self.where_listbox.curselection()
        if selection:
            self.where_listbox.delete(selection[0])
            self.set_status(f"Removed WHERE condition")
        else:
            self.set_status("No WHERE condition selected to remove")
    
    def on_where_double_click_update(self, event):
        selection = self.where_listbox2.curselection()
        if selection:
            self.where_listbox2.delete(selection[0])
            self.set_status("Removed WHERE condition")
    
    def on_where_double_click_delete(self, event):
        selection = self.where_listbox3.curselection()
        if selection:
            self.where_listbox3.delete(selection[0])
            self.set_status("Removed WHERE condition")
    
    def add_order_by(self):
        col = self.order_by_entry.get().strip()
        if not col:
            messagebox.showwarning("Warning", "Please enter a column name")
            return
        
        col_parts = col.split('.')
        col_to_validate = col_parts[-1].strip()
        
        if not self.validate_sql_identifier(col_to_validate):
            messagebox.showerror("Invalid Column", "Column name contains invalid characters")
            return
        
        direction = self.order_dir_var.get()
        order_str = f"{col} {direction}"
        
        self.order_listbox.insert(tk.END, order_str)
        self.order_by_entry.delete(0, tk.END)
        self.set_status(f"Added ORDER BY: {order_str}")
        self.order_by_entry.focus()
        
    def on_query_type_change(self):
        self.current_query_type = self.query_type_var.get()
        
        # Hide all builders
        self.select_builder.pack_forget()
        self.insert_builder.pack_forget()
        self.update_builder.pack_forget()
        self.delete_builder.pack_forget()
        self.create_builder.pack_forget()
        
        # Show the appropriate builder
        if self.current_query_type == "SELECT":
            self.select_builder.pack(fill=tk.BOTH, expand=True)
            self.set_status("SELECT query mode - Choose columns and conditions")
        elif self.current_query_type == "INSERT":
            self.insert_builder.pack(fill=tk.BOTH, expand=True)
            self.set_status("INSERT query mode - Select a table with columns")
        elif self.current_query_type == "UPDATE":
            self.update_builder.pack(fill=tk.BOTH, expand=True)
            self.set_status("UPDATE query mode - Select table and add WHERE conditions")
        elif self.current_query_type == "DELETE":
            self.delete_builder.pack(fill=tk.BOTH, expand=True)
            self.set_status("DELETE query mode - Add WHERE conditions to avoid deleting all rows")
        elif self.current_query_type == "CREATE TABLE":
            self.create_builder.pack(fill=tk.BOTH, expand=True)
            self.set_status("CREATE TABLE mode - Add table and columns from left panels")
    
    def clear_all_tables(self):
        """Clear all tables with confirmation"""
        if not self.tables:
            self.set_status("No tables to clear")
            return
        
        count = len(self.tables)
        result = messagebox.askyesno("Confirm Clear All", 
                                     f"Are you sure you want to delete all {count} table(s)?\n"
                                     "This action cannot be undone.",
                                     icon='warning')
        if result:
            self.tables.clear()
            self.tables_listbox.delete(0, tk.END)
            self.columns_listbox.delete(0, tk.END)
            self.selected_table = None
            self.set_status(f"All {count} table(s) cleared successfully")
        else:
            self.set_status("Clear all tables cancelled")
    
    def clear_all_columns(self):
        """Clear all columns from selected table with confirmation"""
        if not self.selected_table:
            self.set_status("No table selected")
            return
        
        if not self.tables[self.selected_table]:
            self.set_status("No columns to clear")
            return
        
        count = len(self.tables[self.selected_table])
        result = messagebox.askyesno("Confirm Clear All", 
                                     f"Are you sure you want to delete all {count} column(s) from '{self.selected_table}'?\n"
                                     "This action cannot be undone.",
                                     icon='warning')
        if result:
            self.tables[self.selected_table].clear()
            self.update_columns_list()
            self.set_status(f"All {count} column(s) cleared from '{self.selected_table}'")
        else:
            self.set_status("Clear all columns cancelled")
    
    def generate_sql(self):
        query_type = self.query_type_var.get()
        sql = ""
        
        if query_type == "SELECT":
            sql = self.generate_select()
        elif query_type == "INSERT":
            sql = self.generate_insert()
        elif query_type == "UPDATE":
            sql = self.generate_update()
        elif query_type == "DELETE":
            sql = self.generate_delete()
        elif query_type == "CREATE TABLE":
            sql = self.generate_create_table()
        
        self.sql_output.delete(1.0, tk.END)
        self.sql_output.insert(1.0, sql)
        self.set_status(f"{query_type} query generated successfully")
        
    def generate_select(self):
        columns = list(self.select_columns_listbox.get(0, tk.END))
        
        if not columns:
            columns_str = "*"
        else:
            columns_str = ",\n       ".join(columns)
        
        table_name = self.selected_table if self.selected_table else "table_name"
        
        sql = f"SELECT {columns_str}\nFROM {table_name}"
        
        # Add WHERE conditions
        where_conditions = list(self.where_listbox.get(0, tk.END))
        if where_conditions:
            sql += "\nWHERE " + "\n  AND ".join(where_conditions)
        
        # Add GROUP BY
        group_by = self.group_by_entry.get().strip()
        if group_by:
            sql += f"\nGROUP BY {group_by}"
        
        # Add ORDER BY
        order_by_items = list(self.order_listbox.get(0, tk.END))
        if order_by_items:
            sql += "\nORDER BY " + ", ".join(order_by_items)
        
        # Add LIMIT
        limit = self.limit_var.get().strip()
        if limit:
            try:
                int(limit)
                sql += f"\nLIMIT {limit}"
            except ValueError:
                pass
        
        sql += ";"
        return sql
        
    def generate_insert(self):
        if not self.selected_table:
            return "-- Please select a table first"
        
        columns = [col['name'] for col in self.tables[self.selected_table]]
        
        if not columns:
            return "-- Please add columns to the table first"
        
        columns_str = ", ".join(columns)
        values_str = ", ".join(["?" for _ in columns])
        
        sql = f"INSERT INTO {self.selected_table} ({columns_str})\nVALUES ({values_str});"
        return sql
        
    def generate_update(self):
        if not self.selected_table:
            return "-- Please select a table first"
        
        columns = [col['name'] for col in self.tables[self.selected_table]]
        
        if not columns:
            return "-- Please add columns to the table first"
        
        set_clause = ",\n       ".join([f"{col} = ?" for col in columns])
        
        sql = f"UPDATE {self.selected_table}\nSET {set_clause}"
        
        where_conditions = list(self.where_listbox2.get(0, tk.END))
        if where_conditions:
            sql += "\nWHERE " + "\n  AND ".join(where_conditions)
        else:
            sql += "\n-- WARNING: No WHERE clause! This will update all rows!"
        
        sql += ";"
        return sql
        
    def generate_delete(self):
        if not self.selected_table:
            return "-- Please select a table first"
        
        sql = f"DELETE FROM {self.selected_table}"
        
        where_conditions = list(self.where_listbox3.get(0, tk.END))
        if where_conditions:
            sql += "\nWHERE " + "\n  AND ".join(where_conditions)
        else:
            sql += "\n-- WARNING: No WHERE clause! This will delete all rows!"
        
        sql += ";"
        return sql
        
    def generate_create_table(self):
        if not self.selected_table:
            return "-- Please select a table first"
        
        columns = self.tables[self.selected_table]
        
        if not columns:
            return "-- Please add columns to the table first"
        
        sql = f"CREATE TABLE {self.selected_table} (\n"
        
        col_definitions = []
        for col in columns:
            col_definitions.append(f"    {col['name']} {col['type']}")
        
        sql += ",\n".join(col_definitions)
        sql += "\n);"
        
        return sql
        
    def copy_to_clipboard(self):
        sql = self.sql_output.get(1.0, tk.END).strip()
        if sql:
            self.rootsqlquerycr.clipboard_clear()
            self.rootsqlquerycr.clipboard_append(sql)
            self.set_status("SQL copied to clipboard!")
        else:
            self.set_status("No SQL to copy - generate a query first")
        
    def reset_query(self):
        self.select_columns_listbox.delete(0, tk.END)
        self.where_listbox.delete(0, tk.END)
        self.where_listbox2.delete(0, tk.END)
        self.where_listbox3.delete(0, tk.END)
        self.order_listbox.delete(0, tk.END)
        self.order_by_entry.delete(0, tk.END)
        self.group_by_entry.delete(0, tk.END)
        self.limit_var.set("")
        self.sql_output.delete(1.0, tk.END)
        self.set_status("Query cleared - ready for new query")
        
    def show_about(self):
        messagebox.showinfo("About SQL Creator", 
                          "A simple SQL query builder with improved security\n\n"
                          "Quick Tips:\n"
                          "- Double-click columns to add to SELECT\n"
                          "- Double-click items to remove them\n"
                          "- Press Enter in text fields to add items\n"
                          "- Use F5 to generate, F6 to copy, F7 to clear\n"
                          "- Check 'Numeric' for number comparisons\n\n"
                          "Features:\n"
                          "- SQL injection protection\n"
                          "- Multiple ORDER BY support\n"
                          "- GROUP BY clause\n"
                          "- Smart quote handling\n"
                          "- Input validation\n"
                          "- Support for all major SQL operations")

def main():
    rootsqlquerycr = tk.Tk()
    app = SQLCreator(rootsqlquerycr)
    rootsqlquerycr.mainloop()

if __name__ == "__main__":
    main() 