# CodeDiary

Gitコミット履歴を生成AIで解析し、構造化されたプログラミング日誌を自動生成するWindowsデスクトップアプリケーション。Claude、OpenAI、Geminiなど複数のAIプロバイダーに対応しています。

## 主要機能

- **Gitコミット履歴の自動解析**: 指定期間内のコミット履歴を自動抽出
- **複数AIプロバイダー対応**: Claude、OpenAI、Geminiをサポート
- **自動フォールバック**: メインプロバイダー失敗時に自動切り替え
- **GitHub連携**: 複数リポジトリの横断コミット履歴取得
- **ウィンドウ位置・サイズ保存**: UI状態の自動復元

## 前提条件と要件

### システム要件

- **OS**: Windows 11以降
- **Python**: 3.12以降
- **Git**: インストール済み（コミット履歴取得に必須）
- **Google Chrome**: Googleフォーム起動時に使用

### 必要なAPIキー

以下のうち少なくとも1つが必須：

- **Claude API**: Anthropic社のAPIキー
- **OpenAI API**: OpenAI社のAPIキー（推奨）
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
   - 日誌用Google Formを開く

### 設定ファイル（config.ini）

#### AIプロバイダー設定

```ini
[AI]
provider = claude          # メインプロバイダー: claude, openai, gemini
fallback_provider = gemini # フォールバック先
```

#### Google Form設定

```ini
[URL]
form_url = https://forms.gle/your_form_id
```

#### UI設定

```ini
[DiaryText]
font = メイリオ
font_size = 11

[WindowSettings]
window_width = 800
window_height = 600
window_x = 100           # ウィンドウX位置（自動保存）
window_y = 100           # ウィンドウY位置（自動保存）

[Chrome]
chrome_path = C:\Program Files\Google\Chrome\Application\chrome.exe
```

## プロジェクト構造

```
CodeDiary/
├── main.py                           # エントリーポイント
├── build.py                          # PyInstaller実行ファイル化スクリプト
├── requirements.txt                  # Python依存関係
│
├── app/
│   ├── __init__.py                  # バージョン情報
│   └── main_window.py               # メインUIコントローラー
│
├── external_service/                # AI統合層（Factory Pattern）
│   ├── api_factory.py               # AIプロバイダーファクトリ
│   ├── base_api.py                  # 基底APIクライアント
│   ├── claude_api.py                # Claude APIクライアント
│   ├── gemini_api.py                # Gemini APIクライアント
│   └── openai_api.py                # OpenAI APIクライアント
│
├── service/                          # ビジネスロジック層
│   ├── git_commit_history.py        # Gitコミット履歴取得
│   ├── github_commit_tracker.py     # GitHub API連携
│   ├── programming_diary_generator.py # 日誌生成エンジン
│   └── launch_form_page.py          # Google Form自動入力
│
├── utils/                            # 設定・ユーティリティ層
│   ├── config.ini                   # アプリケーション設定
│   ├── config_manager.py            # 設定管理
│   ├── constants.py                 # 定数定義
│   ├── env_loader.py                # 環境変数読み込み
│   ├── exceptions.py                # カスタム例外
│   ├── prompt_template.md           # AIプロンプトテンプレート
│   └── repository_name_extractor.py # リポジトリ名抽出
│
├── widgets/                          # UI層（Tkinter）
│   ├── date_selection_widget.py     # 日付選択ウィジェット
│   ├── diary_content_widget.py      # 日誌表示ウィジェット
│   ├── control_buttons_widget.py    # ボタンウィジェット
│   └── progress_widget.py           # 進捗表示ウィジェット
│
├── scripts/                          # 開発支援スクリプト
│   ├── project_structure.py         # プロジェクト構造出力
│   ├── version_manager.py           # バージョン管理
│   └── APIsetting_check.py          # API設定確認
│
└── tests/                            # テストスイート
    ├── test_programming_diary_generator.py
    ├── test_git_commit_history.py
    ├── test_github_commit_tracker.py
    ├── test_launch_form_page.py
    ├── test_main_window.py
    └── ...
```

