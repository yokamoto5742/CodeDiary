import tkinter as tk
from tkinter import ttk


class DiaryContentWidget(ttk.LabelFrame):
    
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, text="日誌内容", padding="5", **kwargs)
        self.config = config
        self.placeholder_text = "[ここに日誌を出力]"
        
        self._setup_ui()
        
    def _setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        text_container = ttk.Frame(self)
        text_container.grid(row=0, column=0, sticky="wens")
        text_container.columnconfigure(0, weight=1)
        text_container.rowconfigure(0, weight=1)

        font_name = self.config.get('DiaryText', 'font', fallback='メイリオ')
        font_size = self.config.getint('DiaryText', 'font_size', fallback=11)
        
        # テキストウィジェット
        self.diary_text = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=(font_name, font_size),
            state=tk.NORMAL
        )
        self.diary_text.grid(row=0, column=0, sticky="wens")

        scrollbar = ttk.Scrollbar(
            text_container, 
            orient=tk.VERTICAL, 
            command=self.diary_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.diary_text.config(yscrollcommand=scrollbar.set)

        self.set_placeholder_text()
        
    def set_placeholder_text(self):
        self.diary_text.delete(1.0, tk.END)
        self.diary_text.insert(1.0, self.placeholder_text)
        
    def set_content(self, content):
        self.diary_text.delete(1.0, tk.END)
        self.diary_text.insert(1.0, content)
        
    def get_content(self):
        return self.diary_text.get(1.0, tk.END).strip()
        
    def has_content(self):
        content = self.get_content()
        return content and content != self.placeholder_text
        
    def clear_content(self):
        self.set_placeholder_text()
