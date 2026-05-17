"""이미지 로딩/캐시 (Pillow + PhotoImage).

DESIGN: ``PhotoImage``는 GC되면 빈 이미지가 되므로 모듈 캐시가 강한 참조
유지. 같은 이미지의 다른 사이즈는 ``name@WxH`` 키로 분리 캐시.
EXPECTED: lead 골격 / team-member-2가 사운드 추가(OPEN-1 결정 후).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.core.logger import get_logger
from src.core.settings import ASSETS_ROOT

if TYPE_CHECKING:
    from pathlib import Path


_log = get_logger(__name__)


class AssetManager:
    """이미지 로딩 + 강한 참조 캐시.

    이미지 파일이 없으면 경고 후 None을 반환. 골격 단계에서는 대부분의
    리소스가 아직 없으므로 ``has_image()``로 가드한다.
    """

    def __init__(self, images_dir: Path | None = None) -> None:
        self._dir = images_dir or (ASSETS_ROOT / "images")
        self._photo_cache: dict[str, Any] = {}
        self._raw_cache: dict[str, Any] = {}

    # ------------------------------------------------------------------
    def has_image(self, name: str) -> bool:
        return (self._dir / f"{name}.png").exists()

    def image(self, name: str, size: tuple[int, int] | None = None) -> Any | None:
        """``name``.png 로드 (옵션 리사이즈). 없으면 None."""
        key = f"{name}@{size[0]}x{size[1]}" if size else name
        if key in self._photo_cache:
            return self._photo_cache[key]
        path = self._dir / f"{name}.png"
        if not path.exists():
            _log.debug("asset missing: %s", path)
            return None
        try:
            from PIL import Image, ImageTk
        except ImportError:  # pragma: no cover - Pillow는 requirements에 명시
            _log.warning("Pillow not installed; cannot load %s", path)
            return None

        raw = self._raw_cache.get(name)
        if raw is None:
            raw = Image.open(path).convert("RGBA")
            self._raw_cache[name] = raw
        img = raw.resize(size, Image.LANCZOS) if size else raw
        photo = ImageTk.PhotoImage(img)
        self._photo_cache[key] = photo  # 강한 참조 = 누수 방지
        return photo

    def evict(self, prefix: str = "") -> int:
        """캐시에서 prefix로 시작하는 키를 제거. 반환: 제거된 개수."""
        keys = [k for k in self._photo_cache if k.startswith(prefix)]
        for k in keys:
            del self._photo_cache[k]
        return len(keys)
