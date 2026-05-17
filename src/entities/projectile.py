"""발사체(화살/돌).

등속 직선 운동으로 타겟을 향해 이동한다.
타겟까지 거리 < hit_radius이면 ``hit=True``.
타겟이 dying이면 fly-through 후 ``should_release=True``로 자동 회수.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler

# 명중 판정 기본 반경 (px)
_DEFAULT_HIT_RADIUS = 12.0


class Projectile(Entity):
    """발사체.

    Attributes:
        vx, vy: 속도 벡터(px/s).
        damage: 명중 시 적용 데미지.
        hit_radius: 명중 판정 반경(px).
        hit: 타겟 명중 플래그 (CombatSystem이 읽고 처리).
        should_release: 풀에 반환해야 할 때 True (타겟 dying 등).
        target: 추적 대상 엔티티 (optional).
    """

    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        target_x: float = 0.0,
        target_y: float = 0.0,
        damage: int = 10,
        speed: float = 400.0,
        hit_radius: float = _DEFAULT_HIT_RADIUS,
        target: Any = None,
    ) -> None:
        super().__init__(x, y, hp=1)
        self.damage = damage
        self.speed = speed
        self.hit_radius = hit_radius
        self.target: Any = target
        self.hit: bool = False
        self.should_release: bool = False

        # 속도 벡터 계산
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = dx / dist * speed
            self.vy = dy / dist * speed
        else:
            self.vx = 0.0
            self.vy = 0.0

        # 발사 시 타겟 좌표 스냅샷 (target이 없으면 이 좌표로 명중 판정)
        self._target_x = target_x
        self._target_y = target_y

    # ------------------------------------------------------------------
    # 업데이트
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """등속 직선 이동 + 명중 판정.

        타겟 엔티티가 있으면 그 현재 좌표로, 없으면 발사 시 좌표 스냅샷으로
        거리를 계산한다. 한 틱에 타겟을 통과할 수 있으므로 이동 전후의 최소
        거리를 기준으로 판정한다.

        Args:
            dt: 경과 시간(초).
        """
        if not self.alive or self.hit or self.should_release:
            return

        # 타겟이 dying 상태이면 fly-through → should_release
        if self.target is not None and getattr(self.target, "dying", False):
            self.should_release = True
            return

        # 명중 좌표 결정 (이동 전)
        if self.target is not None:
            tx = self.target.x
            ty = self.target.y
        else:
            tx = self._target_x
            ty = self._target_y

        # 이동 전 거리 확인
        dist_before = math.hypot(tx - self.x, ty - self.y)
        if dist_before < self.hit_radius:
            self.hit = True
            return

        # 이동 전 위치 저장
        old_x, old_y = self.x, self.y

        # 이동
        self.x += self.vx * dt
        self.y += self.vy * dt

        # 이동 후 거리 확인
        dist_after = math.hypot(tx - self.x, ty - self.y)
        if dist_after < self.hit_radius:
            self.hit = True
            return

        # 통과 감지: 이동 선분 상 타겟의 최근접 거리를 계산
        # 선분 [old → new] 위의 점 P = old + t*(new-old), t in [0,1]
        seg_dx = self.x - old_x
        seg_dy = self.y - old_y
        seg_len_sq = seg_dx * seg_dx + seg_dy * seg_dy
        if seg_len_sq > 0:
            t = ((tx - old_x) * seg_dx + (ty - old_y) * seg_dy) / seg_len_sq
            t = max(0.0, min(1.0, t))
            closest_x = old_x + t * seg_dx
            closest_y = old_y + t * seg_dy
            closest_dist = math.hypot(tx - closest_x, ty - closest_y)
            if closest_dist < self.hit_radius:
                self.hit = True

    # ------------------------------------------------------------------
    # 초기화 (풀에서 재사용 시)
    # ------------------------------------------------------------------

    def reset(
        self,
        x: float,
        y: float,
        target_x: float,
        target_y: float,
        damage: int,
        speed: float,
        target: Any = None,
        hit_radius: float = _DEFAULT_HIT_RADIUS,
    ) -> None:
        """풀에서 재사용할 때 상태 초기화."""
        self.x = float(x)
        self.y = float(y)
        self.damage = damage
        self.speed = speed
        self.hit_radius = hit_radius
        self.target = target
        self.hit = False
        self.should_release = False
        self.alive = True
        self._target_x = target_x
        self._target_y = target_y

        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = dx / dist * speed
            self.vy = dy / dist * speed
        else:
            self.vx = 0.0
            self.vy = 0.0

    # ------------------------------------------------------------------
    # Entity 오버라이드
    # ------------------------------------------------------------------

    def draw(self, canvas: tk.Canvas, scaler: Scaler) -> None:
        """coords 갱신 (렌더러가 호출)."""
        return
