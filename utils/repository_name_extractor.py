from pathlib import Path

from utils.config_manager import load_config


def get_repository_directory_name() -> str:
    try:
        config = load_config()
        repository_path = config.get('GIT', 'repository_path', fallback='')
        repo_dir_name = Path(repository_path).name
        
        return repo_dir_name
        
    except Exception as e:
        raise Exception(f"プロジェクト名取得に失敗しました: {e}")
