import time

import pyperclip
from playwright.sync_api import Playwright, TimeoutError as PlaywrightTimeoutError, sync_playwright

def copy_google_doc_content(playwright: Playwright):
    document_url = "https://docs.google.com/document/d/10whwZzYqdhE0hJadehajaJGypAdr0ulKG0Pzm7FPuC0/edit?usp=sharing"

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    browser = playwright.chromium.launch(
        executable_path=chrome_path,
        headless=False
    )
    context = browser.new_context(
        locale="ja-JP",
    )
    page = context.new_page()

    try:
        print(f"Googleドキュメントにアクセスしています: {document_url}")
        page.goto(document_url, wait_until="load", timeout=60000)

        print("ドキュメントの読み込みを待っています...")
        editor_selector = 'div.kix-page-paginated'
        page.wait_for_selector(editor_selector, timeout=60000)
        print("ドキュメントの読み込みが完了しました。")

        page.locator(editor_selector).first.click()
        time.sleep(1)

        print("すべてのコンテンツを選択しています (Ctrl+A)...")
        page.keyboard.press("Control+A")
        time.sleep(0.5)  # 選択が反映されるのを待機

        print("クリップボードにコピーしています (Ctrl+C)...")
        # クリップボードをクリアしてからコピー
        pyperclip.copy("")
        page.keyboard.press("Control+C")
        time.sleep(0.5)  # コピーが完了するのを待機

        selected_text = pyperclip.paste()

        if selected_text and selected_text.strip():
            print("\n--------------------")
            print("コピーしました")
            print("--------------------")
        else:
            print("エラー: テキストの取得に失敗しました。ドキュメントが空か、選択がうまくいかなかった可能性があります。")

    except PlaywrightTimeoutError:
        print(f"エラー: タイムアウトしました。ページの読み込みに失敗したか、指定された要素 '{editor_selector}' が見つかりませんでした。")
        print("ネットワーク接続を確認するか、セレクタが正しいか確認してください。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    finally:
        print("ブラウザを閉じています。")
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        copy_google_doc_content(playwright)