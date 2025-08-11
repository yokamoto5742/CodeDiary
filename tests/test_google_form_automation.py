import os
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock

import pytest

from service.google_form_automation import GoogleFormAutomation


class TestGoogleFormAutomation:
    """GoogleFormAutomationクラスのテストクラス"""

    @pytest.fixture
    def mock_config(self):
        """設定ファイルのモック"""
        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, fallback=None: {
            ('Chrome', 'chrome_path'): 'C:/Program Files/Google/Chrome/Application/chrome.exe',
            ('URL', 'form_url'): 'https://forms.gle/test123'
        }.get((section, key), fallback)
        return mock_config

    @pytest.fixture
    def automation(self, mock_config):
        """GoogleFormAutomationのインスタンス作成"""
        with patch('service.google_form_automation.load_config', return_value=mock_config):
            automation = GoogleFormAutomation()
            return automation

    def test_init_success(self, mock_config):
        """正常な初期化のテスト"""
        with patch('service.google_form_automation.load_config', return_value=mock_config):
            automation = GoogleFormAutomation()
            assert automation.chrome_path == 'C:/Program Files/Google/Chrome/Application/chrome.exe'
            assert automation.jst == timezone(timedelta(hours=9))

    def test_get_chrome_path_success(self, automation):
        """Chrome実行ファイルパス取得の正常系テスト"""
        result = automation._get_chrome_path()
        assert result == 'C:/Program Files/Google/Chrome/Application/chrome.exe'

    def test_get_chrome_path_not_configured(self):
        """Chrome実行ファイルパスが設定されていない場合のテスト"""
        mock_config = Mock()
        mock_config.get.return_value = None
        
        with patch('service.google_form_automation.load_config', return_value=mock_config):
            with pytest.raises(Exception, match="設定ファイルにchrome_pathが設定されていません"):
                GoogleFormAutomation()

    def test_check_chrome_path_exists(self, automation):
        """Chrome実行ファイル存在確認の正常系テスト"""
        with patch('os.path.exists', return_value=True):
            result = automation._check_chrome_path()
            assert result is True

    def test_check_chrome_path_not_exists(self, automation):
        """Chrome実行ファイルが存在しない場合のテスト"""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(Exception, match="Chrome実行ファイルが見つかりません"):
                automation._check_chrome_path()

    def test_get_form_url_success(self, automation):
        """フォームURL取得の正常系テスト"""
        result = automation._get_form_url()
        assert result == 'https://forms.gle/test123'

    def test_get_form_url_not_configured(self):
        """フォームURLが設定されていない場合のテスト"""
        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, fallback=None: {
            ('Chrome', 'chrome_path'): 'C:/chrome.exe',
            ('URL', 'form_url'): None
        }.get((section, key), fallback)
        
        with patch('service.google_form_automation.load_config', return_value=mock_config):
            automation = GoogleFormAutomation()
            with pytest.raises(Exception, match="設定ファイルにform_urlが設定されていません"):
                automation._get_form_url()

    @patch('pyperclip.paste')
    def test_get_clipboard_content_success(self, mock_paste, automation):
        """クリップボード内容取得の正常系テスト"""
        # モックの準備
        mock_paste.return_value = "テスト用のクリップボード内容"

        # テスト実行
        result = automation._get_clipboard_content()

        # 検証
        assert result == "テスト用のクリップボード内容"
        mock_paste.assert_called_once()

    @patch('pyperclip.paste')
    def test_get_clipboard_content_empty(self, mock_paste, automation):
        """クリップボードが空の場合のテスト"""
        # モックの準備
        mock_paste.return_value = ""

        # テスト実行と検証
        with pytest.raises(Exception, match="クリップボードが空です"):
            automation._get_clipboard_content()

    @patch('pyperclip.paste')
    def test_get_clipboard_content_none(self, mock_paste, automation):
        """クリップボードがNoneの場合のテスト"""
        # モックの準備
        mock_paste.return_value = None

        # テスト実行と検証
        with pytest.raises(Exception, match="クリップボードが空です"):
            automation._get_clipboard_content()

    @patch('pyperclip.paste')
    def test_get_clipboard_content_whitespace_only(self, mock_paste, automation):
        """クリップボードが空白文字のみの場合のテスト"""
        # モックの準備
        mock_paste.return_value = "   \n\t   "

        # テスト実行と検証
        with pytest.raises(Exception, match="クリップボードが空です"):
            automation._get_clipboard_content()

    @patch('pyperclip.paste')
    def test_get_clipboard_content_exception(self, mock_paste, automation):
        """クリップボードアクセス時の例外発生テスト"""
        # モックの準備
        mock_paste.side_effect = Exception("Clipboard access failed")

        # テスト実行と検証
        with pytest.raises(Exception, match="クリップボードにアクセスできませんでした"):
            automation._get_clipboard_content()

    def test_get_today_date_string(self, automation):
        """今日の日付文字列取得テスト"""
        # 固定日時でテスト
        fixed_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone(timedelta(hours=9)))
        
        with patch('service.google_form_automation.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime
            
            result = automation._get_today_date_string()
            
            assert result == "2024-01-15"
            mock_datetime.now.assert_called_once_with(automation.jst)

    @patch('service.google_form_automation.sync_playwright')
    @patch('os.path.exists')
    @patch('pyperclip.paste')
    def test_run_automation_success(self, mock_paste, mock_exists, mock_playwright, automation):
        """自動化処理の正常系テスト"""
        # モックの準備
        mock_exists.return_value = True
        mock_paste.return_value = "テスト用の作業内容"
        
        # Playwrightのモック設定
        mock_playwright_context = MagicMock()
        mock_playwright.return_value.__enter__.return_value = mock_playwright_context
        
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright_context.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        mock_date_input = MagicMock()
        mock_textarea = MagicMock()
        mock_page.locator.return_value = mock_date_input
        mock_page.get_by_label.return_value = mock_textarea

        # 固定日時でテスト
        fixed_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone(timedelta(hours=9)))
        with patch('service.google_form_automation.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime
            
            # テスト実行
            automation.run_automation()

        # 検証
        mock_playwright_context.chromium.launch.assert_called_once()
        mock_page.goto.assert_called_once_with('https://forms.gle/test123')
        mock_date_input.fill.assert_called_once_with("2024-01-15")
        mock_textarea.fill.assert_called_once_with("テスト用の作業内容")

    @patch('os.path.exists')
    def test_run_automation_chrome_not_found(self, mock_exists, automation):
        """Chrome実行ファイルが見つからない場合のテスト"""
        # モックの準備
        mock_exists.return_value = False

        # テスト実行と検証
        with pytest.raises(Exception, match="Chrome実行ファイルが見つかりません"):
            automation.run_automation()

    @patch('os.path.exists')
    @patch('pyperclip.paste')
    def test_run_automation_clipboard_empty(self, mock_paste, mock_exists, automation):
        """クリップボードが空の場合のテスト"""
        # モックの準備
        mock_exists.return_value = True
        mock_paste.return_value = ""

        # テスト実行と検証
        with pytest.raises(Exception, match="クリップボードが空です"):
            automation.run_automation()

    @patch('service.google_form_automation.sync_playwright')
    @patch('os.path.exists')
    @patch('pyperclip.paste')
    def test_run_automation_playwright_exception(self, mock_paste, mock_exists, mock_playwright, automation):
        """Playwright実行時の例外発生テスト"""
        # モックの準備
        mock_exists.return_value = True
        mock_paste.return_value = "テスト用の作業内容"
        
        # Playwrightで例外発生
        mock_playwright.side_effect = Exception("Playwright error")

        # テスト実行と検証
        with pytest.raises(Exception):
            automation.run_automation()

    @patch('service.google_form_automation.sync_playwright')
    @patch('os.path.exists')
    @patch('pyperclip.paste')
    def test_run_automation_page_navigation_error(self, mock_paste, mock_exists, mock_playwright, automation):
        """ページナビゲーション時のエラーテスト"""
        # モックの準備
        mock_exists.return_value = True
        mock_paste.return_value = "テスト用の作業内容"
        
        # Playwrightのモック設定
        mock_playwright_context = MagicMock()
        mock_playwright.return_value.__enter__.return_value = mock_playwright_context
        
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright_context.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        # ページ遷移でエラー発生
        mock_page.goto.side_effect = Exception("Navigation failed")

        # 固定日時でテスト
        fixed_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone(timedelta(hours=9)))
        with patch('service.google_form_automation.datetime') as mock_datetime:
            mock_datetime.now.return_value = fixed_datetime
            
            # テスト実行（例外は内部でキャッチされて出力される）
            automation.run_automation()

        # ブラウザとコンテキストのクリーンアップが呼ばれることを確認
        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()

    def test_run_automation_form_url_not_configured(self):
        """フォームURLが設定されていない場合の統合テスト"""
        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key, fallback=None: {
            ('Chrome', 'chrome_path'): 'C:/chrome.exe',
            ('URL', 'form_url'): None
        }.get((section, key), fallback)
        
        with patch('service.google_form_automation.load_config', return_value=mock_config), \
             patch('os.path.exists', return_value=True), \
             patch('pyperclip.paste', return_value="テスト内容"):
            
            automation = GoogleFormAutomation()
            
            with pytest.raises(Exception, match="設定ファイルにform_urlが設定されていません"):
                automation.run_automation()
