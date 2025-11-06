import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import datetime
from pathlib import Path
import json
import hashlib
from collections import defaultdict

class ForensicTimelineBuilder:
    def __init__(self, rootfons):
        self.rootfons = rootfons
        self.rootfons.title("Forensic Timeline Builder - Files & Folders")
        self.rootfons.geometry("1100x700")
        self.rootfons.configure(bg='#c0c0c0')
        
        self.files_data = []
        self.selected_path = ""
        self.filter_extension = "all"
        self.date_filter_enabled = False
        self.date_from = None
        self.date_to = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title Bar
        title_frame = tk.Frame(self.rootfons, bg='#000080', height=50)
        title_frame.pack(fill='x', padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="Forensic Timeline Builder",
            bg='#000080', 
            fg='#ffffff',
            font=('MS Sans Serif', 14, 'bold')
        )
        title_label.pack(pady=12)
        
        # Menu Frame
        menu_frame = tk.Frame(self.rootfons, bg='#c0c0c0', relief='raised', bd=2)
        menu_frame.pack(fill='x', padx=2, pady=2)
        
        tk.Button(
            menu_frame,
            text="Select Folder",
            command=self.select_folder,
            bg='#c0c0c0',
            relief='raised',
            bd=2,
            padx=10,
            pady=2,
            font=('MS Sans Serif', 8)
        ).pack(side='left', padx=2, pady=2)
        
        tk.Button(
            menu_frame,
            text="Deep Scan",
            command=self.scan_files,
            bg='#c0c0c0',
            relief='raised',
            bd=2,
            padx=10,
            pady=2,
            font=('MS Sans Serif', 8)
        ).pack(side='left', padx=2, pady=2)
        
        tk.Button(
            menu_frame,
            text="Export Report",
            command=self.export_timeline,
            bg='#c0c0c0',
            relief='raised',
            bd=2,
            padx=10,
            pady=2,
            font=('MS Sans Serif', 8)
        ).pack(side='left', padx=2, pady=2)
        
        tk.Button(
            menu_frame,
            text="Analyze Patterns",
            command=self.analyze_patterns,
            bg='#c0c0c0',
            relief='raised',
            bd=2,
            padx=10,
            pady=2,
            font=('MS Sans Serif', 8)
        ).pack(side='left', padx=2, pady=2)
        
        tk.Button(
            menu_frame,
            text="Find Duplicates",
            command=self.find_duplicates,
            bg='#c0c0c0',
            relief='raised',
            bd=2,
            padx=10,
            pady=2,
            font=('MS Sans Serif', 8)
        ).pack(side='left', padx=2, pady=2)
        
        tk.Button(
            menu_frame,
            text="Clear",
            command=self.clear_data,
            bg='#c0c0c0',
            relief='raised',
            bd=2,
            padx=10,
            pady=2,
            font=('MS Sans Serif', 8)
        ).pack(side='left', padx=2, pady=2)
        
        # Path Display
        path_frame = tk.Frame(self.rootfons, bg='#c0c0c0')
        path_frame.pack(fill='x', padx=5, pady=2)
        
        tk.Label(
            path_frame,
            text="Selected Path:",
            bg='#c0c0c0',
            font=('MS Sans Serif', 8, 'bold')
        ).pack(side='left', padx=2)
        
        self.path_label = tk.Label(
            path_frame,
            text="No folder selected",
            bg='#ffffff',
            relief='sunken',
            bd=2,
            anchor='w',
            font=('MS Sans Serif', 8)
        )
        self.path_label.pack(side='left', fill='x', expand=True, padx=2)
        
        # Filter Frame
        filter_frame = tk.Frame(self.rootfons, bg='#c0c0c0', relief='groove', bd=2)
        filter_frame.pack(fill='x', padx=5, pady=5)
        
        # Sort options
        sort_subframe = tk.Frame(filter_frame, bg='#c0c0c0')
        sort_subframe.pack(side='left', padx=5, pady=3)
        
        tk.Label(
            sort_subframe,
            text="Sort By:",
            bg='#c0c0c0',
            font=('MS Sans Serif', 8, 'bold')
        ).pack(side='left', padx=5)
        
        self.sort_var = tk.StringVar(value='modified')
        sorts = [('Modified', 'modified'), ('Created', 'created'), ('Accessed', 'accessed'), ('Name', 'name'), ('Size', 'size')]
        
        for text, value in sorts:
            tk.Radiobutton(
                sort_subframe,
                text=text,
                variable=self.sort_var,
                value=value,
                bg='#c0c0c0',
                font=('MS Sans Serif', 8),
                command=self.refresh_display
            ).pack(side='left', padx=2)
        
        # Extension filter
        ext_subframe = tk.Frame(filter_frame, bg='#c0c0c0')
        ext_subframe.pack(side='left', padx=20, pady=3)
        
        tk.Label(
            ext_subframe,
            text="Extension:",
            bg='#c0c0c0',
            font=('MS Sans Serif', 8, 'bold')
        ).pack(side='left', padx=5)
        
        self.ext_var = tk.StringVar(value='all')
        self.ext_dropdown = tk.OptionMenu(ext_subframe, self.ext_var, 'all', command=self.on_filter_change)
        self.ext_dropdown.config(bg='#c0c0c0', font=('MS Sans Serif', 8), relief='raised', bd=2)
        self.ext_dropdown.pack(side='left')
        
        # Stats Frame
        stats_frame = tk.Frame(self.rootfons, bg='#c0c0c0', relief='sunken', bd=2)
        stats_frame.pack(fill='x', padx=5, pady=2)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Files: 0 | Total Size: 0 bytes | Extensions: 0 | Scan Depth: 0",
            bg='#c0c0c0',
            fg='#000000',
            font=('MS Sans Serif', 8),
            anchor='w'
        )
        self.stats_label.pack(fill='x', padx=5, pady=2)
        
        # Main Display Area with tabs
        notebook_frame = tk.Frame(self.rootfons, bg='#c0c0c0', relief='sunken', bd=2)
        notebook_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tab buttons
        tab_buttons_frame = tk.Frame(notebook_frame, bg='#c0c0c0')
        tab_buttons_frame.pack(fill='x', padx=2, pady=2)
        
        self.current_tab = 'timeline'
        
        self.tab_timeline_btn = tk.Button(
            tab_buttons_frame,
            text="Timeline View",
            command=lambda: self.switch_tab('timeline'),
            bg='#ffffff',
            relief='raised',
            bd=2,
            padx=10,
            pady=2,
            font=('MS Sans Serif', 8, 'bold')
        )
        self.tab_timeline_btn.pack(side='left', padx=1)
        
        self.tab_analysis_btn = tk.Button(
            tab_buttons_frame,
            text="Analysis",
            command=lambda: self.switch_tab('analysis'),
            bg='#c0c0c0',
            relief='raised',
            bd=2,
            padx=10,
            pady=2,
            font=('MS Sans Serif', 8)
        )
        self.tab_analysis_btn.pack(side='left', padx=1)
        
        self.tab_details_btn = tk.Button(
            tab_buttons_frame,
            text="Detailed View",
            command=lambda: self.switch_tab('details'),
            bg='#c0c0c0',
            relief='raised',
            bd=2,
            padx=10,
            pady=2,
            font=('MS Sans Serif', 8)
        )
        self.tab_details_btn.pack(side='left', padx=1)
        
        # Content frame for all tabs
        self.content_frame = tk.Frame(notebook_frame, bg='#ffffff')
        self.content_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Timeline View
        self.timeline_frame = tk.Frame(self.content_frame, bg='#ffffff')
        
        timeline_scroll_frame = tk.Frame(self.timeline_frame, bg='#c0c0c0', relief='sunken', bd=2)
        timeline_scroll_frame.pack(fill='both', expand=True)
        
        v_scrollbar = tk.Scrollbar(timeline_scroll_frame, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')
        
        h_scrollbar = tk.Scrollbar(timeline_scroll_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        
        self.text_display = tk.Text(
            timeline_scroll_frame,
            bg='#ffffff',
            fg='#000000',
            font=('Courier New', 8),
            wrap='none',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            state='disabled'
        )
        self.text_display.pack(fill='both', expand=True)
        
        v_scrollbar.config(command=self.text_display.yview)
        h_scrollbar.config(command=self.text_display.xview)
        
        self.timeline_frame.pack(fill='both', expand=True)
        
        # Analysis View
        self.analysis_frame = tk.Frame(self.content_frame, bg='#ffffff')
        
        analysis_scroll_frame = tk.Frame(self.analysis_frame, bg='#c0c0c0', relief='sunken', bd=2)
        analysis_scroll_frame.pack(fill='both', expand=True)
        
        v_scrollbar2 = tk.Scrollbar(analysis_scroll_frame, orient='vertical')
        v_scrollbar2.pack(side='right', fill='y')
        
        self.analysis_display = tk.Text(
            analysis_scroll_frame,
            bg='#ffffff',
            fg='#000000',
            font=('Courier New', 8),
            wrap='word',
            yscrollcommand=v_scrollbar2.set,
            state='disabled'
        )
        self.analysis_display.pack(fill='both', expand=True)
        v_scrollbar2.config(command=self.analysis_display.yview)
        
        # Details View
        self.details_frame = tk.Frame(self.content_frame, bg='#ffffff')
        
        details_scroll_frame = tk.Frame(self.details_frame, bg='#c0c0c0', relief='sunken', bd=2)
        details_scroll_frame.pack(fill='both', expand=True)
        
        v_scrollbar3 = tk.Scrollbar(details_scroll_frame, orient='vertical')
        v_scrollbar3.pack(side='right', fill='y')
        
        h_scrollbar3 = tk.Scrollbar(details_scroll_frame, orient='horizontal')
        h_scrollbar3.pack(side='bottom', fill='x')
        
        self.details_display = tk.Text(
            details_scroll_frame,
            bg='#ffffff',
            fg='#000000',
            font=('Courier New', 8),
            wrap='none',
            yscrollcommand=v_scrollbar3.set,
            xscrollcommand=h_scrollbar3.set,
            state='disabled'
        )
        self.details_display.pack(fill='both', expand=True)
        
        v_scrollbar3.config(command=self.details_display.yview)
        h_scrollbar3.config(command=self.details_display.xview)
        
        # Status Bar
        status_frame = tk.Frame(self.rootfons, bg='#c0c0c0', relief='sunken', bd=2)
        status_frame.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready - Forensic Timeline Builder",
            bg='#c0c0c0',
            fg='#000000',
            font=('MS Sans Serif', 8),
            anchor='w'
        )
        self.status_label.pack(side='left', fill='x', expand=True, padx=2, pady=2)
        
        self.progress_label = tk.Label(
            status_frame,
            text="",
            bg='#c0c0c0',
            fg='#000080',
            font=('MS Sans Serif', 8, 'bold'),
            anchor='e'
        )
        self.progress_label.pack(side='right', padx=10, pady=2)
        
    def switch_tab(self, tab_name):
        self.current_tab = tab_name
        
        # Hide all frames
        self.timeline_frame.pack_forget()
        self.analysis_frame.pack_forget()
        self.details_frame.pack_forget()
        
        # Reset button styles
        self.tab_timeline_btn.config(bg='#c0c0c0', font=('MS Sans Serif', 8))
        self.tab_analysis_btn.config(bg='#c0c0c0', font=('MS Sans Serif', 8))
        self.tab_details_btn.config(bg='#c0c0c0', font=('MS Sans Serif', 8))
        
        # Show selected frame and highlight button
        if tab_name == 'timeline':
            self.timeline_frame.pack(fill='both', expand=True)
            self.tab_timeline_btn.config(bg='#ffffff', font=('MS Sans Serif', 8, 'bold'))
        elif tab_name == 'analysis':
            self.analysis_frame.pack(fill='both', expand=True)
            self.tab_analysis_btn.config(bg='#ffffff', font=('MS Sans Serif', 8, 'bold'))
        elif tab_name == 'details':
            self.details_frame.pack(fill='both', expand=True)
            self.tab_details_btn.config(bg='#ffffff', font=('MS Sans Serif', 8, 'bold'))
        
    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Analyze")
        if folder:
            self.selected_path = folder
            self.path_label.config(text=folder)
            self.status_label.config(text=f"Folder selected: {folder}")
            
    def scan_files(self):
        if not self.selected_path:
            messagebox.showwarning("Warning", "Please select a folder first!")
            return
            
        self.status_label.config(text="Deep scanning files...")
        self.progress_label.config(text="Scanning...")
        self.rootfons.update()
        
        self.files_data = []
        total_files = 0
        max_depth = 0
        
        try:
            for rootdir, dirs, files in os.walk(self.selected_path):
                depth = rootdir[len(self.selected_path):].count(os.sep)
                max_depth = max(max_depth, depth)
                
                for filename in files:
                    total_files += 1
                    if total_files % 100 == 0:
                        self.progress_label.config(text=f"Scanned: {total_files}")
                        self.rootfons.update()
                    
                    filepath = os.path.join(rootdir, filename)
                    try:
                        stat_info = os.stat(filepath)
                        file_size = stat_info.st_size
                        
                        # Calculate MD5 hash for files under 10MB
                        file_hash = None
                        if file_size < 10 * 1024 * 1024:  # 10MB
                            try:
                                with open(filepath, 'rb') as f:
                                    file_hash = hashlib.md5(f.read()).hexdigest()
                            except:
                                file_hash = None
                        
                        file_info = {
                            'name': filename,
                            'path': filepath,
                            'relative_path': os.path.relpath(filepath, self.selected_path),
                            'size': file_size,
                            'modified': datetime.datetime.fromtimestamp(stat_info.st_mtime),
                            'created': datetime.datetime.fromtimestamp(stat_info.st_ctime),
                            'accessed': datetime.datetime.fromtimestamp(stat_info.st_atime),
                            'extension': Path(filename).suffix.lower(),
                            'depth': depth,
                            'hash': file_hash
                        }
                        self.files_data.append(file_info)
                    except Exception as e:
                        print(f"Error processing {filepath}: {e}")
            
            # Update extension filter dropdown
            extensions = sorted(set(f['extension'] for f in self.files_data if f['extension']))
            menu = self.ext_dropdown['menu']
            menu.delete(0, 'end')
            menu.add_command(label='all', command=lambda: self.ext_var.set('all'))
            for ext in extensions:
                menu.add_command(label=ext, command=lambda e=ext: self.ext_var.set(e))
            
            self.refresh_display()
            self.auto_analyze_patterns()
            self.update_stats(max_depth)
            
            self.status_label.config(text=f"Scan complete. Found {len(self.files_data)} files.")
            self.progress_label.config(text="Complete")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error scanning files: {str(e)}")
            self.status_label.config(text="Error during scan")
            self.progress_label.config(text="")
    
    def on_filter_change(self, value):
        self.ext_var.set(value)
        self.refresh_display()
            
    def refresh_display(self):
        if not self.files_data:
            return
        
        # Filter by extension
        filtered_files = self.files_data
        if self.ext_var.get() != 'all':
            filtered_files = [f for f in self.files_data if f['extension'] == self.ext_var.get()]
        
        sort_key = self.sort_var.get()
        
        if sort_key in ['modified', 'created', 'accessed']:
            sorted_files = sorted(filtered_files, key=lambda x: x[sort_key], reverse=True)
        elif sort_key == 'size':
            sorted_files = sorted(filtered_files, key=lambda x: x['size'], reverse=True)
        else:  # name
            sorted_files = sorted(filtered_files, key=lambda x: x['name'].lower())
        
        self.text_display.config(state='normal')
        self.text_display.delete('1.0', tk.END)
        
        # Header
        header = f"{'FILENAME':<45} {'SIZE':>12} {'MODIFIED':<20} {'CREATED':<20} {'ACCESSED':<20} {'DEPTH':>5}\n"
        self.text_display.insert(tk.END, header)
        self.text_display.insert(tk.END, "=" * 145 + "\n")
        
        # Data rows
        for file_info in sorted_files:
            size_str = self.format_size(file_info['size'])
            modified_str = file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')
            created_str = file_info['created'].strftime('%Y-%m-%d %H:%M:%S')
            accessed_str = file_info['accessed'].strftime('%Y-%m-%d %H:%M:%S')
            
            name_display = file_info['name'][:43] + '..' if len(file_info['name']) > 45 else file_info['name']
            
            row = f"{name_display:<45} {size_str:>12} {modified_str:<20} {created_str:<20} {accessed_str:<20} {file_info['depth']:>5}\n"
            self.text_display.insert(tk.END, row)
        
        self.text_display.config(state='disabled')
        
        # Update details view
        self.update_details_view(sorted_files)
        
    def update_details_view(self, files):
        self.details_display.config(state='normal')
        self.details_display.delete('1.0', tk.END)
        
        self.details_display.insert(tk.END, "DETAILED FILE INFORMATION\n")
        self.details_display.insert(tk.END, "=" * 120 + "\n\n")
        
        for idx, file_info in enumerate(files[:100], 1):  # Limit to first 100 for performance
            self.details_display.insert(tk.END, f"[{idx}] {file_info['name']}\n")
            self.details_display.insert(tk.END, f"    Full Path: {file_info['path']}\n")
            self.details_display.insert(tk.END, f"    Relative: {file_info['relative_path']}\n")
            self.details_display.insert(tk.END, f"    Size: {self.format_size(file_info['size'])} ({file_info['size']:,} bytes)\n")
            self.details_display.insert(tk.END, f"    Extension: {file_info['extension'] or 'None'}\n")
            self.details_display.insert(tk.END, f"    Directory Depth: {file_info['depth']}\n")
            if file_info['hash']:
                self.details_display.insert(tk.END, f"    MD5 Hash: {file_info['hash']}\n")
            self.details_display.insert(tk.END, f"    Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
            self.details_display.insert(tk.END, f"    Created:  {file_info['created'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
            self.details_display.insert(tk.END, f"    Accessed: {file_info['accessed'].strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
            self.details_display.insert(tk.END, "\n" + "-" * 120 + "\n\n")
        
        if len(files) > 100:
            self.details_display.insert(tk.END, f"\n... and {len(files) - 100} more files\n")
            self.details_display.insert(tk.END, "(Detailed view limited to first 100 files for performance)\n")
        
        self.details_display.config(state='disabled')
        
    def update_stats(self, max_depth):
        total_size = sum(f['size'] for f in self.files_data)
        extensions = len(set(f['extension'] for f in self.files_data if f['extension']))
        
        self.stats_label.config(
            text=f"Files: {len(self.files_data)} | Total Size: {self.format_size(total_size)} | Extensions: {extensions} | Max Depth: {max_depth}"
        )
        
    def auto_analyze_patterns(self):
        if not self.files_data:
            return
        
        self.analysis_display.config(state='normal')
        self.analysis_display.delete('1.0', tk.END)
        
        self.analysis_display.insert(tk.END, "FORENSIC ANALYSIS REPORT\n")
        self.analysis_display.insert(tk.END, "=" * 80 + "\n")
        self.analysis_display.insert(tk.END, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.analysis_display.insert(tk.END, f"Source: {self.selected_path}\n")
        self.analysis_display.insert(tk.END, "=" * 80 + "\n\n")
        
        # 1. Suspicious Activity Detection
        self.analysis_display.insert(tk.END, "[1] SUSPICIOUS ACTIVITY DETECTION\n")
        self.analysis_display.insert(tk.END, "-" * 80 + "\n")
        
        time_buckets = defaultdict(list)
        for file_info in self.files_data:
            bucket = file_info['modified'].replace(second=0, microsecond=0)
            time_buckets[bucket].append(file_info)
        
        suspicious_found = False
        for bucket, files in sorted(time_buckets.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            if len(files) > 20:
                suspicious_found = True
                self.analysis_display.insert(tk.END, f"  ALERT: {bucket.strftime('%Y-%m-%d %H:%M')} - {len(files)} files modified\n")
                
                # Show file types involved
                ext_count = defaultdict(int)
                for f in files:
                    ext_count[f['extension'] or 'no_ext'] += 1
                self.analysis_display.insert(tk.END, f"    Extensions: {dict(sorted(ext_count.items(), key=lambda x: x[1], reverse=True)[:5])}\n")
        
        if not suspicious_found:
            self.analysis_display.insert(tk.END, "  No suspicious mass modifications detected.\n")
        
        # 2. File Size Analysis
        self.analysis_display.insert(tk.END, "\n[2] FILE SIZE ANALYSIS\n")
        self.analysis_display.insert(tk.END, "-" * 80 + "\n")
        
        sizes = [f['size'] for f in self.files_data]
        total_size = sum(sizes)
        avg_size = total_size / len(sizes) if sizes else 0
        
        self.analysis_display.insert(tk.END, f"  Total Size: {self.format_size(total_size)}\n")
        self.analysis_display.insert(tk.END, f"  Average File Size: {self.format_size(avg_size)}\n")
        self.analysis_display.insert(tk.END, f"  Largest File: {self.format_size(max(sizes))} - {max(self.files_data, key=lambda x: x['size'])['name']}\n")
        self.analysis_display.insert(tk.END, f"  Smallest File: {self.format_size(min(sizes))} - {min(self.files_data, key=lambda x: x['size'])['name']}\n")
        
        # Top 10 largest files
        self.analysis_display.insert(tk.END, "\n  Top 10 Largest Files:\n")
        for idx, f in enumerate(sorted(self.files_data, key=lambda x: x['size'], reverse=True)[:10], 1):
            self.analysis_display.insert(tk.END, f"    {idx}. {self.format_size(f['size']):>12} - {f['name']}\n")
        
        # 3. Extension Distribution
        self.analysis_display.insert(tk.END, "\n[3] EXTENSION DISTRIBUTION\n")
        self.analysis_display.insert(tk.END, "-" * 80 + "\n")
        
        ext_stats = defaultdict(lambda: {'count': 0, 'size': 0})
        for f in self.files_data:
            ext = f['extension'] or 'no_extension'
            ext_stats[ext]['count'] += 1
            ext_stats[ext]['size'] += f['size']
        
        sorted_exts = sorted(ext_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        for ext, stats in sorted_exts[:15]:
            self.analysis_display.insert(tk.END, 
                f"  {ext:20s} Count: {stats['count']:>6} Size: {self.format_size(stats['size']):>12}\n")
        
        # 4. Temporal Analysis
        self.analysis_display.insert(tk.END, "\n[4] TEMPORAL ANALYSIS\n")
        self.analysis_display.insert(tk.END, "-" * 80 + "\n")
        
        oldest_modified = min(self.files_data, key=lambda x: x['modified'])
        newest_modified = max(self.files_data, key=lambda x: x['modified'])
        
        self.analysis_display.insert(tk.END, f"  Oldest Modified: {oldest_modified['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.analysis_display.insert(tk.END, f"    File: {oldest_modified['name']}\n")
        self.analysis_display.insert(tk.END, f"  Newest Modified: {newest_modified['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.analysis_display.insert(tk.END, f"    File: {newest_modified['name']}\n")
        
        # Files modified in last 24 hours
        now = datetime.datetime.now()
        recent_files = [f for f in self.files_data if (now - f['modified']).total_seconds() < 86400]
        self.analysis_display.insert(tk.END, f"\n  Files Modified in Last 24 Hours: {len(recent_files)}\n")
        
        # 5. Directory Depth Analysis
        self.analysis_display.insert(tk.END, "\n[5] DIRECTORY STRUCTURE ANALYSIS\n")
        self.analysis_display.insert(tk.END, "-" * 80 + "\n")
        
        depth_stats = defaultdict(int)
        for f in self.files_data:
            depth_stats[f['depth']] += 1
        
        max_depth = max(depth_stats.keys()) if depth_stats else 0
        self.analysis_display.insert(tk.END, f"  Maximum Depth: {max_depth}\n")
        self.analysis_display.insert(tk.END, f"  Average Depth: {sum(f['depth'] for f in self.files_data) / len(self.files_data):.2f}\n\n")
        
        self.analysis_display.insert(tk.END, "  Files by Depth:\n")
        for depth in sorted(depth_stats.keys()):
            self.analysis_display.insert(tk.END, f"    Depth {depth}: {depth_stats[depth]} files\n")
        
        # Files in deep directories (potential hiding)
        deep_files = [f for f in self.files_data if f['depth'] > 5]
        if deep_files:
            self.analysis_display.insert(tk.END, f"\n  WARNING: {len(deep_files)} files found in deep directories (depth > 5)\n")
            self.analysis_display.insert(tk.END, "  This could indicate hidden or obscured files.\n")
        
        self.analysis_display.insert(tk.END, "\n" + "=" * 80 + "\n")
        self.analysis_display.insert(tk.END, "END OF ANALYSIS REPORT\n")
        
        self.analysis_display.config(state='disabled')
        
    def analyze_patterns(self):
        if not self.files_data:
            messagebox.showwarning("Warning", "Please scan files first!")
            return
        
        self.switch_tab('analysis')
        messagebox.showinfo("Analysis Complete", "Pattern analysis has been updated in the Analysis tab.")
        
    def find_duplicates(self):
        if not self.files_data:
            messagebox.showwarning("Warning", "Please scan files first!")
            return
        
        self.status_label.config(text="Finding duplicate files...")
        self.progress_label.config(text="Processing...")
        self.rootfons.update()
        
        # Group files by hash
        hash_groups = defaultdict(list)
        for f in self.files_data:
            if f['hash']:
                hash_groups[f['hash']].append(f)
        
        # Find duplicates
        duplicates = {h: files for h, files in hash_groups.items() if len(files) > 1}
        
        if not duplicates:
            messagebox.showinfo("Duplicate Search", "No duplicate files found!")
            self.status_label.config(text="No duplicates found")
            self.progress_label.config(text="")
            return
        
        # Display results
        result_window = tk.Toplevel(self.rootfons)
        result_window.title("Duplicate Files Found")
        result_window.geometry("900x600")
        result_window.configure(bg='#c0c0c0')
        
        title_frame = tk.Frame(result_window, bg='#000080', height=40)
        title_frame.pack(fill='x', padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text=f"Duplicate Files Report - {len(duplicates)} duplicate groups found",
            bg='#000080',
            fg='#ffffff',
            font=('MS Sans Serif', 10, 'bold')
        ).pack(pady=8)
        
        text_frame = tk.Frame(result_window, bg='#c0c0c0', relief='sunken', bd=2)
        text_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        text_widget = tk.Text(
            text_frame,
            bg='#ffffff',
            fg='#000000',
            font=('Courier New', 8),
            wrap='none',
            yscrollcommand=scrollbar.set
        )
        text_widget.pack(fill='both', expand=True)
        scrollbar.config(command=text_widget.yview)
        
        total_wasted = 0
        for idx, (hash_val, files) in enumerate(sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True), 1):
            file_size = files[0]['size']
            wasted_space = file_size * (len(files) - 1)
            total_wasted += wasted_space
            
            text_widget.insert(tk.END, f"\n[GROUP {idx}] MD5: {hash_val}\n")
            text_widget.insert(tk.END, f"  File Size: {self.format_size(file_size)}\n")
            text_widget.insert(tk.END, f"  Duplicates: {len(files)} copies\n")
            text_widget.insert(tk.END, f"  Wasted Space: {self.format_size(wasted_space)}\n")
            text_widget.insert(tk.END, "  Locations:\n")
            
            for f in files:
                text_widget.insert(tk.END, f"    - {f['relative_path']}\n")
            
            text_widget.insert(tk.END, "\n" + "-" * 100 + "\n")
        
        text_widget.insert(tk.END, f"\n{'=' * 100}\n")
        text_widget.insert(tk.END, f"SUMMARY:\n")
        text_widget.insert(tk.END, f"  Total duplicate groups: {len(duplicates)}\n")
        text_widget.insert(tk.END, f"  Total wasted space: {self.format_size(total_wasted)}\n")
        text_widget.insert(tk.END, f"{'=' * 100}\n")
        
        text_widget.config(state='disabled')
        
        tk.Button(
            result_window,
            text="Close",
            command=result_window.destroy,
            bg='#c0c0c0',
            relief='raised',
            bd=2,
            padx=20,
            pady=5,
            font=('MS Sans Serif', 8)
        ).pack(pady=5)
        
        self.status_label.config(text=f"Found {len(duplicates)} duplicate groups")
        self.progress_label.config(text="")
        
    def export_timeline(self):
        if not self.files_data:
            messagebox.showwarning("Warning", "No data to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            if filename.endswith('.json'):
                self.export_json(filename)
            elif filename.endswith('.csv'):
                self.export_csv(filename)
            else:
                self.export_text(filename)
            
            messagebox.showinfo("Success", f"Timeline exported to:\n{filename}")
            self.status_label.config(text=f"Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting timeline: {str(e)}")
            
    def export_text(self, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("FORENSIC TIMELINE REPORT\n")
            f.write("=" * 120 + "\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source Path: {self.selected_path}\n")
            f.write(f"Total Files: {len(self.files_data)}\n")
            f.write("=" * 120 + "\n\n")
            
            sorted_files = sorted(self.files_data, key=lambda x: x['modified'], reverse=True)
            
            for file_info in sorted_files:
                f.write(f"File: {file_info['name']}\n")
                f.write(f"  Path: {file_info['relative_path']}\n")
                f.write(f"  Size: {self.format_size(file_info['size'])}\n")
                f.write(f"  Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"  Created:  {file_info['created'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"  Accessed: {file_info['accessed'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                if file_info['hash']:
                    f.write(f"  MD5: {file_info['hash']}\n")
                f.write("\n")
                
    def export_json(self, filename):
        export_data = []
        for f in self.files_data:
            export_data.append({
                'name': f['name'],
                'path': f['path'],
                'relative_path': f['relative_path'],
                'size': f['size'],
                'modified': f['modified'].isoformat(),
                'created': f['created'].isoformat(),
                'accessed': f['accessed'].isoformat(),
                'extension': f['extension'],
                'depth': f['depth'],
                'hash': f['hash']
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'generated': datetime.datetime.now().isoformat(),
                'source_path': self.selected_path,
                'total_files': len(self.files_data),
                'files': export_data
            }, f, indent=2)
            
    def export_csv(self, filename):
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Path', 'Size', 'Modified', 'Created', 'Accessed', 'Extension', 'Depth', 'MD5'])
            
            for file_info in self.files_data:
                writer.writerow([
                    file_info['name'],
                    file_info['relative_path'],
                    file_info['size'],
                    file_info['modified'].strftime('%Y-%m-%d %H:%M:%S'),
                    file_info['created'].strftime('%Y-%m-%d %H:%M:%S'),
                    file_info['accessed'].strftime('%Y-%m-%d %H:%M:%S'),
                    file_info['extension'],
                    file_info['depth'],
                    file_info['hash'] or ''
                ])
                
    def clear_data(self):
        self.files_data = []
        self.selected_path = ""
        self.path_label.config(text="No folder selected")
        self.text_display.config(state='normal')
        self.text_display.delete('1.0', tk.END)
        self.text_display.config(state='disabled')
        self.analysis_display.config(state='normal')
        self.analysis_display.delete('1.0', tk.END)
        self.analysis_display.config(state='disabled')
        self.details_display.config(state='normal')
        self.details_display.delete('1.0', tk.END)
        self.details_display.config(state='disabled')
        self.stats_label.config(text="Files: 0 | Total Size: 0 bytes | Extensions: 0 | Scan Depth: 0")
        self.status_label.config(text="Ready - Data cleared")
        self.progress_label.config(text="")
        
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

if __name__ == "__main__":
    rootFONSI = tk.Tk()
    app = ForensicTimelineBuilder(rootFONSI)
    rootFONSI.mainloop()