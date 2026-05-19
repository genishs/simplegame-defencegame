"""WaveSystem 단위 테스트 (tk 비의존).

커버 케이스:
- 단일 웨이브 스폰 타이밍
- 다중 웨이브 순차 진행
- paused 플래그 시 스폰 중단
- all_clear 플래그
- time_to_next_wave / current_wave 속성
- force_next()
- spawn_callback 호출
"""

from __future__ import annotations

from src.data.loader import WaveDef, WaveSpawn
from src.systems.wave import WaveSystem


def _make_wave(
    delay_s: float,
    enemy_type: str = "tang_soldier",
    count: int = 3,
    interval_s: float = 0.5,
    path: str = "p_main",
    boss: str | None = None,
) -> WaveDef:
    spawn = WaveSpawn(type=enemy_type, count=count, interval_s=interval_s, path=path)
    return WaveDef(delay_s=delay_s, spawns=(spawn,), boss=boss)


# ---------------------------------------------------------------------------
# 기본 스폰 타이밍
# ---------------------------------------------------------------------------


def test_single_wave_spawn_timing() -> None:
    """delay_s 후 스폰이 시작되고, interval_s 마다 적이 추가된다."""
    spawned: list[tuple[str, str]] = []
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load((_make_wave(delay_s=2.0, count=3, interval_s=1.0),))

    # delay 미완 → 스폰 없음
    ws.update(1.9)
    assert len(spawned) == 0
    assert ws.current_wave == 0

    # delay 완료 → 웨이브 시작 → 첫 적 즉시
    ws.update(0.2)  # 총 2.1s > 2.0s
    assert ws.current_wave == 1

    # interval 경과 시마다 스폰
    ws.update(1.0)
    ws.update(1.0)
    assert len(spawned) >= 2


def test_spawn_callback_receives_correct_type_and_path() -> None:
    """spawn_callback이 enemy_type, path_id를 올바르게 받는다."""
    calls: list[tuple[str, str]] = []
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: calls.append((t, p))
    ws.load((_make_wave(delay_s=0.0, enemy_type="tang_archer", count=1, interval_s=0.1, path="p_north"),))

    ws.update(0.01)  # delay=0 이므로 즉시 시작
    ws.update(0.5)
    assert any(t == "tang_archer" and p == "p_north" for t, p in calls)


# ---------------------------------------------------------------------------
# 다중 웨이브
# ---------------------------------------------------------------------------


def test_multiple_waves_advance_in_order() -> None:
    """3개 웨이브가 순서대로 진행된다."""
    wave_events: list[int] = []

    class _FakeBus:
        def publish(self, event: str, data: dict) -> None:
            if event == "wave.started":
                wave_events.append(data["index"])

    world: dict = {"events": _FakeBus()}
    ws = WaveSystem(world)
    ws.load(
        (
            _make_wave(delay_s=1.0, count=1, interval_s=0.1),
            _make_wave(delay_s=1.0, count=1, interval_s=0.1),
            _make_wave(delay_s=1.0, count=1, interval_s=0.1),
        )
    )

    # 웨이브 0 시작
    ws.update(1.5)  # delay 1s + 스폰 종료
    ws.update(0.5)

    # 웨이브 1 시작
    ws.update(1.5)
    ws.update(0.5)

    # 웨이브 2 시작
    ws.update(1.5)
    ws.update(0.5)

    assert 0 in wave_events
    assert 1 in wave_events
    assert 2 in wave_events


def test_all_clear_after_last_wave() -> None:
    """마지막 웨이브 종료 후 all_clear=True."""
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load((_make_wave(delay_s=0.0, count=1, interval_s=0.0),))

    ws.update(0.01)  # 웨이브 시작
    ws.update(1.0)  # 스폰 소진

    assert ws.all_clear is True


# ---------------------------------------------------------------------------
# paused 동작
# ---------------------------------------------------------------------------


def test_paused_halts_spawn() -> None:
    """paused=True이면 스폰 타이머가 진행되지 않는다."""
    spawned: list = []
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load((_make_wave(delay_s=1.0, count=5, interval_s=0.2),))

    ws.paused = True
    ws.update(5.0)  # 5초 경과해도 일시정지 중
    assert len(spawned) == 0
    assert ws.current_wave == 0


def test_resume_after_pause_continues_spawn() -> None:
    """일시정지 해제 후 정상적으로 스폰된다."""
    spawned: list = []
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.spawn_callback = lambda t, p: spawned.append((t, p))
    ws.load((_make_wave(delay_s=0.5, count=2, interval_s=0.5),))

    ws.paused = True
    ws.update(2.0)
    assert len(spawned) == 0

    ws.paused = False
    ws.update(0.6)  # delay 소진 + 첫 스폰
    ws.update(0.6)  # 두 번째 스폰
    assert len(spawned) >= 1


# ---------------------------------------------------------------------------
# all_clear 플래그
# ---------------------------------------------------------------------------


def test_all_clear_not_set_during_waves() -> None:
    """웨이브 진행 중에는 all_clear=False."""
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load(
        (
            _make_wave(delay_s=1.0, count=3, interval_s=0.5),
            _make_wave(delay_s=2.0, count=3, interval_s=0.5),
        )
    )

    ws.update(1.1)
    assert ws.all_clear is False


def test_empty_waves_all_clear_immediately() -> None:
    """웨이브가 없으면 로드 즉시 all_clear."""
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load(())
    assert ws.all_clear is True


# ---------------------------------------------------------------------------
# time_to_next_wave / current_wave
# ---------------------------------------------------------------------------


def test_time_to_next_wave_decreases() -> None:
    """time_to_next_wave이 업데이트마다 감소한다."""
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load((_make_wave(delay_s=5.0, count=1, interval_s=1.0),))

    t0 = ws.time_to_next_wave
    ws.update(1.0)
    t1 = ws.time_to_next_wave
    assert t1 < t0


def test_current_wave_increments() -> None:
    """웨이브 시작 시 current_wave가 증가한다."""
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load(
        (
            _make_wave(delay_s=0.1, count=1, interval_s=0.1),
            _make_wave(delay_s=0.1, count=1, interval_s=0.1),
        )
    )

    assert ws.current_wave == 0
    ws.update(0.2)
    assert ws.current_wave >= 1


# ---------------------------------------------------------------------------
# force_next
# ---------------------------------------------------------------------------


def test_force_next_skips_delay() -> None:
    """force_next()가 대기 중인 delay를 건너뛴다."""
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load((_make_wave(delay_s=100.0, count=1, interval_s=0.1),))

    result = ws.force_next()
    assert result is True

    ws.update(0.5)
    assert ws.current_wave >= 1


def test_force_next_returns_false_when_all_clear() -> None:
    """all_clear 상태에서 force_next()는 False."""
    world: dict = {"events": None}
    ws = WaveSystem(world)
    ws.load(())
    assert ws.force_next() is False
