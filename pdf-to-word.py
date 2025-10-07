import tkinter as tk
from tkinter import filedialog, messagebox
from pdf2docx import Converter
import os
import logging

logging.disable(logging.CRITICAL)

class Windows95Converter:
    def __init__(self, rootWORDDOCX):
        self.rootWORDDOCX = rootWORDDOCX
        self.rootWORDDOCX.title("PDF to Word Converter")
        self.rootWORDDOCX.geometry("500x300")
        self.rootWORDDOCX.resizable(False, False)
        
        # Windows 95 colors
        bg_color = "#c0c0c0"
        button_bg = "#c0c0c0"
        self.rootWORDDOCX.configure(bg=bg_color)
        
        # Title bar style frame
        title_frame = tk.Frame(rootWORDDOCX, bg="#000080", height=25)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text="PDF to Word Converter", 
                               bg="#000080", fg="white", font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Main content frame
        content_frame = tk.Frame(rootWORDDOCX, bg=bg_color, relief=tk.RAISED, bd=2)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File selection section
        file_frame = tk.Frame(content_frame, bg=bg_color)
        file_frame.pack(pady=20, padx=20)
        
        tk.Label(file_frame, text="Select PDF file:", bg=bg_color, 
                font=("MS Sans Serif", 8)).pack(anchor=tk.W)
        
        path_frame = tk.Frame(file_frame, bg=bg_color)
        path_frame.pack(fill=tk.X, pady=5)
        
        self.file_path = tk.StringVar()
        self.path_entry = tk.Entry(path_frame, textvariable=self.file_path, 
                                   width=40, font=("MS Sans Serif", 8))
        self.path_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        browse_btn = tk.Button(path_frame, text="Browse...", 
                              command=self.browse_file,
                              bg=button_bg, relief=tk.RAISED, bd=2,
                              font=("MS Sans Serif", 8), width=10)
        browse_btn.pack(side=tk.LEFT)
        
        # Buttons section
        button_frame = tk.Frame(content_frame, bg=bg_color)
        button_frame.pack(pady=20)
        
        convert_btn = tk.Button(button_frame, text="Convert", 
                               command=self.convert_file,
                               bg=button_bg, relief=tk.RAISED, bd=2,
                               font=("MS Sans Serif", 8, "bold"), 
                               width=15, height=2)
        convert_btn.pack(side=tk.LEFT, padx=5)
        
        exit_btn = tk.Button(button_frame, text="Exit", 
                            command=self.rootWORDDOCX.quit,
                            bg=button_bg, relief=tk.RAISED, bd=2,
                            font=("MS Sans Serif", 8), width=15, height=2)
        exit_btn.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        status_frame = tk.Frame(rootWORDDOCX, bg=bg_color, relief=tk.SUNKEN, bd=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                     bg=bg_color, anchor=tk.W,
                                     font=("MS Sans Serif", 8))
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.status_label.config(text="File selected")
    
    def convert_file(self):
        pdf_path = self.file_path.get()
        
        if not pdf_path:
            messagebox.showwarning("Warning", "Please select a PDF file first!")
            return
        
        if not os.path.exists(pdf_path):
            messagebox.showerror("Error", "The selected file does not exist!")
            return
        
        try:
            word_path = pdf_path.replace('.pdf', '.docx')
            
            self.status_label.config(text="Converting...")
            self.rootWORDDOCX.update()
            
            cv = Converter(pdf_path)
            cv.convert(word_path)
            cv.close()
            
            self.status_label.config(text="Conversion successful!")
            messagebox.showinfo("Success", 
                              f"File converted successfully!\n\nSaved as:\n{word_path}")
            
        except Exception as e:
            self.status_label.config(text="Conversion failed")
            messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")

if __name__ == "__main__":
    rootWORDDOCX = tk.Tk()
    app = Windows95Converter(rootWORDDOCX)
    rootWORDDOCX.mainloop()