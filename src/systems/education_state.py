"""교육 통합 세션 상태 (최초 노출 플래그) — tkinter 비의존.

DESIGN (docs/15 §3.1·§4, docs/16 Wave1 1-3·1-4, 리스크 R-5):
- H2 적 첫 등장 배너, H6 라벨 첫 노출 토스트의 "최초 1회" 판정을 담는다.
- "최초 노출됨" 플래그는 **도메인 세션 상태**(본 모듈, tk-free)에 두어
  렌더링(ui/scenes)이 이를 구독·표시만 하도록 분리한다(R-5: tk-free 가드).
- 본 모듈은 순수 파이썬(집합 보관 + 멱등 마킹). 외부 의존 0.

용어:
- 라벨 키는 코덱스 enum 표기를 따른다: ``fact``/``fact_adapted``/``legend``/``fiction``.
  토스트 대상은 [전승](legend)/[픽션](fiction) 둘 뿐(docs/15 §4.1 R3). 나머지는
  토스트 없음(배지만).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# 라벨 첫 노출 토스트 대상 (docs/15 §4.1 R3). fact/fact_adapted 는 토스트 없음.
TOAST_LABELS: frozenset[str] = frozenset({"legend", "fiction"})


@dataclass
class EducationSessionState:
    """교육 후크의 세션 단위 최초 노출 추적.

    한 게임 세션(앱 실행) 동안 유지. 저장 슬롯과는 독립(매 세션 1회 재노출 허용)
    — H2/H6 모두 "게임 내 최초"가 세션 기준이며 능력치/진행도와 무관(EP1).

    Attributes:
        seen_enemy_types: H2 배너를 이미 띄운 적 타입 id 집합.
        seen_labels: H6 토스트를 이미 띄운 라벨 키 집합.
    """

    seen_enemy_types: set[str] = field(default_factory=set)
    seen_labels: set[str] = field(default_factory=set)

    # ------------------------------------------------------------------
    # H2 — 적 첫 등장
    # ------------------------------------------------------------------
    def should_show_enemy_banner(self, enemy_type: str) -> bool:
        """해당 적 타입의 배너를 지금 띄워야 하는가(아직 안 띄웠으면 True)."""
        return bool(enemy_type) and enemy_type not in self.seen_enemy_types

    def mark_enemy_seen(self, enemy_type: str) -> bool:
        """적 타입을 노출됨으로 마킹. 이번 호출이 최초였으면 True 반환(멱등).

        최초 노출일 때만 True 를 돌려주므로, 호출자는 반환값으로 배너 1회 표시를
        결정할 수 있다(2회째부터는 False).
        """
        if not enemy_type or enemy_type in self.seen_enemy_types:
            return False
        self.seen_enemy_types.add(enemy_type)
        return True

    # ------------------------------------------------------------------
    # H6 — 라벨 첫 노출
    # ------------------------------------------------------------------
    def should_show_label_toast(self, label: str) -> bool:
        """해당 라벨의 첫 노출 토스트를 지금 띄워야 하는가.

        토스트 대상([전승]/[픽션])이면서 아직 안 띄운 경우에만 True.
        """
        return label in TOAST_LABELS and label not in self.seen_labels

    def mark_label_seen(self, label: str) -> bool:
        """라벨을 노출됨으로 마킹. 이번 호출이 최초 토스트였으면 True(멱등).

        토스트 비대상 라벨(fact/fact_adapted)은 항상 False(토스트 없음).
        """
        if label not in TOAST_LABELS or label in self.seen_labels:
            return False
        self.seen_labels.add(label)
        return True

    def reset(self) -> None:
        """세션 상태 초기화(테스트/새 게임 시작 시)."""
        self.seen_enemy_types.clear()
        self.seen_labels.clear()
