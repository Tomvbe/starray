from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .config import AppConfig, ConfigError, load_config
from .logging_utils import build_session_logger
from .session import SessionState, SessionError, load_session


def _resolve_storage_paths(cfg: AppConfig) -> tuple[Path, Path]:
    session_dir = cfg.data_dir / "sessions"
    log_dir = cfg.data_dir / "logs"
    return session_dir, log_dir


def cmd_status(config_path: Path) -> int:
    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        print(str(exc))
        return 1

    print("Factory status: ready")
    print(f"Provider: {cfg.provider}")
    print(f"Default model: {cfg.default_model}")
    print(f"Data dir: {cfg.data_dir}")
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
    print(analyst_reply)


def cmd_chat(config_path: Path, message: Optional[str], session_id: Optional[str]) -> int:
    try:
        cfg = load_config(config_path)
    except ConfigError as exc:
        print(str(exc))
        return 1

    sessions_dir, logs_dir = _resolve_storage_paths(cfg)

    try:
        if session_id:
            state = load_session(sessions_dir, session_id)
        else:
            state = SessionState.new()
    except SessionError as exc:
        print(str(exc))
        return 1

    logger = build_session_logger(logs_dir, state.session_id)

    print(f"Session: {state.session_id}")

    if message is not None:
        _handle_turn(message, state, sessions_dir, logger)
        return 0

    print("Type 'exit' to quit.")
    while True:
        user_text = input("you> ")
        if user_text.strip().lower() in {"exit", "quit"}:
            state.save(sessions_dir)
            break
        _handle_turn(user_text, state, sessions_dir, logger)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="factory", description="AI Software Factory CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show baseline app status")
    status_parser.add_argument("--config", "-c", default="configs/factory.toml")

    chat_parser = subparsers.add_parser("chat", help="Run baseline Analyst chat loop")
    chat_parser.add_argument("--config", "-c", default="configs/factory.toml")
    chat_parser.add_argument("--message", "-m")
    chat_parser.add_argument("--session-id")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config_path = Path(args.config)

    if args.command == "status":
        return cmd_status(config_path)
    if args.command == "chat":
        return cmd_chat(config_path, args.message, args.session_id)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
