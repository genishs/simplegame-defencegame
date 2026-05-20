"""게임 전역 상수 / 사용자 설정 보관.

DESIGN: 변경 빈도가 낮은 상수는 모듈 레벨로, 런타임 사용자 설정은
``Settings`` dataclass 인스턴스(추후 JSON 영속화)로 분리한다.
EXPECTED: lead가 골격 작성 / 팀원이 새 상수를 추가하는 정도로 충분.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# 디자인 베이스 해상도 (Scaler와 짝).
# ---------------------------------------------------------------------------
BASE_WIDTH: int = 1920
BASE_HEIGHT: int = 1080

# 게임 루프 타이밍.
TARGET_DT_MS: int = 16
MAX_DT_S: float = 0.05  # 50ms 이상은 클램프(스파이크 방지)

# 게임 타이틀.
APP_TITLE: str = "안시성 디펜스 (Ansiseong Defense)"

# ---------------------------------------------------------------------------
# 경로.
# DECISION: 코드 위치 기준 2단계 상위를 프로젝트 루트로 본다.
# DECISION-DL-P4D-003 (Issue #51, 2026-05-20):
#   PyInstaller --onefile 환경에서는 ``sys._MEIPASS`` 가 자원 추출 디렉토리를
#   가리킨다. ``src/data/`` 의 JSON 자원 (stages/enemies/units) 은 spec 파일의
#   ``datas`` 로 번들되며, 런타임에는 ``sys._MEIPASS / src / data`` 또는
#   ``sys._MEIPASS / data`` 로 추출된다. 개발 모드(`python src/main.py`)
#   에서는 기존처럼 프로젝트 루트의 ``src/data/`` 를 가리킨다.
#
#   사용자 결함 보고(Issue #51): .exe 빌드에서 튜토리얼 후 stage_01 진입 시
#   stage JSON 미발견 → ``BattleScene.stage = None`` → ``update()`` early
#   return → frozen 으로 보이는 현상. 본 수정으로 _MEIPASS 우선 해석한다.
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
SRC_ROOT: Path = PROJECT_ROOT / "src"


def resolve_data_root() -> Path:
    """``src/data`` 디렉터리의 런타임 절대 경로를 반환.

    우선순위:
      1. PyInstaller 번들(``sys._MEIPASS``): ``_MEIPASS/src/data`` 가 존재하면
         그 경로를. 그렇지 않으면 ``_MEIPASS/data`` 도 시도(향후 layout 변경 대비).
      2. 개발 모드: ``PROJECT_ROOT/src/data``.

    실제 디렉토리 존재 여부는 보장하지 않는다(호출자가 가드).
    """
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        cand_a = Path(meipass) / "src" / "data"
        if cand_a.is_dir():
            return cand_a
        cand_b = Path(meipass) / "data"
        if cand_b.is_dir():
            return cand_b
        # 둘 다 없으면 _MEIPASS/src/data 로 폴백(후속 진단 메시지가 명확하도록).
        return cand_a
    return SRC_ROOT / "data"


DATA_ROOT: Path = resolve_data_root()
ASSETS_ROOT: Path = PROJECT_ROOT / "assets"


@dataclass
class Settings:
    """런타임 사용자 설정. 추후 JSON 영속화 대상.

    EXPECTED: team-member-2가 ``save()``/``load()``를 추가.
    """

    window_width: int = 1280
    window_height: int = 720
    fullscreen: bool = False
    master_volume: float = 0.7
    show_debug_overlay: bool = False
    # 키바인딩(베이스). 키 이름은 tk 스타일("<Escape>", "<Key-F3>").
    keymap: dict[str, str] = field(
        default_factory=lambda: {
            "pause": "<Escape>",
            "debug_overlay": "<F3>",
            "next_wave": "<space>",
        }
    )


# 모듈 레벨 싱글톤. App 부트 시 교체 가능.
SETTINGS: Settings = Settings()
