from abc import ABC, abstractmethod
from typing import Optional, Tuple


class BaseAPIClient(ABC):
    def __init__(self, api_key: Optional[str], default_model: Optional[str]):
        self.api_key = api_key
        self.default_model = default_model

    @abstractmethod
    def initialize(self) -> bool:
        pass

    @abstractmethod
    def generate_content(self, prompt: str, model_name: str) -> Tuple[str, int, int]:
        pass