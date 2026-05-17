"""Pathing 단위 테스트 (tk 비의존)."""
from __future__ import annotations

import math

from src.systems.pathing import advance_along_path, step_toward


def test_step_toward_partial_move() -> None:
    new_pos, reached = step_toward((0.0, 0.0), (10.0, 0.0), speed=5.0, dt=1.0)
    assert new_pos == (5.0, 0.0)
    assert reached is False


def test_step_toward_reaches_target() -> None:
    new_pos, reached = step_toward((0.0, 0.0), (3.0, 4.0), speed=10.0, dt=1.0)
    # 거리 5 < 10*1 → 타깃에 정확히 도착.
    assert new_pos == (3.0, 4.0)
    assert reached is True


def test_step_toward_zero_distance() -> None:
    new_pos, reached = step_toward((1.0, 1.0), (1.0, 1.0), speed=10.0, dt=1.0)
    assert new_pos == (1.0, 1.0)
    assert reached is True


def test_advance_along_path_progress() -> None:
    waypoints = [(10.0, 0.0), (10.0, 10.0)]
    # 첫 웨이포인트로 정확히 이동: 10 거리, speed=10, dt=1.
    pos, idx, done = advance_along_path((0.0, 0.0), waypoints, 0, speed=10.0, dt=1.0)
    assert pos == (10.0, 0.0)
    assert idx == 1
    assert done is False
    # 두 번째 웨이포인트로 이동 후 경로 종료.
    pos2, idx2, done2 = advance_along_path(pos, waypoints, idx, speed=10.0, dt=1.0)
    assert pos2 == (10.0, 10.0)
    assert idx2 == 2
    assert done2 is True


def test_advance_already_done() -> None:
    waypoints = [(10.0, 0.0)]
    pos, idx, done = advance_along_path((10.0, 0.0), waypoints, 1, speed=5.0, dt=1.0)
    assert done is True
    assert pos == (10.0, 0.0)
    assert idx == 1


def test_diagonal_movement_unit_vector() -> None:
    # 대각선 (1,1) 방향 7.07 거리, speed=√2 * 1 → 1 만큼 이동해 (1,1) 위치 도달해야 함.
    new_pos, reached = step_toward(
        (0.0, 0.0), (10.0, 10.0), speed=math.sqrt(2.0), dt=1.0
    )
    assert reached is False
    assert abs(new_pos[0] - 1.0) < 1e-9
    assert abs(new_pos[1] - 1.0) < 1e-9
