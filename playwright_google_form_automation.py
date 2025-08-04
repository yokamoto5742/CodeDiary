import datetime
import time

import pyperclip
from playwright.sync_api import sync_playwright


class GoogleFormAutomation:
    """Googleフォームの自動入力を行うクラス"""
    
    def __init__(self, form_url: str):
        self.form_url = form_url
        self.playwright = None
        self.browser = None
        self.page = None
    
    def setup_browser(self):
        """ブラウザのセットアップ"""
        try:
            self.playwright = sync_playwright().start()
            # Chromeブラウザを起動（headless=Falseで画面表示）
            self.browser = self.playwright.chromium.launch(
                headless=False,
                channel="chrome"  # インストール済みのChromeを使用
            )
            self.page = self.browser.new_page()
            print("ブラウザのセットアップが完了しました。")
        except Exception as e:
            print(f"ブラウザのセットアップに失敗しました: {e}")
            raise
    
    def open_form(self):
        """Googleフォームを開く"""
        try:
            print("Googleフォームを開いています...")
            self.page.goto(self.form_url)
            self.page.wait_for_load_state("networkidle")
            print("Googleフォームを開きました。")
        except Exception as e:
            print(f"フォームの読み込みに失敗しました: {e}")
            raise
    
    def fill_creation_date(self):
        """作成日に本日の日付を入力"""
        try:
            # 本日の日付を取得（YYYY/MM/DD形式）
            today = datetime.date.today()
            date_string = today.strftime("%Y/%m/%d")

            print(f"作成日に {date_string} を入力しています...")

            # 日付入力フィールドを探す（複数のセレクタを試行）
            date_selectors = [
                'input[type="date"]',
                'input[aria-label*="日付"]',
                'input[aria-label*="作成日"]',
                'input[placeholder*="年/月/日"]',
                '.quantumWizTextinputPaperinputInput[type="date"]'
            ]

            date_filled = False
            for selector in date_selectors:
                try:
                    if self.page.query_selector(selector):
                        self.page.fill(selector, date_string)
                        date_filled = True
                        print(f"日付フィールド ({selector}) に入力しました。")
                        break
                except Exception:
                    continue

            if not date_filled:
                print("日付フィールドが見つかりませんでした。手動で入力してください。")

        except Exception as e:
            print(f"日付の入力に失敗しました: {e}")
    
    def fill_work_content(self):
        """作業内容にクリップボードの内容を貼り付け"""
        try:
            # クリップボードの内容を取得
            clipboard_content = pyperclip.paste()
            
            if not clipboard_content:
                print("クリップボードが空です。")
                return
            
            print("作業内容にクリップボードの内容を貼り付けています...")
            
            # テキストエリアを探す（複数のセレクタを試行）
            text_selectors = [
                'textarea[aria-label*="作業内容"]',
                'textarea[aria-label*="回答を入力"]',
                'textarea',
                '.quantumWizTextinputPapertextareaInput',
                'div[contenteditable="true"]'
            ]
            
            content_filled = False
            for selector in text_selectors:
                try:
                    elements = self.page.query_selector_all(selector)
                    if elements:
                        # 最初のテキストエリアに入力（通常は作業内容フィールド）
                        elements[0].fill(clipboard_content)
                        content_filled = True
                        print(f"作業内容フィールド ({selector}) に貼り付けました。")
                        break
                except Exception:
                    continue
            
            if not content_filled:
                print("作業内容フィールドが見つかりませんでした。手動で入力してください。")
                
        except Exception as e:
            print(f"作業内容の入力に失敗しました: {e}")
    
    def close_browser(self):
        """ブラウザを閉じる"""
        try:
            if self.browser:
                print("ブラウザを閉じています...")
                time.sleep(2)  # 少し待機してからブラウザを閉じる
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            print("ブラウザを閉じました。")
        except Exception as e:
            print(f"ブラウザの終了中にエラーが発生しました: {e}")
    
    def run_automation(self):
        """自動化の実行"""
        try:
            print("=== Googleフォーム自動入力を開始します ===")
            
            # ブラウザのセットアップ
            self.setup_browser()
            
            # フォームを開く
            self.open_form()
            
            # 少し待機（フォームの読み込み完了を待つ）
            time.sleep(3)
            
            # 作成日を入力
            self.fill_creation_date()
            
            # 作業内容を入力
            self.fill_work_content()
            
            print("=== 自動入力が完了しました ===")
            print("内容を確認して、送信ボタンを手動でクリックしてください。")
            
            # ユーザーが確認できるように少し待機
            input("Enterキーを押すとブラウザが閉じます...")
            
        except Exception as e:
            print(f"自動化の実行中にエラーが発生しました: {e}")
        finally:
            self.close_browser()


def main():
    """メイン関数"""
    # GoogleフォームのURL
    form_url = "https://forms.gle/cEnjC4A7rFdMs6dD6"
    
    # 自動化を実行
    automation = GoogleFormAutomation(form_url)
    automation.run_automation()


if __name__ == "__main__":
    main()
