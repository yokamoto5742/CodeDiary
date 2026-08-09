import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class ControlButtonsWidget(ttk.Frame):
    """日誌生成や操作を行うボタン群を配置するウィジェット"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.create_github_diary_callback: Optional[Callable] = None
        self.close_callback: Optional[Callable] = None

        self._setup_ui()

    def _setup_ui(self):
        """操作ボタンを縦に並べて配置"""
        self.github_button = ttk.Button(
            self,
            text="GitHubで作成",
            command=self._on_create_github_diary
        )
        self.github_button.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        self.close_button = ttk.Button(
            self,
            text="閉じる",
            command=self._on_close
        )
        self.close_button.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

    def set_callbacks(self,
                     create_github_diary: Optional[Callable] = None,
                     close: Optional[Callable] = None):
        """各ボタンのコールバック関数を設定"""
        if create_github_diary:
            self.create_github_diary_callback = create_github_diary
        if close:
            self.close_callback = close

    def _on_create_github_diary(self):
        """GitHub連携で日誌作成ボタンのクリック処理"""
        if self.create_github_diary_callback:
            self.create_github_diary_callback()

    def _on_close(self):
        """閉じるボタンのクリック処理"""
        if self.close_callback:
            self.close_callback()

    def set_buttons_state(self, enabled: bool):
        """操作ボタンの有効/無効を切り替え"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.github_button.config(state=state)
        self.close_button.config(state=state)
