import sys
import tkinter as tk

from app.main_window import CodeDiaryMainWindow


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
