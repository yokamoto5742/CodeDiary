import tkinter as tk
from datetime import datetime, timezone, timedelta
from tkinter import ttk

from tkcalendar import DateEntry


class DateSelectionWidget(ttk.LabelFrame):
    """日付選択ウィジェット"""
    
    def __init__(self, parent, config, **kwargs):
        super().__init__(parent, text="対象期間", padding="5", **kwargs)
        self.config = config
        self.jst = timezone(timedelta(hours=9))
        
        self._setup_ui()
        
    def _setup_ui(self):
        """UIコンポーネントを設定"""
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, weight=1)
        
        # 開始日ラベル
        ttk.Label(self, text="開始日").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )
        
        # 開始日選択
        self.start_date_entry = DateEntry(
            self,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy/mm/dd',
            year=datetime.now(self.jst).year,
            month=datetime.now(self.jst).month,
            day=datetime.now(self.jst).day,
            selectbackground='gray80',
            selectforeground='black',
            normalbackground='white',
            normalforeground='black',
            weekendbackground='lightblue',
            weekendforeground='black',
            othermonthbackground='gray90',
            othermonthforeground='gray50',
            othermonthwebackground='gray80',
            othermonthweforeground='gray70',
            selectmode='day',
            cursor='hand1'
        )
        self.start_date_entry.grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10)
        )
        
        # 終了日ラベル
        ttk.Label(self, text="終了日").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 5)
        )
        
        # 終了日選択
        self.end_date_entry = DateEntry(
            self,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy/mm/dd',
            year=datetime.now(self.jst).year,
            month=datetime.now(self.jst).month,
            day=datetime.now(self.jst).day,
            selectbackground='gray80',
            selectforeground='black',
            normalbackground='white',
            normalforeground='black',
            weekendbackground='lightblue',
            weekendforeground='black',
            othermonthbackground='gray90',
            othermonthforeground='gray50',
            othermonthwebackground='gray80',
            othermonthweforeground='gray70',
            selectmode='day',
            cursor='hand1'
        )
        self.end_date_entry.grid(row=0, column=3, sticky=(tk.W, tk.E))
        
    def get_start_date(self):
        """開始日を取得"""
        return self.start_date_entry.get_date()
        
    def get_end_date(self):
        """終了日を取得"""
        return self.end_date_entry.get_date()
        
    def validate_dates(self):
        """日付の妥当性を検証"""
        try:
            start_date = self.get_start_date()
            end_date = self.get_end_date()
            
            if start_date > end_date:
                return False, "終了日より前の日付を選択してください。"
            
            return True, ""
        except Exception as e:
            return False, f"日付の取得中にエラーが発生しました: {str(e)}"
