import unittest
from pathlib import Path

from factory.config import load_config


class TestConfig(unittest.TestCase):
    def test_load_config_defaults(self) -> None:
        cfg = load_config(Path("configs/factory.toml"))
        self.assertEqual(cfg.provider, "openai")
        self.assertTrue(cfg.default_model)
        self.assertIn("analyst", cfg.role_models)


if __name__ == "__main__":
    unittest.main()
