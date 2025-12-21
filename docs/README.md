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
provider = gemini          # メインプロバイダー: claude, openai, gemini
fallback_provider = gemini # フォールバック先
```

#### Git・GitHub設定

```ini
[GIT]
repository_path = C:/Users/your_name/path/to/repository

[GITHUB]
enable_cross_repo_tracking = true  # 複数リポジトリの横断取得を有効化
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

[UI]
calendar_background = darkblue      # カレンダー背景色
calendar_foreground = white          # カレンダーテキスト色
calendar_select_background = gray80  # カレンダー選択背景色
calendar_select_foreground = black   # カレンダー選択テキスト色

[WindowSettings]
window_width = 800
window_height = 600
window_x = 648    # ウィンドウX位置（自動保存）
window_y = 64     # ウィンドウY位置（自動保存）

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

- **CodeDiaryMainWindow** (`app/main_window.py`): アプリケーション全体のレイアウト管理とイベント処理
- **DateSelectionWidget**: カレンダーベースの日付範囲選択
- **DiaryContentWidget**: 生成された日誌の表示とクリップボード操作
- **ControlButtonsWidget**: 日誌生成・Google Form送信ボタン
- **ProgressWidget**: タスク進捗表示

#### ビジネスロジック層（`service/`）

- **ProgrammingDiaryGenerator**: Gitコミット履歴とAI統合による日誌生成（プロンプト基づく構造化生成）
- **GitCommitHistoryService**: Gitコマンド実行とコミット履歴抽出（日付フィルタリング対応）
- **GitHubCommitTracker**: GitHub APIを使用した複数リポジトリの横断取得
- **GoogleFormLauncher**: Google Form立ち上げ

#### AI統合層（`external_service/`）

Factory Patternを使用した複数AIプロバイダーの動的選択と自動フォールバック：

```python
# プロバイダーの動的選択
client = APIFactory.create_client("gemini")  # "claude", "openai"も可能
client.initialize()
content, input_tokens, output_tokens = client.generate_content(
    prompt="...",
    model_name="gemini-2.0-flash-exp"
)
```

- **BaseAPIClient**: 共通インターフェース定義（`initialize()`、`generate_content()`）
- **ClaudeAPIClient**: Anthropic Claude API統合
- **OpenAIAPIClient**: OpenAI GPT API統合
- **GeminiAPIClient**: Google Gemini API統合

#### 設定管理層（`utils/`）

- **ConfigManager**: `config.ini`の統合管理（AI設定、UI設定、Git/GitHub設定）
- **EnvLoader**: `.env`ファイルからのAPIキーと環境変数読み込み
- **RepositoryNameExtractor**: Gitリポジトリ名抽出ユーティリティ
- **PromptTemplate** (`prompt_template.md`): AI生成プロンプト形式定義

### デザインパターン

1. **Factory Pattern**: `external_service/api_factory.py`でAIプロバイダーを動的に選択・生成
2. **Template Method**: 日誌生成ワークフローの標準化（コミット取得→AI処理→形式化）
3. **Strategy Pattern**: 複数AIプロバイダーが共通インターフェース実装
4. **Configuration Management**: 環境変数とINI設定の統合管理（`config_manager.py`）
5. **Abstract Base Class**: Gitサービス基盤（`BaseCommitService`）で統一的なコミット処理

## 主要機能の詳細

### ProgrammingDiaryGeneratorクラス

Gitコミット履歴をAIで解析して、`prompt_template.md`の形式に基づいて構造化された日誌を生成します。

```python
from service.programming_diary_generator import ProgrammingDiaryGenerator

generator = ProgrammingDiaryGenerator()

# ローカルGitコミット履歴から生成（UIから呼び出される標準的な用法）
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
- `since_date`: 開始日付（ISO 8601形式、必須）
- `until_date`: 終了日付（オプション、指定なしは当日）
- `use_github`: True時はGitHub APIを使用して全リポジトリから取得

**戻り値**: `(日誌テキスト, 入力トークン数, 出力トークン数)`

**日誌形式**:
生成された日誌は以下の構造：
```
yyyy年m月d日(曜日)
リポジトリ名
カテゴリ（機能追加、バグ修正など）
1.概要
（概要文）
2.変更ファイル
（ファイルリスト）
3.詳細
（詳細説明）
```

### GitCommitHistoryServiceクラス

Gitコマンドを実行してコミット履歴を日付範囲で抽出します。`BaseCommitService`を継承し、UTCから日本時間への自動変換に対応。

```python
from service.git_commit_history import GitCommitHistoryService

service = GitCommitHistoryService()
commits = service.get_commit_history(
    since_date="2024-01-01",
    until_date="2024-01-31",
    author="username"  # オプション
)
```

**返り値**: 以下の構造を持つコミット辞書のリスト：
```python
{
    'hash': 'abc123...',        # コミットハッシュ
    'author_name': '著者名',      # コミット著者
    'author_email': 'email@...',  # メールアドレス
    'timestamp': '2024-01-01T...(JST)',  # 日本時間タイムスタンプ
    'message': 'コミットメッセージ',  # コミットメッセージ
    'repository': 'リポジトリ名'  # リポジトリ名（オプション）
}
```

### APIFactory（AI統合）

複数のAIプロバイダーを統一インターフェースで利用。Factory Patternで動的にクライアントを生成：

```python
from external_service.api_factory import APIFactory

