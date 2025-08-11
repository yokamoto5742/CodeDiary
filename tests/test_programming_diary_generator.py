import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

import pytest

from service.programming_diary_generator import ProgrammingDiaryGenerator


class TestProgrammingDiaryGenerator:
    """ProgrammingDiaryGeneratorクラスのテストクラス"""

    @pytest.fixture
    def mock_config(self):
        """設定ファイルのモック"""
        mock_config = Mock()
        mock_config.get.return_value = "/mock/repo/path"
        return mock_config

    @pytest.fixture
    def mock_git_service(self):
        """GitCommitHistoryServiceのモック"""
        mock_service = Mock()
        mock_service.get_repository_info.return_value = {
            'current_branch': 'main',
            'latest_commit': 'abc123 by Test User on 2024-01-01'
        }
        mock_service.get_commit_history.return_value = [
            {
                'hash': 'abc123',
                'author_name': 'Test User',
                'timestamp': '2024-01-01T10:00:00+09:00',
                'message': 'Initial commit'
            }
        ]
        return mock_service

    @pytest.fixture
    def mock_ai_client(self):
        """AIクライアントのモック"""
        mock_client = Mock()
        mock_client.default_model = 'test-model'
        mock_client.initialize.return_value = True
        mock_client._generate_content.return_value = (
            "# テスト日誌\n\n**機能追加**\n- 初期コミット実装",
            100,  # input_tokens
            200   # output_tokens
        )
        return mock_client

    @pytest.fixture
    def generator(self, mock_config, mock_git_service, mock_ai_client):
        """ProgrammingDiaryGeneratorのインスタンス作成"""
        with patch('service.programming_diary_generator.load_environment_variables'), \
             patch('service.programming_diary_generator.load_config', return_value=mock_config), \
             patch('service.programming_diary_generator.GitCommitHistoryService', return_value=mock_git_service), \
             patch('service.programming_diary_generator.get_active_provider', return_value='claude'), \
             patch('service.programming_diary_generator.APIFactory.create_client', return_value=mock_ai_client), \
             patch('service.programming_diary_generator.get_provider_credentials', return_value={'model': 'test-model'}), \
             patch.object(Path, 'parent', Path('/mock/path')):
            
            generator = ProgrammingDiaryGenerator()
            return generator

    def test_init_success(self, mock_config, mock_git_service, mock_ai_client):
        """正常な初期化のテスト"""
        with patch('service.programming_diary_generator.load_environment_variables'), \
             patch('service.programming_diary_generator.load_config', return_value=mock_config), \
             patch('service.programming_diary_generator.GitCommitHistoryService', return_value=mock_git_service), \
             patch('service.programming_diary_generator.get_active_provider', return_value='claude'), \
             patch('service.programming_diary_generator.APIFactory.create_client', return_value=mock_ai_client), \
             patch('service.programming_diary_generator.get_provider_credentials', return_value={'model': 'test-model'}), \
             patch.object(Path, 'parent', Path('/mock/path')):
            
            generator = ProgrammingDiaryGenerator()
            
            assert generator.ai_provider == 'claude'
            assert generator.ai_client == mock_ai_client
            assert generator.default_model == 'test-model'
            assert generator.jst == timezone(timedelta(hours=9))

    def test_init_provider_initialization_error(self, mock_config, mock_git_service):
        """AIプロバイダー初期化エラーのテスト"""
        with patch('service.programming_diary_generator.load_environment_variables'), \
             patch('service.programming_diary_generator.load_config', return_value=mock_config), \
             patch('service.programming_diary_generator.GitCommitHistoryService', return_value=mock_git_service), \
             patch('service.programming_diary_generator.get_active_provider', side_effect=Exception("Provider error")):
            
            with pytest.raises(Exception):
                ProgrammingDiaryGenerator()

    def test_get_prompt_template_path(self, generator):
        """プロンプトテンプレートパス取得のテスト"""
        expected_path = str(Path(generator.prompt_template_path))
        assert "prompt_template.md" in expected_path

    def test_load_prompt_template_success(self, generator):
        """プロンプトテンプレート読み込みの正常系テスト"""
        mock_content = "テスト用プロンプトテンプレート"
        
        with patch('builtins.open', mock_open(read_data=mock_content)):
            result = generator._load_prompt_template()
            assert result == mock_content

    def test_load_prompt_template_file_not_found(self, generator):
        """プロンプトテンプレートファイルが見つからない場合のテスト"""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            with pytest.raises(Exception, match="プロンプトテンプレートファイルが見つかりません"):
                generator._load_prompt_template()

    def test_load_prompt_template_read_error(self, generator):
        """プロンプトテンプレート読み込みエラーのテスト"""
        with patch('builtins.open', side_effect=IOError("Read error")):
            with pytest.raises(Exception, match="プロンプトテンプレートの読み込みに失敗しました"):
                generator._load_prompt_template()

    def test_format_commits_for_prompt_success(self, generator):
        """コミットのプロンプト用フォーマットの正常系テスト"""
        commits = [
            {
                'timestamp': '2024-01-01T10:00:00+09:00',
                'message': '初期コミット'
            },
            {
                'timestamp': '2024-01-02T15:30:00+09:00',
                'message': '機能追加'
            }
        ]

        result = generator._format_commits_for_prompt(commits)

        assert "2024年01月01日(月)" in result
        assert "2024年01月02日(火)" in result
        assert "初期コミット" in result
        assert "機能追加" in result

    def test_format_commits_for_prompt_empty(self, generator):
        """空のコミットリストの場合のテスト"""
        result = generator._format_commits_for_prompt([])
        assert result == "コミット履歴がありません。"

    def test_format_commits_for_prompt_invalid_timestamp(self, generator):
        """不正なタイムスタンプの場合のテスト"""
        commits = [{
            'timestamp': 'invalid-timestamp',
            'message': 'テストコミット'
        }]

        result = generator._format_commits_for_prompt(commits)
        assert "invalid-timestamp" in result
        assert "テストコミット" in result

    def test_convert_markdown_to_plain_text(self, generator):
        """Markdownからプレーンテキストへの変換テスト"""
        markdown_text = """
# タイトル
## サブタイトル

**太字テキスト** と *斜体テキスト*

- 箇条書き1
- 箇条書き2

1. 番号付きリスト1
2. 番号付きリスト2

```python
print("コードブロック")
```

`インラインコード`

---

連続する改行


テスト
        """

        result = generator._convert_markdown_to_plain_text(markdown_text)

        # マークダウン記号が除去されていることを確認
        assert "# " not in result
        assert "**" not in result
        assert "- " not in result.split('\n')[0]  # 最初の行に箇条書き記号がないことを確認
        assert "```" not in result
        assert "`" not in result
        assert "太字テキスト" in result
        assert "斜体テキスト" in result
        assert "インラインコード" in result

    @patch('service.programming_diary_generator.get_repository_directory_name')
    def test_generate_diary_success(self, mock_get_repo_name, generator, mock_git_service, mock_ai_client):
        """日誌生成の正常系テスト"""
        # モックの準備
        mock_get_repo_name.return_value = "TestProject"
        mock_template = "テスト用プロンプトテンプレート"
        
        with patch.object(generator, '_load_prompt_template', return_value=mock_template):
            # テスト実行
            result, input_tokens, output_tokens = generator.generate_diary(
                since_date="2024-01-01",
                until_date="2024-01-02"
            )

        # 検証
        assert "TestProject" in result
        assert input_tokens == 100
        assert output_tokens == 200
        mock_ai_client.initialize.assert_called_once()
        mock_ai_client._generate_content.assert_called_once()
        mock_git_service.get_commit_history.assert_called_once_with(
            since_date="2024-01-01",
            until_date="2024-01-02",
            author=None,
            max_count=None
        )

    def test_generate_diary_with_days_parameter(self, generator, mock_git_service, mock_ai_client):
        """days パラメータを使用した日誌生成のテスト"""
        mock_template = "テスト用プロンプトテンプレート"
        
        # 固定日時でテスト
        fixed_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone(timedelta(hours=9)))
        
        with patch.object(generator, '_load_prompt_template', return_value=mock_template), \
             patch('service.programming_diary_generator.datetime') as mock_datetime, \
             patch('service.programming_diary_generator.get_repository_directory_name', return_value="TestProject"):
            
            mock_datetime.now.return_value = fixed_datetime
            
            # テスト実行
            result, input_tokens, output_tokens = generator.generate_diary(days=7)

        # 検証
        mock_git_service.get_commit_history.assert_called_once()
        call_args = mock_git_service.get_commit_history.call_args
        assert call_args[1]['since_date'] == "2024-01-08"  # 7日前
        assert call_args[1]['until_date'] == "2024-01-16"   # 翌日

    @patch('service.programming_diary_generator.get_repository_directory_name')
    def test_generate_diary_repository_name_error(self, mock_get_repo_name, generator, mock_ai_client):
        """リポジトリ名取得エラーのテスト"""
        # モックの準備
        mock_get_repo_name.side_effect = Exception("Repository name error")
        mock_template = "テスト用プロンプトテンプレート"
        
        with patch.object(generator, '_load_prompt_template', return_value=mock_template):
            # テスト実行（エラーは内部でキャッチされる）
            result, input_tokens, output_tokens = generator.generate_diary()

        # プロジェクト名なしでも結果が返されることを確認
        assert result is not None
        assert input_tokens == 100
        assert output_tokens == 200

    def test_generate_diary_ai_client_error(self, generator, mock_ai_client):
        """AIクライアントエラー時のテスト"""
        # モックの準備
        mock_ai_client.initialize.side_effect = Exception("AI client error")
        mock_template = "テスト用プロンプトテンプレート"
        
        with patch.object(generator, '_load_prompt_template', return_value=mock_template), \
             patch.object(generator, '_try_fallback_provider', side_effect=Exception("Fallback failed")):
            
            # テスト実行と検証
            with pytest.raises(Exception):
                generator.generate_diary()

    def test_try_fallback_provider_success(self, generator):
        """フォールバックプロバイダーの正常系テスト"""
        mock_fallback_client = Mock()
        mock_fallback_client.default_model = 'fallback-model'
        mock_fallback_client._generate_content.return_value = ("fallback diary", 50, 100)
        
        with patch('service.programming_diary_generator.get_ai_provider_config', return_value={'fallback_provider': 'openai'}), \
             patch('service.programming_diary_generator.get_available_providers', return_value={'openai': True}), \
             patch('service.programming_diary_generator.APIFactory.create_client', return_value=mock_fallback_client), \
             patch('service.programming_diary_generator.get_provider_credentials', return_value={'model': 'fallback-model'}), \
             patch.object(generator, 'generate_diary', return_value=("fallback diary", 50, 100)):
            
            result = generator._try_fallback_provider(
                since_date="2024-01-01",
                until_date="2024-01-02",
                days=None,
                author=None,
                max_count=None,
                original_error="Original error"
            )
            
            assert result == ("fallback diary", 50, 100)

    def test_try_fallback_provider_no_fallback_available(self, generator):
        """フォールバックプロバイダーが利用できない場合のテスト"""
        with patch('service.programming_diary_generator.get_ai_provider_config', return_value={'fallback_provider': 'unavailable'}), \
             patch('service.programming_diary_generator.get_available_providers', return_value={'unavailable': False}):
            
            with pytest.raises(Exception, match="プロバイダーエラー \\(フォールバック不可\\)"):
                generator._try_fallback_provider(
                    since_date="2024-01-01",
                    until_date="2024-01-02",
                    days=None,
                    author=None,
                    max_count=None,
                    original_error="Original error"
                )

    def test_try_fallback_provider_fallback_error(self, generator):
        """フォールバックプロバイダーでもエラーが発生する場合のテスト"""
        with patch('service.programming_diary_generator.get_ai_provider_config', return_value={'fallback_provider': 'openai'}), \
             patch('service.programming_diary_generator.get_available_providers', return_value={'openai': True}), \
             patch('service.programming_diary_generator.APIFactory.create_client', side_effect=Exception("Fallback creation error")):
            
            with pytest.raises(Exception, match="プログラミング日誌の生成に失敗しました"):
                generator._try_fallback_provider(
                    since_date="2024-01-01",
                    until_date="2024-01-02",
                    days=None,
                    author=None,
                    max_count=None,
                    original_error="Original error"
                )

    def test_markdown_conversion_comprehensive(self, generator):
        """Markdown変換の包括的テスト"""
        markdown_text = """
### ヘッダー3

__下線太字__ と _下線斜体_

* アスタリスク箇条書き1
+ プラス箇条書き1

3. 番号付きリスト開始番号3
4. 番号付きリスト4

```javascript
console.log("JavaScript code");
```

水平線テスト:
---
---
-----

複数改行テスト:



改行後のテキスト
        """

        result = generator._convert_markdown_to_plain_text(markdown_text)

        # 様々なMarkdown要素が適切に変換されることを確認
        assert "###" not in result
        assert "__" not in result
        assert "```" not in result
        assert "---" in result  # 水平線は保持される
        assert "下線太字" in result
        assert "下線斜体" in result
        assert "console.log" in result
        
        # 連続する改行が適切に処理されることを確認
        lines = result.split('\n')
        consecutive_empty = 0
        max_consecutive_empty = 0
        for line in lines:
            if not line.strip():
                consecutive_empty += 1
                max_consecutive_empty = max(max_consecutive_empty, consecutive_empty)
            else:
                consecutive_empty = 0
        
        # 3つ以上連続する空行がないことを確認
        assert max_consecutive_empty <= 2
