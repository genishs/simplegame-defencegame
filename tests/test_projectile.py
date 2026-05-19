"""Projectile 단위 테스트 (tk 비의존)."""

from __future__ import annotations

import math

from src.entities.projectile import Projectile

# ---------------------------------------------------------------------------
# 기본 생성
# ---------------------------------------------------------------------------


def test_projectile_initial_state() -> None:
    proj = Projectile(x=0.0, y=0.0, target_x=100.0, target_y=0.0, damage=12, speed=400.0)
    assert proj.alive is True
    assert proj.hit is False
    assert proj.should_release is False
    assert proj.damage == 12


def test_velocity_vector_direction() -> None:
    """발사 방향이 타겟을 향하는지 확인."""
    proj = Projectile(x=0.0, y=0.0, target_x=0.0, target_y=100.0, damage=10, speed=200.0)
    # 수직 방향: vx≈0, vy≈200
    assert abs(proj.vx) < 1e-6
    assert abs(proj.vy - 200.0) < 1e-6


def test_velocity_magnitude_equals_speed() -> None:
    proj = Projectile(x=0.0, y=0.0, target_x=3.0, target_y=4.0, damage=10, speed=100.0)
    speed = math.hypot(proj.vx, proj.vy)
    assert abs(speed - 100.0) < 1e-6


# ---------------------------------------------------------------------------
# 이동
# ---------------------------------------------------------------------------


def test_update_moves_projectile() -> None:
    proj = Projectile(x=0.0, y=0.0, target_x=1000.0, target_y=0.0, damage=10, speed=100.0)
    proj.update(1.0)
    assert proj.x > 0.0
    assert proj.hit is False


def test_update_moves_by_speed_times_dt() -> None:
    proj = Projectile(x=0.0, y=0.0, target_x=1000.0, target_y=0.0, damage=10, speed=200.0)
    proj.update(0.5)
    # 수평 이동만: dx = 200 * 0.5 = 100
    assert abs(proj.x - 100.0) < 1e-3


# ---------------------------------------------------------------------------
# 명중 판정: 타겟 거리 < hit_radius
# ---------------------------------------------------------------------------


def test_hit_when_close_to_target() -> None:
    """타겟 좌표에 충분히 가까워지면 hit=True."""
    proj = Projectile(x=0.0, y=0.0, target_x=10.0, target_y=0.0, damage=10, speed=1000.0, hit_radius=12.0)
    # 1 step: 발사체가 target_x=10에 거의 도달
    proj.update(0.02)  # 1000 * 0.02 = 20 > 10 → 이미 지나침
    assert proj.hit is True


def test_no_hit_when_far_from_target() -> None:
    proj = Projectile(x=0.0, y=0.0, target_x=1000.0, target_y=0.0, damage=10, speed=10.0, hit_radius=12.0)
    proj.update(0.016)  # 10 * 0.016 = 0.16 이동 → 타겟까지 999.84 남음
    assert proj.hit is False


# ---------------------------------------------------------------------------
# 타겟 엔티티 추적
# ---------------------------------------------------------------------------


class _DummyEnemy:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.alive = True
        self.dying = False


def test_hit_when_close_to_target_entity() -> None:
    target = _DummyEnemy(x=50.0, y=0.0)
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
    proj.update(0.2)  # 500*0.2=100 이동 → 타겟 통과
    assert proj.hit is True


def test_should_release_when_target_dying() -> None:
    """타겟이 dying이면 should_release=True로 fly-through."""
    target = _DummyEnemy(x=200.0, y=0.0)
    target.dying = True
    proj = Projectile(x=0.0, y=0.0, target_x=200.0, target_y=0.0, damage=10, speed=400.0, target=target)
    proj.update(0.016)
    assert proj.should_release is True
    assert proj.hit is False


# ---------------------------------------------------------------------------
# 정지 상태 처리
# ---------------------------------------------------------------------------


def test_update_no_movement_when_dead() -> None:
    proj = Projectile(x=0.0, y=0.0, target_x=100.0, target_y=0.0, damage=10, speed=100.0)
    proj.alive = False
    proj.update(1.0)
    assert proj.x == 0.0


def test_update_no_movement_when_already_hit() -> None:
    proj = Projectile(x=50.0, y=0.0, target_x=100.0, target_y=0.0, damage=10, speed=100.0)
    proj.hit = True
    proj.update(1.0)
    assert proj.x == 50.0


# ---------------------------------------------------------------------------
# reset 메서드
# ---------------------------------------------------------------------------


def test_reset_reinitializes_state() -> None:
    proj = Projectile(x=0.0, y=0.0, target_x=100.0, target_y=0.0, damage=10, speed=100.0)
    proj.hit = True
    proj.alive = False
    proj.reset(x=10.0, y=20.0, target_x=200.0, target_y=20.0, damage=25, speed=300.0)
    assert proj.x == 10.0
    assert proj.y == 20.0
    assert proj.damage == 25
    assert proj.hit is False
    assert proj.alive is True
    assert proj.should_release is False
