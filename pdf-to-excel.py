import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import pdfplumber
import re
from pathlib import Path
import threading
import csv

class PDFtoExcelConverter:
    def __init__(self, rootexceltopdf):
        self.rootexceltopdf = rootexceltopdf
        self.rootexceltopdf.title("PDF to Excel/CSV Converter")
        self.rootexceltopdf.geometry("600x650")
        self.rootexceltopdf.resizable(False, False)
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.button_bg = "#c0c0c0"
        self.text_bg = "#ffffff"
        self.highlight = "#000080"
        
        self.rootexceltopdf.configure(bg=self.bg_color)
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status = tk.StringVar(value="Ready to convert")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.rootexceltopdf, bg=self.bg_color, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = tk.Frame(main_frame, bg=self.highlight, relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(title_frame, text="PDF to Excel/CSV Converter", 
                              font=("MS Sans Serif", 14, "bold"),
                              bg=self.highlight, fg="white", pady=8)
        title_label.pack()
        
        # PDF File Selection
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
        
        # Output File Selection
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
        
        # Options Frame
        options_frame = tk.LabelFrame(main_frame, text="Options", bg=self.bg_color,
                                     relief=tk.GROOVE, bd=2, font=("MS Sans Serif", 8, "bold"),
                                     padx=10, pady=10)
        options_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        
        # Output Format
        format_frame = tk.Frame(options_frame, bg=self.bg_color)
        format_frame.pack(anchor=tk.W, pady=5)
        
        tk.Label(format_frame, text="Output format:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT)
        
        self.output_format = tk.StringVar(value="xlsx")
        
        format_radio_frame = tk.Frame(options_frame, bg=self.bg_color)
        format_radio_frame.pack(anchor=tk.W, padx=20)
        
        tk.Radiobutton(format_radio_frame, text="Excel (.xlsx)", 
                      variable=self.output_format, value="xlsx",
                      command=self.update_output_extension,
                      bg=self.bg_color, font=("MS Sans Serif", 8),
                      activebackground=self.bg_color).pack(anchor=tk.W)
        
        tk.Radiobutton(format_radio_frame, text="CSV (.csv)", 
                      variable=self.output_format, value="csv",
                      command=self.update_output_extension,
                      bg=self.bg_color, font=("MS Sans Serif", 8),
                      activebackground=self.bg_color).pack(anchor=tk.W)
        
        # Conversion Mode
        mode_frame = tk.Frame(options_frame, bg=self.bg_color)
        mode_frame.pack(anchor=tk.W, pady=5)
        
        tk.Label(mode_frame, text="Conversion mode:", bg=self.bg_color,
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT)
        
        self.mode = tk.StringVar(value="auto")
        
        radio_frame = tk.Frame(options_frame, bg=self.bg_color)
        radio_frame.pack(anchor=tk.W, padx=20)
        
        tk.Radiobutton(radio_frame, text="Auto-detect (tables first)", 
                      variable=self.mode, value="auto",
                      command=self.toggle_delimiter,
                      bg=self.bg_color, font=("MS Sans Serif", 8),
                      activebackground=self.bg_color).pack(anchor=tk.W)
        
        tk.Radiobutton(radio_frame, text="Structured text", 
                      variable=self.mode, value="text", 
                      command=self.toggle_delimiter,
                      bg=self.bg_color, font=("MS Sans Serif", 8),
                      activebackground=self.bg_color).pack(anchor=tk.W)
        
        tk.Radiobutton(radio_frame, text="Simple text (line by line)", 
                      variable=self.mode, value="simple",
                      command=self.toggle_delimiter,
                      bg=self.bg_color, font=("MS Sans Serif", 8),
                      activebackground=self.bg_color).pack(anchor=tk.W)
        
        # Delimiter Options
        delim_frame = tk.Frame(options_frame, bg=self.bg_color)
        delim_frame.pack(anchor=tk.W, pady=5)
        
        self.delimiter_label = tk.Label(delim_frame, text="Delimiter:", 
                                       bg=self.bg_color, font=("MS Sans Serif", 8))
        self.delimiter_label.pack(side=tk.LEFT)
        
        self.delimiter = ttk.Combobox(delim_frame, 
                                     values=["Auto-detect", "Tab", "Space", "Comma (,)", 
                                            "Semicolon (;)", "Pipe (|)", "Colon (:)"], 
                                     width=15, font=("MS Sans Serif", 8), state='disabled')
        self.delimiter.set("Auto-detect")
        self.delimiter.pack(side=tk.LEFT, padx=5)
        
        # Additional Options
        self.all_pages = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Combine all pages into one sheet", 
                      variable=self.all_pages,
                      bg=self.bg_color, font=("MS Sans Serif", 8),
                      activebackground=self.bg_color).pack(anchor=tk.W, pady=5)
        
        self.clean_data = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Clean empty rows/columns", 
                      variable=self.clean_data,
                      bg=self.bg_color, font=("MS Sans Serif", 8),
                      activebackground=self.bg_color).pack(anchor=tk.W, pady=2)
                      
        # Progress bar (using Canvas for retro look)
        progress_frame = tk.Frame(main_frame, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress_canvas = tk.Canvas(progress_frame, height=11, bg="#c0c0c0",
                                        relief=tk.SUNKEN, bd=2)
        self.progress_canvas.pack(fill=tk.X)
        self.progress_active = False

        # Convert Button
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        # Status Bar
        status_frame = tk.Frame(main_frame, relief=tk.SUNKEN, bd=2, bg="white")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(status_frame, textvariable=self.status,
                bg="white", font=("MS Sans Serif", 8),
                anchor=tk.W, padx=5, pady=2).pack(fill=tk.X)
                
        # Convert Button
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        self.convert_btn = tk.Button(button_frame, text="Convert", command=self.convert,
                                     bg=self.button_bg, relief=tk.RAISED, bd=3,
                                     font=("MS Sans Serif", 10, "bold"), 
                                     padx=30, pady=5)
        self.convert_btn.pack()
        
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
        """Update output file extension based on format"""
        current_path = self.output_path.get()
        if current_path:
            path_obj = Path(current_path)
            new_extension = ".xlsx" if self.output_format.get() == "xlsx" else ".csv"
            new_path = path_obj.with_suffix(new_extension)
            self.output_path.set(str(new_path))
    
    def select_pdf(self):
        """Select PDF file"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path.set(filename)
            extension = ".xlsx" if self.output_format.get() == "xlsx" else ".csv"
            output_name = Path(filename).stem + extension
            output_dir = Path(filename).parent
            self.output_path.set(str(output_dir / output_name))
    
    def select_output(self):
        """Select output file"""
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
        """Enable/disable delimiter based on mode"""
        if self.mode.get() in ["simple", "auto"]:
            self.delimiter.config(state='disabled')
            self.delimiter_label.config(foreground='gray')
        else:
            self.delimiter.config(state='normal')
            self.delimiter_label.config(foreground='black')
    
    def get_delimiter(self):
        """Get selected delimiter"""
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
        """Auto-detect delimiter in text"""
        sample_lines = text.split('\n')[:10]
        sample_text = '\n'.join([line for line in sample_lines if line.strip()])
        
        delimiters = ['\t', ',', ';', '|', ':']
        delimiter_counts = {}
        
        for delim in delimiters:
            count = sample_text.count(delim)
            lines_with_delim = sum(1 for line in sample_lines if delim in line)
            if lines_with_delim >= len(sample_lines) * 0.5:
                delimiter_counts[delim] = count
        
        if delimiter_counts:
            return max(delimiter_counts, key=delimiter_counts.get)
        
        if re.search(r'\s{2,}', sample_text):
            return " "
        
        return "\t"
    
    def extract_data_from_pdf(self, pdf_path):
        """Extract text and tables from PDF"""
        pages_data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_data = {
                        'text': '',
                        'tables': [],
                        'page_num': page_num + 1
                    }
                    
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        valid_tables = []
                        for table in tables:
                            if table and len(table) > 0:
                                has_content = any(
                                    any(cell and str(cell).strip() for cell in row)
                                    for row in table
                                )
                                if has_content:
                                    valid_tables.append(table)
                        page_data['tables'] = valid_tables
                    
                    # Extract text
                    text = page.extract_text()
                    if text and text.strip():
                        page_data['text'] = text
                    
                    pages_data.append(page_data)
                    
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return pages_data
    
    def clean_cell_value(self, value):
        """Clean cell value"""
        if value is None:
            return ""
        
        value = str(value).strip()
        value = re.sub(r'\s+', ' ', value)
        value = value.replace('\x00', '').replace('\ufffd', '')
        
        return value
    
    def table_to_dataframe(self, table):
        """Convert table to DataFrame"""
        if not table or len(table) == 0:
            return None
        
        # Clean table data
        cleaned_table = []
        for row in table:
            cleaned_row = [self.clean_cell_value(cell) for cell in row]
            if any(cell for cell in cleaned_row):
                cleaned_table.append(cleaned_row)
        
        if not cleaned_table:
            return None
        
        # Check if first row is header
        if len(cleaned_table) > 1:
            first_row = cleaned_table[0]
            non_empty = sum(1 for cell in first_row if cell)
            
            if non_empty >= len(first_row) * 0.5:
                headers = []
                for i, cell in enumerate(first_row):
                    if cell:
                        headers.append(cell)
                    else:
                        # Use data from first data row for empty headers
                        if len(cleaned_table) > 1 and i < len(cleaned_table[1]):
                            next_cell = cleaned_table[1][i]
                            if next_cell:
                                headers.append(f"{next_cell[:20]}")
                            else:
                                headers.append(f'Col_{i+1}')
                        else:
                            headers.append(f'Col_{i+1}')
                
                # Ensure unique headers
                seen = {}
                for i, h in enumerate(headers):
                    if h in seen:
                        seen[h] += 1
                        headers[i] = f"{h}_{seen[h]}"
                    else:
                        seen[h] = 0
                
                df = pd.DataFrame(cleaned_table[1:], columns=headers)
            else:
                columns = [f'Col_{i+1}' for i in range(len(cleaned_table[0]))]
                df = pd.DataFrame(cleaned_table, columns=columns)
        else:
            columns = [f'Col_{i+1}' for i in range(len(cleaned_table[0]))]
            df = pd.DataFrame(cleaned_table, columns=columns)
        
        return df
    
    def parse_structured_text(self, text, delimiter):
        """Parse structured text to DataFrame"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Auto-detect delimiter
        if delimiter is None:
            delimiter = self.auto_detect_delimiter(text)
        
        data = []
        for line in lines:
            # Skip separator lines
            if re.match(r'^[\-=_\s|]+$', line):
                continue
                
            try:
                if delimiter == " ":
                    row = re.split(r'\s{2,}', line)
                    row = [self.clean_cell_value(cell) for cell in row if cell.strip()]
                elif delimiter == "\t":
                    row = [self.clean_cell_value(cell) for cell in line.split(delimiter)]
                elif delimiter == "|":
                    row = [self.clean_cell_value(cell) for cell in line.split(delimiter)]
                    row = [cell for cell in row if cell]
                else:
                    row = [self.clean_cell_value(cell) for cell in line.split(delimiter)]
                
                if row and any(cell for cell in row):
                    data.append(row)
            except Exception:
                continue
        
        if not data:
            return None
        
        col_counts = [len(row) for row in data]
        if not col_counts:
            return None
        
        most_common_cols = max(set(col_counts), key=col_counts.count)
        
        # Filter and normalize data
        filtered_data = []
        for row in data:
            if abs(len(row) - most_common_cols) <= 2:
                if len(row) < most_common_cols:
                    row = row + [''] * (most_common_cols - len(row))
                elif len(row) > most_common_cols:
                    row = row[:most_common_cols]
                filtered_data.append(row)
        
        if not filtered_data:
            max_cols = max(len(row) for row in data)
            filtered_data = [row + [''] * (max_cols - len(row)) for row in data]
        
        # Detect header
        if len(filtered_data) > 1:
            first_row = filtered_data[0]
            second_row = filtered_data[1]
            
            is_likely_header = False
            if all(cell.strip() for cell in first_row):
                numeric_count = 0
                text_count = 0
                for cell in first_row:
                    if cell:
                        clean_cell = cell.replace('.', '').replace(',', '').replace('-', '').replace('+', '').replace('$', '').strip()
                        if clean_cell.isdigit() or (clean_cell.replace('.', '', 1).isdigit()):
                            numeric_count += 1
                        elif len(cell) > 0:
                            text_count += 1
                
                if text_count > len(first_row) * 0.6:
                    is_likely_header = True
            
            if is_likely_header:
                headers = []
                for i, cell in enumerate(first_row):
                    if cell.strip():
                        headers.append(str(cell).strip())
                    else:
                        # Use value from first data row for empty headers
                        if i < len(second_row) and second_row[i]:
                            headers.append(f"{second_row[i][:20]}")
                        else:
                            headers.append(f'Col_{i+1}')
                
                # Ensure unique headers
                seen = {}
                for i, h in enumerate(headers):
                    if h in seen:
                        seen[h] += 1
                        headers[i] = f"{h}_{seen[h]}"
                    else:
                        seen[h] = 0
                df = pd.DataFrame(filtered_data[1:], columns=headers)
            else:
                columns = [f'Col_{i+1}' for i in range(len(filtered_data[0]))]
                df = pd.DataFrame(filtered_data, columns=columns)
        else:
            columns = [f'Col_{i+1}' for i in range(len(filtered_data[0]))]
            df = pd.DataFrame(filtered_data, columns=columns)
        
        return df
    
    def parse_simple_text(self, text):
        """Parse simple text (line by line)"""
        lines = [self.clean_cell_value(line) for line in text.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        df = pd.DataFrame({'Content': lines})
        return df
    
    def clean_dataframe(self, df):
        """Clean DataFrame"""
        if df is None or df.empty:
            return df
        
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')
        
        for col in df.columns:
            if df[col].astype(str).str.strip().eq('').all():
                df = df.drop(columns=[col])
        
        df = df.reset_index(drop=True)
        
        return df
    
    def save_to_excel(self, dfs, output_path, combine_pages):
        """Save to Excel"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                if combine_pages:
                    combined_df = pd.concat([df for _, df in dfs], ignore_index=True)
                    if self.clean_data.get():
                        combined_df = self.clean_dataframe(combined_df)
                    combined_df.to_excel(writer, sheet_name='All_Pages', index=False)
                else:
                    for page_num, df in dfs:
                        if self.clean_data.get():
                            df = self.clean_dataframe(df)
                        sheet_name = f"Page_{page_num}"[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            return True
        except Exception as e:
            raise Exception(f"Error saving Excel: {str(e)}")
    
    def save_to_csv(self, dfs, output_path, combine_pages):
        """Save to CSV"""
        try:
            if combine_pages:
                combined_df = pd.concat([df for _, df in dfs], ignore_index=True)
                if self.clean_data.get():
                    combined_df = self.clean_dataframe(combined_df)
                combined_df.to_csv(output_path, index=False, encoding='utf-8-sig', 
                                  quoting=csv.QUOTE_MINIMAL, escapechar='\\')
            else:
                if len(dfs) == 1:
                    df = dfs[0][1]
                    if self.clean_data.get():
                        df = self.clean_dataframe(df)
                    df.to_csv(output_path, index=False, encoding='utf-8-sig',
                             quoting=csv.QUOTE_MINIMAL, escapechar='\\')
                else:
                    all_dfs = []
                    for page_num, df in dfs:
                        if self.clean_data.get():
                            df = self.clean_dataframe(df)
                        separator = pd.DataFrame([[f'=== Page {page_num} ===' + '='*50]], 
                                                columns=['Page Separator'])
                        all_dfs.append(separator)
                        all_dfs.append(df)
                    
                    combined = pd.concat(all_dfs, ignore_index=True)
                    combined.to_csv(output_path, index=False, encoding='utf-8-sig',
                                   quoting=csv.QUOTE_MINIMAL, escapechar='\\')
            return True
        except Exception as e:
            raise Exception(f"Error saving CSV: {str(e)}")
    
    def convert(self):
        """Start conversion"""
        if not self.pdf_path.get():
            messagebox.showerror("Error", "Please select a PDF file!")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify output file!")
            return
        
        output_ext = Path(self.output_path.get()).suffix.lower()
        expected_ext = ".xlsx" if self.output_format.get() == "xlsx" else ".csv"
        
        if output_ext != expected_ext:
            response = messagebox.askyesno(
                "Extension Mismatch",
                f"Output extension ({output_ext}) doesn't match format ({expected_ext}).\n\n"
                f"Change to {expected_ext}?"
            )
            if response:
                new_path = Path(self.output_path.get()).with_suffix(expected_ext)
                self.output_path.set(str(new_path))
            else:
                return
        
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
    
    def run_conversion(self):
        """Run conversion process"""
        try:
            # Disable controls
            self.convert_btn.config(state='disabled')
            self.progress_active = True
            self.animate_progress()
            self.status.set("Extracting data from PDF...")
            
            pages_data = self.extract_data_from_pdf(self.pdf_path.get())
            
            if not pages_data:
                self.rootexceltopdf.after(0, lambda: messagebox.showwarning(
                    "Warning", "Could not extract data from PDF!"))
                return
            
            
            self.status.set(f"Processing {len(pages_data)} page(s)...")
            
            mode = self.mode.get()
            delimiter = self.get_delimiter()
            
            dfs = []
            errors = []
            total_pages = len(pages_data)
            
            for idx, page_data in enumerate(pages_data):
                page_num = page_data['page_num']
                df = None
                
                # Update progress
                progress = 20 + int((idx / total_pages) * 60)
                
                self.status.set(f"Processing page {page_num}/{total_pages}...")
                
                try:
                    if mode == "auto":
                        # Try tables first
                        if page_data['tables']:
                            for table in page_data['tables']:
                                df = self.table_to_dataframe(table)
                                if df is not None and not df.empty:
                                    break
                        
                        # Fallback to structured text
                        if df is None or df.empty:
                            if page_data['text']:
                                df = self.parse_structured_text(page_data['text'], None)
                    
                    elif mode == "text":
                        if page_data['text']:
                            df = self.parse_structured_text(page_data['text'], delimiter)
                    
                    elif mode == "simple":
                        if page_data['text']:
                            df = self.parse_simple_text(page_data['text'])
                    
                    if df is not None and not df.empty:
                        dfs.append((page_num, df))
                    else:
                        errors.append(f"Page {page_num}: No data extracted")
                        
                except Exception as e:
                    errors.append(f"Page {page_num}: {str(e)}")
            
            if not dfs:
                error_msg = "Could not extract data from PDF!\n\n"
                if errors:
                    error_msg += "Errors:\n" + "\n".join(errors[:5])
                self.rootexceltopdf.after(0, lambda msg=error_msg: messagebox.showwarning("Warning", msg))
                return
            
            
            self.status.set("Saving file...")
            
            output_format = self.output_format.get()
            combine_pages = self.all_pages.get()
            
            if output_format == "xlsx":
                self.save_to_excel(dfs, self.output_path.get(), combine_pages)
            else:
                self.save_to_csv(dfs, self.output_path.get(), combine_pages)
            
            
            
            success_msg = f"Conversion completed successfully!\n\n"
            success_msg += f"Pages processed: {len(dfs)}/{len(pages_data)}\n"
            success_msg += f"Output: {Path(self.output_path.get()).name}"
            
            if errors:
                success_msg += f"\n\nWarnings: {len(errors)} page(s) had issues"
            
            self.status.set("Conversion completed!")
            self.rootexceltopdf.after(0, lambda msg=success_msg: messagebox.showinfo("Success", msg))
            
        except Exception as e:
            self.status.set("Conversion error!")
            error_msg = f"An error occurred:\n\n{str(e)}"
            self.rootexceltopdf.after(0, lambda msg=error_msg: messagebox.showerror("Error", msg))
        
        finally:
            self.progress_active = False
            self.progress_canvas.delete("all")
            self.rootexceltopdf.after(0, lambda: self.convert_btn.config(state='normal'))

if __name__ == "__main__":
    rootexceltopdf = tk.Tk()
    app = PDFtoExcelConverter(rootexceltopdf)
    rootexceltopdf.mainloop()