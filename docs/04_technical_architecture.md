# 04. Technical Architecture — 안시성 디펜스 (Ansiseong Defense)

> 문서 버전: v0.1 (Draft)
> 작성자: 게임 개발 파트 Tech Lead
> 검토자: 클라이언트 엔지니어 A, 게임플레이 엔지니어 B
> 대상: 안시성 전투 모티브 2D 타워디펜스 (Python 3.11 + tkinter, Windows 단일 .exe)
> 최종 수정일: 2026-05-17

---

## 0. 토의 결과 요약 (Discussion Digest)

본 문서는 Tech Lead 단독 작성이 아니라, 팀원 2명과의 라운드 토론을 거쳐 합의된 결정을 정리한 것이다.

| 참여자 | 역할 | 주요 입장 |
|--------|------|-----------|
| Lead (필자) | Tech Lead | 외부 의존성 최소화, tkinter 한계 내에서 60fps 시뮬레이션 + 30fps 렌더링 타협 가능 |
| Engineer A | 클라이언트/렌더링 | Canvas 객체 재생성 절대 금지, 오브젝트 풀 + `coords()` 이동 강제, DPI 인식 필수 |
| Engineer B | 게임플레이/시스템 | 데이터 주도(JSON) 강력 지지, 시스템 로직은 tk 비의존으로 단위 테스트 가능해야 함 |

**합의된 핵심 결정 3가지 (DECISION)**

1. **렌더 모델**: 단일 `Canvas` + 오브젝트 풀 + `coords()` 기반 이동. 16ms `after()` 게임 루프, 시뮬레이션 dt는 가변, 렌더는 매 틱 실행하되 객체 수 상한(엔티티 ≤ 210)으로 보호.
2. **좌표계**: 디자인 베이스 1920×1080 float 좌표. 윈도우 `<Configure>` 시 단일 scale 계산 → `canvas.scale("all",0,0,s,s)` + 폰트 비례. DPI는 `SetProcessDpiAwarenessContext(-4)`로 Per-Monitor V2.
3. **데이터 주도**: 스테이지/유닛/적은 모두 JSON으로 외부화. 시스템 모듈(combat, economy, wave)은 tk 비의존 → pytest로 단위 테스트.

**남은 OPEN 이슈 (가장 큰 우려)**

- **사운드 백엔드 미확정**: `winsound`는 wav 단일 채널만 가능. BGM+다중 효과음 동시 재생을 위해 외부 lib(`playsound`, `pygame.mixer`만 부분 사용 등)를 도입할지, 무사운드로 갈지 결정 보류. → 본 문서 §10 OPEN-1 참고.

---

## 1. 기술 스택 결정 (Tech Stack Decisions)

### 1.1 런타임 / 라이브러리

| 항목 | 선정 | 버전/비고 | 근거 |
|------|------|-----------|------|
| 언어 | Python | **3.11.x** | 안정성, `tomllib` 포함, `match` 가독성, 3.12는 PyInstaller 호환성 검증 부족 |
| UI/렌더 | tkinter (stdlib) | Tk 8.6 | **사용자 요구사항**: pygame 금지. tkinter만 사용 |
| 이미지 | Pillow | 10.x | PNG 알파 채널, 리사이즈, GIF 시퀀스. PhotoImage만으로는 알파 처리 부실 |
| 빌드 | PyInstaller | 6.x | `--onefile --windowed`로 단일 .exe, Win10/11 검증된 표준 |
| 테스트 | pytest | 8.x | 시스템 로직(tk 비의존) 단위 테스트 |
| 정적 검사 | ruff + black + mypy | 최신 | ruff(lint+isort), black(format), mypy(type) |
| 데이터 | 표준 `json` | stdlib | 외부 데이터 외부화. YAML 채택은 의존성 증가로 거절 |
| 사운드 (OPEN) | `winsound` 또는 미정 | stdlib | §10 OPEN-1 |

**원칙**: 외부 의존성은 Pillow와 PyInstaller(빌드 전용)만으로 제한. 그 외는 stdlib에서 해결한다. 신규 의존성 추가는 PR 리뷰에서 명시적 승인 필요.

### 1.2 requirements.txt (런타임 의존성)

```text
# requirements.txt — 런타임 의존성 (최소화 원칙)
# Python 3.11.x 가정. tkinter는 표준 라이브러리이므로 포함하지 않음.

Pillow==10.4.0
# 사운드 백엔드 결정 시 추가 (OPEN-1):
# playsound==1.3.0    # 대안 A: 가볍지만 동시 재생 불안정
```

### 1.3 requirements-dev.txt (개발 의존성)

```text
# requirements-dev.txt — 개발/빌드/테스트 전용
-r requirements.txt

pyinstaller==6.10.0
pytest==8.3.2
pytest-cov==5.0.0
ruff==0.6.4
black==24.8.0
mypy==1.11.2
types-Pillow==10.2.0.20240822
```

### 1.4 Python 3.11 선정에 대한 토론

> **Engineer A**: 3.12로 가면 `typing` 개선이 있는데 굳이 3.11? > **Lead**: PyInstaller가 3.12에서 Pillow와 함께 `--onefile`로 빌드할 때 안티바이러스 false-positive 빈도가 더 높다는 보고가 있음. 3.11 LTS급 안정성 우선. > **Engineer B**: 3.11이면 `tomllib` 쓸 수 있어서 설정파일에 좋다. 동의.

