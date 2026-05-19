"""Projectile swept-circle 충돌 판정 테스트 (Issue #44, DECISION-DL-P5P-002).

과거: Projectile.update 는 단일-선분(발사체 이동) vs 타겟 현재 위치(점) 의
최단거리만 검사 — 타겟이 같은 dt 동안 빠르게 이동하면 hit_radius 통과 누락.

현재: 발사체 segment [proj_old → proj_new] 와 타겟 segment [tgt_old → tgt_new]
의 swept-circle 최단거리 < hit_radius 일 때 명중. 타겟 ``_prev_x/_prev_y`` 가
없으면 점으로 fallback (하위 호환).

본 모듈은 CB-01~05 회귀 매트릭스 시나리오를 자동화한다.
"""

from __future__ import annotations

import math

import pytest

from src.entities.projectile import Projectile

pytestmark = pytest.mark.regression_p4

# ---------------------------------------------------------------------------
# 헬퍼: prev/cur 좌표 모두 갖는 타겟
# ---------------------------------------------------------------------------


class _MovingTarget:
    """이동하는 타겟 — PathingSystem 이 갱신하는 _prev_x/_prev_y 모사."""

    def __init__(self, x: float, y: float, prev_x: float | None = None, prev_y: float | None = None) -> None:
        self.x = float(x)
        self.y = float(y)
        self._prev_x = float(prev_x) if prev_x is not None else float(x)
        self._prev_y = float(prev_y) if prev_y is not None else float(y)
        self.alive = True
        self.dying = False


# ---------------------------------------------------------------------------
# CB-01: 정지 타겟에 정면 충돌 (legacy 동작 보존)
# ---------------------------------------------------------------------------


def test_cb01_stationary_target_frontal_hit() -> None:
    """발사체가 정지 타겟에 정면 충돌 — 기존 동작 보존."""
    target = _MovingTarget(x=100.0, y=0.0)  # prev = cur (정지)
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=100.0,
        target_y=0.0,
        damage=10,
        speed=500.0,
        target=target,
        hit_radius=12.0,
    )
    # 500 * 0.25 = 125 이동 → target 100 통과
    proj.update(0.25)
    assert proj.hit is True


# ---------------------------------------------------------------------------
# CB-02: 타겟이 같은 방향으로 도주 — 발사체가 따라잡으면 명중
# ---------------------------------------------------------------------------


def test_cb02_fleeing_target_caught_when_projectile_faster() -> None:
    """타겟이 발사체와 같은 방향으로 이동 — 발사체가 더 빠르면 명중."""
    # 타겟이 dt=0.1 동안 (100, 0) → (110, 0) 이동 (속도 100)
    target = _MovingTarget(x=110.0, y=0.0, prev_x=100.0, prev_y=0.0)
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=100.0,
        target_y=0.0,
        damage=10,
        speed=1500.0,
        target=target,
        hit_radius=12.0,
    )
    # 1500 * 0.1 = 150 이동 → 110 통과
    proj.update(0.1)
    assert proj.hit is True


# ---------------------------------------------------------------------------
# CB-03: 빠른 타겟이 발사체 경로 가로지름 — sweep 만이 감지 가능
# ---------------------------------------------------------------------------


def test_cb03_fast_target_crossing_projectile_path() -> None:
    """타겟이 dt 안에 발사체 line 을 수직으로 가로지름 — swept-circle 동기 감지.

    발사체 경로상 (100, 0) 지점에서 타겟이 같은 t≈0.5 시점에 (100, 0) 부근에 위치.
    두 segment 의 동기화된 거리가 hit_radius=12 안으로 들어오는 케이스.
    """
    # 발사체: (0, 0) → (200, 0) 수평 이동 (dt=0.1 에 100 px)
    # 타겟: prev=(100, -20) → cur=(100, 20) (수직 이동) — t=0.5 시점에 (100, 0)
    # 같은 t=0.5 시점 발사체 위치 (50, 0) — 거리 50 (> 12, 미명중)
    # 더 가까운 동기 케이스: 타겟 prev=(50, -5) → cur=(50, 5), 발사체 (0,0) → (100, 0)
    target = _MovingTarget(x=50.0, y=5.0, prev_x=50.0, prev_y=-5.0)
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=50.0,
        target_y=5.0,
        damage=10,
        speed=1000.0,
        target=target,
        hit_radius=12.0,
    )
    # 발사체 dt=0.1: (0,0) → ≈(99.5, 9.95), t=0.5 → (49.75, 4.97)
    # 타겟 t=0.5 → (50, 0). 거리 ≈ sqrt(0.0625 + 24.7) ≈ 4.98 < 12 → 명중.
    proj.update(0.1)
    assert proj.hit is True


# ---------------------------------------------------------------------------
# CB-04: 정지 타겟에서 멀리 떨어진 발사체 → 미명중
# ---------------------------------------------------------------------------


def test_cb04_no_hit_when_far_from_stationary_target() -> None:
    """타겟이 멀리 정지 + 발사체가 한 틱에 충분히 가까워지지 않으면 미명중."""
    target = _MovingTarget(x=1000.0, y=0.0)
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=1000.0,
        target_y=0.0,
        damage=10,
        speed=10.0,
        target=target,
        hit_radius=12.0,
    )
    proj.update(0.016)  # 0.16 px 이동 → 999.84 남음
    assert proj.hit is False


# ---------------------------------------------------------------------------
# CB-05: hit_radius 경계 케이스 — 거리 == hit_radius 직전
# ---------------------------------------------------------------------------


