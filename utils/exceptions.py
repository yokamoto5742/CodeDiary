class AppError(Exception):
    """アプリケーションの基本例外"""
    pass


class APIError(AppError):
    """外部API呼び出しで発生するエラー"""
    pass
