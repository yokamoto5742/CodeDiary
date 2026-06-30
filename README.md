# CodeDiary

Gitコミット履歴を生成AIで解析し、構造化されたプログラミング日誌を自動生成するWindowsデスクトップアプリケーション。

## 主要機能

- **Gitコミット履歴の自動解析**: 指定期間内のコミット履歴を自動抽出
- **GitHub連携**: 複数リポジトリの横断コミット履歴取得
- **ウィンドウ位置・サイズ保存**: UI状態の自動復元

## 前提条件と要件

### システム要件

- **OS**: Windows 11以降
- **Python**: 3.13以降
- **Git**: インストール済み（コミット履歴取得に必須）
- **Google Chrome**: Googleフォーム起動時に使用

### 必要なAPIキー

- **Gemini API**: Google社のAPIキー

## インストール手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/yokamoto5742/CodeDiary
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
# Gemini API
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.0-flash

# GitHub連携
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

2. **期間指定**: カレンダーで開始日・終了日を選択
3. **日誌生成**: GitHub連携日記作成で全リポジトリから生成
4. **結果の利用**:
   - 自動的にクリップボードにコピー
   - 日誌用Google Formを開く

### 設定ファイル（config.ini）

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

```python
client = APIFactory.create_client("gemini")
client.initialize()
content, input_tokens, output_tokens = client.generate_content(
    prompt="...",
    model_name="gemini-2.0-flash-exp"
)
```

- **BaseAPIClient**: 共通インターフェース定義（`initialize()`、`generate_content()`）
- **GeminiAPIClient**: Google Gemini API統合

#### 設定管理層（`utils/`）

- **ConfigManager**: `config.ini`の統合管理（AI設定、UI設定、Git/GitHub設定）
- **EnvLoader**: `.env`ファイルからのAPIキーと環境変数読み込み
- **RepositoryNameExtractor**: Gitリポジトリ名抽出ユーティリティ
- **PromptTemplate** (`prompt_template.md`): AI生成プロンプト形式定義

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
python build.py
```

生成された実行ファイルは`dist/`フォルダに出力されます。

### 拡張方法

#### 新しいAIプロバイダーの追加

1. `external_service/`に新規ファイル作成（例: `your_api.py`）
2. `BaseAPIClient`を継承してクラス定義
3. 以下のメソッドを実装：
   - `initialize()`: APIキー検証など初期化処理
   - `generate_content(prompt, model_name)`: テキスト生成処理（`(content, input_tokens, output_tokens)`を返す）
4. `api_factory.py`の`APIProvider`列挙型に新プロバイダーを追加
5. `create_client`メソッドの`client_mapping`に新クライアントを追加

## トラブルシューティング

### APIプロバイダーエラー

**原因**: `.env`ファイルが見つからない、またはAPIキーが未設定

**解決策**:
1. プロジェクトルートに`.env`ファイルを作成
2. 以下のAPIキーを設定：
   ```env
   GEMINI_API_KEY=your_key
   ```

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

## ライセンス

このプロジェクトのライセンス情報については、 [LICENSE](docs/LICENSE) を参照してください。

## 更新履歴

更新履歴は [CHANGELOG.md](docs/CHANGELOG.md) を参照してください。
