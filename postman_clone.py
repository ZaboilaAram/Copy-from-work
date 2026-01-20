import tkinter as tk
from tkinter import scrolledtext, messagebox
import json
import urllib.request
import urllib.parse
import urllib.error
from PIL import Image, ImageTk
import io

class PostmanClone:
    def __init__(self, rootAPIPOSTMAN):
        self.rootAPIPOSTMAN = rootAPIPOSTMAN
        self.rootAPIPOSTMAN.title("API Check Results")
        self.rootAPIPOSTMAN.geometry("800x600")
        
        # Windows 95 color scheme
        self.bg_color = "#c0c0c0"
        self.button_color = "#c0c0c0"
        self.text_bg = "#ffffff"
        self.border_color = "#808080"
        
        self.rootAPIPOSTMAN.configure(bg=self.bg_color)
        
        # Image reference
        self.current_image = None
        
        # Configure styles
        self.setup_ui()
    
    def _on_mousewheel(self, event):
        # Windows and MacOS
        if event.num == 4 or event.delta > 0:
            self.preview_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.preview_canvas.yview_scroll(1, "units")
            
    def setup_ui(self):
        # Top frame for URL and method
        top_frame = tk.Frame(self.rootAPIPOSTMAN, bg=self.bg_color, relief=tk.RIDGE, bd=2)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Method dropdown
        tk.Label(top_frame, text="Method:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).grid(row=0, column=0, padx=5, pady=5)
        
        self.method_var = tk.StringVar(value="GET")
        method_menu = tk.OptionMenu(top_frame, self.method_var, 
                                    "GET", "POST", "PUT", "DELETE", "PATCH")
        method_menu.config(bg=self.button_color, font=("MS Sans Serif", 8), 
                          relief=tk.RAISED, bd=2, width=8)
        method_menu.grid(row=0, column=1, padx=5, pady=5)
        
        # URL entry
        tk.Label(top_frame, text="URL:", bg=self.bg_color, 
                font=("MS Sans Serif", 8)).grid(row=0, column=2, padx=5, pady=5)
        
        self.url_entry = tk.Entry(top_frame, font=("MS Sans Serif", 8), 
                                 relief=tk.SUNKEN, bd=2)
        self.url_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.url_entry.insert(0, "http://localhost:8000/api/test")
        
        # Send button
        send_btn = tk.Button(top_frame, text="Send", command=self.send_request,
                           bg=self.button_color, font=("MS Sans Serif", 8, "bold"),
                           relief=tk.RAISED, bd=2, width=10)
        send_btn.grid(row=0, column=4, padx=5, pady=5)
        
        top_frame.columnconfigure(3, weight=1)
        
        # Notebook-like tabs for request sections
        tabs_frame = tk.Frame(self.rootAPIPOSTMAN, bg=self.bg_color, relief=tk.RIDGE, bd=2)
        tabs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab buttons
        button_frame = tk.Frame(tabs_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, padx=2, pady=2)
        
        self.current_tab = "headers"
        
        self.headers_btn = tk.Button(button_frame, text="Headers", 
                                     command=lambda: self.switch_tab("headers"),
                                     bg=self.button_color, font=("MS Sans Serif", 8),
                                     relief=tk.SUNKEN, bd=2, width=12)
        self.headers_btn.pack(side=tk.LEFT, padx=2)
        
        self.body_btn = tk.Button(button_frame, text="Body", 
                                 command=lambda: self.switch_tab("body"),
                                 bg=self.button_color, font=("MS Sans Serif", 8),
                                 relief=tk.RAISED, bd=2, width=12)
        self.body_btn.pack(side=tk.LEFT, padx=2)
        
        # Content frame for tabs
        self.content_frame = tk.Frame(tabs_frame, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Headers tab
        self.headers_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        
        tk.Label(self.headers_frame, text="Request Headers (JSON format):", 
                bg=self.bg_color, font=("MS Sans Serif", 8)).pack(anchor="w", padx=5, pady=5)
        
        self.headers_text = scrolledtext.ScrolledText(self.headers_frame, 
                                                     height=8, 
                                                     font=("Courier New", 9),
                                                     relief=tk.SUNKEN, bd=2,
                                                     bg=self.text_bg)
        self.headers_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.headers_text.insert("1.0", '{\n  "Content-Type": "application/json"\n}')
        
        # Body tab
        self.body_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        
        tk.Label(self.body_frame, text="Request Body (JSON format):", 
                bg=self.bg_color, font=("MS Sans Serif", 8)).pack(anchor="w", padx=5, pady=5)
        
        self.body_text = scrolledtext.ScrolledText(self.body_frame, 
                                                  height=8, 
                                                  font=("Courier New", 9),
                                                  relief=tk.SUNKEN, bd=2,
                                                  bg=self.text_bg)
        self.body_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.body_text.insert("1.0", '{\n  "title": "Test",\n  "body": "Test body",\n  "userId": 1\n}')
        
        # Show initial tab
        self.headers_frame.pack(fill=tk.BOTH, expand=True)
        
        # Response section
        response_frame = tk.Frame(self.rootAPIPOSTMAN, bg=self.bg_color, relief=tk.RIDGE, bd=2)
        response_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(response_frame, text="Response:", bg=self.bg_color, 
                font=("MS Sans Serif", 8, "bold")).pack(anchor="w", padx=5, pady=5)
        
        # Status label
        self.status_label = tk.Label(response_frame, text="Status: Ready", 
                                    bg=self.bg_color, font=("MS Sans Serif", 8),
                                    anchor="w")
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
        
        # Response tabs
        response_tabs_frame = tk.Frame(response_frame, bg=self.bg_color)
        response_tabs_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.response_text_btn = tk.Button(response_tabs_frame, text="Response", 
                                          command=lambda: self.switch_response_tab("text"),
                                          bg=self.button_color, font=("MS Sans Serif", 8),
                                          relief=tk.SUNKEN, bd=2, width=12)
        self.response_text_btn.pack(side=tk.LEFT, padx=2)
        
        self.response_preview_btn = tk.Button(response_tabs_frame, text="Preview", 
                                             command=lambda: self.switch_response_tab("preview"),
                                             bg=self.button_color, font=("MS Sans Serif", 8),
                                             relief=tk.RAISED, bd=2, width=12)
        self.response_preview_btn.pack(side=tk.LEFT, padx=2)
        
        # Response content frame
        self.response_content_frame = tk.Frame(response_frame, bg=self.bg_color)
        self.response_content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text response frame
        self.response_text_frame = tk.Frame(self.response_content_frame, bg=self.bg_color)
        
        self.response_text = scrolledtext.ScrolledText(self.response_text_frame, 
                                                      height=10, 
                                                      font=("Courier New", 9),
                                                      relief=tk.SUNKEN, bd=2,
                                                      bg=self.text_bg,
                                                      state=tk.DISABLED)
        self.response_text.pack(fill=tk.BOTH, expand=True)
        
        # Preview frame
        self.response_preview_frame = tk.Frame(self.response_content_frame, bg=self.bg_color)
        
        preview_scroll = tk.Scrollbar(self.response_preview_frame)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.preview_canvas = tk.Canvas(self.response_preview_frame, 
                                       bg=self.text_bg,
                                       relief=tk.SUNKEN, bd=2,
                                       yscrollcommand=preview_scroll.set)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        preview_scroll.config(command=self.preview_canvas.yview)
        
        # Bind mousewheel for scrolling
        self.preview_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.preview_canvas.bind("<Button-4>", self._on_mousewheel)
        self.preview_canvas.bind("<Button-5>", self._on_mousewheel)
        
        self.preview_label = tk.Label(self.response_preview_frame, 
                                     text="No preview available",
                                     bg=self.text_bg,
                                     font=("MS Sans Serif", 8))
        
        # Show text frame by default
        self.response_text_frame.pack(fill=tk.BOTH, expand=True)
        self.current_response_tab = "text"
        
        # Bottom status bar
        status_bar = tk.Frame(self.rootAPIPOSTMAN, bg=self.border_color, relief=tk.SUNKEN, bd=1)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_text = tk.Label(status_bar, text="Ready", bg=self.bg_color, 
                                   font=("MS Sans Serif", 8), anchor="w")
        self.status_text.pack(fill=tk.X, padx=2, pady=1)
        
    def switch_tab(self, tab_name):
        # Update button states
        if tab_name == "headers":
            self.headers_btn.config(relief=tk.SUNKEN)
            self.body_btn.config(relief=tk.RAISED)
            self.body_frame.pack_forget()
            self.headers_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.headers_btn.config(relief=tk.RAISED)
            self.body_btn.config(relief=tk.SUNKEN)
            self.headers_frame.pack_forget()
            self.body_frame.pack(fill=tk.BOTH, expand=True)
        
        self.current_tab = tab_name
    
    def switch_response_tab(self, tab_name):
        # Update button states
        if tab_name == "text":
            self.response_text_btn.config(relief=tk.SUNKEN)
            self.response_preview_btn.config(relief=tk.RAISED)
            self.response_preview_frame.pack_forget()
            self.response_text_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.response_text_btn.config(relief=tk.RAISED)
            self.response_preview_btn.config(relief=tk.SUNKEN)
            self.response_text_frame.pack_forget()
            self.response_preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.current_response_tab = tab_name
    
    def send_request(self):
        url = self.url_entry.get().strip()
        method = self.method_var.get()
        
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        # Clear previous response
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete("1.0", tk.END)
        self.response_text.config(state=tk.DISABLED)
        
        # Clear preview
        self.preview_canvas.delete("all")
        self.preview_label.place_forget()
        
        self.status_label.config(text="Status: Sending request...")
        self.status_text.config(text="Sending request...")
        self.rootAPIPOSTMAN.update()
        
        try:
            # Parse headers
            headers_str = self.headers_text.get("1.0", tk.END).strip()
            headers = {}
            if headers_str:
                try:
                    headers = json.loads(headers_str)
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Invalid JSON in headers")
                    self.status_label.config(text="Status: Error - Invalid headers")
                    self.status_text.config(text="Ready")
                    return
            
            # Parse body
            body_str = self.body_text.get("1.0", tk.END).strip()
            data = None
            if method in ["POST", "PUT", "PATCH"] and body_str:
                try:
                    body_data = json.loads(body_str)
                    data = json.dumps(body_data).encode('utf-8')
                    if 'Content-Type' not in headers:
                        headers['Content-Type'] = 'application/json'
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Invalid JSON in body")
                    self.status_label.config(text="Status: Error - Invalid body")
                    self.status_text.config(text="Ready")
                    return
            
            # Create request
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            
            # Send request
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.status
                response_headers = dict(response.headers)
                response_body_bytes = response.read()
                
                content_type = response_headers.get('Content-Type', '').lower()
                
                # Format response text
                result = f"Status Code: {status_code}\n\n"
                result += "Response Headers:\n"
                result += json.dumps(response_headers, indent=2)
                result += "\n\nResponse Body:\n"
                
                # Check if it's an image
                is_image = False
                if 'image/' in content_type:
                    is_image = True
                    result += f"[Image data - {len(response_body_bytes)} bytes]\n"
                    result += f"Content-Type: {content_type}"
                    
                    # Try to display image in preview
                    try:
                        image = Image.open(io.BytesIO(response_body_bytes))
                        
                        # Resize if too large
                        max_width = 600
                        max_height = 400
                        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                        
                        photo = ImageTk.PhotoImage(image)
                        
                        # Store reference to prevent garbage collection
                        self.current_image = photo
                        
                        # Display on canvas
                        self.preview_canvas.delete("all")
                        canvas_width = self.preview_canvas.winfo_width()
                        if canvas_width <= 1:
                            canvas_width = 600
                        
                        x = canvas_width // 2
                        self.preview_canvas.create_image(x, 10, anchor=tk.N, image=photo)
                        self.preview_canvas.config(scrollregion=self.preview_canvas.bbox("all"))
                        
                    except Exception as img_error:
                        # If image preview fails, show error in preview
                        self.preview_label.config(text=f"Failed to load image: {str(img_error)}")
                        self.preview_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                else:
                    # Try to decode as text
                    try:
                        response_body = response_body_bytes.decode('utf-8')
                        try:
                            # Try to format as JSON
                            json_body = json.loads(response_body)
                            result += json.dumps(json_body, indent=2)
                        except:
                            # Not JSON, display as-is
                            result += response_body
                    except UnicodeDecodeError:
                        result += f"[Binary data - {len(response_body_bytes)} bytes]"
                    
                    # Show "no preview" message
                    self.preview_label.config(text="No preview available for this content type")
                    self.preview_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
                
                # Update response text (make it editable temporarily to insert text)
                self.response_text.config(state=tk.NORMAL)
                self.response_text.delete("1.0", tk.END)
                self.response_text.insert("1.0", result)
                self.response_text.config(state=tk.DISABLED)
                
                self.status_label.config(text=f"Status: {status_code} OK")
                self.status_text.config(text=f"Request completed - {status_code}")
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='ignore')
            result = f"Status Code: {e.code}\n\n"
            result += f"Error: {e.reason}\n\n"
            result += f"Response Body:\n{error_body}"
            
            self.response_text.config(state=tk.NORMAL)
            self.response_text.delete("1.0", tk.END)
            self.response_text.insert("1.0", result)
            self.response_text.config(state=tk.DISABLED)
            
            self.status_label.config(text=f"Status: {e.code} Error")
            self.status_text.config(text=f"Request failed - {e.code}")
            
            # Show error in preview
            self.preview_label.config(text=f"Error: {e.code} - {e.reason}")
            self.preview_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
        except urllib.error.URLError as e:
            messagebox.showerror("Error", f"URL Error: {str(e.reason)}")
            self.status_label.config(text="Status: Connection Error")
            self.status_text.config(text="Ready")
            
            self.preview_label.config(text="Connection Error")
            self.preview_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="Status: Error")
            self.status_text.config(text="Ready")
            
            self.preview_label.config(text=f"Error: {str(e)}")
            self.preview_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

def main():
    rootAPIPOSTMAN = tk.Tk()
    app = PostmanClone(rootAPIPOSTMAN)
    rootAPIPOSTMAN.mainloop()

if __name__ == "__main__":
    main()