**DECISION-1.1**: Python 3.11.x 고정 (`>=3.11,<3.12`).

---

## 2. tkinter 게임 구현 핵심 이슈와 대응 (Tkinter Game Engineering)

tkinter는 게임용으로 설계되지 않았다. 다음 8가지 이슈를 사전에 합의했다.

### 2.1 Canvas 객체 다수 시 성능

| 이슈 | 대응 |
|------|------|
| `create_*` / `delete` 반복 호출 시 GC 비용 큼 | **오브젝트 풀** 패턴. 사망한 엔티티의 Canvas item id 재사용 |
| 위치 갱신을 `delete → create`로 하면 비용 폭발 | `Canvas.coords(item_id, x, y)` 사용. 절대 재생성 금지 |
| 더티 렉트 같은 부분 재그리기는 tk에 존재하지 않음 | 회피 불가. 대신 객체 수 상한 + 화면 밖 객체 `itemconfigure(state="hidden")` |
| 같은 종류 다수 처리 시 루프 비용 | `tag` 활용. `canvas.find_withtag("enemy")` 한 번에 조회 |
| 좌표 변환 + tag 검색 비용 | 엔티티 객체가 item_id를 직접 보관 (find 검색 회피) |

**규칙 (Engineer A 강력 주장)**:
1. 매 프레임 `delete`/`create`는 금지. 풀에서 가져와 `coords` + `itemconfigure(state="normal")`로 활성화.
2. 객체 사망은 `state="hidden"`으로 풀에 반환.
3. 모든 엔티티는 자신의 `canvas_id`를 보유. tag 검색은 디버그/배치 작업에만.

**오브젝트 풀 스케치**:

```python
# src/core/object_pool.py
class CanvasPool:
    """Canvas item id를 재사용하기 위한 풀.

    엔티티 종류별로 분리된 풀을 유지한다.
    """
    def __init__(self, canvas, factory, capacity: int):
        self._canvas = canvas
        self._factory = factory          # () -> int  (create_image 등 반환)
        self._free: list[int] = []
        self._capacity = capacity

    def acquire(self) -> int:
        if self._free:
            iid = self._free.pop()
            self._canvas.itemconfigure(iid, state="normal")
            return iid
        if self._canvas_count() >= self._capacity:
            raise PoolExhausted("capacity reached")
        return self._factory()

    def release(self, iid: int) -> None:
        self._canvas.itemconfigure(iid, state="hidden")
        self._free.append(iid)
```

### 2.2 게임 루프 (Game Loop)

tkinter는 자체 이벤트 루프를 돌리므로 별도 스레드 대신 `root.after()`를 사용한다.

```python
# src/core/game_loop.py
import time

TARGET_DT_MS = 16              # 약 62.5fps 타깃
MAX_DT_S    = 0.05             # 50ms 이상은 클램프(스파이크 방지)

class GameLoop:
    def __init__(self, root, on_tick):
        self.root      = root
        self.on_tick   = on_tick     # callable(dt_seconds)
        self._prev     = time.perf_counter()
        self._running  = False
        self._fps_acc  = 0.0
        self._fps_cnt  = 0
        self.fps       = 0.0

    def start(self) -> None:
        self._running = True
        self._prev = time.perf_counter()
        self._schedule()

    def stop(self) -> None:
        self._running = False

    def _schedule(self) -> None:
        if not self._running:
            return
        self.root.after(TARGET_DT_MS, self._tick)

    def _tick(self) -> None:
        now = time.perf_counter()
        dt  = min(now - self._prev, MAX_DT_S)
        self._prev = now
        self.on_tick(dt)
        # FPS 측정
        self._fps_acc += dt
        self._fps_cnt += 1
        if self._fps_acc >= 0.5:
            self.fps = self._fps_cnt / self._fps_acc
            self._fps_acc = 0.0
            self._fps_cnt = 0
        self._schedule()
```

**왜 `after(16)`인가?**
- `after(0)`은 폭주 가능성. `after(16)`은 OS 타이머 해상도 한계로 실제 ~15-17ms.
- 더 부드러운 60fps가 필요하면 `after_idle` 대안이 있지만 입력 처리 지연 가능 → 채택 안함.

**DECISION-2.1**: 시뮬레이션·렌더 통합 단일 루프, `after(16)` 기반, 가변 dt(클램프 50ms).

### 2.3 입력 처리

```python
# src/systems/input.py 발췌
class InputRouter:
    def __init__(self, root, canvas):
        root.bind("<Key>",       self._on_key)
        canvas.bind("<Button-1>", self._on_click)
        canvas.bind("<Motion>",   self._on_motion)
        canvas.bind("<Button-3>", self._on_rclick)   # 컨텍스트
        self._handlers: dict[str, list] = {}

    def on(self, event_name: str, fn):
        self._handlers.setdefault(event_name, []).append(fn)
```

- 마우스 좌표는 항상 **스크린 좌표 → 베이스 좌표** 변환 후 게임 로직에 전달 (§3 참고).
- 키 바인딩: `F3` 디버그 오버레이, `Esc` 일시정지, `Space` 다음 웨이브.

