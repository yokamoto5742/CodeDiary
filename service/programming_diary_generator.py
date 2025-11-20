import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

from external_service.api_factory import APIFactory
from service.git_commit_history import GitCommitHistoryService
from service.github_commit_tracker import GitHubCommitTracker
from utils.config_manager import get_active_provider, get_provider_credentials, load_config,get_ai_provider_config, get_available_providers
from utils.env_loader import load_environment_variables
from utils.repository_name_extractor import get_repository_directory_name


class ProgrammingDiaryGenerator:
    """Gitコミット履歴から生成AIモデルを使用して日誌を生成"""
    def __init__(self):
        load_environment_variables()
        self.config = load_config()
        self.git_service = GitCommitHistoryService()
        self.ai_provider: Optional[str] = None
        self.ai_client: Any = None
        self.prompt_template_path = self._get_prompt_template_path()
        self.jst = timezone(timedelta(hours=9))
        self.default_model: Optional[str] = None
        self._initialize_ai_provider()

    def _get_prompt_template_path(self) -> str:
        """プロンプトテンプレートファイルのパスを取得"""
        base_path = Path(__file__).parent.parent
        return str(base_path / "utils" / "prompt_template.md")

    def _initialize_ai_provider(self):
        """設定から優先AIプロバイダーを初期化"""
        try:
            self.ai_provider = get_active_provider()
            print(f"使用するAIプロバイダー: {self.ai_provider}")

            self.ai_client = APIFactory.create_client(self.ai_provider)

            credentials = get_provider_credentials(self.ai_provider)
            if self.ai_client is not None:
                if credentials:
                    self.default_model = credentials.get('model', self.ai_client.default_model)
                else:
                    self.default_model = self.ai_client.default_model

                print(f"使用するモデル: {self.default_model}")

        except Exception as e:
            print(f"AIプロバイダーの初期化でエラーが発生しました: {e}")
            raise

    def _load_prompt_template(self) -> str:
        """プロンプトテンプレートファイルを読み込む"""
        try:
            with open(self.prompt_template_path, encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"プロンプトテンプレートファイルが見つかりません: {self.prompt_template_path}")
        except Exception as e:
            raise Exception(f"プロンプトテンプレートの読み込みに失敗しました: {e}")

    def _format_commits_for_prompt(self, commits: List[Dict]) -> str:
        """コミット情報を生成AIプロンプト用にフォーマット"""
        if not commits:
            return "コミット履歴がありません。"

        formatted_commits = []
        for commit in commits:
            try:
                dt = datetime.fromisoformat(commit['timestamp'])
                weekdays = ['月', '火', '水', '木', '金', '土', '日']
                weekday = weekdays[dt.weekday()]
                date_str = dt.strftime(f"%Y年%m月%d日({weekday})")
            except (ValueError, IndexError):
                date_str = commit['timestamp']

            commit_info = f"日時: {date_str}\nメッセージ: {commit['message']}\n"
            formatted_commits.append(commit_info)

        return "\n".join(formatted_commits)

    def _convert_markdown_to_plain_text(self, markdown_text: str) -> str:
        """生成AIが生成したMarkdown形式の日誌をプレーンテキストに変換"""
        patterns = [
            (r'^#{1,6}\s*', ''),
            (r'^\s*[-*+]\s*', ''),
            (r'^\s*\d+\.\s*', ''),
            (r'\*\*([^*]+)\*\*', r'\1'),
            (r'\*([^*]+)\*', r'\1'),
            (r'__([^_]+)__', r'\1'),
            (r'_([^_]+)_', r'\1'),
            (r'```[^`]*```', ''),
            (r'`([^`]+)`', r'\1'),
            (r'^[-–—]{3,}$', '---'),
            (r'\n{3,}', '\n\n'),
        ]

        plain_text = markdown_text

        for pattern, replacement in patterns:
            flags = re.MULTILINE if pattern.startswith('^') else 0
            if pattern == r'```[^`]*```':
                flags = re.DOTALL
            plain_text = re.sub(pattern, replacement, plain_text, flags=flags)

        return plain_text.strip()

    def _try_fallback_provider(self, since_date: Optional[str], until_date: Optional[str], days: Optional[int], original_error: Exception, use_github: bool = False):
        """プロバイダーエラー時にフォールバックプロバイダーで再試行"""
        try:
            config = get_ai_provider_config()
            available_providers = get_available_providers()
            fallback_provider = config.get('fallback_provider')

            if fallback_provider and available_providers.get(fallback_provider, False):
                print(
                    f"⚠️ メインプロバイダーでエラーが発生しました。フォールバックプロバイダー '{fallback_provider}' を試行します...")

                self.ai_provider = fallback_provider
                self.ai_client = APIFactory.create_client(fallback_provider)
                credentials = get_provider_credentials(fallback_provider)
                if self.ai_client is not None and credentials:
                    self.default_model = credentials.get('model', self.ai_client.default_model)

                return self.generate_diary(since_date, until_date, days, use_github)
            else:
                raise Exception(f"プロバイダーエラー (フォールバック不可): {original_error}")

        except Exception as fallback_error:
            raise Exception(
                f"プログラミング日記の生成に失敗しました。\n元のエラー: {original_error}\nフォールバックエラー: {fallback_error}")

    def generate_diary(self,
                       since_date: Optional[str] = None,
                       until_date: Optional[str] = None,
                       days: Optional[int] = None,
                       use_github: bool = False) -> Tuple[str, int, int, str]:
        """コミット履歴からAIで日誌を生成。GitHub APIまたはローカルGitから取得"""
        try:
            if self.ai_client is None:
                raise Exception("AIクライアントが初期化されていません")
            self.ai_client.initialize()

            if days:
                since_date = (datetime.now(self.jst) - timedelta(days=days)).strftime('%Y-%m-%d')
                until_date = (datetime.now(self.jst) + timedelta(days=1)).strftime('%Y-%m-%d')

            print(f"🔍 デバッグ情報:")
            print(f"   AIプロバイダー: {self.ai_provider}")
            print(f"   使用モデル: {self.default_model}")

            github_tracker = None
            commits: List[Dict] = []
            if use_github:
                print(f"   データソース: GitHub API (複数リポジトリ)")

                try:
                    github_tracker = GitHubCommitTracker()
                    print(f"   GitHubユーザー: {github_tracker.username}")

                    if since_date and until_date:
                        commits = github_tracker.get_commits_for_diary_generation_range(since_date, until_date)
                        print(f"   検索期間: {since_date} から {until_date}")
                    elif since_date:
                        commits = github_tracker.get_commits_for_diary_generation(since_date)
                        print(f"   検索期間: {since_date}")
                    else:
                        today = datetime.now().strftime('%Y-%m-%d')
                        commits = github_tracker.get_commits_for_diary_generation(today)
                        print(f"   検索期間: {today}")

                except Exception as e:
                    print(f"   GitHub APIエラー: {e}")
                    print(f"   ローカルGitリポジトリにフォールバック")
                    use_github = False

            if not use_github:
                print(f"   データソース: ローカルGitリポジトリ")
                print(f"   リポジトリパス: {self.git_service.repository_path}")
                print(f"   検索期間: {since_date} から {until_date}")

                repo_info = self.git_service.get_repository_info()
                print(f"   現在のブランチ: {repo_info['current_branch']}")
                print(f"   最新コミット: {repo_info['latest_commit']}")

                if since_date is None or until_date is None:
                    raise Exception("日付が指定されていません")

                commits = self.git_service.get_commit_history(since_date=since_date, until_date=until_date)

            print(f"   取得したコミット数: {len(commits)}")

            prompt_template = self._load_prompt_template()
            formatted_commits = self._format_commits_for_prompt(commits)
            full_prompt = f"{prompt_template}\n\n## Git コミット履歴\n\n{formatted_commits}"

            if self.ai_client is None or self.default_model is None:
                raise Exception("AIクライアントまたはモデルが設定されていません")

            diary_content, input_tokens, output_tokens = self.ai_client.generate_content(
                prompt=full_prompt,
                model_name=self.default_model
            )

            plain_diary = self._convert_markdown_to_plain_text(diary_content)

            try:
                if use_github and github_tracker:
                    project_name = f"GitHub Account: {github_tracker.username}"
                else:
                    project_name = get_repository_directory_name()
                project_diary = f"{project_name}\n{plain_diary}"
            except Exception as e:
                print(f"プロジェクト名の取得に失敗しました: {e}")
                project_diary = plain_diary

            return project_diary, input_tokens, output_tokens, self.default_model

        except Exception as e:
            return self._try_fallback_provider(
                since_date, until_date, days, e, use_github
            )
