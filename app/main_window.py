import threading
import tkinter as tk
from datetime import datetime, timezone, timedelta
from tkinter import ttk, messagebox, filedialog

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

        self._setup_ui()
        self._setup_bindings()

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

        date_frame = ttk.LabelFrame(main_frame, text="期間設定", padding="5")
        date_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        date_frame.columnconfigure(1, weight=1)
        date_frame.columnconfigure(3, weight=1)

        ttk.Label(date_frame, text="開始日").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(date_frame, textvariable=self.start_date_var, width=12)
        self.start_date_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        ttk.Label(date_frame, text="終了日").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(date_frame, textvariable=self.end_date_var, width=12)
        self.end_date_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))

        # デフォルト日付を設定
        today = datetime.now(self.jst).strftime("%Y/%m/%d")
        self.start_date_var.set(today)
        self.end_date_var.set(today)

        # 日誌表示エリア
        text_frame = ttk.LabelFrame(main_frame, text="日誌内容", padding="5")
        text_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        # テキストエリアとスクロールバー
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

        # スクロールバー
        scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.diary_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.diary_text.config(yscrollcommand=scrollbar.set)

        # プレースホルダーテキストを設定
        self._set_placeholder_text()

        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # ボタンの作成
        self.create_button = ttk.Button(
            button_frame,
            text="日誌作成",
            command=self._create_diary
        )
        self.create_button.grid(row=0, column=0, padx=(0, 5))

        self.copy_button = ttk.Button(
            button_frame,
            text="全文コピー",
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
            text="リポジトリ設定",
            command=self._setup_repository
        )
        self.repository_button.grid(row=0, column=3, padx=(0, 5))

        self.close_button = ttk.Button(
            button_frame,
            text="閉じる",
            command=self.root.quit
        )
        self.close_button.grid(row=0, column=4)

        # プログレスバー（非表示で初期化）
        self.progress_var = tk.StringVar()
        self.progress_var.set("")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))

    def _setup_bindings(self):
        # Enterキーで日誌作成
        self.root.bind('<Return>', lambda e: self._create_diary())

        # Ctrl+Cで全文コピー
        self.root.bind('<Control-c>', lambda e: self._copy_all_text())

        # Ctrl+Lでクリア
        self.root.bind('<Control-l>', lambda e: self._clear_text())

    def _set_placeholder_text(self):
        self.diary_text.config(state=tk.NORMAL)
        self.diary_text.delete(1.0, tk.END)
        self.diary_text.insert(1.0, "[ここに日誌を出力]")
        self.diary_text.config(state=tk.DISABLED)

    def _create_diary(self):
        try:
            # ボタンを無効化
            self._set_buttons_state(False)
            self.progress_var.set("日誌生成中...")

            # 日付の取得と変換
            start_date = self._convert_date_format(self.start_date_var.get())
            end_date = self._convert_date_format(self.end_date_var.get())

            if not start_date or not end_date:
                messagebox.showerror("エラー", "日付の形式が正しくありません。YYYY/MM/DD形式で入力してください。")
                return

            # 別スレッドで日誌生成を実行
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
            # 日誌を生成
            diary_content, input_tokens, output_tokens = self.diary_generator.generate_diary(
                since_date=start_date,
                until_date=end_date
            )

            # UIスレッドで結果を表示
            self.root.after(0, self._display_diary_result, diary_content, input_tokens, output_tokens)

        except Exception as e:
            # UIスレッドでエラーを表示
            self.root.after(0, self._display_error, str(e))

    def _display_diary_result(self, diary_content, input_tokens, output_tokens):
        try:
            # テキストエリアに結果を表示
            self.diary_text.config(state=tk.NORMAL)
            self.diary_text.delete(1.0, tk.END)
            self.diary_text.insert(1.0, diary_content)
            self.diary_text.config(state=tk.DISABLED)

            self.root.clipboard_clear()
            self.root.clipboard_append(diary_content)

            # ステータス更新
            total_tokens = input_tokens + output_tokens
            self.progress_var.set(
                f"日誌生成完了 (使用トークン: 入力={input_tokens}, 出力={output_tokens}, 合計={total_tokens})")

            # ボタンの状態を復元
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
                messagebox.showinfo("コピー完了", "全文をクリップボードにコピーしました。")
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

            # フォルダ選択ダイアログ
            new_path = filedialog.askdirectory(
                title="Gitリポジトリフォルダを選択",
                initialdir=current_path if current_path else "."
            )

            if new_path:
                # 設定を更新
                if not self.config.has_section('GIT'):
                    self.config.add_section('GIT')
                self.config.set('GIT', 'repository_path', new_path)

                # 設定を保存
                save_config(self.config)

                # 日誌ジェネレーターも更新
                self.diary_generator = ProgrammingDiaryGenerator()

                messagebox.showinfo("設定完了", f"リポジトリパスを更新しました:\n{new_path}")

        except Exception as e:
            messagebox.showerror("エラー", f"リポジトリ設定中にエラーが発生しました: {str(e)}")

    def _convert_date_format(self, date_str):
        try:
            if not date_str.strip():
                return None

            # スラッシュをハイフンに変換
            date_str = date_str.replace('/', '-')

            # 日付の妥当性をチェック
            datetime.strptime(date_str, '%Y-%m-%d')

            return date_str
        except ValueError:
            return None

    def _set_buttons_state(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.create_button.config(state=state)
        self.clear_button.config(state=state)
        self.repository_button.config(state=state)
        self.close_button.config(state=state)