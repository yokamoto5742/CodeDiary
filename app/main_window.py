import locale
import os
import threading
from tkinter import messagebox, filedialog
from tkinter import ttk

from app import __version__
from service.launch_form_page import launch_form_page
from service.programming_diary_generator import ProgrammingDiaryGenerator
from utils.config_manager import load_config, save_config
from widgets import (
    ControlButtonsWidget,
    DateSelectionWidget,
    DiaryContentWidget,
    ProgressWidget
)


class CodeDiaryMainWindow:
    """CodeDiaryアプリケーションのメインウィンドウ

    UI構成管理、ユーザーイベント処理、ビジネスロジック連携を担当"""

    def __init__(self, root):
        """メインウィンドウを初期化し、UI構成を設定"""
        self.root = root
        self.config = load_config()
        self.diary_generator = ProgrammingDiaryGenerator()

        self._setup_locale()
        self._setup_ui()
        self._setup_bindings()

    def _setup_locale(self):
        """日本語ロケールを初期化"""
        locales = ['Japanese_Japan.932', 'ja']
        for loc in locales:
            try:
                locale.setlocale(locale.LC_ALL, loc)
                return
            except locale.Error:
                continue
        print("警告: 日本語ロケールの設定に失敗しました。デフォルトロケールを使用します。")

    def _setup_ui(self):
        """ウィンドウレイアウトと各ウィジェットを初期化"""
        window_width = self.config.get('WindowSettings', 'window_width', fallback='600')
        window_height = self.config.get('WindowSettings', 'window_height', fallback='600')
        window_x = self.config.get('WindowSettings', 'window_x', fallback='')
        window_y = self.config.get('WindowSettings', 'window_y', fallback='')

        self.root.title(f"CodeDiary v{__version__}")

        if window_x and window_y:
            self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
        else:
            self.root.geometry(f"{window_width}x{window_height}")

        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="wens")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        self.date_selection_widget = DateSelectionWidget(
            main_frame,
            self.config
        )
        self.date_selection_widget.grid(
            row=0, column=0, sticky="we", pady=(0, 10)
        )

        self.progress_widget = ProgressWidget(main_frame)
        self.progress_widget.grid(
            row=1, column=0, sticky="we", pady=(0, 5)
        )

        self.diary_content_widget = DiaryContentWidget(
            main_frame,
            self.config
        )
        self.diary_content_widget.grid(
            row=2, column=0, sticky="wens", pady=(0, 10)
        )

        self.control_buttons_widget = ControlButtonsWidget(main_frame)
        self.control_buttons_widget.grid(
            row=3, column=0, sticky="we"
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
        """キーバインドを設定"""
        self.root.bind('<Control-l>', lambda e: self._clear_text())

    def _validate_dates(self, since_date=None, until_date=None):
        """日付の妥当性を検証 GitHub連携時と通常時で分岐処理"""
        if since_date is not None and until_date is not None:
            if since_date > until_date:
                messagebox.showerror("エラー", "終了日より前の日付を選択してください。")
                return False
            return True
        else:
            is_valid, error_message = self.date_selection_widget.validate_dates()
            if not is_valid:
                messagebox.showerror("エラー", error_message)
            return is_valid

    def _create_diary(self):
        """ローカルGitリポジトリから日誌を生成"""
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
        """GitHub APIから複数リポジトリのコミットを取得し日誌を生成"""
        try:
            github_enabled = self.config.getboolean('GITHUB', 'enable_cross_repo_tracking', fallback=False)
            if not github_enabled:
                messagebox.showwarning(
                    "GitHub連携無効",
                    "GitHub連携が無効になっています。\nutils/config.iniでenable_cross_repo_tracking=trueに設定してください。"
                )
                return

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

            since_date_obj, until_date_obj = self.date_selection_widget.get_selected_dates()
            since_date = since_date_obj.strftime('%Y-%m-%d')
            until_date = until_date_obj.strftime('%Y-%m-%d')

            if not self._validate_dates(since_date_obj, until_date_obj):
                return

            self._set_buttons_state(False)
            self.progress_widget.start_progress("GitHub連携で日記を生成中...")

            thread = threading.Thread(
                target=self._generate_github_diary_thread,
                args=(since_date, until_date),
                daemon=True
            )
            thread.start()

        except Exception as e:
            messagebox.showerror("エラー", f"GitHub連携日記の作成でエラーが発生しました:\n{str(e)}")
            self._set_buttons_state(True)
            self.progress_widget.stop_progress()

    def _generate_github_diary_thread(self, since_date, until_date):
        """GitHub APIからのコミット取得と日誌生成をスレッド内で実行"""
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
        """ローカルGit日誌生成をスレッド内で実行"""
        try:
            diary_content, input_tokens, output_tokens, model_name = self.diary_generator.generate_diary(
                since_date=start_date,
                until_date=end_date
            )

            self.root.after(0, self._display_diary_result, diary_content, input_tokens, output_tokens, model_name)

        except Exception as e:
            self.root.after(0, self._display_error, str(e))

    def _display_diary_result(self, diary_content, input_tokens, output_tokens, model_name):
        """生成した日誌を画面に表示しクリップボードにコピー その後Chromeでフォームを開く"""
        try:
            self.diary_content_widget.set_content(diary_content)

            self.root.clipboard_clear()
            self.root.clipboard_append(diary_content)

            self.progress_widget.set_completion_message(input_tokens, output_tokens, model_name)

            self._set_buttons_state(True)

            launch_form_page()

        except Exception as e:
            self._display_error(f"結果表示エラー: {str(e)}")

    def _schedule_error_display(self, error_message: str):
        """メインスレッドでエラーメッセージを表示するようスケジュール"""
        self.root.after(0, lambda: self.progress_widget.set_error_message(error_message))

    def _display_error(self, error_message):
        """エラーダイアログを表示しUIを回復状態に戻す"""
        messagebox.showerror("エラー", error_message)
        self._set_buttons_state(True)
        self.progress_widget.clear_message()

    def _copy_all_text(self):
        """日誌内容をクリップボードにコピー"""
        try:
            if self.diary_content_widget.has_content():
                content = self.diary_content_widget.get_content()
                self.root.clipboard_clear()
                self.root.clipboard_append(content)
                messagebox.showinfo("コピー完了", "日誌内容をクリップボードにコピーしました")
            else:
                messagebox.showwarning("警告", "コピーするテキストがありません")
        except Exception as e:
            messagebox.showerror("エラー", f"コピー中にエラーが発生しました: {str(e)}")

    def _clear_text(self):
        """日誌内容をリセットし、UI状態を初期化"""
        self.diary_content_widget.clear_content()
        self.progress_widget.clear_message()

    def _setup_repository(self):
        """Gitリポジトリパスの設定を更新"""
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
        """操作ボタンの有効/無効を切り替え"""
        self.control_buttons_widget.set_buttons_state(enabled)

    def _on_closing(self):
        """ウィンドウを閉じる前にウィンドウ位置を保存"""
        try:
            window_x = self.root.winfo_x()
            window_y = self.root.winfo_y()

            if not self.config.has_section('WindowSettings'):
                self.config.add_section('WindowSettings')

            self.config.set('WindowSettings', 'window_x', str(window_x))
            self.config.set('WindowSettings', 'window_y', str(window_y))

            save_config(self.config)
        except Exception as e:
            print(f"ウィンドウ位置の保存中にエラーが発生しました: {e}")
        finally:
            self.root.quit()
