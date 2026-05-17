"""``after(16)`` 기반 게임 루프 (DECISION-2.1).

DESIGN: 가변 dt, 50ms 클램프(스파이크 방지). ``stop()`` 시 다음 스케줄을
취소하지 않고 ``_running`` 플래그로 다음 틱에서 빠져나오는 구조.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TYPE_CHECKING

from src.core.settings import MAX_DT_S, TARGET_DT_MS

if TYPE_CHECKING:
    import tkinter as tk


TickCallback = Callable[[float], None]


class GameLoop:
    """root.after를 사용한 단일 시뮬·렌더 루프."""

    def __init__(self, root: tk.Misc, on_tick: TickCallback) -> None:
        self.root = root
        self.on_tick = on_tick
        self._prev: float = time.perf_counter()
        self._running: bool = False

        # 간이 FPS 측정.
        self._fps_acc: float = 0.0
        self._fps_cnt: int = 0
        self.fps: float = 0.0

    def start(self) -> None:
        """루프 시작."""
        if self._running:
            return
        self._running = True
        self._prev = time.perf_counter()
        self._schedule()

    def stop(self) -> None:
        """루프 중지(현재 예약된 after는 자연 소진)."""
        self._running = False

    # ------------------------------------------------------------------
    def _schedule(self) -> None:
        if not self._running:
            return
        self.root.after(TARGET_DT_MS, self._tick)

    def _tick(self) -> None:
        if not self._running:
            return
        now = time.perf_counter()
        dt = min(now - self._prev, MAX_DT_S)
        self._prev = now
        try:
            self.on_tick(dt)
        finally:
            # FPS 측정은 예외와 무관하게 갱신.
            self._fps_acc += dt
            self._fps_cnt += 1
            if self._fps_acc >= 0.5:
                self.fps = self._fps_cnt / self._fps_acc
                self._fps_acc = 0.0
                self._fps_cnt = 0
            self._schedule()
