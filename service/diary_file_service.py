import subprocess
from pathlib import Path

from utils.config_manager import load_config


def build_diary_path(until_date: str) -> Path:
    """対象期間の終了日から日誌ファイルの保存先パスを組み立てる"""
    daily_dir = Path(load_config().get('Path', 'daily_path'))
    return daily_dir / f"{until_date}_プログラミング学習日誌.md"


def save_diary(file_path: Path, content: str) -> None:
    """日誌内容をMarkdownファイルとして保存"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding='utf-8')


def launch_obsidian() -> None:
    """Obsidianを起動"""
    subprocess.Popen([load_config().get('Obsidian', 'obsidian_path')])
