import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import pyperclip
from playwright.sync_api import sync_playwright, expect

from utils.config_manager import load_config


class GoogleFormAutomation:
    """Playwrightを使用してGoogleFormに自動的に日誌を入力"""
    def __init__(self):
        self.config = load_config()
        self.jst = timezone(timedelta(hours=9))
        self.chrome_path = self._get_chrome_path()
        self.content: Optional[str] = None

    def _get_chrome_path(self) -> str:
        """設定ファイルからChrome実行ファイルのパスを取得"""
        chrome_path = self.config.get('Chrome', 'chrome_path', fallback=None)
        if chrome_path is None:
            raise Exception("設定ファイルにchrome_pathが設定されていません")
        return chrome_path

    def _check_chrome_path(self) -> bool:
        """Chrome実行ファイルが存在することを確認"""
        if not os.path.exists(self.chrome_path):
            raise Exception(f"Chrome実行ファイルが見つかりません: {self.chrome_path}")
        return True

    def _get_form_url(self) -> str:
        """設定ファイルからGoogleFormのURLを取得"""
        form_url = self.config.get('URL', 'form_url', fallback=None)
        if form_url is None:
            raise Exception("設定ファイルにform_urlが設定されていません")
        return form_url

    def _get_clipboard_content(self) -> str:
        """クリップボード内容を取得"""
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text is None or not clipboard_text.strip():
                raise Exception("クリップボードが空です")
            return clipboard_text
        except Exception as e:
            raise Exception(f"クリップボードにアクセスできませんでした: {e}")

    def _get_today_date_string(self) -> str:
        """現在の日時（JST）を日付文字列形式で取得"""
        return datetime.now(self.jst).strftime("%Y-%m-%d")

    def run_automation(self, content: Optional[str] = None):
        """GoogleFormに日付と日誌内容を自動入力"""
        try:
            self._check_chrome_path()
            form_url = self._get_form_url()

            if content:
                clipboard_content = content
            else:
                clipboard_content = self._get_clipboard_content()

            today_date = self._get_today_date_string()

            print(f"作成日: {today_date}")
            print(f"作業内容: {clipboard_content[:50]}...")

            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False,
                    executable_path=self.chrome_path,
                    args=[
                        '--start-maximized',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )

                context = browser.new_context()
                page = context.new_page()

                try:
                    page.goto(form_url)
                    date_input = page.locator('input[type="date"]')
                    expect(date_input).to_be_visible(timeout=10000)
                    date_input.fill(today_date)

                    content_textarea = page.get_by_label("作業内容")
                    expect(content_textarea).to_be_visible(timeout=5000)
                    content_textarea.fill(clipboard_content)
                    print("作業内容を入力し自動入力が完了しました")

                    page.wait_for_event('close', timeout=0)

                except Exception as e:
                    print(f"フォーム自動入力中にエラーが発生しました: {e}")

                finally:
                    context.close()
                    browser.close()

        except Exception as e:
            print(f"エラー: {e}")
            raise


if __name__ == "__main__":
    automation = GoogleFormAutomation()
    automation.run_automation()