### 2.4 이미지 (PhotoImage / Pillow)

| 이슈 | 대응 |
|------|------|
| `PhotoImage`는 GC되면 즉시 빈 이미지 표시 | **AssetManager가 강한 참조 유지**. 모듈 레벨 dict |
| 기본 PhotoImage는 PNG 알파 채널 처리 부실 | `PIL.ImageTk.PhotoImage(Image.open(...).convert("RGBA"))` |
| 동일 이미지 다중 사이즈 필요 | 사이즈별로 캐시 키 분리 (`name@WxH`) |
| 리사이즈 비용 | 스테이지 진입 시 미리 베이스 사이즈로 생성 후 캐시 |

```python
# src/core/assets.py 발췌
from PIL import Image, ImageTk

class AssetManager:
    def __init__(self):
        self._cache: dict[str, ImageTk.PhotoImage] = {}
        self._raw: dict[str, Image.Image] = {}

    def image(self, name: str, size: tuple[int, int] | None = None) -> ImageTk.PhotoImage:
        key = f"{name}@{size[0]}x{size[1]}" if size else name
        if key in self._cache:
            return self._cache[key]
        raw = self._raw.get(name) or Image.open(f"assets/images/{name}.png").convert("RGBA")
        self._raw[name] = raw
        img = raw.resize(size, Image.LANCZOS) if size else raw
        photo = ImageTk.PhotoImage(img)
        self._cache[key] = photo        # 강한 참조 유지 = 누수 회피
        return photo
```

### 2.5 사운드 (OPEN)

| 옵션 | 장점 | 단점 |
|------|------|------|
| `winsound` (stdlib) | 의존성 0, Win 기본 지원 | wav만, 동시 1채널, BGM+SFX 동시 불가 |
| `playsound` | 단순 API | 동시 재생 불안정, 정지 어려움 |
| `pygame.mixer`만 발췌 | 안정적 다채널 | 사용자 요구사항 "pygame 금지" 위반 가능 |
| 무사운드 | 단순함 | 게임성 손실 |

→ **OPEN-1**: 사용자 확정 필요. 임시는 `winsound` 단일 BGM + 효과음 OFF.

### 2.6 한글 폰트

- Windows 기본 한글 폰트 **`Malgun Gothic`** 사용 (라이선스 무료, Win10+ 기본 탑재).
- 폴백: `("Malgun Gothic", "맑은 고딕", "Segoe UI")` 순.
- 폰트 크기는 §3의 스케일러로 계산된 정수 px 사용.

```python
def font_for(base_pt: int, scale: float) -> tuple[str, int]:
    return ("Malgun Gothic", max(8, int(base_pt * scale)))
```

### 2.7 렌더링 성능 측정

매 틱 `on_tick`의 시작/끝을 `time.perf_counter()`로 측정 → 평균/최대를 디버그 오버레이(§8.1)에 노출.

### 2.8 멀티스레딩

**금지**. tk 위젯은 메인 스레드에서만 접근 가능. I/O가 필요하면 `queue.Queue` + `after`로 폴링.

---

## 3. 해상도 스케일링 전략 (Resolution & DPI Scaling)

### 3.1 좌표계 정의

- **베이스 해상도**: 1920×1080 (FHD)
- **베이스 좌표**: 모든 게임 로직(엔티티 위치, 경로, 콜리전 반경)은 베이스 좌표 float로 저장.
- **스크린 좌표**: 화면에 그릴 때만 `to_screen(x, y)`로 변환.

### 3.2 스케일러

```python
# src/core/scaler.py
class Scaler:
    BASE_W = 1920
    BASE_H = 1080

    def __init__(self):
        self.scale = 1.0
        self.off_x = 0
        self.off_y = 0
        self.canvas_w = self.BASE_W
        self.canvas_h = self.BASE_H

    def update(self, canvas_w: int, canvas_h: int) -> tuple[float, float]:
        """윈도우 리사이즈 시 호출. letterbox 방식."""
        prev = self.scale
        self.canvas_w, self.canvas_h = canvas_w, canvas_h
        self.scale = min(canvas_w / self.BASE_W, canvas_h / self.BASE_H)
        # 중앙 정렬 letterbox 오프셋
        self.off_x = (canvas_w - self.BASE_W * self.scale) / 2
        self.off_y = (canvas_h - self.BASE_H * self.scale) / 2
        # tkinter는 누적 scale에 곱해야 하므로 비율 반환
        ratio = self.scale / prev if prev else 1.0
        return ratio, ratio

    def to_screen(self, x: float, y: float) -> tuple[float, float]:
        return self.off_x + x * self.scale, self.off_y + y * self.scale

    def to_base(self, sx: float, sy: float) -> tuple[float, float]:
        if self.scale == 0:
            return 0.0, 0.0
        return (sx - self.off_x) / self.scale, (sy - self.off_y) / self.scale

    def font_pt(self, base_pt: int) -> int:
        return max(8, int(base_pt * self.scale))
```

### 3.3 `<Configure>` 핸들링

