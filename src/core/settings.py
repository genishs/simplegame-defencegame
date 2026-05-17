"""게임 전역 상수 / 사용자 설정 보관.

DESIGN: 변경 빈도가 낮은 상수는 모듈 레벨로, 런타임 사용자 설정은
``Settings`` dataclass 인스턴스(추후 JSON 영속화)로 분리한다.
EXPECTED: lead가 골격 작성 / 팀원이 새 상수를 추가하는 정도로 충분.
"""

from __future__ import annotations

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
#           PyInstaller --onefile은 ``sys._MEIPASS`` 처리를 별도 paths.py가
#           수행할 예정(현재 골격에서는 개발 모드 기준).
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
SRC_ROOT: Path = PROJECT_ROOT / "src"
DATA_ROOT: Path = SRC_ROOT / "data"
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
