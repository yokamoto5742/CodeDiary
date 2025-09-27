# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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