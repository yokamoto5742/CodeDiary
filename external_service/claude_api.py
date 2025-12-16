from anthropic import Anthropic
from anthropic.types import TextBlock
from typing import Tuple, Optional

from external_service.base_api import BaseAPIClient
from utils.config_manager import CLAUDE_API_KEY, CLAUDE_MODEL
from utils.constants import MESSAGES
from utils.exceptions import APIError


class ClaudeAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__(CLAUDE_API_KEY, CLAUDE_MODEL)
        self.client: Optional[Anthropic] = None

    def initialize(self) -> bool:
        try:
            if self.api_key:
                self.client = Anthropic(api_key=self.api_key)
                return True
            else:
                raise APIError(MESSAGES["CLAUDE_API_CREDENTIALS_MISSING"])
        except Exception as e:
            raise APIError(f"Claude API初期化エラー: {str(e)}")

    def generate_content(self, prompt: str, model_name: str) -> Tuple[str, int, int]:
        if self.client is None:
            raise APIError("Claude APIクライアントが初期化されていません")

        try:
            response = self.client.messages.create(
                model=model_name,
                max_tokens=8000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
        except Exception as e:
            raise APIError(f"Claude API呼び出しエラー: {str(e)}")

        # レスポンスのstop_reasonを確認
        if response.stop_reason == "error":
            raise APIError(f"Claude APIがエラーを返しました: stop_reason={response.stop_reason}")

        if not response.content:
            raise APIError(
                f"Claude APIからの応答が空です (stop_reason={response.stop_reason})"
            )

        content_block = response.content[0]
        if isinstance(content_block, TextBlock) and content_block.text:
            summary_text = content_block.text
        else:
            raise APIError(
                f"Claude APIレスポンスにテキストがありません "
                f"(type={type(content_block).__name__}, stop_reason={response.stop_reason})"
            )

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        return summary_text, input_tokens, output_tokens