```python
# src/scenes/battle_scene.py 발췌
def _on_configure(self, event):
    if event.widget is not self.canvas:
        return
    sx, sy = self.scaler.update(event.width, event.height)
    if abs(sx - 1.0) > 1e-6:
        # 모든 Canvas item에 일괄 스케일 적용
        self.canvas.scale("all", 0, 0, sx, sy)
        # 폰트는 별도 재설정
        self._restyle_fonts()
        # letterbox 배경(검은 띠) 재배치
        self._redraw_letterbox()
```

**주의**: `canvas.scale("all", 0, 0, sx, sy)`는 좌표만 곱한다. 이미지의 픽셀 사이즈는 변하지 않는다 → 이미지 자체도 `assets.image(name, size)`로 새 사이즈를 요청해 `itemconfigure(image=...)`로 교체해야 한다.

**DECISION-3.1**: 좌표는 `canvas.scale`, 이미지는 사이즈별 재캐시 후 교체, 폰트는 별도 재설정. 3축을 독립적으로 관리.

### 3.4 DPI 인식 (Windows)

Windows 고DPI 디스플레이에서 tkinter는 기본적으로 흐릿하게 출력된다. 진입점에서 DPI awareness를 명시한다.

```python
# src/main.py 진입 직후
import sys, ctypes
if sys.platform == "win32":
    try:
        # Per-Monitor V2 (-4). Win10 1703+
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except (AttributeError, OSError):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)   # 폴백 V1
        except (AttributeError, OSError):
            ctypes.windll.user32.SetProcessDPIAware()        # 마지막 폴백
```

**DECISION-3.2**: Per-Monitor V2 (-4) 우선 시도, 단계적 폴백. 멀티모니터 이동 시 `WM_DPICHANGED`는 tkinter가 자체 처리.

### 3.5 좌표/스케일 다이어그램

```
[베이스 좌표 (0,0)~(1920,1080)]   ← 게임 로직, JSON 데이터
            │ scaler.to_screen(x,y)
            ▼
[스크린 좌표 (offx,offy)~(...)]   ← Canvas 그리기
            │ (윈도우가 16:9가 아닐 때)
            ▼
[letterbox 검은 띠 좌우 또는 상하]
```

---

## 4. 아키텍처 모듈 구조 (Module Architecture)

### 4.1 디렉토리 트리

```
defensegame/
├── src/
│   ├── main.py                # 진입점: DPI, root Tk 생성, App 부트
│   ├── core/
│   │   ├── __init__.py
│   │   ├── app.py             # App: 씬 라우터 + 상태머신
│   │   ├── game_loop.py       # after(16) 루프, dt 측정
│   │   ├── scaler.py          # 좌표/폰트 스케일링
│   │   ├── assets.py          # 이미지·사운드 로딩 캐시
│   │   ├── object_pool.py     # Canvas item id 풀
│   │   ├── events.py          # pub/sub (subscribe/publish)
│   │   ├── settings.py        # 사용자 설정 + 게임 상수
│   │   └── logger.py          # 표준 logging 래퍼
│   ├── scenes/
│   │   ├── __init__.py
│   │   ├── base_scene.py      # Scene 인터페이스
│   │   ├── menu_scene.py      # 타이틀
│   │   ├── stage_select_scene.py
│   │   ├── battle_scene.py    # 전투 메인
│   │   ├── result_scene.py    # 클리어/패배
│   │   └── ending_scene.py    # 최종 엔딩
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── entity.py          # 베이스 (canvas_id, pos, hp, update)
│   │   ├── hero.py            # 양만춘 (특수 스킬)
│   │   ├── ally.py            # 고구려 유닛 (궁수/방패/석포 등)
│   │   ├── enemy.py           # 당군 (보병/공성/장수)
│   │   ├── projectile.py      # 화살, 돌
│   │   └── effect.py          # 폭발/파티클 (수 제한)
│   ├── systems/
│   │   ├── __init__.py
│   │   ├── pathing.py         # 웨이포인트 추종
│   │   ├── wave.py            # 웨이브 스케줄러
│   │   ├── combat.py          # 데미지/타겟팅
│   │   ├── economy.py         # 자원/구매
│   │   ├── spawn.py           # 적·아군 소환
│   │   └── input.py           # 마우스/키 라우팅
│   ├── data/
│   │   ├── stages/
│   │   │   ├── stage_01.json … stage_05.json
│   │   ├── units.json
│   │   ├── enemies.json
│   │   └── balance.json       # 글로벌 상수 (난이도 곱 등)
│   └── ui/
│       ├── __init__.py
│       ├── hud.py             # 자원, 웨이브, 영웅 HP
│       ├── widgets.py         # 버튼, 진행바 (Canvas 기반)
│       ├── dialog.py          # 일시정지/설정 다이얼로그
│       └── overlay.py         # 디버그 오버레이 (F3)
├── assets/
│   ├── images/
│   ├── sounds/
│   └── fonts/                 # (선택) 별도 라이선스된 한글 폰트
├── tests/
│   ├── test_combat.py
│   ├── test_economy.py
│   ├── test_wave.py
│   ├── test_pathing.py
│   └── test_scaler.py
├── tools/
│   └── build.py               # PyInstaller 래퍼
├── docs/
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml             # ruff/black/mypy/pytest 설정
└── README.md
```

### 4.2 모듈 책임 (한 줄 요약)

