import locale
import threading
import tkinter as tk
from datetime import datetime, timezone, timedelta
from tkinter import ttk, messagebox, filedialog

from tkcalendar import DateEntry

from app import __version__
from service.google_form_automation import google_form_automation
from service.programming_diary_generator import ProgrammingDiaryGenerator
from utils.config_manager import load_config, save_config


class CodeDiaryMainWindow:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.diary_generator = ProgrammingDiaryGenerator()

        self.jst = timezone(timedelta(hours=9))
        self._setup_locale()

        self._setup_ui()
        self._setup_bindings()

    def _setup_locale(self):
        try:
            locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_ALL, 'Japanese_Japan.932')
            except locale.Error:
                try:
                    locale.setlocale(locale.LC_ALL, 'ja')
                except locale.Error:
                    print("警告: 日本語ロケールの設定に失敗しました。デフォルトロケールを使用します。")

    def _setup_ui(self):
        self.root.title(f"CodeDiary v{__version__}")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        date_frame = ttk.LabelFrame(main_frame, text="対象期間", padding="5")
        date_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        date_frame.columnconfigure(1, weight=1)
        date_frame.columnconfigure(3, weight=1)

        ttk.Label(date_frame, text="開始日").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

        self.start_date_entry = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy/mm/dd',
            year=datetime.now(self.jst).year,
            month=datetime.now(self.jst).month,
            day=datetime.now(self.jst).day,
            selectbackground='gray80',
            selectforeground='black',
            normalbackground='white',
            normalforeground='black',
            weekendbackground='lightblue',
            weekendforeground='black',
            othermonthbackground='gray90',
            othermonthforeground='gray50',
            othermonthwebackground='gray80',
            othermonthweforeground='gray70',
            selectmode='day',
            cursor='hand1'
        )
        self.start_date_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Label(date_frame, text="終了日").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))

        self.end_date_entry = DateEntry(
            date_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy/mm/dd',  # YYYY/MM/DD形式
            year=datetime.now(self.jst).year,
            month=datetime.now(self.jst).month,
            day=datetime.now(self.jst).day,
            selectbackground='gray80',
            selectforeground='black',
            normalbackground='white',
            normalforeground='black',
            weekendbackground='lightblue',
            weekendforeground='black',
            othermonthbackground='gray90',
            othermonthforeground='gray50',
            othermonthwebackground='gray80',
            othermonthweforeground='gray70',
            selectmode='day',
            cursor='hand1'
        )
        self.end_date_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))

        text_frame = ttk.LabelFrame(main_frame, text="内容", padding="5")
        text_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        text_container = ttk.Frame(text_frame)
        text_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_container.columnconfigure(0, weight=1)
        text_container.rowconfigure(0, weight=1)

        self.diary_text = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=("メイリオ", 10),
            state=tk.DISABLED
        )
        self.diary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.diary_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.diary_text.config(yscrollcommand=scrollbar.set)

        self._set_placeholder_text()

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.create_button = ttk.Button(
            button_frame,
            text="日誌作成",
            command=self._create_diary
        )
        self.create_button.grid(row=0, column=0, padx=(0, 5))

        self.copy_button = ttk.Button(
            button_frame,
            text="コピー",
            command=self._copy_all_text,
            state=tk.DISABLED
        )
        self.copy_button.grid(row=0, column=1, padx=(0, 5))

        self.clear_button = ttk.Button(
            button_frame,
            text="クリア",
            command=self._clear_text
        )
        self.clear_button.grid(row=0, column=2, padx=(0, 5))

        self.repository_button = ttk.Button(
            button_frame,
            text="Gitリポジトリ設定",
            command=self._setup_repository
        )
        self.repository_button.grid(row=0, column=3, padx=(0, 5))

        self.close_button = ttk.Button(
            button_frame,
            text="閉じる",
            command=self.root.quit
        )
        self.close_button.grid(row=0, column=4)

        self.progress_var = tk.StringVar()
        self.progress_var.set("")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

    def _setup_bindings(self):
        self.root.bind('<Return>', lambda e: self._create_diary())
        self.root.bind('<Control-c>', lambda e: self._copy_all_text())
        self.root.bind('<Control-l>', lambda e: self._clear_text())

    def _set_placeholder_text(self):
        self.diary_text.config(state=tk.NORMAL)
        self.diary_text.delete(1.0, tk.END)
        self.diary_text.insert(1.0, "[ここに日誌を出力]")
        self.diary_text.config(state=tk.DISABLED)

    def _validate_dates(self):
        try:
            start_date = self.start_date_entry.get_date()
            end_date = self.end_date_entry.get_date()

            if start_date > end_date:
                messagebox.showerror("エラー", "終了日より前の日付を選択してください。")
                return False

            return True

        except Exception as e:
            messagebox.showerror("エラー", f"日付の取得中にエラーが発生しました: {str(e)}")
            return False

    def _create_diary(self):
        try:
            if not self._validate_dates():
                return

            self._set_buttons_state(False)
            self.progress_var.set("日誌生成中...")

            start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
            end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')

            thread = threading.Thread(
                target=self._generate_diary_thread,
                args=(start_date, end_date)
            )
            thread.daemon = True
            thread.start()

        except Exception as e:
            messagebox.showerror("エラー", f"日誌作成中にエラーが発生しました: {str(e)}")
            self._set_buttons_state(True)
            self.progress_var.set("")

    def _generate_diary_thread(self, start_date, end_date):
        try:
            diary_content, input_tokens, output_tokens = self.diary_generator.generate_diary(
                since_date=start_date,
                until_date=end_date
            )

            self.root.after(0, self._display_diary_result, diary_content, input_tokens, output_tokens)

        except Exception as e:
            self.root.after(0, self._display_error, str(e))

    def _display_diary_result(self, diary_content, input_tokens, output_tokens):
        try:
            self.diary_text.config(state=tk.NORMAL)
            self.diary_text.delete(1.0, tk.END)
            self.diary_text.insert(1.0, diary_content)
            self.diary_text.config(state=tk.DISABLED)

            self.root.clipboard_clear()
            self.root.clipboard_append(diary_content)

            total_tokens = input_tokens + output_tokens
            self.progress_var.set(
                f"日誌生成完了 (文字数: 入力={input_tokens}, 出力={output_tokens}, 合計={total_tokens})")

            self._set_buttons_state(True)
            self.copy_button.config(state=tk.NORMAL)
            self._execute_google_form_automation()

        except Exception as e:
            self._display_error(f"結果表示エラー: {str(e)}")

    def _execute_google_form_automation(self):
        def run_google_form():
            try:
                google_form_automation()
            except Exception as e:
                self.root.after(0, lambda: self.progress_var.set(f"Google Form入力エラー: {str(e)}"))

        thread = threading.Thread(target=run_google_form)
        thread.daemon = True
        thread.start()

    def _display_error(self, error_message):
        messagebox.showerror("エラー", error_message)
        self._set_buttons_state(True)
        self.progress_var.set("")

    def _copy_all_text(self):
        try:
            content = self.diary_text.get(1.0, tk.END).strip()
            if content and content != "[ここに日誌を出力]":
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                messagebox.showinfo("コピー完了", "クリップボードにコピーしました。")
            else:
                messagebox.showwarning("警告", "コピーする内容がありません。")
        except Exception as e:
            messagebox.showerror("エラー", f"コピー中にエラーが発生しました: {str(e)}")

    def _clear_text(self):
        self._set_placeholder_text()
        self.copy_button.config(state=tk.DISABLED)
        self.progress_var.set("")

    def _setup_repository(self):
        try:
            current_path = self.config.get('GIT', 'repository_path', fallback='')
            new_path = filedialog.askdirectory(
                title="Gitリポジトリフォルダを選択",
                initialdir=current_path if current_path else "."
            )

            if new_path:
                if not self.config.has_section('GIT'):
                    self.config.add_section('GIT')
                self.config.set('GIT', 'repository_path', new_path)

                save_config(self.config)

                self.diary_generator = ProgrammingDiaryGenerator()

                messagebox.showinfo("設定完了", f"リポジトリパスを更新しました:\n{new_path}")

        except Exception as e:
            messagebox.showerror("エラー", f"リポジトリ設定中にエラーが発生しました: {str(e)}")

    def _set_buttons_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.create_button.config(state=state)
        self.clear_button.config(state=state)
        self.repository_button.config(state=state)
        self.close_button.config(state=state)
