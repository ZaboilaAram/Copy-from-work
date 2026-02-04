def _on_scroll(self, *args, scrollbar):
    scrollbar.set(*args)
    self.line_numbers.yview_moveto(args[0])

def _sync_scroll(self, *args):
    self.query_text.yview(*args)
    self.line_numbers.yview(*args)

def _update_line_numbers(self):
    line_count = int(self.query_text.index('end-1c').split('.')[0])
    
    self.line_numbers.config(state=tk.NORMAL)
    self.line_numbers.delete('1.0', tk.END)
    lines = self.query_text.get('1.0', tk.END).count('\n')
    for i in range(1, lines + 1):
        self.line_numbers.insert(tk.END, f"{i}\n")
    self.line_numbers.config(state=tk.DISABLED)
    
    # ADAUGĂ ACEASTĂ LINIE - sincronizează scroll-ul după update
    self.line_numbers.yview_moveto(self.query_text.yview()[0])

def _select_tab(self, tab_id):
    if self.active_tab_id and self.active_tab_id in self.query_tabs:
        # Save current content
        self.query_tabs[self.active_tab_id].content = self.query_text.get('1.0', tk.END)
        self.query_tabs[self.active_tab_id].set_active(False)
    
    self.active_tab_id = tab_id
    tab = self.query_tabs[tab_id]
    tab.set_active(True)
    
    # Load content
    self.query_text.delete('1.0', tk.END)
    self.query_text.insert('1.0', tab.content)
    self._apply_syntax_highlighting()
    self._update_line_numbers()
    
    # ADAUGĂ ACESTE LINII - forțează sincronizarea
    self.query_text.update_idletasks()
    self.line_numbers.yview_moveto(self.query_text.yview()[0])
