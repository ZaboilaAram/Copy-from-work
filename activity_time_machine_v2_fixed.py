import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import sqlite3
import psutil
import threading
import time
from datetime import datetime, timedelta
from collections import defaultdict
import os
import queue
import json
import hashlib
from PIL import ImageGrab, Image, ImageTk
import pyperclip
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path="activity_monitor.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Processes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                process_name TEXT NOT NULL,
                pid INTEGER NOT NULL,
                cpu_percent REAL,
                memory_mb REAL
            )
        ''')
        
        # Files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                file_path TEXT NOT NULL,
                process_name TEXT,
                pid INTEGER,
                file_size INTEGER
            )
        ''')
        
        # Network table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                local_port INTEGER,
                remote_ip TEXT,
                remote_port INTEGER,
                status TEXT,
                process_name TEXT
            )
        ''')
        
        # Screenshots table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                file_path TEXT NOT NULL,
                active_processes TEXT
            )
        ''')
        
        # Clipboard table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clipboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT,
                hash TEXT UNIQUE
            )
        ''')
        
        # USB devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usb_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                device_name TEXT,
                mount_point TEXT,
                total_size INTEGER,
                used_size INTEGER
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds INTEGER,
                idle_time_seconds INTEGER,
                status TEXT
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT
            )
        ''')
        
        # System resources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                disk_read_mb REAL,
                disk_write_mb REAL,
                network_sent_mb REAL,
                network_recv_mb REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_process(self, timestamp, action, process_name, pid, cpu_percent=0, memory_mb=0):
        """Insert process event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO processes (timestamp, action, process_name, pid, cpu_percent, memory_mb)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, action, process_name, pid, cpu_percent, memory_mb))
        conn.commit()
        conn.close()
    
    def insert_file(self, timestamp, action, file_path, process_name=None, pid=None, file_size=0):
        """Insert file event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (timestamp, action, file_path, process_name, pid, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, action, file_path, process_name, pid, file_size))
        conn.commit()
        conn.close()
    
    def insert_network(self, timestamp, local_port, remote_ip, remote_port, status, process_name=None):
        """Insert network event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO network (timestamp, local_port, remote_ip, remote_port, status, process_name)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, local_port, remote_ip, remote_port, status, process_name))
        conn.commit()
        conn.close()
    
    def insert_screenshot(self, timestamp, file_path, active_processes):
        """Insert screenshot record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO screenshots (timestamp, file_path, active_processes)
            VALUES (?, ?, ?)
        ''', (timestamp, file_path, active_processes))
        conn.commit()
        conn.close()
    
    def insert_clipboard(self, timestamp, content, content_type):
        """Insert clipboard entry"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO clipboard (timestamp, content, content_type, hash)
                VALUES (?, ?, ?, ?)
            ''', (timestamp, content, content_type, content_hash))
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # Duplicate content, skip
        conn.close()
    
    def insert_usb_device(self, timestamp, action, device_name, mount_point, total_size=0, used_size=0):
        """Insert USB device event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usb_devices (timestamp, action, device_name, mount_point, total_size, used_size)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, action, device_name, mount_point, total_size, used_size))
        conn.commit()
        conn.close()
    
    def insert_alert(self, timestamp, alert_type, severity, message, details=''):
        """Insert alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (timestamp, alert_type, severity, message, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, alert_type, severity, message, details))
        conn.commit()
        conn.close()
    
    def insert_system_resources(self, timestamp, cpu, memory, disk_read, disk_write, net_sent, net_recv):
        """Insert system resources snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO system_resources (timestamp, cpu_percent, memory_percent, 
                                         disk_read_mb, disk_write_mb, network_sent_mb, network_recv_mb)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, cpu, memory, disk_read, disk_write, net_sent, net_recv))
        conn.commit()
        conn.close()
    
    def get_process_stats(self, hours=24):
        """Get process statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT process_name, COUNT(*) as count, 
                   AVG(cpu_percent) as avg_cpu, 
                   AVG(memory_mb) as avg_mem
            FROM processes
            WHERE timestamp > ? AND action = 'START'
            GROUP BY process_name
            ORDER BY count DESC
            LIMIT 50
        ''', (since,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_timeline(self, limit=100):
        """Get combined timeline of all events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT timestamp, 'PROCESS' as type, 
                   process_name || ' (' || action || ')' as details
            FROM processes
            UNION ALL
            SELECT timestamp, 'FILE', 
                   action || ': ' || file_path
            FROM files
            UNION ALL
            SELECT timestamp, 'NETWORK',
                   remote_ip || ':' || remote_port
            FROM network
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_file_activity(self, hours=24, limit=50):
        """Get recent file activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT timestamp, action, file_path, process_name
            FROM files
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (since, limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_network_connections(self, hours=24, limit=50):
        """Get network connections"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT timestamp, remote_ip, remote_port, process_name
            FROM network
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (since, limit))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_clipboard_history(self, limit=100):
        """Get clipboard history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, content, content_type
            FROM clipboard
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_screenshots(self, limit=50):
        """Get screenshots"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, file_path, active_processes
            FROM screenshots
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_usb_devices(self, limit=50):
        """Get USB device events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, action, device_name, mount_point, total_size
            FROM usb_devices
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_alerts(self, limit=100):
        """Get alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, alert_type, severity, message, details
            FROM alerts
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_system_resources(self, hours=24):
        """Get system resources over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT timestamp, cpu_percent, memory_percent, 
                   disk_read_mb, disk_write_mb, network_sent_mb, network_recv_mb
            FROM system_resources
            WHERE timestamp > ?
            ORDER BY timestamp ASC
        ''', (since,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def search_all(self, search_term, limit=100):
        """Global search across all tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        search_pattern = f'%{search_term}%'
        
        query = '''
            SELECT timestamp, 'PROCESS' as type, process_name as details FROM processes 
            WHERE process_name LIKE ?
            UNION ALL
            SELECT timestamp, 'FILE' as type, file_path FROM files 
            WHERE file_path LIKE ?
            UNION ALL
            SELECT timestamp, 'NETWORK' as type, remote_ip FROM network 
            WHERE remote_ip LIKE ?
            UNION ALL
            SELECT timestamp, 'CLIPBOARD' as type, content FROM clipboard 
            WHERE content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern, limit))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def cleanup_old_data(self, days=30):
        """Delete data older than specified days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        tables = ['processes', 'files', 'network', 'clipboard', 'usb_devices', 'alerts', 'system_resources']
        
        for table in tables:
            cursor.execute(f'DELETE FROM {table} WHERE timestamp < ?', (cutoff,))
        
        conn.commit()
        conn.close()


class ActivityTimeMachineV2:
    def __init__(self, rootactvtmnt):
        self.rootactvtmnt = rootactvtmnt
        self.rootactvtmnt.title("Activity Time Machine - Advanced System Monitor")
        self.rootactvtmnt.geometry("1200x750")
        self.rootactvtmnt.configure(bg="#c0c0c0")
        
        # Database
        self.db = DatabaseManager()
        
        # Queue for thread communication
        self.event_queue = queue.Queue()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Screenshot settings
        self.screenshot_enabled = tk.BooleanVar(value=False)
        self.screenshot_interval = tk.IntVar(value=10)  # minutes
        self.screenshot_dir = "screenshots"
        self.last_screenshot_time = 0  # Track last screenshot time
        
        # Clipboard monitoring
        self.clipboard_enabled = tk.BooleanVar(value=False)
        self.last_clipboard = ""
        
        # USB monitoring
        self.last_partitions = set()
        
        # Session tracking
        self.current_session_id = None
        self.last_activity_time = time.time()
        
        # System resources tracking
        self.last_disk_io = psutil.disk_io_counters()
        self.last_net_io = psutil.net_io_counters()
        
        # Create directories
        os.makedirs(self.screenshot_dir, exist_ok=True)
        os.makedirs("backups", exist_ok=True)
        
        self.setup_ui()
        
        # Start queue processor
        self.process_queue()
        
    def setup_ui(self):
        """Setup user interface"""
        # Title bar - Windows 95 style
        title_frame = tk.Frame(self.rootactvtmnt, bg="#000080", height=25)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Activity Time Machine v2.0 - Advanced System Monitor", 
                              fg="white", bg="#000080", font=("MS Sans Serif", 8, "bold"))
        title_label.pack(side=tk.LEFT, padx=5, pady=3)
        
        # Main frame
        main_frame = tk.Frame(self.rootactvtmnt, bg="#c0c0c0", relief=tk.RAISED, bd=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Control Panel - better organized
        self.setup_control_panel(main_frame)
        
        # Create notebook-style tabs manually (no ttk)
        self.create_tab_system(main_frame)
        
        # Status bar
        status_bar = tk.Frame(self.rootactvtmnt, bg="#c0c0c0", relief=tk.SUNKEN, bd=1)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_bar_label = tk.Label(status_bar, text="Ready - Click Start Monitoring to begin", 
                                         bg="#c0c0c0", anchor=tk.W,
                                         font=("MS Sans Serif", 8))
        self.status_bar_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=1)
        
        self.event_count_label = tk.Label(status_bar, text="Events: 0", 
                                          bg="#c0c0c0", anchor=tk.E,
                                          font=("MS Sans Serif", 8))
        self.event_count_label.pack(side=tk.RIGHT, padx=5, pady=1)
    
    def setup_control_panel(self, parent):
        """Setup control panel with better organization - Windows 95 style"""
        control_frame = tk.Frame(parent, bg="#c0c0c0", relief=tk.GROOVE, bd=2)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Header
        header = tk.Frame(control_frame, bg="#000080", height=20)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="Control Panel", bg="#000080", fg="white",
                font=("MS Sans Serif", 8, "bold")).pack(side=tk.LEFT, padx=5, pady=2)
        
        # Content area
        content = tk.Frame(control_frame, bg="#c0c0c0")
        content.pack(fill=tk.X, padx=10, pady=10)
        
        # Left section - Monitoring
        left_section = tk.Frame(content, bg="#c0c0c0", relief=tk.SUNKEN, bd=1)
        left_section.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        
        tk.Label(left_section, text="Monitoring", bg="#c0c0c0",
                font=("MS Sans Serif", 8, "bold")).pack(anchor=tk.W, padx=5, pady=3)
        
        btn_frame = tk.Frame(left_section, bg="#c0c0c0")
        btn_frame.pack(padx=5, pady=5)
        
        self.start_btn = tk.Button(btn_frame, text="Start", width=12,
                                   relief=tk.RAISED, bd=2, bg="#c0c0c0",
                                   font=("MS Sans Serif", 8), command=self.start_monitoring)
        self.start_btn.grid(row=0, column=0, padx=2, pady=2)
        
        self.stop_btn = tk.Button(btn_frame, text="Stop", width=12,
                                  relief=tk.RAISED, bd=2, bg="#c0c0c0",
                                  font=("MS Sans Serif", 8), command=self.stop_monitoring,
                                  state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=2, pady=2)
        
        # Status indicator
        status_frame = tk.Frame(left_section, bg="#c0c0c0")
        status_frame.pack(padx=5, pady=3)
        
        tk.Label(status_frame, text="Status:", bg="#c0c0c0",
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT)
        
        self.status_label = tk.Label(status_frame, text="Stopped", bg="#c0c0c0",
                                     fg="#800000", font=("MS Sans Serif", 8, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Middle section - Features
        middle_section = tk.Frame(content, bg="#c0c0c0", relief=tk.SUNKEN, bd=1)
        middle_section.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        
        tk.Label(middle_section, text="Optional Features", bg="#c0c0c0",
                font=("MS Sans Serif", 8, "bold")).pack(anchor=tk.W, padx=5, pady=3)
        
        features = tk.Frame(middle_section, bg="#c0c0c0")
        features.pack(padx=5, pady=5)
        
        # Screenshot settings
        screenshot_frame = tk.Frame(features, bg="#c0c0c0")
        screenshot_frame.pack(anchor=tk.W, pady=2)
        
        self.screenshot_check = tk.Checkbutton(screenshot_frame, text="Screenshots every",
                                              variable=self.screenshot_enabled,
                                              bg="#c0c0c0", font=("MS Sans Serif", 8))
        self.screenshot_check.pack(side=tk.LEFT)
        
        self.interval_spinbox = tk.Spinbox(screenshot_frame, from_=1, to=30, width=5,
                                          textvariable=self.screenshot_interval,
                                          font=("MS Sans Serif", 8))
        self.interval_spinbox.pack(side=tk.LEFT, padx=5)
        
        tk.Label(screenshot_frame, text="min", bg="#c0c0c0",
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT)
        
        # Clipboard
        self.clipboard_check = tk.Checkbutton(features, text="Track Clipboard History",
                                             variable=self.clipboard_enabled,
                                             bg="#c0c0c0", font=("MS Sans Serif", 8))
        self.clipboard_check.pack(anchor=tk.W, pady=2)
        
        # Right section - Tools
        right_section = tk.Frame(content, bg="#c0c0c0", relief=tk.SUNKEN, bd=1)
        right_section.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        
        tk.Label(right_section, text="Tools", bg="#c0c0c0",
                font=("MS Sans Serif", 8, "bold")).pack(anchor=tk.W, padx=5, pady=3)
        
        tools = tk.Frame(right_section, bg="#c0c0c0")
        tools.pack(padx=5, pady=5)
        
        tk.Button(tools, text="Backup Database", width=15,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8),
                 command=self.create_backup).pack(pady=2)
        
        tk.Button(tools, text="Cleanup Old Data", width=15,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8),
                 command=self.cleanup_dialog).pack(pady=2)
        
        tk.Button(tools, text="Generate Report", width=15,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8),
                 command=self.generate_report).pack(pady=2)
    
    def create_tab_system(self, parent):
        """Create Windows 95 style tab system without ttk"""
        # Tab container
        tab_container = tk.Frame(parent, bg="#c0c0c0")
        tab_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab buttons frame
        tab_buttons_frame = tk.Frame(tab_container, bg="#c0c0c0")
        tab_buttons_frame.pack(fill=tk.X)
        
        # Tab names in order
        self.tab_names = [
            ("Statistics", "statistics"),
            ("Timeline", "timeline"),
            ("Processes", "processes"),
            ("Files", "files"),
            ("Network", "network"),
            ("Screenshots", "screenshots"),
            ("Clipboard", "clipboard"),
            ("USB Devices", "usb"),
            ("Search", "search"),
            ("Alerts", "alerts")
        ]
        
        # Create tab buttons
        self.tab_buttons = {}
        for name, key in self.tab_names:
            btn = tk.Button(tab_buttons_frame, text=name, width=12,
                          relief=tk.RAISED, bd=2, bg="#c0c0c0",
                          font=("MS Sans Serif", 8),
                          command=lambda k=key: self.show_tab(k))
            btn.pack(side=tk.LEFT, padx=1, pady=1)
            self.tab_buttons[key] = btn
        
        # Content frame for all tabs
        self.tab_content_frame = tk.Frame(tab_container, bg="white", relief=tk.SUNKEN, bd=2)
        self.tab_content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Create all tab contents
        self.create_statistics_tab()
        self.create_timeline_tab()
        self.create_processes_tab()
        self.create_files_tab()
        self.create_network_tab()
        self.create_screenshots_tab()
        self.create_clipboard_tab()
        self.create_usb_tab()
        self.create_search_tab()
        self.create_alerts_tab()
        
        # Show statistics tab by default
        self.current_tab = "statistics"
        self.show_tab("statistics")
    
    def create_statistics_tab(self):
        """Create statistics tab"""
        self.statistics_frame = tk.Frame(self.tab_content_frame, bg="white")
        
        # Toolbar
        toolbar = tk.Frame(self.statistics_frame, bg="#c0c0c0", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Label(toolbar, text="Time range:", bg="#c0c0c0",
                font=("MS Sans Serif", 8, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.stats_timerange = tk.IntVar(value=24)
        
        for hours, text in [(1, "1 Hour"), (6, "6 Hours"), (24, "24 Hours"), (168, "7 Days")]:
            tk.Radiobutton(toolbar, text=text, variable=self.stats_timerange,
                          value=hours, bg="#c0c0c0", font=("MS Sans Serif", 8),
                          command=self.refresh_statistics).pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Refresh Graphs", command=self.refresh_statistics,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.RIGHT, padx=5)
        
        # Info label
        self.stats_info_label = tk.Label(self.statistics_frame, 
                                         text="Click 'Refresh Graphs' to view statistics",
                                         bg="white", fg="#000080",
                                         font=("MS Sans Serif", 8, "bold"))
        self.stats_info_label.pack(pady=5)
        
        # Scrollable container for graphs
        container = tk.Frame(self.statistics_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stats_canvas = tk.Canvas(container, bg="white", yscrollcommand=scrollbar.set)
        self.stats_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.stats_canvas.yview)
        
        self.stats_frame = tk.Frame(self.stats_canvas, bg="white")
        self.stats_canvas.create_window((0, 0), window=self.stats_frame, anchor='nw')
        
        # Bind mousewheel
        self.stats_canvas.bind_all("<MouseWheel>", self._on_mousewheel_stats)
    
    def _on_mousewheel_stats(self, event):
        """Handle mousewheel scrolling for statistics"""
        self.stats_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def _on_mousewheel_screenshots(self, event):
        """Handle mousewheel scrolling for screenshots"""
        self.screenshot_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_timeline_tab(self):
        """Create timeline tab"""
        self.timeline_frame = tk.Frame(self.tab_content_frame, bg="white")
        
        # Toolbar
        toolbar = tk.Frame(self.timeline_frame, bg="#c0c0c0", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_timeline,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="Showing latest 100 events", bg="#c0c0c0",
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=20)
        
        # Timeline display
        container = tk.Frame(self.timeline_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.timeline_text = tk.Text(container, bg="white", fg="black",
                                    font=("Courier New", 9), wrap=tk.WORD,
                                    yscrollcommand=scrollbar.set)
        self.timeline_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.timeline_text.yview)
        
        # Tags
        self.timeline_text.tag_config("process", foreground="#000080")
        self.timeline_text.tag_config("file", foreground="#008000")
        self.timeline_text.tag_config("network", foreground="#800000")
        self.timeline_text.tag_config("usb", foreground="#FF8000")
        self.timeline_text.tag_config("time", foreground="#808080")
    
    def create_processes_tab(self):
        """Create processes tab"""
        self.processes_frame = tk.Frame(self.tab_content_frame, bg="white")
        
        toolbar = tk.Frame(self.processes_frame, bg="#c0c0c0", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_processes,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="Process statistics (Last 24 hours)", bg="#c0c0c0",
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=20)
        
        container = tk.Frame(self.processes_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        #scrollbar = tk.Scrollbar(container)
        #scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.processes_text = scrolledtext.ScrolledText(container, bg="white", fg="black", font=("Courier New", 9), wrap=tk.NONE)
        self.processes_text.pack(fill=tk.BOTH, expand=True)
    
    def create_files_tab(self):
        """Create files tab"""
        self.files_frame = tk.Frame(self.tab_content_frame, bg="white")
        
        toolbar = tk.Frame(self.files_frame, bg="#c0c0c0", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_files,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="File access activity (Last 24 hours)", bg="#c0c0c0",
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=20)
        
        container = tk.Frame(self.files_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        #scrollbar = tk.Scrollbar(container)
        #scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_text = scrolledtext.ScrolledText(container, bg="white", fg="black",
                                                   font=("Courier New", 9), wrap=tk.NONE)
        self.files_text.pack(fill=tk.BOTH, expand=True)
    
    def create_network_tab(self):
        """Create network tab"""
        self.network_frame = tk.Frame(self.tab_content_frame, bg="white")
        
        toolbar = tk.Frame(self.network_frame, bg="#c0c0c0", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_network,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="Network connections (Last 24 hours)", bg="#c0c0c0",
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=20)
        
        container = tk.Frame(self.network_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        #scrollbar = tk.Scrollbar(container)
        #scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.network_text = scrolledtext.ScrolledText(container, bg="white", fg="black",
                                                     font=("Courier New", 9), wrap=tk.NONE)
        self.network_text.pack(fill=tk.BOTH, expand=True)
    
    def create_screenshots_tab(self):
        """Create screenshots tab"""
        self.screenshots_frame = tk.Frame(self.tab_content_frame, bg="white")
        
        toolbar = tk.Frame(self.screenshots_frame, bg="#c0c0c0", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_screenshots,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Take Screenshot Now", command=self.take_screenshot_manual,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Open Folder", command=self.open_screenshot_folder,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        container = tk.Frame(self.screenshots_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.screenshot_canvas = tk.Canvas(container, bg="white", yscrollcommand=scrollbar.set)
        self.screenshot_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Bind mousewheel
        self.screenshot_canvas.bind_all("<MouseWheel>", self._on_mousewheel_screenshots)
        scrollbar.config(command=self.screenshot_canvas.yview)
        
        self.screenshot_frame = tk.Frame(self.screenshot_canvas, bg="white")
        self.screenshot_canvas.create_window((0, 0), window=self.screenshot_frame, anchor="nw")
    
    def create_clipboard_tab(self):
        """Create clipboard tab"""
        self.clipboard_frame = tk.Frame(self.tab_content_frame, bg="white")
        
        toolbar = tk.Frame(self.clipboard_frame, bg="#c0c0c0", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_clipboard,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Clear History", command=self.clear_clipboard_history,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        container = tk.Frame(self.clipboard_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        #scrollbar = tk.Scrollbar(container)
        #scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.clipboard_text = scrolledtext.ScrolledText(container, bg="white", fg="black",
                                                       font=("Courier New", 9), wrap=tk.WORD)
        self.clipboard_text.pack(fill=tk.BOTH, expand=True)
    
    def create_usb_tab(self):
        """Create USB devices tab"""
        self.usb_frame = tk.Frame(self.tab_content_frame, bg="white")
        
        toolbar = tk.Frame(self.usb_frame, bg="#c0c0c0", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_usb,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="USB device connection history", bg="#c0c0c0",
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=20)
        
        container = tk.Frame(self.usb_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        #scrollbar = tk.Scrollbar(container)
        #scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.usb_text = scrolledtext.ScrolledText(container, bg="white", fg="black",
                                                 font=("Courier New", 9), wrap=tk.NONE)
        self.usb_text.pack(fill=tk.BOTH, expand=True)
    
    def create_search_tab(self):
        """Create global search tab"""
        self.search_frame = tk.Frame(self.tab_content_frame, bg="white")
        
        toolbar = tk.Frame(self.search_frame, bg="#c0c0c0", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Label(toolbar, text="Search:", bg="#c0c0c0",
                font=("MS Sans Serif", 8, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(toolbar, width=40, font=("MS Sans Serif", 9))
        self.search_entry.pack(side=tk.LEFT, padx=2)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())
        
        tk.Button(toolbar, text="Search", command=self.perform_search,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        container = tk.Frame(self.search_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        #scrollbar = tk.Scrollbar(container)
        #scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.search_text = scrolledtext.ScrolledText(container, bg="white", fg="black",
                                                    font=("Courier New", 9), wrap=tk.WORD)
        self.search_text.pack(fill=tk.BOTH, expand=True)
    
    def create_alerts_tab(self):
        """Create alerts tab"""
        self.alerts_frame = tk.Frame(self.tab_content_frame, bg="white")
        
        toolbar = tk.Frame(self.alerts_frame, bg="#c0c0c0", relief=tk.RAISED, bd=1)
        toolbar.pack(fill=tk.X, padx=2, pady=2)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_alerts,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0",
                 font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Label(toolbar, text="System alerts and warnings", bg="#c0c0c0",
                font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=20)
        
        container = tk.Frame(self.alerts_frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        #scrollbar = tk.Scrollbar(container)
        #scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.alerts_text = scrolledtext.ScrolledText(container, bg="white", fg="black",
                                                    font=("Courier New", 9), wrap=tk.WORD)
        self.alerts_text.pack(fill=tk.BOTH, expand=True)
        
        # Tags for severity
        self.alerts_text.tag_config("critical", foreground="#FF0000", font=("Courier New", 9, "bold"))
        self.alerts_text.tag_config("warning", foreground="#FF8000")
        self.alerts_text.tag_config("info", foreground="#0000FF")
    
    def show_tab(self, tab_key):
        """Show selected tab"""
        # Hide all tab contents
        for key in [t[1] for t in self.tab_names]:
            if hasattr(self, f'{key}_frame'):
                getattr(self, f'{key}_frame').pack_forget()
        
        # Reset all button states
        for key, btn in self.tab_buttons.items():
            btn.config(relief=tk.RAISED, bg="#c0c0c0")
        
        # Show selected tab and press button
        self.current_tab = tab_key
        self.tab_buttons[tab_key].config(relief=tk.SUNKEN, bg="#ffffff")
        
        if hasattr(self, f'{tab_key}_frame'):
            getattr(self, f'{tab_key}_frame').pack(fill=tk.BOTH, expand=True)
            
            # Auto-refresh when switching to tab
            if tab_key == "statistics":
                self.refresh_statistics()
            elif tab_key == "timeline":
                self.refresh_timeline()
            elif tab_key == "processes":
                self.refresh_processes()
            elif tab_key == "files":
                self.refresh_files()
            elif tab_key == "network":
                self.refresh_network()
            elif tab_key == "screenshots":
                self.refresh_screenshots()
            elif tab_key == "clipboard":
                self.refresh_clipboard()
            elif tab_key == "usb":
                self.refresh_usb()
            elif tab_key == "alerts":
                self.refresh_alerts()
    
    def generate_report(self):
        """Generate activity report"""
        try:
            timestamp = datetime.now()
            report_file = f"backups/report_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("ACTIVITY TIME MACHINE - SYSTEM REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Process stats
                f.write("\n" + "=" * 80 + "\n")
                f.write("TOP PROCESSES (Last 24 hours)\n")
                f.write("=" * 80 + "\n")
                stats = self.db.get_process_stats(hours=24)
                for proc_name, count, avg_cpu, avg_mem in stats[:20]:
                    f.write(f"{proc_name:<30} Starts: {count:<5} CPU: {avg_cpu:.1f}% RAM: {avg_mem:.1f}MB\n")
                
                # File activity
                f.write("\n" + "=" * 80 + "\n")
                f.write("RECENT FILE ACTIVITY (Last 24 hours)\n")
                f.write("=" * 80 + "\n")
                files = self.db.get_file_activity(hours=24, limit=50)
                for ts, action, path, proc in files:
                    f.write(f"[{ts}] {action}: {path}\n")
                
                # Network
                f.write("\n" + "=" * 80 + "\n")
                f.write("NETWORK CONNECTIONS (Last 24 hours)\n")
                f.write("=" * 80 + "\n")
                conns = self.db.get_network_connections(hours=24, limit=50)
                for ts, ip, port, proc in conns:
                    f.write(f"[{ts}] {ip}:{port}\n")
                
                # Alerts
                f.write("\n" + "=" * 80 + "\n")
                f.write("ALERTS\n")
                f.write("=" * 80 + "\n")
                alerts = self.db.get_alerts(limit=50)
                for ts, atype, severity, msg, details in alerts:
                    f.write(f"[{ts}] {severity} - {atype}: {msg}\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 80 + "\n")
            
            messagebox.showinfo("Report Generated", f"Report saved to:\n{report_file}")
        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to generate report:\n{e}")
    
    def start_monitoring(self):
        """Start monitoring"""
        self.is_monitoring = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Active", fg="#008000")
        
        # Initialize last partitions for USB monitoring
        self.last_partitions = set(p.device for p in psutil.disk_partitions())
        
        # Initialize screenshot timer
        self.last_screenshot_time = time.time()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.status_bar_label.config(text="Monitoring started - Collecting system activity data...")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Stopped", fg="#800000")
        self.status_bar_label.config(text="Monitoring stopped - All data saved to database")
    
    def monitor_loop(self):
        """Main monitoring loop - FIXED: Auto-screenshot now works correctly"""
        last_processes = set()
        last_connections = set()
        resource_counter = 0
        
        while self.is_monitoring:
            timestamp = datetime.now().isoformat()
            current_time = time.time()
            
            try:
                # Auto-screenshot check - FIXED: Now checks time properly
                if self.screenshot_enabled.get():
                    interval_seconds = self.screenshot_interval.get() * 60
                    if current_time - self.last_screenshot_time >= interval_seconds:
                        self.take_screenshot()
                        self.last_screenshot_time = current_time
                
                # Monitor processes
                current_processes = set()
                process_count = 0
                
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                    try:
                        if process_count >= 100:  # Limit
                            break
                        
                        proc_name = proc.info['name']
                        pid = proc.info['pid']
                        current_processes.add((proc_name, pid))
                        process_count += 1
                        
                        # New process
                        if (proc_name, pid) not in last_processes:
                            cpu_percent = proc.info.get('cpu_percent', 0) or 0
                            memory_mb = proc.info.get('memory_info').rss / 1024 / 1024 if proc.info.get('memory_info') else 0
                            
                            self.db.insert_process(timestamp, 'START', proc_name, pid, cpu_percent, memory_mb)
                            
                            # Check for high CPU
                            if cpu_percent > 80:
                                self.db.insert_alert(timestamp, 'HIGH_CPU', 'WARNING',
                                                   f'{proc_name} using {cpu_percent:.1f}% CPU',
                                                   f'PID: {pid}')
                            
                            # File access monitoring (limited)
                            try:
                                if hasattr(proc, 'open_files'):
                                    for file in proc.open_files()[:2]:
                                        file_size = 0
                                        try:
                                            file_size = os.path.getsize(file.path)
                                        except:
                                            pass
                                        self.db.insert_file(timestamp, 'OPEN', file.path, proc_name, pid, file_size)
                            except:
                                pass
                    except:
                        pass
                
                # Detect ended processes
                for proc_name, pid in last_processes - current_processes:
                    self.db.insert_process(timestamp, 'END', proc_name, pid)
                
                last_processes = current_processes
                
                # Monitor network
                try:
                    current_connections = set()
                    for conn in psutil.net_connections(kind='inet'):
                        if conn.status == 'ESTABLISHED' and len(current_connections) < 20:
                            if conn.raddr:
                                conn_id = (conn.laddr.port, conn.raddr.ip, conn.raddr.port)
                                current_connections.add(conn_id)
                                
                                if conn_id not in last_connections:
                                    self.db.insert_network(timestamp, conn.laddr.port,
                                                          conn.raddr.ip, conn.raddr.port,
                                                          conn.status)
                    
                    last_connections = current_connections
                except:
                    pass
                
                # Monitor USB devices
                try:
                    current_partitions = set(p.device for p in psutil.disk_partitions())
                    
                    # New devices
                    for device in current_partitions - self.last_partitions:
                        for part in psutil.disk_partitions():
                            if part.device == device:
                                try:
                                    usage = psutil.disk_usage(part.mountpoint)
                                    self.db.insert_usb_device(timestamp, 'CONNECTED', 
                                                             part.device, part.mountpoint,
                                                             usage.total, usage.used)
                                    self.db.insert_alert(timestamp, 'USB_DEVICE', 'INFO',
                                                       f'USB device connected: {part.device}',
                                                       f'Mount: {part.mountpoint}')
                                except:
                                    pass
                    
                    # Removed devices
                    for device in self.last_partitions - current_partitions:
                        self.db.insert_usb_device(timestamp, 'DISCONNECTED', device, '')
                    
                    self.last_partitions = current_partitions
                except:
                    pass
                
                # Monitor clipboard
                if self.clipboard_enabled.get():
                    try:
                        current_clipboard = pyperclip.paste()
                        if current_clipboard and current_clipboard != self.last_clipboard and len(current_clipboard) < 10000:
                            self.db.insert_clipboard(timestamp, current_clipboard, 'TEXT')
                            self.last_clipboard = current_clipboard
                    except:
                        pass
                
                # System resources (every 5 iterations = ~25 seconds)
                resource_counter += 1
                if resource_counter >= 5:
                    resource_counter = 0
                    try:
                        cpu = psutil.cpu_percent(interval=1)
                        memory = psutil.virtual_memory().percent
                        
                        disk_io = psutil.disk_io_counters()
                        disk_read_mb = (disk_io.read_bytes - self.last_disk_io.read_bytes) / 1024 / 1024
                        disk_write_mb = (disk_io.write_bytes - self.last_disk_io.write_bytes) / 1024 / 1024
                        self.last_disk_io = disk_io
                        
                        net_io = psutil.net_io_counters()
                        net_sent_mb = (net_io.bytes_sent - self.last_net_io.bytes_sent) / 1024 / 1024
                        net_recv_mb = (net_io.bytes_recv - self.last_net_io.bytes_recv) / 1024 / 1024
                        self.last_net_io = net_io
                        
                        self.db.insert_system_resources(timestamp, cpu, memory,
                                                       disk_read_mb, disk_write_mb,
                                                       net_sent_mb, net_recv_mb)
                        
                        # Check for high memory
                        if memory > 90:
                            self.db.insert_alert(timestamp, 'HIGH_MEMORY', 'WARNING',
                                               f'Memory usage at {memory:.1f}%', '')
                    except:
                        pass
                
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(5)
    
    def take_screenshot(self):
        """Take a screenshot"""
        try:
            timestamp = datetime.now()
            filename = timestamp.strftime("%Y%m%d_%H%M%S.png")
            filepath = os.path.join(self.screenshot_dir, filename)
            
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            
            # Get active processes
            active_procs = []
            for proc in psutil.process_iter(['name']):
                try:
                    active_procs.append(proc.info['name'])
                    if len(active_procs) >= 10:
                        break
                except:
                    pass
            
            self.db.insert_screenshot(timestamp.isoformat(), filepath, ','.join(active_procs))
        except Exception as e:
            print(f"Screenshot error: {e}")
    
    def take_screenshot_manual(self):
        """Manual screenshot trigger"""
        self.take_screenshot()
        self.refresh_screenshots()
        messagebox.showinfo("Screenshot", "Screenshot captured successfully")
    
    def open_screenshot_folder(self):
        """Open screenshots folder"""
        import subprocess
        import platform
        
        if platform.system() == 'Windows':
            os.startfile(self.screenshot_dir)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', self.screenshot_dir])
        else:
            subprocess.Popen(['xdg-open', self.screenshot_dir])
    
    def process_queue(self):
        """Process events from queue"""
        # Update event counter
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM processes')
            count = cursor.fetchone()[0]
            conn.close()
            
            if hasattr(self, 'event_count_label'):
                self.event_count_label.config(text=f"Events: {count}")
                
            if self.is_monitoring:
                self.status_bar_label.config(text=f"Monitoring active - {count} events recorded")
        except:
            pass
        
        self.rootactvtmnt.after(2000, self.process_queue)
    
    def refresh_timeline(self):
        """Refresh timeline view"""
        self.timeline_text.config(state=tk.NORMAL)
        self.timeline_text.delete(1.0, tk.END)
        
        events = self.db.get_timeline(limit=100)
        
        for timestamp, event_type, details in events:
            time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
            
            self.timeline_text.insert(tk.END, f"[{time_str}] ")
            
            tag = event_type.lower()
            self.timeline_text.insert(tk.END, f"{event_type}: {details}\n", tag)
        
        self.timeline_text.config(state=tk.DISABLED)
    
    def refresh_processes(self):
        """Refresh processes view"""
        self.processes_text.config(state=tk.NORMAL)
        self.processes_text.delete(1.0, tk.END)
        
        stats = self.db.get_process_stats(hours=24)
        
        self.processes_text.insert(tk.END, "PROCESS STATISTICS (Last 24 hours)\n")
        self.processes_text.insert(tk.END, "=" * 80 + "\n\n")
        self.processes_text.insert(tk.END, f"{'Process':<30} {'Count':<10} {'Avg CPU%':<12} {'Avg Mem MB':<12}\n")
        self.processes_text.insert(tk.END, "-" * 80 + "\n")
        
        for proc_name, count, avg_cpu, avg_mem in stats:
            self.processes_text.insert(tk.END, 
                f"{proc_name[:30]:<30} {count:<10} {avg_cpu:<12.1f} {avg_mem:<12.1f}\n")
        
        self.processes_text.config(state=tk.DISABLED)
    
    def refresh_files(self):
        """Refresh files view"""
        self.files_text.config(state=tk.NORMAL)
        self.files_text.delete(1.0, tk.END)
        
        files = self.db.get_file_activity(hours=24, limit=100)
        
        self.files_text.insert(tk.END, "FILE ACTIVITY (Last 24 hours)\n")
        self.files_text.insert(tk.END, "=" * 80 + "\n\n")
        
        for timestamp, action, file_path, process_name in files:
            time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
            proc = process_name if process_name else "Unknown"
            self.files_text.insert(tk.END, 
                f"[{time_str}] {action}: {file_path} ({proc})\n")
        
        self.files_text.config(state=tk.DISABLED)
    
    def refresh_network(self):
        """Refresh network view"""
        self.network_text.config(state=tk.NORMAL)
        self.network_text.delete(1.0, tk.END)
        
        connections = self.db.get_network_connections(hours=24, limit=100)
        
        self.network_text.insert(tk.END, "NETWORK CONNECTIONS (Last 24 hours)\n")
        self.network_text.insert(tk.END, "=" * 80 + "\n\n")
        
        for timestamp, remote_ip, remote_port, process_name in connections:
            time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
            proc = process_name if process_name else "Unknown"
            self.network_text.insert(tk.END, 
                f"[{time_str}] {remote_ip}:{remote_port} ({proc})\n")
        
        self.network_text.config(state=tk.DISABLED)
    
    def refresh_screenshots(self):
        """Refresh screenshots view"""
        # Clear previous thumbnails
        for widget in self.screenshot_frame.winfo_children():
            widget.destroy()
        
        screenshots = self.db.get_screenshots(limit=50)
        
        if not screenshots:
            # Show empty state
            empty_label = tk.Label(self.screenshot_frame, 
                                  text="No screenshots yet\n\nEnable 'Screenshots' in Control Panel and start monitoring",
                                  bg="#ECF0F1", fg="#7F8C8D",
                                  font=("Segoe UI", 11))
            empty_label.pack(expand=True, pady=50)
            return
        
        row = 0
        col = 0
        max_cols = 3
        
        for timestamp, file_path, active_procs in screenshots:
            if os.path.exists(file_path):
                try:
                    # Create thumbnail
                    img = Image.open(file_path)
                    img.thumbnail((280, 180))
                    photo = ImageTk.PhotoImage(img)
                    
                    # Create frame for each screenshot
                    frame = tk.Frame(self.screenshot_frame, relief=tk.SOLID, bd=1, 
                                   bg="white", cursor="hand2")
                    frame.grid(row=row, column=col, padx=10, pady=10)
                    
                    # Image label
                    img_label = tk.Label(frame, image=photo, bg="white")
                    img_label.image = photo  # Keep reference
                    img_label.pack(padx=2, pady=2)
                    
                    # Timestamp
                    time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
                    date_str = timestamp.split('T')[0] if 'T' in timestamp else ""
                    tk.Label(frame, text=f"{date_str} {time_str}", bg="white", 
                            font=("Segoe UI", 9, "bold")).pack(pady=(2, 5))
                    
                    # Click to open - FIXED: Now opens in custom viewer window
                    img_label.bind('<Button-1>', lambda e, path=file_path: self.open_screenshot_viewer(path))
                    frame.bind('<Button-1>', lambda e, path=file_path: self.open_screenshot_viewer(path))
                    
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Error loading screenshot: {e}")
        
        self.screenshot_frame.update_idletasks()
        self.screenshot_canvas.config(scrollregion=self.screenshot_canvas.bbox("all"))
    
    def open_screenshot_viewer(self, filepath):
        """FIXED: Open screenshot in custom Tkinter viewer window"""
        try:
            # Create new window
            viewer = tk.Toplevel(self.rootactvtmnt)
            viewer.title(f"Screenshot Viewer - {os.path.basename(filepath)}")
            viewer.configure(bg="#000000")
            
            # Get screen dimensions
            screen_width = viewer.winfo_screenwidth()
            screen_height = viewer.winfo_screenheight()
            
            # Load image
            img = Image.open(filepath)
            img_width, img_height = img.size
            
            # Calculate scaling to fit screen (leaving some margin)
            max_width = screen_width - 100
            max_height = screen_height - 100
            
            scale_w = max_width / img_width
            scale_h = max_height / img_height
            scale = min(scale_w, scale_h, 1.0)  # Don't upscale
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img_resized)
            
            # Set window size
            viewer.geometry(f"{new_width + 20}x{new_height + 80}")
            
            # Center window on screen
            x = (screen_width - new_width - 20) // 2
            y = (screen_height - new_height - 80) // 2
            viewer.geometry(f"+{x}+{y}")
            
            # Top info bar
            info_frame = tk.Frame(viewer, bg="#c0c0c0", relief=tk.RAISED, bd=2)
            info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Label(info_frame, text=os.path.basename(filepath), 
                    bg="#c0c0c0", font=("MS Sans Serif", 9, "bold")).pack(side=tk.LEFT, padx=10)
            
            tk.Label(info_frame, text=f"Size: {img_width}x{img_height}", 
                    bg="#c0c0c0", font=("MS Sans Serif", 8)).pack(side=tk.LEFT, padx=10)
            
            tk.Button(info_frame, text="Close", command=viewer.destroy,
                     relief=tk.RAISED, bd=2, bg="#c0c0c0",
                     font=("MS Sans Serif", 8)).pack(side=tk.RIGHT, padx=10)
            
            # Image display
            img_frame = tk.Frame(viewer, bg="#000000")
            img_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            label = tk.Label(img_frame, image=photo, bg="#000000")
            label.image = photo  # Keep reference
            label.pack()
            
            # Keyboard shortcuts
            viewer.bind('<Escape>', lambda e: viewer.destroy())
            viewer.bind('<q>', lambda e: viewer.destroy())
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open screenshot:\n{e}")
    
    def refresh_clipboard(self):
        """Refresh clipboard view"""
        self.clipboard_text.config(state=tk.NORMAL)
        self.clipboard_text.delete(1.0, tk.END)
        
        history = self.db.get_clipboard_history(limit=100)
        
        self.clipboard_text.insert(tk.END, "CLIPBOARD HISTORY\n")
        self.clipboard_text.insert(tk.END, "=" * 80 + "\n\n")
        
        for timestamp, content, content_type in history:
            time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
            preview = content[:100] + "..." if len(content) > 100 else content
            self.clipboard_text.insert(tk.END, f"[{time_str}] {content_type}\n")
            self.clipboard_text.insert(tk.END, f"{preview}\n")
            self.clipboard_text.insert(tk.END, "-" * 80 + "\n")
        
        self.clipboard_text.config(state=tk.DISABLED)
    
    def clear_clipboard_history(self):
        """Clear clipboard history"""
        if messagebox.askyesno("Clear Clipboard History", "Are you sure you want to clear all clipboard history?"):
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM clipboard')
            conn.commit()
            conn.close()
            self.refresh_clipboard()
            messagebox.showinfo("Cleared", "Clipboard history cleared successfully")
    
    def refresh_usb(self):
        """Refresh USB devices view"""
        self.usb_text.config(state=tk.NORMAL)
        self.usb_text.delete(1.0, tk.END)
        
        devices = self.db.get_usb_devices(limit=100)
        
        self.usb_text.insert(tk.END, "USB DEVICE HISTORY\n")
        self.usb_text.insert(tk.END, "=" * 80 + "\n\n")
        
        for timestamp, action, device_name, mount_point, total_size in devices:
            time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
            size_str = f"{total_size / (1024**3):.2f} GB" if total_size else "N/A"
            self.usb_text.insert(tk.END, 
                f"[{time_str}] {action}: {device_name} - {mount_point} ({size_str})\n")
        
        self.usb_text.config(state=tk.DISABLED)
    
    def refresh_statistics(self):
        """Refresh statistics graphs - FIXED: matplotlib warnings resolved"""
        hours = self.stats_timerange.get()
        
        # Clear existing graphs
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        stats = self.db.get_process_stats(hours=hours)
        
        if not stats:
            # Show empty state
            empty_frame = tk.Frame(self.stats_frame, bg="white")
            empty_frame.pack(expand=True, fill=tk.BOTH, pady=50)
            
            tk.Label(empty_frame, 
                    text="No data available yet\n\nStart monitoring to collect statistics",
                    bg="white", fg="#808080",
                    font=("MS Sans Serif", 10)).pack(expand=True)
            
            self.stats_info_label.config(
                text="Start monitoring to begin collecting data for statistics",
                fg="#800000")
            return
        
        self.stats_info_label.config(
            text=f"Showing statistics for the last {hours} hour(s) - {len(stats)} processes tracked",
            fg="#008000")
        
        # Graph 1: Process activity
        self.create_process_stats_graph(hours)
        
        # Graph 2: System resources
        self.create_resource_graph(hours)
        
        # Graph 3: Activity timeline
        self.create_activity_timeline(hours)
        
        self.stats_frame.update_idletasks()
        self.stats_canvas.config(scrollregion=self.stats_canvas.bbox("all"))
    
    def create_process_stats_graph(self, hours):
        """Create process statistics bar chart"""
        stats = self.db.get_process_stats(hours=hours)
        
        if not stats:
            return
        
        # Take top 10
        stats = stats[:10]
        processes = [s[0][:15] for s in stats]
        counts = [s[1] for s in stats]
        
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.barh(processes, counts, color='#4472C4')
        ax.set_xlabel('Number of Starts')
        ax.set_title(f'Top 10 Processes (Last {hours}h)')
        ax.invert_yaxis()
        
        canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=False, pady=10)
    
    def create_resource_graph(self, hours):
        """Create system resources line graph - FIXED: matplotlib warning resolved"""
        resources = self.db.get_system_resources(hours=hours)
        
        if not resources:
            return
        
        timestamps = [r[0].split('T')[1][:5] if 'T' in r[0] else r[0] for r in resources]
        cpu = [r[1] for r in resources]
        memory = [r[2] for r in resources]
        
        # Sample data to reduce number of points
        step = max(1, len(timestamps) // 20)
        sampled_timestamps = timestamps[::step]
        sampled_cpu = cpu[::step]
        sampled_memory = memory[::step]
        
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(range(len(sampled_timestamps)), sampled_cpu, 
               label='CPU %', color='#FF6B6B', linewidth=2)
        ax.plot(range(len(sampled_timestamps)), sampled_memory, 
               label='Memory %', color='#4ECDC4', linewidth=2)
        ax.set_xlabel('Time')
        ax.set_ylabel('Usage %')
        ax.set_title(f'System Resources (Last {hours}h)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # FIXED: Set ticks first, then labels
        tick_positions = list(range(0, len(sampled_timestamps), max(1, len(sampled_timestamps) // 10)))
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([sampled_timestamps[i] for i in tick_positions], rotation=45, ha='right')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=False, pady=10)
    
    def create_activity_timeline(self, hours):
        """Create activity timeline graph"""
        # Get event counts per hour
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute('''
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
            FROM (
                SELECT timestamp FROM processes WHERE timestamp > ?
                UNION ALL
                SELECT timestamp FROM files WHERE timestamp > ?
                UNION ALL
                SELECT timestamp FROM network WHERE timestamp > ?
            )
            GROUP BY hour
            ORDER BY hour
        ''', (since, since, since))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return
        
        hours_list = [r[0] for r in results]
        counts = [r[1] for r in results]
        
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(hours_list, counts, color='#95E1D3')
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Event Count')
        ax.set_title(f'Activity by Hour (Last {hours}h)')
        ax.grid(True, alpha=0.3, axis='y')
        
        canvas = FigureCanvasTkAgg(fig, master=self.stats_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=False, pady=10)
    
    def perform_search(self):
        """Perform global search"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            messagebox.showwarning("Search", "Please enter a search term")
            return
        
        self.search_text.config(state=tk.NORMAL)
        self.search_text.delete(1.0, tk.END)
        
        results = self.db.search_all(search_term, limit=200)
        
        self.search_text.insert(tk.END, f"SEARCH RESULTS FOR: '{search_term}'\n")
        self.search_text.insert(tk.END, "=" * 80 + "\n\n")
        self.search_text.insert(tk.END, f"Found {len(results)} results\n\n")
        
        for timestamp, event_type, details in results:
            time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
            preview = details[:100] + "..." if len(details) > 100 else details
            self.search_text.insert(tk.END, f"[{time_str}] {event_type}: {preview}\n")
        
        self.search_text.config(state=tk.DISABLED)
    
    def refresh_alerts(self):
        """Refresh alerts view"""
        self.alerts_text.config(state=tk.NORMAL)
        self.alerts_text.delete(1.0, tk.END)
        
        alerts = self.db.get_alerts(limit=100)
        
        self.alerts_text.insert(tk.END, "SYSTEM ALERTS\n")
        self.alerts_text.insert(tk.END, "=" * 80 + "\n\n")
        
        for timestamp, alert_type, severity, message, details in alerts:
            time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp
            
            tag = severity.lower()
            self.alerts_text.insert(tk.END, f"[{time_str}] ", tag)
            self.alerts_text.insert(tk.END, f"{severity} - {alert_type}\n", tag)
            self.alerts_text.insert(tk.END, f"{message}\n")
            if details:
                self.alerts_text.insert(tk.END, f"Details: {details}\n")
            self.alerts_text.insert(tk.END, "\n")
        
        self.alerts_text.config(state=tk.DISABLED)
    
    def create_backup(self):
        """Create backup of database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backups/backup_{timestamp}.db"
        
        import shutil
        try:
            shutil.copy2(self.db.db_path, backup_file)
            messagebox.showinfo("Backup", f"Backup created:\n{backup_file}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup:\n{e}")
    
    def cleanup_dialog(self):
        """Show cleanup dialog"""
        dialog = tk.Toplevel(self.rootactvtmnt)
        dialog.title("Cleanup Old Data")
        dialog.geometry("300x150")
        dialog.configure(bg="#c0c0c0")
        
        tk.Label(dialog, text="Delete data older than:", bg="#c0c0c0",
                font=("MS Sans Serif", 9)).pack(pady=10)
        
        days_var = tk.IntVar(value=30)
        
        frame = tk.Frame(dialog, bg="#c0c0c0")
        frame.pack(pady=10)
        
        tk.Entry(frame, textvariable=days_var, width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(frame, text="days", bg="#c0c0c0").pack(side=tk.LEFT)
        
        def do_cleanup():
            if messagebox.askyesno("Confirm", f"Delete all data older than {days_var.get()} days?"):
                self.db.cleanup_old_data(days=days_var.get())
                messagebox.showinfo("Cleanup", "Old data deleted successfully")
                dialog.destroy()
        
        tk.Button(dialog, text="Cleanup", command=do_cleanup,
                 relief=tk.RAISED, bd=2, bg="#c0c0c0").pack(pady=10)


def main():
    rootactvtmnt = tk.Tk()
    app = ActivityTimeMachineV2(rootactvtmnt)
    rootactvtmnt.mainloop()

if __name__ == "__main__":
    main()
