import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import re
import hashlib
import base64
import string
import math

class RetroConverterEcosystem:
    def __init__(self, rootconvcalc1):
        self.rootconvcalc1 = rootconvcalc1
        self.rootconvcalc1.title("Universal Converter Suite")
        self.rootconvcalc1.geometry("950x800")
        self.rootconvcalc1.resizable(False, False)
        
        # Windows 95 colors
        self.bg_color = "#c0c0c0"
        self.highlight = "#dfdfdf"
        self.shadow = "#808080"
        self.dark_shadow = "#000000"
        self.text_bg = "#ffffff"
        self.text_fg = "#000000"
        self.blue_title = "#000080"
        self.blue_active = "#0000aa"
        
        self.rootconvcalc1.configure(bg=self.bg_color)
        
        # History storage
        self.history = []
        self.current_tab = "numbers"
        
        # Calculator state
        self.calc_display = ""
        self.calc_memory = 0
        self.calc_last_result = 0
        self.calc_current_operation = None
        self.calc_first_operand = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.rootconvcalc1, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Title bar
        title_frame = tk.Frame(main_frame, bg=self.blue_title, height=20)
        title_frame.pack(fill=tk.X, side=tk.TOP)
        title_label = tk.Label(title_frame, text="Universal Converter Suite v3.0 - Full Operations", 
                              bg=self.blue_title, fg="#ffffff", font=("MS Sans Serif", 9, "bold"),
                              anchor="w", padx=2)
        title_label.pack(fill=tk.X)
        
        # Tab selector
        tab_frame = tk.Frame(main_frame, bg=self.bg_color, height=30)
        tab_frame.pack(fill=tk.X, padx=2, pady=(2, 0))
        
        tab_label = tk.Label(tab_frame, text="Select Tool:", bg=self.bg_color, 
                            fg=self.text_fg, font=("MS Sans Serif", 8))
        tab_label.pack(anchor="w", padx=5, pady=2)
        
        button_frame = tk.Frame(tab_frame, bg=self.bg_color)
        button_frame.pack(anchor="w", padx=5, pady=2)
        
        self.tab_buttons = {}
        tabs = [("numbers", "Number Systems"), ("text", "Text Tools"), 
                ("hash", "Hash/Encode"), ("calculator", "Calculator"), ("analyze", "Analysis")]
        
        for tab_id, tab_name in tabs:
            btn = tk.Button(button_frame, text=tab_name, command=lambda t=tab_id: self.switch_tab(t),
                           bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8),
                           relief=tk.RAISED, borderwidth=2, padx=8, pady=2,
                           activebackground=self.highlight, activeforeground=self.text_fg)
            btn.pack(side=tk.LEFT, padx=2)
            self.tab_buttons[tab_id] = btn
        
        # Content area
        self.content_frame = tk.Frame(main_frame, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Initialize tabs
        self.tabs = {}
        self.create_number_tab()
        self.create_text_tab()
        self.create_hash_tab()
        self.create_calculator_tab()
        self.create_analysis_tab()
        
        self.switch_tab("numbers")
    
    def create_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command, 
                       bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8),
                       relief=tk.RAISED, borderwidth=2, padx=10, pady=2,
                       activebackground=self.highlight, activeforeground=self.text_fg)
        return btn
    
    def switch_tab(self, tab_id):
        for tab_content in self.tabs.values():
            tab_content.pack_forget()
        self.tabs[tab_id].pack(fill=tk.BOTH, expand=True)
        self.current_tab = tab_id
    
    # ==================== NUMBER SYSTEMS TAB ====================
    def create_number_tab(self):
        tab = tk.Frame(self.content_frame, bg=self.bg_color)
        self.tabs["numbers"] = tab
        
        input_label = tk.Label(tab, text="Input Value:", 
                              bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8))
        input_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        self.num_input_var = tk.StringVar()
        self.num_input_entry = tk.Entry(tab, textvariable=self.num_input_var, 
                                        bg=self.text_bg, fg=self.text_fg, font=("MS Sans Serif", 9),
                                        width=50)
        self.num_input_entry.pack(padx=5, pady=2, fill=tk.X)
        self.num_input_entry.bind("<KeyRelease>", lambda e: self.convert_numbers())
        
        format_label = tk.Label(tab, text="Input Format:", 
                               bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8))
        format_label.pack(anchor="w", padx=5, pady=(10, 0))
        
        button_frame = tk.Frame(tab, bg=self.bg_color)
        button_frame.pack(anchor="w", padx=5, pady=2)
        
        self.num_format = tk.StringVar(value="decimal")
        for fmt in ["decimal", "binary", "hexadecimal", "octal"]:
            rb = tk.Radiobutton(button_frame, text=fmt.capitalize(), variable=self.num_format,
                               value=fmt, bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8),
                               command=self.convert_numbers, activebackground=self.bg_color)
            rb.pack(anchor="w", pady=1)
        
        sep = tk.Frame(tab, bg=self.shadow, height=1)
        sep.pack(fill=tk.X, padx=5, pady=8)
        
        output_label = tk.Label(tab, text="Conversion Results:", 
                               bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8, "bold"))
        output_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        self.num_output_text = scrolledtext.ScrolledText(tab, height=12, width=60,
                                                         bg=self.text_bg, fg=self.text_fg,
                                                         font=("Courier New", 9),
                                                         wrap=tk.WORD, relief=tk.SUNKEN,
                                                         borderwidth=1)
        self.num_output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.num_output_text.config(state=tk.DISABLED)
        
        sep2 = tk.Frame(tab, bg=self.shadow, height=1)
        sep2.pack(fill=tk.X, padx=5, pady=8)
        
        btn_frame = tk.Frame(tab, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_button(btn_frame, "Convert", self.convert_numbers).pack(side=tk.LEFT, padx=2)
        self.create_button(btn_frame, "Clear", self.clear_numbers).pack(side=tk.LEFT, padx=2)
    
    def convert_numbers(self):
        input_value = self.num_input_var.get().strip()
        if not input_value:
            self.display_num_output("")
            return
        
        input_format = self.num_format.get()
        
        try:
            if input_format == "decimal":
                if not re.match(r'^-?\d+$', input_value):
                    raise ValueError("Invalid decimal format")
                decimal_val = int(input_value)
            elif input_format == "binary":
                if not re.match(r'^-?[01]+$', input_value):
                    raise ValueError("Invalid binary format")
                decimal_val = int(input_value, 2)
            elif input_format == "hexadecimal":
                if not re.match(r'^-?[0-9a-fA-F]+$', input_value):
                    raise ValueError("Invalid hexadecimal format")
                decimal_val = int(input_value, 16)
            elif input_format == "octal":
                if not re.match(r'^-?[0-7]+$', input_value):
                    raise ValueError("Invalid octal format")
                decimal_val = int(input_value, 8)
            
            output = "[NUMBER CONVERSION]\n" + "-" * 40 + "\n\n"
            output += f"DECIMAL:\n  {decimal_val}\n\n"
            
            if decimal_val >= 0:
                output += f"BINARY:\n  {bin(decimal_val)[2:]}\n"
                output += f"  ({len(bin(decimal_val)[2:])} bits)\n\n"
                output += f"HEXADECIMAL:\n  {hex(decimal_val)[2:].upper()}\n\n"
                output += f"OCTAL:\n  {oct(decimal_val)[2:]}\n\n"
                output += "-" * 40 + "\n"
                output += f"Bits needed: {decimal_val.bit_length()}\n"
                output += f"Power of 2: {decimal_val > 0 and (decimal_val & (decimal_val - 1)) == 0}\n"
            else:
                output += f"BINARY:\n  -{bin(decimal_val)[3:]}\n\n"
                output += f"HEXADECIMAL:\n  -{hex(decimal_val)[3:].upper()}\n\n"
                output += f"OCTAL:\n  -{oct(decimal_val)[3:]}\n"
            
            self.display_num_output(output)
            self.add_history(f"Number: {input_value} ({input_format})")
            
        except ValueError as e:
            self.display_num_output(f"ERROR: {str(e)}")
    
    def display_num_output(self, text):
        self.num_output_text.config(state=tk.NORMAL)
        self.num_output_text.delete(1.0, tk.END)
        self.num_output_text.insert(tk.END, text)
        self.num_output_text.config(state=tk.DISABLED)
    
    def clear_numbers(self):
        self.num_input_var.set("")
        self.display_num_output("")
    
    # ==================== TEXT TOOLS TAB ====================
    def create_text_tab(self):
        tab = tk.Frame(self.content_frame, bg=self.bg_color)
        self.tabs["text"] = tab
        
        input_label = tk.Label(tab, text="Input Text:", 
                              bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8))
        input_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        self.text_input_var = tk.StringVar()
        self.text_input_entry = tk.Entry(tab, textvariable=self.text_input_var, 
                                        bg=self.text_bg, fg=self.text_fg, font=("MS Sans Serif", 9),
                                        width=80)
        self.text_input_entry.pack(padx=5, pady=2, fill=tk.X)
        self.text_input_entry.bind("<KeyRelease>", lambda e: self.convert_text())
        
        tools_label = tk.Label(tab, text="Text Tools:", 
                              bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8))
        tools_label.pack(anchor="w", padx=5, pady=(10, 0))
        
        tools_frame = tk.Frame(tab, bg=self.bg_color)
        tools_frame.pack(anchor="w", padx=5, pady=2)
        
        self.text_tool = tk.StringVar(value="ascii")
        for tool in ["ascii", "reverse", "uppercase", "lowercase", "title", "count", 
                     "text2binary", "text2hex", "text2octal", "binary2text", "hex2text"]:
            rb = tk.Radiobutton(tools_frame, text=self.get_tool_display_name(tool), 
                               variable=self.text_tool,
                               value=tool, bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8),
                               command=self.convert_text, activebackground=self.bg_color)
            rb.pack(anchor="w", pady=1)
        
        sep = tk.Frame(tab, bg=self.shadow, height=1)
        sep.pack(fill=tk.X, padx=5, pady=8)
        
        output_label = tk.Label(tab, text="Output / Analysis:", 
                               bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8, "bold"))
        output_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        self.text_output_text = scrolledtext.ScrolledText(tab, height=12, width=80,
                                                         bg=self.text_bg, fg=self.text_fg,
                                                         font=("Courier New", 9),
                                                         wrap=tk.WORD, relief=tk.SUNKEN,
                                                         borderwidth=1)
        self.text_output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.text_output_text.config(state=tk.DISABLED)
        
        sep2 = tk.Frame(tab, bg=self.shadow, height=1)
        sep2.pack(fill=tk.X, padx=5, pady=8)
        
        btn_frame = tk.Frame(tab, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_button(btn_frame, "Process", self.convert_text).pack(side=tk.LEFT, padx=2)
        self.create_button(btn_frame, "Clear", self.clear_text).pack(side=tk.LEFT, padx=2)
    
    def get_tool_display_name(self, tool):
        names = {
            "ascii": "ASCII Values",
            "reverse": "Reverse Text",
            "uppercase": "Uppercase",
            "lowercase": "Lowercase",
            "title": "Title Case",
            "count": "Count Stats",
            "text2binary": "Text to Binary",
            "text2hex": "Text to Hex",
            "text2octal": "Text to Octal",
            "binary2text": "Binary to Text",
            "hex2text": "Hex to Text"
        }
        return names.get(tool, tool.capitalize())
    
    def convert_text(self):
        input_text = self.text_input_var.get()
        if not input_text:
            self.display_text_output("")
            return
        
        tool = self.text_tool.get()
        output = ""
        
        if tool == "ascii":
            output = "[ASCII VALUES]\n" + "-" * 60 + "\n\n"
            for i, char in enumerate(input_text):
                output += f"'{char}' -> {ord(char):3d} (0x{ord(char):02X}) ({bin(ord(char))[2:]:>8s})\n"
                if (i + 1) % 4 == 0:
                    output += "\n"
        
        elif tool == "reverse":
            reversed_text = input_text[::-1]
            output = "[TEXT REVERSED]\n" + "-" * 60 + "\n"
            output += f"Original:  {input_text}\n\n"
            output += f"Reversed:  {reversed_text}\n"
        
        elif tool == "uppercase":
            upper = input_text.upper()
            output = "[UPPERCASE]\n" + "-" * 60 + "\n"
            output += f"{upper}\n"
        
        elif tool == "lowercase":
            lower = input_text.lower()
            output = "[LOWERCASE]\n" + "-" * 60 + "\n"
            output += f"{lower}\n"
        
        elif tool == "title":
            title = input_text.title()
            output = "[TITLE CASE]\n" + "-" * 60 + "\n"
            output += f"{title}\n"
        
        elif tool == "count":
            output = "[TEXT STATISTICS]\n" + "-" * 60 + "\n\n"
            output += f"Total characters: {len(input_text)}\n"
            output += f"Letters: {sum(1 for c in input_text if c.isalpha())}\n"
            output += f"Digits: {sum(1 for c in input_text if c.isdigit())}\n"
            output += f"Spaces: {sum(1 for c in input_text if c.isspace())}\n"
            output += f"Words: {len(input_text.split())}\n"
            output += f"Lines: {len(input_text.splitlines())}\n"
            output += f"Uppercase: {sum(1 for c in input_text if c.isupper())}\n"
            output += f"Lowercase: {sum(1 for c in input_text if c.islower())}\n"
        
        elif tool == "text2binary":
            output = "[TEXT TO BINARY]\n" + "-" * 60 + "\n\n"
            output += "Character breakdown:\n"
            for char in input_text:
                binary = bin(ord(char))[2:].zfill(8)
                output += f"'{char}' (ASCII {ord(char):3d}) -> {binary}\n"
            output += "\nCombined binary:\n"
            combined = "".join(bin(ord(c))[2:].zfill(8) for c in input_text)
            output += f"{combined}\n\n"
            output += f"Total bits: {len(combined)}\n"
        
        elif tool == "text2hex":
            output = "[TEXT TO HEXADECIMAL]\n" + "-" * 60 + "\n\n"
            output += "Character breakdown:\n"
            for char in input_text:
                hexval = hex(ord(char))[2:].upper().zfill(2)
                output += f"'{char}' (ASCII {ord(char):3d}) -> {hexval}\n"
            output += "\nCombined hexadecimal:\n"
            combined = "".join(hex(ord(c))[2:].upper().zfill(2) for c in input_text)
            output += f"{combined}\n\n"
            output += f"Total bytes: {len(combined) // 2}\n"
        
        elif tool == "text2octal":
            output = "[TEXT TO OCTAL]\n" + "-" * 60 + "\n\n"
            output += "Character breakdown:\n"
            for char in input_text:
                octal = oct(ord(char))[2:].zfill(3)
                output += f"'{char}' (ASCII {ord(char):3d}) -> {octal}\n"
            output += "\nCombined octal:\n"
            combined = "".join(oct(ord(c))[2:].zfill(3) for c in input_text)
            output += f"{combined}\n"
        
        elif tool == "binary2text":
            try:
                binary_clean = input_text.replace(" ", "").replace("\n", "").replace("\t", "")
                if not re.match(r'^[01]+$', binary_clean):
                    raise ValueError("Invalid binary format (only 0 and 1 allowed)")
                
                if len(binary_clean) % 8 != 0:
                    raise ValueError(f"Binary length ({len(binary_clean)}) must be multiple of 8")
                
                output = "[BINARY TO TEXT]\n" + "-" * 60 + "\n\n"
                result_text = ""
                for i in range(0, len(binary_clean), 8):
                    byte = binary_clean[i:i+8]
                    ascii_val = int(byte, 2)
                    char = chr(ascii_val)
                    result_text += char
                    output += f"{byte} -> {ascii_val:3d} ('{char}')\n"
                
                output += f"\nDecoded text:\n{result_text}\n"
            except Exception as e:
                output = f"ERROR: {str(e)}"
        
        elif tool == "hex2text":
            try:
                hex_clean = input_text.replace(" ", "").replace("\n", "").replace("\t", "")
                if not re.match(r'^[0-9a-fA-F]*$', hex_clean):
                    raise ValueError("Invalid hexadecimal format")
                
                if len(hex_clean) % 2 != 0:
                    raise ValueError(f"Hex length ({len(hex_clean)}) must be even")
                
                output = "[HEX TO TEXT]\n" + "-" * 60 + "\n\n"
                result_text = ""
                for i in range(0, len(hex_clean), 2):
                    byte = hex_clean[i:i+2]
                    ascii_val = int(byte, 16)
                    char = chr(ascii_val)
                    result_text += char
                    output += f"{byte} -> {ascii_val:3d} ('{char}')\n"
                
                output += f"\nDecoded text:\n{result_text}\n"
            except Exception as e:
                output = f"ERROR: {str(e)}"
        
        self.display_text_output(output)
        self.add_history(f"Text: {input_text[:30]}... ({tool})")
    
    def display_text_output(self, text):
        self.text_output_text.config(state=tk.NORMAL)
        self.text_output_text.delete(1.0, tk.END)
        self.text_output_text.insert(tk.END, text)
        self.text_output_text.config(state=tk.DISABLED)
    
    def clear_text(self):
        self.text_input_var.set("")
        self.display_text_output("")
    
    # ==================== HASH/ENCODE TAB ====================
    def create_hash_tab(self):
        tab = tk.Frame(self.content_frame, bg=self.bg_color)
        self.tabs["hash"] = tab
        
        input_label = tk.Label(tab, text="Input String:", 
                              bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8))
        input_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        self.hash_input_var = tk.StringVar()
        self.hash_input_entry = tk.Entry(tab, textvariable=self.hash_input_var, 
                                        bg=self.text_bg, fg=self.text_fg, font=("MS Sans Serif", 9),
                                        width=80)
        self.hash_input_entry.pack(padx=5, pady=2, fill=tk.X)
        self.hash_input_entry.bind("<KeyRelease>", lambda e: self.convert_hash())
        
        methods_label = tk.Label(tab, text="Hash/Encode Method:", 
                                bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8))
        methods_label.pack(anchor="w", padx=5, pady=(10, 0))
        
        methods_frame = tk.Frame(tab, bg=self.bg_color)
        methods_frame.pack(anchor="w", padx=5, pady=2)
        
        self.hash_method = tk.StringVar(value="md5")
        for method in ["md5", "sha1", "sha256", "base64", "rot13"]:
            rb = tk.Radiobutton(methods_frame, text=method.upper(), variable=self.hash_method,
                               value=method, bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8),
                               command=self.convert_hash, activebackground=self.bg_color)
            rb.pack(anchor="w", pady=1)
        
        sep = tk.Frame(tab, bg=self.shadow, height=1)
        sep.pack(fill=tk.X, padx=5, pady=8)
        
        output_label = tk.Label(tab, text="Output:", 
                               bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8, "bold"))
        output_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        self.hash_output_text = scrolledtext.ScrolledText(tab, height=12, width=80,
                                                         bg=self.text_bg, fg=self.text_fg,
                                                         font=("Courier New", 9),
                                                         wrap=tk.WORD, relief=tk.SUNKEN,
                                                         borderwidth=1)
        self.hash_output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.hash_output_text.config(state=tk.DISABLED)
        
        sep2 = tk.Frame(tab, bg=self.shadow, height=1)
        sep2.pack(fill=tk.X, padx=5, pady=8)
        
        btn_frame = tk.Frame(tab, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_button(btn_frame, "Encode/Hash", self.convert_hash).pack(side=tk.LEFT, padx=2)
        self.create_button(btn_frame, "Clear", self.clear_hash).pack(side=tk.LEFT, padx=2)
    
    def rot13(self, text):
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr((ord(char) - ord('a') + 13) % 26 + ord('a')))
            elif 'A' <= char <= 'Z':
                result.append(chr((ord(char) - ord('A') + 13) % 26 + ord('A')))
            else:
                result.append(char)
        return ''.join(result)
    
    def convert_hash(self):
        input_str = self.hash_input_var.get()
        if not input_str:
            self.display_hash_output("")
            return
        
        method = self.hash_method.get()
        output = ""
        
        try:
            if method == "md5":
                result = hashlib.md5(input_str.encode()).hexdigest()
                output = f"[MD5 HASH]\n{'-'*40}\n\n{result}\n"
            
            elif method == "sha1":
                result = hashlib.sha1(input_str.encode()).hexdigest()
                output = f"[SHA-1 HASH]\n{'-'*40}\n\n{result}\n"
            
            elif method == "sha256":
                result = hashlib.sha256(input_str.encode()).hexdigest()
                output = f"[SHA-256 HASH]\n{'-'*40}\n\n{result}\n"
            
            elif method == "base64":
                encoded = base64.b64encode(input_str.encode()).decode()
                output = f"[BASE64 ENCODING]\n{'-'*40}\n\n"
                output += f"Encoded:\n{encoded}\n\n"
                output += f"(Can be decoded back to original)\n"
            
            elif method == "rot13":
                result = self.rot13(input_str)
                output = f"[ROT-13 CIPHER]\n{'-'*40}\n\n"
                output += f"Original:  {input_str}\n\n"
                output += f"Encoded:   {result}\n"
            
            self.display_hash_output(output)
            self.add_history(f"Hash: {input_str[:20]}... ({method})")
        
        except Exception as e:
            self.display_hash_output(f"ERROR: {str(e)}")
    
    def display_hash_output(self, text):
        self.hash_output_text.config(state=tk.NORMAL)
        self.hash_output_text.delete(1.0, tk.END)
        self.hash_output_text.insert(tk.END, text)
        self.hash_output_text.config(state=tk.DISABLED)
    
    def clear_hash(self):
        self.hash_input_var.set("")
        self.display_hash_output("")
    
    # ==================== CALCULATOR TAB ====================
    def create_calculator_tab(self):
        tab = tk.Frame(self.content_frame, bg=self.bg_color)
        self.tabs["calculator"] = tab
        
        # Calculator mode selector
        mode_label = tk.Label(tab, text="Calculator Mode:", 
                             bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8))
        mode_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        mode_frame = tk.Frame(tab, bg=self.bg_color)
        mode_frame.pack(anchor="w", padx=5, pady=2)
        
        self.calc_mode = tk.StringVar(value="decimal")
        for mode in ["decimal", "binary", "hexadecimal", "octal"]:
            rb = tk.Radiobutton(mode_frame, text=mode.capitalize(), variable=self.calc_mode,
                               value=mode, bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8),
                               command=self.update_calc_buttons, activebackground=self.bg_color)
            rb.pack(side=tk.LEFT, padx=5)
        
        # Display
        display_frame = tk.Frame(tab, bg=self.bg_color, relief=tk.SUNKEN, borderwidth=2)
        display_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.calc_display_var = tk.StringVar(value="0")
        display = tk.Entry(display_frame, textvariable=self.calc_display_var,
                          bg=self.text_bg, fg=self.text_fg, font=("Courier New", 16, "bold"),
                          justify=tk.RIGHT, state="readonly", relief=tk.FLAT)
        display.pack(fill=tk.X, padx=2, pady=2)
        
        # Secondary display for conversions
        self.calc_secondary_var = tk.StringVar(value="")
        secondary = tk.Label(tab, textvariable=self.calc_secondary_var,
                            bg=self.bg_color, fg=self.shadow, font=("Courier New", 7),
                            anchor="e")
        secondary.pack(fill=tk.X, padx=7, pady=(0, 5))
        
        # Calculator buttons
        button_frame = tk.Frame(tab, bg=self.bg_color)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button layout - Extended with all operations
        buttons = [
            ['MC', 'MR', 'MS', 'M+', 'M-'],
            ['<<', '>>', 'sqrt', 'pow', '%'],
            ['7', '8', '9', '/', 'C'],
            ['4', '5', '6', '*', 'CE'],
            ['1', '2', '3', '-', '('],
            ['0', 'A', 'B', '+', ')'],
            ['C', 'D', 'E', '=', 'ABS'],
            ['F', 'AND', 'OR', 'XOR', 'NOT'],
            ['NAND', 'NOR', 'NEG', 'INV', '!']
        ]
        
        self.calc_buttons = {}
        
        for i, row in enumerate(buttons):
            row_frame = tk.Frame(button_frame, bg=self.bg_color)
            row_frame.pack(fill=tk.X, pady=1)
            
            for j, btn_text in enumerate(row):
                if btn_text in ['A', 'B', 'C', 'D', 'E', 'F']:
                    cmd = lambda t=btn_text: self.calc_button_click(t)
                    btn = tk.Button(row_frame, text=btn_text, command=cmd,
                                   bg="#dfdfdf", fg=self.text_fg, font=("MS Sans Serif", 9, "bold"),
                                   relief=tk.RAISED, borderwidth=2, width=7, height=1,
                                   activebackground=self.highlight)
                    self.calc_buttons[btn_text] = btn
                elif btn_text in ['/', '*', '-', '+', '=', '%', 'pow']:
                    cmd = lambda t=btn_text: self.calc_button_click(t)
                    btn = tk.Button(row_frame, text=btn_text, command=cmd,
                                   bg="#e0e0e0", fg="#000080", font=("MS Sans Serif", 9, "bold"),
                                   relief=tk.RAISED, borderwidth=2, width=7, height=1,
                                   activebackground=self.highlight)
                    self.calc_buttons[btn_text] = btn
                elif btn_text in ['AND', 'OR', 'XOR', 'NOT', 'NAND', 'NOR']:
                    cmd = lambda t=btn_text: self.calc_button_click(t)
                    btn = tk.Button(row_frame, text=btn_text, command=cmd,
                                   bg="#b0b0ff", fg="#000080", font=("MS Sans Serif", 7, "bold"),
                                   relief=tk.RAISED, borderwidth=2, width=7, height=1,
                                   activebackground=self.highlight)
                    self.calc_buttons[btn_text] = btn
                else:
                    cmd = lambda t=btn_text: self.calc_button_click(t)
                    btn = tk.Button(row_frame, text=btn_text, command=cmd,
                                   bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 8),
                                   relief=tk.RAISED, borderwidth=2, width=7, height=1,
                                   activebackground=self.highlight)
                    self.calc_buttons[btn_text] = btn
                
                btn.pack(side=tk.LEFT, padx=1)
        
        # Info label
        info_label = tk.Label(tab, 
                             text="Full Operations: +,-,*,/,%,pow,sqrt,AND,OR,XOR,NOT,NAND,NOR,<<,>>,ABS,NEG,INV,! • Memory: MC/MR/MS/M+/M-",
                             bg=self.bg_color, fg=self.shadow, font=("MS Sans Serif", 6),
                             wraplength=900, justify=tk.LEFT)
        info_label.pack(pady=5)
        
        self.update_calc_buttons()
    
    def update_calc_buttons(self):
        mode = self.calc_mode.get()
        
        # Reset display
        self.calc_display = ""
        self.calc_display_var.set("0")
        self.calc_secondary_var.set("")
        self.calc_first_operand = None
        self.calc_current_operation = None
        
        # Enable/disable hex buttons based on mode
        hex_buttons = ['A', 'B', 'C', 'D', 'E', 'F']
        
        if mode == "hexadecimal":
            for btn in hex_buttons:
                self.calc_buttons[btn].config(state=tk.NORMAL)
        else:
            for btn in hex_buttons:
                self.calc_buttons[btn].config(state=tk.DISABLED)
        
        # Disable certain digits for binary and octal
        if mode == "binary":
            for num in ['2', '3', '4', '5', '6', '7', '8', '9']:
                if num in self.calc_buttons:
                    self.calc_buttons[num].config(state=tk.DISABLED)
        elif mode == "octal":
            for num in ['8', '9']:
                if num in self.calc_buttons:
                    self.calc_buttons[num].config(state=tk.DISABLED)
            for num in ['2', '3', '4', '5', '6', '7']:
                if num in self.calc_buttons:
                    self.calc_buttons[num].config(state=tk.NORMAL)
        else:
            for num in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                if num in self.calc_buttons:
                    self.calc_buttons[num].config(state=tk.NORMAL)
    
    def calc_button_click(self, btn_text):
        current_display = self.calc_display_var.get()
        
        if btn_text == 'C':
            # Clear all
            self.calc_display = ""
            self.calc_display_var.set("0")
            self.calc_secondary_var.set("")
            self.calc_first_operand = None
            self.calc_current_operation = None
        
        elif btn_text == 'CE':
            # Clear entry
            self.calc_display = ""
            self.calc_display_var.set("0")
        
        elif btn_text == 'MC':
            # Memory clear
            self.calc_memory = 0
            self.update_memory_display()
        
        elif btn_text == 'MR':
            # Memory recall
            self.calc_display = str(self.calc_memory)
            self.calc_display_var.set(self.format_number(self.calc_memory))
            self.update_secondary_display(self.calc_memory)
        
        elif btn_text == 'MS':
            # Memory store
            try:
                value = self.parse_display_value()
                self.calc_memory = value
                self.update_memory_display()
            except:
                pass
        
        elif btn_text == 'M+':
            # Memory add
            try:
                value = self.parse_display_value()
                self.calc_memory += value
                self.update_memory_display()
            except:
                pass
        
        elif btn_text == 'M-':
            # Memory subtract
            try:
                value = self.parse_display_value()
                self.calc_memory -= value
                self.update_memory_display()
            except:
                pass
        
        elif btn_text in ['/', '*', '-', '+', '%', 'pow', 'AND', 'OR', 'XOR', 'NAND', 'NOR', '<<', '>>']:
            # Binary operations
            try:
                # Get current value
                if self.calc_display:
                    current_value = self.parse_display_value()
                else:
                    # Try to parse from display
                    try:
                        current_value = self.parse_from_formatted_display(current_display)
                    except:
                        current_value = 0
                
                # If we already have a pending operation, calculate it first
                if self.calc_first_operand is not None and self.calc_current_operation:
                    result = self.perform_operation(self.calc_first_operand, current_value, self.calc_current_operation)
                    self.calc_first_operand = result
                else:
                    self.calc_first_operand = current_value
                
                # Set new operation
                self.calc_current_operation = btn_text
                self.calc_display = ""
                self.calc_display_var.set(f"{self.format_number(self.calc_first_operand)} {btn_text}")
                self.update_secondary_display(self.calc_first_operand)
            except Exception as e:
                self.calc_display_var.set("ERROR")
                self.calc_secondary_var.set(str(e))
        
        elif btn_text == '=':
            # Calculate
            try:
                if self.calc_current_operation and self.calc_first_operand is not None:
                    if self.calc_display:
                        second_operand = self.parse_display_value()
                    else:
                        second_operand = 0
                    
                    result = self.perform_operation(self.calc_first_operand, second_operand, self.calc_current_operation)
                    
                    self.calc_display = str(result)
                    self.calc_display_var.set(self.format_number(result))
                    self.update_secondary_display(result)
                    self.calc_last_result = result
                    self.add_history(f"Calc: {self.format_number(self.calc_first_operand)} {self.calc_current_operation} {self.format_number(second_operand)} = {self.format_number(result)}")
                    
                    self.calc_first_operand = result
                    self.calc_current_operation = None
            except Exception as e:
                self.calc_display_var.set("ERROR")
                self.calc_secondary_var.set(str(e))
        
        elif btn_text == 'sqrt':
            # Square rootconvcalc1 (unary operation)
            try:
                if self.calc_display:
                    value = self.parse_display_value()
                else:
                    value = self.parse_from_formatted_display(current_display)
                    
                if value < 0:
                    raise ValueError("Cannot take sqrt of negative number")
                result = int(math.sqrt(value))
                self.calc_display = str(result)
                self.calc_display_var.set(self.format_number(result))
                self.update_secondary_display(result)
                self.add_history(f"Calc: sqrt({self.format_number(value)}) = {self.format_number(result)}")
            except Exception as e:
                self.calc_display_var.set("ERROR")
                self.calc_secondary_var.set(str(e))
        
        elif btn_text == 'ABS':
            # Absolute value
            try:
                if self.calc_display:
                    value = self.parse_display_value()
                else:
                    value = self.parse_from_formatted_display(current_display)
                    
                result = abs(value)
                self.calc_display = str(result)
                self.calc_display_var.set(self.format_number(result))
                self.update_secondary_display(result)
                self.add_history(f"Calc: abs({self.format_number(value)}) = {self.format_number(result)}")
            except Exception as e:
                self.calc_display_var.set("ERROR")
                self.calc_secondary_var.set(str(e))
        
        elif btn_text == 'NEG':
            # Negate
            try:
                if self.calc_display:
                    value = self.parse_display_value()
                else:
                    value = self.parse_from_formatted_display(current_display)
                    
                result = -value
                self.calc_display = str(result)
                self.calc_display_var.set(self.format_number(result))
                self.update_secondary_display(result)
            except Exception as e:
                self.calc_display_var.set("ERROR")
                self.calc_secondary_var.set(str(e))
        
        elif btn_text == 'NOT':
            # Bitwise NOT
            try:
                if self.calc_display:
                    value = self.parse_display_value()
                else:
                    value = self.parse_from_formatted_display(current_display)
                    
                # For NOT, we need to decide on bit width
                bit_width = max(value.bit_length(), 8)
                mask = (1 << bit_width) - 1
                result = (~value) & mask
                self.calc_display = str(result)
                self.calc_display_var.set(self.format_number(result))
                self.update_secondary_display(result)
                self.add_history(f"Calc: NOT {self.format_number(value)} = {self.format_number(result)}")
            except Exception as e:
                self.calc_display_var.set("ERROR")
                self.calc_secondary_var.set(str(e))
        
        elif btn_text == 'INV':
            # Inverse (1/x)
            try:
                if self.calc_display:
                    value = self.parse_display_value()
                else:
                    value = self.parse_from_formatted_display(current_display)
                    
                if value == 0:
                    raise ValueError("Division by zero")
                result = int(1 / value)
                self.calc_display = str(result)
                self.calc_display_var.set(self.format_number(result))
                self.update_secondary_display(result)
                self.add_history(f"Calc: 1/{self.format_number(value)} = {self.format_number(result)}")
            except Exception as e:
                self.calc_display_var.set("ERROR")
                self.calc_secondary_var.set(str(e))
        
        elif btn_text == '!':
            # Factorial
            try:
                if self.calc_display:
                    value = self.parse_display_value()
                else:
                    value = self.parse_from_formatted_display(current_display)
                    
                if value < 0:
                    raise ValueError("Factorial of negative number")
                if value > 20:
                    raise ValueError("Number too large for factorial")
                result = math.factorial(value)
                self.calc_display = str(result)
                self.calc_display_var.set(self.format_number(result))
                self.update_secondary_display(result)
                self.add_history(f"Calc: {value}! = {result}")
            except Exception as e:
                self.calc_display_var.set("ERROR")
                self.calc_secondary_var.set(str(e))
        
        elif btn_text in ['(', ')']:
            # Parentheses support (for future expansion)
            if current_display == "0" or current_display == "ERROR":
                self.calc_display = btn_text
            else:
                self.calc_display += btn_text
            self.calc_display_var.set(self.calc_display)
        
        else:
            # Append to display (numbers and hex digits)
            # Check if we need to start fresh
            if self.calc_first_operand is not None and not self.calc_display and self.calc_current_operation:
                # Starting to enter second operand
                self.calc_display = btn_text
            elif current_display == "0" or current_display == "ERROR":
                self.calc_display = btn_text
            else:
                # Continue building current number
                self.calc_display += btn_text
            
            self.calc_display_var.set(self.calc_display)
            
    def parse_from_formatted_display(self, display):
        """Parse a formatted display string (e.g., '5 +' -> 5)"""
        # Remove operation symbols from the end
        display = display.strip()
        for op in ['/', '*', '-', '+', '%', 'pow', 'AND', 'OR', 'XOR', 'NAND', 'NOR', '<<', '>>']:
            if display.endswith(' ' + op):
                display = display[:-len(op)-1].strip()
                break
        
        if not display or display == "0":
            return 0
            
        mode = self.calc_mode.get()
        
        try:
            if mode == "decimal":
                return int(display)
            elif mode == "binary":
                return int(display, 2)
            elif mode == "hexadecimal":
                return int(display, 16)
            elif mode == "octal":
                return int(display, 8)
        except:
            return 0
            
    def perform_operation(self, left, right, operation):
        """Perform the specified operation"""
        if operation == '+':
            return left + right
        elif operation == '-':
            return left - right
        elif operation == '*':
            return left * right
        elif operation == '/':
            if right == 0:
                raise ValueError("Division by zero")
            return int(left / right)
        elif operation == '%':
            if right == 0:
                raise ValueError("Modulo by zero")
            return left % right
        elif operation == 'pow':
            if right < 0:
                raise ValueError("Negative exponent not supported")
            if right > 100:
                raise ValueError("Exponent too large")
            return left ** right
        elif operation == 'AND':
            return left & right
        elif operation == 'OR':
            return left | right
        elif operation == 'XOR':
            return left ^ right
        elif operation == 'NAND':
            result = left & right
            bit_width = max(left.bit_length(), right.bit_length(), 8)
            mask = (1 << bit_width) - 1
            return (~result) & mask
        elif operation == 'NOR':
            result = left | right
            bit_width = max(left.bit_length(), right.bit_length(), 8)
            mask = (1 << bit_width) - 1
            return (~result) & mask
        elif operation == '<<':
            if right < 0 or right > 64:
                raise ValueError("Invalid shift amount")
            return left << right
        elif operation == '>>':
            if right < 0 or right > 64:
                raise ValueError("Invalid shift amount")
            return left >> right
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def parse_display_value(self):
        """Parse the current display value according to the selected mode"""
        display = self.calc_display.strip()
        if not display:
            return 0
        
        mode = self.calc_mode.get()
        
        # Handle negative numbers
        is_negative = display.startswith('-')
        if is_negative:
            display = display[1:]
        
        try:
            if mode == "decimal":
                value = int(display)
            elif mode == "binary":
                value = int(display, 2)
            elif mode == "hexadecimal":
                value = int(display, 16)
            elif mode == "octal":
                value = int(display, 8)
            
            return -value if is_negative else value
        except ValueError:
            return 0
    
    def format_number(self, num):
        """Format number according to current mode"""
        mode = self.calc_mode.get()
        
        if mode == "decimal":
            return str(num)
        elif mode == "binary":
            return bin(num)[2:] if num >= 0 else '-' + bin(num)[3:]
        elif mode == "hexadecimal":
            return hex(num)[2:].upper() if num >= 0 else '-' + hex(num)[3:].upper()
        elif mode == "octal":
            return oct(num)[2:] if num >= 0 else '-' + oct(num)[3:]
    
    def update_secondary_display(self, value):
        """Show value in all number systems"""
        try:
            if value >= 0:
                secondary = f"DEC:{value} BIN:{bin(value)[2:]} HEX:{hex(value)[2:].upper()} OCT:{oct(value)[2:]}"
            else:
                secondary = f"DEC:{value} (negative number)"
            self.calc_secondary_var.set(secondary)
        except:
            self.calc_secondary_var.set("")
    
    def update_memory_display(self):
        """Update memory indicator"""
        if self.calc_memory != 0:
            mem_text = f"M: {self.calc_memory}"
            current = self.calc_secondary_var.get()
            if not current.startswith("M:"):
                self.calc_secondary_var.set(mem_text)
    
    # ==================== ANALYSIS TAB ====================
    def create_analysis_tab(self):
        tab = tk.Frame(self.content_frame, bg=self.bg_color)
        self.tabs["analyze"] = tab
        
        history_label = tk.Label(tab, text="Conversion History & Statistics:", 
                                bg=self.bg_color, fg=self.text_fg, font=("MS Sans Serif", 9, "bold"))
        history_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        self.analysis_text = scrolledtext.ScrolledText(tab, height=20, width=80,
                                                      bg=self.text_bg, fg=self.text_fg,
                                                      font=("Courier New", 8),
                                                      wrap=tk.WORD, relief=tk.SUNKEN,
                                                      borderwidth=1)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.analysis_text.config(state=tk.DISABLED)
        
        btn_frame = tk.Frame(tab, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.create_button(btn_frame, "Refresh", self.update_analysis).pack(side=tk.LEFT, padx=2)
        self.create_button(btn_frame, "Clear History", self.clear_history).pack(side=tk.LEFT, padx=2)
        self.create_button(btn_frame, "Export History", self.export_history).pack(side=tk.LEFT, padx=2)
    
    def add_history(self, entry):
        self.history.append(entry)
        if len(self.history) > 100:
            self.history.pop(0)
        if self.current_tab == "analyze":
            self.update_analysis()
    
    def update_analysis(self):
        output = "[CONVERSION HISTORY & STATISTICS]\n" + "=" * 70 + "\n\n"
        
        if not self.history:
            output += "No conversions yet. Start using the tools to build your history!\n"
        else:
            output += f"Total conversions performed: {len(self.history)}\n\n"
            
            # Statistics by type
            number_count = sum(1 for h in self.history if h.startswith("Number:"))
            text_count = sum(1 for h in self.history if h.startswith("Text:"))
            hash_count = sum(1 for h in self.history if h.startswith("Hash:"))
            calc_count = sum(1 for h in self.history if h.startswith("Calc:"))
            
            output += "Breakdown by tool:\n"
            output += f"  Number conversions: {number_count}\n"
            output += f"  Text operations: {text_count}\n"
            output += f"  Hash/Encode operations: {hash_count}\n"
            output += f"  Calculator operations: {calc_count}\n\n"
            
            output += "-" * 70 + "\n"
            output += "Recent entries (last 40):\n"
            output += "-" * 70 + "\n"
            for i, entry in enumerate(self.history[-40:], 1):
                output += f"{i:3d}. {entry}\n"
        
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, output)
        self.analysis_text.config(state=tk.DISABLED)
    
    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all history?"):
            self.history = []
            self.update_analysis()
    
    def export_history(self):
        """Export history to a text file"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export History"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("UNIVERSAL CONVERTER SUITE - HISTORY EXPORT\n")
                    f.write("=" * 70 + "\n\n")
                    f.write(f"Total entries: {len(self.history)}\n")
                    f.write(f"Export date: {self.get_current_date()}\n\n")
                    f.write("-" * 70 + "\n")
                    for i, entry in enumerate(self.history, 1):
                        f.write(f"{i}. {entry}\n")
                messagebox.showinfo("Export Successful", f"History exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export history:\n{str(e)}")
    
    def get_current_date(self):
        """Get current date/time as string"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    rootconvcalc1 = tk.Tk()
    app = RetroConverterEcosystem(rootconvcalc1)
    rootconvcalc1.mainloop()