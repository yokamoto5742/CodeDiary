from typing import Tuple

import google.generativeai as genai

from external_service.base_api import BaseAPIClient
from utils.config_manager import GEMINI_API_KEY, GEMINI_MODEL
from utils.constants import MESSAGES
from utils.exceptions import APIError


class GeminiAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__(GEMINI_API_KEY, GEMINI_MODEL)
        self.client: object | None = None

    def initialize(self) -> bool:
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)
                return True
            else:
                raise APIError(MESSAGES["GEMINI_API_CREDENTIALS_MISSING"])
        except Exception as e:
            raise APIError(f"Gemini API初期化エラー: {str(e)}")

    def generate_content(self, prompt: str, model_name: str) -> Tuple[str, int, int]:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)

            if hasattr(response, 'text'):
                summary_text = response.text
            else:
                summary_text = str(response)

            input_tokens = 0
            output_tokens = 0

            if hasattr(response, 'usage_metadata'):
                input_tokens = response.usage_metadata.prompt_token_count or 0
                output_tokens = response.usage_metadata.candidates_token_count or 0

            return summary_text, input_tokens, output_tokens

        except Exception as e:
            raise APIError(f"Gemini API呼び出しエラー: {str(e)}")
