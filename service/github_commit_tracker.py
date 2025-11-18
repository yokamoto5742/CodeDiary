import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Tuple

import requests

from service.git_commit_history import BaseCommitService


class GitHubCommitTracker(BaseCommitService):
    def __init__(self, token: str = None, username: str = None):
        super().__init__()
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.username = username or os.getenv('GITHUB_USERNAME')

        if not self.token or not self.username:
            raise ValueError("GitHub TokenとUsernameが設定されていません。環境変数GITHUB_TOKENとGITHUB_USERNAMEを設定してください。")

        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'

    def _convert_date_to_utc_range(self, start_date: str, end_date: str = None) -> Tuple[str, str]:
        """日付文字列をUTC ISO形式の範囲に変換"""
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date or start_date, '%Y-%m-%d').date()

        since_jst = datetime.combine(start, datetime.min.time()).replace(tzinfo=self.jst)
        until_jst = datetime.combine(end + timedelta(days=1), datetime.min.time()).replace(tzinfo=self.jst)

        return (
            since_jst.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z'),
            until_jst.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
        )

    def get_user_repositories(self) -> List[Dict[str, Any]]:
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
        try:
            since, until = self._convert_date_to_utc_range(target_date)
        except ValueError:
            raise ValueError(f"日付形式が不正です: {target_date}。YYYY-MM-DD形式で入力してください。")

        url = f'{self.base_url}/repos/{self.username}/{repo_name}/commits'
        params = {
            'author': self.username,
            'since': since,
            'until': until
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            if response.status_code == 404:
                return []
            elif response.status_code != 200:
                print(f"リポジトリ {repo_name} のコミット取得エラー: {response.status_code}")
                return []

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"リポジトリ {repo_name} のコミット取得中にネットワークエラー: {e}")
            return []

    def get_all_commits_by_date(self, target_date: str) -> Dict[str, List[Dict[str, Any]]]:
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
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_all_commits_by_date(today)

    def format_commits_output(self, commits_by_repo: Dict[str, List[Dict[str, Any]]], target_date: str = None) -> str:
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
        commits_by_repo = self.get_all_commits_by_date(target_date)
        formatted_commits = []

        for repo_name, commits in commits_by_repo.items():
            for commit in commits:
                try:
                    formatted_commits.append(self._format_commit_data(
                        hash_val=commit['sha'],
                        author_name=commit['commit']['author']['name'],
                        author_email=commit['commit']['author']['email'],
                        timestamp=commit['commit']['author']['date'],
                        message=f"[{repo_name}] {commit['commit']['message']}",
                        repository=repo_name
                    ))

                except (KeyError, ValueError) as e:
                    print(f"コミット情報の変換でエラー: {e}")
                    continue

        formatted_commits.sort(key=lambda x: x['timestamp'], reverse=True)

        return formatted_commits

    def get_commits_for_repo_by_date_range(self, repo_name: str, since_date: str, until_date: str) -> List[
        Dict[str, Any]]:
        try:
            since, until = self._convert_date_to_utc_range(since_date, until_date)
        except ValueError:
            raise ValueError(f"日付形式が不正です。YYYY-MM-DD形式で入力してください。")

        url = f'{self.base_url}/repos/{self.username}/{repo_name}/commits'
        params = {
            'author': self.username,
            'since': since,
            'until': until
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            if response.status_code == 404:
                return []
            elif response.status_code != 200:
                print(f"リポジトリ {repo_name} のコミット取得エラー: {response.status_code}")
                return []
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"リポジトリ {repo_name} のコミット取得中にネットワークエラー: {e}")
            return []

    def get_all_commits_by_date_range(self, since_date: str, until_date: str) -> Dict[str, List[Dict[str, Any]]]:
        repos = self.get_user_repositories()
        all_commits = {}

        print(f"チェック対象リポジトリ数: {len(repos)}")
        print(f"期間: {since_date} から {until_date}")

        for repo in repos:
            repo_name = repo['name']
            print(f"チェック中: {repo_name}")

            commits = self.get_commits_for_repo_by_date_range(repo_name, since_date, until_date)

            if commits:
                all_commits[repo_name] = commits
                print(f"  → {len(commits)} 件のコミットが見つかりました")

        return all_commits

    def get_commits_for_diary_generation_range(self, since_date: str, until_date: str = None) -> List[Dict[str, Any]]:
        if until_date is None:
            return self.get_commits_for_diary_generation(since_date)

        commits_by_repo = self.get_all_commits_by_date_range(since_date, until_date)
        formatted_commits = []

        for repo_name, commits in commits_by_repo.items():
            for commit in commits:
                try:
                    formatted_commits.append(self._format_commit_data(
                        hash_val=commit['sha'],
                        author_name=commit['commit']['author']['name'],
                        author_email=commit['commit']['author']['email'],
                        timestamp=commit['commit']['author']['date'],
                        message=f"[{repo_name}] {commit['commit']['message']}",
                        repository=repo_name
                    ))
                except (KeyError, ValueError) as e:
                    print(f"コミット情報の変換でエラー: {e}")
                    continue

        formatted_commits.sort(key=lambda x: x['timestamp'], reverse=True)
        return formatted_commits
