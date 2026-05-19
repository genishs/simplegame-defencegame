"""저장 슬롯 (Phase 4, Issue #26).

DESIGN:
- 단일 사용자 저장 슬롯을 JSON 파일로 영속한다 (DECISION-DL-P4-001).
- 위치: ``~/.ansiseong/save_slot.json`` (환경변수 ``ANSISEONG_HOME`` 으로
  override 가능 — 주로 테스트/포터블 실행 용도).
- 본 라운드(Issue #26 튜토리얼)에서 필요한 최소 필드만 정의:
    * ``tutorial_dismissed`` — "다시 보지 않기" 토글 상태.
    * ``tutorial_completed`` — 튜토리얼 완주 여부.
- 후속 라운드에서 진행도/스테이지 진행률 등의 필드가 합류할 수 있도록
  ``data: dict[str, Any]`` 구조를 보존한다 (스키마 마이그레이션 친화적).

DECISION:
- tkinter 의존 0 — 도메인 가드(Phase 3.1) 준수.
- 외부 패키지 0 (stdlib json/pathlib/os 만).
- I/O 실패 시 silent fallback: 읽기 실패 → 빈 dict, 쓰기 실패 → log warning + 무시.
  (튜토리얼 진입 자체가 막히면 안 됨 — DOR)
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from src.core.logger import get_logger

_LOG = get_logger(__name__)


# ---------------------------------------------------------------------------
# 경로 헬퍼
# ---------------------------------------------------------------------------


def get_save_dir() -> Path:
    """저장 슬롯 디렉터리. 환경변수 ``ANSISEONG_HOME`` override 우선."""
    override = os.environ.get("ANSISEONG_HOME")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".ansiseong"


def get_save_path() -> Path:
    """저장 슬롯 JSON 파일 절대 경로."""
    return get_save_dir() / "save_slot.json"


# ---------------------------------------------------------------------------
# 데이터 모델
# ---------------------------------------------------------------------------


@dataclass
class SaveSlot:
    """단일 사용자 저장 슬롯.

    Attributes:
        tutorial_dismissed: ``True`` 이면 자동 진입을 영구 차단 (메뉴 진입은 가능).
        tutorial_completed: ``True`` 이면 단계 8까지 완주 1회 이상.
        extra: 후속 라운드 확장용 자유 필드 (스키마 마이그레이션 친화).
    """

    tutorial_dismissed: bool = False
    tutorial_completed: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # 직렬화
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # extra 는 평면 머지 (read 시 알 수 없는 키 보존)
        extra = d.pop("extra", {})
        d.update(extra)
        return d

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> SaveSlot:
        known = {"tutorial_dismissed", "tutorial_completed"}
        extra = {k: v for k, v in raw.items() if k not in known}
        return cls(
            tutorial_dismissed=bool(raw.get("tutorial_dismissed", False)),
            tutorial_completed=bool(raw.get("tutorial_completed", False)),
            extra=extra,
        )

    # ------------------------------------------------------------------
    # 의미 헬퍼
    # ------------------------------------------------------------------

    def is_empty(self) -> bool:
        """저장 슬롯이 비어 있는가 — 자동 진입 분기 (§1.1).

        ``tutorial_dismissed`` 또는 ``tutorial_completed`` 중 하나라도 True 이거나
        extra 에 데이터가 있으면 "비어 있지 않음" 으로 간주.
        """
        if self.tutorial_dismissed or self.tutorial_completed:
            return False
        return not self.extra

    def should_auto_enter_tutorial(self) -> bool:
        """튜토리얼 자동 진입 조건 (DECISION-PL-P4-002).

        - 저장 슬롯이 비어 있고
        - ``tutorial_dismissed`` 가 아니라면 → 자동 진입.
        """
        return self.is_empty() and not self.tutorial_dismissed


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def load_save_slot(path: Path | None = None) -> SaveSlot:
    """저장 슬롯 JSON 을 로드. 파일이 없거나 깨졌으면 빈 슬롯 반환."""
    p = path or get_save_path()
    try:
        if not p.exists():
            return SaveSlot()
        raw = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            _LOG.warning("save_slot: malformed root (not dict) — using empty")
            return SaveSlot()
        return SaveSlot.from_dict(raw)
    except (OSError, json.JSONDecodeError) as exc:
        _LOG.warning("save_slot: load failed (%s) — using empty", exc)
        return SaveSlot()


def save_save_slot(slot: SaveSlot, path: Path | None = None) -> bool:
    """저장 슬롯을 JSON 파일로 기록. 실패 시 False (예외는 swallow)."""
    p = path or get_save_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(slot.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except OSError as exc:
        _LOG.warning("save_slot: save failed (%s)", exc)
        return False


def mark_tutorial_dismissed(value: bool = True, path: Path | None = None) -> SaveSlot:
    """편의 함수 — tutorial_dismissed 토글 후 즉시 저장."""
    slot = load_save_slot(path)
    slot.tutorial_dismissed = value
    save_save_slot(slot, path)
    return slot


def mark_tutorial_completed(value: bool = True, path: Path | None = None) -> SaveSlot:
    """편의 함수 — tutorial_completed 토글 후 즉시 저장."""
    slot = load_save_slot(path)
    slot.tutorial_completed = value
    save_save_slot(slot, path)
    return slot
