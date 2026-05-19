"""전투 씬 — 게임의 코어 (SCN-05).

DESIGN:
- 단일 캔버스 + World 딕셔너리 + 시스템 오케스트레이션.
- update 순서: WaveSystem → PathingSystem → CombatSystem → HUD.
- 패배 조건: hero hp<=0 OR enemy.goal_reached 누적 >= lives.
- 승리 조건: WaveSystem.all_clear AND len(enemies alive)==0.
- Esc/Space → PauseDialog show.
- M키 = 영웅 직접 조작 모드 토글 (OPEN-D-201).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.core.fonts import family_regular as _family_regular
from src.core.logger import get_logger
from src.data.loader import StageDef, load_stage
from src.scenes.base_scene import BaseScene
from src.systems.combat import CombatSystem
from src.systems.economy import EconomySystem
from src.systems.pathing import PathingSystem
from src.systems.wave import WaveSystem
from src.ui.dialog import PauseDialog, ResultDialog
from src.ui.hud import HUD

if TYPE_CHECKING:
    from src.core.app import App


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
        self._hero_direct_mode: bool = False  # M키 토글 (OPEN-D-201)

        self._placeholder_id: int | None = None

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

        # 배경
        canvas.create_rectangle(0, 0, w, h, fill="#0c1410", outline="", tags=(self._tag, "bg"))

        # 경로 / 빌드존
        if self.stage is not None:
            self._draw_paths()
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

        # 키 바인딩
        self.app.root.bind("<Escape>", self._on_escape)
        self.app.root.bind("<space>", self._on_space)
        self.app.root.bind("m", self._on_m_key)
        self.app.root.bind("M", self._on_m_key)

    def update(self, dt: float) -> None:
        if self._paused or self._game_over or self.stage is None:
            return

        # 시스템 갱신 순서 (DESIGN 명세)
        self.wave.update(dt, self.world)
        self.pathing.update(dt)  # PathingSystem uses self.world internally
        self.combat.update(dt, self.world)
        self.economy.update(dt)

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

    def _spawn_enemy(self, enemy_type: str, path_id: str) -> None:
        """WaveSystem의 spawn_callback — 적을 world['enemies']에 추가."""
        try:
            from src.entities.enemy import Enemy

            enemy = Enemy(x=0.0, y=540.0, hp=100)
            enemy.enemy_type = enemy_type
            enemy.path_id = path_id
            self.world["enemies"].append(enemy)
            self._log.debug("spawned %s on %s", enemy_type, path_id)
        except Exception as exc:  # noqa: BLE001
            self._log.warning("spawn_enemy failed: %s", exc)

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
        """M키 = 영웅 직접 조작 모드 토글 (OPEN-D-201)."""
        self._hero_direct_mode = not self._hero_direct_mode
        self._log.info("hero direct mode: %s", "ON" if self._hero_direct_mode else "OFF")

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
