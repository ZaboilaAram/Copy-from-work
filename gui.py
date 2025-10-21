import os
import tkinter as tk
from tkinter import filedialog, messagebox

class Win95PyCompiler:
    def __init__(self, rootplainpy):
        self.rootplainpy = rootplainpy
        self.rootplainpy.title("Python Script Merger")
        self.rootplainpy.geometry("500x400")
        self.rootplainpy.resizable(False, False)
        
        # Configure colors
        self.bg_color = "#c0c0c0"
        self.rootplainpy.configure(bg=self.bg_color)
        
        self.selected_folder = ""
        self.path_mode = tk.StringVar(value="relative")
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        # Title frame
        title_frame = tk.Frame(self.rootplainpy, bg="#000080", height=25)
        title_frame.pack(fill=tk.X, pady=(0, 2))
        
        title_label = tk.Label(title_frame, text="Python Script Merger", 
                              bg="#000080", fg="white", font=("MS Sans Serif", 9, "bold"))
        title_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Main container
        main_frame = tk.Frame(self.rootplainpy, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Folder selection section
        folder_frame = tk.LabelFrame(main_frame, text="Select Folder", 
                                     bg=self.bg_color, font=("MS Sans Serif", 8, "bold"))
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.folder_label = tk.Label(folder_frame, text="No folder selected", 
                                     bg="white", relief=tk.SUNKEN, anchor=tk.W, 
                                     height=2, font=("MS Sans Serif", 8))
        self.folder_label.pack(fill=tk.X, padx=5, pady=5)
        
        browse_btn = tk.Button(folder_frame, text="Browse...", 
                              command=self.browse_folder,
                              width=15, relief=tk.RAISED, 
                              font=("MS Sans Serif", 8))
        browse_btn.pack(pady=(0, 5))
        
        # Path mode selection
        mode_frame = tk.LabelFrame(main_frame, text="Path Display Mode", 
                                   bg=self.bg_color, font=("MS Sans Serif", 8, "bold"))
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        mode_inner = tk.Frame(mode_frame, bg=self.bg_color)
        mode_inner.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Radiobutton(mode_inner, text="Full absolute path (C:\\Users\\...\\file.py)", 
                      variable=self.path_mode, value="absolute", 
                      bg=self.bg_color, font=("MS Sans Serif", 8),
                      anchor=tk.W).pack(fill=tk.X, pady=2)
        
        tk.Radiobutton(mode_inner, text="Relative from selected folder (subfolder\\file.py)", 
                      variable=self.path_mode, value="relative", 
                      bg=self.bg_color, font=("MS Sans Serif", 8),
                      anchor=tk.W).pack(fill=tk.X, pady=2)
        
        tk.Radiobutton(mode_inner, text="Dot notation (.\\subfolder\\file.py or .\\file.py)", 
                      variable=self.path_mode, value="dot", 
                      bg=self.bg_color, font=("MS Sans Serif", 8),
                      anchor=tk.W).pack(fill=tk.X, pady=2)
        
        # Output filename
        output_frame = tk.LabelFrame(main_frame, text="Output File", 
                                     bg=self.bg_color, font=("MS Sans Serif", 8, "bold"))
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.output_entry = tk.Entry(output_frame, font=("MS Sans Serif", 8))
        self.output_entry.insert(0, "compiled_scripts.txt")
        self.output_entry.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        save_btn = tk.Button(output_frame, text="Browse...", 
                            command=self.browse_save_location,
                            width=15, relief=tk.RAISED, 
                            font=("MS Sans Serif", 8))
        save_btn.pack(pady=5)
        
        # Compile button
        compile_btn = tk.Button(main_frame, text="Compile Python Files", 
                               command=self.compile_files,
                               height=2, relief=tk.RAISED,
                               font=("MS Sans Serif", 9, "bold"))
        compile_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Status bar
        self.status_bar = tk.Label(self.rootplainpy, text="Ready", 
                                   bg=self.bg_color, relief=tk.SUNKEN, 
                                   anchor=tk.W, font=("MS Sans Serif", 8))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.selected_folder = folder
            folder_name = os.path.basename(folder)
            self.folder_label.config(text=f"Selected: {folder_name}")
            self.status_bar.config(text=f"Folder selected: {folder}")
    
    def browse_save_location(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Output File As",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="compiled_scripts.txt"
        )
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)
            self.status_bar.config(text=f"Output location: {file_path}")
    
    def compile_files(self):
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return
        
        output_file = self.output_entry.get()
        if not output_file:
            messagebox.showerror("Error", "Please enter an output filename!")
            return
        
        self.status_bar.config(text="Processing...")
        self.rootplainpy.update()
        
        try:
            py_files = []
            for rootplainpy, dirs, files in os.walk(self.selected_folder):
                for file in sorted(files):
                    if file.endswith('.py'):
                        py_files.append(os.path.join(rootplainpy, file))
            
            if not py_files:
                messagebox.showwarning("Warning", "No .py files found in selected folder!")
                self.status_bar.config(text="No files found")
                return
            
            py_files.sort()
            
            with open(output_file, 'w', encoding='utf-8') as outfile:
                for file_path in py_files:
                    # Determine display path based on mode
                    if self.path_mode.get() == "absolute":
                        # Full absolute path
                        display_path = os.path.abspath(file_path)
                    elif self.path_mode.get() == "relative":
                        # Relative path from selected folder
                        display_path = os.path.relpath(file_path, self.selected_folder)
                    else:  # dot notation
                        # .\ notation with relative path
                        rel_path = os.path.relpath(file_path, self.selected_folder)
                        if rel_path.startswith('.'):
                            display_path = rel_path
                        else:
                            display_path = '.' + os.sep + rel_path
                    
                    outfile.write('=' * 70 + '\n')
                    outfile.write(f'File: {display_path}\n')
                    outfile.write('=' * 70 + '\n\n')
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            outfile.write(content)
                            if not content.endswith('\n'):
                                outfile.write('\n')
                    except Exception as e:
                        outfile.write(f'[ERROR reading file: {e}]\n')
                    
                    outfile.write('\n\n')
            
            messagebox.showinfo("Success", 
                              f"Compiled {len(py_files)} .py files into '{output_file}'")
            self.status_bar.config(text=f"Success! Created {output_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_bar.config(text="Error occurred")

def main():
    rootplainpy = tk.Tk()
    app = Win95PyCompiler(rootplainpy)
    rootplainpy.mainloop()

if __name__ == "__main__":
    main()