| 모듈 | 책임 |
|------|------|
| `main.py` | DPI 설정, root Tk 생성, App 부트스트랩 |
| `core/app.py` | 씬 전환 상태머신, 글로벌 서비스(assets, scaler, events) 보유 |
| `core/game_loop.py` | `after(16)` 루프, dt 계산, FPS 측정 |
| `core/scaler.py` | 베이스↔스크린 좌표/폰트 변환 |
| `core/assets.py` | 이미지·사운드 로딩/캐시, 강한 참조 유지 |
| `core/object_pool.py` | Canvas item id 재사용 풀 |
| `core/events.py` | 도메인 이벤트 pub/sub (예: `enemy.killed`) |
| `core/settings.py` | 사용자 설정(JSON) 영속, 상수 노출 |
| `scenes/*` | 화면 단위. 진입/탈출/업데이트/그리기 |
| `entities/*` | 게임 객체. 상태 + `update(dt, world)` |
| `systems/*` | 횡단 로직(전투/경제/스폰). tk 비의존 (단위 테스트 가능) |
| `data/*` | 외부화된 밸런스/스테이지 데이터 |
| `ui/*` | HUD, 다이얼로그, 디버그 오버레이 |

### 4.3 의존 방향 (Dependency Direction)

```
                    ┌─────────┐
                    │  main   │
                    └────┬────┘
                         ▼
                    ┌─────────┐
                    │  core   │  ← 가장 안쪽. 외부 비의존.
                    └────┬────┘
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         ┌────────┐ ┌─────────┐ ┌───────────┐
         │ scenes │ │entities │ │  systems  │
         └────┬───┘ └────┬────┘ └─────┬─────┘
              │          │            │
              │          └──depends──►│
              └────────depends────────►
                         │
                         ▼
                     ┌──────┐
                     │  ui  │
                     └──────┘
```

**규칙**:
- `core`는 어디서나 import 가능. 다른 곳을 import하지 않는다.
- `entities`는 `core`만 import.
- `systems`는 `core`, `entities` import 가능. 단 `tkinter` import는 **금지**(단위 테스트 가능성 보존).
- `scenes`는 `core`, `entities`, `systems`, `ui` 모두 import 가능. tk 위젯 조립.
- `ui`는 `core`까지만 import. 비즈니스 로직 없음.

**Engineer B 코멘트**: "systems는 무조건 tk 비의존. 그래야 `pytest`로 `combat.calc_damage(...)` 같은 거 1ms에 1000번 돌릴 수 있다."

**DECISION-4.1**: 의존 방향은 위 다이어그램으로 고정. 위반 시 PR reject. `import-linter`로 CI 강제 검사(차후).

---

## 5. 데이터 주도 설계 (Data-Driven Design)

### 5.1 원칙

- 스테이지, 유닛, 적, 웨이브, 밸런스 상수는 모두 JSON에 외부화.
- 디자이너(또는 기획자)가 코드 변경 없이 `*.json`만 편집.
- 로더는 스키마 검증(파이썬 `dataclass` + 수동 검증) 후 비정상이면 즉시 실패(early fail).

### 5.2 스키마 예시

#### 5.2.1 `data/units.json`

```json
{
  "version": 1,
  "units": {
    "archer": {
      "name": "고구려 궁수",
      "cost": 50,
      "hp": 60,
      "atk": 12,
      "atk_speed": 1.2,
      "range": 320,
      "projectile": "arrow",
      "sprite": "ally_archer",
      "size": [48, 64]
    },
    "shield": {
      "name": "방패병",
      "cost": 70,
      "hp": 200,
      "atk": 6,
      "atk_speed": 0.9,
      "range": 40,
      "sprite": "ally_shield",
      "size": [56, 72]
    },
    "stone_thrower": {
      "name": "투석병",
      "cost": 120,
      "hp": 90,
      "atk": 35,
      "atk_speed": 0.4,
      "range": 480,
      "projectile": "stone",
      "splash_radius": 80,
      "sprite": "ally_stone",
      "size": [60, 72]
    }
  }
}
```

#### 5.2.2 `data/stages/stage_01.json`

```json
{
  "id": "stage_01",
  "title": "안시성 외곽",
  "background": "bg_outer_wall",
  "music": "bgm_battle_01",
  "starting_gold": 300,
  "lives": 20,
  "paths": [
    { "id": "p_main",
      "waypoints": [[0, 540], [600, 540], [600, 300], [1920, 300]] }
  ],
  "build_zones": [
    { "x": 700, "y": 600, "w": 80, "h": 80 },
    { "x": 820, "y": 600, "w": 80, "h": 80 }
  ],
  "waves": [
    { "delay_s": 3.0, "spawns": [
        { "type": "tang_soldier", "count": 10, "interval_s": 0.8, "path": "p_main" }
    ]},
    { "delay_s": 8.0, "spawns": [
        { "type": "tang_soldier", "count": 15, "interval_s": 0.6, "path": "p_main" },
        { "type": "tang_shield",  "count": 3,  "interval_s": 2.0, "path": "p_main" }
    ]},
    { "delay_s": 12.0, "boss": "tang_captain", "spawns": [
        { "type": "tang_soldier", "count": 20, "interval_s": 0.5, "path": "p_main" }
    ]}
  ],
  "reward": { "gold": 200, "unlock": "stage_02" }
}
```

