"""웨이브 스케줄러 (tk 비의존).

DESIGN: ``WaveDef`` 리스트를 받아 ``delay_s``만큼 대기 후 ``spawns``를 순회.
``spawn_callback``으로 외부(BattleScene/엔티티 풀)에 적 생성을 위임.
DECISION-A·4.1: tkinter import 절대 금지 — 순수 도메인 모듈.

DECISION-DL-P5P-001 (Issue #43): 보스 spawn path_id 결정 로직.
  과거: ``"p_main"`` 하드코딩 → stage_03/04/05 처럼 ``p_main`` 미정의 시 spawn 실패.
  현재: 우선순위 (a) ``wave_def.boss_path`` 명시 → (b) ``load(paths=...)`` 첫 path id →
        (c) ``world['waypoints']`` 첫 키 → (d) 기존 호환 ``"p_main"`` fallback.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.data.loader import PathDef, WaveDef


SpawnFn = Callable[[str, str], None]  # (enemy_type, path_id) -> None


class WaveSystem:
    """웨이브 큐 관리.

    Attributes:
        waves: 진행할 웨이브 정의 리스트.
        current_index: 진행 중인 웨이브 인덱스(-1=아직 시작 안 됨).
        spawn_callback: 적 1체를 실제로 생성하는 콜백.
        all_clear: 모든 웨이브가 완전히 종료됐을 때 True.
        paused: True이면 스폰/타이머 일시정지.
        time_to_next_wave: 다음 웨이브 시작까지 남은 초(-1=없음).
        current_wave: 현재(0-based) 웨이브 인덱스. 미시작이면 0.
    """

    def __init__(self, world: dict[str, Any]) -> None:  # type: ignore[type-arg]
        self.world = world
        self.waves: tuple[WaveDef, ...] = ()
        self.current_index: int = -1
        self.spawn_callback: SpawnFn | None = None
        self.all_clear: bool = False
        self.paused: bool = False

        # 대기 타이머 (다음 웨이브 시작 전 delay_s)
        self._delay_remaining: float = 0.0
        self._wave_started: bool = False  # 현재 웨이브가 이미 시작됐는가

        # 현재 웨이브 스폰 진행 상태
        # _spawn_queue: list of (type, path, remaining_count, interval_acc)
        self._spawn_queues: list[dict[str, Any]] = []

        # Issue #43: 보스 spawn fallback 시 사용할 기본 path id (load 시 갱신).
        # None 이면 ``world['waypoints']`` 의 첫 키 또는 "p_main" 으로 fallback.
        self._default_path_id: str | None = None

    # ------------------------------------------------------------------
    # 공개 속성 (HUD가 읽음)
    # ------------------------------------------------------------------

    @property
    def current_wave(self) -> int:
        """1-based 현재 웨이브 번호. 미시작이면 0."""
        return max(0, self.current_index + 1)

    @property
    def time_to_next_wave(self) -> float:
        """다음 웨이브까지 남은 초. 없으면 -1."""
        if self.all_clear:
            return -1.0
        if not self._wave_started:
            # 아직 첫 웨이브 대기 중
            return self._delay_remaining
        # 현재 웨이브가 진행 중 → 다음 대기
        next_idx = self.current_index + 1
        if next_idx >= len(self.waves):
            return -1.0
        return self._delay_remaining

    # ------------------------------------------------------------------
    # 로드
    # ------------------------------------------------------------------

    def load(  # type: ignore[no-untyped-def]
        self,
        waves: tuple[WaveDef, ...],
        paths: tuple[PathDef, ...] | None = None,
    ) -> None:
        """스테이지 진입 시 웨이브 정의를 주입.

        Args:
            waves: 진행할 ``WaveDef`` 리스트.
            paths: 스테이지 ``PathDef`` 튜플 (DECISION-DL-P5P-001, Issue #43).
                보스 spawn 시 ``wave.boss_path`` 미명시 + ``world['waypoints']``
                미설정 환경의 fallback 으로 첫 path id 를 사용한다.
                None 이거나 비어 있으면 기존 동작 유지 (world 또는 "p_main" fallback).
        """
        self.waves = tuple(waves)
        self.current_index = -1
        self.all_clear = False
        self.paused = False
        self._wave_started = False
        self._spawn_queues = []
        # paths 주입 시 첫 path id 를 보스 fallback 기본값으로 기억.
        if paths:
            self._default_path_id = paths[0].id
        else:
            self._default_path_id = None
        if self.waves:
            self._delay_remaining = float(self.waves[0].delay_s)
        else:
            self._delay_remaining = 0.0
            self.all_clear = True

    # ------------------------------------------------------------------
    # 업데이트 (매 틱)
    # ------------------------------------------------------------------

    def update(self, dt: float, world: dict[str, Any] | None = None) -> None:
        """매 틱 호출. 시간 누적으로 스폰 + 다음 웨이브 진행."""
        if self.paused or self.all_clear:
            return
        if world is not None:
            self.world = world

        if not self._wave_started:
            # 현재 웨이브 대기 중
            self._delay_remaining -= dt
            if self._delay_remaining <= 0.0:
                # 오버슈트된 dt를 스폰 큐에 바로 반영 (대기 시간 정밀도 보장)
                overshoot = -self._delay_remaining
                self._start_next_wave()
                if self._wave_started and overshoot > 0.0:
                    self._tick_spawns(overshoot)
                    if not self._spawn_queues:
                        self._wave_started = False
                        next_idx = self.current_index + 1
                        if next_idx >= len(self.waves):
                            self.all_clear = True
                            self._publish("wave.all_clear", {})
                        else:
                            self._delay_remaining = float(self.waves[next_idx].delay_s)
        else:
            # 현재 웨이브 스폰 진행
            self._tick_spawns(dt)
            # 모든 스폰 큐가 소진됐으면 다음 웨이브 대기
            if not self._spawn_queues:
                self._wave_started = False
                next_idx = self.current_index + 1
                if next_idx >= len(self.waves):
                    self.all_clear = True
                    self._publish("wave.all_clear", {})
                else:
                    self._delay_remaining = float(self.waves[next_idx].delay_s)

    def force_next(self) -> bool:
        """Space 키로 다음 웨이브 강제 시작. 가능하면 True."""
        if self.all_clear:
            return False
        if not self._wave_started:
            # 대기 중이면 즉시 시작
            self._delay_remaining = 0.0
            return True
        # 현재 웨이브 스폰 중 → 다음 웨이브 있는지 확인
        next_idx = self.current_index + 1
        if next_idx >= len(self.waves):
            return False
        # 현재 스폰 큐 강제 비우고 다음 웨이브 시작
        self._spawn_queues = []
        self._wave_started = False
        self._delay_remaining = 0.0
        return True

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _start_next_wave(self) -> None:
        """다음 웨이브를 시작한다."""
        self.current_index += 1
        if self.current_index >= len(self.waves):
            self.all_clear = True
            self._publish("wave.all_clear", {})
            return

        wave_def = self.waves[self.current_index]
        self._wave_started = True

        # 스폰 큐 초기화
        self._spawn_queues = []
        for spawn in wave_def.spawns:
            self._spawn_queues.append(
                {
                    "type": spawn.type,
                    "path": spawn.path,
                    "remaining": spawn.count,
                    "interval": spawn.interval_s,
                    "acc": 0.0,  # 첫 적은 즉시 스폰
                }
            )

        # 보스 스폰 (DECISION-DL-P5P-001, Issue #43)
        if wave_def.boss:
            boss_path = self._resolve_boss_path(wave_def)
            self._do_spawn(wave_def.boss, boss_path)

        self._publish("wave.started", {"index": self.current_index})

    def _resolve_boss_path(self, wave_def: WaveDef) -> str:
        """보스 wave 의 spawn path id 결정 (DECISION-DL-P5P-001, Issue #43).

        우선순위:
          1. ``wave_def.boss_path`` 에 명시된 값 (stage JSON 의 ``boss_path`` 필드).
          2. 같은 wave 의 ``spawns`` 첫 항목 ``path`` — 정확한 컨텍스트 회복용.
          3. ``load(paths=...)`` 로 주입된 첫 path id.
          4. ``world['waypoints']`` 가 dict 면 첫 키.
          5. 기존 호환 ``"p_main"`` fallback (단일 경로 stage_01/02 동작 보존).
        """
        # (1) WaveDef 명시 필드 (옵션)
        boss_path = getattr(wave_def, "boss_path", None)
        if boss_path:
            return str(boss_path)
        # (2) wave 의 일반 spawn path 차용 — 보스가 보병과 같은 경로로 진입하는 게 자연스러움
        if wave_def.spawns:
            first_spawn_path = wave_def.spawns[0].path
            if first_spawn_path:
                return str(first_spawn_path)
        # (3) load(paths=...) 주입값
        if self._default_path_id:
            return self._default_path_id
        # (4) world['waypoints'] dict 의 첫 키
        wp = self.world.get("waypoints")
        if isinstance(wp, dict) and wp:
            try:
                return next(iter(wp.keys()))
            except StopIteration:
                pass
        # (5) 호환 fallback
        return "p_main"

    def _tick_spawns(self, dt: float) -> None:
        """현재 웨이브의 스폰 큐를 진행한다."""
        finished: list[int] = []
        for i, sq in enumerate(self._spawn_queues):
            if sq["remaining"] <= 0:
                finished.append(i)
                continue
            sq["acc"] += dt
            while sq["acc"] >= sq["interval"] and sq["remaining"] > 0:
                sq["acc"] -= sq["interval"]
                sq["remaining"] -= 1
                self._do_spawn(sq["type"], sq["path"])
            if sq["remaining"] <= 0:
                finished.append(i)

        # 소진된 큐 역순으로 제거
        for i in sorted(set(finished), reverse=True):
            self._spawn_queues.pop(i)

    def _do_spawn(self, enemy_type: str, path_id: str) -> None:
        """실제 스폰 수행. spawn_callback 또는 world.spawn_enemy 사용."""
        if self.spawn_callback is not None:
            self.spawn_callback(enemy_type, path_id)
        elif callable(self.world.get("spawn_enemy")):
            self.world["spawn_enemy"](enemy_type, path_id)

    def _publish(self, event: str, data: dict[str, Any]) -> None:
        bus = self.world.get("events")
        if bus is not None:
            bus.publish(event, data)

    # ------------------------------------------------------------------
    # 하위 호환 (기존 테스트용)
    # ------------------------------------------------------------------

    def _on_wave_start(self, idx: int) -> None:
        self._publish("wave.started", {"index": idx})
