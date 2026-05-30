"""적 유닛(당군 보병/방패/장수/충차/공성탑).

처치 시 ``dying=True`` → ``fade_tick``으로 ``fade_alpha`` 감소 → ``alive=False``.
잔혹 묘사 없이 회색조 페이드아웃으로 처리 (GDD §5, DECISION-05).

보상값(reward_food, reward_pop, reward_arrows)은 인스턴스 속성으로 보유한다.
CombatSystem이 ``alive==False && _was_dying==True`` 상태를 감지해
``on_enemy_defeated(enemy)`` 콜백을 호출한다.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.entities.entity import Entity

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler
    from src.data.loader import EnemyDef

# 페이드 사망 기본 지속시간 (GDD §9.5 처치 연출 300ms → 완전 사망 고려해 0.6s)
_FADE_DURATION_S = 0.6


class Enemy(Entity):
    """경로를 따라 진군하는 적 유닛.

    Attributes:
        enemy_def: EnemyDef 정의.
        path_id: 따를 경로 id.
        wp_index: 현재 목표 웨이포인트 인덱스.
        reached_castle: 마지막 웨이포인트 도달 여부.
        dying: 사망 페이드 진행 중.
        fade_duration_s: 페이드 총 시간.
        fade_alpha: 현재 투명도 (1.0=불투명, 0.0=완전투명).
        reward_food: 처치 시 곡식 보상.
        reward_pop: 처치 시 인구 회복 (현재 0, 확장 여지).
        reward_arrows: 처치 시 화살 보상.
    """

    fade_duration_s: float = _FADE_DURATION_S

    def __init__(self, x: float, y: float, enemy_def: EnemyDef, path_id: str = "") -> None:
        super().__init__(x, y, hp=enemy_def.hp)
        self.enemy_def = enemy_def
        self.path_id: str = path_id
        self.wp_index: int = 0
        # 하위 호환: 기존 코드가 waypoint_idx를 참조하는 경우
        self.waypoint_idx: int = 0
        self.reached_castle: bool = False
        self.goal_reached: bool = False  # PathingSystem 플래그

        # 사망 페이드
        self.dying: bool = False
        self.fade_alpha: float = 1.0
        self._was_dying: bool = False  # CombatSystem이 보상 콜백 1회 트리거에 사용

        # Issue #61 (DECISION-DL-P5S-001): 양만춘 S1 일점사 기절.
        # stun_timer > 0 이면 PathingSystem 이 이동을 정지시키고 매 틱 감소시킨다.
        self.stun_timer: float = 0.0

        # DECISION-DL-P5P-002 (Issue #44): 이전 틱 좌표 스냅샷.
        # Projectile.update 의 swept-circle 충돌 판정이 (_prev_x, _prev_y) →
        # (x, y) 의 한-틱 segment 를 사용해 fast-moving enemy 통과 케이스 감지.
        # PathingSystem 이 매 틱 시작에 갱신; 초기값은 spawn 좌표.
        self._prev_x: float = float(x)
        self._prev_y: float = float(y)

        # 보상 (GDD §5 gold_drop → food, 나머지는 합리값)
        self.reward_food: int = enemy_def.gold_drop  # gold_drop을 곡식 보상으로 매핑
        self.reward_pop: int = 0
        self.reward_arrows: int = max(1, enemy_def.gold_drop // 4)

    # ------------------------------------------------------------------
    # 데미지 처리
    # ------------------------------------------------------------------

    def take_damage(self, amount: int) -> None:
        """데미지를 받고 hp를 감소. hp <= 0이면 dying=True.

        Args:
            amount: 적용할 데미지 (양수).
        """
        if not self.alive or self.dying:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.dying = True
            self._was_dying = True

    # ------------------------------------------------------------------
    # 페이드 틱
    # ------------------------------------------------------------------

    def fade_tick(self, dt: float) -> None:
        """dying 상태이면 fade_alpha를 감소. 0 이하가 되면 alive=False.

        Args:
            dt: 경과 시간(초).
        """
        if not self.dying:
            return
        self.fade_alpha -= dt / self.fade_duration_s
        if self.fade_alpha <= 0.0:
            self.fade_alpha = 0.0
            self.alive = False

    # ------------------------------------------------------------------
    # Entity 오버라이드
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """패이딩 처리. 이동은 PathingSystem이 담당."""
        self.fade_tick(dt)

    def draw(self, canvas: tk.Canvas, scaler: Scaler) -> None:
        """coords 동기화 + hp 바 (렌더러가 호출)."""
        return