#### 5.2.3 `data/enemies.json` (발췌)

```json
{
  "version": 1,
  "enemies": {
    "tang_soldier": {
      "name": "당군 보병",
      "hp": 80, "speed": 60, "damage_to_castle": 1,
      "gold_drop": 8, "sprite": "enemy_soldier"
    },
    "tang_shield": {
      "name": "당군 방패병",
      "hp": 220, "speed": 45, "damage_to_castle": 2,
      "armor": 5, "gold_drop": 18, "sprite": "enemy_shield"
    },
    "tang_captain": {
      "name": "당군 장수",
      "hp": 1800, "speed": 50, "damage_to_castle": 8,
      "armor": 10, "gold_drop": 150, "sprite": "enemy_captain",
      "is_boss": true
    }
  }
}
```

### 5.3 로더

```python
# src/data/loader.py
import json
from pathlib import Path
from dataclasses import dataclass

DATA_ROOT = Path("src/data")

@dataclass(frozen=True)
class UnitDef:
    id: str
    name: str
    cost: int
    hp: int
    atk: int
    atk_speed: float
    range: int
    sprite: str
    size: tuple[int, int]
    projectile: str | None = None
    splash_radius: int | None = None

def load_units() -> dict[str, UnitDef]:
    raw = json.loads((DATA_ROOT / "units.json").read_text(encoding="utf-8"))
    out: dict[str, UnitDef] = {}
    for uid, u in raw["units"].items():
        out[uid] = UnitDef(
            id=uid, name=u["name"], cost=u["cost"], hp=u["hp"],
            atk=u["atk"], atk_speed=u["atk_speed"], range=u["range"],
            sprite=u["sprite"], size=tuple(u["size"]),
            projectile=u.get("projectile"),
            splash_radius=u.get("splash_radius"),
        )
    return out
```

**DECISION-5.1**: 데이터 외부화 + `dataclass(frozen=True)` 불변 객체. 코드는 데이터를 "읽기 전용"으로 다룬다.

---

## 6. 빌드 & 배포 (Build & Distribution)

### 6.1 PyInstaller 명령

```bat
:: tools\build.bat
pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name DefenseGameAnsi ^
    --icon assets\icon.ico ^
    --add-data "assets;assets" ^
    --add-data "src\data;src\data" ^
    --collect-data PIL ^
    --hidden-import PIL._tkinter_finder ^
    --clean ^
    src\main.py
```

| 옵션 | 의미 |
|------|------|
| `--onefile` | 단일 .exe로 패킹 |
| `--windowed` | 콘솔 창 숨김 (`pythonw` 효과) |
| `--add-data "assets;assets"` | Windows 구분자 `;`. 런타임에 `assets/` 폴더로 복사 |
| `--collect-data PIL` | Pillow 보조 데이터 누락 방지 |
| `--hidden-import PIL._tkinter_finder` | Pillow + tkinter 함께 쓸 때 필수 |
| `--icon` | 작업표시줄/창 아이콘 |

### 6.2 리소스 경로 처리 (PyInstaller 호환)

```python
# src/core/paths.py
import sys
from pathlib import Path

def resource_path(rel: str) -> Path:
    """개발 모드/PyInstaller --onefile 양쪽에서 동작."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return base / rel
```

### 6.3 산출물 구조

```
dist/
└── DefenseGameAnsi.exe        # 단일 실행파일
build/                         # PyInstaller 중간 산출물 (커밋 제외)
DefenseGameAnsi.spec           # 자동 생성 spec (커밋)
```

### 6.4 안티바이러스 false-positive 노트

- PyInstaller `--onefile`은 Windows Defender / SmartScreen에서 자주 의심 받음.
- 완화책:
  1. `--onedir`(폴더 배포)로 전환 → 오탐 감소. 단 사용자 경험 저하.
  2. 코드 서명 (EV 인증서) → 비용. **현 단계 보류**.
  3. UPX 압축 비활성 (`--noupx`) → 일부 휴리스틱 회피.
- SmartScreen 경고 시 사용자에게 "추가 정보 → 실행" 안내문 README에 명시.

**DECISION-6.1**: `--onefile`로 출시. 오탐 보고 누적 시 `--onedir` 전환 검토. 코드 서명은 v1.1 이후.

---

## 7. 성능 가드 (Performance Guardrails)

### 7.1 객체 수 상한

| 종류 | 상한 | 풀 초기 용량 |
|------|------|------------|
| 적 (enemy) | 80 | 80 |
| 아군 유닛 (ally) | 30 | 30 |
| 발사체 (projectile) | 100 | 100 |
| 이펙트 (effect) | 30 | 30 |
| HUD/배경 (정적) | n/a | — |
| **합계 (활성 엔티티)** | **240** | **— ** |

- 상한 초과 시: 새 적은 큐에 대기, 새 발사체는 발사 무시, 이펙트는 가장 오래된 것 회수.
- 풀 고갈은 게임 종료 사유가 아니다. **그레이스풀 디그레이드**.

### 7.2 매 프레임 측정