## アーキテクチャ

CodeDiaryはモジュール化されたMVC風アーキテクチャを採用しており、各層が独立して動作します。

### レイヤー構成

#### UI層（`app/`、`widgets/`）

Tkinterを使用したUIコンポーネント：

- **MainWindow**: アプリケーション全体のレイアウト管理とイベント処理
- **DateSelectionWidget**: カレンダーベースの日付範囲選択
- **DiaryContentWidget**: 生成された日誌の表示とクリップボード操作
- **ControlButtonsWidget**: アクション実行ボタン
- **ProgressWidget**: タスク進捗の表示

#### ビジネスロジック層（`service/`）

- **ProgrammingDiaryGenerator**: Gitコミット履歴とAI統合による日誌生成
- **GitCommitHistoryService**: Gitコマンド実行とコミット履歴抽出
- **GitHubCommitTracker**: GitHub APIを使用した複数リポジトリの横断取得
- **GoogleFormLauncher**: Googleフォームの起動

#### AI統合層（`external_service/`）

Factory Patternを使用した複数AIプロバイダーの抽象化：

```python
# 動的なプロバイダー選択
client = APIFactory.create_client("claude")  # "openai", "gemini"も可
client.initialize()
content, input_tokens, output_tokens = client.generate_content(
    prompt="...",
    model_name="claude-3-5-haiku-20241022"
)
```

- **BaseAPIClient**: 共通インターフェース定義
- **ClaudeAPI**: Anthropic Claude統合
- **OpenAIAPI**: OpenAI GPT統合
- **GeminiAPI**: Google Gemini統合

#### 設定管理層（`utils/`）

- **ConfigManager**: `config.ini`とINI設定ファイル管理
- **EnvLoader**: `.env`ファイルの環境変数読み込み
- **RepositoryNameExtractor**: リポジトリ名抽出ユーティリティ

### デザインパターン

1. **Factory Pattern**: `external_service/api_factory.py`でAIプロバイダーを動的に選択
2. **Template Method**: 日誌生成ワークフローの標準化
3. **Strategy Pattern**: 複数AIプロバイダーが共通インターフェースを実装
4. **Configuration Management**: 環境変数とINI設定の統合管理

## 主要機能の詳細

### ProgrammingDiaryGeneratorクラス

Gitコミット履歴をAIで解析して構造化された日誌を生成します。

```python
from service.programming_diary_generator import ProgrammingDiaryGenerator

generator = ProgrammingDiaryGenerator()

# ローカルGitコミット履歴から生成
diary, input_tokens, output_tokens = generator.generate_diary(
    since_date="2024-01-01",
    until_date="2024-01-07"
)

# GitHub連携で全リポジトリから生成
diary, input_tokens, output_tokens = generator.generate_diary(
    since_date="2024-01-01",
    use_github=True
)
```

**パラメータ**:
- `since_date`: 開始日付（ISO 8601形式）
- `until_date`: 終了日付（オプション、指定なしは当日）
- `use_github`: True時はGitHub APIを使用

**戻り値**: (日誌テキスト, 入力トークン数, 出力トークン数)

### GitCommitHistoryServiceクラス

Gitコマンドを使用してコミット履歴を取得します。

```python
from service.git_commit_history import GitCommitHistoryService

service = GitCommitHistoryService()
commits = service.get_commit_history(
    since_date="2024-01-01",
    until_date="2024-01-31",
    author="username"  # オプション
)
```

**返り値**: コミット情報の辞書リスト

### APIFactory（AI統合）

複数のAIプロバイダーを統一インターフェースで利用：

