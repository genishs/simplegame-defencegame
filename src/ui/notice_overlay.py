"""시간 제한 비모달 공지 위젯 — 적 첫 등장 배너(H2) · 라벨 첫 노출 토스트(H6).

DESIGN (docs/15 §3.1, docs/16 Wave1 1-3·1-4):
- 둘 다 **비모달**(게임 일시정지 없음, EP1) + 시간 경과 자동 소멸.
- H2 IntroBanner: 화면 상단(웨이브 안내 아래) 슬라이드-인 배너. 적 한자명+한 줄+
  약점 힌트(데이터 정본 EnemyDef.intro_banner). 최초 스폰 1회(세션 상태가 판정).
- H6 LabelToast: 화면 하단 토스트. [전승]/[픽션] 라벨 게임 내 최초 1회 설명.

본 모듈은 ``src/ui`` 위치라 tkinter 렌더 허용. "최초 1회" 판정은 여기서 하지 않고
``src/systems/education_state.EducationSessionState`` (tk-free) 가 담당한다(R-5).

여러 공지가 겹칠 수 있으므로 매니저(NoticeManager)가 활성 공지 리스트를 관리하고
update(dt) 로 수명을 흘리며 만료분을 정리한다. 동시에 여러 개가 뜨면 세로로 stack.

베이스 해상도 1920×1080 기준 좌표.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.fonts import family_bold as _family_bold
from src.core.fonts import family_regular as _family_regular

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler


class _Notice:
    """단일 공지(배너/토스트) — 캔버스 아이템 + 수명."""

    def __init__(
        self,
        canvas: tk.Canvas,
        scaler: Scaler | None,
        *,
        tag: str,
        text: str,
        kind: str,
        slot: int,
        lifetime_s: float,
    ) -> None:
        self._canvas = canvas
        self._scaler = scaler
        self._tag = tag
        self.kind = kind
        self._lifetime = lifetime_s
        self._elapsed = 0.0
        self._ids: list[int] = []
        self._done = False
        self._build(text, slot)

    @property
    def done(self) -> bool:
        return self._done

    def _build(self, text: str, slot: int) -> None:
        c = self._canvas
        s = self._scaler

        def sx(x: float, y: float) -> tuple[float, float]:
            return s.to_screen(x, y) if s is not None else (x, y)

        def fpt(pt: int) -> int:
            return s.font_pt(pt) if s is not None else pt

        if self.kind == "banner":
            # 상단 배너(웨이브 HUD 아래 y=96~). slot 마다 84px 아래로 stack.
            y0 = 96 + slot * 84
            bx1, by1 = sx(360, y0)
            bx2, by2 = sx(1560, y0 + 72)
            bg = c.create_rectangle(
                bx1,
                by1,
                bx2,
                by2,
                fill="#1c1206",
                outline="#c8954d",
                width=2,
                tags=(self._tag, "notice_banner"),
            )
            tx, ty = sx(960, y0 + 36)
            txt = c.create_text(
                tx,
                ty,
                text=text,
                fill="#f0dcae",
                font=(_family_bold(), fpt(18), "bold"),
                anchor="center",
                justify="center",
                width=int(bx2 - bx1 - 48),
                tags=(self._tag, "notice_banner"),
            )
            self._ids.extend([bg, txt])
        else:
            # 하단 토스트(y=940~). slot 마다 위로 stack.
            y0 = 952 - slot * 72
            bx1, by1 = sx(560, y0)
            bx2, by2 = sx(1360, y0 + 60)
            bg = c.create_rectangle(
                bx1,
                by1,
                bx2,
                by2,
                fill="#12100a",
                outline="#a88a5c",
                width=2,
                tags=(self._tag, "notice_toast"),
            )
            tx, ty = sx(960, y0 + 30)
            txt = c.create_text(
                tx,
                ty,
                text=text,
                fill="#e8d8b0",
                font=(_family_regular(), fpt(15)),
                anchor="center",
                justify="center",
                width=int(bx2 - bx1 - 40),
                tags=(self._tag, "notice_toast"),
            )
            self._ids.extend([bg, txt])

    def update(self, dt: float) -> None:
        if self._done:
            return
        self._elapsed += max(0.0, dt)
        if self._elapsed >= self._lifetime:
            self.dismiss()

    def dismiss(self) -> None:
        if self._done:
            return
        self._done = True
        for item_id in self._ids:
            try:
                self._canvas.delete(item_id)
            except Exception:  # noqa: BLE001
                pass
        self._ids = []


class NoticeManager:
    """활성 공지(배너/토스트) 관리 — 생성·수명·정리.

    렌더만 담당. "최초 1회" 판정은 EducationSessionState 가 호출 측에서 수행한 뒤
    show_* 를 호출한다.
    """

    BANNER_LIFETIME_S: float = 3.0
    TOAST_LIFETIME_S: float = 4.0

    def __init__(self, canvas: tk.Canvas, scaler: Scaler | None, *, tag: str) -> None:
        self._canvas = canvas
        self._scaler = scaler
        self._tag = tag
        self._notices: list[_Notice] = []

    @property
    def active_count(self) -> int:
        return len([n for n in self._notices if not n.done])

    def _slot_for(self, kind: str) -> int:
        return len([n for n in self._notices if not n.done and n.kind == kind])

    def show_banner(self, text: str) -> _Notice | None:
        """H2 적 첫 등장 배너. 빈 텍스트면 생략(graceful)."""
        if not text:
            return None
        notice = _Notice(
            self._canvas,
            self._scaler,
            tag=self._tag,
            text=text,
            kind="banner",
            slot=self._slot_for("banner"),
            lifetime_s=self.BANNER_LIFETIME_S,
        )
        self._notices.append(notice)
        return notice

    def show_toast(self, text: str) -> _Notice | None:
        """H6 라벨 첫 노출 토스트. 빈 텍스트면 생략."""
        if not text:
            return None
        notice = _Notice(
            self._canvas,
            self._scaler,
            tag=self._tag,
            text=text,
            kind="toast",
            slot=self._slot_for("toast"),
            lifetime_s=self.TOAST_LIFETIME_S,
        )
        self._notices.append(notice)
        return notice

    def update(self, dt: float) -> None:
        for n in self._notices:
            n.update(dt)
        self._notices = [n for n in self._notices if not n.done]

    def clear(self) -> None:
        for n in self._notices:
            n.dismiss()
        self._notices = []
