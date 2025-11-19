"""進捗表示ウィジェット"""

import time
import tkinter as tk
from tkinter import ttk
from typing import Optional


class ProgressWidget(ttk.Label):
    """処理進捗とメッセージを表示するラベルウィジェット"""

    def __init__(self, parent, **kwargs):
        self.progress_var = tk.StringVar()
        self.progress_var.set("")

        super().__init__(parent, textvariable=self.progress_var, **kwargs)

        self.start_time: Optional[float] = None
        self.timer_after_id: Optional[str] = None

    def set_message(self, message: str):
        """メッセージを設定して表示"""
        self.progress_var.set(message)

    def clear_message(self):
        """メッセージをクリアしタイマーを停止"""
        self.progress_var.set("")
        self._stop_timer()

    def set_processing_message(self):
        """処理開始メッセージを設定。タイマーで経過時間を更新"""
        self.start_time = time.time()
        self._start_timer()

    def _start_timer(self):
        """経過時間表示タイマーを開始"""
        self._update_elapsed_time()

    def _stop_timer(self):
        """経過時間表示タイマーをキャンセル"""
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None

    def _update_elapsed_time(self):
        """経過時間を1秒ごとに更新"""
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.set_message(f"日誌生成中... {elapsed}秒経過")

            self.timer_after_id = self.after(1000, self._update_elapsed_time)

    def set_completion_message(self, input_tokens: int, output_tokens: int, model_name: Optional[str] = None):
        """完了メッセージを表示。処理時間とトークン数を含める"""
        self._stop_timer()

        if self.start_time:
            total_elapsed = int(time.time() - self.start_time)
            elapsed_str = f"{total_elapsed}秒"
        else:
            elapsed_str = "不明"

        total_tokens = input_tokens + output_tokens
        model_info = f", モデル={model_name}" if model_name else ""

        message = (
            f"日誌生成完了 処理時間: {elapsed_str}, 文字数: 入力={input_tokens}, "
            f"出力={output_tokens}, 合計={total_tokens}{model_info}"
        )
        self.set_message(message)

    def set_error_message(self, error_message: str):
        """エラーメッセージを表示"""
        self._stop_timer()
        self.set_message(f"Google Form入力エラー: {error_message}")

    def start_progress(self, message: str):
        """プログレスメッセージを表示し、経過時間計測を開始"""
        self.set_message(message)
        self.start_time = time.time()
        self._start_timer()

    def stop_progress(self):
        """プログレスメッセージを停止しクリア"""
        self._stop_timer()
        self.clear_message()
