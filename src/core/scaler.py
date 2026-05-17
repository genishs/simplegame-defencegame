"""베이스(1920x1080) ↔ 스크린 좌표 변환 + letterbox.

DESIGN: DECISION-3.1. 좌표는 ``canvas.scale``, 이미지는 사이즈별 재캐시,
폰트는 별도 계산을 하는 3축 독립 전략. 이 모듈은 그 중 좌표/폰트 축이며
``tkinter`` import 없이 동작해 단위 테스트 가능하다.
EXPECTED: lead가 골격 + 테스트 통과 보장. 추가 폰트 폴백 등은 ui 팀.
"""
from __future__ import annotations

from src.core.settings import BASE_HEIGHT, BASE_WIDTH


class Scaler:
    """1920x1080 베이스 좌표를 현재 캔버스 크기에 매핑."""

    BASE_W: int = BASE_WIDTH
    BASE_H: int = BASE_HEIGHT

    def __init__(self) -> None:
        self.scale: float = 1.0
        self.off_x: float = 0.0
        self.off_y: float = 0.0
        self.canvas_w: int = self.BASE_W
        self.canvas_h: int = self.BASE_H

    def update(self, canvas_w: int, canvas_h: int) -> tuple[float, float]:
        """리사이즈 시 호출. letterbox 중앙 정렬. 이전 스케일 대비 비율을 반환.

        반환값은 ``canvas.scale("all", 0, 0, ratio, ratio)``에 그대로 넘겨
        기존 캔버스 아이템 좌표를 보정하는 용도.
        """
        prev = self.scale or 1.0
        # 0 또는 음수는 방어.
        canvas_w = max(1, int(canvas_w))
        canvas_h = max(1, int(canvas_h))
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h
        self.scale = min(canvas_w / self.BASE_W, canvas_h / self.BASE_H)
        self.off_x = (canvas_w - self.BASE_W * self.scale) / 2.0
        self.off_y = (canvas_h - self.BASE_H * self.scale) / 2.0
        ratio = self.scale / prev if prev else 1.0
        return ratio, ratio

    def to_screen(self, x: float, y: float) -> tuple[float, float]:
        """베이스 좌표 → 스크린 좌표."""
        return self.off_x + x * self.scale, self.off_y + y * self.scale

    def to_base(self, sx: float, sy: float) -> tuple[float, float]:
        """스크린 좌표 → 베이스 좌표."""
        if self.scale == 0:
            return 0.0, 0.0
        return (sx - self.off_x) / self.scale, (sy - self.off_y) / self.scale

    def font_pt(self, base_pt: int) -> int:
        """베이스 폰트 pt → 현재 스케일에 맞춘 정수 pt (최소 8)."""
        return max(8, int(base_pt * self.scale))

    def letterbox_rects(self) -> list[tuple[float, float, float, float]]:
        """검은 띠로 채워야 할 사각형들(상/하/좌/우).

        각 튜플은 ``(x1, y1, x2, y2)`` 스크린 좌표.
        """
        rects: list[tuple[float, float, float, float]] = []
        # 좌측
        if self.off_x > 0:
            rects.append((0, 0, self.off_x, self.canvas_h))
            rects.append((self.canvas_w - self.off_x, 0, self.canvas_w, self.canvas_h))
        # 상하
        if self.off_y > 0:
            rects.append((0, 0, self.canvas_w, self.off_y))
            rects.append((0, self.canvas_h - self.off_y, self.canvas_w, self.canvas_h))
        return rects
