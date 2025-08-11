import os
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


# テスト実行時のパス設定
def pytest_configure(config):
    """PyTest設定時に実行される関数"""
    # プロジェクトルートをPythonパスに追加
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """テスト環境のセットアップ（セッション全体で一度だけ実行）"""
    # 環境変数のモック設定
    test_env_vars = {
        'CLAUDE_API_KEY': 'test_claude_key',
        'CLAUDE_MODEL': 'claude-3-haiku-20240307',
        'OPENAI_API_KEY': 'test_openai_key', 
        'OPENAI_MODEL': 'gpt-3.5-turbo',
        'GEMINI_API_KEY': 'test_gemini_key',
        'GEMINI_MODEL': 'gemini-1.5-flash',
        'GEMINI_THINKING_BUDGET': '1024'
    }
    
    # 既存の環境変数をバックアップ
    original_env = {}
    for key, value in test_env_vars.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # 環境変数を元に戻す
    for key, original_value in original_env.items():
        if original_value is not None:
            os.environ[key] = original_value
        elif key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_datetime():
    """datetimeオブジェクトのモック"""
    from datetime import datetime, timezone, timedelta
    
    # 固定日時（JST）
    fixed_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone(timedelta(hours=9)))
    
    mock_dt = Mock()
    mock_dt.now.return_value = fixed_datetime
    mock_dt.fromisoformat = datetime.fromisoformat
    mock_dt.strftime = lambda self, fmt: fixed_datetime.strftime(fmt)
    
    return mock_dt


@pytest.fixture
def mock_config_basic():
    """基本的な設定ファイルのモック"""
    mock_config = Mock()
    
    # デフォルト設定値
    config_values = {
        ('GIT', 'repository_path'): '/mock/repo/path',
        ('AI', 'provider'): 'claude',
        ('AI', 'fallback_provider'): 'openai',
        ('Chrome', 'chrome_path'): 'C:/Program Files/Google/Chrome/Application/chrome.exe',
        ('URL', 'form_url'): 'https://forms.gle/test123',
        ('WindowSettings', 'window_width'): '800',
        ('WindowSettings', 'window_height'): '600',
        ('DiaryText', 'font'): 'メイリオ',
        ('DiaryText', 'font_size'): '11'
    }
    
    def mock_get(section, key, fallback=None):
        return config_values.get((section, key), fallback)
    
    mock_config.get = mock_get
    mock_config.has_section.return_value = True
    mock_config.add_section = Mock()
    mock_config.set = Mock()
    
    return mock_config


@pytest.fixture
def mock_git_commits():
    """テスト用のGitコミットデータ"""
    return [
        {
            'hash': 'abc123def456',
            'author_name': 'Test User',
            'author_email': 'test@example.com',
            'timestamp': '2024-01-15T10:00:00+09:00',
            'message': '初期コミット'
        },
        {
            'hash': 'def456ghi789',
            'author_name': 'Another User',
            'author_email': 'another@example.com',
            'timestamp': '2024-01-15T15:30:00+09:00',
            'message': '機能追加: ユーザー認証機能を実装'
        },
        {
            'hash': 'ghi789jkl012',
            'author_name': 'Test User',
            'author_email': 'test@example.com',
            'timestamp': '2024-01-16T09:15:00+09:00',
            'message': 'バグ修正: ログイン時のエラーハンドリング改善'
        }
    ]


@pytest.fixture
def mock_prompt_template():
    """テスト用のプロンプトテンプレート"""
    return """
あなたは経験豊富なソフトウェア開発者です。提供されたGitコミット履歴を構造化された日誌形式に変換してください。

# 日誌作成要件

## 出力形式
yyyy年m月d日(aaa)
{{カゴテリー1}}
1.概要
{{概要}}
2.変更ファイル
{{変更ファイル}}
3.詳細
{{詳細}}

提供されたコミット履歴から上記の形式で開発日誌を作成してください。
"""


@pytest.fixture
def sample_markdown_diary():
    """サンプルのMarkdown形式日誌"""
    return """
# 2024年1月15日(月)

## 機能追加
1. 概要
ユーザー認証機能を実装

2. 変更ファイル
- service/auth_service.py
- app/login_window.py

3. 詳細
- **ログイン画面**の実装
- *セッション管理*機能の追加
- `JWT`トークン認証の実装

## バグ修正
1. 概要
ログイン時のエラーハンドリング改善

2. 変更ファイル
- utils/error_handler.py

3. 詳細
- 例外処理の改善
- エラーメッセージの国際化対応

```python
def handle_login_error(error):
    logger.error(f"Login failed: {error}")
    return {"status": "error", "message": str(error)}
```

---
"""


@pytest.fixture
def mock_subprocess_result():
    """subprocess実行結果のモック"""
    def create_result(returncode=0, stdout="", stderr=""):
        result = Mock()
        result.returncode = returncode
        result.stdout = stdout
        result.stderr = stderr
        return result
    
    return create_result


@pytest.fixture
def temporary_directory(tmp_path):
    """テスト用の一時ディレクトリ"""
    return tmp_path


# テスト失敗時のデバッグ情報を改善
def pytest_runtest_makereport(item, call):
    """テスト実行結果のレポート作成"""
    if call.when == "call" and call.excinfo is not None:
        # テスト失敗時に詳細な情報を出力
        print(f"\n=== Test Failed: {item.name} ===")
        print(f"Exception: {call.excinfo.value}")
        if hasattr(call.excinfo.value, '__cause__') and call.excinfo.value.__cause__:
            print(f"Caused by: {call.excinfo.value.__cause__}")


# カスタムマーカーの定義
def pytest_configure(config):
    """カスタムマーカーの登録"""
    config.addinivalue_line("markers", "unit: ユニットテストマーカー")
    config.addinivalue_line("markers", "integration: 統合テストマーカー")
    config.addinivalue_line("markers", "slow: 実行時間の長いテストマーカー")
    config.addinivalue_line("markers", "external: 外部依存を含むテストマーカー")


# pytest実行時のワーニング抑制
@pytest.fixture(autouse=True)
def suppress_warnings():
    """不要なワーニングを抑制"""
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
