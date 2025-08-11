import time
import tkinter as tk
from tkinter import ttk


class ProgressWidget(ttk.Label):

    def __init__(self, parent, **kwargs):
        self.progress_var = tk.StringVar()
        self.progress_var.set("")

        super().__init__(parent, textvariable=self.progress_var, **kwargs)

        self.start_time = None
        self.timer_after_id = None

    def set_message(self, message: str):
        self.progress_var.set(message)

    def clear_message(self):
        self.progress_var.set("")
        self._stop_timer()

    def set_processing_message(self):
        self.start_time = time.time()
        self._start_timer()

    def _start_timer(self):
        self._update_elapsed_time()

    def _stop_timer(self):
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None

    def _update_elapsed_time(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.set_message(f"日誌生成中... {elapsed}秒経過")

            self.timer_after_id = self.after(1000, self._update_elapsed_time)

    def set_completion_message(self, input_tokens: int, output_tokens: int):
        self._stop_timer()

        if self.start_time:
            total_elapsed = int(time.time() - self.start_time)
            elapsed_str = f"{total_elapsed}秒"
        else:
            elapsed_str = "不明"

        total_tokens = input_tokens + output_tokens
        message = (
            f"日誌生成完了 処理時間: {elapsed_str}, 文字数: 入力={input_tokens}, "
            f"出力={output_tokens}, 合計={total_tokens}"
        )
        self.set_message(message)

    def set_error_message(self, error_message: str):
        self._stop_timer()
        self.set_message(f"Google Form入力エラー: {error_message}")
