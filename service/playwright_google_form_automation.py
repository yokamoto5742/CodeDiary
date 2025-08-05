from datetime import datetime, timedelta, timezone

import pyperclip
from playwright.sync_api import sync_playwright, expect


def main():
    form_url = "https://forms.gle/cEnjC4A7rFdMs6dD6"
    jst = timezone(timedelta(hours=9))
    today_date_str = datetime.now(jst).strftime("%Y-%m-%d")

    try:
        clipboard_text = pyperclip.paste()
        if not clipboard_text.strip():
            print("エラー: クリップボードにテキストがありません。作業内容をコピーしてから実行してください。")
            return
    except Exception as e:
        print(f"エラー: クリップボードにアクセスできませんでした: {e}")
        return

    print("=== Googleフォーム自動入力を開始します ===")
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
            print("作成日を入力しています...")

            date_input = page.locator('input[type="date"]')
            expect(date_input).to_be_visible(timeout=10000)

            date_input.fill(today_date_str)
            print(f"作成日 ({today_date_str}) を入力しました。")
            print("作業内容を入力しています...")

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
                        print(f"作業内容を入力しました（セレクタ: {selector}）。")
                        content_filled = True
                        break
                except Exception:
                    continue

            if not content_filled:
                print("警告: 作業内容フィールドが見つかりませんでした。手動で入力してください。")

            print("=== 自動入力が完了しました ===")
            print("ブラウザを閉じるとプログラムが終了します...")
            page.wait_for_event('close')

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            print("ブラウザは開いたままにします。手動で操作してください。")
            print("ブラウザを閉じるとプログラムが終了します...")
            page.wait_for_event('close')

if __name__ == "__main__":
    main()
