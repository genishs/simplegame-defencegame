"""진입점: DPI 인식 설정 → root Tk 생성 → App 구성 → 메인 씬으로 진입.

실행: ``python -m src.main`` 또는 ``python src/main.py``.
"""

from __future__ import annotations

import sys

from src.core.app import App
from src.core.logger import get_logger, setup_logging


def _enable_dpi_awareness() -> None:
    """Windows에서 흐릿한 출력을 방지(DECISION-3.2). 다른 OS는 no-op."""
    if sys.platform != "win32":
        return
    import ctypes  # 지연 import: 비Windows에서 무용

    # Per-Monitor V2 (-4) → V1 (2) → SystemDPIAware 의 단계적 폴백.
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
        return
    except (AttributeError, OSError):
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except (AttributeError, OSError):
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        # 모두 실패해도 게임은 동작해야 한다.
        pass


def _register_scenes(app: App) -> None:
    """모든 씬을 App에 등록. 임포트 위치를 좁혀 순환을 방지."""
    from src.scenes.battle_scene import BattleScene
    from src.scenes.ending_scene import EndingScene
    from src.scenes.menu_scene import MenuScene
    from src.scenes.stage_select_scene import StageSelectScene
    from src.scenes.tutorial_scene import TutorialScene

    app.register_scene("menu", MenuScene)
    app.register_scene("stage_select", StageSelectScene)
    app.register_scene("battle", BattleScene)
    app.register_scene("ending", EndingScene)
    # Phase 4 / Issue #26 — 튜토리얼 (DECISION-DL-P4-003).
    app.register_scene("tutorial", TutorialScene)


def _resolve_initial_scene() -> str:
    """저장 슬롯 검사 후 첫 씬 결정 (DECISION-DL-P4-003).

    - 저장 슬롯이 비어 있고 ``tutorial_dismissed`` 가 아니면 ``tutorial``.
    - 그 외에는 ``menu``.
    """
    from src.scenes.tutorial_scene import decide_initial_scene

    return decide_initial_scene(default_scene="menu")


def main() -> int:
    """엔트리. 정상 종료 시 0 반환."""
    setup_logging()
    log = get_logger(__name__)

    _enable_dpi_awareness()

    # tk import는 DPI 설정 이후가 안전(일부 환경 보고).
    import tkinter as tk

    root = tk.Tk()
    app = App(root)
    _register_scenes(app)

    initial = _resolve_initial_scene()
    log.info("initial scene resolved: %s", initial)

    try:
        app.run(initial_scene=initial)
    except KeyboardInterrupt:
        log.info("interrupted by user")
        app.quit()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
