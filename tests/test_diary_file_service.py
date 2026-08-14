from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from service.diary_file_service import build_diary_path, launch_obsidian, save_diary


@pytest.fixture
def mock_config():
    """設定ファイルのモック"""
    config = Mock()
    config.get.side_effect = lambda section, key: {
        ('Path', 'daily_path'): 'C:\\Diary\\01_Daily',
        ('Obsidian', 'obsidian_path'): 'C:\\Program Files\\Obsidian\\Obsidian.exe'
    }.get((section, key))
    return config


class TestBuildDiaryPath:
    """build_diary_path関数のテストクラス"""

    def test_filename_uses_until_date(self, mock_config):
        """終了日からファイル名が生成される"""
        with patch('service.diary_file_service.load_config', return_value=mock_config):
            result = build_diary_path('2026-08-09')

        assert result.name == '2026-08-09_プログラミング学習日誌.md'
        assert result.parent == Path('C:\\Diary\\01_Daily')

    def test_config_read_error(self, mock_config):
        """設定読み込みエラーが伝播する"""
        with patch('service.diary_file_service.load_config', side_effect=Exception("Config error")):
            with pytest.raises(Exception, match="Config error"):
                build_diary_path('2026-08-09')


class TestSaveDiary:
    """save_diary関数のテストクラス"""

    def test_writes_content_as_utf8(self, tmp_path):
        """UTF-8で内容が書き込まれる"""
        file_path = tmp_path / '2026-08-09_プログラミング学習日誌.md'
        content = '## 作業内容\n**機能追加**\n- テスト'

        save_diary(file_path, content)

        assert file_path.read_text(encoding='utf-8') == content

    def test_creates_missing_directory(self, tmp_path):
        """保存先ディレクトリが存在しない場合は作成される"""
        file_path = tmp_path / '01_Daily' / '2026-08-09_プログラミング学習日誌.md'

        save_diary(file_path, 'テスト')

        assert file_path.exists()

    def test_appends_to_existing_section(self, tmp_path):
        """既存ファイルの同じ見出しには本文が追記される"""
        file_path = tmp_path / '2026-08-09_プログラミング学習日誌.md'
        file_path.write_text('## 作業内容\n\n旧内容\n\n## 知見集\n\n- 旧知見\n', encoding='utf-8')

        save_diary(file_path, '## 作業内容\n\n新内容\n\n## 知見集\n\n- 新知見\n')

        assert file_path.read_text(encoding='utf-8') == (
            '## 作業内容\n\n旧内容\n\n新内容\n\n## 知見集\n\n- 旧知見\n\n- 新知見\n'
        )

    def test_keeps_section_order_and_appends_new_section(self, tmp_path):
        """既存にない見出しは末尾に追加され、既存の並び順は保たれる"""
        file_path = tmp_path / '2026-08-09_プログラミング学習日誌.md'
        file_path.write_text('## 作業内容\n\n旧内容\n', encoding='utf-8')

        save_diary(file_path, '## 学びと気づき\n\n事実：テスト\n\n## 作業内容\n\n新内容\n')

        assert file_path.read_text(encoding='utf-8') == (
            '## 作業内容\n\n旧内容\n\n新内容\n\n## 学びと気づき\n\n事実：テスト\n'
        )

    def test_skips_empty_new_section(self, tmp_path):
        """新しい内容の空セクションは追記されない"""
        file_path = tmp_path / '2026-08-09_プログラミング学習日誌.md'
        file_path.write_text('## 作業内容\n\n旧内容\n\n## 自由記載\n\n手書きメモ\n', encoding='utf-8')

        save_diary(file_path, '## 作業内容\n\n新内容\n\n## 自由記載\n\n')

        assert file_path.read_text(encoding='utf-8') == (
            '## 作業内容\n\n旧内容\n\n新内容\n\n## 自由記載\n\n手書きメモ\n'
        )


class TestLaunchObsidian:
    """launch_obsidian関数のテストクラス"""

    def test_launches_configured_executable(self, mock_config):
        """設定されたObsidianの実行ファイルを起動する"""
        with patch('service.diary_file_service.load_config', return_value=mock_config), \
             patch('service.diary_file_service.subprocess.Popen') as mock_popen:

            launch_obsidian()

        mock_popen.assert_called_once_with(['C:\\Program Files\\Obsidian\\Obsidian.exe'])

    def test_executable_not_found(self, mock_config):
        """実行ファイルが見つからない場合は例外を送出する"""
        with patch('service.diary_file_service.load_config', return_value=mock_config), \
             patch('service.diary_file_service.subprocess.Popen',
                   side_effect=FileNotFoundError("Obsidian not found")):

            with pytest.raises(FileNotFoundError, match="Obsidian not found"):
                launch_obsidian()
