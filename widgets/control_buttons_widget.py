import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class ControlButtonsWidget(ttk.Frame):
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.create_diary_callback: Optional[Callable] = None
        self.create_github_diary_callback: Optional[Callable] = None
        self.copy_text_callback: Optional[Callable] = None
        self.clear_text_callback: Optional[Callable] = None
        self.setup_repository_callback: Optional[Callable] = None
        self.close_callback: Optional[Callable] = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        self.create_button = ttk.Button(
            self,
            text="ローカルで作成",
            command=self._on_create_diary
        )
        self.create_button.grid(row=0, column=0, padx=(0, 5))

        self.github_button = ttk.Button(
            self,
            text="GitHubで作成",
            command=self._on_create_github_diary
        )
        self.github_button.grid(row=0, column=1, padx=(0, 5))

        self.copy_button = ttk.Button(
            self,
            text="コピー",
            command=self._on_copy_text,
            state=tk.DISABLED
        )
        self.copy_button.grid(row=0, column=2, padx=(0, 5))

        self.clear_button = ttk.Button(
            self,
            text="クリア",
            command=self._on_clear_text
        )
        self.clear_button.grid(row=0, column=3, padx=(0, 5))

        self.repository_button = ttk.Button(
            self,
            text="Gitリポジトリ設定",
            command=self._on_setup_repository
        )
        self.repository_button.grid(row=0, column=4, padx=(0, 5))

        self.close_button = ttk.Button(
            self,
            text="閉じる",
            command=self._on_close
        )
        self.close_button.grid(row=0, column=5)
        
    def set_callbacks(self,
                     create_diary: Optional[Callable] = None,
                     create_github_diary: Optional[Callable] = None,
                     copy_text: Optional[Callable] = None,
                     clear_text: Optional[Callable] = None,
                     setup_repository: Optional[Callable] = None,
                     close: Optional[Callable] = None):
        if create_diary:
            self.create_diary_callback = create_diary
        if create_github_diary:
            self.create_github_diary_callback = create_github_diary
        if copy_text:
            self.copy_text_callback = copy_text
        if clear_text:
            self.clear_text_callback = clear_text
        if setup_repository:
            self.setup_repository_callback = setup_repository
        if close:
            self.close_callback = close
            
    def _on_create_diary(self):
        if self.create_diary_callback:
            self.create_diary_callback()

    def _on_create_github_diary(self):
        if self.create_github_diary_callback:
            self.create_github_diary_callback()
            
    def _on_copy_text(self):
        if self.copy_text_callback:
            self.copy_text_callback()
            
    def _on_clear_text(self):
        if self.clear_text_callback:
            self.clear_text_callback()
            
    def _on_setup_repository(self):
        if self.setup_repository_callback:
            self.setup_repository_callback()
            
    def _on_close(self):
        if self.close_callback:
            self.close_callback()
            
    def set_buttons_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.create_button.config(state=state)
        self.clear_button.config(state=state)
        self.repository_button.config(state=state)
        self.close_button.config(state=state)
        
    def set_copy_button_state(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.copy_button.config(state=state)
