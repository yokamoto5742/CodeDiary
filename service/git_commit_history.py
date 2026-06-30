import os
import subprocess
from abc import ABC
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from utils.config_manager import load_config


class BaseCommitService(ABC):
    """コミット処理の共通基盤を提供する抽象基底クラス"""
    def __init__(self):
        self.config = load_config()
        self.jst = timezone(timedelta(hours=9))

    def _convert_utc_to_jst(self, timestamp_utc: str) -> str:
        """UTC形式のタイムスタンプを日本時間に変換"""
        try:
            dt_utc = datetime.fromisoformat(timestamp_utc.replace('Z', '+00:00'))
            dt_jst = dt_utc.astimezone(self.jst)
            return dt_jst.isoformat()
        except ValueError:
            return timestamp_utc

    def _format_commit_data(self, hash_val: str, author_name: str, author_email: str,
                           timestamp: str, message: str, repository: Optional[str] = None) -> Dict:
        """コミットデータを共通フォーマットで整形"""
        formatted_data = {
            'hash': hash_val,
            'author_name': author_name,
            'author_email': author_email,
            'timestamp': self._convert_utc_to_jst(timestamp),
            'message': message
        }
        if repository:
            formatted_data['repository'] = repository
        return formatted_data

    def _get_subprocess_kwargs(self):
        """subprocess実行時の標準的な引数を生成"""
        kwargs = {
            'capture_output': True,
            'text': True,
            'encoding': 'utf-8'
        }

        if os.name == 'nt':
            kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

        return kwargs
