# 必要なライブラリをインポートします
from playwright.sync_api import sync_playwright, Page, expect
import pyperclip
from datetime import datetime
import time

# GoogleフォームのURL
FORM_URL = "https://forms.gle/cEnjC4A7rFdMs6dD6"


def main():
    """
    メインの処理を実行する関数
    """
    # --- 1. 入力するデータを準備 ---
    # 今日の日付をYYYY-MM-DD形式で取得
    today_date_str = datetime.now().strftime("%Y-%m-%d")

    # クリップボードからテキストを取得
    try:
        clipboard_text = pyperclip.paste()
        if not clipboard_text.strip():
            print("エラー: クリップボードにテキストがありません。作業内容をコピーしてから実行してください。")
            return
    except pyperclip.PyperclipException as e:
        print(f"エラー: クリップボードにアクセスできませんでした。: {e}")
        print("ヒント: 'xclip' または 'xsel' がLinuxに必要な場合があります。 (sudo apt-get install xclip)")
        return

    print("--- 自動入力を開始します ---")
    print(f"作成日: {today_date_str}")
    print(f"作業内容: {clipboard_text[:50]}...")  # 内容を一部表示

    # --- 2. Playwrightでブラウザを操作 ---
    with sync_playwright() as p:
        # Chromiumブラウザを起動 (headless=Falseでブラウザの動きが見える)
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        try:
            # --- 3. フォームページに移動し、入力 ---
            print(f"Googleフォームを開いています: {FORM_URL}")
            page.goto(FORM_URL, timeout=60000)  # タイムアウトを60秒に設定

            # 「作成日」の入力欄が表示されるまで待機
            date_input = page.locator('input[type="date"]')
            expect(date_input).to_be_visible()

            # 日付を入力
            date_input.fill(today_date_str)
            print("日付を入力しました。")

            # 「作業内容」の入力欄が表示されるまで待機
            content_textarea = page.locator('textarea[aria-label="作業内容"]')
            expect(content_textarea).to_be_visible()

            # クリップボードの内容を入力
            content_textarea.fill(clipboard_text)
            print("作業内容を貼り付けました。")

            # --- 4. 送信 (コメントアウト) ---
            # 自動で送信したい場合は、以下の行のコメントを解除してください
            # submit_button = page.locator('div[role="button"]:has-text("送信")')
            # submit_button.click()
            # print("フォームを送信しました。")

            print("--- 自動入力が完了しました ---")
            print("ブラウザを確認してください。15秒後に自動で閉じます。")
            time.sleep(15)  # ユーザーが確認する時間

        except Exception as e:
            print(f"エラーが発生しました: {e}")

        finally:
            # ブラウザを閉じる
            browser.close()
            print("ブラウザを閉じました。")


if __name__ == "__main__":
    # --- 実行前の準備 ---
    # ターミナルで以下のコマンドを実行して、必要なライブラリをインストールしてください
    # pip install playwright pyperclip
    #
    # Playwrightのブラウザをインストールします (初回のみ)
    # playwright install

    main()
