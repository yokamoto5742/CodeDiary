from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from utils.repository_name_extractor import get_repository_directory_name


class TestRepositoryNameExtractor:
    """repository_name_extractorモジュールのテストクラス"""

    def test_get_repository_directory_name_success(self):
        """リポジトリディレクトリ名取得の正常系テスト"""
        mock_config = Mock()
        mock_config.get.return_value = "/home/user/projects/my-awesome-project"

        with patch('utils.repository_name_extractor.load_config', return_value=mock_config):
            result = get_repository_directory_name()

        assert result == "my-awesome-project"
        mock_config.get.assert_called_once_with('GIT', 'repository_path', fallback='')

    def test_get_repository_directory_name_windows_path(self):
        """Windowsパス形式での正常系テスト"""
        mock_config = Mock()
        mock_config.get.return_value = "C:\\Users\\yokam\\PycharmProjects\\CodeDiary"

        with patch('utils.repository_name_extractor.load_config', return_value=mock_config):
            result = get_repository_directory_name()

        assert result == "CodeDiary"

    def test_get_repository_directory_name_empty_path(self):
        """空のパスの場合のテスト"""
        mock_config = Mock()
        mock_config.get.return_value = ""

        with patch('utils.repository_name_extractor.load_config', return_value=mock_config):
            result = get_repository_directory_name()

        assert result == ""

    def test_get_repository_directory_name_root_path(self):
        """ルートパスの場合のテスト"""
        mock_config = Mock()
        mock_config.get.return_value = "/"

        with patch('utils.repository_name_extractor.load_config', return_value=mock_config):
            result = get_repository_directory_name()

        assert result == ""

    def test_get_repository_directory_name_config_error(self):
        """設定読み込みエラーのテスト"""
        with patch('utils.repository_name_extractor.load_config', side_effect=Exception("Config error")):
            with pytest.raises(Exception, match="プロジェクト名取得に失敗しました"):
                get_repository_directory_name()

    def test_get_repository_directory_name_config_get_error(self):
        """設定値取得エラーのテスト"""
        mock_config = Mock()
        mock_config.get.side_effect = Exception("Get error")

        with patch('utils.repository_name_extractor.load_config', return_value=mock_config):
            with pytest.raises(Exception, match="プロジェクト名取得に失敗しました"):
                get_repository_directory_name()

    def test_get_repository_directory_name_relative_path(self):
        """相対パスの場合のテスト"""
        mock_config = Mock()
        mock_config.get.return_value = "./my-project"

        with patch('utils.repository_name_extractor.load_config', return_value=mock_config):
            result = get_repository_directory_name()

        assert result == "my-project"

    def test_get_repository_directory_name_nested_path(self):
        """深い階層のパスのテスト"""
        mock_config = Mock()
        mock_config.get.return_value = "/very/deep/nested/path/to/my-project"

        with patch('utils.repository_name_extractor.load_config', return_value=mock_config):
            result = get_repository_directory_name()

        assert result == "my-project"