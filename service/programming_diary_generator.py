import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from external_service.claude_api import ClaudeAPIClient
from service.git_commit_history import GitCommitHistoryService
from utils.config_manager import load_config, save_config
from utils.env_loader import load_environment_variables


class ProgrammingDiaryGenerator:
    """プログラミング日誌生成サービス"""
    
    def __init__(self):
        """初期化"""
        load_environment_variables()
        self.config = load_config()
        self.git_service = GitCommitHistoryService()
        self.claude_client = ClaudeAPIClient()
        self.prompt_template_path = self._get_prompt_template_path()
        
    def _get_prompt_template_path(self) -> str:
        """プロンプトテンプレートファイルのパスを取得"""
        base_path = Path(__file__).parent.parent
        return str(base_path / "utils" / "prompt_template.md")
    
    def _load_prompt_template(self) -> str:
        """プロンプトテンプレートを読み込む"""
        try:
            with open(self.prompt_template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"プロンプトテンプレートファイルが見つかりません: {self.prompt_template_path}")
        except Exception as e:
            raise Exception(f"プロンプトテンプレートの読み込みに失敗しました: {e}")
    
    def _format_commits_for_prompt(self, commits: List[Dict]) -> str:
        """コミット履歴をプロンプト用にフォーマット"""
        if not commits:
            return "コミット履歴がありません。"
        
        formatted_commits = []
        for commit in commits:
            commit_info = f"日時: {commit['timestamp']}\nメッセージ: {commit['message']}\n"
            formatted_commits.append(commit_info)
        
        return "\n".join(formatted_commits)
    
    def _convert_markdown_to_plain_text(self, markdown_text: str) -> str:
        """マークダウン形式をプレーンテキストに変換"""
        # マークダウンの装飾文字を削除
        plain_text = markdown_text
        
        # ヘッダー記号を削除
        plain_text = re.sub(r'^#{1,6}\s*', '', plain_text, flags=re.MULTILINE)
        
        # リスト記号を削除
        plain_text = re.sub(r'^\s*[-*+]\s*', '', plain_text, flags=re.MULTILINE)
        
        # 番号付きリストの番号を削除
        plain_text = re.sub(r'^\s*\d+\.\s*', '', plain_text, flags=re.MULTILINE)
        
        # 強調記号を削除
        plain_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', plain_text)
        plain_text = re.sub(r'\*([^*]+)\*', r'\1', plain_text)
        plain_text = re.sub(r'__([^_]+)__', r'\1', plain_text)
        plain_text = re.sub(r'_([^_]+)_', r'\1', plain_text)
        
        # コードブロックの装飾を削除
        plain_text = re.sub(r'```[^`]*```', '', plain_text, flags=re.DOTALL)
        plain_text = re.sub(r'`([^`]+)`', r'\1', plain_text)
        
        # ハイフンライン（区切り線）を削除
        plain_text = re.sub(r'^[-–—]{3,}$', '---', plain_text, flags=re.MULTILINE)
        
        # 余分な空白行を整理
        plain_text = re.sub(r'\n{3,}', '\n\n', plain_text)
        
        return plain_text.strip()
    
    def generate_diary(self, 
                      since_date: Optional[str] = None,
                      until_date: Optional[str] = None,
                      days: Optional[int] = None,
                      author: Optional[str] = None,
                      max_count: Optional[int] = None) -> Tuple[str, int, int]:
        """
        プログラミング日誌を生成
        
        Args:
            since_date: 開始日 (YYYY-MM-DD形式)
            until_date: 終了日 (YYYY-MM-DD形式)
            days: 過去何日分を取得するか
            author: 作成者でフィルタ
            max_count: 最大取得件数
            
        Returns:
            Tuple[str, int, int]: (生成された日誌, 入力トークン数, 出力トークン数)
        """
        try:
            # Git履歴を取得
            commits = self.git_service.get_commit_history(
                since_date=since_date,
                until_date=until_date,
                author=author,
                max_count=max_count
            )
            
            if not commits:
                return "指定期間にコミット履歴が見つかりませんでした。", 0, 0
            
            # プロンプトテンプレートを読み込み
            prompt_template = self._load_prompt_template()
            
            # コミット履歴をフォーマット
            formatted_commits = self._format_commits_for_prompt(commits)
            
            # Claude APIに送信するプロンプトを作成
            full_prompt = f"{prompt_template}\n\n## Git コミット履歴\n\n{formatted_commits}"
            
            # Claude APIで日誌を生成
            diary_content, input_tokens, output_tokens = self.claude_client._generate_content(
                prompt=full_prompt,
                model_name=self.claude_client.default_model
            )
            
            # マークダウンをプレーンテキストに変換
            plain_diary = self._convert_markdown_to_plain_text(diary_content)
            
            return plain_diary, input_tokens, output_tokens
            
        except Exception as e:
            raise Exception(f"プログラミング日誌の生成に失敗しました: {e}")
    
    def save_diary_to_file(self, diary_content: str, filename: Optional[str] = None) -> str:
        """生成された日誌をファイルに保存"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"programming_diary_{timestamp}.txt"
        
        # 出力ディレクトリを設定
        output_dir = self.config.get('OUTPUT', 'output_directory', fallback='logs')
        output_path = Path(self.git_service.repository_path) / output_dir
        output_path.mkdir(exist_ok=True)
        
        file_path = output_path / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(diary_content)
            return str(file_path)
        except Exception as e:
            raise Exception(f"ファイルの保存に失敗しました: {e}")
    
    def generate_and_save_diary(self,
                               since_date: Optional[str] = None,
                               until_date: Optional[str] = None,
                               days: Optional[int] = None,
                               author: Optional[str] = None,
                               max_count: Optional[int] = None,
                               filename: Optional[str] = None) -> Dict[str, any]:
        """
        プログラミング日誌を生成してファイルに保存
        
        Returns:
            Dict: 生成結果の詳細情報
        """
        try:
            # 日誌を生成
            diary_content, input_tokens, output_tokens = self.generate_diary(
                since_date=since_date,
                until_date=until_date,
                days=days,
                author=author,
                max_count=max_count
            )
            
            # ファイルに保存
            saved_path = self.save_diary_to_file(diary_content, filename)
            
            return {
                'success': True,
                'diary_content': diary_content,
                'saved_path': saved_path,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'diary_content': None,
                'saved_path': None,
                'input_tokens': 0,
                'output_tokens': 0,
                'total_tokens': 0
            }


def main():
    """メイン実行関数（CLIでの実行用）"""
    import argparse
    
    parser = argparse.ArgumentParser(description="プログラミング日誌生成ツール")
    parser.add_argument('--since', type=str, help='開始日 (YYYY-MM-DD形式)')
    parser.add_argument('--until', type=str, help='終了日 (YYYY-MM-DD形式)')
    parser.add_argument('--days', type=int, help='過去何日分を取得するか', default=7)
    parser.add_argument('--author', type=str, help='作成者でフィルタ')
    parser.add_argument('--max-count', type=int, help='最大取得件数')
    parser.add_argument('--output', type=str, help='出力ファイル名')
    parser.add_argument('--no-save', action='store_true', help='ファイル保存を無効にする')
    
    args = parser.parse_args()
    
    try:
        generator = ProgrammingDiaryGenerator()
        
        print("プログラミング日誌を生成中...")
        
        if args.no_save:
            # 生成のみ（保存しない）
            diary_content, input_tokens, output_tokens = generator.generate_diary(
                since_date=args.since,
                until_date=args.until,
                days=args.days,
                author=args.author,
                max_count=args.max_count
            )
            
            print("\n" + "="*60)
            print("生成されたプログラミング日誌")
            print("="*60)
            print(diary_content)
            print(f"\n使用トークン数: 入力={input_tokens}, 出力={output_tokens}, 合計={input_tokens + output_tokens}")
            
        else:
            # 生成して保存
            result = generator.generate_and_save_diary(
                since_date=args.since,
                until_date=args.until,
                days=args.days,
                author=args.author,
                max_count=args.max_count,
                filename=args.output
            )
            
            if result['success']:
                print(f"✅ プログラミング日誌を生成しました: {result['saved_path']}")
                print(f"使用トークン数: 入力={result['input_tokens']}, 出力={result['output_tokens']}, 合計={result['total_tokens']}")
                print("\n" + "="*60)
                print("生成された内容のプレビュー")
                print("="*60)
                print(result['diary_content'][:500] + ("..." if len(result['diary_content']) > 500 else ""))
            else:
                print(f"❌ エラー: {result['error']}")
                sys.exit(1)
                
    except KeyboardInterrupt:
        print("\n処理が中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
