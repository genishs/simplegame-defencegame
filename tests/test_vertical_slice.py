"""수직 슬라이스 통합 테스트 — Phase 3.5 / Issue #12.

검증 항목:
- 메뉴 → 스테이지 선택 → 배틀 → 결과 → 엔딩 일련의 씬 전환이 누락 없이 동작.
- BattleScene 진입 시 영웅(Hero) 인스턴스가 world["hero"] 에 자동 등록.
- M키 토글이 영웅 자동 모드 ↔ 수동 모드를 정상 전환.
- stage_05 클리어 시 "다음" 버튼이 ending 으로, 그 외 stage 는 stage_select 로.
- UI 텍스트 SSOT 키 존재 (메뉴/스테이지/배틀/엔딩의 핵심 라벨).

tk 비의존 FakeApp/FakeCanvas 인프라 재사용 (tests/test_battle_scene_flow.py).
"""

from __future__ import annotations

from typing import Any

from tests.test_battle_scene_flow import FakeApp

# ---------------------------------------------------------------------------
# 1. 씬 전환 사슬 — 메뉴 → 스테이지 선택 → 배틀 → 엔딩
# ---------------------------------------------------------------------------


def test_menu_new_game_routes_to_stage_select() -> None:
    """메뉴의 "새 게임" 버튼은 stage_select 로 라우팅 (Issue #12).

    수직 슬라이스 흐름에서 사용자가 stage 1 을 선택할 수 있어야 한다.
    기존(Phase 3.4 이전): "새 게임" → battle 직행.
    Phase 3.5: "새 게임" → stage_select.
    """
    from src.scenes.menu_scene import _BUTTONS

    new_game = next((b for b in _BUTTONS if b[0] == "menu.new_game"), None)
    assert new_game is not None, "menu.new_game 버튼 정의 누락"
    # b = (key, dest, bx, by, bw, bh) — dest 는 두 번째.
    assert new_game[1] == "stage_select", f"menu.new_game 은 stage_select 로 가야 함, 실제={new_game[1]}"


def test_menu_continue_routes_to_stage_select() -> None:
    """이어하기도 stage_select 경유로 일관."""
    from src.scenes.menu_scene import _BUTTONS

    cont = next((b for b in _BUTTONS if b[0] == "menu.continue"), None)
    assert cont is not None
    assert cont[1] == "stage_select"


def test_menu_quit_button_present() -> None:
    """메뉴에 종료(__quit__) 버튼이 있어야 사용자가 정상 종료할 수 있다."""
    from src.scenes.menu_scene import _BUTTONS

    quit_btn = next((b for b in _BUTTONS if b[0] == "menu.quit"), None)
    assert quit_btn is not None
    assert quit_btn[1] == "__quit__"


def test_stage_select_lists_all_five_stages() -> None:
    """스테이지 선택 씬에 stage_01~stage_05 5종이 모두 노출된다."""
    from src.scenes.stage_select_scene import _STAGES

    ids = {s["id"] for s in _STAGES}
    assert ids == {"stage_01", "stage_02", "stage_03", "stage_04", "stage_05"}


# ---------------------------------------------------------------------------
# 2. BattleScene 진입 시 hero 자동 등록 (DECISION-DL-P3-5-003)
# ---------------------------------------------------------------------------


def test_battle_scene_auto_creates_hero_on_build() -> None:
    """build() 직후 world["hero"] 가 Hero 인스턴스로 채워진다."""
    from src.entities.hero import Hero
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id="stage_01")
    scene.build()
    hero = scene.world.get("hero")
    assert hero is not None, "battle 진입 시 hero 가 자동 생성되어야 함"
    assert isinstance(hero, Hero)
    # 기본 hp/공격 능력치가 양수.
    assert hero.hp > 0
    assert hero.max_hp > 0


def test_battle_scene_hero_spawn_uses_build_zone() -> None:
    """build_zone 이 정의된 stage 에서는 hero 좌표가 zone 영역 내부."""
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id="stage_01")
    scene.build()

    hero = scene.world["hero"]
    assert scene.stage is not None
    zone = scene.stage.build_zones[0]
    # zone 중심 부근에 있어야 함.
    expected_x = float(zone["x"]) + float(zone["w"]) / 2.0
    expected_y = float(zone["y"]) + float(zone["h"]) / 2.0
    assert abs(hero.x - expected_x) < 1e-6
    assert abs(hero.y - expected_y) < 1e-6


