# CodeDiary

Gitコミット履歴を生成AIで解析し、構造化されたプログラミング日誌を自動生成するWindowsデスクトップアプリケーション。

## 主要機能

- **Gitコミット履歴の自動解析**: 指定期間内のコミット履歴を自動抽出
- **GitHub連携**: 複数リポジトリの横断コミット履歴取得
- **Markdownファイル出力**: 対象期間の終了日でファイル名を付けて日誌保存フォルダに保存
- **Obsidian連携**: 日誌ファイル作成後にObsidianを自動起動
- **ウィンドウ位置・サイズ保存**: UI状態の自動復元

## 前提条件と要件

### システム要件

- **OS**: Windows 11以降
- **Python**: 3.13以降
- **Git**: インストール済み（コミット履歴取得に必須）
- **Obsidian**: 日誌ファイル作成後の起動に使用

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
uv sync
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
3. **日誌生成**: 「GitHubで作成」で全リポジトリから生成
4. **結果の利用**:
   - `YYYY-MM-DD_プログラミング学習日誌.md`（YYYY-MM-DDは対象期間の終了日）として保存フォルダに出力
   - 同名ファイルが存在する場合は上書き確認ダイアログを表示
   - 保存後にObsidianを自動起動

### 設定ファイル（config.ini）

#### Git・GitHub設定

```ini
[GIT]
repository_path = C:/Users/your_name/path/to/repository

[GITHUB]
enable_cross_repo_tracking = true  # 複数リポジトリの横断取得を有効化
```

#### 保存先・Obsidian設定

```ini
[Path]
daily_path = C:\Users\your_name\path\to\プログラミング学習日誌  # 日誌の保存先

[Obsidian]
obsidian_path = C:\Program Files\Obsidian\Obsidian.exe  # 保存後に起動する実行ファイル
```

#### UI設定

```ini
[UI]
calendar_background = darkblue      # カレンダー背景色
calendar_foreground = white          # カレンダーテキスト色
calendar_select_background = gray80  # カレンダー選択背景色
calendar_select_foreground = black   # カレンダー選択テキスト色

[WindowSettings]
window_width = 300
window_height = 200
window_x = 0    # ウィンドウX位置（自動保存）
window_y = 0    # ウィンドウY位置（自動保存）
```

## アーキテクチャ

CodeDiaryはモジュール化されたMVC風アーキテクチャを採用しており、各層が独立して動作します。

### レイヤー構成

#### UI層（`app/`、`widgets/`）

Tkinterを使用したUIコンポーネント：

- **CodeDiaryMainWindow** (`app/main_window.py`): アプリケーション全体のレイアウト管理とイベント処理
- **DateSelectionWidget**: カレンダーベースの日付範囲選択
- **ControlButtonsWidget**: 日誌生成・閉じるボタン
- **ProgressWidget**: タスク進捗とトークン数・モデル名の表示

#### ビジネスロジック層（`service/`）

- **ProgrammingDiaryGenerator**: Gitコミット履歴とAI統合による日誌生成（プロンプト基づく構造化生成）
- **GitCommitHistoryService**: Gitコマンド実行とコミット履歴抽出（日付フィルタリング対応）
- **GitHubCommitTracker**: GitHub APIを使用した複数リポジトリの横断取得
  - ThreadPoolExecutorによる**並列コミット取得**（最大8スレッド同時実行）
  - 日付フィルタリング（前回push日から効率化）
  - 日付範囲対応メソッド
- **DiaryFileService** (`service/diary_file_service.py`): Markdownファイル保存、Obsidian起動

#### AI統合層（`external_service/`）

```python
client = GeminiAPIClient()
client.initialize()
content, input_tokens, output_tokens = client.generate_content(
    prompt="...",
    model_name="gemini-2.0-flash-exp"
)
```

- **GeminiAPIClient**: Google Gemini API統合（`initialize()`、`generate_content()`）

#### 設定管理層（`utils/`）

- **ConfigManager**: `config.ini`の統合管理（AI設定、UI設定、Git/GitHub設定）
- **EnvLoader**: `.env`ファイルからのAPIキーと環境変数読み込み
- **RepositoryNameExtractor**: Gitリポジトリ名抽出ユーティリティ
- **PromptTemplate** (`prompt_template.md`): AI生成プロンプト形式定義

### AIプロンプト形式

生成AIへ送信するプロンプトは、`utils/prompt_template.md`で定義されており、以下の構成で日誌を生成します：

#### 日誌構成

- **作業内容**: コミット履歴の圧縮要約（1日あたり400字以内）
  - リポジトリ別に整理、日付順に並べる
  - カテゴリ分類: 機能追加、バグ修正、UI改善、リファクタリング、テスト、ドキュメント、設定構成
  - 変更ファイル最大5件、詳細は最大3項目まで

- **学びと気づき**: コミット履歴から読み取れる学習ポイント（AIが下書き）
  - 事実・原因・次のアクションの3点セットで記述
  - 同一機能への繰り返し修正、revert、環境構築での課題などを優先抽出

- **知見集**: 日誌ではなく知見集（CLAUDE.md等）に転記すべき情報
  - ビルド設定、CI設定、環境構築などの再利用可能な手順
  - 繰り返し登場する問題パターン

- **自由記載**: ユーザーが追加記入する欄

## 開発者向け情報

### 開発環境セットアップ

```bash
# 仮想環境の有効化
venv\Scripts\activate

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

#### AIモデルの変更

`.env`の`GEMINI_MODEL`を変更することで使用するGeminiモデルを切り替えられます。API呼び出しの実装は`external_service/gemini_api.py`の`GeminiAPIClient`に集約されています。

## トラブルシューティング

### APIプロバイダーエラー

**原因**: `.env`ファイルが見つからない、またはAPIキーが未設定

**解決策**:
1. プロジェクトルートに`.env`ファイルを作成
2. 以下のAPIキーを設定：
   ```env
   GEMINI_API_KEY=your_key
   ```

### Obsidianが起動しない

**原因**: Obsidianがインストールされていない、またはパスが不正

**解決策**:
1. Obsidianをインストール
2. `config.ini`の`[Obsidian]`セクションで`obsidian_path`を確認
   - Windows標準インストール: `C:\Program Files\Obsidian\Obsidian.exe`
3. パスが正しいか確認：`dir "C:\Program Files\Obsidian\"`

### 日誌ファイルが保存されない

**原因**: `daily_path`が不正、または保存先への書き込み権限がない

**解決策**:
1. `config.ini`の`[Path]`セクションで`daily_path`を確認
2. 保存先フォルダは存在しない場合に自動作成されるため、親フォルダの書き込み権限を確認

## ライセンス

このプロジェクトのライセンス情報については、 [LICENSE](docs/LICENSE) を参照してください。

## 更新履歴

更新履歴は [CHANGELOG.md](docs/CHANGELOG.md) を参照してください。
