    def _apply_syntax_highlighting(self):
        content = self.query_text.get('1.0', tk.END)
        
        # Skip highlighting for very large content
        if len(content) > 10000:
            return
        
        for tag in ['keyword', 'function', 'string', 'comment', 'number', 'table']:
            self.query_text.tag_remove(tag, '1.0', tk.END)
        
        # Limit highlighting to visible area + buffer for large files
        if len(content) > 5000:
            # Only highlight first 5000 chars
            content = content[:5000]
            end_pos = '1.0+5000c'
        else:
            end_pos = tk.END
        
        # Strings
        for m in re.finditer(r"'[^']*'|\"[^\"]*\"", content):
            self.query_text.tag_add('string', f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        
        # Comments
        for m in re.finditer(r'--[^\n]*|/\*[\s\S]*?\*/', content):
            self.query_text.tag_add('comment', f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        
        # Numbers
        for m in re.finditer(r'\b\d+\.?\d*\b', content):
            self.query_text.tag_add('number', f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        
        # Keywords
        for kw in self.sql_keywords:
            for m in re.finditer(r'\b' + kw + r'\b', content, re.IGNORECASE):
                self.query_text.tag_add('keyword', f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        
        # Functions
        for func in self.sql_functions:
            for m in re.finditer(r'\b' + func + r'\s*\(', content, re.IGNORECASE):
                end = m.end() - 1
                self.query_text.tag_add('function', f"1.0+{m.start()}c", f"1.0+{end}c")
        
        # Tables (from cache)
        for table in self.tables_cache:
            for m in re.finditer(r'\b' + re.escape(table) + r'\b', content, re.IGNORECASE):
                self.query_text.tag_add('table', f"1.0+{m.start()}c", f"1.0+{m.end()}c")
                
    def _update_line_numbers(self):
        line_count = int(self.query_text.index('end-1c').split('.')[0])
        
        # Skip line numbers update for very large files
        # if line_count > 5000:
            # self.line_numbers.config(state=tk.NORMAL)
            # self.line_numbers.delete('1.0', tk.END)
            # self.line_numbers.insert('1.0', "Large file\n(line numbers\ndisabled)")
            # self.line_numbers.config(state=tk.DISABLED)
            # return
    
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        lines = self.query_text.get('1.0', tk.END).count('\n')
        for i in range(1, lines + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        self.line_numbers.config(state=tk.DISABLED)

class SQLManagerStudioPro:
    def __INIT__ etc
      self.highlight_after_id = None


def _on_key_release(self, e=None):
        # Cancel previous scheduled highlight
        if self.highlight_after_id:
            self.root.after_cancel(self.highlight_after_id)
        
        # Schedule new highlight after 300ms of inactivity
        self.highlight_after_id = self.root.after(300, self._apply_syntax_highlighting)
        self._update_line_numbers()

def _paste(self):
        try:
            # Get clipboard content length
            clipboard = self.root.clipboard_get()
            
            if len(clipboard) > 10000:
                # Warn user about large paste
                if not messagebox.askyesno("Large Content", 
                    "Pasting large content will disable syntax highlighting.\nContinue?"):
                    return 'break'
            
            self.query_text.event_generate("<<Paste>>")
            
            # Delay highlighting for large pastes
            if len(clipboard) > 5000:
                self.root.after(1000, self._apply_syntax_highlighting)
            
        except:
            pass
        return 'break'

