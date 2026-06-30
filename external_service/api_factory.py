from enum import Enum
from typing import Union

from external_service.base_api import BaseAPIClient
from external_service.gemini_api import GeminiAPIClient
from utils.exceptions import APIError


class APIProvider(Enum):
    GEMINI = "gemini"


class APIFactory:
    @staticmethod
    def create_client(provider: Union[APIProvider, str]) -> BaseAPIClient:
        if isinstance(provider, str):
            try:
                provider = APIProvider(provider.lower())
            except ValueError:
                raise APIError(f"未対応のAPIプロバイダー: {provider}")

        client_mapping = {
            APIProvider.GEMINI: GeminiAPIClient,
        }

        if provider in client_mapping:
            return client_mapping[provider]()
        else:
            raise APIError(f"未対応のAPIプロバイダー: {provider}")
