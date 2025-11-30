import subprocess

from utils.config_manager import load_config


def launch_form_page():
    config = load_config()
    chrome_path = config.get('Chrome', 'chrome_path')

    form_url = config.get('URL', 'form_url').strip('"')
    subprocess.Popen([chrome_path, form_url])


if __name__ == "__main__":
    launch_form_page()