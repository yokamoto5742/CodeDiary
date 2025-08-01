import os
import sys
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_manager import load_config, save_config


class GitCommitHistoryService:
    def __init__(self):
        """
        Gitコミット履歴取得サービス
        """
        self.config = self._load_or_create_config()
        self.repository_path = self._get_repository_path()

    def _load_or_create_config(self):
        """設定ファイルを読み込み、存在しない場合は作成"""
        try:
            config = load_config()

            # GITセクションが存在しない場合は作成
            if not config.has_section('GIT'):
                config.add_section('GIT')
                config.set('GIT', 'repository_path', str(Path(__file__).parent.parent))
                config.set('GIT', 'default_author', '')
                config.set('GIT', 'output_format', 'table')

                save_config(config)
                print("Git設定を config.ini に追加しました")

            # OUTPUTセクションが存在しない場合は作成
            if not config.has_section('OUTPUT'):
                config.add_section('OUTPUT')
                config.set('OUTPUT', 'save_to_file', 'True')
                config.set('OUTPUT', 'output_directory', 'logs')
                # シンプルなファイル名パターンを使用（%文字を避ける）
                config.set('OUTPUT', 'filename_format', 'commit_history_datetime.txt')

                save_config(config)
                print("Output設定を config.ini に追加しました")

            return config

        except Exception as e:
            raise Exception(f"設定ファイルの読み込みに失敗しました: {e}")

    def _get_repository_path(self) -> str:
        """リポジトリパスを取得"""
        try:
            repo_path = self.config.get('GIT', 'repository_path', fallback=str(Path(__file__).parent.parent))

            # 相対パスの場合は絶対パスに変換
            if not os.path.isabs(repo_path):
                repo_path = os.path.abspath(os.path.join(Path(__file__).parent.parent, repo_path))

            if not os.path.exists(repo_path):
                raise Exception(f"リポジトリパスが存在しません: {repo_path}")

            # .gitディレクトリの存在確認
            git_dir = os.path.join(repo_path, '.git')
            if not os.path.exists(git_dir):
                raise Exception(f"指定されたパスはGitリポジトリではありません: {repo_path}")

            return repo_path
        except Exception as e:
            raise Exception(f"リポジトリパスの取得に失敗しました: {e}")

    def get_commit_history(self,
                           since_date: str = None,
                           until_date: str = None,
                           author: str = None,
                           max_count: int = None,
                           branch: str = None) -> List[Dict]:
        """
        指定期間のコミット履歴を取得

        Args:
            since_date: 開始日 (YYYY-MM-DD形式)
            until_date: 終了日 (YYYY-MM-DD形式)
            author: 作成者名
            max_count: 最大取得件数
            branch: ブランチ名

        Returns:
            コミット履歴のリスト
        """
        cmd = ['git', 'log', '--pretty=format:%H|%an|%ae|%ad|%s', '--date=short']

        # 日付範囲の指定
        if since_date:
            cmd.append(f'--since={since_date}')
        if until_date:
            cmd.append(f'--until={until_date}')

        # 作成者の指定
        if author:
            cmd.append(f'--author={author}')
        elif self.config.get('GIT', 'default_author', fallback=''):
            cmd.append(f'--author={self.config.get("GIT", "default_author")}')

        # 最大件数の指定
        if max_count:
            cmd.append(f'--max-count={max_count}')

        # ブランチの指定
        if branch:
            cmd.append(branch)

        try:
            # Gitコマンドを実行
            result = subprocess.run(
                cmd,
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            if result.returncode != 0:
                raise Exception(f"Gitコマンドの実行に失敗しました: {result.stderr}")

            # 結果をパース
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|')
                    if len(parts) >= 5:
                        commits.append({
                            'hash': parts[0],
                            'author_name': parts[1],
                            'author_email': parts[2],
                            'date': parts[3],
                            'message': '|'.join(parts[4:])  # メッセージに|が含まれる場合に対応
                        })

            return commits

        except subprocess.SubprocessError as e:
            raise Exception(f"Gitコマンドの実行でエラーが発生しました: {e}")
        except Exception as e:
            raise Exception(f"コミット履歴の取得に失敗しました: {e}")

    def format_output(self, commits: List[Dict], output_format: str = 'table') -> str:
        """
        コミット履歴をフォーマット

        Args:
            commits: コミット履歴のリスト
            output_format: 出力形式 (table, json, csv)

        Returns:
            フォーマットされた文字列
        """
        if not commits:
            return "コミット履歴が見つかりませんでした。"

        if output_format == 'json':
            import json
            return json.dumps(commits, indent=2, ensure_ascii=False)

        elif output_format == 'csv':
            lines = ['ハッシュ,作成者,メール,日付,メッセージ']
            for commit in commits:
                # CSVのエスケープ処理
                message = commit["message"].replace('"', '""')
                lines.append(
                    f'"{commit["hash"]}","{commit["author_name"]}","{commit["author_email"]}","{commit["date"]}","{message}"')
            return '\n'.join(lines)

        else:  # table format
            output = []
            output.append("=" * 100)
            output.append(f"コミット履歴 ({len(commits)}件)")
            output.append(f"リポジトリ: {self.repository_path}")
            output.append("=" * 100)
            output.append("")

            for i, commit in enumerate(commits, 1):
                output.append(f"{i:3}. [{commit['date']}] {commit['author_name']}")
                output.append(f"     ハッシュ: {commit['hash'][:8]}...")
                output.append(f"     メッセージ: {commit['message']}")
                output.append(f"     メール: {commit['author_email']}")
                output.append("")

            return '\n'.join(output)

    def save_to_file(self, content: str, filename: str = None) -> str:
        """
        コンテンツをファイルに保存

        Args:
            content: 保存する内容
            filename: ファイル名（未指定の場合は設定から自動生成）

        Returns:
            保存したファイルのパス
        """
        if not filename:
            try:
                # 設定から読み取り
                filename_format = self.config.get('OUTPUT', 'filename_format', fallback='commit_history_datetime.txt')

                # 設定値に応じてファイル名を生成
                if filename_format == 'commit_history_datetime.txt':
                    # デフォルトパターン: 日時を含むファイル名
                    filename = datetime.now().strftime('commit_history_%Y%m%d_%H%M%S.txt')
                elif '%' in filename_format:
                    # strftimeフォーマットが含まれている場合
                    if '%%' in filename_format:
                        filename_format = filename_format.replace('%%', '%')
                    filename = datetime.now().strftime(filename_format)
                else:
                    # 静的なファイル名の場合
                    filename = filename_format

            except Exception:
                # 設定読み取りエラーの場合はデフォルトを使用
                filename = datetime.now().strftime('commit_history_%Y%m%d_%H%M%S.txt')

        # 出力ディレクトリの作成
        output_dir = self.config.get('OUTPUT', 'output_directory', fallback='logs')
        output_path = Path(self.repository_path) / output_dir
        output_path.mkdir(exist_ok=True)

        file_path = output_path / filename

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return str(file_path)
        except Exception as e:
            raise Exception(f"ファイルの保存に失敗しました: {e}")

    def get_repository_info(self) -> Dict:
        """リポジトリの基本情報を取得"""
        try:
            # 現在のブランチ
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repository_path,
                capture_output=True,
                text=True
            )
            current_branch = branch_result.stdout.strip()

            # リモートURL
            remote_result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.repository_path,
                capture_output=True,
                text=True
            )
            remote_url = remote_result.stdout.strip() if remote_result.returncode == 0 else "未設定"

            # 最新コミット情報
            latest_commit_result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%H|%an|%ad', '--date=short'],
                cwd=self.repository_path,
                capture_output=True,
                text=True
            )

            latest_commit_info = "情報なし"
            if latest_commit_result.returncode == 0 and latest_commit_result.stdout:
                parts = latest_commit_result.stdout.split('|')
                if len(parts) >= 3:
                    latest_commit_info = f"{parts[0][:8]} by {parts[1]} on {parts[2]}"

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
        """ブランチ一覧を取得"""
        try:
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=self.repository_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return []

            branches = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    # 現在のブランチを示す*や空白を除去
                    branch = line.strip().lstrip('* ')
                    if not branch.startswith('remotes/origin/HEAD'):
                        branches.append(branch)

            return branches
        except Exception:
            return []

    def get_authors_list(self, days: int = 365) -> List[str]:
        """作成者一覧を取得"""
        try:
            since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            result = subprocess.run(
                ['git', 'log', f'--since={since_date}', '--pretty=format:%an', '--all'],
                cwd=self.repository_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return []

            authors = list(set(result.stdout.strip().split('\n')))
            return [author for author in authors if author]
        except Exception:
            return []


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Gitコミット履歴取得サービス",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 過去7日間のコミット履歴を取得
  python git_commit_history_service.py --days 7

  # 指定期間のコミット履歴を取得
  python git_commit_history_service.py --since 2025-01-01 --until 2025-01-31

  # 特定の作成者のコミット履歴を取得
  python git_commit_history_service.py --author "山田太郎" --days 30

  # CSV形式で出力
  python git_commit_history_service.py --format csv --days 14

  # リポジトリ情報とブランチ一覧を表示
  python git_commit_history_service.py --info --list-branches
        """
    )

    parser.add_argument(
        '--since', '-s',
        help='開始日 (YYYY-MM-DD形式)'
    )
    parser.add_argument(
        '--until', '-u',
        help='終了日 (YYYY-MM-DD形式)'
    )
    parser.add_argument(
        '--days', '-d',
        type=int,
        help='過去X日間のコミット履歴を取得'
    )
    parser.add_argument(
        '--author', '-a',
        help='作成者名でフィルタ'
    )
    parser.add_argument(
        '--max-count', '-n',
        type=int,
        help='最大取得件数'
    )
    parser.add_argument(
        '--branch', '-b',
        help='対象ブランチ'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['table', 'json', 'csv'],
        default='table',
        help='出力形式 (デフォルト: table)'
    )
    parser.add_argument(
        '--output', '-o',
        help='出力ファイル名'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='ファイル保存をスキップ'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='リポジトリ情報を表示'
    )
    parser.add_argument(
        '--list-branches',
        action='store_true',
        help='ブランチ一覧を表示'
    )
    parser.add_argument(
        '--list-authors',
        action='store_true',
        help='作成者一覧を表示'
    )

    args = parser.parse_args()

    try:
        # GitCommitHistoryServiceのインスタンス作成
        service = GitCommitHistoryService()

        # リポジトリ情報の表示
        if args.info:
            repo_info = service.get_repository_info()
            print("=" * 80)
            print("リポジトリ情報")
            print("=" * 80)
            print(f"パス: {repo_info['path']}")
            print(f"現在のブランチ: {repo_info['current_branch']}")
            print(f"リモートURL: {repo_info['remote_url']}")
            print(f"最新コミット: {repo_info['latest_commit']}")
            print()

        # ブランチ一覧の表示
        if args.list_branches:
            branches = service.get_branch_list()
            print("=" * 80)
            print("ブランチ一覧")
            print("=" * 80)
            for branch in branches:
                print(f"  {branch}")
            print()

        # 作成者一覧の表示
        if args.list_authors:
            authors = service.get_authors_list()
            print("=" * 80)
            print("作成者一覧（過去1年間）")
            print("=" * 80)
            for author in sorted(authors):
                print(f"  {author}")
            print()

        # 情報表示のみの場合は終了
        if args.info or args.list_branches or args.list_authors:
            if not any([args.since, args.until, args.days]):
                return

        # 日付範囲の計算
        since_date = args.since
        until_date = args.until

        if args.days:
            since_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
            until_date = datetime.now().strftime('%Y-%m-%d')

        # デフォルトで過去30日を指定
        if not since_date and not until_date and not args.days:
            since_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            until_date = datetime.now().strftime('%Y-%m-%d')
            print(f"期間が指定されていないため、過去30日間のコミット履歴を取得します")

        # コミット履歴の取得
        print("コミット履歴を取得中...")
        commits = service.get_commit_history(
            since_date=since_date,
            until_date=until_date,
            author=args.author,
            max_count=args.max_count,
            branch=args.branch
        )

        # 出力のフォーマット
        output_format = args.format or service.config.get('GIT', 'output_format', fallback='table')
        formatted_output = service.format_output(commits, output_format)

        # コンソールに出力
        print(formatted_output)

        # ファイルに保存
        if not args.no_save:
            save_to_file = service.config.getboolean('OUTPUT', 'save_to_file', fallback=True)
            if save_to_file:
                saved_path = service.save_to_file(formatted_output, args.output)
                print(f"\n結果をファイルに保存しました: {saved_path}")

    except KeyboardInterrupt:
        print("\n処理が中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()