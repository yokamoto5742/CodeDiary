import locale
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk

from app import __version__
from service.google_form_automation import GoogleFormAutomation
from service.programming_diary_generator import ProgrammingDiaryGenerator
from utils.config_manager import load_config, save_config
from widgets import (
    ControlButtonsWidget,
    DateSelectionWidget,
    DiaryContentWidget,
    ProgressWidget
)


class CodeDiaryMainWindow:

    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.diary_generator = ProgrammingDiaryGenerator()

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
        window_width = self.config.get('WindowSettings', 'window_width', fallback='600')
        window_height = self.config.get('WindowSettings', 'window_height', fallback='600')

        self.root.title(f"CodeDiary v{__version__}")
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(True, True)

        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        self.date_selection_widget = DateSelectionWidget(
            main_frame,
            self.config
        )
        self.date_selection_widget.grid(
            row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10)
        )

        self.progress_widget = ProgressWidget(main_frame)
        self.progress_widget.grid(
            row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5)
        )

        self.diary_content_widget = DiaryContentWidget(
            main_frame,
            self.config
        )
        self.diary_content_widget.grid(
            row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10)
        )

        self.control_buttons_widget = ControlButtonsWidget(main_frame)
        self.control_buttons_widget.grid(
            row=3, column=0, sticky=(tk.W, tk.E)
        )

        self.control_buttons_widget.set_callbacks(
            create_diary=self._create_diary,
            create_github_diary=self._create_github_diary,
            copy_text=self._copy_all_text,
            clear_text=self._clear_text,
            setup_repository=self._setup_repository,
            close=self.root.quit
        )

    def _setup_bindings(self):
        self.root.bind('<Return>', lambda e: self._create_diary())
        self.root.bind('<Control-c>', lambda e: self._copy_all_text())
        self.root.bind('<Control-l>', lambda e: self._clear_text())

    def _validate_dates(self, since_date=None, until_date=None):
        if since_date is not None and until_date is not None:
            # GitHub連携用の日付検証
            if since_date > until_date:
                messagebox.showerror("エラー", "終了日より前の日付を選択してください。")
                return False
            return True
        else:
            # 通常の日付検証
            is_valid, error_message = self.date_selection_widget.validate_dates()
            if not is_valid:
                messagebox.showerror("エラー", error_message)
            return is_valid

    def _create_diary(self):
        try:
            if not self._validate_dates():
                return

            self._set_buttons_state(False)
            self.progress_widget.set_processing_message()

            start_date = self.date_selection_widget.get_start_date().strftime('%Y-%m-%d')
            end_date = self.date_selection_widget.get_end_date().strftime('%Y-%m-%d')

            thread = threading.Thread(
                target=self._generate_diary_thread,
                args=(start_date, end_date)
            )
            thread.daemon = True
            thread.start()

        except Exception as e:
            messagebox.showerror("エラー", f"日誌作成中にエラーが発生しました: {str(e)}")
            self._set_buttons_state(True)
            self.progress_widget.clear_message()

    def _create_github_diary(self):
        """GitHub連携で日記を作成"""
        try:
            # GitHub設定をチェック
            github_enabled = self.config.getboolean('GITHUB', 'enable_cross_repo_tracking', fallback=False)
            if not github_enabled:
                messagebox.showwarning(
                    "GitHub連携無効", 
                    "GitHub連携が無効になっています。\nutils/config.iniでenable_cross_repo_tracking=trueに設定してください。"
                )
                return
                
            # GitHub認証情報をチェック
            import os
            if not os.getenv('GITHUB_TOKEN') or not os.getenv('GITHUB_USERNAME'):
                messagebox.showerror(
                    "GitHub設定エラー", 
                    "GitHub認証情報が設定されていません。\n\n"
                    "以下の環境変数を設定してください：\n"
                    "• GITHUB_TOKEN: Personal Access Token\n"
                    "• GITHUB_USERNAME: GitHubユーザー名\n\n"
                    "PowerShellでの設定例：\n"
                    '$env:GITHUB_TOKEN = "your_token_here"\n'
                    '$env:GITHUB_USERNAME = "your_username_here"'
                )
                return

            since_date, until_date = self.date_selection_widget.get_selected_dates()
            if not self._validate_dates(since_date, until_date):
                return

            self._set_buttons_state(tk.DISABLED)
            self.progress_widget.start_progress("GitHub連携で日記を生成中...")

            # GitHub用の別スレッドで実行
            thread = threading.Thread(
                target=self._generate_github_diary_thread, 
                args=(since_date, until_date),
                daemon=True
            )
            thread.start()

        except Exception as e:
            messagebox.showerror("エラー", f"GitHub連携日記の作成でエラーが発生しました:\n{str(e)}")
            self._set_buttons_state(tk.NORMAL)
            self.progress_widget.stop_progress()

    def _generate_github_diary_thread(self, since_date, until_date):
        """GitHub日記生成用スレッド"""
        try:
            diary_content, input_tokens, output_tokens, model_name = self.diary_generator.generate_diary(
                since_date=since_date,
                until_date=until_date,
                use_github=True
            )
            self.root.after(0, self._display_diary_result, diary_content, input_tokens, output_tokens, model_name)
        except Exception as e:
            self.root.after(0, self._schedule_error_display, str(e))

    def _generate_diary_thread(self, start_date, end_date):
        try:
            diary_content, input_tokens, output_tokens, model_name = self.diary_generator.generate_diary(
                since_date=start_date,
                until_date=end_date
            )

            self.root.after(0, self._display_diary_result, diary_content, input_tokens, output_tokens, model_name)

        except Exception as e:
            self.root.after(0, self._display_error, str(e))

    def _display_diary_result(self, diary_content, input_tokens, output_tokens, model_name):
        try:
            self.diary_content_widget.set_content(diary_content)

            self.root.clipboard_clear()
            self.root.clipboard_append(diary_content)

            self.progress_widget.set_completion_message(input_tokens, output_tokens, model_name)

            self._set_buttons_state(True)
            self.control_buttons_widget.set_copy_button_state(True)

            self._execute_GoogleFormAutomation(diary_content)

        except Exception as e:
            self._display_error(f"結果表示エラー: {str(e)}")

    def _execute_GoogleFormAutomation(self, diary_content=None):
        thread = threading.Thread(target=self._run_google_form_automation, args=(diary_content,))
        thread.daemon = True
        thread.start()

    def _run_google_form_automation(self, diary_content=None):
        try:
            automation = GoogleFormAutomation()
            automation.run_automation(diary_content)
        except Exception as e:
            self._schedule_error_display(str(e))

    def _schedule_error_display(self, error_message: str):
        self.root.after(0, lambda: self.progress_widget.set_error_message(error_message))

    def _display_error(self, error_message):
        messagebox.showerror("エラー", error_message)
        self._set_buttons_state(True)
        self.progress_widget.clear_message()

    def _copy_all_text(self):
        """テキスト全体をコピー"""
        try:
            if self.diary_content_widget.has_content():
                content = self.diary_content_widget.get_content()
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                messagebox.showinfo("コピー完了", "クリップボードにコピーしました。")
            else:
                messagebox.showwarning("警告", "コピーするテキストがありません。")
        except Exception as e:
            messagebox.showerror("エラー", f"コピー中にエラーが発生しました: {str(e)}")

    def _clear_text(self):
        self.diary_content_widget.clear_content()
        self.control_buttons_widget.set_copy_button_state(False)
        self.progress_widget.clear_message()

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
        self.control_buttons_widget.set_buttons_state(enabled)
