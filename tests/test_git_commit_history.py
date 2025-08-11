import os
import subprocess
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock

import pytest

from service.git_commit_history import GitCommitHistoryService


class TestGitCommitHistoryService:
    """GitCommitHistoryServiceクラスのテストクラス"""

    @pytest.fixture
    def mock_config(self):
        """設定ファイルのモック"""
        mock_config = Mock()
        mock_config.get.return_value = "/mock/repo/path"
        return mock_config

    @pytest.fixture
    def service(self, mock_config):
        """GitCommitHistoryServiceのインスタンス作成"""
        with patch('service.git_commit_history.load_config', return_value=mock_config), \
             patch('os.path.exists', return_value=True):
            service = GitCommitHistoryService()
            service.repository_path = "/mock/repo/path"
            return service

    def test_init_success(self, mock_config):
        """正常な初期化のテスト"""
        with patch('service.git_commit_history.load_config', return_value=mock_config), \
             patch('os.path.exists', return_value=True):
            service = GitCommitHistoryService()
            assert service.repository_path == "/mock/repo/path"
            assert service.jst == timezone(timedelta(hours=9))

    def test_init_repository_path_not_exists(self, mock_config):
        """リポジトリパスが存在しない場合のテスト"""
        with patch('service.git_commit_history.load_config', return_value=mock_config), \
             patch('os.path.exists', return_value=False):
            with pytest.raises(Exception, match="リポジトリパスが存在しません"):
                GitCommitHistoryService()

    @patch('subprocess.run')
    def test_get_commit_history_success(self, mock_subprocess_run, service):
        """コミット履歴取得の正常系テスト"""
        # モックの準備
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123|John Doe|john@example.com|2024-01-01T10:00:00+09:00|Initial commit\n" \
                           "def456|Jane Smith|jane@example.com|2024-01-02T15:30:00+09:00|Add feature"
        mock_subprocess_run.return_value = mock_result

        # テスト実行
        result = service.get_commit_history(
            since_date="2024-01-01",
            until_date="2024-01-02"
        )

        # 検証
        assert len(result) == 2
        assert result[0]['hash'] == 'abc123'
        assert result[0]['author_name'] == 'John Doe'
        assert result[0]['message'] == 'Initial commit'
        assert result[1]['hash'] == 'def456'
        assert result[1]['author_name'] == 'Jane Smith'

        # subprocess.runが適切に呼ばれることを確認
        mock_subprocess_run.assert_called_once()
        args = mock_subprocess_run.call_args[0][0]
        assert 'git' in args
        assert 'log' in args
        assert '--since=2024-01-01 00:00:00 +0900' in args
        assert '--until=2024-01-02 23:59:59 +0900' in args

    @patch('subprocess.run')
    def test_get_commit_history_git_command_failure(self, mock_subprocess_run, service):
        """Gitコマンド失敗時のテスト"""
        # モックの準備
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "fatal: not a git repository"
        mock_subprocess_run.return_value = mock_result

        # テスト実行と検証
        with pytest.raises(Exception, match="Gitコマンドの実行に失敗しました"):
            service.get_commit_history()

    @patch('subprocess.run')
    def test_get_commit_history_subprocess_error(self, mock_subprocess_run, service):
        """subprocess例外発生時のテスト"""
        # モックの準備
        mock_subprocess_run.side_effect = subprocess.SubprocessError("Command failed")

        # テスト実行と検証
        with pytest.raises(Exception, match="Gitコマンドの実行でエラーが発生しました"):
            service.get_commit_history()

    @patch('subprocess.run')
    def test_get_commit_history_empty_result(self, mock_subprocess_run, service):
        """空の結果が返される場合のテスト"""
        # モックの準備
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_subprocess_run.return_value = mock_result

        # テスト実行
        result = service.get_commit_history()

        # 検証
        assert result == []

    def test_format_output_success(self, service):
        """出力フォーマットの正常系テスト"""
        # テストデータ
        commits = [
            {
                'timestamp': '2024-01-01T10:00:00+09:00',
                'message': 'Initial commit'
            },
            {
                'timestamp': '2024-01-02T15:30:00+09:00',
                'message': 'Add feature'
            }
        ]

        # テスト実行
        result = service.format_output(commits)

        # 検証
        assert "コミット履歴 (2件)" in result
        assert "Initial commit" in result
        assert "Add feature" in result
        assert "2024/01/01 10:00:00 (JST)" in result
        assert "2024/01/02 15:30:00 (JST)" in result

    def test_format_output_empty_commits(self, service):
        """空のコミットリストの場合のテスト"""
        result = service.format_output([])
        assert result == "コミット履歴が見つかりませんでした。"

    def test_format_output_invalid_timestamp(self, service):
        """不正なタイムスタンプの場合のテスト"""
        commits = [{
            'timestamp': 'invalid-timestamp',
            'message': 'Test commit'
        }]

        result = service.format_output(commits)
        assert "invalid-timestamp" in result
        assert "Test commit" in result

    @patch('subprocess.run')
    def test_get_repository_info_success(self, mock_subprocess_run, service):
        """リポジトリ情報取得の正常系テスト"""
        # モックの準備
        def mock_run_side_effect(cmd, **kwargs):
            mock_result = Mock()
            mock_result.returncode = 0
            if 'branch' in cmd:
                mock_result.stdout = "main"
            elif 'remote' in cmd:
                mock_result.stdout = "https://github.com/user/repo.git"
            elif 'log' in cmd:
                mock_result.stdout = "abc123|John Doe|2024-01-01T10:00:00+09:00"
            return mock_result

        mock_subprocess_run.side_effect = mock_run_side_effect

        # テスト実行
        result = service.get_repository_info()

        # 検証
        assert result['path'] == "/mock/repo/path"
        assert result['current_branch'] == "main"
        assert result['remote_url'] == "https://github.com/user/repo.git"
        assert "abc123" in result['latest_commit']
        assert "John Doe" in result['latest_commit']

    @patch('subprocess.run')
    def test_get_repository_info_error_handling(self, mock_subprocess_run, service):
        """リポジトリ情報取得のエラーハンドリングテスト"""
        # モックの準備
        mock_subprocess_run.side_effect = Exception("Command failed")

        # テスト実行
        result = service.get_repository_info()

        # 検証
        assert result['path'] == "/mock/repo/path"
        assert result['current_branch'] == "エラー"
        assert "取得エラー" in result['remote_url']
        assert result['latest_commit'] == "エラー"

    @patch('subprocess.run')
    def test_get_branch_list_success(self, mock_subprocess_run, service):
        """ブランチリスト取得の正常系テスト"""
        # モックの準備
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "  main\n* feature-branch\n  remotes/origin/main\n  remotes/origin/HEAD -> origin/main"
        mock_subprocess_run.return_value = mock_result

        # テスト実行
        result = service.get_branch_list()

        # 検証
        assert "main" in result
        assert "feature-branch" in result
        assert "remotes/origin/main" in result
        # HEAD -> origin/main は除外される
        assert "remotes/origin/HEAD -> origin/main" not in result

    @patch('subprocess.run')
    def test_get_branch_list_error_handling(self, mock_subprocess_run, service):
        """ブランチリスト取得のエラーハンドリングテスト"""
        # モックの準備
        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess_run.return_value = mock_result

        # テスト実行
        result = service.get_branch_list()

        # 検証
        assert result == []

    @patch('subprocess.run')
    def test_get_branch_list_exception(self, mock_subprocess_run, service):
        """ブランチリスト取得の例外発生時のテスト"""
        # モックの準備
        mock_subprocess_run.side_effect = Exception("Command failed")

        # テスト実行
        result = service.get_branch_list()

        # 検証
        assert result == []

    def test_get_subprocess_kwargs_windows(self, service):
        """Windows環境でのsubprocessオプション設定テスト"""
        with patch('os.name', 'nt'):
            kwargs = service._get_subprocess_kwargs()
            
            assert kwargs['capture_output'] is True
            assert kwargs['text'] is True
            assert kwargs['encoding'] == 'utf-8'
            assert kwargs['creationflags'] == subprocess.CREATE_NO_WINDOW

    def test_get_subprocess_kwargs_non_windows(self, service):
        """非Windows環境でのsubprocessオプション設定テスト"""
        with patch('os.name', 'posix'):
            kwargs = service._get_subprocess_kwargs()
            
            assert kwargs['capture_output'] is True
            assert kwargs['text'] is True
            assert kwargs['encoding'] == 'utf-8'
            assert 'creationflags' not in kwargs
