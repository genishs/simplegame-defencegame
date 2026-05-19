"""사운드 백엔드 (OPEN-1 미확정).

OPEN: backend TBD — winsound(stdlib) / playsound / 무사운드 중 미결.
현 단계에서는 모든 호출이 no-op. 인터페이스만 고정하여 후속 합류에 대비.
EXPECTED: lead가 OPEN-1 결정 후 구현. 그때까지 호출자는 자유롭게 호출 가능.
"""

from __future__ import annotations

from src.core.logger import get_logger

_log = get_logger(__name__)


class SoundManager:
    """no-op 사운드 매니저."""

    def play_bgm(self, name: str, loop: bool = True) -> None:
        # OPEN: backend TBD
        _log.debug("SoundManager.play_bgm(%s, loop=%s) [no-op]", name, loop)

    def play_sfx(self, name: str) -> None:
        # OPEN: backend TBD
        _log.debug("SoundManager.play_sfx(%s) [no-op]", name)

    def stop_all(self) -> None:
        _log.debug("SoundManager.stop_all() [no-op]")
