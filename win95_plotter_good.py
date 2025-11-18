import tkinter as tk
from tkinter import messagebox, scrolledtext
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class Win95DataPlotter:
    def __init__(self, rootdataplt):
        self.rootdataplt = rootdataplt
        self.rootdataplt.title("Data Plotter")
        self.rootdataplt.geometry("900x700")
        self.rootdataplt.configure(bg="#c0c0c0")
        
        # Create menu bar
        menubar = tk.Menu(rootdataplt)
        rootdataplt.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear All", command=self.clear_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=rootdataplt.destroy)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main container with sunken border
        main_frame = tk.Frame(rootdataplt, bg="#c0c0c0", relief=tk.SUNKEN, bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for controls
        left_panel = tk.Frame(main_frame, bg="#c0c0c0", width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        
        # Chart type selection
        chart_frame = tk.LabelFrame(left_panel, text="Chart Type", bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        chart_frame.pack(fill=tk.X, pady=5)
        
        self.chart_type = tk.StringVar(value="line")
        tk.Radiobutton(chart_frame, text="Line Chart", variable=self.chart_type, 
                      value="line", bg="#c0c0c0").pack(anchor=tk.W, padx=10)
        tk.Radiobutton(chart_frame, text="Bar Chart", variable=self.chart_type, 
                      value="bar", bg="#c0c0c0").pack(anchor=tk.W, padx=10)
        tk.Radiobutton(chart_frame, text="Scatter Plot", variable=self.chart_type, 
                      value="scatter", bg="#c0c0c0").pack(anchor=tk.W, padx=10)
        tk.Radiobutton(chart_frame, text="Pie Chart", variable=self.chart_type, 
                      value="pie", bg="#c0c0c0").pack(anchor=tk.W, padx=10)
        tk.Radiobutton(chart_frame, text="Histogram", variable=self.chart_type, 
                      value="hist", bg="#c0c0c0").pack(anchor=tk.W, padx=10)
        
        # Data input mode
        mode_frame = tk.LabelFrame(left_panel, text="Data Input Mode", bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        mode_frame.pack(fill=tk.X, pady=5)
        
        self.input_mode = tk.StringVar(value="simple")
        tk.Radiobutton(mode_frame, text="Simple (Y values only)", variable=self.input_mode, 
                      value="simple", bg="#c0c0c0").pack(anchor=tk.W, padx=10)
        tk.Radiobutton(mode_frame, text="X,Y pairs", variable=self.input_mode, 
                      value="pairs", bg="#c0c0c0").pack(anchor=tk.W, padx=10)
        tk.Radiobutton(mode_frame, text="Multiple series", variable=self.input_mode, 
                      value="multi", bg="#c0c0c0").pack(anchor=tk.W, padx=10)
        
        # Data input area
        data_frame = tk.LabelFrame(left_panel, text="Data Input", bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        data_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(data_frame, text="Enter data (comma or space separated):", 
                bg="#c0c0c0").pack(anchor=tk.W, padx=5, pady=2)
        
        self.data_input = scrolledtext.ScrolledText(data_frame, height=10, width=30, 
                                                    relief=tk.SUNKEN, bd=2)
        self.data_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chart customization
        custom_frame = tk.LabelFrame(left_panel, text="Customization", bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        custom_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(custom_frame, text="Chart Title:", bg="#c0c0c0").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.title_entry = tk.Entry(custom_frame, relief=tk.SUNKEN, bd=2)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        self.title_entry.insert(0, "Data Chart")
        
        tk.Label(custom_frame, text="X Label:", bg="#c0c0c0").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.xlabel_entry = tk.Entry(custom_frame, relief=tk.SUNKEN, bd=2)
        self.xlabel_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)
        self.xlabel_entry.insert(0, "X Axis")
        
        tk.Label(custom_frame, text="Y Label:", bg="#c0c0c0").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.ylabel_entry = tk.Entry(custom_frame, relief=tk.SUNKEN, bd=2)
        self.ylabel_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.EW)
        self.ylabel_entry.insert(0, "Y Axis")
        
        custom_frame.columnconfigure(1, weight=1)
        
        # Plot button
        tk.Button(left_panel, text="Generate Chart", command=self.plot_data, 
                 relief=tk.RAISED, bd=3, bg="#c0c0c0").pack(fill=tk.X, pady=10)
        
        # Right panel for chart display
        right_panel = tk.Frame(main_frame, bg="#c0c0c0", relief=tk.SUNKEN, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Matplotlib figure
        self.figure = Figure(figsize=(6, 5), dpi=80, facecolor='#ffffff')
        self.ax = self.figure.add_subplot(111, facecolor='#ffffff')
        self.canvas = FigureCanvasTkAgg(self.figure, right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial empty plot
        self.ax.text(0.5, 0.5, 'Enter data and click Generate Chart', 
                    ha='center', va='center', transform=self.ax.transAxes)
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.canvas.draw()
        
    def parse_data(self, text):
        """Parse input data based on selected mode"""
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        if self.input_mode.get() == "simple":
            # Simple mode: just Y values
            data = []
            for line in lines:
                values = [float(x) for x in line.replace(',', ' ').split() if x]
                data.extend(values)
            return list(range(len(data))), data
        
        elif self.input_mode.get() == "pairs":
            # Pairs mode: X,Y values
            x_data, y_data = [], []
            for line in lines:
                values = [float(x) for x in line.replace(',', ' ').split() if x]
                if len(values) >= 2:
                    x_data.append(values[0])
                    y_data.append(values[1])
            return x_data, y_data
        
        else:  # multi mode
            # Multiple series: each line is a series
            series = []
            for line in lines:
                values = [float(x) for x in line.replace(',', ' ').split() if x]
                if values:
                    series.append(values)
            return series
    
    def plot_data(self):
        """Generate the chart based on inputs"""
        try:
            text = self.data_input.get("1.0", tk.END)
            if not text.strip():
                messagebox.showwarning("No Data", "Please enter some data to plot.")
                return
            
            self.ax.clear()
            chart_type = self.chart_type.get()
            
            if self.input_mode.get() == "multi":
                series = self.parse_data(text)
                if chart_type == "line":
                    for i, s in enumerate(series):
                        self.ax.plot(s, marker='o', label=f'Series {i+1}')
                    self.ax.legend()
                elif chart_type == "bar":
                    x = np.arange(len(series[0]))
                    width = 0.8 / len(series)
                    for i, s in enumerate(series):
                        self.ax.bar(x + i * width, s, width, label=f'Series {i+1}')
                    self.ax.legend()
                else:
                    messagebox.showinfo("Info", "Multiple series only supported for Line and Bar charts")
                    return
            else:
                x_data, y_data = self.parse_data(text)
                
                if chart_type == "line":
                    self.ax.plot(x_data, y_data, marker='o', color='blue')
                elif chart_type == "bar":
                    self.ax.bar(x_data, y_data, color='steelblue')
                elif chart_type == "scatter":
                    self.ax.scatter(x_data, y_data, color='red', s=50)
                elif chart_type == "pie":
                    self.ax.pie(y_data, labels=[f'Item {i+1}' for i in range(len(y_data))], 
                               autopct='%1.1f%%')
                elif chart_type == "hist":
                    self.ax.hist(y_data, bins=min(20, len(y_data)), color='green', edgecolor='black')
            
            if chart_type != "pie":
                self.ax.set_xlabel(self.xlabel_entry.get())
                self.ax.set_ylabel(self.ylabel_entry.get())
            
            self.ax.set_title(self.title_entry.get())
            self.ax.grid(True, alpha=0.3)
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot data:\n{str(e)}")
    
    def clear_all(self):
        """Clear all inputs and chart"""
        self.data_input.delete("1.0", tk.END)
        self.ax.clear()
        self.ax.text(0.5, 0.5, 'Enter data and click Generate Chart', 
                    ha='center', va='center', transform=self.ax.transAxes)
        self.canvas.draw()
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Data Plotter v1.0\n\nSupports multiple chart types and data formats.\n\nPress enter for a new field of number.")

if __name__ == "__main__":
    rootdataplt = tk.Tk()
    app = Win95DataPlotter(rootdataplt)
    rootdataplt.mainloop()
