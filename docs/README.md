# CodeDiary

## プロジェクト概要

**CodeDiary**は、Gitコミット履歴を基に生成AIを活用してプログラミング日誌を自動生成するデスクトップアプリケーションです。開発者の日々の作業を構造化された日誌形式に変換し、Google Formへの自動入力まで行います。

### 主要な機能

- **Gitコミット履歴の自動取得**: 指定期間内のコミット履歴を抽出
- **生成AI活用日誌生成**: 複数のAIプロバイダー（Claude、OpenAI、Gemini）による構造化された日誌作成
- **フォールバック機能**: フォールバック機能により、メインプロバイダーが利用できない場合の自動切り替え
- **Google Form自動入力**: 生成された日誌のワンクリック送信

### 対象ユーザー

- 日々の開発作業を記録したいソフトウェア開発者
- プロジェクト進捗の可視化が必要なチームリーダー
- 開発日誌の作成を効率化したい個人・チーム

### 解決する問題

- 手動での開発日誌作成の時間コスト削減
- コミット履歴の構造化と可読性向上
- 定期的な作業報告の自動化

## 前提条件と要件

### システム要件

- **OS**: Windows 11
- **Python**: 3.11以降推奨
- **Google Chrome**: Google Form自動入力機能に必要

### ハードウェア要件

- **RAM**: 4GB以上推奨
- **ストレージ**: 100MB以上の空き容量

### 必要なAPIキー

以下のうち少なくとも1つのAPIキーが必要です：

- **Claude API**: Anthropic社のClaude APIキー
- **OpenAI API**: OpenAI社のAPIキー
- **Gemini API**: Google社のGemini APIキー

## インストール手順

### 1. Pythonのインストール

Python 3.11以降をインストールしてください。
```bash
# Pythonバージョン確認
python --version
```

### 2. リポジトリのクローン

```bash
git clone <repository-url>
cd CodeDiary
```

### 3. 仮想環境の作成（推奨）

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 4. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 5. 環境変数の設定

プロジェクトルートに`.env`ファイルを作成し、以下の形式でAPIキーを設定してください：

```env
# Claude API（推奨）
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-5-haiku-20241022

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-mini

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_THINKING_BUDGET=-1
```

### 6. Google Chromeのインストール

