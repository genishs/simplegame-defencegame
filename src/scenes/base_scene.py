"""씬 추상 베이스.

DESIGN: 씬은 lifecycle 4 단계(build/update/render/teardown)와 1 콜백
(on_resize)을 가진다. 캔버스는 App이 소유하고 모든 씬이 공유 — 씬은
``app.canvas``에 자신의 태그(``self._tag``)로 아이템을 그리고, teardown에서
태그로 일괄 ``delete``.
EXPECTED: lead 골격. 팀원은 메서드를 override.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.app import App


class BaseScene:
    """모든 씬의 베이스. 자체 캔버스 태그를 보유해 teardown 시 청소.

    Attributes:
        app: 부모 App.
        _tag: 본 씬이 캔버스에 그리는 모든 아이템의 공통 태그.
    """

    #: 서브클래스가 override. ``app.canvas.delete(tag)``에 사용된다.
    SCENE_TAG: str = "scene"

    def __init__(self, app: "App") -> None:
        self.app = app
        self._tag: str = self.SCENE_TAG

    # ------------------------------------------------------------------
    # lifecycle — 서브클래스 override
    # ------------------------------------------------------------------
    def build(self) -> None:
        """씬 진입. 캔버스 위에 정적 요소를 한 번 그린다."""

    def update(self, dt: float) -> None:
        """매 틱 시뮬레이션 갱신."""

    def render(self) -> None:
        """매 틱 렌더링(이동/상태 반영). 정적 요소는 ``build``에서 그릴 것."""

    def teardown(self) -> None:
        """씬 이탈. 캔버스에서 본 씬의 아이템을 모두 삭제."""
        try:
            self.app.canvas.delete(self._tag)
        except Exception:  # noqa: BLE001
            pass

    def on_resize(self, width: int, height: int) -> None:
        """캔버스 크기 변경. 기본 동작은 no-op."""
