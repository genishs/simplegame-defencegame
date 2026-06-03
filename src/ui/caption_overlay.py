"""도입 역사 캡션 오버레이 (교육 통합 H1 · L1).

DESIGN (docs/15 §3.1, docs/16 §2 Wave1 1-1):
- 스테이지 진입 시 ``StageDef.history_caption`` 을 화면 중앙 1줄로 표시.
- **비모달**: 게임을 일시정지시키지 않는다 (EP1 흐름 보존). 시간 경과로 자동 소멸.
- 페이드: fade-in → hold → fade-out (총 약 2초 + 페이드). 스킵 가능(클릭).
- 본 위젯은 캔버스 아이템만 소유하며 update(dt) 로 알파를 흘린다.
  알파는 tk Canvas 가 직접 지원하지 않으므로 stipple 단계로 근사한다.

도메인 가드: 본 모듈은 ``src/ui`` 에 위치하므로 tkinter 렌더 허용. 캡션 텍스트는
``StageDef.history_caption`` (데이터 정본, src/data/stages/*.json) 에서 주입받는다.
캡션은 (사실)/(사실+각색) 영역 텍스트만 사용한다 (EP2 / QA-EDU-11).

베이스 해상도 1920×1080 기준 좌표.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.fonts import family_bold as _family_bold

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler


# stipple 단계: 알파 근사 (밝을수록 촘촘). 빈 문자열 = 불투명.
_STIPPLE_STEPS: list[str] = ["gray12", "gray25", "gray50", "gray75", ""]


class CaptionOverlay:
    """스테이지 도입 캡션 (H1).

    수명 단계(초):
        fade_in (0.0 ~ 0.5) → hold (0.5 ~ 2.5) → fade_out (2.5 ~ 3.0) → done.

    Args:
        canvas: 대상 Canvas.
        scaler: 좌표/폰트 Scaler (None 이면 raw).
        text: 캡션 텍스트 (``StageDef.history_caption``). 빈 문자열/None 이면
            ``build`` 가 no-op 이 되어 아무것도 그리지 않는다.
        tag: 소속 씬 태그 (teardown 일괄 삭제용).
    """

    TAG: str = "caption_overlay"

    FADE_IN_S: float = 0.5
    HOLD_S: float = 2.0
    FADE_OUT_S: float = 0.5

    def __init__(
        self,
        canvas: tk.Canvas,
        scaler: Scaler | None,
        text: str | None,
        *,
        tag: str | None = None,
    ) -> None:
        self._canvas = canvas
        self._scaler = scaler
        self._text = (text or "").strip()
        self._tag = tag or self.TAG
        self._ids: list[int] = []
        self._elapsed: float = 0.0
        self._active: bool = False
        self._done: bool = bool(not self._text)

    # ------------------------------------------------------------------
    @property
    def active(self) -> bool:
        return self._active

    @property
    def done(self) -> bool:
        return self._done

    def build(self) -> None:
        """캡션 아이템을 캔버스에 생성. 텍스트가 없으면 no-op."""
        if not self._text or self._active or self._done:
            return
        c = self._canvas
        s = self._scaler

        def sx(x: float, y: float) -> tuple[float, float]:
            return s.to_screen(x, y) if s is not None else (x, y)

        def fpt(pt: int) -> int:
            return s.font_pt(pt) if s is not None else pt

        # 반투명 배경 띠 (가독성). 페이드와 함께 흐른다.
        bx1, by1 = sx(360, 470)
        bx2, by2 = sx(1560, 610)
        bg = c.create_rectangle(
            bx1,
            by1,
            bx2,
            by2,
            fill="#0a0805",
            outline="#7a5c2a",
            width=2,
            stipple="gray50",
            tags=(self._tag, self.TAG),
        )
        self._ids.append(bg)

        tx, ty = sx(960, 540)
        text_id = c.create_text(
            tx,
            ty,
            text=self._text,
            fill="#f0e0b0",
            font=(_family_bold(), fpt(22), "bold"),
            anchor="center",
            justify="center",
            width=int((bx2 - bx1) - 60),
            tags=(self._tag, self.TAG),
        )
        self._ids.append(text_id)
        self._active = True
        self._apply_stipple(0)

    def update(self, dt: float) -> None:
        """수명 진행 + 알파(stipple) 갱신. done 이면 no-op."""
        if not self._active or self._done:
            return
        self._elapsed += max(0.0, dt)
        total = self.FADE_IN_S + self.HOLD_S + self.FADE_OUT_S
        if self._elapsed >= total:
            self.dismiss()
            return
        self._apply_stipple(self._alpha_step())

    def _alpha_step(self) -> int:
        """현재 경과에 따른 stipple 단계 인덱스 (0=가장 투명, 마지막=불투명)."""
        steps = len(_STIPPLE_STEPS) - 1
        e = self._elapsed
        if e < self.FADE_IN_S:
            frac = e / self.FADE_IN_S if self.FADE_IN_S > 0 else 1.0
            return max(0, min(steps, int(round(frac * steps))))
        if e < self.FADE_IN_S + self.HOLD_S:
            return steps
        # fade out
        fo_e = e - self.FADE_IN_S - self.HOLD_S
        frac = 1.0 - (fo_e / self.FADE_OUT_S if self.FADE_OUT_S > 0 else 1.0)
        return max(0, min(steps, int(round(frac * steps))))

    def _apply_stipple(self, step_idx: int) -> None:
        stipple = _STIPPLE_STEPS[max(0, min(len(_STIPPLE_STEPS) - 1, step_idx))]
        c = self._canvas
        for item_id in self._ids:
            try:
                c.itemconfig(item_id, stipple=stipple)
            except Exception:  # noqa: BLE001
                pass

    def dismiss(self) -> None:
        """캡션을 즉시 제거 (스킵/만료 공통)."""
        if self._done:
            return
        self._active = False
        self._done = True
        c = self._canvas
        for item_id in self._ids:
            try:
                c.delete(item_id)
            except Exception:  # noqa: BLE001
                pass
        self._ids = []