```python
from external_service.api_factory import APIFactory

# プロバイダーの選択（config.iniから読み込みが基本）
client = APIFactory.create_client("claude")
client.initialize()

# コンテンツ生成
content, input_tokens, output_tokens = client.generate_content(
    prompt="プロンプトテキスト",
    model_name="claude-3-5-haiku-20241022"
)

# エラーハンドリングと自動フォールバック
if client is None:
    print("別のプロバイダーへの自動切り替えが実行されます")
```

### GoogleFormLauncher

生成された日誌をGoogle Formに自動入力：

```python
from service.launch_form_page import launch_form_page

launch_form_page(diary_content)
```

ChromeとPlaywrightを使用してフォームを自動入力します。

## 開発者向け情報

### 開発環境セットアップ

```bash
# 仮想環境の有効化
venv\Scripts\activate

# テストフレームワークのインストール（requirements.txtに含まれている）
pip install pytest pytest-cov

# テスト実行（全テスト）
pytest

# カバレッジ付きテスト
pytest --cov=service --cov=external_service --cov=utils --cov=app

# 特定テストの実行
pytest tests/test_programming_diary_generator.py -v

# テスト実行（詳細出力）
pytest -v
```

### ビルド

実行ファイル化（PyInstallerを使用）：

```bash
# ビルド（バージョン自動更新）
python build.py
```

生成された実行ファイルは`dist/`フォルダに出力されます。

### 開発支援スクリプト

```bash
# プロジェクト構造の確認
python scripts/project_structure.py

# バージョン情報の更新
python scripts/version_manager.py

# API設定の確認
python scripts/APIsetting_check.py
```

### コード規約

CLAUDE.mdに記載されたPythonコード規約に従ってください：

- import順序: 標準ライブラリ → サードパーティ → カスタムモジュール
- 各グループ内でアルファベット順ソート（importが先、fromは後）
- 差分ベースのコード提示

### 拡張方法

#### 新しいAIプロバイダーの追加

1. `external_service/`に新規ファイル作成（例: `your_api.py`）
2. `BaseAPIClient`を継承してクラス定義
3. `generate_content`メソッドを実装
4. `api_factory.py`の`APIProvider`列挙型と`create_client`メソッドに追加

#### UIウィジェット追加

1. `widgets/`フォルダに新規ウィジェット作成
2. `main_window.py`で統合
3. レイアウト管理（grid、pack等）を実装

#### テストの追加

`tests/`フォルダに`test_*.py`形式でテストファイルを作成：

```python
import pytest
from service.your_service import YourService

def test_your_feature():
    service = YourService()
    result = service.some_method()
    assert result is not None
```

## トラブルシューティング

### APIキーエラー

```
APIError: 未対応のAPIプロバイダー
```

**解決策**:
- `.env`ファイルがプロジェクトルートに配置されているか確認
- 少なくとも1つのAPIキーが有効か確認
- `config.ini`の`provider`設定値が正しいか確認（claude、openai、gemini）

### Gitコミット履歴が取得できない

**解決策**:
- リポジトリパスが正しいか確認
- Gitがインストール済みか確認（`git --version`実行）
- リポジトリへの読み取り権限を確認

### Google Formが起動しない

**解決策**:
- Google Chromeのインストール確認
- `config.ini`の`chrome_path`が正しいか確認


### 日本語が文字化けする

**解決策**:
- システムロケール設定を確認
- `config.ini`の`font`設定を確認（メイリオなど）
- Pythonファイルの先頭に`# -*- coding: utf-8 -*-`が記載されているか確認

### メモリ使用量が多い

**解決策**:
- 大量のコミット履歴を処理する場合は日付範囲を絞って実行
- AIプロバイダーのレスポンスタイムアウト設定を確認

## バージョン情報

- **現在のバージョン**: 1.1.6
- **最終更新**: 2025年12月15日

### 主な変更点

CHANGELOG.mdを参照してください。

## ライセンス

LICENSEファイルを参照してください。

## サポート

問題や要望は以下の方法でお問い合わせください：

- **GitHub Issues**: プロジェクトのIssueページ
- **開発ガイド**: CLAUDE.mdを参照
