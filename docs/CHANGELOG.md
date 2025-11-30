# CHANGELOG

## [1.1.3] - 2025-11-30

### Added
- **テストスイート拡張**: CodeDiaryMainWindow と launch_form_page のテストを追加
  - `tests/test_launch_form_page.py`: launch_form_page 関数の機能テスト（168 行）
- **プログラミング学習日誌フォーム起動機能**: `service/launch_form_page.py` を新規追加
  - UI から学習日誌フォームの起動をサポート
  - `utils/config.ini` に対応設定を追加

### Changed
- **モジュール整理**: `google_form_automation.py` を `service/` から `scripts/` に移動し、スクリプトユーティリティを適切に配置

## [1.1.2] - 2025-11-20

### Fixed
- **ビルドプロセスの修正**: `prompt_template.md`のパスをutilsディレクトリに修正
  - `build.py`: ビルド時にprompt_template.mdを正しい位置から取得するよう修正
  - バンドルファイルに正しいパスで含める処理を改善

## [1.1.1] 記載なし

### Changed
- **UIコードの整理**: `widgets`モジュール内の不要なコメントを削除し、コード品質を向上
- **バージョン情報の更新**: アプリケーションバージョンを1.1.2に更新、README.mdを同期

### Enhanced
- **GitHub連携フォーマット改善**: `service/github_commit_tracker.py`のコミット情報フォーマット処理を最適化

## [1.0.6] - 2025-09-28

### Fixed
- **タイムゾーン処理の修正**: `GitHubCommitTracker`のJST→UTC変換処理を改善
  - `get_commits_for_repo_by_date`メソッド: JST 0時をUTC 15時（前日）に正確に変換
  - `get_commits_for_repo_by_date_range`メソッド: 日付範囲指定時のタイムゾーン変換を修正
  - GitHub API の`since`/`until`パラメータでJST日付が正しく処理されるよう改善

### Enhanced
- **テストスイート更新**: タイムゾーン変換に対応したテストケースの修正
  - 期待値をJST→UTC変換後の正しい値に更新
  - 不要な`load_config`パッチを削除してテスト安定性を向上
  - 全92テストケースが引き続き成功

### Technical
- インポート文に`timezone`クラスを追加
- JST（UTC+9）からUTCへの変換ロジックを明示的に実装
- GitHub API 日付パラメータの正確性を保証

## [1.0.5] - 2025-09-27

### Added
- **テストスイート拡張**: `GitHubCommitTracker`クラスの包括的なユニットテスト
  - 新規ファイル: `tests/test_github_commit_tracker.py`
  - 32個のテストケースで96%のコードカバレッジを達成
  - モック機能を活用した外部依存関係の分離テスト
  - 正常系・異常系の両方を網羅するテスト設計

### Enhanced
- **品質保証**: pytest-test-creatorエージェントによる自動テスト生成
- **エラーハンドリングテスト**: HTTP エラー、ネットワークエラー、認証エラーの検証
- **データフォーマットテスト**: 日付変換、コミットソート、JSON レスポンス処理の検証
- **パラメータ化テスト**: 効率的な複数シナリオテスト実装

### Technical
- テスト実行環境: pytest + coverage
- モックライブラリ: unittest.mock を活用
- 全テストスイート: 92テスト（既存60 + 新規32）が成功
- CI/CD 準備: 包括的なテストベースの確立

## [1.0.4] - 2025-09-25

### Added
- **GitHub連携機能**: 複数リポジトリの横断コミット履歴取得機能を追加
  - `GitHubCommitTracker`クラス: GitHub API経由で全リポジトリのコミット履歴を取得
  - UI に「GitHub連携日記作成」ボタンを新規追加
  - 設定ファイル(`utils/config.ini`)にGitHub連携設定セクションを追加
  - 環境変数による GitHub 認証情報管理 (`GITHUB_TOKEN`, `GITHUB_USERNAME`)

### Changed
- `ProgrammingDiaryGenerator.generate_diary()`メソッドに`use_github`パラメータを追加
- GitHub連携時のコミットメッセージにリポジトリ名を自動付与 (`[repo_name] commit_message`)
- フォールバック処理でGitHub連携パラメータを継承するよう改修
- UI レイアウト調整: ボタン配置を6列に拡張

### Enhanced
- **エラーハンドリング**: GitHub API エラー時の自動ローカルGitフォールバック
- **認証チェック**: GitHub認証情報の事前検証とユーザーフレンドリーなエラーメッセージ
- **設定管理**: GitHub機能の有効/無効切り替え設定
- **デバッグ情報**: データソース（GitHub API vs ローカルGit）の明確な表示

### Technical
- 新規ファイル: `service/github_commit_tracker.py`
- GitHub API v3 を使用した REST API 実装
- リクエストタイムアウトとページネーション対応
- JST タイムゾーン変換とコミット時刻ソート機能

## [1.0.3] - 2025-08-14

### Added
- PostToolUseとStop/SessionEndフック通知機能
- CLAUDE.mdガイドラインとアーキテクチャ説明の充実

### Removed
- ビルドスクリプト関連ファイルの整理
- 不要なGoogleドキュメント連携スクリプトを削除

## [1.0.2] - 2025-08-14

### Added
- Googleドキュメントコピー機能
- PyInstallerビルド自動化スクリプト

### Enhanced
- バージョン管理の自動化改善

## [1.0.1] - 2025-08-14

### Enhanced
- READMEと__init__.pyのバージョン・更新日自動更新機能

## [1.0.0] - 2025-08-14

### Added
- 初期リリース
- Gitコミット履歴の自動取得機能
- 複数AIプロバイダー対応（Claude、OpenAI、Gemini）
- Google Form自動入力機能
- Tkinter ベースのデスクトップUI
- 設定管理システム（INI + 環境変数）
- フォールバック機能付きAI連携
- 日本語ローカライゼーション

### Features
- **AI統合**: ファクトリーパターンによる複数プロバイダー対応
- **Git連携**: subprocess経由でのコミット履歴取得
- **Web自動化**: Playwrightベースのフォーム入力
- **UI Components**: モジュラーウィジェットシステム
- **エラーハンドリング**: 包括的な例外処理とフォールバック
- **設定管理**: 統一された設定インターフェース