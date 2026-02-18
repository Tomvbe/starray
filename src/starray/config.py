from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(slots=True)
class AppConfig:
    provider: str
    default_model: str
    role_models: dict[str, str]
    data_dir: Path


class ConfigError(RuntimeError):
    """Raised when the app configuration is missing or invalid."""


def load_config(config_path: Path) -> AppConfig:
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    try:
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML in config file: {config_path}") from exc

    provider_cfg = raw.get("provider", {})
    storage_cfg = raw.get("storage", {})

    provider = provider_cfg.get("name", "openai")
    default_model = provider_cfg.get("default_model", "gpt-4.1")
    role_models = dict(provider_cfg.get("role_models", {}))

    data_dir_raw = storage_cfg.get("data_dir", ".starray")
    data_dir = Path(data_dir_raw)

    return AppConfig(
        provider=provider,
        default_model=default_model,
        role_models=role_models,
        data_dir=data_dir,
    )
