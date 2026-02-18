from __future__ import annotations

import logging
from pathlib import Path


def build_session_logger(log_dir: Path, session_id: str) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{session_id}.log"

    logger = logging.getLogger(f"starray.session.{session_id}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
