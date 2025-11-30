import subprocess
from unittest.mock import Mock, patch

import pytest

from service.launch_form_page import launch_form_page


class TestLaunchFormPage:
    """launch_form_page関数のテストクラス"""

    @pytest.fixture
    def mock_config(self):
        """設定ファイルのモック"""
        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key: {
            ('Chrome', 'chrome_path'): 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            ('URL', 'form_url'): '"https://forms.gle/test"'
        }.get((section, key))
        return mock_config

    def test_launch_form_page_success(self, mock_config):
        """フォームページ起動の正常系テスト"""
        with patch('service.launch_form_page.load_config', return_value=mock_config), \
             patch('service.launch_form_page.subprocess.Popen') as mock_popen:

            launch_form_page()

            mock_popen.assert_called_once_with([
                'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                'https://forms.gle/test'
            ])

    def test_launch_form_page_url_without_quotes(self):
        """フォームURL: 引用符なしのテスト"""
        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key: {
            ('Chrome', 'chrome_path'): 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            ('URL', 'form_url'): 'https://forms.gle/test'
        }.get((section, key))

        with patch('service.launch_form_page.load_config', return_value=mock_config), \
             patch('service.launch_form_page.subprocess.Popen') as mock_popen:

            launch_form_page()

            mock_popen.assert_called_once_with([
                'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                'https://forms.gle/test'
            ])

    def test_launch_form_page_different_chrome_path(self):
        """異なるChromeパスでの起動テスト"""
        custom_chrome_path = 'D:\\CustomApps\\Chrome\\chrome.exe'
        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key: {
            ('Chrome', 'chrome_path'): custom_chrome_path,
            ('URL', 'form_url'): 'https://forms.gle/test'
        }.get((section, key))

        with patch('service.launch_form_page.load_config', return_value=mock_config), \
             patch('service.launch_form_page.subprocess.Popen') as mock_popen:

            launch_form_page()

            mock_popen.assert_called_once_with([
                custom_chrome_path,
                'https://forms.gle/test'
            ])

    def test_launch_form_page_different_url(self):
        """異なるフォームURLでの起動テスト"""
        custom_url = '"https://example.com/form"'
        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key: {
            ('Chrome', 'chrome_path'): 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            ('URL', 'form_url'): custom_url
        }.get((section, key))

        with patch('service.launch_form_page.load_config', return_value=mock_config), \
             patch('service.launch_form_page.subprocess.Popen') as mock_popen:

            launch_form_page()

            mock_popen.assert_called_once_with([
                'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                'https://example.com/form'
            ])

    def test_launch_form_page_config_loading_error(self):
        """設定ファイル読み込みエラーのテスト"""
        with patch('service.launch_form_page.load_config', side_effect=Exception("Config error")):
            with pytest.raises(Exception, match="Config error"):
                launch_form_page()

    def test_launch_form_page_popen_error(self, mock_config):
        """subprocess.Popenエラーのテスト"""
        with patch('service.launch_form_page.load_config', return_value=mock_config), \
             patch('service.launch_form_page.subprocess.Popen',
                   side_effect=FileNotFoundError("Chrome not found")):

            with pytest.raises(FileNotFoundError, match="Chrome not found"):
                launch_form_page()

    def test_launch_form_page_permission_error(self, mock_config):
        """権限エラーのテスト"""
        with patch('service.launch_form_page.load_config', return_value=mock_config), \
             patch('service.launch_form_page.subprocess.Popen',
                   side_effect=PermissionError("Permission denied")):

            with pytest.raises(PermissionError, match="Permission denied"):
                launch_form_page()

    def test_launch_form_page_url_with_spaces(self):
        """URLに空白を含む場合のテスト"""
        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key: {
            ('Chrome', 'chrome_path'): 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            ('URL', 'form_url'): '  "https://forms.gle/test"  '
        }.get((section, key))

        with patch('service.launch_form_page.load_config', return_value=mock_config), \
             patch('service.launch_form_page.subprocess.Popen') as mock_popen:

            launch_form_page()

            # strip('"')は両端の"のみを削除するため、前後の空白はそのまま残る
            mock_popen.assert_called_once_with([
                'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
                '  "https://forms.gle/test"  '
            ])

    def test_launch_form_page_url_with_multiple_quotes(self):
        """URLに複数の引用符がある場合のテスト"""
        mock_config = Mock()
        mock_config.get.side_effect = lambda section, key: {
            ('Chrome', 'chrome_path'): 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            ('URL', 'form_url'): '"""https://forms.gle/test"""'
        }.get((section, key))

        with patch('service.launch_form_page.load_config', return_value=mock_config), \
             patch('service.launch_form_page.subprocess.Popen') as mock_popen:

            launch_form_page()

            # strip('"')は両端の"を削除するため、最初と最後の1つずつしか削除されない
            # 結果: '"https://forms.gle/test"'となる
            args = mock_popen.call_args[0][0]
            assert args[0] == 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
            # 複数の"がある場合の動作を確認
            assert 'https://forms.gle/test' in args[1]

    def test_launch_form_page_subprocess_returns_process(self, mock_config):
        """subprocess.Popenがプロセスオブジェクトを返すことを確認"""
        mock_process = Mock()

        with patch('service.launch_form_page.load_config', return_value=mock_config), \
             patch('service.launch_form_page.subprocess.Popen', return_value=mock_process) as mock_popen:

            # 関数の戻り値は明示的にないが、Popenが呼ばれることを確認
            launch_form_page()

            mock_popen.assert_called_once()
            # Popenが正しい引数で呼ばれたことを確認
            call_args = mock_popen.call_args[0][0]
            assert len(call_args) == 2
            assert 'chrome.exe' in call_args[0]
            assert 'https://forms.gle/test' == call_args[1]
