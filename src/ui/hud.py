"""HUD (자원/웨이브/영웅 HP 상단 바 + 영웅 패널).

DESIGN-D-009: 색약 모드 ON 시 자원 아이콘에 흑백 보조 글리프 병기.
DESIGN-D-207: HUD 카운트 갱신은 itemconfig만 사용 (재생성 금지).
DESIGN-D-205: 보스 페이즈 전환 시 흰 플래시 1프레임 콜백 노출.

베이스 해상도 1920×1080 기준 좌표 → scaler.to_screen() 변환.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.core.fonts import family_bold as _family_bold
from src.core.fonts import family_regular as _family_regular

if TYPE_CHECKING:
    import tkinter as tk

    from src.core.scaler import Scaler

# ---------------------------------------------------------------------------
# UI 문자열 (docs/story/08_ui_strings.md §3)
# ---------------------------------------------------------------------------
_DEFAULT_STRINGS: dict[str, str] = {
    "hud.grain": "곡식",
    "hud.population": "인구",
    "hud.arrows": "화살",
    "hud.wave_progress": "진군",
    "hud.next_wave_in": "다음",
    "hud.castle": "성문",
    "hud.speed.pause": "||",
    "hud.speed.1x": "1×",
    "hud.speed.2x": "2×",
    "hero.name_label": "양만춘",
    "hero.hp": "HP",
    "hero.ultimate": "R",
}

# 색약 모드용 보조 글리프 (DECISION-D-009 / DECISION-D-111)
_MONO_GLYPHS: dict[str, str] = {
    "hud.grain": "穀",
    "hud.population": "民",
    "hud.arrows": "矢",
}


class HUD:
    """전투 화면 HUD.

    캔버스 아이템은 build() 에서 한 번만 생성하고,
    update(state) 에서 itemconfig 만으로 값을 갱신한다.
    """

    TAG: str = "hud"

    def __init__(self) -> None:
        self._canvas: tk.Canvas | None = None
        self._scaler: Scaler | None = None
        self._strings: dict[str, str] = dict(_DEFAULT_STRINGS)
        self._color_blind_mode: bool = False

        # Canvas item id 저장소
        self._ids: dict[str, int] = {}

        # 보스 페이즈 플래시 콜백
        self._flash_callback: Any = None

    # ------------------------------------------------------------------
    # build
    # ------------------------------------------------------------------

    def build(
        self,
        canvas: tk.Canvas,
        scaler: Scaler,
        ui_strings: dict[str, str] | None = None,
        *,
        color_blind_mode: bool = False,
        on_pause_click: Any = None,
    ) -> None:
        """캔버스 위에 HUD 아이템을 생성한다. 한 번만 호출.

        Args:
            canvas: 대상 Canvas.
            scaler: 좌표/폰트 변환용 Scaler.
            ui_strings: KEY → 표시 텍스트 매핑. None이면 기본값 사용.
            color_blind_mode: 색약 모드 여부.
            on_pause_click: 일시정지 버튼 콜백.
        """
        self._canvas = canvas
        self._scaler = scaler
        self._color_blind_mode = color_blind_mode
        if ui_strings:
            self._strings.update(ui_strings)

        s = scaler
        c = canvas
        tag = self.TAG

        def sx(bx: float, by: float) -> tuple[float, float]:
            return s.to_screen(bx, by)

        def fpt(pt: int) -> int:
            return s.font_pt(pt)

        def font(pt: int, bold: bool = False) -> tuple[str, int, str]:
            style = "bold" if bold else "normal"
            family = _family_bold() if bold else _family_regular()
            return (family, fpt(pt), style)

        # ── 상단 HUD 배경 (y=0~80) ──────────────────────────────────────
        x1, y1 = sx(0, 0)
        x2, y2 = sx(1920, 80)
        self._ids["hud_bg"] = c.create_rectangle(
            x1, y1, x2, y2, fill="#1a1208", outline="#3a2a10", tags=(tag,)
        )

        # ── 자원 3종 (곡식·인구·화살) ────────────────────────────────────
        res_defs = [
            ("grain", "hud.grain", 16, "#e8c860"),
            ("pop", "hud.population", 210, "#88ddaa"),
            ("arrows", "hud.arrows", 380, "#aaccff"),
        ]
        for key, str_key, bx, clr in res_defs:
            lx, ly = sx(bx, 16)
            label = self._strings.get(str_key, str_key)
            if self._color_blind_mode:
                glyph = _MONO_GLYPHS.get(str_key, "")
                label = f"{label} {glyph}" if glyph else label

            self._ids[f"{key}_label"] = c.create_text(
                lx, ly, text=label, fill=clr, font=font(14), anchor="nw", tags=(tag,)
            )
            vx, vy = sx(bx + 48, 40)
            self._ids[f"{key}_val"] = c.create_text(
                vx, vy, text="0", fill="#f0e0c0", font=font(20, bold=True), anchor="center", tags=(tag,)
            )

        # ── 구분선 ──────────────────────────────────────────────────────
        lx1, ly1 = sx(580, 20)
        lx2, ly2 = sx(580, 60)
        self._ids["sep1"] = c.create_line(lx1, ly1, lx2, ly2, fill="#5a4a30", tags=(tag,))

        # ── 성문 HP(lives) — Issue #75 / DECISION-DL-P5C-008 ────────────
        # 적이 castle 도달 시 lives 가 차감된다. 패배 조건(코어 HP=0)을 사용자가
        # 체감하도록 상단 바에 성문 HP 게이지 + 숫자를 표시. 자원 영역(우측) 과
        # 웨이브 진행(x=1120) 사이의 빈 공간(x=620~860)에 배치.
        clx, cly = sx(632, 16)
        self._ids["castle_label"] = c.create_text(
            clx,
            cly,
            text=self._strings.get("hud.castle", "성문"),
            fill="#e08858",
            font=font(14),
            anchor="nw",
            tags=(tag,),
        )
        # 성문 HP 바 배경 + 채움
        cbg_x1, cbg_y1 = sx(632, 40)
        cbg_x2, cbg_y2 = sx(840, 60)
        self._ids["castle_hp_bg"] = c.create_rectangle(
            cbg_x1, cbg_y1, cbg_x2, cbg_y2, fill="#3a1810", outline="#6a3018", tags=(tag,)
        )
        self._ids["castle_hp_bar"] = c.create_rectangle(
            cbg_x1, cbg_y1, cbg_x2, cbg_y2, fill="#d07038", outline="", tags=(tag,)
        )
        # 성문 HP 숫자 (바 위 중앙)
        cvx, cvy = sx(736, 50)
        self._ids["castle_hp_val"] = c.create_text(
            cvx, cvy, text="--/--", fill="#ffe0c0", font=font(12, bold=True), anchor="center", tags=(tag,)
        )

        # ── 웨이브 진행 (HUD-12) — Issue #70 풀어쓰기 라벨 ──────────────
        wx, wy = sx(1120, 40)
        self._ids["wave_progress"] = c.create_text(
            wx,
            wy,
            text="웨이브 시작 대기 / 총 0",
            fill="#f0c060",
            font=font(18, bold=True),
            anchor="center",
            tags=(tag,),
        )

        # ── 다음 진군 카운트다운 (HUD-13) — Issue #70 풀어쓰기 ─────────
        nx, ny = sx(1380, 40)
        self._ids["next_wave"] = c.create_text(
            nx,
            ny,
            text="다음 진군 -- 초 후",
            fill="#a0c0e0",
            font=font(16),
            anchor="center",
            tags=(tag,),
        )

        # ── 일시정지 버튼 (HUD-09) ─────────────────────────────────────
        px1, py1 = sx(920, 16)
        px2, py2 = sx(980, 64)
        self._ids["pause_btn"] = c.create_rectangle(
            px1, py1, px2, py2, fill="#2a2010", outline="#8a7040", tags=(tag,)
        )
        pcx, pcy = sx(950, 40)
        self._ids["pause_label"] = c.create_text(
            pcx, pcy, text="||", fill="#e0d0a0", font=font(16, bold=True), anchor="center", tags=(tag,)
        )
        if on_pause_click is not None:
            c.tag_bind(self._ids["pause_btn"], "<Button-1>", lambda _e: on_pause_click())
            c.tag_bind(self._ids["pause_label"], "<Button-1>", lambda _e: on_pause_click())

        # ── 영웅 패널 배경 (HRO-01, 우패널 y=290~610) ─────────────────
        hx1, hy1 = sx(1620, 290)
        hx2, hy2 = sx(1900, 610)
        self._ids["hero_panel"] = c.create_rectangle(
            hx1, hy1, hx2, hy2, fill="#1a1208", outline="#5a4a30", width=2, tags=(tag,)
        )

        # 영웅 이름
        hnx, hny = sx(1760, 315)
        self._ids["hero_name"] = c.create_text(
            hnx,
            hny,
            text=self._strings.get("hero.name_label", "양만춘"),
            fill="#f0d080",
            font=font(18, bold=True),
            anchor="center",
            tags=(tag,),
        )

        # 영웅 HP 바 배경
        hpbg_x1, hpbg_y1 = sx(1636, 350)
        hpbg_x2, hpbg_y2 = sx(1896, 374)
        self._ids["hero_hp_bg"] = c.create_rectangle(
            hpbg_x1, hpbg_y1, hpbg_x2, hpbg_y2, fill="#440000", outline="#660000", tags=(tag,)
        )
        self._ids["hero_hp_bar"] = c.create_rectangle(
            hpbg_x1, hpbg_y1, hpbg_x2, hpbg_y2, fill="#aa3333", outline="", tags=(tag,)
        )

        # 영웅 HP 숫자
        hpvx, hpvy = sx(1760, 385)
        self._ids["hero_hp_val"] = c.create_text(
            hpvx, hpvy, text="HP: ---", fill="#ddaaaa", font=font(14), anchor="center", tags=(tag,)
        )

        # 영웅 페이즈 표시
        hphx, hphy = sx(1760, 410)
        self._ids["hero_phase"] = c.create_text(
            hphx, hphy, text="Phase 1", fill="#c8a050", font=font(14), anchor="center", tags=(tag,)
        )

        # 궁극기 쿨다운 슬롯 R
        rsx, rsy = sx(1640, 430)
        rex, rey = sx(1700, 490)
        self._ids["ult_slot_bg"] = c.create_rectangle(
            rsx, rsy, rex, rey, fill="#2a1a0c", outline="#8a6a30", tags=(tag,)
        )
        rcx, rcy = sx(1670, 460)
        self._ids["ult_label"] = c.create_text(
            rcx, rcy, text="R", fill="#e0c060", font=font(18, bold=True), anchor="center", tags=(tag,)
        )
        self._ids["ult_cooldown"] = c.create_text(
            rcx, sx(1670, 480)[1], text="", fill="#aaaaaa", font=font(11), anchor="center", tags=(tag,)
        )

        # 보스 페이즈 플래시 오버레이 (기본 hidden)
        ox1, oy1 = sx(0, 0)
        ox2, oy2 = sx(1920, 1080)
        self._ids["flash_overlay"] = c.create_rectangle(
            ox1, oy1, ox2, oy2, fill="white", outline="", state="hidden", tags=(tag,)
        )

    # ------------------------------------------------------------------
    # update
    # ------------------------------------------------------------------

    def update(self, state: dict[str, Any]) -> None:
        """state 딕셔너리로 HUD 값을 갱신한다 (itemconfig만 사용).

        state 키:
            food (int), pop (int), arrows (int),
            hero_hp (int), hero_max_hp (int), hero_phase (int),
            ult_cooldown_s (float),
            wave (int), total_waves (int), time_to_next (float)
        """
        if self._canvas is None:
            return

        c = self._canvas
        ids = self._ids
        s = self._scaler

        # 자원 값
        food = state.get("food", state.get("gold", 0))
        pop = state.get("pop", state.get("population", 0))
        arrows = state.get("arrows", 0)

        if "grain_val" in ids:
            c.itemconfig(ids["grain_val"], text=str(food))
        if "pop_val" in ids:
            c.itemconfig(ids["pop_val"], text=str(pop))
        if "arrows_val" in ids:
            c.itemconfig(ids["arrows_val"], text=str(arrows))

        # 웨이브 진행
        wave = state.get("wave", 0)
        total = state.get("total_waves", 0)
        time_to_next = state.get("time_to_next", -1.0)

        # Issue #70 (DECISION-DL-P4D-011): wave 표시 명확화.
        # rc.6 사용자 검수: "웨이브 3" 표시가 "총 3번" 인지 "3번째" 인지 모호.
        # 풀어쓰기 "현재 N / 전체 M" 으로 의미를 명확히 한다.
        # 게임 시작 직후 wave=0 (대기) 인 동안은 "곧 시작" 표기.
        if "wave_progress" in ids:
            if wave <= 0:
                wave_text = f"웨이브 시작 대기 / 총 {total}"
            else:
                wave_text = f"웨이브 {wave} / 총 {total}"
            c.itemconfig(ids["wave_progress"], text=wave_text)

        if "next_wave" in ids:
            # Issue #70: 다음 웨이브 카운트다운 표기도 풀어쓰기.
            if time_to_next > 0:
                c.itemconfig(ids["next_wave"], text=f"다음 진군 {time_to_next:.0f}초 후")
            elif time_to_next == 0:
                c.itemconfig(ids["next_wave"], text="진군 진행 중")
            else:
                c.itemconfig(ids["next_wave"], text="진군 종료")

        # 성문 HP(lives) — Issue #75 / DECISION-DL-P5C-008
        # castle_hp = 남은 lives (lives - goals_reached), castle_max_hp = 초기 lives.
        castle_hp = state.get("castle_hp")
        castle_max_hp = state.get("castle_max_hp")
        if castle_hp is not None and castle_max_hp is not None:
            castle_hp = max(0, int(castle_hp))
            castle_max_hp = max(1, int(castle_max_hp))
            if "castle_hp_val" in ids:
                c.itemconfig(ids["castle_hp_val"], text=f"{castle_hp}/{castle_max_hp}")
            if "castle_hp_bar" in ids and s is not None:
                ratio = max(0.0, min(1.0, castle_hp / castle_max_hp))
                bx1, by1 = s.to_screen(632, 40)
                bx2, by2 = s.to_screen(840, 60)
                bar_w = (bx2 - bx1) * ratio
                c.coords(ids["castle_hp_bar"], bx1, by1, bx1 + bar_w, by2)
                # 위험(30% 이하)이면 진한 적색으로 경고
                c.itemconfig(ids["castle_hp_bar"], fill="#d07038" if ratio > 0.3 else "#dd3322")

        # 영웅 HP
        hero_hp = state.get("hero_hp", 0)
        hero_max_hp = state.get("hero_max_hp", max(hero_hp, 1))
        if "hero_hp_val" in ids:
            c.itemconfig(ids["hero_hp_val"], text=f"HP: {hero_hp}/{hero_max_hp}")

        # HP 바 비율
        if "hero_hp_bar" in ids and s is not None and hero_max_hp > 0:
            ratio = max(0.0, min(1.0, hero_hp / hero_max_hp))
            bx1, by1 = s.to_screen(1636, 350)
            bx2, by2 = s.to_screen(1896, 374)
            bar_w = (bx2 - bx1) * ratio
            c.coords(ids["hero_hp_bar"], bx1, by1, bx1 + bar_w, by2)
            bar_clr = "#aa3333" if ratio > 0.3 else "#dd2222"
            c.itemconfig(ids["hero_hp_bar"], fill=bar_clr)

        # 영웅 페이즈
        hero_phase = state.get("hero_phase", 1)
        if "hero_phase" in ids:
            c.itemconfig(ids["hero_phase"], text=f"Phase {hero_phase}")

        # 궁극기 쿨다운
        ult_cd = state.get("ult_cooldown_s", 0.0)
        if "ult_cooldown" in ids:
            if ult_cd > 0:
                c.itemconfig(ids["ult_cooldown"], text=f"{ult_cd:.0f}s")
                c.itemconfig(ids["ult_slot_bg"], fill="#2a1a0c")
            else:
                c.itemconfig(ids["ult_cooldown"], text="준비")
                c.itemconfig(ids["ult_slot_bg"], fill="#3a2a0c")

    # ------------------------------------------------------------------
    # 보스 페이즈 플래시 (DECISION-D-205)
    # ------------------------------------------------------------------

    def trigger_boss_phase_flash(self) -> None:
        """보스 페이즈 전환 시 흰 플래시 1프레임 토글."""
        if self._canvas is None:
            return
        ids = self._ids
        if "flash_overlay" in ids:
            self._canvas.itemconfig(ids["flash_overlay"], state="normal")
            # 80ms 후 숨김
            self._canvas.after(80, lambda: self._hide_flash())

    def _hide_flash(self) -> None:
        if self._canvas is None:
            return
        ids = self._ids
        if "flash_overlay" in ids:
            try:
                self._canvas.itemconfig(ids["flash_overlay"], state="hidden")
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------------
    # 성문 피격 플래시 (Issue #75 / DECISION-DL-P5C-008)
    # ------------------------------------------------------------------

    def flash_castle_damage(self) -> None:
        """적이 castle 에 도달해 lives 가 차감될 때 성문 HP 게이지를 번쩍인다.

        성문 HP 바 배경을 붉게 번쩍여(180ms) 사용자가 차감을 즉시 체감하게 한다.
        BattleScene 이 breach 발생 시 호출.
        """
        if self._canvas is None:
            return
        ids = self._ids
        if "castle_hp_bg" not in ids:
            return
        c = self._canvas
        try:
            c.itemconfig(ids["castle_hp_bg"], fill="#ff5530", outline="#ffaa66")
            c.after(180, self._reset_castle_bg)
        except Exception:  # noqa: BLE001
            pass

    def _reset_castle_bg(self) -> None:
        if self._canvas is None:
            return
        ids = self._ids
        if "castle_hp_bg" in ids:
            try:
                self._canvas.itemconfig(ids["castle_hp_bg"], fill="#3a1810", outline="#6a3018")
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------------
    # teardown
    # ------------------------------------------------------------------

    def teardown(self) -> None:
        """HUD 아이템 전부 삭제."""
        if self._canvas is None:
            return
        try:
            self._canvas.delete(self.TAG)
        except Exception:  # noqa: BLE001
            pass
        self._ids = {}
