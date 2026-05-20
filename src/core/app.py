"""App: 씬 라우터 + 글로벌 서비스 컨테이너.

DESIGN: ``App``은 root Tk를 받아 글로벌 서비스(events/assets/scaler/sound)를
구성하고, 현재 활성 씬에게 ``update(dt)``를 위임한다. 씬 전환은 단순
"이전 씬 teardown → 새 씬 build" 모델.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import TYPE_CHECKING

from src.core.assets import AssetManager
from src.core.events import EventBus
from src.core.fonts import register_korean_fonts
from src.core.game_loop import GameLoop
from src.core.logger import get_logger
from src.core.scaler import Scaler
from src.core.settings import APP_TITLE, SETTINGS
from src.core.sound import SoundManager

if TYPE_CHECKING:
    from src.scenes.base_scene import BaseScene


SceneFactory = Callable[["App"], "BaseScene"]


class App:
    """게임 애플리케이션 컨테이너.

    Attributes:
        root: 최상위 Tk 윈도우.
        canvas: 단일 게임 캔버스(모든 씬이 공유).
        events: 글로벌 이벤트 버스.
        assets: 이미지 캐시.
        scaler: 좌표/폰트 스케일러.
        sound: 사운드 매니저(현재 no-op).
        loop: GameLoop 인스턴스.
        current_scene: 활성 씬 또는 None.
    """

    def __init__(self, root: tk.Tk) -> None:
        self._log = get_logger(__name__)
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{SETTINGS.window_width}x{SETTINGS.window_height}")
        self.root.minsize(800, 450)

        # DECISION-Q-007 / Issue #7: 번들된 Noto Sans KR 을 프로세스에 등록.
        # 실패 시 Malgun Gothic 으로 자동 폴백(`src.core.fonts.family_*()`).
        try:
            register_korean_fonts(self.root)
        except Exception:  # noqa: BLE001
            self._log.exception("Korean font registration failed; falling back")

        # 단일 캔버스(DECISION-A): 모든 씬이 이 캔버스를 공유.
        self.canvas = tk.Canvas(
            self.root,
            width=SETTINGS.window_width,
            height=SETTINGS.window_height,
            bg="#101010",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # 글로벌 서비스.
        self.events = EventBus()
        self.assets = AssetManager()
        self.scaler = Scaler()
        self.sound = SoundManager()

        # 씬.
        self.current_scene: BaseScene | None = None
        self._scene_factories: dict[str, SceneFactory] = {}

        # 메인 루프.
        self.loop = GameLoop(self.root, self._tick)

        # DECISION-DL-P4D-005 (Issue #51): _tick() 반복 예외 시 frozen 회피.
        # 동일 예외가 연속 N회 발생하면 사용자에게 에러 메시지를 캔버스에 표시하고
        # 메뉴 복귀 안내를 제공한다. silently catch 만으로는 사용자가 frozen 으로
        # 인지할 수밖에 없는 결함(검수 결함 2호) 의 신뢰성 보강.
        self._tick_error_streak: int = 0
        self._tick_error_signature: str | None = None
        self._tick_error_banner_id: int | None = None

        # 종료/리사이즈 훅.
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.canvas.bind("<Configure>", self._on_configure)

    # ------------------------------------------------------------------
    # 씬 라우팅
    # ------------------------------------------------------------------
    def register_scene(self, name: str, factory: SceneFactory) -> None:
        """씬 이름과 팩토리를 등록. 팩토리는 ``App``을 받아 씬을 반환."""
        self._scene_factories[name] = factory

    def goto(self, name: str) -> None:
        """등록된 씬으로 전환."""
        factory = self._scene_factories.get(name)
        if factory is None:
            raise KeyError(f"unknown scene: {name!r}")
        self._log.info("scene transition -> %s", name)
        if self.current_scene is not None:
            try:
                self.current_scene.teardown()
            except Exception:  # noqa: BLE001
                self._log.exception("scene teardown failed")
        self.canvas.delete("all")
        # DECISION-DL-P4D-005: 씬 전환 시 tick 에러 배너/상태 리셋.
        self._tick_error_streak = 0
        self._tick_error_signature = None
        self._tick_error_banner_id = None  # canvas.delete("all") 이 아이템을 제거함.
        self.current_scene = factory(self)
        self.current_scene.build()

    # ------------------------------------------------------------------
    # 실행 / 종료
    # ------------------------------------------------------------------
    def run(self, initial_scene: str) -> None:
        """초기 씬 진입 + 메인 루프 시작 + ``mainloop()``."""
        self.goto(initial_scene)
        self.loop.start()
        self.root.mainloop()

    def quit(self) -> None:
        """정상 종료."""
        self._log.info("quit requested")
        self.loop.stop()
        try:
            if self.current_scene is not None:
                self.current_scene.teardown()
        except Exception:  # noqa: BLE001
            self._log.exception("scene teardown on quit failed")
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # 내부 콜백
    # ------------------------------------------------------------------
    # DECISION-DL-P4D-005: 동일 예외 연속 발생 임계. 60FPS 기준 약 0.05초 분량.
    _TICK_ERROR_BANNER_THRESHOLD: int = 3

    def _tick(self, dt: float) -> None:
        scene = self.current_scene
        if scene is None:
            return
        try:
            scene.update(dt)
            scene.render()
        except Exception as exc:  # noqa: BLE001
            # 한 프레임 예외가 게임 전체를 종료시키지 않도록 격리.
            self._log.exception("scene tick failed")
            # DECISION-DL-P4D-005 (Issue #51): 같은 예외가 연속 반복되면 frozen
            # 상태로 보인다. 임계 초과 시 캔버스에 에러 배너를 한 번만 그려서
            # 사용자가 무엇이 잘못되었는지 인지하고 메뉴로 복귀하도록 안내한다.
            signature = f"{type(exc).__name__}:{exc}"
            if signature == self._tick_error_signature:
                self._tick_error_streak += 1
            else:
                self._tick_error_signature = signature
                self._tick_error_streak = 1
            if (
                self._tick_error_streak >= self._TICK_ERROR_BANNER_THRESHOLD
                and self._tick_error_banner_id is None
            ):
                self._show_tick_error_banner(signature)
        else:
            # 정상 tick 한 번이면 streak 리셋.
            if self._tick_error_streak > 0:
                self._tick_error_streak = 0
                self._tick_error_signature = None
                self._clear_tick_error_banner()

    def _show_tick_error_banner(self, signature: str) -> None:
        """반복 예외 발생 시 사용자에게 에러 배너 표시 (DECISION-DL-P4D-005)."""
        try:
            w = self.canvas.winfo_width() or self.scaler.canvas_w
            h = self.canvas.winfo_height() or self.scaler.canvas_h
            text = (
                "⚠ 내부 오류가 반복 발생했습니다.\n"
                f"({signature})\n"
                "ESC 키로 일시정지 후 메뉴로 돌아가거나 게임을 다시 실행하시오."
            )
            self._tick_error_banner_id = self.canvas.create_text(
                w / 2,
                h / 2,
                text=text,
                fill="#ff8a6a",
                font=("", 14, "bold"),
                justify="center",
                tags=("__app_tick_error_banner",),
            )
        except Exception:  # noqa: BLE001
            self._log.exception("failed to render tick error banner")

    def _clear_tick_error_banner(self) -> None:
        if self._tick_error_banner_id is not None:
            try:
                self.canvas.delete(self._tick_error_banner_id)
            except Exception:  # noqa: BLE001
                pass
            self._tick_error_banner_id = None

    def _on_configure(self, event: tk.Event[tk.Canvas]) -> None:
        if event.widget is not self.canvas:
            return
        ratio_x, ratio_y = self.scaler.update(event.width, event.height)
        # 기존 캔버스 아이템 좌표 보정. 신생 캔버스이거나 ratio≈1이면 skip.
        if abs(ratio_x - 1.0) > 1e-6:
            self.canvas.scale("all", 0, 0, ratio_x, ratio_y)
        if self.current_scene is not None:
            try:
                self.current_scene.on_resize(event.width, event.height)
            except Exception:  # noqa: BLE001
                self._log.exception("scene on_resize failed")
