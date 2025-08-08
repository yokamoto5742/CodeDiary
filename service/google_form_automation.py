from datetime import datetime, timedelta, timezone

import pyperclip
from playwright.sync_api import sync_playwright, expect

from utils.config_manager import load_config


def google_form_automation():
    config = load_config()
    form_url = config.get('URL', 'form_url', fallback=None)

    jst = timezone(timedelta(hours=9))
    today_date_str = datetime.now(jst).strftime("%Y-%m-%d")

    try:
        clipboard_text = pyperclip.paste()
        # Noneチェックを先に実行
        if clipboard_text is None or not clipboard_text.strip():
            print("警告: クリップボードが空です")
            return
    except Exception as e:
        print(f"エラー: クリップボードにアクセスできませんでした: {e}")
        return

    print(f"作成日: {today_date_str}")
    print(f"作業内容: {clipboard_text[:50]}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome"
        )
        page = browser.new_page()

        try:
            page.goto(form_url)
            date_input = page.locator('input[type="date"]')
            expect(date_input).to_be_visible(timeout=10000)
            date_input.fill(today_date_str)

            content_selectors = [
                'textarea[aria-label="作業内容"]',
                'textarea[aria-label*="回答を入力"]',
                'textarea'
            ]

            content_filled = False
            for selector in content_selectors:
                try:
                    content_textarea = page.locator(selector).first
                    if content_textarea.is_visible():
                        expect(content_textarea).to_be_visible(timeout=5000)
                        content_textarea.fill(clipboard_text)
                        content_filled = True
                        break
                except Exception:
                    continue

            if not content_filled:
                print("警告: 作業内容フィールドが見つかりませんでした。")

            print("=== 自動入力が完了しました ===")
            page.wait_for_event('close')

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            page.wait_for_event('close')


if __name__ == "__main__":
    google_form_automation()