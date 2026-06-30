import configparser
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def get_config_path():
    """設定ファイルのパスを取得。PyInstallerビルド時は_MEIPASSを使用"""
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    else:
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, 'config.ini')


CONFIG_PATH = get_config_path()

_cached_config = None


def load_environment_variables():
    """プロジェクトルートの.envファイルから環境変数を読み込む"""
    current_dir = Path(__file__).parent.parent
    env_path = current_dir / '.env'

    if env_path.exists():
        load_dotenv(env_path)
        return True
    return False


load_environment_variables()


def load_config(force_reload: bool = False) -> configparser.ConfigParser:
    """設定ファイルを読み込む。キャッシュを使用して多重読み込みを防止"""
    global _cached_config
    if _cached_config is None or force_reload:
        config = configparser.ConfigParser()
        try:
            with open(CONFIG_PATH, encoding='utf-8') as f:
                config.read_file(f)
        except FileNotFoundError:
            print(f"設定ファイルが見つかりません: {CONFIG_PATH}")
            raise
        except configparser.Error as e:
            print(f"設定ファイルの解析中にエラーが発生しました: {e}")
            raise
        _cached_config = config
    return _cached_config


def save_config(config: configparser.ConfigParser):
    """設定ファイルに設定を保存し、キャッシュを更新"""
    global _cached_config
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        _cached_config = config
    except IOError as e:
        print(f"設定ファイルの保存中にエラーが発生しました: {e}")
        raise


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
GEMINI_THINKING_BUDGET = os.environ.get("GEMINI_THINKING_BUDGET")
