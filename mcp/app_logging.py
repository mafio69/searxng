"""Environment mode resolution and rotating/gzip-archived application logging."""

import gzip
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_FILE = ROOT / ".local" / "logs" / "szukaj.log"
DEFAULT_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_BACKUP_COUNT = 5
DEV_ENVIRONMENTS = {"dev", "development", "local"}
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def is_dev_env(env_value: str | None = None) -> bool:
    raw = os.getenv("APP_ENV", "prod") if env_value is None else env_value
    return raw.strip().lower() in DEV_ENVIRONMENTS


def resolve_log_level(level_name: str | None = None) -> int:
    raw = (os.getenv("LOG_LEVEL") or "WARNING") if level_name is None else level_name
    normalized = raw.strip().upper()
    if normalized == "WARN":
        normalized = "WARNING"
    level = getattr(logging, normalized, None)
    return level if isinstance(level, int) else logging.WARNING


def _positive_int(raw: str | None, default: int) -> int:
    if not raw:
        return default
    try:
        parsed = int(raw)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _archive_name(default_name: str) -> str:
    return f"{default_name}.gz"


def _compress_rotated_log(source: str, destination: str) -> None:
    source_path = Path(source)
    if not source_path.is_file():
        return
    with source_path.open("rb") as src, gzip.open(destination, "wb") as dst:
        shutil.copyfileobj(src, dst)
    source_path.unlink(missing_ok=True)


class CompressedRotatingFileHandler(RotatingFileHandler):
    """Rotates logs by size and compresses rotated backups into .gz archives."""

    def __init__(self, filename: Path, max_bytes: int, backup_count: int):
        super().__init__(
            filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        self.namer = _archive_name
        self.rotator = _compress_rotated_log


def _close_existing_handlers(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


def configure_logging(
    level_name: str | None = None,
    log_file: Path | str | None = None,
    max_bytes: int | None = None,
    backup_count: int | None = None,
) -> logging.Logger:
    logger = logging.getLogger("szukaj")
    _close_existing_handlers(logger)
    logger.setLevel(resolve_log_level(level_name))
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    target_str = os.getenv("LOG_FILE") if log_file is None else str(log_file)
    target_path = Path(target_str) if target_str else DEFAULT_LOG_FILE
    resolved_max_bytes = (
        _positive_int(os.getenv("LOG_MAX_BYTES"), DEFAULT_MAX_BYTES)
        if max_bytes is None
        else max_bytes
    )
    resolved_backups = (
        _positive_int(os.getenv("LOG_BACKUP_COUNT"), DEFAULT_BACKUP_COUNT)
        if backup_count is None
        else backup_count
    )

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = CompressedRotatingFileHandler(
            target_path,
            max_bytes=resolved_max_bytes,
            backup_count=resolved_backups,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError as exc:
        logger.warning("File logging unavailable (%s); continuing with stderr only", type(exc).__name__)

    return logger


def get_logger() -> logging.Logger:
    logger = logging.getLogger("szukaj")
    if not logger.handlers:
        return configure_logging()
    return logger