def test_battle_scene_compute_hero_spawn_fallback_center() -> None:
    """stage 가 None 인 비정상 경로에서도 hero 좌표 헬퍼가 화면 중앙을 반환."""
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id="stage_01")
    scene.stage = None
    x, y = scene._compute_hero_spawn_xy()
    assert x == 960.0
    assert y == 540.0


# ---------------------------------------------------------------------------
# 3. M키 영웅 모드 토글 (자동 ↔ 수동) — 수직 슬라이스 회귀 가드
# ---------------------------------------------------------------------------


def test_m_key_round_trip_preserves_auto_default() -> None:
    """수직 슬라이스 사양: 영웅은 기본이 자동(False), M키 토글로 수동(True)."""
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id="stage_01")
    scene.build()
    assert scene._hero_direct_mode is False, "기본 모드는 자동"

    scene._on_m_key(None)
    assert scene._hero_direct_mode is True

    scene._on_m_key(None)
    assert scene._hero_direct_mode is False


# ---------------------------------------------------------------------------
# 4. End-of-battle 라우팅 — stage_05 승리 → ending, 그 외 → stage_select
# ---------------------------------------------------------------------------


class _RecordingApp(FakeApp):
    """ResultDialog 콜백에서 호출되는 goto 를 캡쳐하기 위한 mock."""

    def __init__(self) -> None:
        super().__init__()
        self.last_goto: str | None = None

    def goto(self, name: str, **kwargs: Any) -> None:  # type: ignore[override]
        self.last_goto = name
        self._goto_calls.append(name)


def _trigger_victory(scene: Any) -> None:
    """승리 조건을 강제 발화."""
    scene.wave.all_clear = True
    scene.world["enemies"] = []
    scene.world["lives"] = 20
    scene.world["goals_reached"] = 0
    scene._check_end_conditions()


def test_battle_victory_routes_to_stage_select_when_not_final_stage() -> None:
    """stage_01 클리어 시 "다음" 버튼은 stage_select 로 이동."""
    from src.scenes.battle_scene import BattleScene

    app = _RecordingApp()
    scene = BattleScene(app, stage_id="stage_01")
    scene.build()

    _trigger_victory(scene)
    assert scene._game_over is True
    assert scene._result_dialog is not None

    # 다음 버튼 콜백을 직접 호출 (UI 클릭 시뮬).
    scene._result_dialog._on_next()
    assert app.last_goto == "stage_select"


def test_battle_victory_routes_to_ending_on_final_stage() -> None:
    """stage_05 클리어 시 "다음" 버튼은 ending 으로 이동 (수직 슬라이스 종결)."""
    from src.scenes.battle_scene import BattleScene

    app = _RecordingApp()
    scene = BattleScene(app, stage_id="stage_05")
    scene.build()

    _trigger_victory(scene)
    assert scene._game_over is True
    assert scene._result_dialog is not None

    scene._result_dialog._on_next()
    assert app.last_goto == "ending"


def test_battle_defeat_routes_to_stage_select() -> None:
    """패배 시 다음/재도전/메뉴 모두 stage_select 로 회귀."""
    from src.scenes.battle_scene import BattleScene

    app = _RecordingApp()
    scene = BattleScene(app, stage_id="stage_01")
    scene.build()

    # 패배 강제: goals_reached >= lives.
    scene.world["goals_reached"] = 100
    scene.world["lives"] = 20
    scene._check_end_conditions()
    assert scene._game_over is True

    scene._result_dialog._on_next()
    assert app.last_goto == "stage_select"
    scene._result_dialog._on_menu()
    assert app.last_goto == "stage_select"


# ---------------------------------------------------------------------------
# 5. UI 문자열 SSOT 키 검증 — 메뉴/스테이지/배틀/엔딩
# ---------------------------------------------------------------------------


