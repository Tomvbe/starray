import unittest
from pathlib import Path

from src.starray.analyst import AnalystRuntime
from src.starray.config import AppConfig


class TestAnalystRuntime(unittest.TestCase):
    def test_respond_uses_local_fallback_when_remote_provider_unavailable(self) -> None:
        cfg = AppConfig(
            provider="openai",
            provider_fallbacks=[],
            default_model="gpt-4.1",
            role_models={"analyst": "gpt-4.1"},
            role_fallback_models={"analyst": ["gpt-4.1-mini"]},
            temperature=0.2,
            request_timeout_seconds=30.0,
            data_dir=Path(".starray"),
        )
        runtime = AnalystRuntime(cfg)

        response = runtime.respond("draft a plan")

        self.assertTrue(response.content)
        self.assertEqual(response.provider, "local")
        self.assertTrue(response.fallback_used)

    def test_provider_summary_lists_route_order(self) -> None:
        cfg = AppConfig(
            provider="openai",
            provider_fallbacks=["anthropic", "gemini"],
            default_model="gpt-4.1",
            role_models={"analyst": "gpt-4.1"},
            role_fallback_models={"analyst": ["gpt-4.1-mini"]},
            temperature=0.2,
            request_timeout_seconds=30.0,
            data_dir=Path(".starray"),
        )
        runtime = AnalystRuntime(cfg)

        summary = runtime.provider_summary()

        self.assertIn("openai -> anthropic -> gemini -> local", summary)
        self.assertIn("gpt-4.1 -> gpt-4.1-mini", summary)


if __name__ == "__main__":
    unittest.main()