def test_cb05_hit_radius_boundary_inside_hits() -> None:
    """closest_dist < hit_radius 이면 명중 (안쪽 경계)."""
    target = _MovingTarget(x=11.5, y=0.0)  # 발사체 정지 시 거리 11.5 < 12
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=11.5,
        target_y=0.0,
        damage=10,
        speed=0.001,  # 거의 정지
        target=target,
        hit_radius=12.0,
    )
    proj.update(0.001)
    assert proj.hit is True


def test_cb05b_hit_radius_boundary_outside_no_hit() -> None:
    """closest_dist > hit_radius 이면 미명중 (바깥 경계)."""
    target = _MovingTarget(x=20.0, y=100.0)  # y 차이 100 — 발사체 라인에서 멀음
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=20.0,
        target_y=0.0,  # 발사 방향은 (20, 0) — 위로 이동
        damage=10,
        speed=1.0,
        target=target,
        hit_radius=12.0,
    )
    proj.update(0.001)  # 거의 안 움직임 + 타겟이 멀음
    assert proj.hit is False


# ---------------------------------------------------------------------------
# CB-06: 타겟이 dying — fly-through (should_release)
# ---------------------------------------------------------------------------


def test_cb06_dying_target_triggers_fly_through() -> None:
    """타겟이 dying 이면 hit 대신 should_release=True."""
    target = _MovingTarget(x=50.0, y=0.0)
    target.dying = True
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=50.0,
        target_y=0.0,
        damage=10,
        speed=500.0,
        target=target,
        hit_radius=12.0,
    )
    proj.update(0.2)
    assert proj.should_release is True
    assert proj.hit is False


# ---------------------------------------------------------------------------
# CB-07: target=None — fallback 으로 _target_x/_target_y 사용
# ---------------------------------------------------------------------------


def test_cb07_no_target_entity_uses_snapshot() -> None:
    """target=None 이면 발사 시점 좌표 스냅샷으로 명중 판정."""
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=50.0,
        target_y=0.0,
        damage=10,
        speed=500.0,
        target=None,
        hit_radius=12.0,
    )
    proj.update(0.15)  # 75 px 이동 → 50 통과
    assert proj.hit is True


# ---------------------------------------------------------------------------
# CB-08: legacy 타겟 (_prev_x/_prev_y 없음) — 단일 점으로 동작
# ---------------------------------------------------------------------------


class _LegacyTarget:
    """_prev_x/_prev_y 가 없는 구식 타겟 (하위 호환 검사)."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.alive = True
        self.dying = False


def test_cb08_legacy_target_without_prev_uses_point_fallback() -> None:
    """_prev_x/_prev_y 가 없는 타겟은 현재 좌표만으로 판정 (legacy 동작)."""
    target = _LegacyTarget(x=50.0, y=0.0)
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=50.0,
        target_y=0.0,
        damage=10,
        speed=500.0,
        target=target,
        hit_radius=12.0,
    )
    proj.update(0.2)  # 100 px 이동 → 50 통과
    assert proj.hit is True


# ---------------------------------------------------------------------------
# CB-09: PathingSystem 통합 — _prev_x/_prev_y 자동 갱신 확인
# ---------------------------------------------------------------------------


def test_cb09_pathing_system_updates_prev_coordinates() -> None:
    """PathingSystem.update 가 enemy._prev_x/_prev_y 를 갱신한다."""
    from src.data.loader import EnemyDef
    from src.entities.enemy import Enemy
    from src.systems.pathing import PathingSystem

    edef = EnemyDef(
        id="dummy",
        name="dummy",
        hp=10,
        speed=100.0,
        armor=0,
        damage_to_castle=1,
        gold_drop=1,
        sprite="x",
    )
    enemy = Enemy(x=0.0, y=0.0, enemy_def=edef, path_id="p0")
    world: dict = {"enemies": [enemy], "waypoints": {"p0": [(0.0, 0.0), (200.0, 0.0)]}}
    ps = PathingSystem(world)
    # 첫 update: prev 는 spawn 좌표 (0, 0), cur 는 100 으로 이동.
    ps.update(1.0)
    assert math.isclose(enemy._prev_x, 0.0)
    assert math.isclose(enemy._prev_y, 0.0)
    assert enemy.x > 0.0
    # 두 번째 update: prev=현재 위치, cur=다음 위치.
    prev_x = enemy.x
    ps.update(0.5)
    assert math.isclose(enemy._prev_x, prev_x)


# ---------------------------------------------------------------------------
# CB-10: swept-circle 으로 fast-overshoot 케이스 회귀 가드
# ---------------------------------------------------------------------------


def test_cb10_high_speed_projectile_no_overshoot() -> None:
    """높은 속도 발사체가 작은 hit_radius 를 한 틱에 통과해도 명중 (regression).

    DECISION-DT1-P4B-005 의 시뮬레이터 우회 사유였던 overshoot 케이스.
    speed=1000 px/s, dt=0.05 → 50 px 이동. hit_radius=12 — 한 틱에 24 px 통과 폭
    안에 들지 못해도 segment sweep 으로 잡힌다.
    """
    target = _MovingTarget(x=25.0, y=0.0)  # prev = cur (정지 보스)
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=25.0,
        target_y=0.0,
        damage=10,
        speed=1000.0,
        target=target,
        hit_radius=12.0,
    )
    proj.update(0.05)  # 50 px 이동 → x=50, 타겟 25 — 거리 25 지만 segment 가 통과
    assert proj.hit is True
