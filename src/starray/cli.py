from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from typing import Optional

from . import __version__
from .analyst import AnalystRuntime
from .config import AppConfig, ConfigError, load_config
from .logging_utils import build_session_logger
from .session import SessionState, SessionError, load_session


class Ui:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    RED = "\033[31m"
    BLUE = "\033[34m"

    def __init__(self) -> None:
        self.use_color = sys.stdout.isatty() and os.getenv("NO_COLOR") is None

    def c(self, text: str, *styles: str) -> str:
        if not self.use_color:
            return text
        return "".join(styles) + text + self.RESET


ui = Ui()
APP_NAME = "starray"
ENV_CONFIG = "STARRAY_CONFIG"
CONFIG_FILENAME = "starray.toml"


def _resolve_storage_paths(cfg: AppConfig) -> tuple[Path, Path]:
    data_dir = cfg.data_dir.expanduser()
    session_dir = data_dir / "sessions"
    log_dir = data_dir / "logs"
    return session_dir, log_dir


def _user_config_path() -> Path:
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    base = Path(xdg_config_home).expanduser() if xdg_config_home else Path.home() / ".config"
    return base / APP_NAME / CONFIG_FILENAME


def _user_state_path() -> Path:
    xdg_state_home = os.getenv("XDG_STATE_HOME")
    base = Path(xdg_state_home).expanduser() if xdg_state_home else Path.home() / ".local" / "state"
    return base / APP_NAME


def _project_config_path() -> Path:
    return Path("configs") / CONFIG_FILENAME


def _resolve_config_path(cli_config: Optional[str]) -> Path:
    if cli_config:
        return Path(cli_config).expanduser()
    env_config = os.getenv(ENV_CONFIG)
    if env_config:
        return Path(env_config).expanduser()
    user_config = _user_config_path()
    if user_config.exists():
        return user_config
    project_config = _project_config_path()
    if project_config.exists():
        return project_config
    return user_config


def _resolve_init_config_path(cli_config: Optional[str]) -> Path:
    if cli_config:
        return Path(cli_config).expanduser()
    env_config = os.getenv(ENV_CONFIG)
    if env_config:
        return Path(env_config).expanduser()
    return _user_config_path()


def _default_config_text() -> str:
    state_dir = _user_state_path().as_posix()
    return f"""[provider]
name = "openai"
fallbacks = ["anthropic", "gemini", "local"]
default_model = "gpt-4.1"
temperature = 0.2
request_timeout_seconds = 30

[provider.role_models]
analyst = "gpt-4.1"
planner = "gpt-4.1-mini"
architect = "gpt-4.1"
implementer = "gpt-4.1"
tester = "gpt-4.1-mini"
security = "gpt-4.1"

[provider.role_fallback_models]
analyst = ["gpt-4.1-mini"]

[storage]
data_dir = "{state_dir}"
"""


def _print_config_error(exc: ConfigError, config_path: Path) -> int:
    print(ui.c(str(exc), Ui.RED))
    if config_path == _user_config_path():
        print(ui.c("No user config found. Run: starray init", Ui.YELLOW))
    return 1


def cmd_status(config_path: Path) -> int:
    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        return _print_config_error(exc, config_path)

    print(ui.c("Starray status: ready", Ui.BOLD, Ui.GREEN))
    print(f"{ui.c('Config:', Ui.CYAN)} {config_path}")
    print(f"{ui.c('Provider:', Ui.CYAN)} {cfg.provider}")
    print(f"{ui.c('Provider fallbacks:', Ui.CYAN)} {', '.join(cfg.provider_fallbacks) or '(none)'}")
    print(f"{ui.c('Default model:', Ui.CYAN)} {cfg.default_model}")
    print(f"{ui.c('Data dir:', Ui.CYAN)} {cfg.data_dir}")
    return 0


def _handle_turn(
    user_text: str,
    analyst_runtime: AnalystRuntime,
    state: SessionState,
    sessions_dir: Path,
    logger,
) -> None:
    user_text = user_text.strip()
    if not user_text:
        return

    analyst_response = analyst_runtime.respond(user_text)
    state.add_turn("user", user_text)
    state.add_turn("analyst", analyst_response.content)
    logger.info("user=%s", user_text)
    logger.info(
        "analyst provider=%s model=%s fallback=%s",
        analyst_response.provider,
        analyst_response.model,
        analyst_response.fallback_used,
    )
    logger.info("analyst=%s", analyst_response.content)
    state.save(sessions_dir)
    provider_line = (
        f"{ui.c('│', Ui.MAGENTA)} "
        f"{ui.c('[provider]', Ui.DIM)} {analyst_response.provider}/{analyst_response.model}"
    )
    print(
        f"{ui.c('┌─ Analyst', Ui.BOLD, Ui.MAGENTA)}\n"
        f"{provider_line}\n"
        f"{ui.c('│', Ui.MAGENTA)} {analyst_response.content}\n"
        f"{ui.c('└────────', Ui.MAGENTA)}"
    )


