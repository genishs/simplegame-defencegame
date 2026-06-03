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


# ---------------------------------------------------------------------------
# H2/H6 — EducationSessionState (systems, tk-free)
# ---------------------------------------------------------------------------
def _state() -> Any:
    from src.systems.education_state import EducationSessionState

    return EducationSessionState()


def test_enemy_seen_first_time_only() -> None:
    st = _state()
    assert st.should_show_enemy_banner("tang_soldier") is True
    assert st.mark_enemy_seen("tang_soldier") is True  # 최초
    assert st.mark_enemy_seen("tang_soldier") is False  # 2회째
    assert st.should_show_enemy_banner("tang_soldier") is False


def test_enemy_seen_empty_type_graceful() -> None:
    st = _state()
    assert st.mark_enemy_seen("") is False
    assert st.should_show_enemy_banner("") is False


def test_label_toast_only_for_legend_and_fiction() -> None:
    st = _state()
    assert st.should_show_label_toast("legend") is True
    assert st.should_show_label_toast("fiction") is True
    # fact / fact_adapted 는 토스트 없음.
    assert st.should_show_label_toast("fact") is False
    assert st.should_show_label_toast("fact_adapted") is False
    assert st.mark_label_seen("fact") is False


def test_label_toast_first_time_only() -> None:
    st = _state()
    assert st.mark_label_seen("legend") is True
    assert st.mark_label_seen("legend") is False
    assert st.should_show_label_toast("legend") is False


def test_state_reset() -> None:
    st = _state()
    st.mark_enemy_seen("tang_soldier")
    st.mark_label_seen("legend")
    st.reset()
    assert st.should_show_enemy_banner("tang_soldier") is True
    assert st.should_show_label_toast("legend") is True


# ---------------------------------------------------------------------------
# H2/H6 — BattleScene 통합
# ---------------------------------------------------------------------------
def _banner_texts(scene: Any) -> list[str]:
    texts: list[str] = []
    for _i, (kind, _args, kw) in scene.app.canvas.items.items():
        if kind == "text" and "notice_banner" in (kw.get("tags") or ()):
            texts.append(kw.get("text", ""))
    return texts


def _toast_texts(scene: Any) -> list[str]:
    texts: list[str] = []
    for _i, (kind, _args, kw) in scene.app.canvas.items.items():
        if kind == "text" and "notice_toast" in (kw.get("tags") or ()):
            texts.append(kw.get("text", ""))
    return texts


def test_legend_toast_shown_on_battle_enter_once() -> None:
    """H6: 전투 진입 시 [전승] 토스트 1회. 같은 세션 두 번째 전투에선 안 뜸."""
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene1 = BattleScene(app, stage_id="stage_01")
    scene1.build()
    assert any("전승" in t for t in _toast_texts(scene1))
    # 같은 app(세션) 의 두 번째 전투 — 토스트 재노출 금지.
    # (씬 전환을 모사: 이전 씬 teardown 으로 캔버스 정리 후 새 씬 build.)
    scene1.teardown()
    scene2 = BattleScene(app, stage_id="stage_02")
    scene2.build()
    assert _toast_texts(scene2) == []


def test_enemy_intro_banner_first_spawn_once() -> None:
    """H2: 적 타입 최초 스폰 1회 배너. 2회째 스폰엔 안 뜸."""
    scene = _battle("stage_01")
    scene._spawn_enemy("tang_soldier", scene.stage.paths[0].id)
    first = [t for t in _banner_texts(scene) if "당군 보병" in t]
    assert len(first) == 1
    scene._spawn_enemy("tang_soldier", scene.stage.paths[0].id)
    again = [t for t in _banner_texts(scene) if "당군 보병" in t]
    assert len(again) == 1  # 여전히 1회분만(2회째 추가 없음)


def test_enemy_banner_graceful_for_undefined_type() -> None:
    """R-3: enemies.json 에 없는 적 타입은 배너 생략(크래시 금지)."""
    scene = _battle("stage_05")
    # stage_05 spawn 타입 중 enemies.json 키에 없는 것(예: tang_heavy_infantry).
    scene._spawn_enemy("tang_heavy_infantry", scene.stage.paths[0].id)
    # 크래시 없이 통과 + 배너 텍스트에 미정의 타입 관련 항목 없음.
    assert all("당군 보병" not in t for t in _banner_texts(scene))


def test_notices_auto_dismiss() -> None:
    scene = _battle("stage_01")
    scene._spawn_enemy("tang_soldier", scene.stage.paths[0].id)
    assert scene._notices.active_count >= 1
    # 충분히 긴 시간 경과 → 전부 소멸.
    scene._notices.update(10.0)
    assert scene._notices.active_count == 0


