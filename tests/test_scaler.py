"""Scaler 단위 테스트 (tk 비의존)."""
from __future__ import annotations

from src.core.scaler import Scaler


def test_default_identity() -> None:
    s = Scaler()
    s.update(Scaler.BASE_W, Scaler.BASE_H)
    assert s.scale == 1.0
    assert s.off_x == 0.0 and s.off_y == 0.0
    assert s.to_screen(0, 0) == (0.0, 0.0)
    assert s.to_screen(1920, 1080) == (1920.0, 1080.0)


def test_letterbox_centers_canvas_when_wider() -> None:
    s = Scaler()
    s.update(2400, 1080)  # 16:9보다 가로가 더 김 → 좌우 띠.
    assert s.off_x > 0
    assert s.off_y == 0
    rects = s.letterbox_rects()
    # 좌측 + 우측 두 개의 검은 띠가 생긴다.
    assert len(rects) == 2


def test_letterbox_when_taller() -> None:
    s = Scaler()
    s.update(1920, 1440)  # 세로가 더 김 → 상하 띠.
    assert s.off_x == 0
    assert s.off_y > 0


def test_to_screen_and_back() -> None:
    s = Scaler()
    s.update(1280, 720)  # 비율 동일, scale=2/3.
    bx, by = 960.0, 540.0
    sx, sy = s.to_screen(bx, by)
    rx, ry = s.to_base(sx, sy)
    assert abs(rx - bx) < 1e-6
    assert abs(ry - by) < 1e-6


def test_font_pt_minimum_8() -> None:
    s = Scaler()
    s.update(100, 100)  # 매우 작은 캔버스 → scale 매우 작음.
    assert s.font_pt(10) >= 8


def test_update_returns_ratio() -> None:
    s = Scaler()
    s.update(1920, 1080)
    rx, ry = s.update(960, 540)  # 절반.
    assert abs(rx - 0.5) < 1e-6
    assert abs(ry - 0.5) < 1e-6
