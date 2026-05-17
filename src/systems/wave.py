"""웨이브 스케줄러 (tk 비의존).

DESIGN: ``WaveDef`` 리스트를 받아 ``delay_s``만큼 대기 후 ``spawns``를 순회.
``spawn_callback``으로 외부(BattleScene/엔티티 풀)에 적 생성을 위임.
EXPECTED: team-member-2가 spawn_callback 본 구현 + 보스 스폰 + force_next.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.data.loader import WaveDef


SpawnFn = Callable[[str, str], None]  # (enemy_type, path_id) -> None


class WaveSystem:
    """웨이브 큐 관리.

    Attributes:
        waves: 진행할 웨이브 정의 리스트.
        current_index: 진행 중인 웨이브 인덱스(없으면 -1).
        spawn_callback: 적 1체를 실제로 생성하는 콜백. team-member-2가 주입.
    """

    def __init__(self, world: dict) -> None:  # type: ignore[type-arg]
        self.world = world
        self.waves: tuple[WaveDef, ...] = ()
        self.current_index: int = -1
        self._delay_remaining: float = 0.0
        self._active: bool = False
        self.spawn_callback: SpawnFn | None = None

    def load(self, waves) -> None:  # type: ignore[no-untyped-def]
        """스테이지 진입 시 웨이브 정의를 주입."""
        self.waves = tuple(waves)
        self.current_index = -1
        self._delay_remaining = self.waves[0].delay_s if self.waves else 0.0
        self._active = bool(self.waves)

    def update(self, dt: float) -> None:
        """매 틱 호출. 시간 누적으로 다음 웨이브 트리거."""
        if not self._active:
            return
        # TODO(team-member-2): spawns interval_s 누적, spawn_callback 호출,
        # 웨이브 종료 시 다음으로 넘기기, 보스 스폰 발행.
        self._delay_remaining -= dt
        if self._delay_remaining <= 0 and self.current_index + 1 < len(self.waves):
            self.current_index += 1
            self._on_wave_start(self.current_index)
            if self.current_index + 1 < len(self.waves):
                self._delay_remaining = self.waves[self.current_index + 1].delay_s
            else:
                self._active = False

    def force_next(self) -> bool:
        """Space 키로 다음 웨이브 강제 시작. 가능하면 True."""
        # TODO(team-member-2): 현 웨이브 종료 + 다음으로 전환.
        if self.current_index + 1 >= len(self.waves):
            return False
        self._delay_remaining = 0.0
        return True

    # ------------------------------------------------------------------
    def _on_wave_start(self, idx: int) -> None:
        bus = self.world.get("events")
        if bus is not None:
            bus.publish("wave.started", {"index": idx})