def _print_intro(cfg: AppConfig, session_id: str) -> None:
    print(ui.c("╔═════════════════════════════════════════════════════╗", Ui.BLUE))
    print(ui.c("║                     StarRay CLI                     ║", Ui.BOLD, Ui.BLUE))
    print(ui.c("╚═════════════════════════════════════════════════════╝", Ui.BLUE))
    print(
        f"{ui.c('Analyst', Ui.BOLD, Ui.MAGENTA)} is active. Provider abstraction is enabled; specialist graph comes in Phase 2."
    )
    print(
        f"{ui.c('Provider:', Ui.CYAN)} {cfg.provider}   "
        f"{ui.c('Model:', Ui.CYAN)} {cfg.default_model}   "
        f"{ui.c('Session:', Ui.CYAN)} {session_id}"
    )
    print(
        ui.c(
            "Commands: /help, /provider, /session, /status, exit",
            Ui.DIM,
        )
    )


def cmd_provider(config_path: Path) -> int:
    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        return _print_config_error(exc, config_path)

    analyst_runtime = AnalystRuntime(cfg)
    print(ui.c("Provider routing", Ui.BOLD, Ui.GREEN))
    print(f"{ui.c('Config:', Ui.CYAN)} {config_path}")
    print(analyst_runtime.provider_summary())
    return 0


def cmd_chat(config_path: Path, message: Optional[str], session_id: Optional[str]) -> int:
    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        return _print_config_error(exc, config_path)

    sessions_dir, logs_dir = _resolve_storage_paths(cfg)
    analyst_runtime = AnalystRuntime(cfg)

    try:
        if session_id:
            state = load_session(sessions_dir, session_id)
            print(ui.c(f"Resumed session: {state.session_id}", Ui.YELLOW))
        else:
            state = SessionState.new()
    except SessionError as exc:
        print(ui.c(str(exc), Ui.RED))
        return 1

    logger = build_session_logger(logs_dir, state.session_id)

    _print_intro(cfg, state.session_id)

    if message is not None:
        _handle_turn(message, analyst_runtime, state, sessions_dir, logger)
        print(ui.c(f"Session saved: {state.session_id}", Ui.GREEN))
        return 0

    print(ui.c("Type 'exit' to quit.", Ui.DIM))
    try:
        while True:
            print(ui.c("┌─ Input", Ui.BOLD, Ui.CYAN))
            user_text = input(ui.c("│ ", Ui.CYAN))
            if user_text.strip().lower() in {"exit", "quit"}:
                state.save(sessions_dir)
                break
            if user_text.strip() == "/help":
                print(ui.c("Commands: /help, /provider, /session, /status, exit", Ui.DIM))
                continue
            if user_text.strip() == "/provider":
                print(analyst_runtime.provider_summary())
                continue
            if user_text.strip() == "/session":
                print(ui.c(f"Current session: {state.session_id}", Ui.YELLOW))
                continue
            if user_text.strip() == "/status":
                print(
                    f"{ui.c('Provider:', Ui.CYAN)} {cfg.provider}   "
                    f"{ui.c('Model:', Ui.CYAN)} {cfg.default_model}"
                )
                continue
            _handle_turn(user_text, analyst_runtime, state, sessions_dir, logger)
    except (KeyboardInterrupt, EOFError):
        state.save(sessions_dir)
        print()

    print(ui.c(f"Session saved: {state.session_id}", Ui.GREEN))
    print(ui.c(f"Resume with: starray --session-id {state.session_id}", Ui.YELLOW))
    return 0


def cmd_init(config_path: Path, force: bool) -> int:
    config_path = config_path.expanduser()
    if config_path.exists() and not force:
        print(ui.c(f"Config already exists: {config_path}", Ui.YELLOW))
        print(ui.c("Use --force to overwrite.", Ui.DIM))
        return 1

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(_default_config_text(), encoding="utf-8")
    print(ui.c(f"Created config: {config_path}", Ui.GREEN))
    print(ui.c("Start chat with: starray", Ui.DIM))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="starray", description="Starray CLI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--config", "-c")
    parser.add_argument("--session-id")
    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser("status", help="Show baseline app status")
    status_parser.add_argument("--config", "-c", dest="sub_config")

    provider_parser = subparsers.add_parser("provider", help="Show provider/model routing")
    provider_parser.add_argument("--config", "-c", dest="sub_config")

    chat_parser = subparsers.add_parser("chat", help="Run baseline Analyst chat loop")
    chat_parser.add_argument("--config", "-c", dest="sub_config")
    chat_parser.add_argument("--message", "-m")
    chat_parser.add_argument("--session-id", dest="sub_session_id")

    init_parser = subparsers.add_parser("init", help="Create a user config file")
    init_parser.add_argument("--config", "-c", dest="sub_config")
    init_parser.add_argument("--force", action="store_true")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_value = getattr(args, "sub_config", None) or args.config
    if args.command == "init":
        config_path = _resolve_init_config_path(config_value)
    else:
        config_path = _resolve_config_path(config_value)

    if args.command == "status":
        return cmd_status(config_path)
    if args.command == "provider":
        return cmd_provider(config_path)
    if args.command == "chat":
        session_id = getattr(args, "sub_session_id", None) or args.session_id
        return cmd_chat(config_path, args.message, session_id)
    if args.command == "init":
        return cmd_init(config_path, args.force)
    if args.command is None:
        session_id = getattr(args, "session_id", None)
        return cmd_chat(config_path, None, session_id)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
