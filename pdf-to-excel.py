import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import PyPDF2
import re
from pathlib import Path
import threading
import csv

class PDFtoExcelConverter:
    def __init__(self, rootexceltopdf):
        self.rootexceltopdf = rootexceltopdf
        self.rootexceltopdf.title("PDF to Excel/CSV Converter")
        self.rootexceltopdf.geometry("600x550")
        self.rootexceltopdf.resizable(False, False)
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.button_bg = "#c0c0c0"
        self.text_bg = "#ffffff"
        self.highlight = "#000080"
        
        # Configure rootexceltopdf background
        self.rootexceltopdf.configure(bg=self.bg_color)
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status = tk.StringVar(value="Ready to convert")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame with Windows 95 style
        main_frame = tk.Frame(self.rootexceltopdf, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with Windows 95 style
        title_frame = tk.Frame(main_frame, bg=self.highlight, relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(title_frame, text="PDF to Excel/CSV Converter", 
                              font=("MS Sans Serif", 14, "bold"),
                              bg=self.highlight, fg="white", pady=8)
        title_label.pack()
        
        # Select PDF
        pdf_frame = tk.Frame(main_frame, bg=self.bg_color)
        pdf_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(pdf_frame, text="PDF File:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT)
        
        self.pdf_entry = tk.Entry(pdf_frame, textvariable=self.pdf_path, 
                                 bg=self.text_bg, relief=tk.SUNKEN, bd=2, 
                                 font=("MS Sans Serif", 8))
        self.pdf_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.pdf_btn = tk.Button(pdf_frame, text="Browse...", command=self.select_pdf,
                                bg=self.button_bg, relief=tk.RAISED, bd=2,
                                font=("MS Sans Serif", 8), padx=10)
        self.pdf_btn.pack(side=tk.LEFT)
        
        # Select output destination
        output_frame = tk.Frame(main_frame, bg=self.bg_color)
        output_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(output_frame, text="Save as:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT)
        
        self.output_entry = tk.Entry(output_frame, textvariable=self.output_path,
                                    bg=self.text_bg, relief=tk.SUNKEN, bd=2,
                                    font=("MS Sans Serif", 8))
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.output_btn = tk.Button(output_frame, text="Browse...", command=self.select_output,
                                   bg=self.button_bg, relief=tk.RAISED, bd=2,
                                   font=("MS Sans Serif", 8), padx=10)
        self.output_btn.pack(side=tk.LEFT)
        
        # Options frame with Windows 95 group box style
        options_frame = tk.LabelFrame(main_frame, text="Options", bg=self.bg_color,
                                     relief=tk.GROOVE, bd=2, font=("MS Sans Serif", 8, "bold"),
                                     padx=10, pady=10)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        
        # Output format
        format_frame = tk.Frame(options_frame, bg=self.bg_color)
        format_frame.pack(anchor=tk.W, pady=5)
        
        tk.Label(format_frame, text="Output format:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT)
        
        self.output_format = tk.StringVar(value="xlsx")
        
        format_radio_frame = tk.Frame(options_frame, bg=self.bg_color)
        format_radio_frame.pack(anchor=tk.W, padx=20)
        
        self.radio_xlsx = tk.Radiobutton(format_radio_frame, text="Excel (.xlsx)", 
                                        variable=self.output_format, value="xlsx",
                                        command=self.update_output_extension,
                                        bg=self.bg_color, font=("MS Sans Serif", 8),
                                        activebackground=self.bg_color)
        self.radio_xlsx.pack(anchor=tk.W)
        
        self.radio_csv = tk.Radiobutton(format_radio_frame, text="CSV (.csv)", 
                                       variable=self.output_format, value="csv",
                                       command=self.update_output_extension,
                                       bg=self.bg_color, font=("MS Sans Serif", 8),
                                       activebackground=self.bg_color)
        self.radio_csv.pack(anchor=tk.W)
        
        # Conversion mode
        mode_frame = tk.Frame(options_frame, bg=self.bg_color)
        mode_frame.pack(anchor=tk.W, pady=5)
        
        tk.Label(mode_frame, text="Conversion mode:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT)
        
        self.mode = tk.StringVar(value="text")
        
        radio_frame = tk.Frame(options_frame, bg=self.bg_color)
        radio_frame.pack(anchor=tk.W, padx=20)
        
        self.radio_text = tk.Radiobutton(radio_frame, text="Structured text", 
                                        variable=self.mode, value="text", 
                                        command=self.toggle_delimiter,
                                        bg=self.bg_color, font=("MS Sans Serif", 8),
                                        activebackground=self.bg_color)
        self.radio_text.pack(anchor=tk.W)
        
        self.radio_simple = tk.Radiobutton(radio_frame, text="Simple text (line by line)", 
                                          variable=self.mode, value="simple",
                                          command=self.toggle_delimiter,
                                          bg=self.bg_color, font=("MS Sans Serif", 8),
                                          activebackground=self.bg_color)
        self.radio_simple.pack(anchor=tk.W)
        
        # Delimiter
        delim_frame = tk.Frame(options_frame, bg=self.bg_color)
        delim_frame.pack(anchor=tk.W, pady=5)
        
        self.delimiter_label = tk.Label(delim_frame, text="Delimiter:", 
                                       bg=self.bg_color, font=("MS Sans Serif", 8))
        self.delimiter_label.pack(side=tk.LEFT)
        
        self.delimiter = ttk.Combobox(delim_frame, values=["Auto-detect", "Tab", "Space", "Comma (,)", "Semicolon (;)", "Pipe (|)", "Colon (:)"], 
                                     width=15, font=("MS Sans Serif", 8))
        self.delimiter.set("Auto-detect")
        self.delimiter.pack(side=tk.LEFT, padx=5)
        
        # All pages checkbox
        self.all_pages = tk.BooleanVar(value=True)
        self.all_pages_check = tk.Checkbutton(options_frame, text="Combine all pages into one sheet", 
                                             variable=self.all_pages,
                                             bg=self.bg_color, font=("MS Sans Serif", 8),
                                             activebackground=self.bg_color)
        self.all_pages_check.pack(anchor=tk.W, pady=5)
        
        # Clean data checkbox
        self.clean_data = tk.BooleanVar(value=True)
        self.clean_data_check = tk.Checkbutton(options_frame, text="Clean empty rows/columns", 
                                               variable=self.clean_data,
                                               bg=self.bg_color, font=("MS Sans Serif", 8),
                                               activebackground=self.bg_color)
        self.clean_data_check.pack(anchor=tk.W, pady=2)
        
        # Convert button - bigger and centered
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        self.convert_btn = tk.Button(button_frame, text="Convert", command=self.convert,
                                     bg=self.button_bg, relief=tk.RAISED, bd=3,
                                     font=("MS Sans Serif", 10, "bold"), 
                                     padx=30, pady=5)
        self.convert_btn.pack()
        
        # Progress bar (using Canvas for retro look)
        progress_frame = tk.Frame(main_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_canvas = tk.Canvas(progress_frame, height=11, bg="#c0c0c0",
                                        relief=tk.SUNKEN, bd=2)
        self.progress_canvas.pack(fill=tk.X)
        self.progress_active = False
        
        # Status bar
        status_frame = tk.Frame(main_frame, relief=tk.SUNKEN, bd=2, bg="white")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        status_label = tk.Label(status_frame, textvariable=self.status,
                               bg="white", font=("MS Sans Serif", 8),
                               anchor=tk.W, padx=5, pady=2)
        status_label.pack(fill=tk.X)
    
    def animate_progress(self):
        """Animate progress bar Windows 95 style"""
        if self.progress_active:
            width = self.progress_canvas.winfo_width()
            self.progress_canvas.delete("all")
            
            if not hasattr(self, 'progress_pos'):
                self.progress_pos = 0
            
            block_width = 20
            block_height = 16
            spacing = 2
            
            for i in range(int(width / (block_width + spacing))):
                x = i * (block_width + spacing)
                offset = (self.progress_pos + i * 3) % 20
                color = "#000080" if offset < 10 else "#c0c0c0"
                
                self.progress_canvas.create_rectangle(x, 2, x + block_width, 
                                                     block_height, fill=color, outline="gray")
            
            self.progress_pos = (self.progress_pos + 1) % 20
            self.rootexceltopdf.after(100, self.animate_progress)
    
    def update_output_extension(self):
        """Update output file extension based on format selection"""
        current_path = self.output_path.get()
        if current_path:
            path_obj = Path(current_path)
            new_extension = ".xlsx" if self.output_format.get() == "xlsx" else ".csv"
            new_path = path_obj.with_suffix(new_extension)
            self.output_path.set(str(new_path))
    
    def select_pdf(self):
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
            # Auto-suggest output filename based on format
            extension = ".xlsx" if self.output_format.get() == "xlsx" else ".csv"
            output_name = Path(filename).stem + extension
            output_dir = Path(filename).parent
            self.output_path.set(str(output_dir / output_name))
    
    def select_output(self):
        format_type = self.output_format.get()
        if format_type == "xlsx":
            filetypes = [("Excel files", "*.xlsx"), ("All files", "*.*")]
            default_ext = ".xlsx"
        else:
            filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
            default_ext = ".csv"
        
        filename = filedialog.asksaveasfilename(
            title="Save as",
            defaultextension=default_ext,
            filetypes=filetypes
        )
        if filename:
            self.output_path.set(filename)
    
    def toggle_delimiter(self):
        """Enable/disable delimiter options based on mode"""
        if self.mode.get() == "simple":
            self.delimiter.config(state='disabled')
            self.delimiter_label.config(foreground='gray')
        else:
            self.delimiter.config(state='normal')
            self.delimiter_label.config(foreground='black')
    
    def disable_all_controls(self):
        """Disable all controls during conversion"""
        self.pdf_entry.config(state='disabled')
        self.pdf_btn.config(state='disabled')
        self.output_entry.config(state='disabled')
        self.output_btn.config(state='disabled')
        self.radio_text.config(state='disabled')
        self.radio_simple.config(state='disabled')
        self.radio_xlsx.config(state='disabled')
        self.radio_csv.config(state='disabled')
        self.delimiter.config(state='disabled')
        self.all_pages_check.config(state='disabled')
        self.clean_data_check.config(state='disabled')
        self.convert_btn.config(state='disabled')
    
    def enable_all_controls(self):
        """Re-enable all controls after conversion"""
        self.pdf_entry.config(state='normal')
        self.pdf_btn.config(state='normal')
        self.output_entry.config(state='normal')
        self.output_btn.config(state='normal')
        self.radio_text.config(state='normal')
        self.radio_simple.config(state='normal')
        self.radio_xlsx.config(state='normal')
        self.radio_csv.config(state='normal')
        self.all_pages_check.config(state='normal')
        self.clean_data_check.config(state='normal')
        self.convert_btn.config(state='normal')
        self.toggle_delimiter()
    
    def get_delimiter(self):
        delim_map = {
            "Auto-detect": None,
            "Tab": "\t",
            "Space": " ",
            "Comma (,)": ",",
            "Semicolon (;)": ";",
            "Pipe (|)": "|",
            "Colon (:)": ":"
        }
        return delim_map.get(self.delimiter.get(), None)
    
    def auto_detect_delimiter(self, text):
        """Auto-detect the most likely delimiter in the text"""
        sample_lines = text.split('\n')[:10]  # Check first 10 lines
        sample_text = '\n'.join([line for line in sample_lines if line.strip()])
        
        delimiters = ['\t', ',', ';', '|', ':']
        delimiter_counts = {}
        
        for delim in delimiters:
            count = sample_text.count(delim)
            # Check if delimiter appears consistently across lines
            lines_with_delim = sum(1 for line in sample_lines if delim in line)
            if lines_with_delim >= len(sample_lines) * 0.5:  # At least 50% of lines
                delimiter_counts[delim] = count
        
        if delimiter_counts:
            return max(delimiter_counts, key=delimiter_counts.get)
        
        # Check for multiple spaces (columnar data)
        if re.search(r'\s{2,}', sample_text):
            return " "
        
        return "\t"  # Default to tab
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using PyPDF2"""
        text_by_page = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text and text.strip():
                        text_by_page.append(text)
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return text_by_page
    
    def clean_cell_value(self, value):
        """Clean and normalize cell values"""
        if value is None:
            return ""
        
        value = str(value).strip()
        
        # Remove multiple spaces
        value = re.sub(r'\s+', ' ', value)
        
        # Remove common PDF artifacts
        value = value.replace('\x00', '').replace('\ufffd', '')
        
        return value
    
    def parse_structured_text(self, text, delimiter):
        """Parse structured text into DataFrame with improved error handling"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Auto-detect delimiter if not specified
        if delimiter is None:
            delimiter = self.auto_detect_delimiter(text)
        
        data = []
        for line in lines:
            try:
                if delimiter == " ":
                    # For spaces, split on multiple spaces
                    row = re.split(r'\s{2,}', line)
                    row = [self.clean_cell_value(cell) for cell in row if cell.strip()]
                elif delimiter == "\t":
                    # For tabs, split normally
                    row = [self.clean_cell_value(cell) for cell in line.split(delimiter)]
                else:
                    # For other delimiters, split and clean
                    row = [self.clean_cell_value(cell) for cell in line.split(delimiter)]
                
                # Only add rows with content
                if row and any(cell for cell in row):
                    data.append(row)
            except Exception:
                continue  # Skip problematic lines
        
        if not data:
            return None
        
        # Find the most common number of columns (likely the correct structure)
        col_counts = [len(row) for row in data]
        if not col_counts:
            return None
        
        most_common_cols = max(set(col_counts), key=col_counts.count)
        
        # Filter out rows that differ significantly from the expected column count
        # Allow tolerance of ±1 column
        filtered_data = []
        for row in data:
            if abs(len(row) - most_common_cols) <= 1:
                # Normalize row length
                if len(row) < most_common_cols:
                    row = row + [''] * (most_common_cols - len(row))
                elif len(row) > most_common_cols:
                    row = row[:most_common_cols]
                filtered_data.append(row)
        
        if not filtered_data:
            # If filtering removed everything, use original data
            max_cols = max(len(row) for row in data)
            filtered_data = [row + [''] * (max_cols - len(row)) for row in data]
        
        # Detect if first row is header
        if len(filtered_data) > 1:
            first_row = filtered_data[0]
            # Header detection: check if first row contains mostly text and second row contains numbers
            is_likely_header = True
            for cell in first_row:
                if cell and cell.replace('.', '').replace(',', '').replace('-', '').isdigit():
                    is_likely_header = False
                    break
            
            if is_likely_header:
                # Use first row as header
                headers = [str(cell) if cell else f'Column_{i+1}' for i, cell in enumerate(first_row)]
                df = pd.DataFrame(filtered_data[1:], columns=headers)
            else:
                # Generate generic column names
                columns = [f'Column_{i+1}' for i in range(len(filtered_data[0]))]
                df = pd.DataFrame(filtered_data, columns=columns)
        else:
            # Single row - use generic column names
            columns = [f'Column_{i+1}' for i in range(len(filtered_data[0]))]
            df = pd.DataFrame(filtered_data, columns=columns)
        
        return df
    
    def parse_simple_text(self, text):
        """Parse simple text into DataFrame (one line = one entry)"""
        lines = [self.clean_cell_value(line) for line in text.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        df = pd.DataFrame({'Content': lines})
        return df
    
    def clean_dataframe(self, df):
        """Clean DataFrame by removing empty rows and columns"""
        if df is None or df.empty:
            return df
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Remove completely empty columns
        df = df.dropna(axis=1, how='all')
        
        # Remove columns that are entirely empty strings
        for col in df.columns:
            if df[col].astype(str).str.strip().eq('').all():
                df = df.drop(columns=[col])
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def save_to_excel(self, dfs, output_path, combine_pages):
        """Save DataFrames to Excel with error handling"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                if combine_pages:
                    # Combine all dataframes
                    combined_df = pd.concat([df for _, df in dfs], ignore_index=True)
                    if self.clean_data.get():
                        combined_df = self.clean_dataframe(combined_df)
                    combined_df.to_excel(writer, sheet_name='All_Pages', index=False)
                else:
                    # Save each page separately
                    for page_num, df in dfs:
                        if self.clean_data.get():
                            df = self.clean_dataframe(df)
                        sheet_name = f"Page_{page_num}"[:31]  # Excel sheet name limit
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            return True
        except Exception as e:
            raise Exception(f"Error saving Excel file: {str(e)}")
    
    def save_to_csv(self, dfs, output_path, combine_pages):
        """Save DataFrames to CSV with error handling"""
        try:
            if combine_pages:
                # Combine all dataframes
                combined_df = pd.concat([df for _, df in dfs], ignore_index=True)
                if self.clean_data.get():
                    combined_df = self.clean_dataframe(combined_df)
                combined_df.to_csv(output_path, index=False, encoding='utf-8-sig', 
                                  quoting=csv.QUOTE_MINIMAL, escapechar='\\')
            else:
                # For multiple pages in CSV, save to multiple files or append with separator
                if len(dfs) == 1:
                    df = dfs[0][1]
                    if self.clean_data.get():
                        df = self.clean_dataframe(df)
                    df.to_csv(output_path, index=False, encoding='utf-8-sig',
                             quoting=csv.QUOTE_MINIMAL, escapechar='\\')
                else:
                    # Save with page separators
                    all_dfs = []
                    for page_num, df in dfs:
                        if self.clean_data.get():
                            df = self.clean_dataframe(df)
                        # Add a separator row with page info
                        separator = pd.DataFrame([[f'=== Page {page_num} ===' + '='*50]], 
                                                columns=['Page Separator'])
                        all_dfs.append(separator)
                        all_dfs.append(df)
                    
                    combined = pd.concat(all_dfs, ignore_index=True)
                    combined.to_csv(output_path, index=False, encoding='utf-8-sig',
                                   quoting=csv.QUOTE_MINIMAL, escapechar='\\')
            return True
        except Exception as e:
            raise Exception(f"Error saving CSV file: {str(e)}")
    
    def convert(self):
        if not self.pdf_path.get():
            messagebox.showerror("Error", "Please select a PDF file!")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify the output file!")
            return
        
        # Validate output path extension matches format
        output_ext = Path(self.output_path.get()).suffix.lower()
        expected_ext = ".xlsx" if self.output_format.get() == "xlsx" else ".csv"
        
        if output_ext != expected_ext:
            response = messagebox.askyesno(
                "Extension Mismatch",
                f"The output file extension ({output_ext}) doesn't match the selected format ({expected_ext}).\n\n"
                f"Do you want to change it to {expected_ext}?"
            )
            if response:
                new_path = Path(self.output_path.get()).with_suffix(expected_ext)
                self.output_path.set(str(new_path))
            else:
                return
        
        # Run conversion in separate thread
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
    
    def run_conversion(self):
        try:
            self.disable_all_controls()
            self.progress_active = True
            self.animate_progress()
            self.status.set("Extracting text from PDF...")
            
            pages_text = self.extract_text_from_pdf(self.pdf_path.get())
            
            if not pages_text:
                self.rootexceltopdf.after(0, lambda: messagebox.showwarning(
                    "Warning", "Could not extract text from PDF! The PDF might be image-based or encrypted."))
                return
            
            self.status.set(f"Processing {len(pages_text)} page(s)...")
            
            mode = self.mode.get()
            delimiter = self.get_delimiter()
            
            dfs = []
            errors = []
            
            for i, text in enumerate(pages_text):
                try:
                    if mode == "text":
                        df = self.parse_structured_text(text, delimiter)
                    else:
                        df = self.parse_simple_text(text)
                    
                    if df is not None and not df.empty:
                        dfs.append((i + 1, df))
                    else:
                        errors.append(f"Page {i+1}: No data extracted")
                except Exception as e:
                    errors.append(f"Page {i+1}: {str(e)}")
            
            if not dfs:
                error_msg = "Could not extract data from PDF!\n\n"
                if errors:
                    error_msg += "Errors:\n" + "\n".join(errors[:5])
                self.rootexceltopdf.after(0, lambda msg=error_msg: messagebox.showwarning(
                    "Warning", msg))
                return
            
            self.status.set("Saving file...")
            
            output_format = self.output_format.get()
            combine_pages = self.all_pages.get()
            
            if output_format == "xlsx":
                self.save_to_excel(dfs, self.output_path.get(), combine_pages)
            else:
                self.save_to_csv(dfs, self.output_path.get(), combine_pages)
            
            success_msg = f"Conversion completed successfully!\n\n"
            success_msg += f"Pages processed: {len(dfs)}/{len(pages_text)}\n"
            success_msg += f"Output: {Path(self.output_path.get()).name}"
            
            if errors:
                success_msg += f"\n\nWarnings: {len(errors)} page(s) had issues"
            
            self.status.set("Conversion completed successfully!")
            self.rootexceltopdf.after(0, lambda msg=success_msg: messagebox.showinfo(
                "Success", msg))
            
        except Exception as e:
            self.status.set("Conversion error!")
            error_msg = f"An error occurred:\n\n{str(e)}"
            self.rootexceltopdf.after(0, lambda msg=error_msg: messagebox.showerror(
                "Error", msg))
        
        finally:
            self.progress_active = False
            self.progress_canvas.delete("all")
            self.rootexceltopdf.after(0, self.enable_all_controls)

if __name__ == "__main__":
    rootexceltopdf = tk.Tk()
    app = PDFtoExcelConverter(rootexceltopdf)
    rootexceltopdf.mainloop()