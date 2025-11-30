import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.main_window import CodeDiaryMainWindow


class TestCodeDiaryMainWindow:
    """CodeDiaryMainWindowクラスのテストクラス"""

    @pytest.fixture
    def mock_config(self):
        """設定ファイルのモック"""
        mock_config = Mock()

        def get_side_effect(section, key, fallback=None):
            config_values = {
                ('GIT', 'repository_path'): '/mock/repo/path',
                ('WindowSettings', 'window_width'): '800',
                ('WindowSettings', 'window_height'): '600',
                ('DiaryText', 'font'): 'メイリオ',
            }
            return config_values.get((section, key), fallback)

        def getint_side_effect(section, key, fallback=None):
            config_values = {
                ('DiaryText', 'font_size'): 11,
            }
            return config_values.get((section, key), fallback)

        mock_config.get.side_effect = get_side_effect
        mock_config.getint.side_effect = getint_side_effect
        mock_config.getboolean.return_value = False
        mock_config.has_section.return_value = True
        return mock_config

    @pytest.fixture
    def mock_diary_generator(self):
        """ProgrammingDiaryGeneratorのモック"""
        mock_generator = Mock()
        mock_generator.generate_diary.return_value = (
            "# テスト日誌\n\n**機能追加**\n- テスト実装",
            100,  # input_tokens
            200,  # output_tokens
            'test-model'
        )
        return mock_generator

    @pytest.fixture
    def root(self):
        """Tkinterルートウィンドウ"""
        root_window = tk.Tk()
        yield root_window
        root_window.destroy()

    @pytest.fixture
    def main_window(self, root, mock_config, mock_diary_generator):
        """CodeDiaryMainWindowのインスタンス"""
        with patch('app.main_window.load_config', return_value=mock_config), \
             patch('app.main_window.ProgrammingDiaryGenerator', return_value=mock_diary_generator):
            window = CodeDiaryMainWindow(root)
            return window

    def test_init_success(self, root, mock_config, mock_diary_generator):
        """正常な初期化のテスト"""
        with patch('app.main_window.load_config', return_value=mock_config), \
             patch('app.main_window.ProgrammingDiaryGenerator', return_value=mock_diary_generator):
            window = CodeDiaryMainWindow(root)

            assert window.root == root
            assert window.config == mock_config
            assert window.diary_generator == mock_diary_generator
            assert hasattr(window, 'date_selection_widget')
            assert hasattr(window, 'progress_widget')
            assert hasattr(window, 'diary_content_widget')
            assert hasattr(window, 'control_buttons_widget')

    def test_setup_locale_success(self, main_window):
        """ロケール設定の正常系テスト"""
        # ロケール設定は初期化時に実行されるため、エラーがなければ成功
        assert main_window is not None

    def test_setup_ui_creates_widgets(self, main_window):
        """UI設定でウィジェットが正しく作成されるテスト"""
        assert main_window.date_selection_widget is not None
        assert main_window.progress_widget is not None
        assert main_window.diary_content_widget is not None
        assert main_window.control_buttons_widget is not None

    def test_validate_dates_valid_dates(self, main_window):
        """日付検証: 有効な日付範囲のテスト"""
        since_date = datetime(2024, 1, 1)
        until_date = datetime(2024, 1, 31)

        result = main_window._validate_dates(since_date, until_date)
        assert result is True

    def test_validate_dates_invalid_dates(self, main_window):
        """日付検証: 無効な日付範囲のテスト（終了日が開始日より前）"""
        since_date = datetime(2024, 1, 31)
        until_date = datetime(2024, 1, 1)

        with patch.object(messagebox, 'showerror'):
            result = main_window._validate_dates(since_date, until_date)
            assert result is False

    def test_validate_dates_widget_validation(self, main_window):
        """日付検証: ウィジェットからの検証のテスト"""
        main_window.date_selection_widget.validate_dates = Mock(return_value=(True, ""))

        result = main_window._validate_dates()
        assert result is True

    def test_validate_dates_widget_validation_error(self, main_window):
        """日付検証: ウィジェットからの検証エラーのテスト"""
        main_window.date_selection_widget.validate_dates = Mock(
            return_value=(False, "エラーメッセージ")
        )

        with patch.object(messagebox, 'showerror'):
            result = main_window._validate_dates()
            assert result is False

    def test_create_diary_success(self, main_window):
        """日誌作成の正常系テスト"""
        main_window.date_selection_widget.validate_dates = Mock(return_value=(True, ""))
        main_window.date_selection_widget.get_start_date = Mock(
            return_value=datetime(2024, 1, 1)
        )
        main_window.date_selection_widget.get_end_date = Mock(
            return_value=datetime(2024, 1, 31)
        )

        with patch('threading.Thread') as mock_thread:
            main_window._create_diary()
            mock_thread.assert_called_once()

    def test_create_diary_validation_error(self, main_window):
        """日誌作成: 日付検証エラーのテスト"""
        main_window.date_selection_widget.validate_dates = Mock(
            return_value=(False, "エラー")
        )

        with patch.object(messagebox, 'showerror'), \
             patch('threading.Thread') as mock_thread:
            main_window._create_diary()
            mock_thread.assert_not_called()

    def test_create_github_diary_disabled(self, main_window):
        """GitHub連携日誌作成: 機能無効時のテスト"""
        main_window.config.getboolean.return_value = False

        with patch.object(messagebox, 'showwarning') as mock_warning:
            main_window._create_github_diary()
            mock_warning.assert_called_once()

    def test_create_github_diary_no_credentials(self, main_window):
        """GitHub連携日誌作成: 認証情報なしのテスト"""
        main_window.config.getboolean.return_value = True

        with patch('os.getenv', return_value=None), \
             patch.object(messagebox, 'showerror') as mock_error:
            main_window._create_github_diary()
            mock_error.assert_called_once()

    def test_create_github_diary_success(self, main_window):
        """GitHub連携日誌作成の正常系テスト"""
        main_window.config.getboolean.return_value = True
        main_window.date_selection_widget.get_selected_dates = Mock(
            return_value=(datetime(2024, 1, 1), datetime(2024, 1, 31))
        )

        with patch('os.getenv', return_value='test_value'), \
             patch('threading.Thread') as mock_thread:
            main_window._create_github_diary()
            mock_thread.assert_called_once()

    def test_display_diary_result_success(self, main_window):
        """日誌結果表示の正常系テスト"""
        diary_content = "# テスト日誌"
        input_tokens = 100
        output_tokens = 200
        model_name = "test-model"

        main_window.diary_content_widget.set_content = Mock()
        main_window.progress_widget.set_completion_message = Mock()
        main_window.control_buttons_widget.set_copy_button_state = Mock()

        with patch('app.main_window.launch_form_page') as mock_launch:
            main_window._display_diary_result(
                diary_content, input_tokens, output_tokens, model_name
            )

            main_window.diary_content_widget.set_content.assert_called_once_with(diary_content)
            main_window.progress_widget.set_completion_message.assert_called_once_with(
                input_tokens, output_tokens, model_name
            )
            main_window.control_buttons_widget.set_copy_button_state.assert_called_once_with(True)
            mock_launch.assert_called_once()

    def test_display_diary_result_error(self, main_window):
        """日誌結果表示のエラーテスト"""
        main_window.diary_content_widget.set_content = Mock(
            side_effect=Exception("表示エラー")
        )

        with patch.object(messagebox, 'showerror'):
            main_window._display_diary_result("content", 100, 200, "model")

    def test_display_error(self, main_window):
        """エラー表示のテスト"""
        error_message = "テストエラー"

        with patch.object(messagebox, 'showerror') as mock_error:
            main_window._display_error(error_message)
            mock_error.assert_called_once_with("エラー", error_message)

    def test_copy_all_text_success(self, main_window):
        """テキストコピーの正常系テスト"""
        main_window.diary_content_widget.has_content = Mock(return_value=True)
        main_window.diary_content_widget.get_content = Mock(return_value="テスト内容")

        with patch.object(messagebox, 'showinfo'):
            main_window._copy_all_text()

    def test_copy_all_text_no_content(self, main_window):
        """テキストコピー: 内容なしのテスト"""
        main_window.diary_content_widget.has_content = Mock(return_value=False)

        with patch.object(messagebox, 'showwarning') as mock_warning:
            main_window._copy_all_text()
            mock_warning.assert_called_once()

    def test_copy_all_text_error(self, main_window):
        """テキストコピー: エラーのテスト"""
        main_window.diary_content_widget.has_content = Mock(
            side_effect=Exception("コピーエラー")
        )

        with patch.object(messagebox, 'showerror') as mock_error:
            main_window._copy_all_text()
            mock_error.assert_called_once()

    def test_clear_text(self, main_window):
        """テキストクリアのテスト"""
        main_window.diary_content_widget.clear_content = Mock()
        main_window.control_buttons_widget.set_copy_button_state = Mock()
        main_window.progress_widget.clear_message = Mock()

        main_window._clear_text()

        main_window.diary_content_widget.clear_content.assert_called_once()
        main_window.control_buttons_widget.set_copy_button_state.assert_called_once_with(False)
        main_window.progress_widget.clear_message.assert_called_once()

    def test_setup_repository_success(self, main_window):
        """リポジトリ設定の正常系テスト"""
        new_path = "C:/test/repo"

        main_window.config.has_section = Mock(return_value=True)
        main_window.config.set = Mock()

        with patch('tkinter.filedialog.askdirectory', return_value=new_path), \
             patch('app.main_window.save_config'), \
             patch('app.main_window.ProgrammingDiaryGenerator'), \
             patch.object(messagebox, 'showinfo'):
            main_window._setup_repository()

            main_window.config.set.assert_called_once_with('GIT', 'repository_path', new_path)

    def test_setup_repository_cancel(self, main_window):
        """リポジトリ設定: キャンセルのテスト"""
        with patch('tkinter.filedialog.askdirectory', return_value=''):
            main_window._setup_repository()
            # キャンセル時は何もしない

    def test_setup_repository_error(self, main_window):
        """リポジトリ設定: エラーのテスト"""
        with patch('tkinter.filedialog.askdirectory', side_effect=Exception("設定エラー")), \
             patch.object(messagebox, 'showerror') as mock_error:
            main_window._setup_repository()
            mock_error.assert_called_once()

    def test_set_buttons_state(self, main_window):
        """ボタン状態設定のテスト"""
        main_window.control_buttons_widget.set_buttons_state = Mock()

        main_window._set_buttons_state(True)
        main_window.control_buttons_widget.set_buttons_state.assert_called_once_with(True)

        main_window._set_buttons_state(False)
        main_window.control_buttons_widget.set_buttons_state.assert_called_with(False)

    def test_generate_diary_thread_success(self, main_window, mock_diary_generator):
        """日誌生成スレッドの正常系テスト"""
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        main_window.root.after = Mock()

        main_window._generate_diary_thread(start_date, end_date)

        mock_diary_generator.generate_diary.assert_called_once_with(
            since_date=start_date,
            until_date=end_date
        )
        main_window.root.after.assert_called_once()

    def test_generate_diary_thread_error(self, main_window, mock_diary_generator):
        """日誌生成スレッドのエラーテスト"""
        mock_diary_generator.generate_diary.side_effect = Exception("生成エラー")
        main_window.root.after = Mock()

        main_window._generate_diary_thread("2024-01-01", "2024-01-31")

        main_window.root.after.assert_called_once()

    def test_generate_github_diary_thread_success(self, main_window, mock_diary_generator):
        """GitHub日誌生成スレッドの正常系テスト"""
        since_date = "2024-01-01"
        until_date = "2024-01-31"

        main_window.root.after = Mock()

        main_window._generate_github_diary_thread(since_date, until_date)

        mock_diary_generator.generate_diary.assert_called_once_with(
            since_date=since_date,
            until_date=until_date,
            use_github=True
        )
        main_window.root.after.assert_called_once()

    def test_generate_github_diary_thread_error(self, main_window, mock_diary_generator):
        """GitHub日誌生成スレッドのエラーテスト"""
        mock_diary_generator.generate_diary.side_effect = Exception("GitHub生成エラー")
        main_window.root.after = Mock()

        main_window._generate_github_diary_thread("2024-01-01", "2024-01-31")

        main_window.root.after.assert_called_once()

    def test_schedule_error_display(self, main_window):
        """エラー表示スケジュールのテスト"""
        error_message = "スケジュールされたエラー"
        main_window.root.after = Mock()

        main_window._schedule_error_display(error_message)

        main_window.root.after.assert_called_once()
