import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

import requests

from utils.config_manager import load_config


class GitHubCommitTracker:
    """GitHubアカウント全体の今日のコミット履歴を取得するクラス"""

    def __init__(self, token: str = None, username: str = None):
        """
        初期化

        Args:
            token: GitHub Personal Access Token
            username: GitHubユーザー名
        """
        self.config = load_config()
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.username = username or os.getenv('GITHUB_USERNAME')

        if not self.token or not self.username:
            raise ValueError("GitHub TokenとUsernameが設定されていません。環境変数GITHUB_TOKENとGITHUB_USERNAMEを設定してください。")

        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'

    def get_user_repositories(self) -> List[Dict[str, Any]]:
        """ユーザーのすべてのリポジトリを取得"""
        repos = []
        page = 1
        per_page = 100

        while True:
            url = f'{self.base_url}/user/repos'
            params = {
                'page': page,
                'per_page': per_page,
                'sort': 'updated',
                'affiliation': 'owner,collaborator,organization_member'
            }

            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=30)

                if response.status_code != 200:
                    print(f"リポジトリ取得エラー: {response.status_code}")
                    break

                page_repos = response.json()
                if not page_repos:
                    break

                repos.extend(page_repos)
                page += 1

                if len(page_repos) < per_page:
                    break

            except requests.exceptions.RequestException as e:
                print(f"リポジトリ取得中にネットワークエラーが発生: {e}")
                break

        return repos

    def get_commits_for_repo_by_date(self, repo_name: str, target_date: str) -> List[Dict[str, Any]]:
        """指定したリポジトリの指定日のコミットを取得"""
        try:
            target_datetime = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError(f"日付形式が不正です: {target_date}。YYYY-MM-DD形式で入力してください。")

        since = datetime.combine(target_datetime, datetime.min.time()).isoformat() + 'Z'
        until = datetime.combine(target_datetime + timedelta(days=1), datetime.min.time()).isoformat() + 'Z'

        url = f'{self.base_url}/repos/{self.username}/{repo_name}/commits'
        params = {
            'author': self.username,
            'since': since,
            'until': until
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            if response.status_code == 404:
                return []  # リポジトリが見つからないまたはアクセス権限がない
            elif response.status_code != 200:
                print(f"リポジトリ {repo_name} のコミット取得エラー: {response.status_code}")
                return []

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"リポジトリ {repo_name} のコミット取得中にネットワークエラー: {e}")
            return []

    def get_all_commits_by_date(self, target_date: str) -> Dict[str, List[Dict[str, Any]]]:
        """すべてのリポジトリから指定日のコミットを取得"""
        repos = self.get_user_repositories()
        all_commits = {}

        print(f"チェック対象リポジトリ数: {len(repos)}")

        for repo in repos:
            repo_name = repo['name']
            print(f"チェック中: {repo_name}")

            commits = self.get_commits_for_repo_by_date(repo_name, target_date)

            if commits:
                all_commits[repo_name] = commits
                print(f"  → {len(commits)} 件のコミットが見つかりました")

        return all_commits

    def get_today_commits(self) -> Dict[str, List[Dict[str, Any]]]:
        """今日のコミットを取得"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_all_commits_by_date(today)

    def format_commits_output(self, commits_by_repo: Dict[str, List[Dict[str, Any]]], target_date: str = None) -> str:
        """コミット情報を整理して表示用文字列を生成"""
        if not commits_by_repo:
            date_str = target_date or "今日"
            return f"{date_str}のコミットはありません。"

        total_commits = sum(len(commits) for commits in commits_by_repo.values())
        date_str = target_date or "今日"

        output = []
        output.append("=" * 100)
        output.append(f"{date_str}のGitHubコミット履歴 ({total_commits} 件)")
        output.append("=" * 100)
        output.append("")

        for repo_name, commits in commits_by_repo.items():
            output.append(f"📁 リポジトリ: {repo_name}")
            output.append("-" * 50)

            for commit in commits:
                try:
                    commit_date = datetime.fromisoformat(
                        commit['commit']['author']['date'].replace('Z', '+00:00')
                    ).strftime('%H:%M:%S')
                except (ValueError, KeyError):
                    commit_date = "時刻不明"

                message = commit['commit']['message'].split('\n')[0]  # 最初の行のみ
                sha = commit['sha'][:7]

                output.append(f"  {commit_date} [{sha}] {message}")

            output.append("")

        return '\n'.join(output)

    def get_commits_for_diary_generation(self, target_date: str) -> List[Dict[str, Any]]:
        """日記生成用のコミット情報を取得（GitCommitHistoryServiceと同じ形式）"""
        commits_by_repo = self.get_all_commits_by_date(target_date)

        # GitCommitHistoryService.get_commit_history()と同じ形式に変換
        formatted_commits = []

        for repo_name, commits in commits_by_repo.items():
            for commit in commits:
                try:
                    # ISO形式の日時を取得
                    timestamp_iso = commit['commit']['author']['date']

                    # JST変換
                    dt_utc = datetime.fromisoformat(timestamp_iso.replace('Z', '+00:00'))
                    dt_jst = dt_utc.astimezone(datetime.now().astimezone().tzinfo)
                    timestamp_jst = dt_jst.isoformat()

                    formatted_commits.append({
                        'hash': commit['sha'],
                        'author_name': commit['commit']['author']['name'],
                        'author_email': commit['commit']['author']['email'],
                        'timestamp': timestamp_jst,
                        'message': f"[{repo_name}] {commit['commit']['message']}",  # リポジトリ名を追加
                        'repository': repo_name  # 追加情報
                    })

                except (KeyError, ValueError) as e:
                    print(f"コミット情報の変換でエラー: {e}")
                    continue

        # 時刻順にソート（新しい順）
        formatted_commits.sort(key=lambda x: x['timestamp'], reverse=True)

        return formatted_commits