# プロバイダー指定でクライアント生成（通常はconfig.iniから読み込み）
client = APIFactory.create_client("gemini")  # "claude", "openai"も可
client.initialize()

# AIによるコンテンツ生成
content, input_tokens, output_tokens = client.generate_content(
    prompt="プロンプトテキスト",
    model_name="gemini-2.0-flash-exp"
)

# 返り値
# content: 生成されたテキスト
# input_tokens: 入力トークン数
# output_tokens: 出力トークン数
```

**対応プロバイダー**:
- `claude`: Anthropic Claude API（デフォルトモデル: claude-3-5-haiku-20241022）
- `openai`: OpenAI GPT API（デフォルトモデル: gpt-4o-mini）
- `gemini`: Google Gemini API（デフォルトモデル: gemini-2.0-flash-exp）

### GoogleFormLauncher

Google Formを立ち上げる：

```python
from service.launch_form_page import launch_form_page

launch_form_page(diary_content)
```

### AIプロンプト形式

生成AIへ送信するプロンプトは、`utils/prompt_template.md`で定義されており、以下の構成で日誌を生成します：

- **日付別整理**: 作業日ごとにセクション分け、リポジトリ名明記
- **カテゴリ分類**: 機能追加、バグ修正、UI改善、リファクタリング、テスト、ドキュメント、設定構成など
- **出力形式**: 日付、リポジトリ名、カテゴリ、概要、変更ファイル、詳細を階層化

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
3. 以下のメソッドを実装：
   - `initialize()`: APIキー検証など初期化処理
   - `generate_content(prompt, model_name)`: テキスト生成処理（`(content, input_tokens, output_tokens)`を返す）
4. `api_factory.py`の`APIProvider`列挙型に新プロバイダーを追加
5. `create_client`メソッドの`client_mapping`に新クライアントを追加

#### UIウィジェット追加

1. `widgets/`フォルダに新規ウィジェット作成
2. `app/main_window.py`の`_setup_ui()`で統合
3. Tkinterのレイアウト管理（grid、pack等）で配置

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

実行：
```bash
pytest tests/test_your_service.py -v
```

## トラブルシューティング

### APIプロバイダーエラー（APIError: 未対応のAPIプロバイダー）

**原因**: `.env`ファイルが見つからない、またはAPIキーが未設定

**解決策**:
1. プロジェクトルートに`.env`ファイルを作成
2. 以下のいずれかのAPIキーを設定：
   ```env
   CLAUDE_API_KEY=your_key
   OPENAI_API_KEY=your_key
   GEMINI_API_KEY=your_key
   ```
3. `config.ini`の`[AI]`セクション設定を確認（provider = claude/openai/gemini）
4. 開発支援スクリプトで確認：`python scripts/APIsetting_check.py`

### Gitコミット履歴が取得できない

**原因**: リポジトリパスが不正またはGitが未インストール

**解決策**:
1. `config.ini`の`[GIT]`セクションでリポジトリパスを確認
2. Gitがインストール済みか確認：`git --version`
3. リポジトリフォルダのアクセス権限を確認
4. コマンドラインで直接実行確認：`git log --since="2024-01-01" --until="2024-01-31"`

### Google Formが起動しない

**原因**: Chromeがインストールされていない、またはパスが不正

**解決策**:
1. Google Chromeをインストール
2. `config.ini`の`[Chrome]`セクションで`chrome_path`を確認
   - Windows標準インストール: `C:\Program Files\Google\Chrome\Application\chrome.exe`
3. Chromeのパスが正しいか確認：`dir "C:\Program Files\Google\Chrome\Application\"`

### 日本語が文字化けする

**原因**: フォント設定またはロケール設定の問題

**解決策**:
1. `config.ini`の`[DiaryText]`セクションでフォント設定を確認
   - 推奨: `font = メイリオ`（Windows標準日本語フォント）
2. 代替フォント：`MS ゴシック`、`Yu Gothic`
3. Pythonファイルエンコーディング確認（通常UTF-8で自動処理）

### メモリ使用量が多い

**原因**: 大量のコミット履歴の処理またはAIプロバイダーのレスポンス待機

**解決策**:
1. 日付範囲を絞って実行（例：1週間単位）
2. 大規模リポジトリの場合は特定著者で絞る（開発ツール機能）
3. AIプロバイダーのタイムアウト設定を調整

## バージョン情報

- **現在のバージョン**: 1.1.6
- **最終更新**: 2025年12月21日

### 主な変更点

CHANGELOG.mdを参照してください。

## ライセンス

LICENSEファイルを参照してください。

## サポート

問題や要望は以下の方法でお問い合わせください：

- **GitHub Issues**: プロジェクトのIssueページ
- **開発ガイド**: CLAUDE.mdを参照
