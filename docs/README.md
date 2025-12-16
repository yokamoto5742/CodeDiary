# CodeDiary

Gitコミット履歴を生成AIで解析し、構造化されたプログラミング日誌を自動生成するWindowsデスクトップアプリケーション。Claude、OpenAI、Geminiなど複数のAIプロバイダーに対応し、Google Formへの自動入力にも対応しています。

## 主要機能

- **Gitコミット履歴の自動解析**: 指定期間内のコミット履歴を自動抽出
- **複数AIプロバイダー対応**: Claude、OpenAI、Geminiをサポート
- **自動フォールバック**: メインプロバイダー失敗時に自動切り替え
- **GitHub連携**: 複数リポジトリの横断コミット履歴取得
- **Google Form自動入力**: 生成された日誌のワンクリック送信

## 前提条件と要件

### システム要件

- **OS**: Windows 10以降
- **Python**: 3.11以降
- **Git**: インストール済み（コミット履歴取得に必須）
- **Google Chrome**: Google Form自動入力機能に使用（オプション）

### 必要なAPIキー

以下のうち少なくとも1つが必須：

- **Claude API**: Anthropic社のAPIキー
- **OpenAI API**: OpenAI社のAPIキー
- **Gemini API**: Google社のAPIキー

## インストール手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd CodeDiary
```

### 2. 仮想環境の構築

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

プロジェクトルートに`.env`ファイルを作成：

```env
# Claude API（推奨）
CLAUDE_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-3-5-haiku-20241022

# OpenAI API
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Gemini API
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# GitHub連携（オプション）
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_github_username
```

### 5. 初期設定

アプリケーション起動時に`utils/config.ini`が自動作成されます。

## 使用方法

### 基本的な使い方

```bash
# アプリケーション起動
python main.py
```

UIから以下の操作を実行：

1. **Gitリポジトリ設定**: 対象リポジトリフォルダを選択
2. **期間指定**: カレンダーで開始日・終了日を選択
3. **日誌生成**:
   - 「日誌作成」: ローカルGitコミット履歴から生成
   - 「GitHub連携日記作成」: 全リポジトリから生成
4. **結果の利用**:
   - 自動的にクリップボードにコピー
   - Google Formに自動入力可能

### AIプロバイダー設定

`utils/config.ini`で設定：

```ini
[AI]
provider = openai          # メインプロバイダー: claude, openai, gemini
fallback_provider = gemini # フォールバック先
```

### Google Form設定

```ini
[URL]
form_url = https://forms.gle/your_form_id
```

### UI設定

```ini
[DiaryText]
font = メイリオ
font_size = 11

[WindowSettings]
window_width = 800
window_height = 600

[Chrome]
chrome_path = C:\Program Files\Google\Chrome\Application\chrome.exe
```

## プロジェクト構造

```
CodeDiary/
├── main.py                     # エントリーポイント
├── requirements.txt            # 依存関係
├── app/
│   └── main_window.py          # メインUIコントローラー
├── external_service/
│   ├── api_factory.py          # AIプロバイダーファクトリ
│   ├── base_api.py             # 基底APIクライアント
│   ├── claude_api.py           # Claude APIクライアント
│   ├── gemini_api.py           # Gemini APIクライアント
│   └── openai_api.py           # OpenAI APIクライアント
├── service/
│   ├── git_commit_history.py   # Gitコミット履歴取得
│   ├── github_commit_tracker.py # GitHub API連携
│   ├── programming_diary_generator.py # 日誌生成エンジン
│   └── launch_form_page.py     # Google Form自動入力
├── utils/
│   ├── config.ini              # 設定ファイル
│   ├── config_manager.py       # 設定管理
│   ├── env_loader.py           # 環境変数読み込み
│   ├── prompt_template.md      # AIプロンプトテンプレート
│   └── repository_name_extractor.py # リポジトリ名抽出
├── widgets/
│   ├── date_selection_widget.py # 日付選択ウィジェット
│   ├── diary_content_widget.py  # 日誌表示ウィジェット
│   ├── control_buttons_widget.py # ボタンウィジェット
│   └── progress_widget.py       # 進捗表示ウィジェット
├── scripts/
│   ├── project_structure.py    # プロジェクト構造出力
│   └── version_manager.py      # バージョン管理
└── tests/                      # テストスイート
```

## 主要機能の説明

### アーキテクチャ

CodeDiaryはモジュール化されたMVC風アーキテクチャを採用：

- **UI層** (`app/`, `widgets/`): Tkinter UIコンポーネント
- **ビジネスロジック層** (`service/`): 日誌生成、Git操作、Google Form自動化
- **AI統合層** (`external_service/`): Factory Patternで複数AIプロバイダーを統一インターフェースで利用
- **設定管理層** (`utils/`): 環境変数とINIファイルの統合管理

### ProgrammingDiaryGenerator クラス

コミット履歴をAIで解析して日誌を生成：

```python
from service.programming_diary_generator import ProgrammingDiaryGenerator

