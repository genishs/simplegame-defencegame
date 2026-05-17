"""표준 logging 래퍼.

DESIGN: stdlib ``logging``만 사용. 개발 모드(``DEFGAME_DEV=1``)는 DEBUG,
운영은 INFO. 파일 핸들러 추가는 추후 확장.
"""

from __future__ import annotations

import logging
import os
import sys

_CONFIGURED: bool = False


def setup_logging(level: int | None = None) -> None:
    """루트 로거를 한 번만 구성한다(중복 호출 안전).

    Args:
        level: 명시적 레벨. None이면 ``DEFGAME_DEV`` 환경변수로 결정.
    """
    global _CONFIGURED
    if _CONFIGURED:
        return
    if level is None:
        level = logging.DEBUG if os.environ.get("DEFGAME_DEV") == "1" else logging.INFO

    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """모듈별 로거를 가져온다. ``setup_logging`` 자동 호출."""
    setup_logging()
    return logging.getLogger(name)
