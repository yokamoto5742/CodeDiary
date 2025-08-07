import tkinter as tk
from tkinter import ttk


class DiaryContentWidget(ttk.LabelFrame):
    """日誌内容表示ウィジェット"""
    
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, text="日誌内容", padding="5", **kwargs)
        self.config = config
        self.placeholder_text = "[ここに日誌を出力]"
        
        self._setup_ui()
        
    def _setup_ui(self):
        """UIコンポーネントを設定"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # テキスト表示コンテナ
        text_container = ttk.Frame(self)
        text_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_container.columnconfigure(0, weight=1)
        text_container.rowconfigure(0, weight=1)
        
        # フォント設定を取得
        font_name = self.config.get('DiaryText', 'font', fallback='メイリオ')
        font_size = self.config.getint('DiaryText', 'font_size', fallback=10)
        
        # テキストウィジェット
        self.diary_text = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=(font_name, font_size),
            state=tk.NORMAL
        )
        self.diary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(
            text_container, 
            orient=tk.VERTICAL, 
            command=self.diary_text.yview
        )
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.diary_text.config(yscrollcommand=scrollbar.set)
        
        # プレースホルダーテキストを設定
        self.set_placeholder_text()
        
    def set_placeholder_text(self):
        """プレースホルダーテキストを設定"""
        self.diary_text.delete(1.0, tk.END)
        self.diary_text.insert(1.0, self.placeholder_text)
        
    def set_content(self, content):
        """テキスト内容を設定"""
        self.diary_text.delete(1.0, tk.END)
        self.diary_text.insert(1.0, content)
        
    def get_content(self):
        """テキスト内容を取得"""
        return self.diary_text.get(1.0, tk.END).strip()
        
    def has_content(self):
        """有効な内容があるかチェック"""
        content = self.get_content()
        return content and content != self.placeholder_text
        
    def clear_content(self):
        """内容をクリア"""
        self.set_placeholder_text()
