import tkinter as tk
from tkinter import ttk
import platform
import subprocess
import os
import sys

class DeviceManagerW95:
    def __init__(self, root):
        self.root = root
        self.root.title("Device Manager")
        self.root.geometry("600x500")
        self.root.configure(bg='#c0c0c0')
        
        # Initialize variables
        self.selected_device = None
        self.selected_item_frame = None
        
        # Windows 95 style configuration
        self.setup_w95_style()
        
        # Create menu bar
        self.create_menu()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        self.create_content_area()
        
        # Populate device tree
        self.populate_devices()
        
    def setup_w95_style(self):
        # Configure default colors and fonts for W95 look
        self.bg_color = '#c0c0c0'
        self.button_color = '#c0c0c0'
        self.text_color = '#000000'
        self.font = ('MS Sans Serif', 8)
        
    def create_menu(self):
        menubar = tk.Menu(self.root, bg=self.bg_color, font=self.font)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, font=self.font)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh")
        file_menu.add_command(label="Print...")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, font=self.font)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find...")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, font=self.font)
        menubar.add_cascade(label="View", menu=view_menu)
        self.view_mode = tk.StringVar(value="by_type")
        view_menu.add_radiobutton(label="Devices by type", variable=self.view_mode, 
                                value="by_type", command=self.change_view)
        view_menu.add_radiobutton(label="Devices by connection", variable=self.view_mode, 
                                value="by_connection", command=self.change_view)
        view_menu.add_radiobutton(label="Resources by type", variable=self.view_mode, 
                                value="resources_type", command=self.change_view)
        view_menu.add_radiobutton(label="Resources by connection", variable=self.view_mode, 
                                value="resources_connection", command=self.change_view)
        view_menu.add_separator()
        self.show_hidden = tk.BooleanVar(value=False)
        view_menu.add_checkbutton(label="Show hidden devices", variable=self.show_hidden, 
                                command=self.toggle_hidden_devices)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.bg_color, font=self.font)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Help Topics")
        help_menu.add_separator()
        help_menu.add_command(label="About Device Manager")
        
    def create_toolbar(self):
        toolbar_frame = tk.Frame(self.root, bg=self.bg_color, relief='raised', bd=1)
        toolbar_frame.pack(fill='x', padx=2, pady=1)
        
        # Toolbar buttons with W95 style
        buttons = [
            ("Properties", self.show_properties),
            ("Refresh", self.refresh_devices),
            ("Remove", self.remove_device),
            ("Print", self.print_devices)
        ]
        
        for text, command in buttons:
            btn = tk.Button(toolbar_frame, text=text, command=command,
                          bg=self.button_color, font=self.font,
                          relief='raised', bd=2, padx=8, pady=2)
            btn.pack(side='left', padx=1)
            
    def create_content_area(self):
        # Main frame with sunken border
        main_frame = tk.Frame(self.root, bg='white', relief='sunken', bd=2)
        main_frame.pack(fill='both', expand=True, padx=4, pady=4)
        
        # Create treeview-like display using Text widget and frames
        self.tree_frame = tk.Frame(main_frame, bg='white')
        self.tree_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Canvas for custom tree display
        self.canvas = tk.Canvas(self.tree_frame, bg='white', 
                               yscrollcommand=scrollbar.set,
                               highlightthickness=0)
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        # Frame inside canvas for tree items
        self.tree_content = tk.Frame(self.canvas, bg='white')
        self.canvas_window = self.canvas.create_window(0, 0, anchor='nw', window=self.tree_content)
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.tree_content.bind('<Configure>', self.on_frame_configure)
        
        # Bind mouse wheel scrolling
        self.canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        self.canvas.bind('<Button-4>', self.on_mouse_wheel)  # Linux
        self.canvas.bind('<Button-5>', self.on_mouse_wheel)  # Linux
        
        # Make canvas focusable for mouse wheel events
        self.canvas.focus_set()
        
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        
    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        
    def on_mouse_wheel(self, event):
        # Handle mouse wheel scrolling
        if event.num == 4 or event.delta > 0:  # Scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:  # Scroll down
            self.canvas.yview_scroll(1, "units")
        
    def create_tree_item(self, parent, text, level=0, expanded=True, has_children=False, is_hidden=False):
        # Skip hidden devices if not showing them
        if is_hidden and not self.show_hidden.get():
            return None
            
        item_frame = tk.Frame(parent, bg='white')
        item_frame.pack(fill='x', pady=1)
        
        # Store original text color for later restoration
        text_color = '#808080' if is_hidden else '#000000'
        
        # Indentation
        indent_frame = tk.Frame(item_frame, bg='white', width=level*20)
        indent_frame.pack(side='left')
        
        # Expand/collapse button for items with children
        if has_children:
            expand_btn = tk.Button(item_frame, text='-' if expanded else '+',
                                 width=1, height=1, font=('MS Sans Serif', 6),
                                 bg='white', relief='flat', bd=0)
            expand_btn.pack(side='left')
        else:
            spacer = tk.Frame(item_frame, bg='white', width=12)
            spacer.pack(side='left')
            
        # Icon placeholder (small colored rectangle)
        icon_color = self.get_device_icon_color(text)
        icon = tk.Frame(item_frame, bg=icon_color, width=16, height=16)
        icon.pack(side='left', padx=(2, 4))
        
        # Device name
        name_label = tk.Label(item_frame, text=text, bg='white', fg=text_color,
                            font=self.font, anchor='w')
        name_label.pack(side='left')
        
        # Store the original color in the label for later restoration
        name_label.original_color = text_color
        
        # Bind click events
        for widget in [item_frame, name_label]:
            widget.bind('<Button-1>', lambda e, device=text, frame=item_frame: self.select_device(device, frame))
            widget.bind('<Double-Button-1>', lambda e, device=text: self.show_properties())
            # Bind mouse wheel to canvas when hovering over items
            widget.bind('<MouseWheel>', self.on_mouse_wheel)
            widget.bind('<Button-4>', self.on_mouse_wheel)
            widget.bind('<Button-5>', self.on_mouse_wheel)
            
        return item_frame
        
    def get_device_icon_color(self, device_name):
        # Simple color coding for different device types
        if 'Display' in device_name or 'Graphics' in device_name:
            return '#0000ff'  # Blue for display
        elif 'Audio' in device_name or 'Sound' in device_name:
            return '#ff0000'  # Red for audio
        elif 'Network' in device_name or 'Ethernet' in device_name:
            return '#00ff00'  # Green for network
        elif 'USB' in device_name:
            return '#ffff00'  # Yellow for USB
        elif 'Disk' in device_name or 'Storage' in device_name:
            return '#ff00ff'  # Magenta for storage
        else:
            return '#808080'  # Gray for other devices
            
    def get_system_devices(self):
        devices_by_type = {
            'Computer': [platform.node() or 'Local Computer'],
            'Disk drives': ['Local Disk (C:)', 'CD-ROM Drive (D:)', 'Floppy Disk (A:)'],
            'Display adapters': ['Standard VGA Graphics Adapter', 'Generic PnP Monitor'],
            'Floppy disk controllers': ['Standard Floppy Disk Controller'],
            'Hard disk controllers': ['Primary IDE Controller', 'Secondary IDE Controller'],
            'Keyboard': ['Standard 101/102-Key or Microsoft Natural PS/2 Keyboard'],
            'Modem': [],
            'Monitor': ['Generic PnP Monitor', 'Default Monitor'],
            'Mouse': ['Microsoft PS/2 Mouse'],
            'Network adapters': ['Ethernet Controller', 'Dial-Up Adapter'],
            'Ports (COM & LPT)': ['Communications Port (COM1)', 'Communications Port (COM2)', 'Printer Port (LPT1)'],
            'SCSI controllers': [],
            'Sound, video and game controllers': ['Audio Device on High Definition Audio Bus', 'Game Port for Creative'],
            'System devices': ['ACPI Power Button', 'System Timer', 'Programmable Interrupt Controller', 'DMA Controller', 'System Speaker'],
            'Universal Serial Bus controllers': ['USB Root Hub', 'USB Composite Device']
        }
        
        devices_by_connection = {
            'Computer': [platform.node() or 'Local Computer'],
            'ISA bus': ['System Timer', 'Programmable Interrupt Controller', 'DMA Controller', 'System Speaker'],
            'PCI bus': ['Standard VGA Graphics Adapter', 'Audio Device on High Definition Audio Bus', 'Ethernet Controller'],
            'USB Root Hub': ['USB Composite Device', 'USB Mouse'],
            'IDE/ATA': ['Local Disk (C:)', 'CD-ROM Drive (D:)'],
            'Floppy': ['Floppy Disk (A:)'],
            'PS/2': ['Standard PS/2 Keyboard', 'Microsoft PS/2 Mouse']
        }
        
        resources_by_type = {
            'Computer': [platform.node() or 'Local Computer'],
            'Direct memory access (DMA)': ['DMA 00: System Timer', 'DMA 04: Standard Floppy Disk Controller'],
            'Input/output (I/O)': ['03F8-03FF: Communications Port (COM1)', '02F8-02FF: Communications Port (COM2)', '0378-037F: Printer Port (LPT1)'],
            'Interrupt request (IRQ)': ['IRQ 00: System Timer', 'IRQ 01: Standard PS/2 Keyboard', 'IRQ 06: Standard Floppy Disk Controller', 'IRQ 12: Microsoft PS/2 Mouse'],
            'Memory': ['A0000-BFFFF: VGA Graphics Adapter', 'F0000-FFFFF: System BIOS']
        }
        
        resources_by_connection = {
            'Computer': [platform.node() or 'Local Computer'],
            'ISA bus': ['IRQ 00: System Timer', 'IRQ 01: Standard PS/2 Keyboard', 'DMA 00: System Timer'],
            'PCI bus': ['IRQ 11: Audio Device', 'IRQ 10: Ethernet Controller', 'A0000-BFFFF: VGA Graphics'],
            'System board': ['F0000-FFFFF: System BIOS', 'IRQ 13: Math Coprocessor']
        }
        
        hidden_devices = ['Legacy Device', 'Unknown Device', 'Disabled Network Adapter']
        
        if self.view_mode.get() == "by_type":
            return devices_by_type, hidden_devices
        elif self.view_mode.get() == "by_connection":
            return devices_by_connection, hidden_devices
        elif self.view_mode.get() == "resources_type":
            return resources_by_type, []
        else:  # resources_connection
            return resources_by_connection, []
        
    def get_windows_devices(self):
        devices = {}
        try:
            # Try to get some real Windows device info
            import wmi
            c = wmi.WMI()
            
            # This would work with wmi module, but we're avoiding dependencies
            # So we'll use generic info instead
        except:
            pass
            
        # Generic Windows-like devices
        return {
            'Disk drives': ['Generic Hard Disk', 'CD-ROM Drive'],
            'Display adapters': ['Standard VGA Graphics Adapter', 'Generic PnP Monitor'],
            'Keyboard': ['Standard 101/102-Key or Microsoft Natural PS/2 Keyboard'],
            'Mouse': ['Microsoft PS/2 Mouse'],
            'Network adapters': ['Ethernet Controller', 'Wireless Network Adapter'],
            'Sound, video and game controllers': ['Audio Device on High Definition Audio Bus'],
            'System devices': ['ACPI Power Button', 'System Timer', 'Programmable Interrupt Controller'],
            'Universal Serial Bus controllers': ['USB Root Hub', 'USB Composite Device']
        }
        
    def get_generic_devices(self):
        # Generic device list that works on any system
        return {
            'Disk drives': ['Local Disk (C:)', 'CD-ROM Drive (D:)'],
            'Display adapters': ['Standard VGA Graphics Adapter'],
            'Keyboard': ['Standard PS/2 Keyboard'],
            'Mouse': ['PS/2 Compatible Mouse'],
            'Network adapters': ['Network Adapter'],
            'Sound, video and game controllers': ['Audio Device'],
            'System devices': ['System Timer', 'Programmable Interrupt Controller', 'DMA Controller'],
            'Universal Serial Bus controllers': ['USB Root Hub']
        }
        
    def populate_devices(self):
        # Clear existing items
        for widget in self.tree_content.winfo_children():
            widget.destroy()
            
        # Clear selection
        self.selected_device = None
        self.selected_item_frame = None
            
        devices, hidden_devices = self.get_system_devices()
        
        # Computer root node
        computer_frame = self.create_tree_item(self.tree_content, 
                                             devices['Computer'][0], 
                                             level=0, has_children=True)
        
        # Device categories
        for category, device_list in devices.items():
            if category == 'Computer' or not device_list:
                continue
                
            # Category header
            category_frame = self.create_tree_item(self.tree_content, 
                                                 category, 
                                                 level=1, has_children=True)
            
            # Individual devices
            for device in device_list:
                is_hidden = device in hidden_devices
                device_frame = self.create_tree_item(self.tree_content, 
                                                   device, 
                                                   level=2, has_children=False,
                                                   is_hidden=is_hidden)
                                                   
        # Add hidden devices if showing them
        if self.show_hidden.get() and hidden_devices:
            for hidden_device in hidden_devices:
                device_frame = self.create_tree_item(self.tree_content, 
                                                   hidden_device, 
                                                   level=2, has_children=False,
                                                   is_hidden=True)
    def select_device(self, device, frame):
        # Clear previous selection
        if self.selected_item_frame:
            self.selected_item_frame.configure(bg='white')
            for child in self.selected_item_frame.winfo_children():
                if isinstance(child, tk.Label) and hasattr(child, 'original_color'):
                    # Restore original text color
                    child.configure(bg='white', fg=child.original_color)
                elif isinstance(child, tk.Frame) and child.winfo_width() < 50:  # Icon frame
                    pass  # Keep icon color
                else:
                    child.configure(bg='white')
        
        # Highlight new selection with Windows 95 selection color
        self.selected_device = device
        self.selected_item_frame = frame
        frame.configure(bg='#0000ff')  # Windows 95 selection blue
        
        for child in frame.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg='#0000ff', fg='white')
            elif isinstance(child, tk.Frame) and child.winfo_width() < 50:  # Icon frame
                pass  # Keep icon color
            else:
                try:
                    child.configure(bg='#0000ff')
                except:
                    pass
        
    def change_view(self):
        self.populate_devices()
        
    def toggle_hidden_devices(self):
        self.populate_devices()
        
    def show_properties(self):
        device_name = self.selected_device if self.selected_device else "Unknown Device"
        
        # Create properties dialog
        prop_window = tk.Toplevel(self.root)
        prop_window.title(f"{device_name} Properties")
        prop_window.geometry("450x350")
        prop_window.configure(bg=self.bg_color)
        prop_window.transient(self.root)
        prop_window.grab_set()
        prop_window.resizable(False, False)
        
        # Create notebook-style tabs
        tab_frame = tk.Frame(prop_window, bg=self.bg_color)
        tab_frame.pack(fill='x', padx=5, pady=5)
        
        # Tab buttons
        general_tab = tk.Button(tab_frame, text="General", bg=self.button_color, 
                               font=self.font, relief='raised', bd=2, padx=15)
        general_tab.pack(side='left')
        
        driver_tab = tk.Button(tab_frame, text="Driver", bg=self.button_color, 
                              font=self.font, relief='sunken', bd=1, padx=15)
        driver_tab.pack(side='left')
        
        resources_tab = tk.Button(tab_frame, text="Resources", bg=self.button_color, 
                                 font=self.font, relief='sunken', bd=1, padx=15)
        resources_tab.pack(side='left')
        
        # Properties content
        prop_frame = tk.Frame(prop_window, bg='white', relief='sunken', bd=2)
        prop_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Device icon and name
        header_frame = tk.Frame(prop_frame, bg='white')
        header_frame.pack(fill='x', pady=10)
        
        icon_color = self.get_device_icon_color(device_name)
        icon = tk.Frame(header_frame, bg=icon_color, width=32, height=32)
        icon.pack(side='left', padx=10)
        
        tk.Label(header_frame, text=device_name, 
                font=('MS Sans Serif', 10, 'bold'), bg='white').pack(side='left', padx=10)
        
        # Device information
        info_frame = tk.Frame(prop_frame, bg='white')
        info_frame.pack(fill='both', expand=True, padx=10)
        
        # Device type
        tk.Label(info_frame, text="Device type:", 
                font=self.font, bg='white', anchor='w').pack(fill='x', pady=2)
        device_type = self.get_device_type(device_name)
        tk.Label(info_frame, text=f"    {device_type}", 
                font=self.font, bg='white', anchor='w', fg='#000080').pack(fill='x')
        
        # Manufacturer
        tk.Label(info_frame, text="Manufacturer:", 
                font=self.font, bg='white', anchor='w').pack(fill='x', pady=(10,2))
        manufacturer = self.get_device_manufacturer(device_name)
        tk.Label(info_frame, text=f"    {manufacturer}", 
                font=self.font, bg='white', anchor='w', fg='#000080').pack(fill='x')
        
        # Location
        tk.Label(info_frame, text="Location:", 
                font=self.font, bg='white', anchor='w').pack(fill='x', pady=(10,2))
        location = self.get_device_location(device_name)
        tk.Label(info_frame, text=f"    {location}", 
                font=self.font, bg='white', anchor='w', fg='#000080').pack(fill='x')
        
        # Device status
        tk.Label(info_frame, text="Device status:", 
                font=self.font, bg='white', anchor='w').pack(fill='x', pady=(10,2))
        
        status_frame = tk.Frame(info_frame, bg='white', relief='sunken', bd=1)
        status_frame.pack(fill='x', pady=5)
        
        status_text = "This device is working properly."
        if "Hidden" in device_name or "Unknown" in device_name or "Legacy" in device_name:
            status_text = "This device has problems. (Code 10)"
            
        tk.Label(status_frame, text=status_text, 
                font=self.font, bg='white', anchor='w', padx=5, pady=5).pack(fill='x')
        
        # Button frame
        btn_frame = tk.Frame(prop_window, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        ok_btn = tk.Button(btn_frame, text="OK", command=prop_window.destroy,
                          bg=self.button_color, font=self.font,
                          relief='raised', bd=2, padx=20)
        ok_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=prop_window.destroy,
                              bg=self.button_color, font=self.font,
                              relief='raised', bd=2, padx=15)
        cancel_btn.pack(side='left', padx=5)
        
    def get_device_type(self, device_name):
        if 'Display' in device_name or 'VGA' in device_name or 'Graphics' in device_name:
            return 'Display adapters'
        elif 'Audio' in device_name or 'Sound' in device_name:
            return 'Sound, video and game controllers'
        elif 'Network' in device_name or 'Ethernet' in device_name or 'Adapter' in device_name:
            return 'Network adapters'
        elif 'USB' in device_name:
            return 'Universal Serial Bus controllers'
        elif 'Disk' in device_name or 'Drive' in device_name:
            return 'Disk drives'
        elif 'Keyboard' in device_name:
            return 'Keyboard'
        elif 'Mouse' in device_name:
            return 'Mouse'
        elif 'Timer' in device_name or 'Controller' in device_name or 'DMA' in device_name:
            return 'System devices'
        else:
            return 'Other devices'
            
    def get_device_manufacturer(self, device_name):
        if 'Microsoft' in device_name:
            return 'Microsoft'
        elif 'Standard' in device_name or 'Generic' in device_name:
            return 'Standard system devices'
        elif 'Creative' in device_name:
            return 'Creative Technology Ltd.'
        elif 'Intel' in device_name:
            return 'Intel Corporation'
        else:
            return 'Unknown manufacturer'
            
    def get_device_location(self, device_name):
        if 'USB' in device_name:
            return 'Universal Serial Bus'
        elif 'PS/2' in device_name:
            return 'PS/2 Port'
        elif 'PCI' in device_name or 'Audio' in device_name or 'Graphics' in device_name or 'Ethernet' in device_name:
            return 'PCI bus 0, device 1, function 0'
        elif 'IDE' in device_name or 'Disk' in device_name:
            return 'IDE Channel 0'
        elif 'COM' in device_name:
            return 'ISA bus'
        else:
            return 'System board'
        
    def refresh_devices(self):
        self.populate_devices()
        
    def remove_device(self):
        # Show confirmation dialog
        confirm_window = tk.Toplevel(self.root)
        confirm_window.title("Confirm Device Removal")
        confirm_window.geometry("350x120")
        confirm_window.configure(bg=self.bg_color)
        confirm_window.transient(self.root)
        confirm_window.grab_set()
        
        tk.Label(confirm_window, text="Warning: You are about to remove this device from your system.",
                font=self.font, bg=self.bg_color).pack(pady=10)
        tk.Label(confirm_window, text="This could cause your system to become unstable.",
                font=self.font, bg=self.bg_color).pack()
        
        btn_frame = tk.Frame(confirm_window, bg=self.bg_color)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="OK", command=confirm_window.destroy,
                 bg=self.button_color, font=self.font, padx=20).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Cancel", command=confirm_window.destroy,
                 bg=self.button_color, font=self.font, padx=20).pack(side='left', padx=5)
        
    def print_devices(self):
        # Show print dialog
        print_window = tk.Toplevel(self.root)
        print_window.title("Print")
        print_window.geometry("300x200")
        print_window.configure(bg=self.bg_color)
        print_window.transient(self.root)
        print_window.grab_set()
        
        tk.Label(print_window, text="Print Device Manager Information",
                font=self.font, bg=self.bg_color).pack(pady=10)
        
        print_frame = tk.Frame(print_window, bg='white', relief='sunken', bd=2)
        print_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(print_frame, text="Printer: Default Printer", 
                font=self.font, bg='white').pack(anchor='w', padx=5, pady=2)
        tk.Label(print_frame, text="Pages: All", 
                font=self.font, bg='white').pack(anchor='w', padx=5, pady=2)
        
        btn_frame = tk.Frame(print_window, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Print", command=print_window.destroy,
                 bg=self.button_color, font=self.font, padx=20).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Cancel", command=print_window.destroy,
                 bg=self.button_color, font=self.font, padx=20).pack(side='left', padx=5)

def main():
    root = tk.Tk()
    
    # Set Windows 95 icon if available
    try:
        root.iconbitmap('') # Would use actual icon file
    except:
        pass
        
    app = DeviceManagerW95(root)
    root.mainloop()

if __name__ == "__main__":
    main()
