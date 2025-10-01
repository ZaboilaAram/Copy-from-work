import tkinter as tk
from tkinter import filedialog, messagebox
import os
from pathlib import Path
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from docx import Document

class Win95PDFConverter:
    def __init__(self, rootconvertoR):
        self.rootconvertoR = rootconvertoR
        self.rootconvertoR.title("File to PDF Converter")
        self.rootconvertoR.geometry("500x400")
        self.rootconvertoR.resizable(False, False)
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.dark_shadow = "#808080"
        self.light_shadow = "#ffffff"
        self.button_color = "#c0c0c0"
        self.text_bg = "#ffffff"
        
        self.rootconvertoR.configure(bg=self.bg_color)
        
        self.selected_file = None
        self.setup_ui()
    
    def create_3d_frame(self, parent, sunken=False):
        """Create a frame with 3D border effect"""
        frame = tk.Frame(parent, bg=self.bg_color)
        
        if sunken:
            # Sunken effect (dark on top/left, light on bottom/right)
            top = tk.Frame(frame, bg=self.dark_shadow, height=2)
            top.pack(side=tk.TOP, fill=tk.X)
            left = tk.Frame(frame, bg=self.dark_shadow, width=2)
            left.pack(side=tk.LEFT, fill=tk.Y)
            bottom = tk.Frame(frame, bg=self.light_shadow, height=2)
            bottom.pack(side=tk.BOTTOM, fill=tk.X)
            right = tk.Frame(frame, bg=self.light_shadow, width=2)
            right.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            # Raised effect (light on top/left, dark on bottom/right)
            top = tk.Frame(frame, bg=self.light_shadow, height=2)
            top.pack(side=tk.TOP, fill=tk.X)
            left = tk.Frame(frame, bg=self.light_shadow, width=2)
            left.pack(side=tk.LEFT, fill=tk.Y)
            bottom = tk.Frame(frame, bg=self.dark_shadow, height=2)
            bottom.pack(side=tk.BOTTOM, fill=tk.X)
            right = tk.Frame(frame, bg=self.dark_shadow, width=2)
            right.pack(side=tk.RIGHT, fill=tk.Y)
        
        inner = tk.Frame(frame, bg=self.bg_color)
        inner.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)
        
        return frame, inner
    
    def setup_ui(self):
        # Title
        title_label = tk.Label(
            self.rootconvertoR,
            text="File to PDF Converter",
            font=("MS Sans Serif", 14, "bold"),
            bg=self.bg_color,
            fg="#000080"
        )
        title_label.pack(pady=20)
        
        # Main container
        main_frame, inner_main = self.create_3d_frame(self.rootconvertoR, sunken=True)
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # File selection section
        file_frame = tk.Frame(inner_main, bg=self.bg_color)
        file_frame.pack(pady=20, padx=10, fill=tk.X)
        
        tk.Label(
            file_frame,
            text="Selected File:",
            font=("MS Sans Serif", 9),
            bg=self.bg_color
        ).pack(anchor=tk.W)
        
        # File display with sunken frame
        display_frame, display_inner = self.create_3d_frame(file_frame, sunken=True)
        display_frame.pack(fill=tk.X, pady=5)
        
        self.file_label = tk.Label(
            display_inner,
            text="No file selected",
            font=("MS Sans Serif", 9),
            bg=self.text_bg,
            anchor=tk.W,
            padx=5,
            pady=5
        )
        self.file_label.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(inner_main, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        # Browse button
        browse_btn = tk.Button(
            button_frame,
            text="Browse...",
            font=("MS Sans Serif", 9),
            bg=self.button_color,
            relief=tk.RAISED,
            bd=2,
            width=15,
            command=self.browse_file
        )
        browse_btn.pack(pady=5)
        
        # Convert button
        convert_btn = tk.Button(
            button_frame,
            text="Convert to PDF",
            font=("MS Sans Serif", 9, "bold"),
            bg=self.button_color,
            relief=tk.RAISED,
            bd=2,
            width=15,
            command=self.convert_file
        )
        convert_btn.pack(pady=5)
        
        # Help button
        help_btn = tk.Button(
            button_frame,
            text="Help",
            font=("MS Sans Serif", 9),
            bg=self.button_color,
            relief=tk.RAISED,
            bd=2,
            width=15,
            command=self.show_help
        )
        help_btn.pack(pady=5)
        
        # Supported formats label
        formats_label = tk.Label(
            inner_main,
            text="Supported formats: XLSX, CSV, DOCX",
            font=("MS Sans Serif", 8),
            bg=self.bg_color,
            fg=self.dark_shadow
        )
        formats_label.pack(side=tk.BOTTOM, pady=10)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a file to convert",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("Word files", "*.docx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file = file_path
            file_name = os.path.basename(file_path)
            self.file_label.config(text=file_name)
    
    def convert_xlsx_to_pdf(self, input_file, output_file):
        """Convert Excel file to PDF"""
        df = pd.read_excel(input_file)
        
        pdf = SimpleDocTemplate(output_file, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Convert dataframe to list of lists with Paragraphs for text wrapping
        header = [[Paragraph(str(col), styles['Normal']) for col in df.columns]]
        
        data_rows = []
        for _, row in df.iterrows():
            data_row = [Paragraph(str(cell), styles['Normal']) for cell in row]
            data_rows.append(data_row)
        
        data = header + data_rows
        
        # Calculate column widths to fit page
        available_width = letter[0] - 100  # Leave margins
        col_width = available_width / len(df.columns)
        col_widths = [col_width] * len(df.columns)
        
        # Create table with column widths and allow splitting across pages
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        elements.append(table)
        pdf.build(elements)
    
    def convert_csv_to_pdf(self, input_file, output_file):
        """Convert CSV file to PDF"""
        df = pd.read_csv(input_file)
        
        pdf = SimpleDocTemplate(output_file, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Convert dataframe to list of lists with Paragraphs for text wrapping
        header = [[Paragraph(str(col), styles['Normal']) for col in df.columns]]
        
        data_rows = []
        for _, row in df.iterrows():
            data_row = [Paragraph(str(cell), styles['Normal']) for cell in row]
            data_rows.append(data_row)
        
        data = header + data_rows
        
        # Calculate column widths to fit page
        available_width = letter[0] - 100  # Leave margins
        col_width = available_width / len(df.columns)
        col_widths = [col_width] * len(df.columns)
        
        # Create table with column widths and allow splitting across pages
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        elements.append(table)
        pdf.build(elements)
    
    def convert_docx_to_pdf(self, input_file, output_file):
        """Convert Word document to PDF"""
        doc = Document(input_file)
        
        pdf = SimpleDocTemplate(output_file, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                p = Paragraph(paragraph.text, styles['Normal'])
                elements.append(p)
                elements.append(Spacer(1, 12))
        
        pdf.build(elements)
    
    def convert_file(self):
        if not self.selected_file:
            messagebox.showwarning(
                "No File Selected",
                "Please select a file to convert."
            )
            return
        
        # Get file extension
        file_ext = Path(self.selected_file).suffix.lower()
        
        # Check if supported
        if file_ext not in ['.xlsx', '.csv', '.docx']:
            messagebox.showerror(
                "Unsupported Format",
                "Please select an XLSX, CSV, or DOCX file."
            )
            return
        
        # Ask for save location
        output_file = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=Path(self.selected_file).stem + ".pdf"
        )
        
        if not output_file:
            return
        
        try:
            # Convert based on file type
            if file_ext == '.xlsx':
                self.convert_xlsx_to_pdf(self.selected_file, output_file)
            elif file_ext == '.csv':
                self.convert_csv_to_pdf(self.selected_file, output_file)
            elif file_ext == '.docx':
                self.convert_docx_to_pdf(self.selected_file, output_file)
            
            messagebox.showinfo(
                "Success",
                "File converted successfully!"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Conversion Error",
                f"An error occurred during conversion:\n{str(e)}"
            )
    
    def show_help(self):
        """Show help dialog with program information"""
        help_text = """File to PDF Converter - Help

SUPPORTED FORMATS:
- XLSX (Microsoft Excel)
- CSV (Comma-Separated Values)
- DOCX (Microsoft Word)

WHAT IT DOES:

XLSX & CSV Files:
- Converts spreadsheet data into PDF tables
- Automatically wraps long text in cells
- Splits large tables across multiple pages
- Repeats header row on each page
- Does NOT support embedded images or charts

DOCX Files:
- Converts text paragraphs to PDF
- Preserves paragraph structure
- Does NOT support images, tables, or formatting

HOW TO USE:
1. Click "Browse..." to select your file
2. Click "Convert to PDF" to choose output location
3. Wait for the success message

LIMITATIONS:
- Images are not supported in any format
- Charts and graphs are not converted
- Complex formatting may be simplified
- Very wide tables may have small text

Version 1.0"""
        
        # Create help window
        help_window = tk.Toplevel(self.rootconvertoR)
        help_window.title("Help - File to PDF Converter")
        help_window.geometry("450x500")
        help_window.resizable(False, False)
        help_window.configure(bg=self.bg_color)
        
        # Make it modal
        help_window.transient(self.rootconvertoR)
        help_window.grab_set()
        
        # Main frame with 3D border
        main_frame, inner_main = self.create_3d_frame(help_window, sunken=True)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Text widget for help content
        text_widget = tk.Text(
            inner_main,
            font=("MS Sans Serif", 9),
            bg=self.text_bg,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            height=25,
            width=50
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", help_text)
        text_widget.config(state=tk.DISABLED)
        
        # OK button
        ok_btn = tk.Button(
            help_window,
            text="OK",
            font=("MS Sans Serif", 9),
            bg=self.button_color,
            relief=tk.RAISED,
            bd=2,
            width=10,
            command=help_window.destroy
        )
        ok_btn.pack(pady=10)

def main():
    rootconvertoR = tk.Tk()
    app = Win95PDFConverter(rootconvertoR)
    rootconvertoR.mainloop()

if __name__ == "__main__":
    main()