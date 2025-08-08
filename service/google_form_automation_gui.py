import os
import subprocess
from datetime import datetime, timedelta, timezone

import pyperclip
from playwright.sync_api import sync_playwright, expect

from utils.config_manager import load_config


class ChromeGoogleFormAutomation:
    """ローカルChromeを使用したGoogleフォーム自動入力クラス"""

    def __init__(self):
        self.config = load_config()
        self.jst = timezone(timedelta(hours=9))
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    def _get_form_url(self) -> str:
        """設定からフォームURLを取得"""
        form_url = self.config.get('URL', 'form_url', fallback=None)
        if not form_url:
            raise Exception("設定ファイルにform_urlが設定されていません")
        return form_url

    def _get_clipboard_content(self) -> str:
        """クリップボードの内容を取得"""
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text is None or not clipboard_text.strip():
                raise Exception("クリップボードが空です")
            return clipboard_text
        except Exception as e:
            raise Exception(f"クリップボードにアクセスできませんでした: {e}")

    def _check_chrome_path(self) -> bool:
        """Chromeの実行ファイルが存在するかチェック"""
        if not os.path.exists(self.chrome_path):
            raise Exception(f"Chrome実行ファイルが見つかりません: {self.chrome_path}")
        return True

    def _get_today_date_string(self) -> str:
        """本日の日付文字列を取得（YYYY-MM-DD形式）"""
        return datetime.now(self.jst).strftime("%Y-%m-%d")

    def run_automation(self):
        """自動入力処理を実行"""
        try:
            # 事前チェック
            self._check_chrome_path()
            form_url = self._get_form_url()
            clipboard_content = self._get_clipboard_content()
            today_date = self._get_today_date_string()

            print(f"Chrome実行パス: {self.chrome_path}")
            print(f"フォームURL: {form_url}")
            print(f"作成日: {today_date}")
            print(f"作業内容: {clipboard_content[:50]}...")

            with sync_playwright() as p:
                # 指定されたChromeパスでブラウザを起動
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
                    # フォームページを開く
                    print("フォームページを開いています...")
                    page.goto(form_url)

                    # 日付入力フィールドを探して入力
                    print("日付を入力しています...")
                    date_input = page.locator('input[type="date"]')
                    expect(date_input).to_be_visible(timeout=10000)
                    date_input.fill(today_date)

                    # 作業内容入力フィールドを探して入力
                    print("作業内容を入力しています...")
                    content_selectors = [
                        'textarea[aria-label="作業内容"]',
                        'textarea[aria-label*="回答を入力"]',
                        'textarea[aria-label*="作業"]',
                        'textarea'
                    ]

                    content_filled = False
                    for selector in content_selectors:
                        try:
                            content_textarea = page.locator(selector).first
                            if content_textarea.is_visible():
                                expect(content_textarea).to_be_visible(timeout=5000)
                                content_textarea.fill(clipboard_content)
                                content_filled = True
                                print(f"作業内容を入力しました (使用セレクタ: {selector})")
                                break
                        except Exception:
                            continue

                    if not content_filled:
                        print("警告: 作業内容フィールドが見つかりませんでした")
                        print("手動で作業内容を入力してください")

                    print("=" * 50)
                    print("自動入力が完了しました")
                    print("フォームページは開いたままです")
                    print("必要に応じて内容を確認し、送信してください")
                    print("=" * 50)

                    # ページを開いたまま維持（ユーザーが手動で閉じるまで待機）
                    print("フォームページを閉じるには、ブラウザを閉じてください...")
                    try:
                        # ページが閉じられるまで待機
                        page.wait_for_event('close', timeout=0)
                    except:
                        # タイムアウトまたはその他のエラーが発生した場合
                        pass

                except Exception as e:
                    print(f"フォーム自動入力中にエラーが発生しました: {e}")
                    print("ブラウザは開いたままです。手動で入力してください。")
                    try:
                        page.wait_for_event('close', timeout=0)
                    except:
                        pass

                finally:
                    # リソースをクリーンアップ
                    try:
                        context.close()
                        browser.close()
                    except:
                        pass

        except Exception as e:
            print(f"エラー: {e}")
            raise


def chrome_google_form_automation():
    """メイン実行関数"""
    try:
        automation = ChromeGoogleFormAutomation()
        automation.run_automation()
    except Exception as e:
        print(f"Google Form自動化でエラーが発生しました: {e}")


if __name__ == "__main__":
    chrome_google_form_automation()