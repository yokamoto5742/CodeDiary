from typing import Optional, Tuple

from google import genai

from utils.config_manager import GEMINI_API_KEY, GEMINI_MODEL
from utils.constants import MESSAGES
from utils.exceptions import APIError


class GeminiAPIClient:
    def __init__(self):
        self.api_key: Optional[str] = GEMINI_API_KEY
        self.default_model: Optional[str] = GEMINI_MODEL
        self.client: Optional[genai.Client] = None

    def initialize(self) -> bool:
        try:
            if self.api_key:
                self.client = genai.Client(api_key=self.api_key)
                return True
            else:
                raise APIError(MESSAGES["GEMINI_API_CREDENTIALS_MISSING"])
        except Exception as e:
            raise APIError(f"Gemini API初期化エラー: {str(e)}")

    def generate_content(self, prompt: str, model_name: str) -> Tuple[str, int, int]:
        try:
            if self.client is None:
                raise APIError(MESSAGES["GEMINI_API_CREDENTIALS_MISSING"])

            interaction = self.client.interactions.create(
                model=model_name,
                input=prompt,
            )

            summary_text = getattr(interaction, 'output_text', None) or str(interaction)

            input_tokens = 0
            output_tokens = 0

            usage = getattr(interaction, 'usage', None)
            if usage is not None:
                input_tokens = getattr(usage, 'total_input_tokens', 0) or 0
                output_tokens = getattr(usage, 'total_output_tokens', 0) or 0

            return summary_text, input_tokens, output_tokens

        except Exception as e:
            raise APIError(f"Gemini API呼び出しエラー: {str(e)}")
