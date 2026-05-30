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

    ``world`` dict 키:
        enemies: list[Enemy]  — 이동할 적 목록
        waypoints: list[Point] 또는 dict[str, list[Point]]
            단일 경로이면 list, 복수 경로이면 path_id → list 매핑.

    각 enemy의 ``wp_index``(또는 ``waypoint_idx``)가 마지막 웨이포인트에
    도달하면 ``goal_reached=True``로 플래그를 세운다 (외부에서 자원 차감/패배 판정).
    """

    def __init__(self, world: dict) -> None:  # type: ignore[type-arg]
        self.world = world

    def update(self, dt: float, enemies: list | None = None, waypoints: list | None = None) -> None:
        """경로 추종 한 틱.

        Args:
            dt: 경과 시간(초).
            enemies: 이동할 적 목록. None이면 ``self.world['enemies']`` 사용.
            waypoints: 웨이포인트 리스트. None이면 ``self.world['waypoints']`` 사용.
        """
        w = self.world
        enemy_list = enemies if enemies is not None else w.get("enemies", [])
        wp_map = waypoints if waypoints is not None else w.get("waypoints", [])

        for enemy in enemy_list:
            if not enemy.alive:
                continue
            if getattr(enemy, "goal_reached", False):
                continue
            if getattr(enemy, "dying", False):
                continue

            # Issue #61 (DECISION-DL-P5S-001): S1 일점사 기절. 기절 중이면 이동을
            # 정지하고 타이머만 감소시킨다. prev 좌표는 현재 좌표로 동기화해
            # Projectile swept-circle 충돌 판정(정지 타겟)이 정상 동작하게 한다.
            stun = getattr(enemy, "stun_timer", 0.0)
            if stun > 0.0:
                enemy.stun_timer = max(0.0, stun - dt)
                enemy._prev_x = float(enemy.x)
                enemy._prev_y = float(enemy.y)
                continue

            # DECISION-DL-P5P-002 (Issue #44): 이동 직전 좌표 스냅샷.
            # Projectile.update 의 swept-circle 충돌 판정이 이 값을 사용해
            # (prev → cur) dt-segment 를 정확히 평가한다. CombatSystem 이
            # PathingSystem 이후 호출되므로 (prev=이번 틱 이동 전, cur=이동 후).
            enemy._prev_x = float(enemy.x)
            enemy._prev_y = float(enemy.y)

            # 경로 선택: dict이면 path_id로 조회, list이면 직접 사용
            if isinstance(wp_map, dict):
                path_id = getattr(enemy, "path_id", "")
                wps: list[Point] = wp_map.get(path_id, [])
            else:
                wps = wp_map  # type: ignore[assignment]

            if not wps:
                continue

            # wp_index (wp_index와 waypoint_idx 모두 지원)
            idx = getattr(enemy, "wp_index", getattr(enemy, "waypoint_idx", 0))
            speed = float(getattr(enemy, "enemy_def", None) and enemy.enemy_def.speed or 60.0)

            # 남은 dt 안에서 여러 웨이포인트를 통과할 수 있으므로 루프 처리
            remaining_dt = dt
            cur_pos: Point = (enemy.x, enemy.y)
            cur_idx = idx
            done = False

            while remaining_dt > 0 and not done:
                if cur_idx >= len(wps):
                    done = True
                    break
                target_wp = wps[cur_idx]
                dx = target_wp[0] - cur_pos[0]
                dy = target_wp[1] - cur_pos[1]
                dist_to_wp = math.hypot(dx, dy)
                time_to_wp = dist_to_wp / speed if speed > 0 else float("inf")
                if remaining_dt >= time_to_wp:
                    # 이 웨이포인트 도달
                    cur_pos = target_wp
                    remaining_dt -= time_to_wp
                    cur_idx += 1
                    if cur_idx >= len(wps):
                        done = True
                else:
                    # 이 웨이포인트에 도달하지 못함 — 부분 이동
                    new_pos, _reached = step_toward(cur_pos, target_wp, speed, remaining_dt)
                    cur_pos = new_pos
                    remaining_dt = 0

            enemy.x, enemy.y = cur_pos
            # 양쪽 속성 동기화
            if hasattr(enemy, "wp_index"):
                enemy.wp_index = cur_idx
            if hasattr(enemy, "waypoint_idx"):
                enemy.waypoint_idx = cur_idx

            if done:
                enemy.goal_reached = True
                if hasattr(enemy, "reached_castle"):
                    enemy.reached_castle = True
