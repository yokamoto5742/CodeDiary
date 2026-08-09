import os
from unittest.mock import Mock, patch

import pytest
import requests

from service.github_commit_tracker import GitHubCommitTracker


class TestGitHubCommitTracker:
    """GitHubCommitTrackerクラスのテストスイート"""

    @pytest.fixture
    def mock_env_vars(self):
        """GitHub環境変数のモック"""
        return {
            'GITHUB_TOKEN': 'test_token_123',
            'GITHUB_USERNAME': 'test_user'
        }

    @pytest.fixture
    def mock_config(self):
        """設定ファイルのモック"""
        mock_config = Mock()
        return mock_config

    @pytest.fixture
    def sample_repo_data(self):
        """サンプルリポジトリデータ"""
        return [
            {
                'name': 'test-repo-1',
                'updated_at': '2024-01-15T10:00:00Z',
                'private': False
            },
            {
                'name': 'test-repo-2',
                'updated_at': '2024-01-14T15:30:00Z',
                'private': True
            }
        ]

    @pytest.fixture
    def sample_commit_data(self):
        """サンプルコミットデータ"""
        return [
            {
                'sha': 'abc123def456ghi789jkl012mno345pqr678stu901',
                'commit': {
                    'author': {
                        'name': 'Test User',
                        'email': 'test@example.com',
                        'date': '2024-01-15T10:30:00Z'
                    },
                    'message': '初期コミット\n\n詳細な説明'
                }
            },
            {
                'sha': 'def456ghi789jkl012mno345pqr678stu901vwx234',
                'commit': {
                    'author': {
                        'name': 'Test User',
                        'email': 'test@example.com',
                        'date': '2024-01-15T15:45:00Z'
                    },
                    'message': '機能追加: ユーザー認証'
                }
            }
        ]

    @pytest.fixture
    def tracker(self, mock_env_vars, mock_config):
        """GitHubCommitTrackerインスタンス"""
        with patch.dict(os.environ, mock_env_vars):
            return GitHubCommitTracker()

    def test_init_with_environment_variables(self, mock_env_vars, mock_config):
        """環境変数からの初期化テスト"""
        with patch.dict(os.environ, mock_env_vars):
            tracker = GitHubCommitTracker()

            assert tracker.token == 'test_token_123'
            assert tracker.username == 'test_user'
            assert tracker.headers['Authorization'] == 'token test_token_123'
            assert tracker.base_url == 'https://api.github.com'

    def test_init_with_parameters(self, mock_config):
        """パラメータでの初期化テスト"""
        tracker = GitHubCommitTracker(token='custom_token', username='custom_user')

        assert tracker.token == 'custom_token'
        assert tracker.username == 'custom_user'
        assert tracker.headers['Authorization'] == 'token custom_token'

    def test_init_missing_token_raises_error(self, mock_config):
        """トークンが設定されていない場合のエラーテスト"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GitHub TokenとUsernameが設定されていません"):
                GitHubCommitTracker()

    def test_init_missing_username_raises_error(self, mock_config):
        """ユーザー名が設定されていない場合のエラーテスト"""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'token'}, clear=True):
            with pytest.raises(ValueError, match="GitHub TokenとUsernameが設定されていません"):
                GitHubCommitTracker()

    @patch('requests.get')
    def test_get_user_repositories_success(self, mock_get, tracker, sample_repo_data):
        """リポジトリ取得成功テスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_repo_data
        mock_get.return_value = mock_response

        repos = tracker.get_user_repositories()

        assert len(repos) == 2
        assert repos[0]['name'] == 'test-repo-1'
        assert repos[1]['name'] == 'test-repo-2'

        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == 'https://api.github.com/user/repos'
        assert kwargs['headers']['Authorization'] == 'token test_token_123'

    @patch('requests.get')
    def test_get_user_repositories_pagination(self, mock_get, tracker, sample_repo_data):
        """リポジトリ取得のページネーションテスト"""
        # 100件の完全なページを作成してページネーションをテスト
        full_page_repos = [{'name': f'repo-{i}', 'updated_at': '2024-01-15T10:00:00Z'} for i in range(100)]

        # 最初のページ（100件フル）
        mock_response_1 = Mock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = full_page_repos

        # 2ページ目（少数）
        mock_response_2 = Mock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = sample_repo_data  # 2件

        mock_get.side_effect = [mock_response_1, mock_response_2]

        repos = tracker.get_user_repositories()

        assert len(repos) == 102  # 100 + 2
        assert mock_get.call_count == 2

    @patch('requests.get')
    def test_get_user_repositories_http_error(self, mock_get, tracker, capsys):
        """リポジトリ取得HTTPエラーテスト"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        repos = tracker.get_user_repositories()

        assert repos == []
        captured = capsys.readouterr()
        assert "リポジトリ取得エラー: 401" in captured.out

    @patch('requests.get')
    def test_get_user_repositories_network_error(self, mock_get, tracker, capsys):
        """リポジトリ取得ネットワークエラーテスト"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        repos = tracker.get_user_repositories()

        assert repos == []
        captured = capsys.readouterr()
        assert "ネットワークエラーが発生" in captured.out

    @patch('requests.get')
    def test_get_commits_for_repo_by_date_success(self, mock_get, tracker, sample_commit_data):
        """日付指定コミット取得成功テスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_commit_data
        mock_get.return_value = mock_response

        commits = tracker.get_commits_for_repo_by_date('test-repo', '2024-01-15')

        assert len(commits) == 2
        assert commits[0]['sha'] == 'abc123def456ghi789jkl012mno345pqr678stu901'

        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert 'test_user/test-repo/commits' in args[0]
        # JST 0時をUTCに変換（JST 0時 = UTC 前日15時）
        assert kwargs['params']['since'] == '2024-01-14T15:00:00Z'
        assert kwargs['params']['until'] == '2024-01-15T15:00:00Z'

    def test_get_commits_for_repo_by_date_invalid_date(self, tracker):
        """無効な日付形式のテスト"""
        with pytest.raises(ValueError, match="日付形式が不正です"):
            tracker.get_commits_for_repo_by_date('test-repo', 'invalid-date')

    @patch('requests.get')
    def test_get_commits_for_repo_by_date_repo_not_found(self, mock_get, tracker):
        """リポジトリが見つからない場合のテスト"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        commits = tracker.get_commits_for_repo_by_date('nonexistent-repo', '2024-01-15')

        assert commits == []

    @patch('requests.get')
    def test_get_commits_for_repo_by_date_http_error(self, mock_get, tracker, capsys):
        """コミット取得HTTPエラーテスト"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        commits = tracker.get_commits_for_repo_by_date('test-repo', '2024-01-15')

        assert commits == []
        captured = capsys.readouterr()
        assert "コミット取得エラー: 500" in captured.out

    @patch('requests.get')
    def test_get_commits_for_repo_by_date_network_error(self, mock_get, tracker, capsys):
        """コミット取得ネットワークエラーテスト"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        commits = tracker.get_commits_for_repo_by_date('test-repo', '2024-01-15')

        assert commits == []
        captured = capsys.readouterr()
        assert "ネットワークエラー" in captured.out

    def test_get_all_commits_by_date(self, tracker, sample_repo_data, sample_commit_data):
        """日付指定全コミット取得テスト"""
        with patch.object(tracker, 'get_user_repositories', return_value=sample_repo_data):
            with patch.object(tracker, 'get_commits_for_repo_by_date', return_value=sample_commit_data):
                all_commits = tracker.get_all_commits_by_date('2024-01-15')

                assert 'test-repo-1' in all_commits
                assert 'test-repo-2' in all_commits
                assert len(all_commits['test-repo-1']) == 2

    def test_get_all_commits_by_date_no_commits(self, tracker, sample_repo_data):
        """コミットがない場合のテスト"""
        with patch.object(tracker, 'get_user_repositories', return_value=sample_repo_data):
            with patch.object(tracker, 'get_commits_for_repo_by_date', return_value=[]):
                all_commits = tracker.get_all_commits_by_date('2024-01-15')

                assert all_commits == {}

    def test_filter_repos_by_push_date_skips_stale_repos(self, tracker):
        """since以前にしかpushのないリポジトリが除外されることのテスト"""
        repos = [
            {'name': 'active', 'pushed_at': '2024-01-15T10:00:00Z'},
            {'name': 'stale', 'pushed_at': '2023-12-01T10:00:00Z'},
            {'name': 'unknown'},  # pushed_atがない場合は除外しない
        ]

        filtered = tracker._filter_repos_by_push_date(repos, '2024-01-14T15:00:00Z')

        assert [repo['name'] for repo in filtered] == ['active', 'unknown']

    def test_get_all_commits_by_date_skips_stale_repos(self, tracker, sample_commit_data):
        """pushed_atで除外されたリポジトリにはAPI呼び出しが発生しないことのテスト"""
        repos = [
            {'name': 'active', 'pushed_at': '2024-01-15T10:00:00Z'},
            {'name': 'stale', 'pushed_at': '2023-12-01T10:00:00Z'},
        ]

        with patch.object(tracker, 'get_user_repositories', return_value=repos):
            with patch.object(tracker, 'get_commits_for_repo_by_date',
                              return_value=sample_commit_data) as mock_fetch:
                all_commits = tracker.get_all_commits_by_date('2024-01-15')

                assert list(all_commits.keys()) == ['active']
                mock_fetch.assert_called_once_with('active', '2024-01-15')

    def test_collect_commits_preserves_repo_order(self, tracker):
        """並列取得でもリポジトリ順が保たれることのテスト"""
        repos = [{'name': f'repo-{i}'} for i in range(5)]

        result = tracker._collect_commits(repos, lambda name: [{'sha': name}])

        assert list(result.keys()) == ['repo-0', 'repo-1', 'repo-2', 'repo-3', 'repo-4']

    @patch('service.github_commit_tracker.datetime')
    def test_get_today_commits(self, mock_datetime, tracker):
        """今日のコミット取得テスト"""
        mock_datetime.now.return_value.strftime.return_value = '2024-01-15'

        with patch.object(tracker, 'get_all_commits_by_date', return_value={'test-repo': []}) as mock_get_all:
            tracker.get_today_commits()
            mock_get_all.assert_called_once_with('2024-01-15')

    def test_format_commits_output_empty(self, tracker):
        """空のコミットデータのフォーマットテスト"""
        output = tracker.format_commits_output({}, '2024-01-15')
        assert "2024-01-15のコミットはありません" in output

    def test_format_commits_output_with_commits(self, tracker, sample_commit_data):
        """コミットありのフォーマットテスト"""
        commits_by_repo = {'test-repo': sample_commit_data}

        output = tracker.format_commits_output(commits_by_repo, '2024-01-15')

        assert "2024-01-15のGitHubコミット履歴 (2 件)" in output
        assert "📁 リポジトリ: test-repo" in output
        assert "初期コミット" in output
        assert "機能追加: ユーザー認証" in output

    def test_format_commits_output_malformed_date(self, tracker):
        """不正な日付形式のコミットデータのフォーマットテスト"""
        malformed_commit = {
            'sha': 'abc123',
            'commit': {
                'author': {'date': 'invalid-date'},
                'message': 'test commit'
            }
        }
        commits_by_repo = {'test-repo': [malformed_commit]}

        output = tracker.format_commits_output(commits_by_repo)

        assert "時刻不明" in output
        assert "test commit" in output

    def test_get_commits_for_diary_generation(self, tracker, sample_commit_data):
        """日誌生成用コミット取得テスト"""
        commits_by_repo = {'test-repo': sample_commit_data}

        with patch.object(tracker, 'get_all_commits_by_date', return_value=commits_by_repo):
            formatted_commits = tracker.get_commits_for_diary_generation('2024-01-15')

            assert len(formatted_commits) == 2
            assert formatted_commits[0]['repository'] == 'test-repo'
            assert '[test-repo]' in formatted_commits[0]['message']
            # タイムスタンプが降順でソートされるため、後のコミット（15:45）が最初に来る
            assert formatted_commits[0]['hash'] == 'def456ghi789jkl012mno345pqr678stu901vwx234'
            assert formatted_commits[0]['author_name'] == 'Test User'

    def test_get_commits_for_diary_generation_error_handling(self, tracker, capsys):
        """日誌生成用コミット取得のエラーハンドリングテスト"""
        malformed_commit = {
            'sha': 'abc123',
            'commit': {
                'author': {}  # 必要なキーが不足
            }
        }
        commits_by_repo = {'test-repo': [malformed_commit]}

        with patch.object(tracker, 'get_all_commits_by_date', return_value=commits_by_repo):
            formatted_commits = tracker.get_commits_for_diary_generation('2024-01-15')

            assert len(formatted_commits) == 0
            captured = capsys.readouterr()
            assert "コミット情報の変換でエラー" in captured.out

    @patch('requests.get')
    def test_get_commits_for_repo_by_date_range_success(self, mock_get, tracker, sample_commit_data):
        """日付範囲指定コミット取得成功テスト"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_commit_data
        mock_get.return_value = mock_response

        commits = tracker.get_commits_for_repo_by_date_range('test-repo', '2024-01-15', '2024-01-16')

        assert len(commits) == 2

        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        # JST 0時をUTCに変換（JST 0時 = UTC 前日15時）
        assert kwargs['params']['since'] == '2024-01-14T15:00:00Z'
        assert kwargs['params']['until'] == '2024-01-16T15:00:00Z'

    def test_get_commits_for_repo_by_date_range_invalid_date(self, tracker):
        """無効な日付範囲のテスト"""
        with pytest.raises(ValueError, match="日付形式が不正です"):
            tracker.get_commits_for_repo_by_date_range('test-repo', 'invalid', '2024-01-16')

    def test_get_all_commits_by_date_range(self, tracker, sample_repo_data, sample_commit_data):
        """日付範囲指定全コミット取得テスト"""
        with patch.object(tracker, 'get_user_repositories', return_value=sample_repo_data):
            with patch.object(tracker, 'get_commits_for_repo_by_date_range', return_value=sample_commit_data):
                all_commits = tracker.get_all_commits_by_date_range('2024-01-15', '2024-01-16')

                assert 'test-repo-1' in all_commits
                assert 'test-repo-2' in all_commits

    def test_get_all_commits_by_date_range_skips_stale_repos(self, tracker, sample_commit_data):
        """日付範囲指定でもpushed_atによる除外が効くことのテスト"""
        repos = [
            {'name': 'active', 'pushed_at': '2024-01-16T10:00:00Z'},
            {'name': 'stale', 'pushed_at': '2023-12-01T10:00:00Z'},
        ]

        with patch.object(tracker, 'get_user_repositories', return_value=repos):
            with patch.object(tracker, 'get_commits_for_repo_by_date_range',
                              return_value=sample_commit_data) as mock_fetch:
                all_commits = tracker.get_all_commits_by_date_range('2024-01-15', '2024-01-16')

                assert list(all_commits.keys()) == ['active']
                mock_fetch.assert_called_once_with('active', '2024-01-15', '2024-01-16')

    def test_get_commits_for_diary_generation_range_single_date(self, tracker):
        """日誌生成用コミット取得（単一日付）テスト"""
        with patch.object(tracker, 'get_commits_for_diary_generation', return_value=[]) as mock_single:
            tracker.get_commits_for_diary_generation_range('2024-01-15')
            mock_single.assert_called_once_with('2024-01-15')

    def test_get_commits_for_diary_generation_range_date_range(self, tracker, sample_commit_data):
        """日誌生成用コミット取得（日付範囲）テスト"""
        commits_by_repo = {'test-repo': sample_commit_data}

        with patch.object(tracker, 'get_all_commits_by_date_range', return_value=commits_by_repo):
            formatted_commits = tracker.get_commits_for_diary_generation_range('2024-01-15', '2024-01-16')

            assert len(formatted_commits) == 2
            # 日時順（降順）でソートされているかチェック
            assert formatted_commits[0]['timestamp'] >= formatted_commits[1]['timestamp']

    def test_get_commits_for_diary_generation_range_error_handling(self, tracker, capsys):
        """日誌生成用コミット取得（範囲）のエラーハンドリングテスト"""
        malformed_commit = {
            'sha': 'abc123',
            'commit': {
                'author': {'date': 'invalid-date'}
            }
        }
        commits_by_repo = {'test-repo': [malformed_commit]}

        with patch.object(tracker, 'get_all_commits_by_date_range', return_value=commits_by_repo):
            formatted_commits = tracker.get_commits_for_diary_generation_range('2024-01-15', '2024-01-16')

            assert len(formatted_commits) == 0
            captured = capsys.readouterr()
            assert "コミット情報の変換でエラー" in captured.out

    @pytest.mark.parametrize("status_code,expected_empty", [
        (200, False),
        (404, True),
        (401, True),
        (500, True)
    ])
    @patch('requests.get')
    def test_get_commits_status_codes(self, mock_get, tracker, status_code, expected_empty):
        """様々なHTTPステータスコードのテスト"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json.return_value = [{'test': 'data'}] if status_code == 200 else []
        mock_get.return_value = mock_response

        commits = tracker.get_commits_for_repo_by_date('test-repo', '2024-01-15')

        if expected_empty:
            assert commits == []
        else:
            assert len(commits) == 1

    def test_commit_sorting_by_timestamp(self, tracker):
        """タイムスタンプでのコミットソートテスト"""
        commits_data = [
            {
                'sha': 'first',
                'commit': {
                    'author': {
                        'name': 'User',
                        'email': 'user@example.com',
                        'date': '2024-01-15T10:00:00Z'
                    },
                    'message': 'First commit'
                }
            },
            {
                'sha': 'second',
                'commit': {
                    'author': {
                        'name': 'User',
                        'email': 'user@example.com',
                        'date': '2024-01-15T12:00:00Z'
                    },
                    'message': 'Second commit'
                }
            }
        ]

        commits_by_repo = {'test-repo': commits_data}

        with patch.object(tracker, 'get_all_commits_by_date', return_value=commits_by_repo):
            formatted_commits = tracker.get_commits_for_diary_generation('2024-01-15')

            # 降順でソートされているかチェック（新しい順）
            assert len(formatted_commits) == 2
            assert 'Second commit' in formatted_commits[0]['message']
            assert 'First commit' in formatted_commits[1]['message']