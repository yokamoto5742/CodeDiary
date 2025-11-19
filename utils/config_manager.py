"""アプリケーション設定とAIプロバイダー認証情報を一元管理"""

import configparser
import os
import sys
from pathlib import Path
from typing import Dict, Optional

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


def get_ai_provider_config() -> Dict[str, str]:
    """設定ファイルからAIプロバイダー設定（メインとフォールバック）を取得"""
    config = load_config()

    provider = config.get('AI', 'provider', fallback='gemini')
    fallback_provider = config.get('AI', 'fallback_provider', fallback='openai')

    return {
        'provider': provider,
        'fallback_provider': fallback_provider
    }


def get_available_providers() -> Dict[str, bool]:
    """環境変数から利用可能なAIプロバイダーを判定"""
    providers = {
        'claude': bool(os.environ.get("CLAUDE_API_KEY")),
        'openai': bool(os.environ.get("OPENAI_API_KEY")),
        'gemini': bool(os.environ.get("GEMINI_API_KEY"))
    }
    return providers


def get_provider_credentials(provider: str) -> Optional[Dict[str, Optional[str]]]:
    """指定プロバイダーのAPI認証情報を環境変数から取得"""
    credentials_map = {
        'claude': {
            'api_key': os.environ.get("CLAUDE_API_KEY"),
            'model': os.environ.get("CLAUDE_MODEL")
        },
        'openai': {
            'api_key': os.environ.get("OPENAI_API_KEY"),
            'model': os.environ.get("OPENAI_MODEL")
        },
        'gemini': {
            'api_key': os.environ.get("GEMINI_API_KEY"),
            'model': os.environ.get("GEMINI_MODEL"),
            'thinking_budget': os.environ.get("GEMINI_THINKING_BUDGET")
        }
    }

    return credentials_map.get(provider)


def validate_provider_config(provider: str) -> bool:
    """指定プロバイダーの認証情報が設定されているか検証"""
    credentials = get_provider_credentials(provider)
    if not credentials or not credentials.get('api_key'):
        return False
    return True


def get_active_provider() -> str:
    """利用可能なプロバイダーを優先順位に従って選択。全て未設定時は例外発生"""
    config = get_ai_provider_config()
    available_providers = get_available_providers()

    main_provider = config['provider']
    if available_providers.get(main_provider, False):
        return main_provider

    fallback_provider = config['fallback_provider']
    if available_providers.get(fallback_provider, False):
        print(f"警告: '{main_provider}' が利用できないため、'{fallback_provider}' を使用します")
        return fallback_provider

    for provider, available in available_providers.items():
        if available:
            print(f"警告: 設定されたプロバイダーが利用できないため、'{provider}' を使用します")
            return provider

    raise Exception("利用可能なAIプロバイダーがありません。APIキーの設定を確認してください。")


CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
GEMINI_THINKING_BUDGET = os.environ.get("GEMINI_THINKING_BUDGET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL")
