import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import ast
import os
from pathlib import Path


class CodeVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Code Logic Visualizer")
        self.root.geometry("1400x850")
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.window_bg = "#ffffff"
        self.title_bar = "#000080"
        self.button_face = "#c0c0c0"
        self.button_shadow = "#808080"
        self.button_highlight = "#ffffff"
        self.text_bg = "#ffffff"
        self.text_fg = "#000000"
        
        self.root.configure(bg=self.bg_color)
        
        self.current_file = None
        self.parsed_data = []
        self.tree_structure = []
        self.current_step = 0
        self.auto_play = False
        self.folder_files = {}  # Dictionary to store file paths
        self.current_folder = None  # Store current folder path
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title bar simulation
        title_frame = tk.Frame(self.root, bg=self.title_bar, height=30)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="Python Code Visualizer", 
                bg=self.title_bar, fg="white", 
                font=("MS Sans Serif", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Toolbar
        toolbar_frame = tk.Frame(self.root, bg=self.bg_color, relief=tk.RAISED, bd=2)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        self.create_win95_button(toolbar_frame, "Open File", self.open_file, 100).pack(side=tk.LEFT, padx=2, pady=2)
        self.create_win95_button(toolbar_frame, "Open Folder", self.open_folder, 100).pack(side=tk.LEFT, padx=2, pady=2)
        
        tk.Frame(toolbar_frame, bg=self.button_shadow, width=2, height=30).pack(side=tk.LEFT, padx=5)
        
        self.create_win95_button(toolbar_frame, "Analyze", self.start_visualization, 80).pack(side=tk.LEFT, padx=2, pady=2)
        
        tk.Frame(toolbar_frame, bg=self.button_shadow, width=2, height=30).pack(side=tk.LEFT, padx=5)
        
        self.create_win95_button(toolbar_frame, "Prev", self.prev_step, 60).pack(side=tk.LEFT, padx=2, pady=2)
        self.create_win95_button(toolbar_frame, "Next", self.next_step, 60).pack(side=tk.LEFT, padx=2, pady=2)
        self.create_win95_button(toolbar_frame, "Step Into", self.step_into, 80).pack(side=tk.LEFT, padx=2, pady=2)
        self.create_win95_button(toolbar_frame, "Step Out", self.step_out, 80).pack(side=tk.LEFT, padx=2, pady=2)
        
        tk.Frame(toolbar_frame, bg=self.button_shadow, width=2, height=30).pack(side=tk.LEFT, padx=5)
        
        self.create_win95_button(toolbar_frame, "Auto Play", self.toggle_auto_play, 80).pack(side=tk.LEFT, padx=2, pady=2)
        self.create_win95_button(toolbar_frame, "Reset", self.reset, 60).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Status label
        self.status_label = tk.Label(toolbar_frame, text="Ready", bg=self.bg_color, 
                                     fg=self.text_fg, font=("MS Sans Serif", 8))
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Main container with sunken border
        main_container = tk.Frame(self.root, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create main PanedWindow for horizontal resizing
        main_paned = tk.PanedWindow(main_container, orient=tk.HORIZONTAL, 
                                    sashwidth=5, sashrelief=tk.RAISED,
                                    bg=self.bg_color, bd=0)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - File tree
        left_panel = tk.Frame(main_paned, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        main_paned.add(left_panel, minsize=150, width=250)
        
        tk.Label(left_panel, text="Project Explorer", bg=self.title_bar, fg="white",
                font=("MS Sans Serif", 9, "bold"), anchor=tk.W).pack(fill=tk.X)
        
        tree_container = tk.Frame(left_panel, bg="white", relief=tk.SUNKEN, bd=1)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.file_tree = scrolledtext.ScrolledText(tree_container, wrap=tk.WORD,
                                                   bg="white", fg="black",
                                                   font=("MS Sans Serif", 9),
                                                   relief=tk.FLAT,
                                                   state=tk.DISABLED,
                                                   cursor="hand2")
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse wheel to file tree
        self.file_tree.bind('<MouseWheel>', lambda e: self._on_mousewheel(e, self.file_tree))
        self.file_tree.bind('<Button-4>', lambda e: self._on_mousewheel(e, self.file_tree))
        self.file_tree.bind('<Button-5>', lambda e: self._on_mousewheel(e, self.file_tree))
        
        # Bind double-click to open file
        self.file_tree.bind('<Double-Button-1>', self.on_file_tree_double_click)
        
        # Center panel - Code display
        center_panel = tk.Frame(main_paned, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        main_paned.add(center_panel, minsize=300)
        
        # Title bar with file path
        title_bar_frame = tk.Frame(center_panel, bg=self.title_bar, height=20)
        title_bar_frame.pack(fill=tk.X)
        title_bar_frame.pack_propagate(False)
        
        tk.Label(title_bar_frame, text="Source Code", bg=self.title_bar, fg="white",
                font=("MS Sans Serif", 9, "bold"), anchor=tk.W).pack(side=tk.LEFT, padx=5)
        
        self.file_path_label = tk.Label(title_bar_frame, text="", bg=self.title_bar, fg="#FFFF00",
                                        font=("MS Sans Serif", 8), anchor=tk.W)
        self.file_path_label.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        code_container = tk.Frame(center_panel, bg="white", relief=tk.SUNKEN, bd=1)
        code_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Line numbers
        line_frame = tk.Frame(code_container, bg="#e0e0e0", width=40)
        line_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.line_numbers = tk.Text(line_frame, width=4, bg="#e0e0e0", fg="#606060",
                                    font=("Courier New", 10), relief=tk.FLAT,
                                    state=tk.DISABLED)
        self.line_numbers.pack(fill=tk.BOTH, expand=True)
        
        # Code text with scrollbars
        code_text_frame = tk.Frame(code_container, bg="white")
        code_text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Horizontal scrollbar
        h_scrollbar = tk.Scrollbar(code_text_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Vertical scrollbar
        self.v_scrollbar = tk.Scrollbar(code_text_frame, orient=tk.VERTICAL)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.code_text = tk.Text(code_text_frame, wrap=tk.NONE,
                                bg="white", fg="black",
                                font=("Courier New", 10),
                                relief=tk.FLAT,
                                insertbackground="black",
                                state=tk.DISABLED,
                                xscrollcommand=h_scrollbar.set,
                                yscrollcommand=self._sync_scrollbars)
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        h_scrollbar.config(command=self.code_text.xview)
        self.v_scrollbar.config(command=self._sync_scroll)
        
        # Bind mouse wheel to code text
        self.code_text.bind('<MouseWheel>', lambda e: self._on_code_mousewheel(e))
        self.code_text.bind('<Button-4>', lambda e: self._on_code_mousewheel(e))
        self.code_text.bind('<Button-5>', lambda e: self._on_code_mousewheel(e))
        
        # Right panel - Tree visualization with vertical split
        right_panel = tk.Frame(main_paned, bg=self.bg_color, relief=tk.SUNKEN, bd=2)
        main_paned.add(right_panel, minsize=400, width=500)
        
        # Create vertical PanedWindow for canvas and info
        right_paned = tk.PanedWindow(right_panel, orient=tk.VERTICAL,
                                     sashwidth=5, sashrelief=tk.RAISED,
                                     bg=self.bg_color, bd=0)
        right_paned.pack(fill=tk.BOTH, expand=True)
        
        # Top part - Canvas
        canvas_panel = tk.Frame(right_paned, bg=self.bg_color)
        right_paned.add(canvas_panel, minsize=200)
        
        tk.Label(canvas_panel, text="Logic Flow Tree", bg=self.title_bar, fg="white",
                font=("MS Sans Serif", 9, "bold"), anchor=tk.W).pack(fill=tk.X)
        
        # Canvas for tree visualization
        canvas_container = tk.Frame(canvas_panel, bg="white", relief=tk.SUNKEN, bd=1)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        canvas_frame = tk.Frame(canvas_container, bg="white")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=0)
        scrollbar_y = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar_x = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse wheel to canvas
        self.canvas.bind('<MouseWheel>', lambda e: self._on_canvas_mousewheel(e))
        self.canvas.bind('<Button-4>', lambda e: self._on_canvas_mousewheel(e))
        self.canvas.bind('<Button-5>', lambda e: self._on_canvas_mousewheel(e))
        
        # Bottom part - Info panel
        info_panel = tk.Frame(right_paned, bg=self.bg_color)
        right_paned.add(info_panel, minsize=80, height=120)
        
        tk.Label(info_panel, text="Current Step", bg=self.title_bar, fg="white",
                font=("MS Sans Serif", 9, "bold"), anchor=tk.W).pack(fill=tk.X)
        
        self.info_text = scrolledtext.ScrolledText(info_panel, wrap=tk.WORD,
                                                   bg="white", fg="black",
                                                   font=("Courier New", 8),
                                                   relief=tk.FLAT,
                                                   state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Bind mouse wheel to info text
        self.info_text.bind('<MouseWheel>', lambda e: self._on_mousewheel(e, self.info_text))
        self.info_text.bind('<Button-4>', lambda e: self._on_mousewheel(e, self.info_text))
        self.info_text.bind('<Button-5>', lambda e: self._on_mousewheel(e, self.info_text))
        
        # Status bar at bottom
        status_bar = tk.Frame(self.root, bg=self.bg_color, relief=tk.SUNKEN, bd=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_text = tk.Label(status_bar, text="Ready", bg=self.bg_color, 
                                    fg=self.text_fg, font=("MS Sans Serif", 8), anchor=tk.W)
        self.status_text.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.step_label = tk.Label(status_bar, text="Step: 0/0", bg=self.bg_color,
                                   fg=self.text_fg, font=("MS Sans Serif", 8))
        self.step_label.pack(side=tk.RIGHT, padx=5, pady=2)
        
    def create_win95_button(self, parent, text, command, width):
        frame = tk.Frame(parent, bg=self.button_face, relief=tk.RAISED, bd=2)
        
        btn = tk.Label(frame, text=text, bg=self.button_face, fg=self.text_fg,
                      font=("MS Sans Serif", 9), width=width//7, cursor="hand2")
        btn.pack(padx=3, pady=3)
        
        def on_enter(e):
            frame.config(relief=tk.RAISED, bd=2)
            
        def on_leave(e):
            frame.config(relief=tk.RAISED, bd=2)
            
        def on_click(e):
            frame.config(relief=tk.SUNKEN, bd=2)
            self.root.after(100, lambda: frame.config(relief=tk.RAISED, bd=2))
            command()
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        btn.bind('<Button-1>', on_click)
        
        return frame
        
    def open_file(self):
        filename = filedialog.askopenfilename(
            title="Select Python file",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.current_file = filename
            self.load_file(filename)
            self.status_text.config(text=f"Loaded: {os.path.basename(filename)}")
            
            # If no folder is loaded, show just this file in tree
            if not self.current_folder:
                self.file_tree.config(state=tk.NORMAL)
                self.file_tree.delete(1.0, tk.END)
                self.file_tree.insert(1.0, f"[+] {os.path.basename(filename)}\n")
                self.file_tree.config(state=tk.DISABLED)
            
    def open_folder(self):
        folder = filedialog.askdirectory(title="Select folder with Python files")
        if folder:
            self.load_folder(folder)
            self.status_text.config(text=f"Loaded folder: {os.path.basename(folder)}")
            
    def load_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            self.code_text.config(state=tk.NORMAL)
            self.code_text.delete(1.0, tk.END)
            self.code_text.insert(1.0, code)
            self.code_text.config(state=tk.DISABLED)
            self.update_line_numbers()
            
            # Update file path label
            if self.current_folder:
                # Show relative path from folder
                try:
                    rel_path = Path(filepath).relative_to(self.current_folder)
                    self.file_path_label.config(text=f"- {rel_path}")
                except ValueError:
                    # File is outside the folder
                    self.file_path_label.config(text=f"- {os.path.basename(filepath)}")
            else:
                # Just show filename
                self.file_path_label.config(text=f"- {os.path.basename(filepath)}")
            
            # Don't modify file_tree if we have a folder loaded
            # This preserves the folder view when opening files from it
            
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, f"File: {os.path.basename(filepath)}\n")
            self.info_text.insert(tk.END, f"Lines: {code.count(chr(10)) + 1}\n")
            self.info_text.insert(tk.END, f"Size: {len(code)} bytes\n")
            
            if self.current_folder:
                self.info_text.insert(tk.END, f"\nFolder: {os.path.basename(self.current_folder)}\n")
                self.info_text.insert(tk.END, "Double-click other files to open\n")
            
            self.info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load file:\n{str(e)}")
            
    def load_folder(self, folder):
        py_files = list(Path(folder).rglob("*.py"))
        
        if not py_files:
            messagebox.showwarning("Warning", "No Python files found in folder")
            return
        
        # Store current folder
        self.current_folder = folder
        
        # Clear file paths dictionary
        self.folder_files = {}
        
        self.file_tree.config(state=tk.NORMAL)
        self.file_tree.delete(1.0, tk.END)
        self.file_tree.insert(1.0, f"[+] {os.path.basename(folder)}\n")
        
        # Configure tag for clickable files
        self.file_tree.tag_config("file_link", foreground="blue", underline=0)
        
        line_num = 2  # Start from line 2 (after folder name)
        for file in sorted(py_files):
            rel_path = file.relative_to(folder)
            depth = len(rel_path.parts) - 1
            indent = "  " * depth
            file_name = rel_path.name
            
            # Store the full path with line number as key
            self.folder_files[line_num] = str(file)
            
            # Insert file with tag
            start_pos = self.file_tree.index(tk.INSERT)
            self.file_tree.insert(tk.END, f"{indent}|- ")
            
            # Insert filename with clickable tag
            file_start = self.file_tree.index(tk.INSERT)
            self.file_tree.insert(tk.END, f"{file_name}\n")
            file_end = self.file_tree.index(tk.INSERT)
            
            # Apply tag to filename only
            self.file_tree.tag_add("file_link", file_start, f"{file_end}-1c")
            
            line_num += 1
        
        self.file_tree.config(state=tk.DISABLED)
            
        self.current_file = folder
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, f"Folder: {os.path.basename(folder)}\n")
        self.info_text.insert(tk.END, f"Found {len(py_files)} Python files\n")
        self.info_text.insert(tk.END, "Double-click a file to open it\n")
        self.info_text.config(state=tk.DISABLED)
        
    def update_line_numbers(self, event=None):
        line_count = self.code_text.get(1.0, tk.END).count('\n')
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, line_numbers_string)
        self.line_numbers.config(state=tk.DISABLED)
        
    def start_visualization(self):
        code = self.code_text.get(1.0, tk.END)
        
        if not code.strip():
            messagebox.showwarning("Warning", "No code to visualize")
            return
            
        try:
            tree = ast.parse(code)
            self.parsed_data = self.analyze_ast(tree)
            self.tree_structure = self.build_tree_structure(tree)
            self.current_step = 0
            self.draw_tree_visualization()
            self.status_text.config(text="Analysis complete. Use Next Step to navigate.")
            self.step_label.config(text=f"Step: 0/{len(self.parsed_data)}")
            
        except SyntaxError as e:
            messagebox.showerror("Syntax Error", f"Code has syntax errors:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not analyze code:\n{str(e)}")
            
    def analyze_ast(self, tree):
        elements = []
        
        class Analyzer(ast.NodeVisitor):
            def __init__(self, elements_list):
                self.elements = elements_list
                self.depth = 0
                
            def visit_FunctionDef(self, node):
                self.elements.append({
                    'type': 'function',
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'line': node.lineno,
                    'depth': self.depth,
                    'body_length': len(node.body)
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_ClassDef(self, node):
                self.elements.append({
                    'type': 'class',
                    'name': node.name,
                    'bases': [self.get_name(base) for base in node.bases],
                    'line': node.lineno,
                    'depth': self.depth,
                    'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_Import(self, node):
                self.elements.append({
                    'type': 'import',
                    'modules': [alias.name for alias in node.names],
                    'line': node.lineno,
                    'depth': self.depth
                })
                
            def visit_ImportFrom(self, node):
                self.elements.append({
                    'type': 'import_from',
                    'module': node.module or '',
                    'names': [alias.name for alias in node.names],
                    'line': node.lineno,
                    'depth': self.depth
                })
                
            def visit_If(self, node):
                self.elements.append({
                    'type': 'if',
                    'line': node.lineno,
                    'depth': self.depth,
                    'has_else': len(node.orelse) > 0
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_For(self, node):
                self.elements.append({
                    'type': 'for',
                    'target': self.get_name(node.target),
                    'line': node.lineno,
                    'depth': self.depth
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_While(self, node):
                self.elements.append({
                    'type': 'while',
                    'line': node.lineno,
                    'depth': self.depth
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_Try(self, node):
                self.elements.append({
                    'type': 'try',
                    'line': node.lineno,
                    'depth': self.depth,
                    'handlers': len(node.handlers)
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_With(self, node):
                self.elements.append({
                    'type': 'with',
                    'line': node.lineno,
                    'depth': self.depth
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_Assign(self, node):
                self.elements.append({
                    'type': 'assign',
                    'targets': [self.get_name(t) for t in node.targets],
                    'line': node.lineno,
                    'depth': self.depth
                })
                
            def visit_Return(self, node):
                self.elements.append({
                    'type': 'return',
                    'line': node.lineno,
                    'depth': self.depth
                })
                
            def get_name(self, node):
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    return f"{self.get_name(node.value)}.{node.attr}"
                else:
                    return "?"
                    
        analyzer = Analyzer(elements)
        analyzer.visit(tree)
        
        return elements
        
    def build_tree_structure(self, tree):
        structure = []
        
        class TreeBuilder(ast.NodeVisitor):
            def __init__(self, structure_list):
                self.structure = structure_list
                self.depth = 0
                
            def visit_Module(self, node):
                self.structure.append({
                    'type': 'module',
                    'name': 'Program Start',
                    'depth': 0,
                    'children': []
                })
                self.generic_visit(node)
                
            def visit_FunctionDef(self, node):
                self.structure.append({
                    'type': 'function',
                    'name': node.name,
                    'depth': self.depth,
                    'line': node.lineno,
                    'children': []
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_ClassDef(self, node):
                self.structure.append({
                    'type': 'class',
                    'name': node.name,
                    'depth': self.depth,
                    'line': node.lineno,
                    'children': []
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_If(self, node):
                self.structure.append({
                    'type': 'if',
                    'name': 'condition',
                    'depth': self.depth,
                    'line': node.lineno,
                    'children': []
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_For(self, node):
                target = node.target.id if isinstance(node.target, ast.Name) else 'item'
                self.structure.append({
                    'type': 'for',
                    'name': f'loop: {target}',
                    'depth': self.depth,
                    'line': node.lineno,
                    'children': []
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
            def visit_While(self, node):
                self.structure.append({
                    'type': 'while',
                    'name': 'condition',
                    'depth': self.depth,
                    'line': node.lineno,
                    'children': []
                })
                self.depth += 1
                self.generic_visit(node)
                self.depth -= 1
                
        builder = TreeBuilder(structure)
        builder.visit(tree)
        
        return structure
        
    def draw_tree_visualization(self):
        self.canvas.delete("all")
        
        if not self.tree_structure and not self.parsed_data:
            self.canvas.create_text(250, 200, text="No code analyzed yet",
                                   fill="black", font=("MS Sans Serif", 12))
            return
            
        # Draw tree structure
        x_start = 30
        y_start = 30
        y_spacing = 50
        x_spacing = 40
        
        # Icon colors for different types
        colors = {
            'module': '#000080',
            'class': '#800080',
            'function': '#008000',
            'if': '#FF0000',
            'for': '#FF8000',
            'while': '#FF8000',
            'try': '#800000',
            'import': '#000080',
            'import_from': '#000080',
            'assign': '#000000',
            'return': '#800080',
            'with': '#008080'
        }
        
        y = y_start
        prev_positions = {}
        
        for idx, item in enumerate(self.tree_structure):
            x = x_start + (item['depth'] * x_spacing)
            
            # Draw connection line to parent
            if item['depth'] > 0:
                parent_depth = item['depth'] - 1
                if parent_depth in prev_positions:
                    parent_y = prev_positions[parent_depth]
                    self.canvas.create_line(x - x_spacing + 8, parent_y + 8, 
                                          x - 15, y + 8,
                                          fill="#808080", width=1)
                    self.canvas.create_line(x - 15, y + 8, x, y + 8,
                                          fill="#808080", width=1)
            
            # Highlight current step
            is_current = False
            if self.current_step > 0 and idx < len(self.parsed_data):
                if self.parsed_data[self.current_step - 1].get('line') == item.get('line'):
                    is_current = True
            
            # Draw icon (folder or file)
            color = colors.get(item['type'], '#000000')
            
            if item['type'] in ['module', 'class']:
                # Folder icon
                self.draw_folder_icon(x, y, color, is_current)
            else:
                # File/document icon
                self.draw_file_icon(x, y, color, is_current)
            
            # Draw label
            label = item['name']
            if item['type'] in ['class', 'function']:
                label = f"{label}()"
                
            font = ("MS Sans Serif", 9, "bold" if is_current else "normal")
            text_color = "#FF0000" if is_current else "black"
            
            self.canvas.create_text(x + 25, y + 8, text=label, anchor=tk.W,
                                   fill=text_color, font=font)
            
            # Store position for connection lines
            prev_positions[item['depth']] = y
            
            y += y_spacing
            
        # Draw parsed data list on the right side
        list_x = 350
        list_y = y_start
        
        self.canvas.create_text(list_x, 10, text="Execution Steps:",
                               fill="black", font=("MS Sans Serif", 10, "bold"),
                               anchor=tk.W)
        
        max_steps = min(len(self.parsed_data), self.current_step + 1) if self.current_step > 0 else len(self.parsed_data)
        
        for idx, element in enumerate(self.parsed_data[:max_steps]):
            is_active = (idx == self.current_step - 1) if self.current_step > 0 else False
            
            # Draw step box
            box_x = list_x
            box_y = list_y + (idx * 35)
            box_width = 120
            box_height = 30
            
            # Win95 style raised/sunken button
            relief_color = "#FFFF00" if is_active else self.button_highlight
            shadow_color = "#000000" if is_active else self.button_shadow
            
            # Draw 3D effect
            self.canvas.create_rectangle(box_x, box_y, 
                                        box_x + box_width, box_y + box_height,
                                        fill=self.button_face, outline="black")
            
            # Highlight top-left
            self.canvas.create_line(box_x, box_y, box_x + box_width, box_y,
                                   fill=relief_color, width=2)
            self.canvas.create_line(box_x, box_y, box_x, box_y + box_height,
                                   fill=relief_color, width=2)
            
            # Shadow bottom-right
            self.canvas.create_line(box_x + box_width, box_y, 
                                   box_x + box_width, box_y + box_height,
                                   fill=shadow_color, width=2)
            self.canvas.create_line(box_x, box_y + box_height,
                                   box_x + box_width, box_y + box_height,
                                   fill=shadow_color, width=2)
            
            # Text
            color = colors.get(element['type'], '#000000')
            label_text = self.get_short_label(element)
            
            self.canvas.create_text(box_x + box_width//2, box_y + 8,
                                   text=element['type'].upper(),
                                   fill=color, font=("MS Sans Serif", 7, "bold"),
                                   anchor=tk.N)
            
            self.canvas.create_text(box_x + box_width//2, box_y + 20,
                                   text=label_text,
                                   fill="black", font=("MS Sans Serif", 7),
                                   anchor=tk.N)
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def draw_folder_icon(self, x, y, color, is_current):
        # Folder icon
        outline = "#FF0000" if is_current else "black"
        width = 2 if is_current else 1
        
        # Folder tab
        self.canvas.create_polygon(x, y + 3, x + 6, y + 3, x + 8, y, x + 12, y,
                                  fill=color, outline=outline, width=width)
        # Folder body
        self.canvas.create_rectangle(x, y + 3, x + 16, y + 16,
                                    fill=color, outline=outline, width=width)
        
    def draw_file_icon(self, x, y, color, is_current):
        # Document icon
        outline = "#FF0000" if is_current else "black"
        width = 2 if is_current else 1
        
        # Document body
        self.canvas.create_rectangle(x + 2, y, x + 14, y + 16,
                                    fill="white", outline=outline, width=width)
        # Folded corner
        self.canvas.create_polygon(x + 14, y, x + 14, y + 4, x + 10, y,
                                  fill="#C0C0C0", outline=outline, width=width)
        
        # Lines on document
        for i in range(3):
            self.canvas.create_line(x + 4, y + 4 + (i * 3), x + 12, y + 4 + (i * 3),
                                   fill=color, width=1)
        
    def get_short_label(self, element):
        elem_type = element['type']
        
        if elem_type == 'function':
            return element['name'][:10]
        elif elem_type == 'class':
            return element['name'][:10]
        elif elem_type in ['import', 'import_from']:
            return element.get('module', '')[:10]
        elif elem_type == 'for':
            return element.get('target', '')[:10]
        elif elem_type == 'assign':
            return str(element.get('targets', [''])[0])[:10]
        else:
            return f"L:{element.get('line', '?')}"
        
    def next_step(self):
        if not self.parsed_data:
            messagebox.showinfo("Info", "Please analyze code first")
            return
            
        if self.current_step < len(self.parsed_data):
            self.current_step += 1
            self.draw_tree_visualization()
            self.update_info()
            self.step_label.config(text=f"Step: {self.current_step}/{len(self.parsed_data)}")
            
            if self.auto_play and self.current_step < len(self.parsed_data):
                self.root.after(1000, self.next_step)
        else:
            self.auto_play = False
            self.status_text.config(text="Reached end of execution")
    
    def prev_step(self):
        if not self.parsed_data:
            messagebox.showinfo("Info", "Please analyze code first")
            return
            
        if self.current_step > 0:
            self.current_step -= 1
            if self.current_step == 0:
                self.canvas.delete("all")
                self.info_text.config(state=tk.NORMAL)
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(1.0, "At beginning. Click Next to start.")
                self.info_text.config(state=tk.DISABLED)
                self.code_text.config(state=tk.NORMAL)
                self.code_text.tag_remove("highlight", "1.0", tk.END)
                self.code_text.config(state=tk.DISABLED)
            else:
                self.draw_tree_visualization()
                self.update_info()
            self.step_label.config(text=f"Step: {self.current_step}/{len(self.parsed_data)}")
            self.status_text.config(text="Moved to previous step")
        else:
            self.status_text.config(text="Already at beginning")
    
    def step_into(self):
        if not self.parsed_data:
            messagebox.showinfo("Info", "Please analyze code first")
            return
        
        if self.current_step >= len(self.parsed_data):
            self.status_text.config(text="Already at end")
            return
        
        # If at step 0, just go to first step
        if self.current_step == 0:
            self.next_step()
            return
        
        current_element = self.parsed_data[self.current_step - 1]
        current_depth = current_element['depth']
        current_type = current_element['type']
        
        # Check if current element can contain code (function, class, if, for, while, try, with)
        can_step_into = current_type in ['function', 'class', 'if', 'for', 'while', 'try', 'with']
        
        if not can_step_into:
            # Can't step into this element, just go to next
            self.status_text.config(text=f"Cannot step into {current_type}, moving to next")
            self.next_step()
            return
        
        # Look for the next element that is exactly one level deeper (immediate child)
        for i in range(self.current_step, len(self.parsed_data)):
            if self.parsed_data[i]['depth'] == current_depth + 1:
                # Found first child element
                self.current_step = i + 1
                self.draw_tree_visualization()
                self.update_info()
                self.step_label.config(text=f"Step: {self.current_step}/{len(self.parsed_data)}")
                self.status_text.config(text=f"Stepped into {current_type}: depth {current_depth + 1}")
                return
            elif self.parsed_data[i]['depth'] <= current_depth:
                # Reached same or lower level without finding children
                break
        
        # No children found, just go to next
        self.status_text.config(text=f"No code inside {current_type}, moving to next")
        self.next_step()
    
    def step_out(self):
        if not self.parsed_data:
            messagebox.showinfo("Info", "Please analyze code first")
            return
        
        if self.current_step == 0:
            self.status_text.config(text="At beginning")
            return
        
        current_element = self.parsed_data[self.current_step - 1]
        current_depth = current_element['depth']
        
        if current_depth == 0:
            # Already at top level, go to next top-level element
            for i in range(self.current_step, len(self.parsed_data)):
                if self.parsed_data[i]['depth'] == 0:
                    self.current_step = i + 1
                    self.draw_tree_visualization()
                    self.update_info()
                    self.step_label.config(text=f"Step: {self.current_step}/{len(self.parsed_data)}")
                    self.status_text.config(text="Already at top level, moved to next top-level element")
                    return
            
            # No more top-level elements
            self.status_text.config(text="Already at top level, no more elements")
            return
        
        # Find first element at lower depth (parent's next sibling or higher)
        target_depth = current_depth - 1
        
        for i in range(self.current_step, len(self.parsed_data)):
            if self.parsed_data[i]['depth'] <= target_depth:
                self.current_step = i + 1
                self.draw_tree_visualization()
                self.update_info()
                self.step_label.config(text=f"Step: {self.current_step}/{len(self.parsed_data)}")
                self.status_text.config(text=f"Stepped out: depth {self.parsed_data[i]['depth']}")
                return
        
        # Reached end without finding lower depth
        self.status_text.config(text="Stepped out: reached end of code")
        self.current_step = len(self.parsed_data)
        self.step_label.config(text=f"Step: {self.current_step}/{len(self.parsed_data)}")
    
    def on_file_tree_double_click(self, event):
        # Get the line number where user clicked
        try:
            index = self.file_tree.index(f"@{event.x},{event.y}")
            line_num = int(index.split('.')[0])
            
            # Check if this line has a file path stored
            if line_num in self.folder_files:
                file_path = self.folder_files[line_num]
                self.load_file(file_path)
                self.status_text.config(text=f"Opened: {os.path.basename(file_path)}")
            
        except Exception as e:
            # Silently ignore clicks on non-file lines
            pass
    
    def _sync_scroll(self, *args):
        """Synchronize scrolling between code text and line numbers"""
        self.code_text.yview(*args)
        self.line_numbers.yview(*args)
    
    def _sync_scrollbars(self, *args):
        """Update scrollbar and sync line numbers"""
        self.v_scrollbar.set(*args)
        self.line_numbers.yview_moveto(args[0])
    
    def _on_code_mousewheel(self, event):
        """Handle mouse wheel scrolling for code text and line numbers together"""
        if event.num == 5 or event.delta < 0:
            self.code_text.yview_scroll(1, "units")
            self.line_numbers.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.code_text.yview_scroll(-1, "units")
            self.line_numbers.yview_scroll(-1, "units")
        return "break"
    
    def _on_mousewheel(self, event, widget):
        # Handle mouse wheel scrolling for text widgets
        if event.num == 5 or event.delta < 0:
            widget.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            widget.yview_scroll(-1, "units")
        return "break"
    
    def _on_canvas_mousewheel(self, event):
        # Handle mouse wheel scrolling for canvas
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        return "break"
            
    def toggle_auto_play(self):
        self.auto_play = not self.auto_play
        if self.auto_play:
            self.status_text.config(text="Auto-play enabled")
            self.next_step()
        else:
            self.status_text.config(text="Auto-play disabled")
            
    def update_info(self):
        if self.current_step == 0:
            return
            
        element = self.parsed_data[self.current_step - 1]
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, f"Step {self.current_step}/{len(self.parsed_data)}\n")
        self.info_text.insert(tk.END, "-" * 40 + "\n")
        self.info_text.insert(tk.END, f"Type: {element['type'].upper()}\n")
        self.info_text.insert(tk.END, f"Line: {element.get('line', 'N/A')}\n")
        self.info_text.insert(tk.END, f"Depth: {element.get('depth', 0)}\n")
        
        for key, value in element.items():
            if key not in ['type', 'line', 'depth']:
                self.info_text.insert(tk.END, f"{key}: {value}\n")
        
        self.info_text.config(state=tk.DISABLED)
                
        # Highlight line in code
        if 'line' in element:
            self.highlight_line(element['line'])
            
    def highlight_line(self, line_num):
        self.code_text.config(state=tk.NORMAL)
        self.code_text.tag_remove("highlight", "1.0", tk.END)
        start = f"{line_num}.0"
        end = f"{line_num}.end"
        self.code_text.tag_add("highlight", start, end)
        self.code_text.tag_config("highlight", background="#FFFF00", foreground="black")
        self.code_text.see(start)
        self.code_text.config(state=tk.DISABLED)
        
        # Sync line numbers view with code text
        self.line_numbers.see(start)
        
    def reset(self):
        self.current_step = 0
        self.auto_play = False
        self.canvas.delete("all")
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Ready to analyze code.\nClick 'Analyze' to begin.")
        self.info_text.config(state=tk.DISABLED)
        self.code_text.config(state=tk.NORMAL)
        self.code_text.tag_remove("highlight", "1.0", tk.END)
        self.code_text.config(state=tk.DISABLED)
        self.step_label.config(text="Step: 0/0")
        self.status_text.config(text="Reset complete")


def main():
    rootdbgrrr = tk.Tk()
    app = CodeVisualizer(rootdbgrrr)
    rootdbgrrr.mainloop()


if __name__ == "__main__":
    main()
