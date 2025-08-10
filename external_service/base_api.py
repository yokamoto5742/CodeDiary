from abc import ABC, abstractmethod
from typing import Tuple


class BaseAPIClient(ABC):
    def __init__(self, api_key: str, default_model: str):
        self.api_key = api_key
        self.default_model = default_model

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def _generate_content(self, prompt: str, model_name: str) -> Tuple[str, int, int]:
        pass