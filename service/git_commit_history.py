import json
import os
import sys
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict

from utils.config_manager import load_config

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class GitCommitHistoryService:
    def __init__(self):
        self.config = load_config()
        self.repository_path = self._get_repository_path()
        self.jst = timezone(timedelta(hours=9))

    def _get_repository_path(self) -> str:
        try:
            repo_path = self.config.get('GIT', 'repository_path', fallback=str(Path(__file__).parent.parent))

            if not os.path.exists(repo_path):
                raise Exception(f"リポジトリパスが存在しません: {repo_path}")

            git_dir = os.path.join(repo_path, '.git')
            if not os.path.exists(git_dir):
                raise Exception(f"指定されたパスはGitリポジトリではありません: {repo_path}")

            return repo_path
        except Exception as e:
            raise Exception(f"リポジトリパスの取得に失敗しました: {e}")

    def _get_subprocess_kwargs(self):
        kwargs = {
            'capture_output': True,
            'text': True,
            'encoding': 'utf-8'
        }

        if os.name == 'nt':
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

        return kwargs

    def get_commit_history(self,
                           since_date: str = None,
                           until_date: str = None,
                           author: str = None,
                           max_count: int = None,
                           branch: str = None) -> List[Dict]:
        cmd = ['git', 'log', '--pretty=format:%H|%an|%ae|%aI|%s']

        env = os.environ.copy()
        env['TZ'] = 'Asia/Tokyo'

        if since_date:
            since_datetime = f"{since_date} 00:00:00 +0900"
            cmd.append(f'--since={since_datetime}')
        if until_date:
            until_datetime = f"{until_date} 23:59:59 +0900"
            cmd.append(f'--until={until_datetime}')

        try:
            subprocess_kwargs = self._get_subprocess_kwargs()
            subprocess_kwargs['env'] = env
            subprocess_kwargs['cwd'] = self.repository_path

            result = subprocess.run(cmd, **subprocess_kwargs)

            if result.returncode != 0:
                raise Exception(f"Gitコマンドの実行に失敗しました: {result.stderr}")

            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 5:
                        timestamp_utc = parts[3]
                        try:
                            dt_utc = datetime.fromisoformat(timestamp_utc.replace('Z', '+00:00'))
                            dt_jst = dt_utc.astimezone(self.jst)
                            timestamp_jst = dt_jst.isoformat()
                        except ValueError:
                            # 変換に失敗した場合は元のタイムスタンプを使用
                            timestamp_jst = timestamp_utc

                        commits.append({
                            'hash': parts[0],
                            'author_name': parts[1],
                            'author_email': parts[2],
                            'timestamp': timestamp_jst,
                            'message': '|'.join(parts[4:])
                        })

            return commits

        except subprocess.SubprocessError as e:
            raise Exception(f"Gitコマンドの実行でエラーが発生しました: {e}")
        except Exception as e:
            raise Exception(f"コミット履歴の取得に失敗しました: {e}")

    def format_output(self, commits: List[Dict], output_format: str = 'table') -> str:
        if not commits:
            return "コミット履歴が見つかりませんでした。"

        if output_format == 'json':
            simplified_commits = []
            for commit in commits:
                simplified_commits.append({
                    'timestamp': commit['timestamp'],
                    'message': commit['message']
                })
            return json.dumps(simplified_commits, ensure_ascii=False, indent=2)

        elif output_format == 'llm_json':
            return json.dumps(commits, ensure_ascii=False, indent=2)

        output = []
        output.append("=" * 100)
        output.append(f"コミット履歴 ({len(commits)}件)")
        output.append(f"リポジトリ: {self.repository_path}")
        output.append("=" * 100)
        output.append("")

        for i, commit in enumerate(commits, 1):
            try:
                dt = datetime.fromisoformat(commit['timestamp'])
                formatted_time = dt.strftime("%Y/%m/%d %H:%M:%S (JST)")
            except ValueError:
                formatted_time = commit['timestamp']

            output.append(f"{i:3d}. {formatted_time}")
            output.append(f"     メッセージ: {commit['message']}")
            output.append("")

        return '\n'.join(output)

    def get_repository_info(self) -> Dict:
        try:
            env = os.environ.copy()
            env['TZ'] = 'Asia/Tokyo'

            # subprocess実行時にコンソールウィンドウを表示しない設定を適用
            subprocess_kwargs = self._get_subprocess_kwargs()
            subprocess_kwargs['env'] = env
            subprocess_kwargs['cwd'] = self.repository_path

            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                **subprocess_kwargs
            )
            current_branch = branch_result.stdout.strip()

            remote_result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                **subprocess_kwargs
            )
            remote_url = remote_result.stdout.strip() if remote_result.returncode == 0 else "未設定"

            latest_commit_result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%H|%an|%aI'],
                **subprocess_kwargs
            )

            latest_commit_info = "情報なし"
            if latest_commit_result.returncode == 0 and latest_commit_result.stdout:
                parts = latest_commit_result.stdout.split('|')
                if len(parts) >= 3:
                    try:
                        dt_utc = datetime.fromisoformat(parts[2].replace('Z', '+00:00'))
                        dt_jst = dt_utc.astimezone(self.jst)
                        formatted_time = dt_jst.strftime("%Y/%m/%d %H:%M JST")
                    except ValueError:
                        formatted_time = parts[2]
                    latest_commit_info = f"{parts[0][:8]} by {parts[1]} on {formatted_time}"

            return {
                'path': self.repository_path,
                'current_branch': current_branch,
                'remote_url': remote_url,
                'latest_commit': latest_commit_info
            }
        except Exception as e:
            return {
                'path': self.repository_path,
                'current_branch': 'エラー',
                'remote_url': f'取得エラー: {e}',
                'latest_commit': 'エラー'
            }

    def get_branch_list(self) -> List[str]:
        try:
            env = os.environ.copy()
            env['TZ'] = 'Asia/Tokyo'

            subprocess_kwargs = self._get_subprocess_kwargs()
            subprocess_kwargs['env'] = env
            subprocess_kwargs['cwd'] = self.repository_path

            result = subprocess.run(
                ['git', 'branch', '-a'],
                **subprocess_kwargs
            )

            if result.returncode != 0:
                return []

            branches = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    branch = line.strip().lstrip('* ')
                    if not branch.startswith('remotes/origin/HEAD'):
                        branches.append(branch)

            return branches
        except Exception:
            return []
