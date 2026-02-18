from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from typing import Optional

from . import __version__
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


def _resolve_storage_paths(cfg: AppConfig) -> tuple[Path, Path]:
    session_dir = cfg.data_dir / "sessions"
    log_dir = cfg.data_dir / "logs"
    return session_dir, log_dir


def cmd_status(config_path: Path) -> int:
    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        print(ui.c(str(exc), Ui.RED))
        return 1

    print(ui.c("Starray status: ready", Ui.BOLD, Ui.GREEN))
    print(f"{ui.c('Provider:', Ui.CYAN)} {cfg.provider}")
    print(f"{ui.c('Default model:', Ui.CYAN)} {cfg.default_model}")
    print(f"{ui.c('Data dir:', Ui.CYAN)} {cfg.data_dir}")
    return 0


def _handle_turn(
    user_text: str,
    state: SessionState,
    sessions_dir: Path,
    logger,
) -> None:
    user_text = user_text.strip()
    if not user_text:
        return

    analyst_reply = "Analyst: received. Phase 0 scaffold is active; orchestration comes next."
    state.add_turn("user", user_text)
    state.add_turn("analyst", analyst_reply)
    logger.info("user=%s", user_text)
    logger.info("analyst=%s", analyst_reply)
    state.save(sessions_dir)
    print(
        f"{ui.c('┌─ Analyst', Ui.BOLD, Ui.MAGENTA)}\n"
        f"{ui.c('│', Ui.MAGENTA)} {analyst_reply}\n"
        f"{ui.c('└────────', Ui.MAGENTA)}"
    )


def _print_intro(cfg: AppConfig, session_id: str) -> None:
    print(ui.c("╔═════════════════════════════════════════════════════╗", Ui.BLUE))
    print(ui.c("║                     StarRay CLI                     ║", Ui.BOLD, Ui.BLUE))
    print(ui.c("╚═════════════════════════════════════════════════════╝", Ui.BLUE))
    print(
        f"{ui.c('Analyst', Ui.BOLD, Ui.MAGENTA)} is active. Hidden specialist agents are offline in Phase 0."
    )
    print(
        f"{ui.c('Provider:', Ui.CYAN)} {cfg.provider}   "
        f"{ui.c('Model:', Ui.CYAN)} {cfg.default_model}   "
        f"{ui.c('Session:', Ui.CYAN)} {session_id}"
    )
    print(
        ui.c(
            "Commands: /help, /session, /status, exit",
            Ui.DIM,
        )
    )


def cmd_chat(config_path: Path, message: Optional[str], session_id: Optional[str]) -> int:
    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        print(ui.c(str(exc), Ui.RED))
        return 1

    sessions_dir, logs_dir = _resolve_storage_paths(cfg)

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
        _handle_turn(message, state, sessions_dir, logger)
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
                print(ui.c("Commands: /help, /session, /status, exit", Ui.DIM))
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
            _handle_turn(user_text, state, sessions_dir, logger)
    except (KeyboardInterrupt, EOFError):
        state.save(sessions_dir)
        print()

    print(ui.c(f"Session saved: {state.session_id}", Ui.GREEN))
    print(ui.c(f"Resume with: starray --session-id {state.session_id}", Ui.YELLOW))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="starray", description="Starray CLI")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--config", "-c", default="configs/starray.toml")
    parser.add_argument("--session-id")
    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser("status", help="Show baseline app status")
    status_parser.add_argument("--config", "-c")

    chat_parser = subparsers.add_parser("chat", help="Run baseline Analyst chat loop")
    chat_parser.add_argument("--config", "-c")
    chat_parser.add_argument("--message", "-m")
    chat_parser.add_argument("--session-id")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_value = args.config or "configs/starray.toml"
    config_path = Path(config_value)

    if args.command == "status":
        return cmd_status(config_path)
    if args.command == "chat":
        session_id = args.session_id or getattr(args, "session_id", None)
        return cmd_chat(config_path, args.message, session_id)
    if args.command is None:
        session_id = getattr(args, "session_id", None)
        return cmd_chat(config_path, None, session_id)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