# ---------------------------------------------------------------------------
# H4/H5 — codex_progress (systems, tk-free)
# ---------------------------------------------------------------------------
def test_auto_unlocked_includes_codex_01() -> None:
    from src.data.loader import load_codex
    from src.systems.codex_progress import auto_unlocked_ids

    cards = load_codex()
    auto = auto_unlocked_ids(cards)
    assert "codex_01" in auto  # codex_01 unlock=auto


def test_stage_clear_unlocks_cards() -> None:
    from src.data.loader import load_codex
    from src.systems.codex_progress import cards_unlocked_by_clear

    cards = load_codex()
    # stage 1 클리어 → codex_02(stage_clear,1) + codex_07(양만춘, stage_clear,1).
    s1 = cards_unlocked_by_clear(cards, 1, stars=1)
    assert "codex_02" in s1
    assert "codex_07" in s1
    # stage 5 별3개 전용 카드(codex_13)는 stars<3 이면 미해금.
    s5_low = cards_unlocked_by_clear(cards, 5, stars=1)
    assert "codex_13" not in s5_low
    s5_three = cards_unlocked_by_clear(cards, 5, stars=3)
    assert "codex_13" in s5_three


def test_true_ending_unlocks_card_15() -> None:
    from src.data.loader import load_codex
    from src.systems.codex_progress import cards_unlocked_by_true_ending

    cards = load_codex()
    assert "codex_15" in cards_unlocked_by_true_ending(cards)


def test_compute_progress_counts_and_milestone() -> None:
    from src.data.loader import load_codex
    from src.systems.codex_progress import compute_progress

    cards = load_codex()
    prog = compute_progress(cards, {"codex_01", "codex_07"})
    assert prog.total == 15
    assert prog.unlocked == 2
    # codex_07 은 legend, codex_01 은 fact.
    assert prog.fact == 1
    assert prog.legend == 1
    assert prog.milestone_reached() is None
    # 5장이면 milestone 5.
    five = compute_progress(cards, {c.id for c in cards[:5]})
    assert five.milestone_reached() == 5
    full = compute_progress(cards, {c.id for c in cards})
    assert full.is_complete is True
    assert full.milestone_reached() == 15


def test_save_roundtrip_unlocked_ids(tmp_path: Any) -> None:
    from src.core.save_slot import SaveSlot
    from src.systems.codex_progress import load_unlocked_ids, store_unlocked_ids

    slot = SaveSlot()
    assert load_unlocked_ids(slot) == set()
    store_unlocked_ids(slot, {"codex_02", "codex_01"})
    # to_dict/from_dict 라운드트립으로 영속 유지.
    revived = SaveSlot.from_dict(slot.to_dict())
    assert load_unlocked_ids(revived) == {"codex_01", "codex_02"}


# ---------------------------------------------------------------------------
# H4 — ResultCard 렌더 + BattleScene 통합
# ---------------------------------------------------------------------------
def test_result_card_shows_front_only() -> None:
    from src.data.loader import load_codex
    from src.ui.result_card import ResultCard

    cards = load_codex()
    card = next(c for c in cards if c.id == "codex_07")  # legend
    rc = ResultCard(FakeCanvas(), FakeScaler(), card, on_read=lambda: None, tag="dialog_result")
    rc.show()
    texts = [kw.get("text", "") for (_k, _a, kw) in rc._canvas.items.values()]
    # 제목/요약은 노출되지만 본문(body)은 노출되지 않는다(DECISION-EDU-001).
    assert card.title in texts
    assert card.summary in texts
    assert card.body not in texts
    # 라벨 표기 [전승] 포함.
    assert any("전승" in t for t in texts)


def test_battle_victory_unlocks_and_shows_card(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.setenv("ANSISEONG_HOME", str(tmp_path))
    scene = _battle("stage_01")
    scene._end_battle(victory=True)
    # 결과 카드가 노출되었다.
    assert scene._result_card is not None
    assert scene._result_card.visible is True
    # 세이브에 해금 카드가 영속되었다.
    from src.core.save_slot import load_save_slot
    from src.systems.codex_progress import load_unlocked_ids

    owned = load_unlocked_ids(load_save_slot())
    assert "codex_02" in owned


def test_battle_defeat_shows_no_card(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.setenv("ANSISEONG_HOME", str(tmp_path))
    scene = _battle("stage_01")
    scene._end_battle(victory=False)
    assert scene._result_card is None
