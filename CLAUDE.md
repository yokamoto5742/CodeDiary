# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

CodeDiaryは、Gitコミット履歴を生成AI（Gemini）で解析し、構造化されたプログラミング日誌を自動生成するWindowsデスクトップアプリケーション（Tkinter製）。詳細な機能・アーキテクチャ・トラブルシューティングは `README.md` を参照。

## セットアップとコマンド

パッケージ管理は `uv`。

```bash
uv sync                          # 依存関係インストール
uv run python main.py            # アプリケーション起動（エントリポイントは main.py）
uv run python build.py           # PyInstallerで実行ファイル化（dist/に出力）
```

テストコマンドは `.claude/rules/testing.md` を参照。

## 注意点（ハマりどころ）

- **`.env` の読み込みは `utils/env_loader.py` の `load_environment_variables()` に一元化されている**: `utils/config_manager.py` はこれをインポートし、インポート時に副作用として呼び出している。
- **`utils/config.ini` はgit管理下にある**: アプリ初回起動時に自動生成される設定ファイルだが、リポジトリにはこの開発機のローカルパス（OneDriveパス等）が入った状態でコミットされている。テンプレートファイルとして扱わない。個人環境向けの変更を誤ってコミットしない。
- **AIプロバイダーはGeminiのみ**: 過去にClaude/OpenAIやPlaywrightによるGoogleフォーム自動化をサポートしていた名残（`docs/CHANGELOG.md` の古いエントリや `__pycache__` 内の古い `.pyc` ファイル名）が残っているが、該当するソースコードは既に削除済み。存在すると思い込まない。
- **Windows専用**: Obsidianの実行パス（`C:\Program Files\Obsidian\Obsidian.exe`）などがハードコードされており、動作前提はWindows 11以降。
- **`.env` の内容を読み取り・出力・コミットしない**: APIキー（`GEMINI_API_KEY`, `GITHUB_TOKEN`）が含まれる。
