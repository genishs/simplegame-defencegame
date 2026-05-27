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


# ---------------------------------------------------------------------------
# 호밍(추적) 발사체 — Issue #76 / DECISION-DL-P5C-007
# ---------------------------------------------------------------------------


def test_homing_hits_moving_target() -> None:
    """타겟이 발사 후 옆으로 이동해도 호밍 발사체는 결국 명중한다.

    발사 시점 타겟은 (300,0). 매 틱 타겟을 y축으로 60px/s 이동시킨다.
    과거 등속 직선 발사체였다면 처음 조준한 (300,0) 으로만 향해 빗나갔을 것.
    호밍 발사체는 매 틱 재조준하므로 hit=True 에 도달해야 한다.
    """
    target = _DummyEnemy(x=300.0, y=0.0)
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=300.0,
        target_y=0.0,
        damage=10,
        speed=520.0,
        target=target,
        hit_radius=12.0,
    )
    dt = 0.016
    hit = False
    for _ in range(400):  # 최대 ~6.4초 시뮬
        # 타겟이 옆으로 계속 이동 (발사체보다 느림)
        target.y += 60.0 * dt
        proj.update(dt)
        if proj.hit:
            hit = True
            break
    assert hit, "호밍 발사체가 이동하는 타겟을 명중시키지 못함"


def test_homing_reaims_velocity_toward_target() -> None:
    """호밍: 타겟이 이동하면 다음 틱 속도 벡터가 새 타겟 방향으로 갱신된다."""
    target = _DummyEnemy(x=200.0, y=0.0)
    proj = Projectile(
        x=0.0,
        y=0.0,
        target_x=200.0,
        target_y=0.0,
        damage=10,
        speed=400.0,
        target=target,
        hit_radius=12.0,
    )
    # 발사 직후엔 +x 방향 (vy≈0)
    assert abs(proj.vy) < 1e-6
    # 타겟을 아래로 크게 이동시킨 뒤 한 틱 → 속도에 +y 성분이 생겨야 함
    target.y = 300.0
    proj.update(0.016)
    assert proj.vy > 0.0, "호밍 재조준이 타겟 이동을 반영하지 않음"
    # 속력은 보존
    assert abs(math.hypot(proj.vx, proj.vy) - 400.0) < 1e-3


def test_no_homing_without_target_entity() -> None:
    """target 엔티티가 없으면(좌표 고정) 직선 운동을 유지한다 (하위 호환)."""
    proj = Projectile(x=0.0, y=0.0, target_x=200.0, target_y=0.0, damage=10, speed=400.0)
    vy0 = proj.vy
    proj.update(0.016)
    assert proj.vy == vy0  # 재조준 없음
