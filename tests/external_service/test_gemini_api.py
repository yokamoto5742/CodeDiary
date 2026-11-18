from unittest.mock import MagicMock

from external_service.gemini_api import GeminiAPIClient


def _create_client(thinking_level: str | None) -> tuple[GeminiAPIClient, MagicMock]:
    client = GeminiAPIClient()
    client.thinking_level = thinking_level
    mock_genai_client = MagicMock()
    mock_genai_client.interactions.create.return_value = MagicMock(output_text="日誌")
    client.client = mock_genai_client
    return client, mock_genai_client


def test_generate_content_with_thinking_level() -> None:
    client, mock_genai_client = _create_client("low")

    client.generate_content("プロンプト", "gemini-test")

    mock_genai_client.interactions.create.assert_called_once_with(
        model="gemini-test",
        input="プロンプト",
        generation_config={"thinking_level": "low"},
    )


def test_generate_content_without_thinking_level() -> None:
    client, mock_genai_client = _create_client(None)

    client.generate_content("プロンプト", "gemini-test")

    mock_genai_client.interactions.create.assert_called_once_with(
        model="gemini-test",
        input="プロンプト",
        generation_config=None,
    )