```python
# src/core/profiler.py
import time, collections

class FrameProfiler:
    def __init__(self, window: int = 60):
        self.samples = collections.deque(maxlen=window)
        self._t0 = 0.0

    def begin(self) -> None:
        self._t0 = time.perf_counter()

    def end(self) -> None:
        self.samples.append(time.perf_counter() - self._t0)

    def avg_ms(self) -> float:
        return (sum(self.samples) / len(self.samples) * 1000.0) if self.samples else 0.0

    def max_ms(self) -> float:
        return (max(self.samples) * 1000.0) if self.samples else 0.0
```

- 평균 12ms 초과 시 디버그 오버레이가 빨간색 경고.
- 최대 33ms(=30fps 1프레임) 초과가 연속 10회면 자동 로그 기록.

### 7.3 이미지 메모리 누수 회피

- 모든 `PhotoImage`는 `AssetManager._cache`가 강한 참조 보유.
- 엔티티는 `canvas.itemconfigure(image=...)`로 이미지만 교체, 객체 자체는 재사용.
- 씬 전환 시: 이전 씬 전용 이미지는 `AssetManager.evict(prefix="bg_stage01_")`로 명시 해제.

### 7.4 JSON 핫패스 회피

- 매 프레임 JSON 파싱 금지. 로딩은 씬 진입 1회.
- `dataclass(frozen=True)`로 만든 정의는 모듈 캐시.

---

## 8. 개발자 도구 (Dev Tools)

### 8.1 디버그 오버레이 (F3)

```
┌───────────────────────────────┐
│ FPS: 60.2 / avg 14.3ms / max 22ms
│ Entities: enemy 12 / ally 5 / proj 7
│ Pool free: e 68 / a 25 / p 93
│ Wave 2/5 — gold 240
│ Mouse: base (842, 510)  screen (1023, 612)
│ Scale: 0.83  DPI: 144
└───────────────────────────────┘
[좌표 그리드 (옅은 회색, 100px 간격)]
```

- F3 토글, F4 그리드만 토글, F5 핫리로드.
- 오버레이는 `Canvas` 상단 별도 tag 그룹(`overlay`)에 그리고 `tag_raise("overlay")`로 항상 최상위.

### 8.2 데이터 핫리로드 (개발 모드)

- 환경변수 `DEFGAME_DEV=1`일 때만 활성.
- F5 누르면 `data/*.json` 재로드 + 현재 씬 재초기화(전투 중이면 다음 웨이브부터 적용).
- 운영 빌드(`--windowed --onefile`)에서는 dev 분기 차단.

### 8.3 단위 테스트

```python
# tests/test_combat.py
from src.systems.combat import calc_damage

def test_armor_reduces_damage_linearly():
    assert calc_damage(atk=50, armor=10) == 40

def test_damage_cannot_go_negative():
    assert calc_damage(atk=5, armor=10) == 1   # 최소 1 보장

# tests/test_scaler.py
from src.core.scaler import Scaler

def test_letterbox_centers_canvas():
    s = Scaler(); s.update(2000, 1080)
    assert s.off_x > 0 and s.off_y == 0  # 가로가 남으므로 좌우 띠
```

- **목표 커버리지**: `systems/` 80%, `core/scaler` 90%.
- tk 위젯이 필요한 모듈(`scenes/`, `ui/`)은 통합 테스트 수동.

### 8.4 로깅

- 표준 `logging` 사용. 운영 빌드는 `WARNING` 이상, 개발은 `DEBUG`.
- 파일 출력: `%LOCALAPPDATA%/DefenseGameAnsi/logs/game.log` (로테이션).

---

## 9. 코드 컨벤션 (Code Conventions)

### 9.1 기본 규칙

- **PEP 8** 준수. 줄 길이 100 (black 기본 88 대신 합의).
- **타입 힌트 필수**. 공개 API는 100%, 내부는 권장.
- **docstring**: Google 스타일.
- **import 순서**: stdlib → 3rd-party → 1st-party(`src.*`). 각 그룹 사이 빈 줄.
- **네이밍**: 클래스 `PascalCase`, 함수/변수 `snake_case`, 상수 `UPPER_SNAKE`.
- **F-string 우선**, `%` 포매팅 금지.

### 9.2 도구 설정 (pyproject.toml 발췌)

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "B", "UP", "SIM"]
ignore = ["E501"]   # black이 다룸

[tool.black]
line-length = 100
target-version = ["py311"]

