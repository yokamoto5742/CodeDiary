import re
import subprocess
from pathlib import Path
from typing import List, Tuple

from utils.config_manager import load_config

SECTION_HEADING_PATTERN = re.compile(r'^## .*$', re.MULTILINE)


def build_diary_path(until_date: str) -> Path:
    """対象期間の終了日から日誌ファイルの保存先パスを組み立てる"""
    daily_dir = Path(load_config().get('Path', 'daily_path'))
    return daily_dir / f"{until_date}_プログラミング学習日誌.md"


def _split_sections(content: str) -> List[Tuple[str, str]]:
    """Markdownを見出し(##)ごとに(見出し, 本文)へ分割する。最初の見出しより前の部分は見出しを空文字にする"""
    headings = list(SECTION_HEADING_PATTERN.finditer(content))
    sections = []

    preamble = content[:headings[0].start()] if headings else content
    if preamble.strip():
        sections.append(('', preamble.strip()))

    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(content)
        sections.append((heading.group().strip(), content[heading.end():end].strip()))

    return sections


def _merge_content(existing_content: str, new_content: str) -> str:
    """既存の内容に新しい内容を見出しごとに追記する。新しい内容は見出しの直後（既存本文の前）へ挿入する"""
    merged = [[heading, body] for heading, body in _split_sections(existing_content)]
    indexes = {heading: index for index, (heading, _) in enumerate(merged)}

    for heading, body in _split_sections(new_content):
        if not body:
            continue
        if heading in indexes:
            section = merged[indexes[heading]]
            section[1] = f"{body}\n\n{section[1]}".strip()
        else:
            indexes[heading] = len(merged)
            merged.append([heading, body])

    return "\n\n".join(f"{heading}\n\n{body}".strip() for heading, body in merged) + "\n"


def save_diary(file_path: Path, content: str) -> None:
    """日誌内容をMarkdownファイルとして保存する。同名ファイルがある場合は見出しごとに追記する"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        content = _merge_content(file_path.read_text(encoding='utf-8'), content)
    file_path.write_text(content, encoding='utf-8')


def launch_obsidian() -> None:
    """Obsidianを起動"""
    subprocess.Popen([load_config().get('Obsidian', 'obsidian_path')])
