"""웨이포인트 추종 (tk 비의존).

DESIGN: 경로는 ``(x, y)`` 튜플 리스트. 적은 ``waypoint_idx``를 보유하고
시스템은 다음 웨이포인트까지의 단위 벡터 × speed × dt 만큼 이동시킨다.

이 모듈은 ``tkinter``를 import하지 않으므로 pytest 단위 테스트 가능.
EXPECTED: lead가 핵심 함수 + 테스트 / team-member-1이 enemy.update와 결선.
"""
from __future__ import annotations

import math

Point = tuple[float, float]


def step_toward(
    cur: Point,
    target: Point,
    speed: float,
    dt: float,
) -> tuple[Point, bool]:
    """``cur``에서 ``target``으로 ``speed * dt``만큼 이동.

    Returns:
        새 좌표와 "타깃에 도달했는가(True/False)" 플래그.
    """
    dx = target[0] - cur[0]
    dy = target[1] - cur[1]
    dist = math.hypot(dx, dy)
    move = speed * dt
    if dist <= move or dist == 0:
        return target, True
    ratio = move / dist
    return (cur[0] + dx * ratio, cur[1] + dy * ratio), False


def advance_along_path(
    cur: Point,
    waypoints: list[Point] | tuple[Point, ...],
    waypoint_idx: int,
    speed: float,
    dt: float,
) -> tuple[Point, int, bool]:
    """``waypoints``를 따라 한 틱 진군.

    Returns:
        (새 좌표, 새 waypoint_idx, 경로 종료 여부).
        ``waypoint_idx`` 가 ``len(waypoints)``에 도달하면 경로 종료(True).
    """
    if waypoint_idx >= len(waypoints):
        return cur, waypoint_idx, True
    target = waypoints[waypoint_idx]
    new_pos, reached = step_toward(cur, target, speed, dt)
    if reached:
        new_idx = waypoint_idx + 1
        done = new_idx >= len(waypoints)
        return new_pos, new_idx, done
    return new_pos, waypoint_idx, False


class PathingSystem:
    """엔티티 컬렉션의 경로 추종을 일괄 갱신.

    EXPECTED: team-member-1이 ``world['enemies']``를 순회하여 위치/idx 갱신.
    """

    def __init__(self, world: dict) -> None:  # type: ignore[type-arg]
        self.world = world

    def update(self, dt: float) -> None:
        # TODO(team-member-1): enemies에 대해 advance_along_path 호출.
        return
