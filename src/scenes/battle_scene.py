"""전투 씬 — 게임의 코어 (SCN-05).

DESIGN:
- 단일 캔버스 + World 딕셔너리 + 시스템 오케스트레이션.
- update 순서: WaveSystem → PathingSystem → CombatSystem → HUD.
- 패배 조건: hero hp<=0 OR enemy.goal_reached 누적 >= lives
  (DECISION-DL-P5C-005, Issue #62 — BattleScene._apply_castle_breaches 가
  goal_reached/reached_castle 플래그를 world['goals_reached'] 로 변환).
- 승리 조건: WaveSystem.all_clear AND len(enemies alive)==0.
- Esc/Space → PauseDialog show.
- M키 = 영웅 직접 조작 모드 토글 (OPEN-D-201, Issue #4).
- spawn_enemy: stage.paths 의 waypoint 시퀀스를 world['waypoints']에
  ``dict[path_id, list[Point]]`` 로 주입하고, EnemyDef 를 들고 Enemy 인스턴스를
  생성 (Issue #1, DECISION-DL-P3-3-004/005/006).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.core.fonts import family_bold as _family_bold
from src.core.fonts import family_regular as _family_regular
from src.core.logger import get_logger
from src.data.loader import EnemyDef, StageDef, UnitDef, load_enemies, load_stage, load_units
from src.scenes.base_scene import BaseScene
from src.systems.combat import CombatSystem
from src.systems.economy import EconomySystem
from src.systems.pathing import PathingSystem
from src.systems.wave import WaveSystem
from src.ui.dialog import PauseDialog, ResultDialog
from src.ui.hud import HUD

if TYPE_CHECKING:
    from src.core.app import App

# Issue #4 / DECISION-DL-P3-3-001: 영웅 수동 모드에서 사용할 키 매핑.
# 화살표와 WASD 동시 지원으로 접근성과 키보드 레이아웃 호환성 확보.
_HERO_DIR_KEYS: dict[str, tuple[float, float]] = {
    # 화살표
    "Up": (0.0, -1.0),
    "Down": (0.0, 1.0),
    "Left": (-1.0, 0.0),
    "Right": (1.0, 0.0),
    # WASD (대문자/소문자 모두)
    "w": (0.0, -1.0),
    "s": (0.0, 1.0),
    "a": (-1.0, 0.0),
    "d": (1.0, 0.0),
    "W": (0.0, -1.0),
    "S": (0.0, 1.0),
    "A": (-1.0, 0.0),
    "D": (1.0, 0.0),
}

# UI 문자열 (docs/story/08_ui_strings.md §3.4 — DECISION-DL-P3-3-007 / P3-5-005)
_UI_STRINGS_DEFAULT: dict[str, str] = {
    "hero.manual_mode.on": "직접 조작 모드 ON (WASD/방향키 이동)",
    "hero.manual_mode.off": "직접 조작 모드 OFF",
    # Issue #12 — 배틀 씬 진입 안내 텍스트도 SSOT 키 사용.
    "battle.placeholder.intro": (
        "전투 — {stage_id}\n웨이브: {waves}\n" "ESC/Space = 일시정지 | M = 직접조작 모드"
    ),
    # Issue #56 (DECISION-DL-P4D-008): 배치 UI 안내.
    "battle.placement.hint_idle": "아래에서 유닛을 골라 녹색 칸을 클릭하시오",
    "battle.placement.hint_selected": "녹색 칸을 클릭해 {unit_name}을(를) 배치하시오",
    "battle.placement.insufficient_food": "곡식이 부족합니다 ({need} 필요)",
    "battle.placement.zone_taken": "이미 유닛이 배치된 칸입니다",
}


class BattleScene(BaseScene):
    """전투 메인 씬.

    World 컨테이너는 ``self.world`` 딕셔너리: 시스템 간 공유되는 단순 가방.
    """

    SCENE_TAG = "battle"

    def __init__(self, app: App, stage_id: str = "stage_01") -> None:
        super().__init__(app)
        self._log = get_logger(__name__)
        self.stage_id = stage_id
        self.stage: StageDef | None = None
        # path_id → list[(x, y)] 매핑. PathingSystem 이 직접 조회.
        self._waypoints_by_path: dict[str, list[tuple[float, float]]] = {}
        # enemy_type id → EnemyDef. spawn 시 lookup.
        self._enemy_defs: dict[str, EnemyDef] = {}

        # ----- World 컨테이너 -------------------------------------------------
        self.world: dict[str, Any] = {
            "enemies": [],
            "allies": [],
            "projectiles": [],
            "effects": [],
            "hero": None,
            "gold": 0,
            "food": 0,
            "pop": 0,
            "arrows": 100,
            "population": 0,
            "lives": 0,
            "goals_reached": 0,  # enemy가 목표 도달한 누적 횟수
            "events": app.events,
            "spawn_enemy": self._spawn_enemy,
            # PathingSystem 이 사용. dict[path_id → waypoints] 형태.
            "waypoints": self._waypoints_by_path,
        }

        # 시스템
        self.economy = EconomySystem(self.world)
        self.wave = WaveSystem(self.world)
        self.combat = CombatSystem(self.world)
        self.pathing = PathingSystem(self.world)

        # HUD / 다이얼로그
        self.hud = HUD()
        self._pause_dialog: PauseDialog | None = None
        self._result_dialog: ResultDialog | None = None

        # 상태 플래그
        self._paused: bool = False
        self._game_over: bool = False
        # M키 토글 (OPEN-D-201, Issue #4). True 이면 자동 AI 정지 + 방향키/WASD 이동.
        self._hero_direct_mode: bool = False
        # 매 update() 에서 누적된 입력 방향 (한 틱 1회 이동에 사용).
        self._hero_move_dir: tuple[float, float] = (0.0, 0.0)

        self._placeholder_id: int | None = None
        # 직접조작 모드 상태 표시 캔버스 아이템 (DECISION-DL-P3-3-002).
        self._manual_mode_label_id: int | None = None
        # Issue #29 / DECISION-AUDIO-012: 웨이브 시작 SFX 트리거 추적.
        self._last_wave_index: int = -1

        # DECISION-DL-P4D-006 (Issue #53): render() 가 생성한 entity canvas id
        # 집합. 다음 틱에 world 에서 빠진 엔티티의 캔버스 아이템을 정리하기 위해
        # 추적한다. teardown 은 ``self._tag`` 로 일괄 삭제하므로 별도 정리 불필요.
        self._known_canvas_items: set[int] = set()

        # DECISION-DL-P4D-008 (Issue #56): 유닛 배치 UI 상태.
        # - _units_db: 가용 유닛 사전 (data/units.json)
        # - _selected_unit_id: 현재 선택된 유닛 id (배치 대기). None 이면 선택 없음.
        # - _build_zone_occupants: index → Ally 매핑 (한 zone 당 1체).
        # - _placement_hint_id: 하단 안내 텍스트 canvas id.
        # - _placement_btn_ids: 좌측 유닛 선택 버튼 (rect, label, cost_text, key).
        # - _build_zone_canvas_ids: zone index → canvas rectangle id.
        self._units_db: dict[str, UnitDef] = {}
        self._selected_unit_id: str | None = None
        self._build_zone_occupants: dict[int, Any] = {}
        self._placement_hint_id: int | None = None
        self._placement_btn_state: dict[str, dict[str, Any]] = {}
        self._build_zone_canvas_ids: dict[int, int] = {}

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # 스테이지 → BGM 매핑 (Phase 5.1, Issue #30)
    # ------------------------------------------------------------------
    _STAGE_BGM: dict[str, str] = {
        "stage_01": "bgm.stage_01_02",
        "stage_02": "bgm.stage_01_02",
        "stage_03": "bgm.stage_03_04",
        "stage_04": "bgm.stage_03_04",
        "stage_05": "bgm.stage_05",
    }

    def build(self) -> None:
        # BGM — 스테이지별 BGM 재생 (Phase 5.1, Issue #30)
        # 스테이지 ID에 해당하는 BGM 식별자 탐색. 매핑 없으면 bgm.stage_01_02 기본.
        bgm_name = self._STAGE_BGM.get(self.stage_id, "bgm.stage_01_02")
        self.app.sound.play_bgm(bgm_name, loop=True, fade_in=1.0)

        canvas = self.app.canvas
        scaler = self.app.scaler
        w = canvas.winfo_width() or scaler.canvas_w
        h = canvas.winfo_height() or scaler.canvas_h

        # 스테이지 데이터 로드
        # DECISION-DL-P4D-004 (Issue #51): 데이터 로드 실패 사유를 보존해 사용자
        # 가 frozen 화면 대신 명확한 에러 메시지를 볼 수 있게 한다. .exe 환경에서
        # JSON 자원 번들 누락(DECISION-DL-P4D-003 의 spec 수정 전 빌드)이 가장
        # 흔한 실패 시나리오. 메시지에는 stage_id 와 검색한 DATA_ROOT 가 포함된다.
        self._stage_load_error: str | None = None
        try:
            self.stage = load_stage(self.stage_id)
        except FileNotFoundError as exc:
            self._log.warning("stage file missing: %s (%s)", self.stage_id, exc)
            self.stage = None
            self._stage_load_error = (
                f"스테이지 데이터를 찾을 수 없습니다: {self.stage_id}\n" f"경로: {exc.filename or exc}"
            )
        except Exception as exc:  # noqa: BLE001
            self._log.exception("stage load failed: %s", self.stage_id)
            self.stage = None
            self._stage_load_error = (
                f"스테이지 로드 중 오류가 발생했습니다: {self.stage_id}\n" f"{type(exc).__name__}: {exc}"
            )

        # 적 정의 데이터 로드 (Issue #1, DECISION-DL-P3-3-006).
        # 누락된 enemies.json 은 치명적이지 않으므로 경고만 남기고 빈 맵 유지.
        try:
            self._enemy_defs = load_enemies()
        except (FileNotFoundError, OSError) as exc:
            self._log.warning("enemies.json load failed: %s", exc)
            self._enemy_defs = {}

        # 유닛 정의 데이터 로드 (Issue #56, DECISION-DL-P4D-008).
        try:
            self._units_db = load_units()
        except (FileNotFoundError, OSError) as exc:
            self._log.warning("units.json load failed: %s", exc)
            self._units_db = {}

        # 배경
        canvas.create_rectangle(0, 0, w, h, fill="#0c1410", outline="", tags=(self._tag, "bg"))

        # 경로 / 빌드존
        if self.stage is not None:
            self._draw_paths()
            self._populate_waypoints()
            self._draw_build_zones()
            self.world["gold"] = self.stage.starting_gold
            self.world["food"] = self.stage.starting_gold
            self.world["pop"] = self.stage.starting_population
            self.world["population"] = self.stage.starting_population
            self.world["lives"] = self.stage.lives
            # Issue #43 / DECISION-DL-P5P-001: paths 컨텍스트 주입으로 보스 spawn fallback 안정화.
            self.wave.load(self.stage.waves, paths=self.stage.paths)

        # 영웅(양만춘) 생성 — 수직 슬라이스 (Issue #12, DECISION-DL-P3-5-003).
        # build_zones 평균 좌표 부근 또는 화면 중앙에 스폰. 자동 AI 작동.
        # M키 토글 시 _hero_direct_mode 가 True 가 되어 수동 이동 처리.
        if self.world.get("hero") is None:
            try:
                from src.entities.hero import Hero

                hero_x, hero_y = self._compute_hero_spawn_xy()
                self.world["hero"] = Hero(x=hero_x, y=hero_y)
                self._log.debug(
                    "hero spawned at (%.1f, %.1f) stage=%s",
                    hero_x,
                    hero_y,
                    self.stage_id,
                )
            except Exception as exc:  # noqa: BLE001
                self._log.warning("hero spawn failed: %s", exc)

        # HUD 초기화 (상단 바 + 영웅 패널)
        self.hud.build(
            canvas,
            scaler,
            on_pause_click=self._toggle_pause,
        )

        # 전투 진입 안내 텍스트 (Issue #12, DECISION-DL-P3-5-005)
        # DECISION-DL-P4D-004: stage 로드 실패 시 frozen 대신 사용자에게 사유 표시.
        if self._stage_load_error is not None:
            placeholder_text = (
                f"⚠ {self._stage_load_error}\n\n"
                f"메인 메뉴로 돌아가려면 ESC 또는 일시정지 메뉴를 사용하시오."
            )
            placeholder_fill = "#ff8a6a"
        else:
            waves_count = len(self.stage.waves) if self.stage else 0
            placeholder_text = _UI_STRINGS_DEFAULT["battle.placeholder.intro"].format(
                stage_id=self.stage_id,
                waves=waves_count,
            )
            placeholder_fill = "#e0d0a0"
        self._placeholder_id = canvas.create_text(
            w / 2,
            h / 2,
            text=placeholder_text,
            fill=placeholder_fill,
            font=(_family_regular(), 16),
            justify="center",
            tags=(self._tag, "placeholder"),
        )

        # 직접조작 모드 상태 표시 (DECISION-DL-P3-3-002).
        # 좌하단 영역에 토글 상태를 항시 표시 → 토스트보다 영구적이라 모드 망각 방지.
        # Issue #12: 폰트는 SSOT (Noto Sans KR / Malgun Gothic 폴백) 로 통일.
        self._manual_mode_label_id = canvas.create_text(
            16,
            h - 24,
            text=_UI_STRINGS_DEFAULT["hero.manual_mode.off"],
            fill="#8a7a4a",
            font=(_family_regular(), 12),
            anchor="w",
            tags=(self._tag, "manual_mode_label"),
        )

        # 유닛 선택 패널 + 배치 안내 (Issue #56, DECISION-DL-P4D-008).
        if self.stage is not None and self._units_db:
            self._draw_unit_selection_panel()
            self._draw_placement_hint()

        # 키 바인딩
        self.app.root.bind("<Escape>", self._on_escape)
        self.app.root.bind("<space>", self._on_space)
        self.app.root.bind("m", self._on_m_key)
        self.app.root.bind("M", self._on_m_key)
        # 영웅 수동 모드용 키 (Issue #4, DECISION-DL-P3-3-001).
        for key in ("<Up>", "<Down>", "<Left>", "<Right>"):
            self.app.root.bind(key, self._on_hero_dir_key)
        for ch in ("w", "a", "s", "d", "W", "A", "S", "D"):
            self.app.root.bind(ch, self._on_hero_dir_key)
        # 영웅 스킬 키 Q/W/E (GDD §6 단축키, Issue #61, DECISION-DL-P5S-001).
        for ch in ("q", "Q", "e", "E"):
            self.app.root.bind(ch, self._on_skill_key)
        # 'w'/'W' 는 위 수동 이동(전진)과 S2 가 겹친다 — 충돌을 피하기 위해
        # S2 는 대문자가 아닌 별도 키가 없으므로, w 핸들러에서 이동과 스킬을
        # 모두 처리하도록 _on_hero_dir_key 가 분기한다(아래 참조). 여기서는
        # q/e 만 직접 바인딩하고 w 는 _on_hero_dir_key 가 위임한다.

    def update(self, dt: float) -> None:
        if self._paused or self._game_over or self.stage is None:
            return

        # 시스템 갱신 순서 (DESIGN 명세)
        self.wave.update(dt, self.world)
        self.pathing.update(dt)  # PathingSystem uses self.world internally
        self.combat.update(dt, self.world)
        self.economy.update(dt)

        # Issue #29 / DECISION-AUDIO-012: 웨이브 시작 SFX
        current_wave_idx = self.wave.current_index
        if current_wave_idx != self._last_wave_index and current_wave_idx >= 0:
            self._last_wave_index = current_wave_idx
            try:
                self.app.sound.play_sfx("sfx.wave_start")
            except Exception:  # noqa: BLE001
                pass

        # 영웅 업데이트 (Issue #4, DECISION-DL-P3-3-003).
        # 자동 모드: Hero.update 로 쿨다운/페이즈 갱신.
        # 수동 모드: 누적된 이동 입력만 처리. AI 자동 update 호출하지 않음.
        # Issue #57/#58 (DECISION-DL-P4D-007): 자동·수동 모두 평타 자동 공격
        # 트리거. 수동 모드에서도 영웅이 적과 전투할 수 있어야 한다.
        hero = self.world.get("hero")
        if hero is not None:
            prev_phase = getattr(hero, "current_phase", None)
            if self._hero_direct_mode:
                self._apply_hero_manual_move(hero, dt)
                # 수동 모드도 쿨다운/페이즈는 흘러야 평타가 가능 (Issue #58).
                if hasattr(hero, "update"):
                    try:
                        hero.update(dt)
                    except Exception:  # noqa: BLE001
                        pass
            else:
                if hasattr(hero, "update"):
                    hero.update(dt)
            # Hero 평타 자동 공격 (Issue #57/#58, DECISION-DL-P4D-007)
            self._tick_hero_attack(hero)
            # Hero S1/S2/S3 스킬 — 활성 DoT + 자동 AI (Issue #61, DECISION-DL-P5S-001)
            self._tick_hero_skills(hero, dt)
            # Issue #29 / DECISION-AUDIO-012: 영웅 페이즈 변화(스킬 발동) SFX
            new_phase = getattr(hero, "current_phase", None)
            if prev_phase is not None and new_phase is not None and new_phase != prev_phase:
                try:
                    self.app.sound.play_sfx("sfx.hero_skill")
                except Exception:  # noqa: BLE001
                    pass

        # 적이 castle(마지막 waypoint)에 도달했는지 검사 → lives 차감.
        # DECISION-DL-P5C-005 (Issue #62): PathingSystem 이 goal_reached/
        # reached_castle 플래그만 세팅하므로 BattleScene 이 누적 lives 손실로
        # 변환해야 게임이 끝날 수 있다. BL-07 시뮬레이터(`auto_mode_simulator.py`)
        # 의 처리 로직과 정합 — damage_to_castle 만큼 goals_reached 증가 +
        # 적 alive=False 처리. 이중 카운트 방지를 위해 dying 상태 적은 제외.
        self._apply_castle_breaches()

        # 죽은 적 정리
        self._cleanup_dead()

        # 승/패 판정
        self._check_end_conditions()

        # HUD 갱신
        self._refresh_hud()

    def render(self) -> None:
        """매 틱 entity 캔버스 아이템 갱신 (DECISION-DL-P4D-006, Issue #53).

        BL-07 시뮬레이터(`tests/test_clear_rate_simulation.py`) 는 systems 만
        직접 사용해 100% 클리어를 통과했으나, 실제 BattleScene 은 ``render()``
        가 빈 함수(``pass``) 였다. 결과적으로 영웅·적·아군·발사체·이펙트가
        시뮬레이션 상에는 존재하지만 캔버스에 그려지지 않아 stage 진입 후
        "전투 시작이 안 됨" 으로 사용자에게 보였다 (검수 결함 3호, Issue #53).

        본 구현은 entity 별로 ``canvas_id`` 가 None 이면 ``create_*`` 로 생성,
        이후 틱부터는 ``coords`` 로 위치만 갱신해 churn 을 회피한다. 죽은
        엔티티는 ``_cleanup_dead`` 가 world 리스트에서 제거하지만 캔버스 아이템
        은 본 메서드에서 동기화 정리한다 (``_known_canvas_items`` 추적).

        DECISION-DL-P4D-006 (Issue #53):
          - 렌더 책임은 BattleScene 에 둔다 (entity 의 draw 는 tk import 회피
            를 위해 no-op 유지 — 도메인 가드 src/entities tkinter-free).
          - 좌표는 ``scaler.to_screen`` 으로 베이스(1920×1080) → 스크린 변환.
          - 적/아군/영웅은 hp 비율에 따라 fill 변경, dying 상태는 회색.
          - 시각 단순화 (Phase 3.5 placeholder 스타일 유지): 원형/사각형.
          - 게임플레이 균형 영향 0 — 시뮬레이션 상태(좌표/hp) 만 시각화.
        """
        if self.stage is None:
            return
        canvas = getattr(self.app, "canvas", None)
        scaler = getattr(self.app, "scaler", None)
        if canvas is None or scaler is None:
            return

        # 현재 활성 엔티티의 canvas_id 추적 (cleanup 대비).
        active_ids: set[int] = set()

        # ----- 영웅 -----
        hero = self.world.get("hero")
        if hero is not None and getattr(hero, "alive", True):
            self._render_hero(canvas, scaler, hero)
            if hero.canvas_id is not None:
                active_ids.add(int(hero.canvas_id))

        # ----- 아군 -----
        for ally in self.world.get("allies", []):
            if not getattr(ally, "alive", True):
                continue
            self._render_ally(canvas, scaler, ally)
            if ally.canvas_id is not None:
                active_ids.add(int(ally.canvas_id))

        # ----- 적 -----
        for enemy in self.world.get("enemies", []):
            if not getattr(enemy, "alive", True):
                continue
            self._render_enemy(canvas, scaler, enemy)
            if enemy.canvas_id is not None:
                active_ids.add(int(enemy.canvas_id))
            # Issue #71: hp 바 (배경/전경) 도 active_ids 에 등록해 죽었을 때
            # 함께 cleanup 되도록 한다.
            for cid_attr in ("_hp_bg_id", "_hp_fg_id"):
                cid = getattr(enemy, cid_attr, None)
                if cid is not None:
                    active_ids.add(int(cid))

        # ----- 발사체 -----
        for proj in self.world.get("projectiles", []):
            if not getattr(proj, "alive", True):
                continue
            self._render_projectile(canvas, scaler, proj)
            if proj.canvas_id is not None:
                active_ids.add(int(proj.canvas_id))

        # ----- 이펙트 -----
        for fx in self.world.get("effects", []):
            if not getattr(fx, "alive", True):
                continue
            self._render_effect(canvas, scaler, fx)
            if fx.canvas_id is not None:
                active_ids.add(int(fx.canvas_id))

        # ----- 화살비(S3) 지대 — Issue #61, DECISION-DL-P5S-001 -----
        # 활성 지대는 매 render 마다 전용 태그로 재그린다(소수라 churn 무시 가능).
        if hero is not None:
            self._render_arrow_rains(canvas, scaler, hero)

        # 죽어서 world 에서 빠진 엔티티의 canvas_id 정리.
        stale = self._known_canvas_items - active_ids
        for item_id in stale:
            try:
                canvas.delete(item_id)
            except Exception:  # noqa: BLE001
                pass
        self._known_canvas_items = active_ids

    _ARROW_RAIN_TAG: str = "arrowrain"

    def _render_arrow_rains(self, canvas: Any, scaler: Any, hero: Any) -> None:
        """활성 화살비 지대 시각화 (Issue #61).

        GDD §3.2 S3: "검은 점선 화살이 위에서 떨어짐 (단순 라인)". 지대 경계 원 +
        시간 위상에 따라 내려오는 짧은 세로 화살선 몇 개로 표현한다. 전용 태그를
        매 틱 삭제 후 재생성해 상태(지대 수/위치/잔여시간)와 동기화한다.
        """
        try:
            canvas.delete(self._ARROW_RAIN_TAG)
        except Exception:  # noqa: BLE001
            return
        zones = getattr(hero, "active_arrow_rains", None)
        if not zones:
            return
        scale = float(getattr(scaler, "scale", 1.0))
        for zone in zones:
            cx, cy = scaler.to_screen(float(zone["x"]), float(zone["y"]))
            r = float(zone["radius"]) * scale
            try:
                canvas.create_oval(
                    cx - r,
                    cy - r,
                    cx + r,
                    cy + r,
                    outline="#2a2a2a",
                    dash=(4, 4),
                    width=2,
                    tags=(self._tag, self._ARROW_RAIN_TAG),
                )
            except Exception:  # noqa: BLE001
                continue
            # 낙하 화살선 — 잔여시간 위상으로 y 오프셋을 줘 떨어지는 느낌.
            phase = (float(zone.get("remaining", 0.0)) * 3.0) % 1.0
            for k in range(-2, 3):
                ax = cx + k * (r * 0.4)
                base_y = cy - r * 0.6 + (phase + (k + 2) * 0.2) % 1.0 * (r * 1.2)
                try:
                    canvas.create_line(
                        ax,
                        base_y,
                        ax,
                        base_y + 14 * scale,
                        fill="#101010",
                        width=2,
                        arrow="last",
                        tags=(self._tag, self._ARROW_RAIN_TAG),
                    )
                except Exception:  # noqa: BLE001
                    pass

    # ------------------------------------------------------------------
    # entity 렌더 헬퍼 (DECISION-DL-P4D-006, Issue #53)
    #
    # 도메인 가드: ``src/entities/*`` 는 tkinter import 금지. 렌더는 본 씬이
    # 책임지며 entity 의 좌표·hp·상태만 읽는다.
    # ------------------------------------------------------------------

    # 베이스(1920×1080) 좌표계에서 보이는 반지름·크기 (PR #24 placeholder 톤).
    _HERO_RADIUS_BASE: float = 22.0
    _ALLY_RADIUS_BASE: float = 14.0
    _ENEMY_RADIUS_BASE: float = 12.0
    _PROJECTILE_RADIUS_BASE: float = 4.0
    _EFFECT_RADIUS_BASE: float = 18.0

    def _render_hero(self, canvas: Any, scaler: Any, hero: Any) -> None:
        sx, sy = scaler.to_screen(float(hero.x), float(hero.y))
        r = self._HERO_RADIUS_BASE * float(getattr(scaler, "scale", 1.0))
        hp_ratio = 1.0
        max_hp = getattr(hero, "max_hp", 0) or 1
        if max_hp:
            hp_ratio = max(0.0, min(1.0, float(getattr(hero, "hp", 0)) / float(max_hp)))
        # 페이즈에 따라 외곽선 색 변경: phase1=청, phase2=황, phase3=주황, phase4=적
        phase = int(getattr(hero, "current_phase", 1) or 1)
        outline_by_phase = {1: "#4a8ad4", 2: "#d4b048", 3: "#d48848", 4: "#d44848"}
        outline = outline_by_phase.get(phase, "#4a8ad4")
        # 모드(자동/수동)에 따라 fill 강조.
        fill = "#5a4ac4" if self._hero_direct_mode else "#3a2a8c"
        if hp_ratio <= 0.0:
            fill = "#404040"

        if hero.canvas_id is None:
            hero.canvas_id = canvas.create_oval(
                sx - r,
                sy - r,
                sx + r,
                sy + r,
                fill=fill,
                outline=outline,
                width=3,
                tags=(self._tag, "hero"),
            )
        else:
            try:
                canvas.coords(hero.canvas_id, sx - r, sy - r, sx + r, sy + r)
                canvas.itemconfig(hero.canvas_id, fill=fill, outline=outline)
            except Exception:  # noqa: BLE001
                pass

    def _render_ally(self, canvas: Any, scaler: Any, ally: Any) -> None:
        sx, sy = scaler.to_screen(float(ally.x), float(ally.y))
        r = self._ALLY_RADIUS_BASE * float(getattr(scaler, "scale", 1.0))
        fill = "#2a7a4a"
        outline = "#88d4a8"
        if ally.canvas_id is None:
            ally.canvas_id = canvas.create_rectangle(
                sx - r,
                sy - r,
                sx + r,
                sy + r,
                fill=fill,
                outline=outline,
                width=2,
                tags=(self._tag, "ally"),
            )
        else:
            try:
                canvas.coords(ally.canvas_id, sx - r, sy - r, sx + r, sy + r)
            except Exception:  # noqa: BLE001
                pass

    def _render_enemy(self, canvas: Any, scaler: Any, enemy: Any) -> None:
        """적 본체 + HP 바 (Issue #71, DECISION-DL-P4D-010).

        rc.6 검수 결함 #71: 사용자가 "적이 공격받는데 죽지 않고 그냥 지나간다"
        고 보고. 진단 결과 영웅 평타가 데미지를 입히고 적이 사망 페이드도 정상
        진입하지만, **외형상 적의 hp 변화가 보이지 않아** 사용자는 적이 무적
        인 듯한 인상을 받음. 본 메서드는 적 본체 아래에 hp 바를 그려 매 틱
        hp 비율로 갱신해 시각 피드백을 제공한다 (단순 색약 친화 빨/노/초).

        도메인 가드: src/entities/enemy.py 변경 없음. 본 BattleScene 의 렌더
        책임만 확장. hp 바도 ``_known_canvas_items`` 에 등록되어 죽은 적
        cleanup 시 함께 삭제됨.
        """
        sx, sy = scaler.to_screen(float(enemy.x), float(enemy.y))
        r = self._ENEMY_RADIUS_BASE * float(getattr(scaler, "scale", 1.0))
        # dying 상태이면 회색 페이드 (잔혹 묘사 회피, GDD §5)
        if getattr(enemy, "dying", False):
            fill = "#666666"
            outline = "#888888"
        else:
            # boss 는 짙은 자주, 일반은 적색.
            enemy_def = getattr(enemy, "enemy_def", None)
            is_boss = bool(getattr(enemy_def, "is_boss", False)) if enemy_def else False
            fill = "#7a2a5a" if is_boss else "#a04030"
            outline = "#d8a060" if is_boss else "#e8c8a0"
        if enemy.canvas_id is None:
            enemy.canvas_id = canvas.create_oval(
                sx - r,
                sy - r,
                sx + r,
                sy + r,
                fill=fill,
                outline=outline,
                width=2,
                tags=(self._tag, "enemy"),
            )
        else:
            try:
                canvas.coords(enemy.canvas_id, sx - r, sy - r, sx + r, sy + r)
                canvas.itemconfig(enemy.canvas_id, fill=fill, outline=outline)
            except Exception:  # noqa: BLE001
                pass

        # HP 바 (Issue #71, DECISION-DL-P4D-010) — dying 상태에서는 숨김.
        edef = getattr(enemy, "enemy_def", None)
        max_hp = int(getattr(edef, "hp", 0) or getattr(enemy, "hp", 1) or 1)
        cur_hp = max(0, int(getattr(enemy, "hp", 0)))
        ratio = max(0.0, min(1.0, cur_hp / max_hp)) if max_hp > 0 else 0.0
        bar_w = r * 1.6  # 본체보다 약간 좁게
        bar_h = max(3.0, 4.0 * float(getattr(scaler, "scale", 1.0)))
        bx1 = sx - bar_w
        bx2 = sx + bar_w
        by1 = sy - r - bar_h - 4.0
        by2 = sy - r - 4.0
        bg_id = getattr(enemy, "_hp_bg_id", None)
        fg_id = getattr(enemy, "_hp_fg_id", None)
        if getattr(enemy, "dying", False):
            # 페이드 중에는 hp 바 숨김
            for cid in (bg_id, fg_id):
                if cid is not None:
                    try:
                        canvas.itemconfig(cid, state="hidden")
                    except Exception:  # noqa: BLE001
                        pass
            return
        # 비율에 따른 색상 — 색약 친화 (빨/노/초 분리)
        if ratio > 0.6:
            bar_fill = "#3fbf6f"
        elif ratio > 0.3:
            bar_fill = "#e8c860"
        else:
            bar_fill = "#d44040"
        # 배경
        if bg_id is None:
            enemy._hp_bg_id = canvas.create_rectangle(
                bx1,
                by1,
                bx2,
                by2,
                fill="#1c1c1c",
                outline="#3a3a3a",
                width=1,
                tags=(self._tag, "enemy_hp_bg"),
            )
        else:
            try:
                canvas.coords(bg_id, bx1, by1, bx2, by2)
                canvas.itemconfig(bg_id, state="normal")
            except Exception:  # noqa: BLE001
                pass
        # 전경 (hp 비율)
        fg_x2 = bx1 + (bx2 - bx1) * ratio
        if fg_id is None:
            enemy._hp_fg_id = canvas.create_rectangle(
                bx1,
                by1,
                fg_x2,
                by2,
                fill=bar_fill,
                outline="",
                tags=(self._tag, "enemy_hp_fg"),
            )
        else:
            try:
                canvas.coords(fg_id, bx1, by1, fg_x2, by2)
                canvas.itemconfig(fg_id, fill=bar_fill, state="normal")
            except Exception:  # noqa: BLE001
                pass

    def _render_projectile(self, canvas: Any, scaler: Any, proj: Any) -> None:
        sx, sy = scaler.to_screen(float(proj.x), float(proj.y))
        r = self._PROJECTILE_RADIUS_BASE * float(getattr(scaler, "scale", 1.0))
        if proj.canvas_id is None:
            proj.canvas_id = canvas.create_oval(
                sx - r,
                sy - r,
                sx + r,
                sy + r,
                fill="#e8d060",
                outline="",
                tags=(self._tag, "projectile"),
            )
        else:
            try:
                canvas.coords(proj.canvas_id, sx - r, sy - r, sx + r, sy + r)
            except Exception:  # noqa: BLE001
                pass

    def _render_effect(self, canvas: Any, scaler: Any, fx: Any) -> None:
        sx, sy = scaler.to_screen(float(fx.x), float(fx.y))
        r = self._EFFECT_RADIUS_BASE * float(getattr(scaler, "scale", 1.0))
        alpha = float(getattr(fx, "alpha", 1.0))
        # tk Canvas 는 알파 미지원 → stipple 로 근사 (alpha < 0.5 일 때 gray50).
        stipple = "" if alpha >= 0.5 else "gray50"
        if fx.canvas_id is None:
            fx.canvas_id = canvas.create_oval(
                sx - r,
                sy - r,
                sx + r,
                sy + r,
                fill="#f0e8a8",
                outline="",
                stipple=stipple,
                tags=(self._tag, "effect"),
            )
        else:
            try:
                canvas.coords(fx.canvas_id, sx - r, sy - r, sx + r, sy + r)
                canvas.itemconfig(fx.canvas_id, stipple=stipple)
            except Exception:  # noqa: BLE001
                pass

    def teardown(self) -> None:
        self.hud.teardown()
        super().teardown()
        try:
            self.app.root.unbind("<Escape>")
            self.app.root.unbind("<space>")
            self.app.root.unbind("m")
            self.app.root.unbind("M")
            for key in ("<Up>", "<Down>", "<Left>", "<Right>"):
                self.app.root.unbind(key)
            for ch in ("w", "a", "s", "d", "W", "A", "S", "D"):
                self.app.root.unbind(ch)
            # Issue #61: 스킬 키 Q/E 해제 (W 는 위에서 해제됨).
            for ch in ("q", "Q", "e", "E"):
                self.app.root.unbind(ch)
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # 내부 헬퍼
    # ------------------------------------------------------------------

    def _draw_paths(self) -> None:
        assert self.stage is not None
        canvas = self.app.canvas
        scaler = self.app.scaler
        for path in self.stage.paths:
            pts: list[float] = []
            for bx, by in path.waypoints:
                sx, sy = scaler.to_screen(bx, by)
                pts.extend([sx, sy])
            if len(pts) >= 4:
                canvas.create_line(
                    *pts,
                    fill="#7a5c2a",
                    width=4,
                    smooth=False,
                    tags=(self._tag, "path"),
                )

    def _draw_build_zones(self) -> None:
        """build_zone 사각형 + 클릭 핸들러 (Issue #56, DECISION-DL-P4D-008).

        zone index 를 클로저로 캡처해 ``_on_build_zone_click(idx)`` 으로 라우팅.
        """
        assert self.stage is not None
        canvas = self.app.canvas
        scaler = self.app.scaler
        self._build_zone_canvas_ids.clear()
        for idx, zone in enumerate(self.stage.build_zones):
            x1, y1 = scaler.to_screen(zone["x"], zone["y"])
            x2, y2 = scaler.to_screen(zone["x"] + zone["w"], zone["y"] + zone["h"])
            rect_id = canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="#1c2c1c",
                outline="#5fa860",
                width=2,
                dash=(6, 4),
                tags=(self._tag, "build_zone", f"build_zone_{idx}"),
            )
            # 중앙에 "+" 글리프 — 빈 슬롯 시각화 (배치 후 hidden).
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            plus_id = canvas.create_text(
                cx,
                cy,
                text="+",
                fill="#88c088",
                font=(_family_bold(), 32),
                anchor="center",
                tags=(self._tag, "build_zone", f"build_zone_plus_{idx}"),
            )

            def _make_handler(i: int) -> Any:
                def _h(_e: Any) -> None:
                    self._on_build_zone_click(i)

                return _h

            handler = _make_handler(idx)
            try:
                canvas.tag_bind(rect_id, "<ButtonRelease-1>", handler)
                canvas.tag_bind(plus_id, "<ButtonRelease-1>", handler)
            except Exception:  # noqa: BLE001
                pass
            self._build_zone_canvas_ids[idx] = rect_id

    def _populate_waypoints(self) -> None:
        """Stage.paths 의 waypoint 시퀀스를 world['waypoints'] 에 주입한다.

        PathingSystem 은 ``world['waypoints']`` 가 dict 면 ``path_id`` 로,
        list 면 단일 경로로 해석한다. 본 씬은 다중 경로 지원을 위해 dict 사용.
        (Issue #1, DECISION-DL-P3-3-004)
        """
        if self.stage is None:
            return
        # 기존 객체를 mutate 해야 world 와 systems 가 공유하는 참조가 끊기지 않음.
        self._waypoints_by_path.clear()
        for path in self.stage.paths:
            self._waypoints_by_path[path.id] = [(float(x), float(y)) for x, y in path.waypoints]

    def _spawn_enemy(self, enemy_type: str, path_id: str) -> None:
        """WaveSystem의 spawn_callback — 적을 world['enemies']에 추가.

        - ``enemy_type`` (예: ``tang_soldier``) 으로 EnemyDef 를 lookup.
        - ``path_id`` 에 해당하는 waypoints 의 첫 좌표에서 스폰.
        - ``Enemy`` 생성자에 EnemyDef + path_id 를 전달해 PathingSystem 과 결선.
        (Issue #1, DECISION-DL-P3-3-005/006)
        """
        try:
            from src.entities.enemy import Enemy

            enemy_def = self._enemy_defs.get(enemy_type)
            if enemy_def is None:
                self._log.warning(
                    "spawn_enemy: unknown enemy_type=%s (stage=%s)",
                    enemy_type,
                    self.stage_id,
                )
                return

            waypoints = self._waypoints_by_path.get(path_id)
            if not waypoints:
                self._log.warning(
                    "spawn_enemy: unknown path_id=%s (stage=%s)",
                    path_id,
                    self.stage_id,
                )
                return

            start_x, start_y = waypoints[0]
            enemy = Enemy(x=start_x, y=start_y, enemy_def=enemy_def, path_id=path_id)
            self.world["enemies"].append(enemy)
            self._log.debug(
                "spawned %s on %s at (%.1f, %.1f)",
                enemy_type,
                path_id,
                start_x,
                start_y,
            )
        except Exception as exc:  # noqa: BLE001
            self._log.warning("spawn_enemy failed: %s", exc)

    # ------------------------------------------------------------------
    # 유닛 배치 UI (Issue #56, DECISION-DL-P4D-008)
    # ------------------------------------------------------------------

    def _draw_unit_selection_panel(self) -> None:
        """하단 좌측 유닛 선택 패널 (Issue #56, DECISION-DL-P4D-008).

        units.json 의 각 유닛에 대해 버튼 1개 (이름 + 곡식 비용).
        클릭 시 ``self._selected_unit_id`` 가 토글된다.
        """
        canvas = self.app.canvas
        scaler = self.app.scaler
        # 베이스 좌표 1920×1080 기준 — 좌측 하단 (40, 840) 시작.
        base_x = 40
        base_y = 850
        btn_w = 200
        btn_h = 70
        spacing = 12

        # 패널 배경
        panel_x1, panel_y1 = scaler.to_screen(base_x - 12, base_y - 36)
        panel_x2, panel_y2 = scaler.to_screen(
            base_x + btn_w + 12,
            base_y + (btn_h + spacing) * len(self._units_db) + 12,
        )
        canvas.create_rectangle(
            panel_x1,
            panel_y1,
            panel_x2,
            panel_y2,
            fill="#1a1208",
            outline="#7a5c3a",
            width=2,
            tags=(self._tag, "placement_panel_bg"),
        )
        title_x, title_y = scaler.to_screen(base_x, base_y - 18)
        canvas.create_text(
            title_x,
            title_y,
            text="아군 배치",
            fill="#f0d080",
            font=(_family_bold(), 14),
            anchor="w",
            tags=(self._tag, "placement_panel_title"),
        )

        for i, (unit_id, unit_def) in enumerate(self._units_db.items()):
            bx = base_x
            by = base_y + i * (btn_h + spacing)
            x1, y1 = scaler.to_screen(bx, by)
            x2, y2 = scaler.to_screen(bx + btn_w, by + btn_h)
            rect_id = canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="#3a2a1c",
                outline="#a88a5c",
                width=2,
                tags=(self._tag, "placement_btn", f"placement_btn_{unit_id}"),
            )
            name_x, name_y = scaler.to_screen(bx + 12, by + 14)
            name_id = canvas.create_text(
                name_x,
                name_y,
                text=unit_def.name,
                fill="#f0e0c0",
                font=(_family_bold(), 14),
                anchor="nw",
                tags=(self._tag, "placement_btn", f"placement_btn_{unit_id}"),
            )
            cost_x, cost_y = scaler.to_screen(bx + 12, by + 42)
            cost_id = canvas.create_text(
                cost_x,
                cost_y,
                text=f"곡식 {unit_def.cost}",
                fill="#e8c860",
                font=(_family_regular(), 12),
                anchor="nw",
                tags=(self._tag, "placement_btn", f"placement_btn_{unit_id}"),
            )

            def _make_select(uid: str) -> Any:
                def _h(_e: Any) -> None:
                    self._on_unit_button_click(uid)

                return _h

            handler = _make_select(unit_id)
            for iid in (rect_id, name_id, cost_id):
                try:
                    canvas.tag_bind(iid, "<ButtonRelease-1>", handler)
                except Exception:  # noqa: BLE001
                    pass

            self._placement_btn_state[unit_id] = {
                "rect_id": rect_id,
                "name_id": name_id,
                "cost_id": cost_id,
            }

    def _draw_placement_hint(self) -> None:
        """배치 안내 텍스트 (패널 위 또는 하단)."""
        canvas = self.app.canvas
        scaler = self.app.scaler
        hx, hy = scaler.to_screen(260, 1040)
        self._placement_hint_id = canvas.create_text(
            hx,
            hy,
            text=_UI_STRINGS_DEFAULT["battle.placement.hint_idle"],
            fill="#d4a84a",
            font=(_family_regular(), 13),
            anchor="w",
            tags=(self._tag, "placement_hint"),
        )

    def _refresh_placement_hint(self, text: str | None = None, fill: str = "#d4a84a") -> None:
        if self._placement_hint_id is None:
            return
        canvas = self.app.canvas
        if text is None:
            if self._selected_unit_id and self._selected_unit_id in self._units_db:
                udef = self._units_db[self._selected_unit_id]
                text = _UI_STRINGS_DEFAULT["battle.placement.hint_selected"].format(unit_name=udef.name)
                fill = "#f0d080"
            else:
                text = _UI_STRINGS_DEFAULT["battle.placement.hint_idle"]
        try:
            canvas.itemconfig(self._placement_hint_id, text=text, fill=fill)
        except Exception:  # noqa: BLE001
            pass

    def _on_unit_button_click(self, unit_id: str) -> None:
        """유닛 선택 버튼 클릭 — 같은 유닛 다시 누르면 토글 해제."""
        if self._paused or self._game_over:
            return
        if self._selected_unit_id == unit_id:
            # 토글 해제
            self._selected_unit_id = None
        else:
            self._selected_unit_id = unit_id
        self._refresh_unit_button_highlight()
        self._refresh_placement_hint()

    def _refresh_unit_button_highlight(self) -> None:
        canvas = self.app.canvas
        for uid, state in self._placement_btn_state.items():
            selected = uid == self._selected_unit_id
            fill = "#5a4a2c" if selected else "#3a2a1c"
            outline = "#d4a84a" if selected else "#a88a5c"
            try:
                canvas.itemconfig(state["rect_id"], fill=fill, outline=outline)
            except Exception:  # noqa: BLE001
                pass

    def _on_build_zone_click(self, zone_idx: int) -> None:
        """build_zone 클릭 — 선택된 유닛을 배치 (Issue #56, DECISION-DL-P4D-008).

        - 선택 유닛 없음: 안내 텍스트만 갱신.
        - 곡식 부족: 안내 + 동작 안 함.
        - zone 이미 점유: 안내.
        - 정상: Ally 생성 → world['allies'] 에 추가 → 곡식 차감 → 점유 표시.
        """
        if self._paused or self._game_over or self.stage is None:
            return
        if self._selected_unit_id is None or self._selected_unit_id not in self._units_db:
            self._refresh_placement_hint(
                text=_UI_STRINGS_DEFAULT["battle.placement.hint_idle"],
            )
            return
        if zone_idx in self._build_zone_occupants:
            self._refresh_placement_hint(
                text=_UI_STRINGS_DEFAULT["battle.placement.zone_taken"],
                fill="#e08840",
            )
            return
        unit_def = self._units_db[self._selected_unit_id]
        food = int(self.world.get("food", 0))
        if food < unit_def.cost:
            self._refresh_placement_hint(
                text=_UI_STRINGS_DEFAULT["battle.placement.insufficient_food"].format(need=unit_def.cost),
                fill="#e08840",
            )
            return

        zone = self.stage.build_zones[zone_idx]
        cx = float(zone["x"]) + float(zone["w"]) / 2.0
        cy = float(zone["y"]) + float(zone["h"]) / 2.0
        try:
            from src.entities.ally import Ally

            ally = Ally(x=cx, y=cy, unit_def=unit_def)
            self.world["allies"].append(ally)
            self._build_zone_occupants[zone_idx] = ally
            # 곡식 차감
            self.world["food"] = food - unit_def.cost
            self.world["gold"] = max(0, int(self.world.get("gold", food)) - unit_def.cost)
            # 빈 zone "+" 글리프 숨김
            canvas = self.app.canvas
            try:
                canvas.itemconfig(f"build_zone_plus_{zone_idx}", state="hidden")
            except Exception:  # noqa: BLE001
                pass
            # 점유 표시 — zone 외곽선 색 변경
            try:
                canvas.itemconfig(self._build_zone_canvas_ids[zone_idx], outline="#3c6a3c")
            except Exception:  # noqa: BLE001
                pass
            self._log.info(
                "ally placed: %s at (%.1f, %.1f) zone=%d",
                unit_def.name,
                cx,
                cy,
                zone_idx,
            )
            self._refresh_placement_hint()
            # 튜토리얼 단계 3 진행 트리거 — TutorialScene 이 통합되면 이벤트 발행.
            bus = self.world.get("events")
            if bus is not None:
                try:
                    bus.publish("battle.ally.placed", {"unit_id": self._selected_unit_id, "zone": zone_idx})
                except Exception:  # noqa: BLE001
                    pass
        except Exception as exc:  # noqa: BLE001
            self._log.warning("ally place failed: %s", exc)

    def _tick_hero_attack(self, hero: Any) -> None:
        """매 틱 영웅 평타 자동 공격 트리거 (Issue #57/#58, DECISION-DL-P4D-007).

        Hero.auto_attack 이 발사 가능하면 dict 반환, 아니면 None.
        Projectile 을 world['projectiles'] 에 추가 → CombatSystem 이 매 틱
        update 로 명중·데미지·이펙트 처리를 그대로 가져감.

        도메인 가드: Hero 는 발사 정보만 반환, 발사체 생성은 본 씬이 담당.
        """
        if hero is None or not getattr(hero, "alive", True):
            return
        if not hasattr(hero, "auto_attack"):
            return
        enemies = self.world.get("enemies", [])
        if not enemies:
            return
        try:
            fire_info = hero.auto_attack(enemies)
        except Exception as exc:  # noqa: BLE001
            self._log.warning("hero auto_attack failed: %s", exc)
            return
        if fire_info is None:
            return
        # Projectile 스폰 — 아군 발사체와 동일한 경로로 CombatSystem 명중 처리.
        try:
            from src.entities.projectile import Projectile

            target = fire_info["target"]
            proj = Projectile(
                x=float(fire_info["x"]),
                y=float(fire_info["y"]),
                target_x=float(target.x),
                target_y=float(target.y),
                damage=int(fire_info["damage"]),
                speed=520.0,  # 영웅 활은 일반 궁수보다 약간 빠름
                target=target,
            )
            self.world["projectiles"].append(proj)
        except Exception as exc:  # noqa: BLE001
            self._log.warning("hero projectile spawn failed: %s", exc)

    def _apply_hero_manual_move(self, hero: Any, dt: float) -> None:
        """수동 모드 영웅 이동 적용 + 페이즈/쿨다운 부분 갱신.

        - WASD/방향키 누적 입력 (``self._hero_move_dir``) 으로 hero.x/y 이동.
        - hero.update() 의 자동 AI(있는 경우)는 호출하지 않으나, 페이즈/쿨다운은
          UI 일관성을 위해 직접 갱신한다.
        (Issue #4, DECISION-DL-P3-3-003)
        """
        dx, dy = self._hero_move_dir
        if dx != 0.0 or dy != 0.0:
            speed = float(getattr(hero, "move_speed", 150.0))
            # 대각선 정규화 (1,1) → ~0.707 로 같은 속도 유지.
            mag = (dx * dx + dy * dy) ** 0.5
            if mag > 0:
                dx /= mag
                dy /= mag
            hero.x = float(getattr(hero, "x", 0.0)) + dx * speed * dt
            hero.y = float(getattr(hero, "y", 0.0)) + dy * speed * dt
            # 입력은 한 틱만 살아있도록 소거 (key 이벤트 기반이라 hold 는 자동 재발화).
        self._hero_move_dir = (0.0, 0.0)

        # 쿨다운/페이즈 부분 갱신 (자동 모드의 부수 효과는 유지).
        if hasattr(hero, "_ult_timer") and hero._ult_timer > 0.0:  # noqa: SLF001
            hero._ult_timer = max(0.0, hero._ult_timer - dt)  # noqa: SLF001
        if hasattr(hero, "current_phase") and hasattr(hero, "_prev_phase"):
            new_phase = hero.current_phase
            if new_phase != hero._prev_phase:  # noqa: SLF001
                hero.phase_changed = True
                hero._prev_phase = new_phase  # noqa: SLF001

    def _apply_castle_breaches(self) -> None:
        """적이 castle 도달 시 lives 차감 + 적 제거 (Issue #62, DECISION-DL-P5C-005).

        BattleScene.update 매 틱마다 호출. PathingSystem 이 마지막 waypoint
        도달한 적에 ``goal_reached=True`` (및 ``reached_castle=True``) 를 세팅
        하지만, 이를 ``world['goals_reached']`` 누적 손실로 변환하는 책임은
        BattleScene 에 있다. 본 메서드는 BL-07 시뮬레이터의 처리
        (``auto_mode_simulator.StageSimulator``) 와 동일 정책::

          breach 1회 = enemy.enemy_def.damage_to_castle 만큼 goals_reached 증가
          breach 후 enemy.alive = False (다음 _cleanup_dead 에서 정리)

        이중 카운트 방지를 위해 이미 dying (사망 페이드 중) 인 적은 건너뛴다.
        """
        enemies = self.world.get("enemies", [])
        if not enemies:
            return
        breach_count = 0
        for enemy in enemies:
            if not getattr(enemy, "alive", False):
                continue
            if getattr(enemy, "dying", False):
                continue
            if not (getattr(enemy, "goal_reached", False) or getattr(enemy, "reached_castle", False)):
                continue
            # damage_to_castle 만큼 손실. EnemyDef 가 누락된 경우 1 로 fallback.
            edef = getattr(enemy, "enemy_def", None)
            damage = int(getattr(edef, "damage_to_castle", 1) or 1)
            self.world["goals_reached"] = int(self.world.get("goals_reached", 0)) + damage
            # 살아있는 채로 제거 (페이드 없이 곧장 사라짐 — castle 진입 묘사).
            enemy.alive = False
            breach_count += 1
        if breach_count > 0:
            self._log.debug(
                "castle breach: %d enemies reached goal (goals_reached=%d)",
                breach_count,
                self.world.get("goals_reached", 0),
            )
            # Issue #75 / DECISION-DL-P5C-008: 성문 HP 차감 시각 피드백.
            try:
                self.hud.flash_castle_damage()
            except Exception:  # noqa: BLE001
                pass

    def _cleanup_dead(self) -> None:
        """alive==False인 엔티티를 world 목록에서 제거.

        Issue #29 / DECISION-AUDIO-012: 적 사망 시 sfx.enemy_die SFX 재생.
        """
        for key in ("enemies", "allies", "projectiles", "effects"):
            lst = self.world.get(key)
            if isinstance(lst, list):
                dead_enemies = [e for e in lst if not getattr(e, "alive", True)] if key == "enemies" else []
                self.world[key] = [e for e in lst if getattr(e, "alive", True)]
                # 적 사망 SFX (1번만 재생 — 동시 다수 사망 시에도 단발)
                if dead_enemies:
                    try:
                        self.app.sound.play_sfx("sfx.enemy_die")
                    except Exception:  # noqa: BLE001
                        pass

    def _check_end_conditions(self) -> None:
        """승/패 판정 및 ResultDialog 표시."""
        if self._game_over:
            return

        # 패배 조건
        hero = self.world.get("hero")
        hero_dead = hero is not None and getattr(hero, "hp", 1) <= 0
        goals_reached = self.world.get("goals_reached", 0)
        lives = self.world.get("lives", 20)
        lives_depleted = goals_reached >= lives

        if hero_dead or lives_depleted:
            self._end_battle(victory=False)
            return

        # 승리 조건
        if self.wave.all_clear and not self.world["enemies"]:
            self._end_battle(victory=True)

    def _end_battle(self, victory: bool) -> None:
        """전투 종료 처리.

        - 승리 + 마지막 stage(=stage_05): "다음" → ending 씬 (수직 슬라이스 종결).
        - 승리 + 그 외 stage: "다음" → stage_select (다음 스테이지 선택 가능).
        - 패배: 다음/재도전 모두 stage_select 로 회귀 (게임오버 다이얼로그 표시).
        (Issue #12, DECISION-DL-P3-5-004)
        """
        if self._game_over:
            return
        self._game_over = True
        self._paused = True

        stage = self.stage
        stars = 1 if victory else 0
        fame = stars * 3
        grain = stage.reward.grain if stage else 0

        stats: dict[str, Any] = {
            "stars": stars,
            "fame": fame,
            "grain": grain,
            "waves_survived": self.wave.current_wave,
        }

        # "다음" 동선 결정: stage_05 클리어 + 승리 → ending 으로 직행.
        is_final_stage_win = bool(victory) and self.stage_id == "stage_05"
        next_scene = "ending" if is_final_stage_win else "stage_select"

        canvas = self.app.canvas
        scaler = self.app.scaler
        self._result_dialog = ResultDialog(
            canvas,
            scaler,
            victory=victory,
            stats=stats,
            on_next=lambda: self.app.goto(next_scene),
            on_retry=lambda: self.app.goto("battle"),
            on_menu=lambda: self.app.goto("stage_select"),
        )
        self._result_dialog.show()

    def _compute_hero_spawn_xy(self) -> tuple[float, float]:
        """영웅 스폰 좌표 계산 (Issue #12, DECISION-DL-P3-5-003).

        - stage.build_zones 가 있으면 첫 zone 중앙.
        - 없으면 1920×1080 화면 중앙.
        """
        if self.stage is not None and self.stage.build_zones:
            z = self.stage.build_zones[0]
            return (float(z["x"]) + float(z["w"]) / 2.0, float(z["y"]) + float(z["h"]) / 2.0)
        return (960.0, 540.0)

    def _refresh_hud(self) -> None:
        """HUD state dict를 구성해서 업데이트."""
        w = self.world
        hero = w.get("hero")
        hero_hp = getattr(hero, "hp", 0) if hero else 0
        hero_max_hp = getattr(hero, "max_hp", max(hero_hp, 1)) if hero else 1
        hero_phase = getattr(hero, "phase", 1) if hero else 1
        ult_cd = float(getattr(hero, "_ult_timer", 0.0)) if hero else 0.0  # noqa: SLF001
        # Issue #61: S1/S2/S3 스킬 쿨다운 (HUD Q/W/E 슬롯).
        s1_cd = float(getattr(hero, "s1_cooldown", 0.0)) if hero else 0.0
        s2_cd = float(getattr(hero, "s2_cooldown", 0.0)) if hero else 0.0
        s3_cd = float(getattr(hero, "s3_cooldown", 0.0)) if hero else 0.0

        # 성문 HP(lives) — Issue #75 / DECISION-DL-P5C-008.
        # 남은 lives = 초기 lives - 누적 goals_reached (음수 방지는 HUD 가 처리).
        castle_max_hp = int(w.get("lives", 0))
        castle_hp = castle_max_hp - int(w.get("goals_reached", 0))

        state: dict[str, Any] = {
            "food": w.get("food", w.get("gold", 0)),
            "pop": w.get("pop", w.get("population", 0)),
            "arrows": w.get("arrows", 0),
            "hero_hp": hero_hp,
            "hero_max_hp": hero_max_hp,
            "hero_phase": hero_phase,
            "ult_cooldown_s": ult_cd,
            "s1_cooldown_s": s1_cd,
            "s2_cooldown_s": s2_cd,
            "s3_cooldown_s": s3_cd,
            "wave": self.wave.current_wave,
            "total_waves": len(self.wave.waves),
            "time_to_next": self.wave.time_to_next_wave,
            "castle_hp": castle_hp,
            "castle_max_hp": castle_max_hp,
        }
        self.hud.update(state)

    # ------------------------------------------------------------------
    # 이벤트 핸들러
    # ------------------------------------------------------------------

    def _on_escape(self, _event: Any) -> None:
        self._toggle_pause()

    def _on_space(self, _event: Any) -> None:
        if self._paused and self._pause_dialog and self._pause_dialog.visible:
            return
        if not self._paused:
            self.wave.force_next()
        else:
            self._toggle_pause()

    def _on_m_key(self, _event: Any) -> None:
        """M키 = 영웅 직접 조작 모드 토글 (OPEN-D-201, Issue #4).

        토글 후 상태 라벨을 즉시 갱신하고 events 버스에 이벤트 발행.
        """
        self._hero_direct_mode = not self._hero_direct_mode
        on = self._hero_direct_mode
        self._log.info("hero direct mode: %s", "ON" if on else "OFF")
        self._refresh_manual_mode_label()
        # 모드 변경 이벤트 (HUD/QA 후크가 구독 가능).
        bus = self.world.get("events")
        if bus is not None:
            try:
                bus.publish("hero.manual_mode.toggled", {"on": on})
            except Exception:  # noqa: BLE001
                pass

    def _refresh_manual_mode_label(self) -> None:
        """직접조작 모드 상태 라벨 갱신 (DECISION-DL-P3-3-002)."""
        if self._manual_mode_label_id is None:
            return
        canvas = getattr(self.app, "canvas", None)
        if canvas is None or not hasattr(canvas, "itemconfig"):
            return
        if self._hero_direct_mode:
            text = _UI_STRINGS_DEFAULT["hero.manual_mode.on"]
            fill = "#f0c060"
        else:
            text = _UI_STRINGS_DEFAULT["hero.manual_mode.off"]
            fill = "#8a7a4a"
        try:
            canvas.itemconfig(self._manual_mode_label_id, text=text, fill=fill)
        except Exception:  # noqa: BLE001
            pass

    def _on_hero_dir_key(self, event: Any) -> None:
        """영웅 수동 모드 방향 입력 (Issue #4, DECISION-DL-P3-3-001).

        수동 모드 OFF 또는 일시정지/게임오버 상태이면 무시.
        같은 틱에 여러 키가 들어오면 방향이 누적된다 (예: Up+Right → 우상).

        Issue #61: 'w'/'W' 키는 수동 모드에서는 전진 이동, 그 외(자동 모드)
        에서는 S2 독려의 함성으로 분기한다(GDD §6 Q/W/E 스킬과 WASD 이동 충돌
        해소). Q/E 는 _on_skill_key 가 별도 처리.
        """
        keysym = getattr(event, "keysym", None)
        if keysym is None:
            return
        # 'w'/'W' 자동 모드 → S2 스킬 (수동 모드는 아래 이동 처리로 진행).
        if keysym in ("w", "W") and not self._hero_direct_mode:
            if not self._paused and not self._game_over:
                self._activate_skill("s2")
            return
        if not self._hero_direct_mode or self._paused or self._game_over:
            return
        vec = _HERO_DIR_KEYS.get(keysym)
        if vec is None:
            return
        cur_x, cur_y = self._hero_move_dir
        self._hero_move_dir = (cur_x + vec[0], cur_y + vec[1])

    def _on_skill_key(self, event: Any) -> None:
        """영웅 스킬 키 입력 Q(S1)/E(S3) (Issue #61, DECISION-DL-P5S-001).

        S2(W)는 이동 키와 겹쳐 ``_on_hero_dir_key`` 가 분기 처리한다.
        일시정지/게임오버 상태이면 무시.
        """
        if self._paused or self._game_over:
            return
        keysym = (getattr(event, "keysym", "") or "").lower()
        if keysym == "q":
            self._activate_skill("s1")
        elif keysym == "e":
            self._activate_skill("s3")

    def _activate_skill(self, name: str) -> None:
        """스킬 발동 — Hero.cast_* 호출 + 발동 시 시각/사운드 스폰.

        도메인 가드: 효과 적용은 Hero 가, Effect/Projectile 스폰은 본 씬이.
        """
        hero = self.world.get("hero")
        if hero is None or not getattr(hero, "alive", True):
            return
        enemies = self.world.get("enemies", [])
        allies = self.world.get("allies", [])
        try:
            if name == "s1":
                res = hero.cast_s1(enemies)
            elif name == "s2":
                res = hero.cast_s2(allies)
            elif name == "s3":
                tx, ty = self._pick_arrow_rain_target(enemies, hero)
                res = hero.cast_s3(tx, ty)
            else:
                return
        except Exception as exc:  # noqa: BLE001
            self._log.warning("hero skill %s failed: %s", name, exc)
            return
        if res and res.get("fired"):
            self._spawn_skill_visual(name, res, hero)

    def _pick_arrow_rain_target(self, enemies: list[Any], hero: Any) -> tuple[float, float]:
        """S3 화살비 낙하 지점 선정 — 적 군집 중심 우선, 없으면 최근접 적, 폴백 영웅 전방."""
        from src.entities.hero import _S3_RADIUS  # 군집 반경 재사용

        cluster = None
        try:
            cluster = hero._densest_enemy_cluster(enemies, _S3_RADIUS, 1)  # noqa: SLF001
        except Exception:  # noqa: BLE001
            cluster = None
        if cluster is not None:
            return cluster
        # 폴백: 최근접 적, 그조차 없으면 영웅 전방(위쪽).
        target = None
        try:
            target = hero.find_target_in_range(enemies)
        except Exception:  # noqa: BLE001
            target = None
        if target is not None:
            return (float(target.x), float(target.y))
        return (float(getattr(hero, "x", 960.0)), float(getattr(hero, "y", 540.0)) - 120.0)

    def _spawn_skill_visual(self, name: str, res: dict[str, Any], hero: Any) -> None:
        """스킬 발동 시 Effect 스폰 + 사운드 (Issue #61).

        - S1: 타겟 위치에 황금 강타 Effect + 영웅→타겟 발사체 잔상.
        - S2: 영웅 머리 위 함성 Effect (버프 대상 표시는 render 가 처리).
        - S3: 지대 중심 Effect (지대 원은 render 가 매 틱 표시).
        """
        try:
            from src.entities.effect import Effect

            effects = self.world.setdefault("effects", [])
            if name == "s1":
                target = res.get("target")
                if target is not None:
                    # 타겟 위치에 황금 강타 Effect (발사체 잔상은 평타 카운트와
                    # 혼동을 막기 위해 생략 — 시각은 Effect 로 충분).
                    effects.append(Effect(x=float(target.x), y=float(target.y), kind="hit"))
            elif name == "s2":
                effects.append(Effect(x=float(hero.x), y=float(hero.y) - 30.0, kind="hit"))
            elif name == "s3":
                effects.append(
                    Effect(
                        x=float(res.get("x", hero.x)),
                        y=float(res.get("y", hero.y)),
                        kind="hit",
                    )
                )
        except Exception as exc:  # noqa: BLE001
            self._log.warning("skill visual spawn failed: %s", exc)
        # 발동 사운드.
        try:
            self.app.sound.play_sfx("sfx.hero_skill")
        except Exception:  # noqa: BLE001
            pass

    def _tick_hero_skills(self, hero: Any, dt: float) -> None:
        """매 틱 영웅 스킬 처리 — 활성 화살비 DoT + 자동 모드 AI 스킬 사용 (Issue #61)."""
        if hero is None or not getattr(hero, "alive", True):
            return
        enemies = self.world.get("enemies", [])
        allies = self.world.get("allies", [])
        # 활성 화살비(S3) DoT 적용.
        if hasattr(hero, "tick_active_skills"):
            try:
                hero.tick_active_skills(dt, enemies)
            except Exception as exc:  # noqa: BLE001
                self._log.warning("hero tick_active_skills failed: %s", exc)
        # 자동 모드에서만 AI 자동 스킬. 수동 모드는 플레이어 키 입력으로 발동.
        if not self._hero_direct_mode and hasattr(hero, "auto_cast"):
            try:
                results = hero.auto_cast(allies, enemies)
            except Exception as exc:  # noqa: BLE001
                self._log.warning("hero auto_cast failed: %s", exc)
                results = []
            for res in results:
                if res.get("fired"):
                    self._spawn_skill_visual(res.get("skill", ""), res, hero)

    def _toggle_pause(self) -> None:
        """일시정지 토글."""
        if self._game_over:
            return

        if self._paused:
            # 재개
            self._paused = False
            if self._pause_dialog:
                self._pause_dialog.hide()
                self._pause_dialog = None
        else:
            # 일시정지
            self._paused = True
            self.wave.paused = True
            canvas = self.app.canvas
            scaler = self.app.scaler
            self._pause_dialog = PauseDialog(
                canvas,
                scaler,
                on_resume=self._toggle_pause,
                on_quit=lambda: self.app.goto("menu"),
                on_stage_select=lambda: self.app.goto("stage_select"),
            )
            self._pause_dialog.show()
            # 재개 시 wave.paused 해제
            _orig_resume = self._pause_dialog._on_resume  # noqa: SLF001

            def _resume_and_unpause() -> None:
                self.wave.paused = False
                _orig_resume()

            self._pause_dialog._on_resume = _resume_and_unpause  # noqa: SLF001