Google Form自動入力機能を使用する場合は、Google Chromeをインストールしてください：
- [Google Chrome公式サイト](https://www.google.com/chrome/)からダウンロード
- デフォルトパス: `C:\Program Files\Google\Chrome\Application\chrome.exe`

### 7. 設定ファイルの確認

初回起動時に`utils/config.ini`が自動作成されます。必要に応じて設定を変更してください。

## 使用方法

### 基本的な使い方

1. **アプリケーション起動**
   ```bash
   python main.py
   ```

2. **Gitリポジトリの設定**
   - 「Gitリポジトリ設定」ボタンをクリック
   - 対象のGitリポジトリフォルダを選択

3. **対象期間の設定**
   - 開始日と終了日を選択（カレンダーウィジェット使用）

4. **日誌生成**
   - 「日誌作成」ボタンをクリック
   - AIが自動でコミット履歴を解析し、日誌を生成

5. **結果の確認と利用**
   - 生成された日誌が画面に表示
   - 自動的にクリップボードにコピー
   - Google Formに自動入力（設定済みの場合）

### 高度な使用方法

#### AIプロバイダーの変更

`utils/config.ini`ファイルを編集：

```ini
[AI]
provider = claude  # claude, openai, gemini から選択
fallback_provider = openai  # メイン失敗時のフォールバック先
```

#### Google Form設定

```ini
[URL]
form_url = https://forms.gle/your_form_id_here
```

#### UI設定のカスタマイズ

```ini
[DiaryText]
font = メイリオ
font_size = 11

[WindowSettings]
window_width = 600
window_height = 600
```

## プロジェクト構造

```
CodeDiary/
├── main.py                     # アプリケーションエントリーポイント
├── requirements.txt            # 依存関係
├── prompt_template.md          # AI用プロンプトテンプレート
├── app/
│   ├── __init__.py
│   └── main_window.py          # メインウィンドウ
├── external_service/
│   ├── __init__.py
│   ├── api_factory.py          # AIプロバイダーファクトリ
│   ├── base_api.py             # 基底APIクライアント
│   ├── claude_api.py           # Claude APIクライアント
│   ├── gemini_api.py           # Gemini APIクライアント
│   └── openai_api.py           # OpenAI APIクライアント
├── service/
│   ├── __init__.py
│   ├── git_commit_history.py   # Gitコミット履歴取得
│   ├── google_form_automation.py # Google Form自動入力
│   └── programming_diary_generator.py # 日誌生成エンジン
├── utils/
│   ├── config.ini              # 設定ファイル
│   ├── config_manager.py       # 設定管理
│   ├── constants.py            # 定数定義
│   ├── exceptions.py           # カスタム例外
│   ├── env_loader.py           # 環境変数読み込み
│   └── repository_name_extractor.py # リポジトリ名抽出
├── widgets/
│   ├── __init__.py
│   ├── control_buttons_widget.py # ボタン群ウィジェット
│   ├── date_selection_widget.py  # 日付選択ウィジェット
│   ├── diary_content_widget.py   # 日誌表示ウィジェット
│   └── progress_widget.py        # 進捗表示ウィジェット
├── scripts/
│   ├── project_structure.py   # プロジェクト構造出力
│   └── version_manager.py     # バージョン管理
└── tests/                     # テストファイル群
```

### 主要ファイルの役割

- **main.py**: アプリケーションの起動とTkinterアプリケーションの初期化
- **main_window.py**: メインUIとコンポーネント間の連携制御
- **programming_diary_generator.py**: コミット履歴を日誌に変換するメインエンジン
- **git_commit_history.py**: Gitコマンドを使用したコミット履歴の取得
- **api_factory.py**: AIプロバイダーの動的選択と初期化
- **config_manager.py**: 設定ファイルと環境変数の統合管理

## 機能説明

### GitCommitHistoryService クラス

Gitリポジトリからコミット履歴を取得します。

```python
# 基本的な使用例
service = GitCommitHistoryService()
commits = service.get_commit_history(
    since_date="2024-01-01",
    until_date="2024-01-31",
    author="username"
)
```

#### 主要メソッド

- `get_commit_history()`: 指定期間のコミット履歴取得
- `get_repository_info()`: リポジトリの基本情報取得
- `format_output()`: コミット履歴の整形出力

### ProgrammingDiaryGenerator クラス

AIを使用してコミット履歴から構造化された日誌を生成します。

```python
# 日誌生成の例
generator = ProgrammingDiaryGenerator()
diary, input_tokens, output_tokens = generator.generate_diary(
    since_date="2024-01-01",
    until_date="2024-01-07",
    days=7  # または日数指定
)
```

#### 特徴

- **複数AIプロバイダー対応**: Claude、OpenAI、Geminiの自動切り替え
- **フォールバック機能**: メインプロバイダー失敗時の自動代替
- **Markdown→プレーンテキスト変換**: 出力形式の最適化

### GoogleFormAutomation クラス

生成された日誌をGoogle Formに自動入力します。

```python
# 自動入力の実行
automation = GoogleFormAutomation()
automation.run_automation()  # クリップボードの内容を自動入力
```

#### 機能

- **Playwright使用**: 高信頼性のブラウザ自動化
- **日付自動入力**: 実行日の自動設定
- **エラーハンドリング**: 入力失敗時の適切な対応

### API Factory パターン

複数のAIプロバイダーを統一インターフェースで利用できます。

```python
# プロバイダーの動的選択
client = APIFactory.create_client("claude")
client.initialize()
result = client._generate_content(prompt, model_name)
```

## 設定

### config.ini の主要設定項目

```ini
[AI]
provider = claude              # メインAIプロバイダー
fallback_provider = openai     # フォールバックプロバイダー

[GIT]
repository_path = C:/path/to/your/repo  # Gitリポジトリパス

[Chrome]
chrome_path = C:/Program Files/Google/Chrome/Application/chrome.exe

[URL]
form_url = https://forms.gle/your_form_id

[WindowSettings]
window_width = 600
window_height = 600

[DiaryText]
font = メイリオ
font_size = 11
```

### 環境変数設定

`.env`ファイルでAPIキーを管理：

```env
# 優先順位の高いプロバイダーから設定
CLAUDE_API_KEY=sk-ant-xxxxx
CLAUDE_MODEL=claude-3-haiku-20240307

OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-3.5-turbo

GEMINI_API_KEY=xxxxx
GEMINI_MODEL=gemini-1.5-flash
GEMINI_THINKING_BUDGET=1024
```

## 開発者向け情報

### 開発環境のセットアップ

```bash
# 開発用依存関係のインストール
pip install pytest pytest-cov

# テストの実行
pytest tests/

# カバレッジレポートの生成
pytest --cov=service --cov=external_service --cov=utils --cov-report=html
```

### アーキテクチャ

- **MVCパターン**: モデル（Service層）、ビュー（Widgets）、コントローラー（MainWindow）
- **ファクトリーパターン**: AIプロバイダーの動的生成
- **設定管理**: INIファイルと環境変数の統合管理

### 拡張方法

1. **新しいAIプロバイダーの追加**
   - `external_service/`に新しいAPIクライアントを作成
   - `BaseAPIClient`を継承し、`_generate_content`メソッドを実装
   - `api_factory.py`に追加

2. **UI機能の追加**
   - `widgets/`に新しいウィジェットクラスを作成
   - `main_window.py`で統合

3. **新しい出力形式の追加**
   - `programming_diary_generator.py`の変換メソッドを拡張

### ビルド手順

実行ファイルの作成：

```bash
python build.py
```

このコマンドで以下が実行されます：
- バージョンの自動更新
- PyInstallerによる実行ファイル生成
- 必要なリソースファイルの同梱

## トラブルシューティング

### よくある問題と解決方法

#### Q: APIキーエラーが発生する
**A**: 
- `.env`ファイルのAPIキーが正しく設定されているか確認
- 少なくとも1つのプロバイダーのAPIキーが有効であることを確認
- APIキーの利用制限や請求状況を確認

#### Q: Gitコミット履歴が取得できない
**A**:
- 指定したパスが正しいGitリポジトリであることを確認
- Gitがシステムにインストールされていることを確認
- リポジトリへの読み取り権限があることを確認

#### Q: Google Form自動入力が動作しない
**A**:
- Chromeのインストールパスを確認
- フォームURLが正しく設定されているか確認
- ブラウザがブロックしていないか確認

#### Q: 日本語が文字化けする
**A**:
- システムの日本語ロケール設定を確認
- フォント設定（メイリオ）が利用可能か確認

#### Q: メモリ使用量が多い
**A**:
- 一度に処理するコミット数を制限
- 大量のコミット履歴がある場合は期間を短く設定
- アプリケーションの再起動

#### Q: 日誌生成に時間がかかる
**A**:
- コミット数が多い場合は期間を調整
- より高速なAIプロバイダーに変更
- ネットワーク接続状況を確認

### デバッグ情報

アプリケーション実行時にコンソールに出力される情報を確認：

```
🔍 デバッグ情報:
   AIプロバイダー: claude
   使用モデル: claude-3-haiku-20240307
   リポジトリパス: /path/to/repo
   検索期間: 2024-01-01 から 2024-01-07
   現在のブランチ: main
   最新コミット: abc123 by User on 2024-01-07
   取得したコミット数: 15
```

### パフォーマンス最適化

- **期間の適切な設定**: 大量のコミットを避けるため、適切な期間を設定
- **AIプロバイダーの選択**: 用途に応じて最適なプロバイダーを選択
- **メモリ管理**: 長時間使用時は定期的にアプリケーションを再起動

## バージョン情報

- **初回リリース日**: 2025-08-12
- **対応Python**: 3.11以降
- **対応OS**: Windows 11

## ライセンス

このプロジェクトのライセンス情報については、LICENSEファイルを参照してください。

## サポート

問題や要望がございましたら、以下の方法でお気軽にお問い合わせください：

- GitHub Issues: プロジェクトのIssueページ
- 開発者へのダイレクトメッセージ

## 貢献

プロジェクトへの貢献を歓迎します！貢献方法：

1. リポジトリをフォーク
2. フィーチャーブランチを作成
3. 変更をコミット
4. プルリクエストを送信

開発に参加される際は、既存のコードスタイルとテストパターンに従ってください。
