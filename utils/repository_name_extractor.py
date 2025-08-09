from pathlib import Path

from utils.config_manager import load_config


def get_repository_directory_name() -> str:
    try:
        config = load_config()
        repository_path = config.get('GIT', 'repository_path', fallback='')
        repo_dir_name = Path(repository_path).name
        
        return repo_dir_name
        
    except Exception as e:
        raise Exception(f"プロジェクト名の取得に失敗しました: {e}")

if __name__ == "__main__":
    try:
        directory_name = get_repository_directory_name()
        print(f"プロジェクト名: {directory_name}")
        
    except Exception as e:
        print(f"実行エラー: {e}")
