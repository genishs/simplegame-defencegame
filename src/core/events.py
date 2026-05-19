"""단순 pub/sub 이벤트 버스.

DESIGN: 도메인 이벤트(예: ``enemy.killed``, ``wave.cleared``)는 문자열 키로
이름 짓고, 핸들러는 ``(payload: dict) -> None`` 시그니처를 가진다.
스레드 안전성은 보장하지 않는다(tkinter 메인 스레드 단일 호출 전제).
EXPECTED: lead 기본 구현, team-member-1/2가 이벤트명을 추가/구독.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

EventHandler = Callable[[dict[str, Any]], None]


class EventBus:
    """가벼운 pub/sub.

    핸들러 호출 중 예외는 다른 구독자를 막지 않도록 격리한다.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """이벤트 구독."""
        self._handlers.setdefault(event_name, []).append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        """구독 해제. 등록되지 않은 핸들러는 무시."""
        if event_name in self._handlers:
            try:
                self._handlers[event_name].remove(handler)
            except ValueError:
                pass

    def publish(self, event_name: str, payload: dict[str, Any] | None = None) -> None:
        """이벤트 발행. 핸들러 예외는 잡아 stderr로 흘려보낸다."""
        from src.core.logger import get_logger

        log = get_logger(__name__)
        for h in list(self._handlers.get(event_name, ())):
            try:
                h(payload or {})
            except Exception:  # noqa: BLE001
                log.exception("event handler failed: %s", event_name)

    def clear(self) -> None:
        """모든 구독을 비운다(테스트 / 씬 전환 헬퍼)."""
        self._handlers.clear()
