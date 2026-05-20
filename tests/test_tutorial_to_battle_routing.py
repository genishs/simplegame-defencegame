"""튜토리얼 종료 → stage_01 진입 경로 회귀 가드 — Issue #51.

검수 결함 2호 (v0.4.0-rc.2):
  사용자 보고: "튜토리얼 끝나고 stage01에서 더이상 동작하지 않아"
  종합 증상: BattleScene 부분 렌더 + update 정지 + 입력 차단 frozen.

원인 (DECISION-DL-P4D-003):
  PyInstaller spec 의 ``datas`` 에 ``src/data/`` JSON 자원이 누락되어, .exe
  환경에서 ``load_stage("stage_01")`` 가 FileNotFoundError → ``self.stage =
  None`` → ``BattleScene.update()`` 가 매 tick early return → frozen.
  Issue #49 (튜토리얼 spotlight) fix 와 별개의 결함.

본 테스트는 다음 회귀를 차단한다:
  1. ``src/data/`` 의 stage_*.json / enemies.json / units.json 이 모두 존재.
  2. ``resolve_data_root()`` 가 개발 모드/번들 환경 모두 일관된 경로 반환.
  3. AnsiseongDefense.spec 에 ``src/data`` 항목이 datas 로 등록.
  4. ``TutorialScene._complete_tutorial()`` 가 stage_select 로 라우팅.
  5. stage_select 카드 클릭 → BattleScene 진입 → 첫 update tick 까지 정상.
  6. stage 로드 실패 시 frozen 대신 시각적 에러 placeholder 가 표시됨.
  7. ``app._tick()`` 동일 예외 반복 시 에러 배너가 한 번만 표시됨.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tests.test_battle_scene_flow import FakeApp, FakeCanvas, FakeEventBus, FakeRoot, FakeScaler

# ---------------------------------------------------------------------------
# 1. 데이터 자원 파일 존재 검증
# ---------------------------------------------------------------------------


def test_all_stage_json_files_present() -> None:
    """src/data/stages/stage_01..05.json 5개 모두 존재."""
    from src.core.settings import DATA_ROOT

    stages_dir = DATA_ROOT / "stages"
    assert stages_dir.is_dir(), f"stages 디렉토리 미존재: {stages_dir}"
    for sid in ("stage_01", "stage_02", "stage_03", "stage_04", "stage_05"):
        sp = stages_dir / f"{sid}.json"
        assert sp.is_file(), f"{sid}.json 미존재: {sp}"
        # JSON 파싱도 통과해야 함.
        with open(sp, encoding="utf-8") as f:
            raw = json.load(f)
        assert raw["id"] == sid


def test_enemies_and_units_json_present() -> None:
    """src/data/enemies.json + units.json 존재 + 핵심 키 보유."""
    from src.core.settings import DATA_ROOT

    enemies_path = DATA_ROOT / "enemies.json"
    assert enemies_path.is_file(), f"enemies.json 미존재: {enemies_path}"
    with open(enemies_path, encoding="utf-8") as f:
        raw = json.load(f)
    assert "enemies" in raw
    # stage_01 wave 에서 사용하는 tang_soldier 가 정의되어 있어야 함.
    assert "tang_soldier" in raw["enemies"]

    units_path = DATA_ROOT / "units.json"
    assert units_path.is_file(), f"units.json 미존재: {units_path}"


# ---------------------------------------------------------------------------
# 2. resolve_data_root() / DATA_ROOT 일관성
# ---------------------------------------------------------------------------


def test_resolve_data_root_returns_path_with_stages_subdir_in_dev_mode() -> None:
    """개발 모드(sys._MEIPASS 없음)에서 DATA_ROOT 가 stages/ 하위를 가진다."""
    from src.core.settings import resolve_data_root

    root = resolve_data_root()
    assert (root / "stages").is_dir(), f"DATA_ROOT/stages 미존재: {root}"
    assert (root / "stages" / "stage_01.json").is_file()


# ---------------------------------------------------------------------------
# 3. PyInstaller spec 에 src/data 번들 항목 포함 검증
# ---------------------------------------------------------------------------


def test_pyinstaller_spec_bundles_src_data() -> None:
    """AnsiseongDefense.spec 의 datas 에 src/data 가 번들 대상으로 등록.

    이 회귀 가드가 없으면 사용자가 .exe 빌드를 다시 만들 때마다 결함이
    재발할 수 있다. spec 텍스트 검사로 충분 (정적 분석 수준).
    """
    from src.core.settings import PROJECT_ROOT

    spec_path = PROJECT_ROOT / "AnsiseongDefense.spec"
    assert spec_path.is_file(), "AnsiseongDefense.spec 파일 미존재"
    text = spec_path.read_text(encoding="utf-8")
    # 데이터 디렉토리가 PROJECT_ROOT / "src" / "data" 로 datas 에 append 되어야 함.
    assert "src" in text and "data" in text
    # 명시적 dest 가 "src/data" 또는 "data" 형태로 datas 에 추가되어야 함.
    pattern = re.compile(r'datas\.append\(\s*\(\s*str\(\s*data_dir\s*\)\s*,\s*"src/data"\s*\)\s*\)')
    assert pattern.search(text), (
        "AnsiseongDefense.spec 에 src/data datas append 항목이 없습니다 — " "DECISION-DL-P4D-003 회귀."
    )


# ---------------------------------------------------------------------------
# 4. TutorialScene._complete_tutorial → stage_select 라우팅
# ---------------------------------------------------------------------------


class _RecordingTutorialApp(FakeApp):
    """튜토리얼이 호출하는 goto 를 캡쳐."""

    def __init__(self) -> None:
        super().__init__()
        self.last_goto: str | None = None

    def goto(self, name: str, **kwargs: Any) -> None:  # type: ignore[override]
        self.last_goto = name
        self._goto_calls.append(name)


def test_tutorial_complete_routes_to_stage_select(tmp_path: Path) -> None:
    """단계 8 완료 → stage_select 라우팅. 검수 결함의 직접 차단 라인."""
    from src.scenes.tutorial_scene import TutorialScene

    app = _RecordingTutorialApp()
    scene = TutorialScene(app)
    # save_slot path 오버라이드: 테스트 격리.
    scene.force_set_save_slot_path(tmp_path / "save_slot.json")
    scene.build()
    # 단계 8 까지 강제 진행.
    for s in range(2, 9):
        scene._enter_step(s)
    assert scene.step == 8
    scene._complete_tutorial()
    assert app.last_goto == "stage_select", f"튜토리얼 종료는 stage_select 로 가야 함, 실제={app.last_goto}"


# ---------------------------------------------------------------------------
# 5. Stage_select 카드 클릭 lambda → battle 라우팅 + BattleScene 진입 후 stage 정상 로드
# ---------------------------------------------------------------------------


def test_battle_scene_loads_stage_01_and_runs_first_tick() -> None:
    """BattleScene(stage_id='stage_01').build() 직후 stage 로드 정상 + update tick 진행.

    검수 결함의 핵심: stage=None 이 되면 update() 가 early return → frozen.
    본 테스트는 정상 환경에서 stage 가 None 이 아니고 update 가 시스템을
    호출함을 보장한다.
    """
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id="stage_01")
    scene.build()
    assert scene.stage is not None, "stage_01 로드 실패 — frozen 의 직접 원인"
    assert scene._stage_load_error is None, f"예상 외 로드 에러: {scene._stage_load_error}"
    # wave 가 적어도 1개 로드.
    assert len(scene.wave.waves) >= 1
    # hero 자동 등록 (Phase 3.5 회귀 가드 재확인).
    assert scene.world.get("hero") is not None
    # 첫 tick.
    scene.update(0.016)
    # update 가 early return 하지 않고 시스템들을 굴렸음을 wave.current_wave 진행으로 검증.
    # 첫 wave delay_s=3 이므로 0.016s 만에는 아직 spawn 안 했지만, time_to_next 가 감소.
    assert scene.wave.time_to_next_wave < 3.0


# ---------------------------------------------------------------------------
# 6. Stage 로드 실패 시 frozen 대신 에러 placeholder 표시
# ---------------------------------------------------------------------------


def test_battle_scene_shows_error_placeholder_when_stage_missing() -> None:
    """존재하지 않는 stage_id 진입 시 frozen 대신 에러 텍스트가 placeholder 로 표시.

    DECISION-DL-P4D-004: stage=None 인 상태로 진입할 때 사용자가 "검은 화면"
    + "프로즌" 만 보는 결함을 차단하기 위한 시각적 진단 메시지.
    """
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id="stage_does_not_exist_xx")
    scene.build()
    assert scene.stage is None
    assert scene._stage_load_error is not None
    # placeholder 텍스트가 에러 사유를 포함.
    placeholder_items = [
        v for v in app.canvas.items.values() if v[0] == "text" and "찾을 수 없" in str(v[2].get("text", ""))
    ]
    assert placeholder_items, "stage 로드 실패 시 에러 placeholder 가 캔버스에 그려져야 함"


def test_battle_scene_update_remains_safe_when_stage_missing() -> None:
    """stage=None 이어도 update() 가 예외 없이 종료해 외부 에러 배너 의존이 없음.

    이 분기에서 적/영웅/wave 가 안 도는 것은 정상. 다만 사용자는 placeholder
    텍스트로 사유를 알 수 있다.
    """
    from src.scenes.battle_scene import BattleScene

    app = FakeApp()
    scene = BattleScene(app, stage_id="stage_does_not_exist_xx")
    scene.build()
    # update 가 매 tick 안전하게 early return.
    for _ in range(5):
        scene.update(0.016)
    # 게임오버는 트리거되지 않음 (stage 없으면 조건 평가 자체 skip).
    assert scene._game_over is False


# ---------------------------------------------------------------------------
# 7. App._tick() 반복 예외 → 에러 배너 한 번만 표시
# ---------------------------------------------------------------------------


class _AppHarness:
    """App 의 _tick 동작만 빠르게 테스트하기 위한 경량 하네스 (tk 없이).

    클래스 속성 ``_TICK_ERROR_BANNER_THRESHOLD`` 는 ``App`` 과 동일 값으로
    선언해 ``App._tick`` 본문이 ``self._TICK_ERROR_BANNER_THRESHOLD`` 를 참조해도
    문제없이 동작하게 한다.
    """

    # App 과 동일 임계 (단위 테스트 격리).
    _TICK_ERROR_BANNER_THRESHOLD: int = 3

    def __init__(self, raising_scene: Any) -> None:
        from src.core.logger import get_logger

        self._log = get_logger("test._app_harness")
        self.canvas = FakeCanvas()
        self.scaler = FakeScaler()
        self.events = FakeEventBus()
        self.root = FakeRoot()
        self.current_scene = raising_scene
        # App 의 _tick / _show_tick_error_banner / _clear_tick_error_banner 의
        # 동작만 단위로 재현하기 위해 같은 필드 사양으로 초기화.
        self._tick_error_streak: int = 0
        self._tick_error_signature: str | None = None
        self._tick_error_banner_id: int | None = None

    # App 의 메서드를 그대로 위임 (bound import).
    def _tick(self, dt: float) -> None:
        from src.core.app import App

        # 같은 메서드 본문을 그대로 실행.
        App._tick(self, dt)  # type: ignore[arg-type]

    def _show_tick_error_banner(self, signature: str) -> None:
        from src.core.app import App

        App._show_tick_error_banner(self, signature)  # type: ignore[arg-type]

    def _clear_tick_error_banner(self) -> None:
        from src.core.app import App

        App._clear_tick_error_banner(self)  # type: ignore[arg-type]


class _RaisingScene:
    def __init__(self) -> None:
        self.calls: int = 0

    def update(self, dt: float) -> None:
        self.calls += 1
        raise RuntimeError("simulated tick failure")

    def render(self) -> None:
        pass


def test_app_tick_repeated_exception_emits_banner_once() -> None:
    """DECISION-DL-P4D-005: 동일 예외가 임계 이상 반복되면 에러 배너 1회 표시.

    silent catch 만으로는 사용자가 frozen 으로 인지하는 결함을 보강.
    """
    scene = _RaisingScene()
    harness = _AppHarness(scene)
    # 임계(3) 미만에서는 배너가 안 뜸.
    harness._tick(0.016)
    harness._tick(0.016)
    assert harness._tick_error_banner_id is None
    # 3 회째에 배너.
    harness._tick(0.016)
    assert harness._tick_error_banner_id is not None
    banner_id = harness._tick_error_banner_id
    # 추가 tick 에서도 같은 배너 id 유지(중복 생성 안 함).
    harness._tick(0.016)
    harness._tick(0.016)
    assert harness._tick_error_banner_id == banner_id


def test_app_tick_banner_cleared_after_successful_tick() -> None:
    """예외가 멎고 정상 tick 이 들어오면 streak/배너 리셋."""

    class _ToggleScene:
        def __init__(self) -> None:
            self.fail_until: int = 3
            self.calls: int = 0

        def update(self, dt: float) -> None:
            self.calls += 1
            if self.calls <= self.fail_until:
                raise RuntimeError("temp fail")

        def render(self) -> None:
            pass

    scene = _ToggleScene()
    harness = _AppHarness(scene)
    for _ in range(3):
        harness._tick(0.016)
    assert harness._tick_error_banner_id is not None
    # 4 번째 tick 은 정상.
    harness._tick(0.016)
    assert harness._tick_error_streak == 0
    assert harness._tick_error_signature is None
    assert harness._tick_error_banner_id is None


# ---------------------------------------------------------------------------
# 8. 전체 사슬 — tutorial 완료 → stage_select 카드 → battle → first tick
# ---------------------------------------------------------------------------


def test_full_chain_tutorial_complete_to_battle_first_tick(tmp_path: Path) -> None:
    """튜토리얼 8단계 완료 → stage_select → battle build → first update tick.

    Issue #51 의 사용자 시나리오를 자동화. FakeApp 의 goto 는 씬 교체를
    실제로 하지 않으므로, 본 테스트는 라우팅 호출 순서 + BattleScene
    독립 진입의 정상성을 함께 검증한다.
    """
    from src.scenes.battle_scene import BattleScene
    from src.scenes.tutorial_scene import TutorialScene

    app = _RecordingTutorialApp()

    # ---- 튜토리얼 종료까지.
    tut = TutorialScene(app)
    tut.force_set_save_slot_path(tmp_path / "save_slot.json")
    tut.build()
    for s in range(2, 9):
        tut._enter_step(s)
    tut._complete_tutorial()
    assert app.last_goto == "stage_select"

    # ---- stage_select 카드 클릭은 app.goto("battle") 호출이므로 직접 모방.
    app.goto("battle")
    assert app.last_goto == "battle"

    # ---- BattleScene 진입 (실제 씬 생성).
    bs = BattleScene(app, stage_id="stage_01")
    bs.build()
    assert bs.stage is not None
    assert bs._stage_load_error is None
    # 첫 update tick 이 예외 없이 종료.
    bs.update(0.016)
    bs.update(0.016)
    # 적이 아직 spawn 전이지만, wave system 은 진행 중이어야 한다.
    assert bs.wave.time_to_next_wave < 3.0
