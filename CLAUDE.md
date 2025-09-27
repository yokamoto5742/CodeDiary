# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## House Rules:
- 文章ではなくパッチの差分を返すこと。Return patch diffs, not prose.
- 不明な点がある場合は、トレードオフを明記した2つの選択肢を提案すること（80語以内）。
- 変更範囲は最小限に抑えること
- Pythonコードのimport文は以下の適切な順序に並べ替えてください。
標準ライブラリ
サードパーティライブラリ
カスタムモジュール 
それぞれアルファベット順に並べます。importが先でfromは後です。

## Automatic Notifications (Hooks)
自動通知は`.claude/settings.local.json` で設定済。サブエージェントが作業を完了したときも通知する。：
- **Stop Hook**: ユーザーがClaude Codeを停止した時に「作業が完了しました」と通知
- **SessionEnd Hook**: セッション終了時に「Claude Code セッションが終了しました」と通知

## Commands

### Running the Application
```bash
python main.py
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_programming_diary_generator.py

# Run tests with verbose output
pytest -v
```

### Building
```bash
# Build executable with automatic version update
python build.py
```

### Development Tools
```bash
# Check project structure
python scripts/project_structure.py

# Update version information
python scripts/version_manager.py

# Check API configuration
python scripts/APIsetting_check.py
```

## Architecture Overview

CodeDiary is a desktop application that generates programming diaries from Git commit history using AI providers. The application follows a modular MVC-style architecture:

### Core Components

- **Entry Point**: `main.py` - Tkinter application initialization
- **Main UI Controller**: `app/main_window.py` - Orchestrates all UI components and business logic
- **Diary Generation Engine**: `service/programming_diary_generator.py` - Core business logic for AI-powered diary generation
- **Git Service**: `service/git_commit_history.py` - Git command execution and commit history extraction
- **AI Provider System**: `external_service/` - Factory pattern for multiple AI providers (Claude, OpenAI, Gemini)

### AI Provider Architecture

The application uses a factory pattern (`external_service/api_factory.py`) to support multiple AI providers with automatic fallback:

1. **Primary Provider**: Configured in `utils/config.ini`
2. **Fallback System**: Automatic switching when primary provider fails
3. **Supported Providers**: Claude (Anthropic), OpenAI, Gemini (Google)

### Configuration Management

- **Environment Variables**: API keys loaded from `.env` file via `utils/env_loader.py`
- **Application Config**: `utils/config.ini` for UI settings, provider selection, and Chrome path
- **Config Manager**: `utils/config_manager.py` centralizes all configuration access

### Widget System

Modular UI components in `widgets/`:
- `date_selection_widget.py` - Calendar-based date range selection
- `diary_content_widget.py` - Diary display and clipboard integration
- `control_buttons_widget.py` - Action buttons (generate, Google Form submit)
- `progress_widget.py` - Task progress indication

### Service Layer

- **Programming Diary Generator**: Combines Git history with AI to create structured diaries
- **Google Form Automation**: Playwright-based browser automation for form submission
- **Git Commit History**: Git command wrapper with date filtering and formatting

## Key Design Patterns

1. **Factory Pattern**: AI provider selection and instantiation
2. **Template Method**: Diary generation workflow with AI provider abstraction
3. **Strategy Pattern**: Multiple AI providers implementing common interface
4. **Configuration Management**: Centralized config with environment variable override

## Development Notes

- **AI Prompt Template**: `prompt_template.md` defines the structured diary format
- **Localization**: Japanese locale setup with UTF-8 encoding
- **Error Handling**: Comprehensive exception handling with fallback mechanisms
- **Testing**: Pytest with coverage reporting for core services
- **Build Process**: PyInstaller with automatic version management

## Environment Setup

Required environment variables in `.env`:
```env
# At least one AI provider required
CLAUDE_API_KEY=your_key_here
CLAUDE_MODEL=claude-3-5-haiku-20241022

OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini

GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

## Important File Relationships

- `main.py` → `app/main_window.py` → Widget orchestration
- `programming_diary_generator.py` → `api_factory.py` → AI provider instances
- `config_manager.py` ↔ `env_loader.py` → Unified configuration access
- `prompt_template.md` → Loaded by diary generator for AI prompts
- `build.py` → `version_manager.py` → Automated version updates

The application emphasizes modularity, error resilience, and multi-provider AI integration while maintaining a clean separation between UI, business logic, and external services.