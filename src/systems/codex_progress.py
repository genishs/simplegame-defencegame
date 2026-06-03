"""코덱스 해금/진행도 로직 — tkinter 비의존 (교육 통합 H4/H5).

DESIGN (docs/15 §3.2·§3.4·§6.1, docs/16 Wave2 2-2·Wave3 3-2):
- 해금 매핑: ``CodexCard.unlock`` (auto/stage_clear/stage_three_stars/true_ending)
  를 클리어 이벤트(스테이지 id + 별 수)에 대응시켜 "지금 해금되는 카드"를 계산.
- 진행도: 획득 카드 집합 기준 완성도(N/15)·라벨 분포·칭호(5/10/15).
- 진행 상태(획득 카드 id 집합)는 로컬 세이브 슬롯에 영속(DECISION-EDU-004 오프라인).

순수 로직만. 렌더(ui/scenes)·저장 I/O(core.save_slot)는 호출자가 결합한다.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from src.data.loader import CodexCard

# 완성도 칭호 임계 (docs/15 §3.4). 능력치 보상 없음(EP1).
MILESTONES: tuple[int, ...] = (5, 10, 15)
TOTAL_CARDS: int = 15


def auto_unlocked_ids(cards: Sequence[CodexCard]) -> set[str]:
    """``unlock.type == 'auto'`` 카드 id 집합 (게임 시작 시 기본 해금)."""
    return {c.id for c in cards if c.unlock.type == "auto"}


def cards_unlocked_by_clear(
    cards: Sequence[CodexCard],
    stage_number: int,
    stars: int,
) -> set[str]:
    """스테이지 클리어(별 수 포함) 시 새로 해금되는 카드 id 집합.

    Args:
        cards: 전체 코덱스 카드.
        stage_number: 클리어한 스테이지 번호(1~5).
        stars: 획득 별 수(0~3). ``stage_three_stars`` 는 stars>=3 일 때만.

    Returns:
        해당 클리어로 조건을 만족하는 카드 id 집합. ``true_ending`` 은 본 함수가
        다루지 않는다(별도 ``cards_unlocked_by_true_ending``).
    """
    out: set[str] = set()
    for c in cards:
        u = c.unlock
        if u.type == "stage_clear" and u.stage == stage_number:
            out.add(c.id)
        elif u.type == "stage_three_stars" and u.stage == stage_number and stars >= 3:
            out.add(c.id)
    return out


def cards_unlocked_by_true_ending(cards: Sequence[CodexCard]) -> set[str]:
    """진엔딩(5스테이지 전부 별3개) 도달 시 해금되는 카드 id 집합."""
    return {c.id for c in cards if c.unlock.type == "true_ending"}


@dataclass(frozen=True)
class CodexProgress:
    """획득 카드 집합 기준 완성도 스냅샷."""

    unlocked: int
    total: int
    fact: int
    legend: int
    fiction: int

    @property
    def is_complete(self) -> bool:
        return self.total > 0 and self.unlocked >= self.total

    def milestone_reached(self) -> int | None:
        """현재 획득 수가 정확히 도달한 최고 칭호 임계(없으면 None).

        5/10/15 중 ``unlocked`` 이상을 만족하는 최대 임계를 돌려준다.
        """
        reached = [m for m in MILESTONES if self.unlocked >= m]
        return max(reached) if reached else None


def compute_progress(cards: Sequence[CodexCard], unlocked_ids: Iterable[str]) -> CodexProgress:
    """획득 카드 집합으로 완성도/라벨 분포 계산.

    라벨 분포는 **획득한 카드만** 집계한다. ``fact_adapted`` 는 (사실) 배지를
    공유하므로 fact 로 합산한다(R5).
    """
    ids = set(unlocked_ids)
    by_id = {c.id: c for c in cards}
    fact = legend = fiction = 0
    for cid in ids:
        c = by_id.get(cid)
        if c is None:
            continue
        if c.label in ("fact", "fact_adapted"):
            fact += 1
        elif c.label == "legend":
            legend += 1
        elif c.label == "fiction":
            fiction += 1
    return CodexProgress(
        unlocked=len([cid for cid in ids if cid in by_id]),
        total=len(cards),
        fact=fact,
        legend=legend,
        fiction=fiction,
    )


# ---------------------------------------------------------------------------
# 세이브 슬롯 연동 (DECISION-EDU-004 오프라인 영속)
# ---------------------------------------------------------------------------
_SAVE_KEY: str = "codex_unlocked"


def load_unlocked_ids(slot) -> set[str]:  # type: ignore[no-untyped-def]
    """SaveSlot.extra 에서 획득 카드 id 집합 로드. 없으면 빈 집합(graceful)."""
    raw = getattr(slot, "extra", {}) or {}
    stored = raw.get(_SAVE_KEY)
    if isinstance(stored, list):
        return {str(x) for x in stored}
    return set()


def store_unlocked_ids(slot, unlocked_ids: Iterable[str]) -> None:  # type: ignore[no-untyped-def]
    """SaveSlot.extra 에 획득 카드 id 집합 기록(정렬 list 직렬화)."""
    if not hasattr(slot, "extra") or slot.extra is None:
        slot.extra = {}
    slot.extra[_SAVE_KEY] = sorted(set(unlocked_ids))
