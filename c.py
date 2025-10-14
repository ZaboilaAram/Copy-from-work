import tkinter as tk
from tkinter import messagebox

class ProgrammerCalculator:
    def __init__(self, rootprgrmcalc2):
        self.rootprgrmcalc2 = rootprgrmcalc2
        self.rootprgrmcalc2.title("Programmer Calculator")
        self.rootprgrmcalc2.configure(bg='#c0c0c0')
        self.rootprgrmcalc2.resizable(False, False)
        
        # Variables
        self.current_value = "0"
        self.previous_value = ""
        self.operation = ""
        self.current_base = "DEC"
        self.bit_width = 32
        self.shift_mode = "DEC"  # DEC or BIN
        self.new_number = True
        self.buttons_dict = {}
        self.in_shift_operation = False
        
        # Color scheme for button states
        self.colors = {
            'enabled': '#4A90E2',   # Light navy blue
            'disabled': '#c0c0c0'   # Gray (same as window bg)
        }
        
        # Create main frame with 3D border
        main_frame = tk.Frame(rootprgrmcalc2, bg='#c0c0c0', relief='raised', bd=2)
        main_frame.pack(padx=5, pady=5)
        
        # Display frame
        display_frame = tk.Frame(main_frame, bg='#c0c0c0', relief='sunken', bd=2)
        display_frame.pack(padx=5, pady=5, fill='x')
        
        # Operation display
        self.operation_display = tk.Entry(display_frame, font=('MS Sans Serif', 10),
                                         justify='right', bg='white', fg='#666666',
                                         relief='flat', bd=0, state='readonly')
        self.operation_display.pack(ipady=4, padx=2, pady=1, fill='x')
        
        # Main display
        self.display = tk.Entry(display_frame, font=('MS Sans Serif', 16, 'bold'),
                               justify='right', bg='white', fg='black',
                               relief='flat', bd=0, state='readonly')
        self.display.pack(ipady=8, padx=2, pady=2, fill='x')
        self.update_display()
        
        # Base and Bit selection frame
        options_frame = tk.Frame(main_frame, bg='#c0c0c0')
        options_frame.pack(padx=5, pady=5, fill='x')
        
        # Left side - Base selection
        base_frame = tk.Frame(options_frame, bg='#c0c0c0')
        base_frame.pack(side='left', padx=10)
        
        tk.Label(base_frame, text="Base:", bg='#c0c0c0', 
                font=('MS Sans Serif', 8)).grid(row=0, column=0, sticky='w', pady=2)
        
        self.base_var = tk.StringVar(value="DEC")
        for i, base in enumerate(["HEX", "DEC", "OCT", "BIN"]):
            rb = tk.Radiobutton(base_frame, text=base, variable=self.base_var,
                               value=base, bg='#c0c0c0', 
                               font=('MS Sans Serif', 8),
                               command=self.change_base,
                               activebackground='#c0c0c0')
            rb.grid(row=i+1, column=0, sticky='w', pady=1)
        
        # Right side - Bit width selection
        bit_frame = tk.Frame(options_frame, bg='#c0c0c0')
        bit_frame.pack(side='right', padx=10)
        
        tk.Label(bit_frame, text="Bits:", bg='#c0c0c0', 
                font=('MS Sans Serif', 8)).grid(row=0, column=0, sticky='w', pady=2)
        
        self.bit_var = tk.StringVar(value="32")
        for i, bits in enumerate(["8", "16", "32", "64"]):
            rb = tk.Radiobutton(bit_frame, text=bits, variable=self.bit_var,
                               value=bits, bg='#c0c0c0', 
                               font=('MS Sans Serif', 8),
                               command=self.change_bit_width,
                               activebackground='#c0c0c0')
            rb.grid(row=i+1, column=0, sticky='w', pady=1)
        
        # Shift mode selection frame - initially hidden
        self.shift_frame = tk.Frame(main_frame, bg='#c0c0c0')
        
        tk.Label(self.shift_frame, text="Shift Mode:", bg='#c0c0c0', 
                font=('MS Sans Serif', 8)).pack(side='left', padx=5)
        
        self.shift_var = tk.StringVar(value="DEC")
        for mode in ["DEC", "BIN"]:
            rb = tk.Radiobutton(self.shift_frame, text=mode, variable=self.shift_var,
                               value=mode, bg='#c0c0c0', 
                               font=('MS Sans Serif', 8),
                               command=self.change_shift_mode,
                               activebackground='#c0c0c0')
            rb.pack(side='left', padx=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#c0c0c0')
        buttons_frame.pack(padx=5, pady=5)
        
        # Button layout with corrected groups
        # any: 0-1 (valide în toate bazele)
        # oct_plus: 2-7 (valide în OCT și superior)
        # dec_plus: 8-9 (valide doar în DEC și HEX)
        buttons = [
            [('A', 'hex'), ('B', 'hex'), ('C', 'hex'), ('D', 'hex'), ('E', 'hex'), ('F', 'hex')],
            [('7', 'oct_plus'), ('8', 'dec_plus'), ('9', 'dec_plus'), ('/', 'operator'), ('MOD', 'bitwise'), ('AND', 'bitwise')],
            [('4', 'oct_plus'), ('5', 'oct_plus'), ('6', 'oct_plus'), ('*', 'operator'), ('XOR', 'bitwise'), ('OR', 'bitwise')],
            [('1', 'any'), ('2', 'oct_plus'), ('3', 'oct_plus'), ('-', 'operator'), ('<<', 'bitwise'), ('>>', 'bitwise')],
            [('0', 'any'), ('+', 'operator'), ('=', 'operator'), ('NOT', 'bitwise'), ('~', 'bitwise'), ('^', 'bitwise')],
            [('CLR', 'operator'), ('DEL', 'operator'), ('~', 'bitwise'), ('^', 'bitwise'), ('NAND', 'bitwise'), ('CE', 'operator')]
        ]
        
        for i, row in enumerate(buttons):
            for j, (btn_text, btn_group) in enumerate(row):
                btn = tk.Button(buttons_frame, text=btn_text,
                              width=6, height=2,
                              font=('MS Sans Serif', 9),
                              bg=self.colors['enabled'], fg='white',
                              relief='raised', bd=2,
                              activebackground=self.colors['enabled'],
                              command=lambda x=btn_text: self.button_click(x))
                btn.grid(row=i, column=j, padx=2, pady=2, sticky='nsew')
                self.buttons_dict[(i, j)] = (btn, btn_text, btn_group)
        
        # Initial button state update
        self.update_button_states()
    
    def show_shift_mode(self, show=True):
        """Show or hide shift mode selection"""
        if show:
            self.shift_frame.pack(padx=5, pady=5, fill='x')
        else:
            self.shift_frame.pack_forget()
    
    def update_button_states(self):
        """Enable/disable buttons based on current base and shift mode"""
        valid_groups = self.get_valid_groups()
        
        for (row, col), (btn, text, group) in self.buttons_dict.items():
            if group in valid_groups or group == 'operator' or group == 'bitwise':
                btn.config(state='normal', bg=self.colors['enabled'], fg='white')
            else:
                btn.config(state='disabled', bg=self.colors['disabled'], fg='gray')
    
    def get_valid_groups(self):
        """Return valid button groups for current base and shift mode"""
        # If in shift operation with BIN mode, allow only binary digits (0-1)
        if self.in_shift_operation and self.shift_mode == "BIN":
            return ['any']  # 0-1
        
        # If in shift operation with DEC mode, allow decimal digits (0-9)
        if self.in_shift_operation and self.shift_mode == "DEC":
            return ['any', 'oct_plus', 'dec_plus']  # 0-9
        
        # Normal mode - base selection
        if self.current_base == "HEX":
            return ['hex', 'dec_plus', 'oct_plus', 'any']
        elif self.current_base == "DEC":
            return ['dec_plus', 'oct_plus', 'any']
        elif self.current_base == "OCT":
            return ['oct_plus', 'any']
        elif self.current_base == "BIN":
            return ['any']
        return []
    
    def change_shift_mode(self):
        """Change shift mode (DEC or BIN)"""
        self.shift_mode = self.shift_var.get()
        self.update_button_states()
    
    def update_display(self):
        self.display.configure(state='normal')
        self.display.delete(0, tk.END)
        self.display.insert(0, self.current_value)
        self.display.configure(state='readonly')
        
        self.operation_display.configure(state='normal')
        self.operation_display.delete(0, tk.END)
        if self.previous_value and self.operation:
            op_text = f"{self.previous_value} {self.operation}"
            self.operation_display.insert(0, op_text)
        self.operation_display.configure(state='readonly')
    
    def change_bit_width(self):
        self.bit_width = int(self.bit_var.get())
    
    def change_base(self):
        try:
            if self.current_value == "0":
                self.current_base = self.base_var.get()
                self.update_button_states()
                return
            
            # Convert current value to decimal first
            if self.current_base == "HEX":
                dec_val = int(self.current_value, 16)
            elif self.current_base == "DEC":
                dec_val = int(self.current_value)
            elif self.current_base == "OCT":
                dec_val = int(self.current_value, 8)
            elif self.current_base == "BIN":
                dec_val = int(self.current_value, 2)
            
            # Convert to new base
            new_base = self.base_var.get()
            self.current_value = self.convert_to_base(dec_val, new_base)
            self.current_base = new_base
            self.update_display()
            self.update_button_states()
        except:
            messagebox.showerror("Error", "Invalid value for selected base")
            self.current_value = "0"
            self.current_base = self.base_var.get()
            self.update_display()
            self.update_button_states()
    
    def convert_to_base(self, value, base):
        if base == "HEX":
            return hex(value)[2:].upper()
        elif base == "DEC":
            return str(value)
        elif base == "OCT":
            return oct(value)[2:]
        elif base == "BIN":
            return bin(value)[2:]
    
    def to_decimal(self, value):
        try:
            if self.current_base == "HEX":
                return int(value, 16)
            elif self.current_base == "DEC":
                return int(value)
            elif self.current_base == "OCT":
                return int(value, 8)
            elif self.current_base == "BIN":
                return int(value, 2)
        except:
            return 0
    
    def from_decimal(self, value):
        if value < 0:
            if self.bit_width == 8:
                value = value & 0xFF
            elif self.bit_width == 16:
                value = value & 0xFFFF
            elif self.bit_width == 32:
                value = value & 0xFFFFFFFF
            elif self.bit_width == 64:
                value = value & 0xFFFFFFFFFFFFFFFF
        
        return self.convert_to_base(value, self.current_base)
    
    def apply_bit_mask(self, value):
        mask = (1 << self.bit_width) - 1
        return value & mask
    
    def is_valid_digit(self, key):
        """Check if digit is valid for current base or shift mode"""
        try:
            digit = int(key)
            
            # In shift operation with BIN mode - only 0, 1
            if self.in_shift_operation and self.shift_mode == "BIN":
                return digit <= 1
            
            # In shift operation with DEC mode - 0-9
            if self.in_shift_operation and self.shift_mode == "DEC":
                return digit <= 9
            
            # Normal operation
            if self.current_base == "BIN":
                return digit <= 1
            elif self.current_base == "OCT":
                return digit <= 7
            return True
        except:
            return False
    
    def button_click(self, key):
        # Number input
        if key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            if not self.is_valid_digit(key):
                mode_info = f"{self.shift_mode} mode" if self.in_shift_operation else f"{self.current_base} base"
                messagebox.showwarning("Invalid", f"Invalid digit '{key}' for {mode_info}")
                return
            
            if self.new_number:
                self.current_value = key
                self.new_number = False
            else:
                if self.current_value == "0":
                    self.current_value = key
                else:
                    self.current_value += key
            self.update_display()
        
        # Hex letters
        elif key in ['A', 'B', 'C', 'D', 'E', 'F']:
            if self.current_base != "HEX":
                messagebox.showwarning("Invalid", "Hex digits only in HEX mode")
                return
            
            if self.new_number:
                self.current_value = key
                self.new_number = False
            else:
                if self.current_value == "0":
                    self.current_value = key
                else:
                    self.current_value += key
            self.update_display()
        
        # Clear current
        elif key == 'CLR':
            self.current_value = "0"
            self.new_number = True
            self.in_shift_operation = False
            self.show_shift_mode(False)
            self.update_button_states()
            self.update_display()
        
        # Clear all
        elif key == 'CE':
            self.current_value = "0"
            self.previous_value = ""
            self.operation = ""
            self.new_number = True
            self.in_shift_operation = False
            self.show_shift_mode(False)
            self.update_button_states()
            self.update_display()
        
        # Backspace
        elif key == 'DEL':
            if len(self.current_value) > 1:
                self.current_value = self.current_value[:-1]
            else:
                self.current_value = "0"
            self.update_display()
        
        # Parentheses handling
        elif key in ['(', ')']:
            if self.new_number:
                self.current_value = key
                self.new_number = False
            else:
                self.current_value += key
            self.update_display()
        
        # Binary operations
        elif key in ['+', '-', '*', '/', 'MOD', 'AND', 'OR', 'XOR', '<<', '>>']:
            if self.operation and self.previous_value and not self.new_number:
                self.calculate()
            
            self.previous_value = self.current_value
            self.operation = key
            self.new_number = True
            
            # Set shift operation flag and show/hide shift mode selection
            if key in ['<<', '>>']:
                self.in_shift_operation = True
                self.show_shift_mode(True)
            else:
                self.in_shift_operation = False
                self.show_shift_mode(False)
            
            self.update_display()
            self.update_button_states()
        
        # Unary bitwise operations
        elif key in ['NOT', '~', '^']:
            try:
                dec_val = self.to_decimal(self.current_value)
                
                if key == 'NOT':
                    result = ~dec_val & ((1 << self.bit_width) - 1)
                elif key == '~':
                    result = ~dec_val & ((1 << self.bit_width) - 1)
                elif key == '^':
                    result = dec_val ^ ((1 << self.bit_width) - 1)
                
                self.current_value = self.from_decimal(result)
                self.new_number = True
                self.update_display()
            except:
                messagebox.showerror("Error", "Invalid operation")
        
        # NAND operation
        elif key == 'NAND':
            if self.operation and self.previous_value and not self.new_number:
                self.calculate()
            
            self.previous_value = self.current_value
            self.operation = 'NAND'
            self.new_number = True
            self.in_shift_operation = False
            self.show_shift_mode(False)
            self.update_display()
            self.update_button_states()
        
        # Equals
        elif key == '=':
            if self.previous_value and self.operation:
                self.calculate()
            self.new_number = True
            self.in_shift_operation = False
            self.show_shift_mode(False)
            self.update_button_states()
    
    def calculate(self):
        try:
            val1 = self.to_decimal(self.previous_value)
            
            # For shift operations, interpret shift amount according to shift mode
            if self.operation in ['<<', '>>']:
                if self.shift_mode == "BIN":
                    val2 = int(self.current_value, 2)
                else:  # DEC mode
                    val2 = int(self.current_value)
            else:
                val2 = self.to_decimal(self.current_value)
            
            result = 0
            
            if self.operation == '+':
                result = val1 + val2
            elif self.operation == '-':
                result = val1 - val2
            elif self.operation == '*':
                result = val1 * val2
            elif self.operation == '/':
                if val2 == 0:
                    messagebox.showerror("Error", "Division by zero")
                    return
                result = val1 // val2
            elif self.operation == 'MOD':
                if val2 == 0:
                    messagebox.showerror("Error", "Modulo by zero")
                    return
                result = val1 % val2
            elif self.operation == 'AND':
                result = val1 & val2
            elif self.operation == 'OR':
                result = val1 | val2
            elif self.operation == 'XOR':
                result = val1 ^ val2
            elif self.operation == '<<':
                if val2 < 0:
                    messagebox.showerror("Error", "Shift amount must be non-negative")
                    return
                result = (val1 << val2) & ((1 << self.bit_width) - 1)
            elif self.operation == '>>':
                if val2 < 0:
                    messagebox.showerror("Error", "Shift amount must be non-negative")
                    return
                result = val1 >> val2
            elif self.operation == 'NAND':
                result = ~(val1 & val2) & ((1 << self.bit_width) - 1)
            
            result = self.apply_bit_mask(result)
            self.current_value = self.from_decimal(result)
            self.previous_value = ""
            self.operation = ""
            self.in_shift_operation = False
            self.update_display()
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")
            self.current_value = "0"
            self.in_shift_operation = False
            self.update_display()
        finally:
            self.update_button_states()

if __name__ == "__main__":
    rootprgrmcalc2 = tk.Tk()
    app = ProgrammerCalculator(rootprgrmcalc2)
    rootprgrmcalc2.mainloop()