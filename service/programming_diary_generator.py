import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from external_service.api_factory import APIFactory
from service.git_commit_history import GitCommitHistoryService
from utils.config_manager import get_active_provider, get_provider_credentials, load_config,get_ai_provider_config, get_available_providers
from utils.env_loader import load_environment_variables
from utils.repository_name_extractor import get_repository_directory_name


class ProgrammingDiaryGenerator:
    def __init__(self):
        load_environment_variables()
        self.config = load_config()
        self.git_service = GitCommitHistoryService()
        self.ai_provider = None
        self.ai_client = None
        self.prompt_template_path = self._get_prompt_template_path()
        self.jst = timezone(timedelta(hours=9))
        self._initialize_ai_provider()

    def _get_prompt_template_path(self) -> str:
        base_path = Path(__file__).parent.parent
        return str(base_path / "prompt_template.md")

    def _initialize_ai_provider(self):
        try:
            self.ai_provider = get_active_provider()
            print(f"使用するAIプロバイダー: {self.ai_provider}")

            self.ai_client = APIFactory.create_client(self.ai_provider)

            credentials = get_provider_credentials(self.ai_provider)
            if credentials:
                self.default_model = credentials.get('model', self.ai_client.default_model)
            else:
                self.default_model = self.ai_client.default_model

            print(f"使用するモデル: {self.default_model}")

        except Exception as e:
            print(f"AIプロバイダーの初期化でエラーが発生しました: {e}")
            raise

    def _load_prompt_template(self) -> str:
        try:
            with open(self.prompt_template_path, encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"プロンプトテンプレートファイルが見つかりません: {self.prompt_template_path}")
        except Exception as e:
            raise Exception(f"プロンプトテンプレートの読み込みに失敗しました: {e}")

    def _format_commits_for_prompt(self, commits: List[Dict]) -> str:
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
        patterns = [
            (r'^#{1,6}\s*', ''),  # ヘッダー
            (r'^\s*[-*+]\s*', ''),  # 箇条書き
            (r'^\s*\d+\.\s*', ''),  # 番号付きリスト
            (r'\*\*([^*]+)\*\*', r'\1'),  # 太字(**)
            (r'\*([^*]+)\*', r'\1'),  # 斜体(*)
            (r'__([^_]+)__', r'\1'),  # 太字(__)
            (r'_([^_]+)_', r'\1'),  # 斜体(_)
            (r'```[^`]*```', ''),  # コードブロック
            (r'`([^`]+)`', r'\1'),  # インラインコード
            (r'^[-–—]{3,}$', '---'),  # 水平線
            (r'\n{3,}', '\n\n'),  # 連続改行
        ]

        plain_text = markdown_text

        for pattern, replacement in patterns:
            flags = re.MULTILINE if pattern.startswith('^') else 0
            if pattern == r'```[^`]*```':
                flags = re.DOTALL
            plain_text = re.sub(pattern, replacement, plain_text, flags=flags)

        return plain_text.strip()

    def generate_diary(self,
                       since_date: Optional[str] = None,
                       until_date: Optional[str] = None,
                       days: Optional[int] = None,
                       author: Optional[str] = None,
                       max_count: Optional[int] = None) -> Tuple[str, int, int]:
        try:
            self.ai_client.initialize()

            if days:
                since_date = (datetime.now(self.jst) - timedelta(days=days)).strftime('%Y-%m-%d')
                until_date = (datetime.now(self.jst) + timedelta(days=1)).strftime('%Y-%m-%d')

            print(f"🔍 デバッグ情報:")
            print(f"   AIプロバイダー: {self.ai_provider}")
            print(f"   使用モデル: {self.default_model}")
            print(f"   リポジトリパス: {self.git_service.repository_path}")
            print(f"   検索期間: {since_date} から {until_date}")
            print(f"   作成者フィルタ: {author or '全て'}")

            repo_info = self.git_service.get_repository_info()
            print(f"   現在のブランチ: {repo_info['current_branch']}")
            print(f"   最新コミット: {repo_info['latest_commit']}")

            commits = self.git_service.get_commit_history(
                since_date=since_date,
                until_date=until_date,
                author=author,
                max_count=max_count
            )

            print(f"   取得したコミット数: {len(commits)}")

            if not commits:
                print("⚠️ 指定期間にコミットが見つかりませんでした。過去7日間で再検索します...")
                extended_since = (datetime.now(self.jst) - timedelta(days=7)).strftime('%Y-%m-%d')
                extended_commits = self.git_service.get_commit_history(
                    since_date=extended_since,
                    until_date=until_date,
                    author=author,
                    max_count=5
                )
                if extended_commits:
                    print(f"   過去7日間では {len(extended_commits)} 件のコミットが見つかりました")
                    print("   最新のコミット:")
                    for i, commit in enumerate(extended_commits[:3]):
                        print(f"     {i + 1}. {commit['timestamp']}: {commit['message']}")
                else:
                    print("   過去7日間でもコミットが見つかりませんでした")

                return "指定期間にコミット履歴が見つかりませんでした。", 0, 0

            prompt_template = self._load_prompt_template()
            formatted_commits = self._format_commits_for_prompt(commits)
            full_prompt = f"{prompt_template}\n\n## Git コミット履歴\n\n{formatted_commits}"

            diary_content, input_tokens, output_tokens = self.ai_client._generate_content(
                prompt=full_prompt,
                model_name=self.default_model
            )

            plain_diary = self._convert_markdown_to_plain_text(diary_content)

            try:
                project_name = get_repository_directory_name()
                project_diary = f"{project_name}\n{plain_diary}"
            except Exception as e:
                print(f"プロジェクト名の取得に失敗しました: {e}")

            return project_diary, input_tokens, output_tokens

        except Exception as e:
            return self._try_fallback_provider(
                since_date, until_date, days, author, max_count, str(e)
            )

    def _try_fallback_provider(self, since_date, until_date, days, author, max_count, original_error):
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
                if credentials:
                    self.default_model = credentials.get('model', self.ai_client.default_model)

                return self.generate_diary(since_date, until_date, days, author, max_count)
            else:
                raise Exception(f"プロバイダーエラー (フォールバック不可): {original_error}")

        except Exception as fallback_error:
            raise Exception(
                f"プログラミング日誌の生成に失敗しました。\n元のエラー: {original_error}\nフォールバックエラー: {fallback_error}")