generator = ProgrammingDiaryGenerator()

# ローカルGitから生成
diary, input_tokens, output_tokens = generator.generate_diary(
    since_date="2024-01-01",
    until_date="2024-01-07"
)

# GitHub連携で生成
diary, input_tokens, output_tokens = generator.generate_diary(
    since_date="2024-01-01",
    use_github=True
)
```

### API Factory パターン

複数のAIプロバイダーを動的に切り替え：

```python
from external_service.api_factory import APIFactory

# プロバイダーを動的に選択
client = APIFactory.create_client("claude")  # "openai", "gemini"も可
client.initialize()
content, input_tokens, output_tokens = client.generate_content(
    prompt="...",
    model_name="claude-3-5-haiku-20241022"
)
```

### GitCommitHistoryService クラス

Gitコマンドでコミット履歴を取得：

```python
from service.git_commit_history import GitCommitHistoryService

service = GitCommitHistoryService()
commits = service.get_commit_history(
    since_date="2024-01-01",
    until_date="2024-01-31",
    author="username"  # オプション
)
```

## 開発者向け情報

### 開発環境セットアップ

テストとビルドのセットアップ：

```bash
# テストフレームワークのインストール
pip install pytest pytest-cov

# テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=service --cov=external_service --cov=utils

# 特定テストの実行
pytest tests/test_programming_diary_generator.py -v
```

### ビルド

実行ファイル化：

```bash
# ビルド（バージョン自動更新）
python build.py
```

### プロジェクト構造確認

```bash
# プロジェクト構造出力
python scripts/project_structure.py

# バージョン情報更新
python scripts/version_manager.py
```

### 拡張方法

**新しいAIプロバイダーの追加**:

1. `external_service/`に新しいクライアント作成（`BaseAPIClient`継承）
2. `generate_content`メソッドを実装
3. `api_factory.py`の`APIProvider`に追加

**UIウィジェット追加**:

1. `widgets/`に新規ウィジェット作成
2. `main_window.py`で統合

## トラブルシューティング

### APIキーエラー

```
APIError: 未対応のAPIプロバイダー
```

**解決策**:
- `.env`ファイルを確認（プロジェクトルートに配置）
- 少なくとも1つのAPIキーが有効か確認
- `config.ini`の`provider`設定が正しいか確認

### Gitコミット履歴が取得できない

**解決策**:
- リポジトリパスが正しいか確認
- Gitがインストール済みか確認（`git --version`）
- リポジトリへの読み取り権限確認

### Google Form自動入力が動作しない

**解決策**:
- Chromeのインストールパスを確認
- `config.ini`の`form_url`が正しいか確認
- Playwright操作タイムアウト（ネットワーク遅延などを確認）

### 日本語が文字化けする

**解決策**:
- システムロケール設定確認
- `config.ini`の`font`設定を確認（メイリオなど）

## バージョン情報

- **現在のバージョン**: 1.1.4
- **最終更新**: 2025年12月15日
- **対応Python**: 3.11以降
- **対応OS**: Windows 10以降

## ライセンス

LICENSEファイルを参照してください。

## サポート

問題や要望は以下の方法でお問い合わせください：

- GitHub Issues: プロジェクトのIssueページ
- CLAUDE.md: プロジェクト開発ガイド