[tool.mypy]
python_version = "3.11"
strict = true
exclude = ["build/", "dist/"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q --strict-markers"
```

### 9.3 커밋 메시지

- Conventional Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`.
- 본문에 "왜"를 적는다.

### 9.4 PR 체크리스트

- [ ] 타입 힌트
- [ ] ruff/black/mypy 통과
- [ ] 신규 시스템 로직은 단위 테스트 동반
- [ ] 데이터 외부화 대상이 코드에 하드코딩되지 않았는가
- [ ] tk 위젯 import가 `systems/`에 새로 생기지 않았는가

---

## 10. 위험 & 미해결 (Risks & Open Questions)

### 10.1 OPEN: 사운드 라이브러리

| ID | OPEN-1 |
|----|--------|
| 질문 | BGM + 다중 SFX 동시 재생이 필요한가? 필요하다면 어떤 라이브러리로? |
| 옵션 | (a) `winsound`만 사용(SFX 단일) (b) `playsound` 도입 (c) 무사운드 |
| 임팩트 | 게임성. 외부 의존성 추가 여부 |
| 결정자 | 프로듀서 / 사용자 |
| 데드라인 | Alpha 빌드 전 |

### 10.2 OPEN: tkinter 성능 한계

| ID | OPEN-2 |
|----|--------|
| 질문 | 동시 엔티티 240체 + 60fps가 저사양 노트북에서 유지되지 않으면? |
| 백업안 | (a) Canvas 분할(전경/배경/HUD 3개) (b) 타깃 fps 30으로 하향 (c) **pygame 전환 — 사용자 명시 승인 필수** |
| 트리거 | QA 디바이스에서 평균 fps < 30이 5분 이상 |
| 데드라인 | Beta 진입 전 |

### 10.3 OPEN: 한글 폰트 라이선스

| ID | OPEN-3 |
|----|--------|
| 질문 | `Malgun Gothic`은 Windows 라이선스 하 사용 가능하나, 별도 게임 분위기 폰트(예: 손글씨/궁서체) 필요 시 라이선스는? |
| 후보 | 네이버 나눔손글씨, 한국저작권위원회 KoPub (둘 다 무료 상업 이용 가능, 출처 표기 의무) |
| 결정자 | 디자이너 |

### 10.4 OPEN: 데이터 핫리로드 범위

| ID | OPEN-4 |
|----|--------|
| 질문 | 전투 중 JSON 핫리로드 시 진행 중 엔티티 정의를 즉시 교체할지, 다음 웨이브부터 적용할지 |
| 잠정 | 다음 웨이브부터 적용 (안정성 우선) |

### 10.5 DECISION 요약 표

| ID | 결정 | 비고 |
|----|------|------|
| DECISION-1.1 | Python 3.11.x 고정 | PyInstaller 안정성 |
| DECISION-2.1 | `after(16)` 단일 루프, 가변 dt, 50ms 클램프 | §2.2 |
| DECISION-3.1 | 좌표/이미지/폰트 3축 독립 스케일 | §3.3 |
| DECISION-3.2 | Per-Monitor V2 DPI awareness, 단계 폴백 | §3.4 |
| DECISION-4.1 | 의존 방향 고정, `systems`에 tk import 금지 | §4.3 |
| DECISION-5.1 | 데이터 외부화 + `frozen dataclass` | §5.3 |
| DECISION-6.1 | `--onefile` 우선, 오탐 누적 시 `--onedir` | §6.4 |
| DECISION-A | 렌더 모델: 풀 + `coords()` 이동 | §0, §2.1 |
| DECISION-B | 데이터 주도 + tk 비의존 시스템 | §0, §4.3, §5 |

### 10.6 추적 표

| 항목 | 상태 | 담당 |
|------|------|------|
| OPEN-1 사운드 | 사용자 결정 대기 | Lead |
| OPEN-2 tk 성능 | QA 후 재평가 | Engineer A |
| OPEN-3 폰트 | 디자이너 확인 | Designer |
| OPEN-4 핫리로드 | 잠정 결정, Beta 후 재논의 | Engineer B |

---

## 부록 A. 게임 루프 시퀀스 다이어그램

```
   root.after(16) ──► GameLoop._tick
                          │
                          ├─► InputRouter.flush()
                          │
                          ├─► Scene.update(dt)
                          │      │
                          │      ├─► WaveSystem.update(dt)   → spawn Enemy
                          │      ├─► PathingSystem.update(dt)
                          │      ├─► CombatSystem.update(dt) → spawn Projectile, kill Enemy
                          │      ├─► EconomySystem.update(dt)
                          │      └─► Hero/Ally/Enemy/Projectile.update(dt)
                          │
                          ├─► Scene.render()
                          │      │
                          │      └─► entity.canvas_id → canvas.coords(...)
                          │
                          ├─► HUD.render()
                          ├─► Overlay.render()    (F3)
                          │
                          └─► root.after(16) ──► (next tick)
```

## 부록 B. 시스템 ↔ 엔티티 상호작용 표

| 시스템 | 읽는 엔티티 상태 | 변경하는 엔티티 상태 | 발행 이벤트 |
|--------|------------------|----------------------|------------|
| pathing | `pos`, `waypoint_idx` | `pos`, `waypoint_idx` | `enemy.reached_castle` |
| wave | — | spawn 큐 | `wave.started`, `wave.cleared` |
| combat | `pos`, `range`, `target`, `cooldown` | `hp`, `cooldown`, spawn Projectile | `enemy.killed`, `hero.took_damage` |
| economy | 자원 | 자원 | `gold.changed` |
| spawn | 풀 가용성 | 엔티티 활성화 | `entity.spawned` |
| input | 마우스/키 | — | `ui.click`, `ui.key` |

## 부록 C. 빠른 시작 (Onboarding)

```powershell
# 1. 가상환경
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. 의존성
pip install -r requirements-dev.txt

# 3. 실행 (개발 모드)
$env:DEFGAME_DEV = "1"
python -m src.main

# 4. 테스트
pytest

# 5. 빌드
.\tools\build.bat
```

---

> 본 문서는 살아있는 문서입니다. 이슈가 결정될 때마다 OPEN → DECISION으로 승격하고 버전을 증가시킵니다.
