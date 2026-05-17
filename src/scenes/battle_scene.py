"""전투 씬 — 게임의 코어.

DESIGN:
- 단일 캔버스 + 오브젝트 풀(미구현 stub) + ``coords()`` 이동 (DECISION-A).
- 시스템은 모두 tk 비의존: ``WaveSystem``, ``CombatSystem``, ``EconomySystem``,
  ``PathingSystem``이 ``update(dt, world)``를 받는다.
- 본 씬은 골격 단계: 스테이지 JSON을 로드해 경로/빌드존을 그리고 placeholder
  텍스트를 표시. 실제 게임 로직은 팀원이 채운다.

EXPECTED: team-member-1이 entities + combat, team-member-2가 wave + spawn + HUD.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.core.logger import get_logger
from src.data.loader import StageDef, load_stage
from src.scenes.base_scene import BaseScene
from src.systems.economy import EconomySystem
from src.systems.wave import WaveSystem

if TYPE_CHECKING:
    from src.core.app import App


class BattleScene(BaseScene):
    """전투 메인 씬.

    World 컨테이너는 ``self.world`` 딕셔너리: 시스템 간 공유되는 단순 가방.
    실제 ECS가 아니라, 시스템이 직접 참조할 엔티티 컬렉션이다.
    """

    SCENE_TAG = "battle"

    def __init__(self, app: "App", stage_id: str = "stage_01") -> None:
        super().__init__(app)
        self._log = get_logger(__name__)
        self.stage_id = stage_id
        self.stage: StageDef | None = None

        # ----- World 컨테이너 (팀원 작업 자리) -----------------------------
        # TODO(team-member-1): entities 컬렉션을 풀로 교체. 현재는 빈 리스트.
        self.world: dict[str, Any] = {
            "enemies": [],  # list[Enemy]
            "allies": [],  # list[Ally]
            "projectiles": [],  # list[Projectile]
            "effects": [],  # list[Effect]
            "hero": None,  # Hero | None
            "gold": 0,
            "population": 0,
            "lives": 0,
            "events": app.events,
        }

        # 시스템 인스턴스(생성만, 실제 로직은 stub).
        self.economy = EconomySystem(self.world)
        self.wave = WaveSystem(self.world)

        self._paused: bool = False
        self._placeholder_id: int | None = None

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------
    def build(self) -> None:
        canvas = self.app.canvas
        w = canvas.winfo_width() or self.app.scaler.canvas_w
        h = canvas.winfo_height() or self.app.scaler.canvas_h

        # 스테이지 데이터 로드.
        try:
            self.stage = load_stage(self.stage_id)
        except FileNotFoundError:
            self._log.warning("stage file missing: %s", self.stage_id)
            self.stage = None

        # 배경.
        canvas.create_rectangle(
            0, 0, w, h, fill="#0c1410", outline="", tags=(self._tag, "bg")
        )

        # 경로 라인(베이스 좌표 → 스크린).
        if self.stage is not None:
            self._draw_paths()
            self._draw_build_zones()
            self.world["gold"] = self.stage.starting_gold
            self.world["population"] = self.stage.starting_population
            self.world["lives"] = self.stage.lives
            self.wave.load(self.stage.waves)

        # placeholder.
        self._placeholder_id = canvas.create_text(
            w / 2,
            h / 2,
            text=(
                "전투 씬 — Phase 2 골격 — 구현 예정\n"
                f"stage: {self.stage_id}    "
                f"waves: {len(self.stage.waves) if self.stage else 0}    "
                "ESC = 메뉴 / Space = 다음 웨이브"
            ),
            fill="#e0d0a0",
            font=("Malgun Gothic", 18, "bold"),
            justify="center",
            tags=(self._tag, "placeholder"),
        )

        # 키 바인딩.
        self.app.root.bind("<Escape>", self._on_escape)
        self.app.root.bind("<space>", self._on_space)

    def update(self, dt: float) -> None:
        if self._paused or self.stage is None:
            return
        # 시스템 갱신. tk 비의존.
        self.wave.update(dt)
        self.economy.update(dt)
        # TODO(team-member-1): combat/pathing/entities update 호출.

    def render(self) -> None:
        # 골격에선 정적. team-member-1이 엔티티 위치 동기화로 채움.
        return

    def teardown(self) -> None:
        super().teardown()
        try:
            self.app.root.unbind("<Escape>")
            self.app.root.unbind("<space>")
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

    def _on_escape(self, _event) -> None:  # type: ignore[no-untyped-def]
        self.app.goto("menu")

    def _on_space(self, _event) -> None:  # type: ignore[no-untyped-def]
        # TODO(team-member-2): WaveSystem.force_next() 호출로 다음 웨이브.
        self._log.info("force next wave requested (stub)")
