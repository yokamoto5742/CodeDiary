import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from external_service.claude_api import ClaudeAPIClient
from service.git_commit_history import GitCommitHistoryService
from utils.config_manager import load_config
from utils.env_loader import load_environment_variables


class ProgrammingDiaryGenerator:
    def __init__(self):
        load_environment_variables()
        self.config = load_config()
        self.git_service = GitCommitHistoryService()
        self.claude_client = ClaudeAPIClient()
        self.prompt_template_path = self._get_prompt_template_path()
        self.jst = timezone(timedelta(hours=9))

    def _get_prompt_template_path(self) -> str:
        base_path = Path(__file__).parent.parent
        return str(base_path / "prompt_template.md")

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
            self.claude_client.initialize()

            if days:
                since_date = (datetime.now(self.jst) - timedelta(days=days)).strftime('%Y-%m-%d')
                until_date = (datetime.now(self.jst) + timedelta(days=1)).strftime('%Y-%m-%d')

            print(f"🔍 デバッグ情報:")
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

            diary_content, input_tokens, output_tokens = self.claude_client._generate_content(
                prompt=full_prompt,
                model_name=self.claude_client.default_model
            )

            plain_diary = self._convert_markdown_to_plain_text(diary_content)

            return plain_diary, input_tokens, output_tokens

        except Exception as e:
            raise Exception(f"プログラミング日誌の生成に失敗しました: {e}")
