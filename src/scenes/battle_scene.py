"""전투 씬 — 게임의 코어 (SCN-05).

DESIGN:
- 단일 캔버스 + World 딕셔너리 + 시스템 오케스트레이션.
- update 순서: WaveSystem → PathingSystem → CombatSystem → HUD.
- 패배 조건: hero hp<=0 OR enemy.goal_reached 누적 >= lives.
- 승리 조건: WaveSystem.all_clear AND len(enemies alive)==0.
- Esc/Space → PauseDialog show.
- M키 = 영웅 직접 조작 모드 토글 (OPEN-D-201, Issue #4).
- spawn_enemy: stage.paths 의 waypoint 시퀀스를 world['waypoints']에
  ``dict[path_id, list[Point]]`` 로 주입하고, EnemyDef 를 들고 Enemy 인스턴스를
  생성 (Issue #1, DECISION-DL-P3-3-004/005/006).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.core.fonts import family_regular as _family_regular
from src.core.logger import get_logger
from src.data.loader import EnemyDef, StageDef, load_enemies, load_stage
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

# UI 문자열 (docs/story/08_ui_strings.md §3.4 — DECISION-DL-P3-3-007)
_UI_STRINGS_DEFAULT: dict[str, str] = {
    "hero.manual_mode.on": "직접 조작 모드 ON (WASD/방향키 이동)",
    "hero.manual_mode.off": "직접 조작 모드 OFF",
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

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    def build(self) -> None:
        canvas = self.app.canvas
        scaler = self.app.scaler
        w = canvas.winfo_width() or scaler.canvas_w
        h = canvas.winfo_height() or scaler.canvas_h

        # 스테이지 데이터 로드
        try:
            self.stage = load_stage(self.stage_id)
        except FileNotFoundError:
            self._log.warning("stage file missing: %s", self.stage_id)
            self.stage = None

        # 적 정의 데이터 로드 (Issue #1, DECISION-DL-P3-3-006).
        # 누락된 enemies.json 은 치명적이지 않으므로 경고만 남기고 빈 맵 유지.
        try:
            self._enemy_defs = load_enemies()
        except (FileNotFoundError, OSError) as exc:
            self._log.warning("enemies.json load failed: %s", exc)
            self._enemy_defs = {}

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
            self.wave.load(self.stage.waves)

        # HUD 초기화 (상단 바 + 영웅 패널)
        self.hud.build(
            canvas,
            scaler,
            on_pause_click=self._toggle_pause,
        )

        # 전투 플레이스홀더 텍스트
        self._placeholder_id = canvas.create_text(
            w / 2,
            h / 2,
            text=(
                "전투 씬 — Phase 2 구현 중\n"
                f"stage: {self.stage_id}    "
                f"waves: {len(self.stage.waves) if self.stage else 0}\n"
                "ESC/Space = 일시정지 | M = 직접조작 모드"
            ),
            fill="#e0d0a0",
            font=(_family_regular(), 16),
            justify="center",
            tags=(self._tag, "placeholder"),
        )

        # 직접조작 모드 상태 표시 (DECISION-DL-P3-3-002).
        # 좌하단 영역에 토글 상태를 항시 표시 → 토스트보다 영구적이라 모드 망각 방지.
        self._manual_mode_label_id = canvas.create_text(
            16,
            h - 24,
            text=_UI_STRINGS_DEFAULT["hero.manual_mode.off"],
            fill="#8a7a4a",
            font=("Malgun Gothic", 12),
            anchor="w",
            tags=(self._tag, "manual_mode_label"),
        )

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

    def update(self, dt: float) -> None:
        if self._paused or self._game_over or self.stage is None:
            return

        # 시스템 갱신 순서 (DESIGN 명세)
        self.wave.update(dt, self.world)
        self.pathing.update(dt)  # PathingSystem uses self.world internally
        self.combat.update(dt, self.world)
        self.economy.update(dt)

        # 영웅 업데이트 (Issue #4, DECISION-DL-P3-3-003).
        # 자동 모드: Hero.update 로 쿨다운/페이즈 갱신.
        # 수동 모드: 누적된 이동 입력만 처리. AI 자동 update 호출하지 않음.
        hero = self.world.get("hero")
        if hero is not None:
            if self._hero_direct_mode:
                self._apply_hero_manual_move(hero, dt)
            else:
                if hasattr(hero, "update"):
                    hero.update(dt)

        # 죽은 적 정리
        self._cleanup_dead()

        # 승/패 판정
        self._check_end_conditions()

        # HUD 갱신
        self._refresh_hud()

    def render(self) -> None:
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
        assert self.stage is not None
        canvas = self.app.canvas
        scaler = self.app.scaler
        for zone in self.stage.build_zones:
            x1, y1 = scaler.to_screen(zone["x"], zone["y"])
            x2, y2 = scaler.to_screen(zone["x"] + zone["w"], zone["y"] + zone["h"])
            canvas.create_rectangle(
                x1, y1, x2, y2, outline="#5fa860", width=2, tags=(self._tag, "build_zone")
            )

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

    def _cleanup_dead(self) -> None:
        """alive==False인 엔티티를 world 목록에서 제거."""
        for key in ("enemies", "allies", "projectiles", "effects"):
            lst = self.world.get(key)
            if isinstance(lst, list):
                self.world[key] = [e for e in lst if getattr(e, "alive", True)]

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
        """전투 종료 처리."""
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

        canvas = self.app.canvas
        scaler = self.app.scaler
        self._result_dialog = ResultDialog(
            canvas,
            scaler,
            victory=victory,
            stats=stats,
            on_next=lambda: self.app.goto("stage_select"),
            on_retry=lambda: self.app.goto("battle"),
            on_menu=lambda: self.app.goto("stage_select"),
        )
        self._result_dialog.show()

    def _refresh_hud(self) -> None:
        """HUD state dict를 구성해서 업데이트."""
        w = self.world
        hero = w.get("hero")
        hero_hp = getattr(hero, "hp", 0) if hero else 0
        hero_max_hp = getattr(hero, "max_hp", max(hero_hp, 1)) if hero else 1
        hero_phase = getattr(hero, "phase", 1) if hero else 1
        ult_cd = 0.0  # 추후 Hero.ult_cooldown으로 교체

        state: dict[str, Any] = {
            "food": w.get("food", w.get("gold", 0)),
            "pop": w.get("pop", w.get("population", 0)),
            "arrows": w.get("arrows", 0),
            "hero_hp": hero_hp,
            "hero_max_hp": hero_max_hp,
            "hero_phase": hero_phase,
            "ult_cooldown_s": ult_cd,
            "wave": self.wave.current_wave,
            "total_waves": len(self.wave.waves),
            "time_to_next": self.wave.time_to_next_wave,
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
        """
        if not self._hero_direct_mode or self._paused or self._game_over:
            return
        keysym = getattr(event, "keysym", None)
        if keysym is None:
            return
        vec = _HERO_DIR_KEYS.get(keysym)
        if vec is None:
            return
        cur_x, cur_y = self._hero_move_dir
        self._hero_move_dir = (cur_x + vec[0], cur_y + vec[1])

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
