"""교육 통합 UI 문자열 (docs/story/08_ui_strings.md §22 SSOT 미러).

DESIGN: 본 게임은 아직 ui_strings 자동 추출 파이프라인이 없어, 각 씬이 표시
텍스트를 모듈 상수로 보유한다(기존 패턴: battle_scene/dialog/hud의 ``_STRINGS``).
교육 후크(H2/H4/H5/H6/H8)는 여러 씬에서 같은 키를 공유하므로 본 모듈에 한데 모아
중복·표기 불일치를 방지한다(R2 라벨 SSOT 준수).

라벨 칩 색(docs/15 R2 / 사용자 지시):
    fact=청 #2D5A8C, fact_adapted=녹 #4A6B3A, legend=황토 #C8954D, fiction=적 #A02E2E.
라벨 표기(codex.label.*)는 본 모듈 ``LABEL_TEXT`` 가 유일 원천.
"""

from __future__ import annotations

# 라벨 표기 (codex.label.*) — R2 SSOT.
LABEL_TEXT: dict[str, str] = {
    "fact": "(사실)",
    "fact_adapted": "(사실)",  # R5: 별도 4번째 라벨 없음. 배지는 (사실), 본문에 각색 고지.
    "legend": "[전승]",
    "fiction": "[픽션]",
}

# 라벨 칩 색 (배경). 사용자 지시 + docs/15 R2.
LABEL_COLOR: dict[str, str] = {
    "fact": "#2D5A8C",
    "fact_adapted": "#4A6B3A",
    "legend": "#C8954D",
    "fiction": "#A02E2E",
}

# 라벨 첫 노출 토스트 (H6, toast.first_*). 기존 키 재사용(§22 R2).
LABEL_TOAST_TEXT: dict[str, str] = {
    "legend": "[전승]은 후대 전승으로 전해진 내용입니다. 정사에 직접 기록은 없습니다.",
    "fiction": "[픽션]은 본 게임이 창작한 보조 인물·장면입니다.",
}

# 결과 카드 (H4, result.card.*).
STRINGS: dict[str, str] = {
    "result.card.title": "새 역사 노트",
    "result.card.new_badge": "NEW",
    "result.card.read_in_codex": "도감에서 읽기",
    "result.win.history_note": "역사 노트가 도감에 추가되었습니다.",
    "toast.codex_unlocked": "역사 노트 해금",
    # 도감 완성도 메타 (H5, codex.progress.*).
    "codex.progress.label": "역사 노트 {current}/15",
    "codex.progress.label_breakdown": "(사실) {fact} · [전승] {legend} · [픽션] {fiction}",
    "codex.progress.milestone_5": "다섯 장을 모았습니다 — 안시성의 이야기를 듣는 이.",
    "codex.progress.milestone_10": "열 장을 모았습니다 — 안시성의 기록자.",
    "codex.progress.milestone_15": "열다섯 장을 모두 모았습니다 — 안시성의 사관(史官).",
    "codex.source.original_toggle": "한문 원문 보기",
    "codex.locked": "아직 해금되지 않은 역사 노트입니다.",
    "codex.title": "역사 노트 도감",
    "codex.back": "뒤로",
    # 충돌 노트 (H8, hero.name_note / codex.conflict.*).
    "hero.name_note": "정사(삼국사기·자치통감)에는 안시성주의 이름이 전하지 않습니다. '양만춘'은 후대 전승입니다.",  # noqa: E501
    "codex.conflict.taizong": "당 태종 부상설은 후대 야사입니다. 정사에는 직접 기록이 없습니다. 자세한 내용은 도감 카드를 보시오.",  # noqa: E501
    "codex.conflict.mound_days": "안시성 공방은 약 88일, 토산 구축은 그 중 60일입니다. 두 숫자는 다른 것을 가리킵니다.",  # noqa: E501
}


def label_text(label: str) -> str:
    """라벨 키 → 표기 문구 (R2 SSOT). 미지정 라벨은 빈 문자열."""
    return LABEL_TEXT.get(label, "")


def label_color(label: str) -> str:
    """라벨 키 → 칩 색. 미지정 라벨은 중립 회색."""
    return LABEL_COLOR.get(label, "#555555")
