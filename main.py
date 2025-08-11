import sys
import tkinter as tk

from app.main_window import CodeDiaryMainWindow

import os
from dotenv import load_dotenv

load_dotenv()

print("=== API キー設定状況 ===")
print(f"OPENAI_API_KEY: {'設定済み' if os.environ.get('OPENAI_API_KEY') else '未設定'}")
print(f"GEMINI_API_KEY: {'設定済み' if os.environ.get('GEMINI_API_KEY') else '未設定'}")
print(f"CLAUDE_API_KEY: {'設定済み' if os.environ.get('CLAUDE_API_KEY') else '未設定'}")
print("========================")


def main():
    try:
        root = tk.Tk()
        app = CodeDiaryMainWindow(root)
        root.mainloop()
        
    except Exception as e:
        print(f"アプリケーション起動エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