def test_menu_strings_have_korean_labels() -> None:
    """메뉴 _STRINGS 에 핵심 라벨이 한국어로 정의되어 있다."""
    from src.scenes.menu_scene import _STRINGS

    required = [
        "title.game_title",
        "menu.new_game",
        "menu.stage_select",
        "menu.quit",
    ]
    for key in required:
        assert key in _STRINGS, f"menu_scene._STRINGS missing key: {key}"
        assert _STRINGS[key], f"menu_scene._STRINGS empty value for {key}"


def test_stage_select_strings_present() -> None:
    """스테이지 선택 씬의 핵심 라벨 SSOT 키가 정의되어 있다."""
    from src.scenes.stage_select_scene import _STRINGS

    for key in ("stage_select.title", "stage_select.back", "stage_select.play"):
        assert key in _STRINGS
        assert _STRINGS[key]


def test_battle_scene_strings_present() -> None:
    """battle_scene 의 hero manual mode + placeholder 키가 SSOT 에 등록되어 있다."""
    from src.scenes.battle_scene import _UI_STRINGS_DEFAULT

    for key in (
        "hero.manual_mode.on",
        "hero.manual_mode.off",
        "battle.placeholder.intro",
    ):
        assert key in _UI_STRINGS_DEFAULT
        assert _UI_STRINGS_DEFAULT[key]


def test_ending_scene_panels_cover_all_required_beats() -> None:
    """엔딩 8 패널 (최소 사실/전승/픽션 라벨 보존)."""
    from src.scenes.ending_scene import _PANELS

    assert len(_PANELS) >= 8
    # 마지막 컷 + 피날레가 정의되어 있어야 메뉴 복귀 흐름이 완결.
    has_last_cut = any(p.get("is_last_cut") for p in _PANELS)
    has_finale = any(p.get("is_finale") for p in _PANELS)
    assert has_last_cut, "엔딩에 is_last_cut 패널 필요 (DECISION-E03)"
    assert has_finale, "엔딩에 is_finale 패널 필요 (메뉴 복귀)"


# ---------------------------------------------------------------------------
# 6. main.py 씬 등록 검증 — 4개 씬 등록 누락 방지
# Phase 4 (Issue #26): "tutorial" 씬이 합류해 총 5개로 확장. 본 회귀는 누락 방지가
# 목적이므로 핵심 4 + tutorial 모두 등록되었는지 검증한다.
# ---------------------------------------------------------------------------


def test_main_registers_all_four_scenes() -> None:
    """main._register_scenes 가 menu/stage_select/battle/ending(+tutorial) 씬을 모두 등록.

    실제 Tk 없이 호출하기 위해 register_scene 만 검증하는 fake App 사용.
    """
    from src.main import _register_scenes

    recorded: dict[str, Any] = {}

    class _FakeApp:
        def register_scene(self, name: str, factory: Any) -> None:
            recorded[name] = factory

    _register_scenes(_FakeApp())  # type: ignore[arg-type]
    # 핵심 4 + Phase 4 합류한 tutorial.
    assert {"menu", "stage_select", "battle", "ending", "tutorial"}.issubset(set(recorded.keys()))


# ---------------------------------------------------------------------------
# 7. Stage 1 전 wave playable — wave 누적 완주 가능 여부 회귀 가드
# ---------------------------------------------------------------------------


def test_stage_01_all_waves_loadable() -> None:
    """Stage 1 의 모든 wave 가 WaveSystem 에 로드되고 spawn 가능."""
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id="stage_01")
    scene.build()

    assert scene.stage is not None
    assert len(scene.stage.waves) >= 1
    # WaveSystem 에도 동일 개수가 로드.
    assert len(scene.wave.waves) == len(scene.stage.waves)


def test_stage_01_force_advance_through_waves() -> None:
    """force_next() 로 모든 wave 를 진행시켜도 예외 없음."""
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id="stage_01")
    scene.build()
    assert scene.stage is not None

    total = len(scene.stage.waves)
    for _ in range(total + 2):  # 마지막 이후도 안전하게 호출.
        scene.wave.force_next()
        scene.update(0.05)
    # 예외 없이 통과하면 OK. all_clear 플래그 또는 current_wave 가 진행됨.
    assert scene.wave.current_wave >= 1
