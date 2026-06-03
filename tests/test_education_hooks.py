"""교육 통합(Track A) UI/씬 훅 테스트 (Wave 1~).

DESIGN: docs/15 (스펙) + docs/16 (구현 계획). tk-free fakes (test_battle_scene_flow
의 FakeApp/FakeCanvas/FakeScaler) 를 재사용해 headless 로 검증한다.

커버 대상(점진 확장):
    - H1 캡션 오버레이: 수명/페이드/스킵, BattleScene 진입 시 캡션 생성, 캡션 없으면 생략.
    - H6 라벨 첫 노출 세션 상태(systems, tk-free): 최초 1회만 토스트.
    - H2 적 첫 등장 세션 상태(systems, tk-free): 타입별 최초 1회 + graceful.
"""

from __future__ import annotations

from typing import Any

from tests.test_battle_scene_flow import FakeApp, FakeCanvas, FakeScaler


# ---------------------------------------------------------------------------
# H1 — CaptionOverlay 단위
# ---------------------------------------------------------------------------
def _make_overlay(text: str | None) -> Any:
    from src.ui.caption_overlay import CaptionOverlay

    return CaptionOverlay(FakeCanvas(), FakeScaler(), text, tag="battle")


def test_caption_overlay_builds_when_text_present() -> None:
    ov = _make_overlay("645년 5월, 당군이 요동으로 밀려옵니다.")
    ov.build()
    assert ov.active is True
    assert ov.done is False
    assert len(ov._ids) == 2  # 배경 + 텍스트


def test_caption_overlay_noop_when_text_missing() -> None:
    for empty in (None, "", "   "):
        ov = _make_overlay(empty)
        ov.build()
        assert ov.active is False
        assert ov.done is True
        assert ov._ids == []


def test_caption_overlay_auto_dismiss_after_lifetime() -> None:
    ov = _make_overlay("캡션")
    ov.build()
    total = ov.FADE_IN_S + ov.HOLD_S + ov.FADE_OUT_S
    # 수명 직전까지는 살아 있다.
    ov.update(total - 0.1)
    assert ov.done is False
    # 수명 초과 시 자동 소멸.
    ov.update(0.2)
    assert ov.done is True
    assert ov.active is False


def test_caption_overlay_skip_dismisses() -> None:
    ov = _make_overlay("캡션")
    ov.build()
    ov.dismiss()
    assert ov.done is True
    assert ov.active is False


def test_caption_overlay_fade_steps_monotonic_in_fade_in() -> None:
    ov = _make_overlay("캡션")
    ov.build()
    start = ov._alpha_step()
    ov._elapsed = ov.FADE_IN_S / 2
    mid = ov._alpha_step()
    ov._elapsed = ov.FADE_IN_S + 0.01
    full = ov._alpha_step()
    assert start <= mid <= full


# ---------------------------------------------------------------------------
# H1 — BattleScene 진입 통합
# ---------------------------------------------------------------------------
def _battle(stage_id: str = "stage_01") -> Any:
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id=stage_id)
    scene.build()
    return scene


def test_battle_scene_creates_caption_overlay() -> None:
    scene = _battle("stage_01")
    assert scene._caption_overlay is not None
    assert scene._caption_overlay.active is True


def test_battle_scene_caption_ticks_even_when_paused() -> None:
    scene = _battle("stage_01")
    ov = scene._caption_overlay
    assert ov is not None
    scene._paused = True
    total = ov.FADE_IN_S + ov.HOLD_S + ov.FADE_OUT_S
    scene.update(total + 0.1)  # paused 여도 캡션은 진행
    assert ov.done is True


def test_battle_scene_caption_skips_on_space() -> None:
    scene = _battle("stage_01")
    ov = scene._caption_overlay
    assert ov is not None and ov.active
    scene._on_space(None)
    assert ov.done is True


# ---------------------------------------------------------------------------
# H3 — 유닛 사료 툴팁
# ---------------------------------------------------------------------------
def _tooltip_item(scene: Any) -> dict[str, Any]:
    """현재 툴팁 텍스트 아이템의 merged kwargs 반환."""
    cid = scene._unit_tooltip_text_id
    _kind, _args, kw = scene.app.canvas.items[cid]
    return kw


def test_unit_tooltip_built_hidden_initially() -> None:
    scene = _battle("stage_01")
    assert scene._unit_tooltip_text_id is not None
    assert _tooltip_item(scene)["state"] == "hidden"


def test_unit_tooltip_shows_history_blurb_on_hover() -> None:
    scene = _battle("stage_01")
    # archer 는 history_blurb 가 채워져 있다(units.json).
    scene._show_unit_history_tooltip("archer")
    kw = _tooltip_item(scene)
    assert kw["state"] == "normal"
    assert "활의 강국" in kw["text"]


def test_unit_tooltip_hides_on_leave() -> None:
    scene = _battle("stage_01")
    scene._show_unit_history_tooltip("archer")
    scene._hide_unit_history_tooltip()
    assert _tooltip_item(scene)["state"] == "hidden"


def test_unit_tooltip_graceful_when_no_blurb() -> None:
    scene = _battle("stage_01")
    # blurb 없는 유닛 id (존재하지 않는 키) → 크래시 없이 숨김 유지.
    scene._show_unit_history_tooltip("__nonexistent__")
    assert _tooltip_item(scene)["state"] == "hidden"


def test_every_loaded_unit_has_history_blurb() -> None:
    """QA-EDU-04: 배치 가능한 모든 유닛 툴팁에 사료가 있다(존재 유닛 전수)."""
    scene = _battle("stage_01")
    for uid, udef in scene._units_db.items():
        assert getattr(udef, "history_blurb", None), uid
