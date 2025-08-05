from pathlib import Path

from playwright.sync_api import sync_playwright


def launch_chrome_with_login_state():
    chrome_user_data = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(chrome_user_data),
            headless=False,
            channel="chrome"
        )

        page = context.new_page()

        print("Enterキーを押すとChromeを終了します...")
        input()

        # 終了
        context.close()


if __name__ == "__main__":
    launch_chrome_with_login_state()
