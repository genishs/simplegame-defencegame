# 03. BGM 백엔드 제안 (BGM Backend Proposal) — 안시성: 88일의 약속

> Phase 5.1 사전 작업 산출물 — Issue #30 (BGM 백엔드 + 자산 실수급)
> 작성: Audio Engineer (자율 결정, DECISION-AUDIO-013, 2026-05-19)
> 기준 커밋: `0773a5f` (develop HEAD)
> 참조: `docs/audio/00_audio_policy.md` §3(백엔드 검토), DECISION-AUDIO-003/004/012
> 선행 결정: DECISION-AUDIO-012 — simpleaudio SFX 시범 도입 완료 (Phase 4 후반, PR #42)

---

## 0. 목적

Phase 5.1에서 BGM 스트리밍 재생 백엔드를 도입하기 위한 정책 검토 문서.
**실제 `requirements.txt` 추가 및 구현은 Phase 5.1 본 작업 위임** — 본 문서는 정책 결정만 기록한다.

---

## 1. 현재 상태 요약

| 기능 | 현재 상태 | 담당 패키지 |
|------|---------|------------|
| SFX/UI Sound 재생 | 구현 완료 (Phase 4 후반) | `simpleaudio` (DECISION-AUDIO-012) |
| BGM 재생 | **no-op stub** | — (Phase 5 위임) |
| BGM 루프/페이드 | 미구현 | — |
| BGM 볼륨 독립 채널 | 미구현 | — |

`src/core/sound.py` `play_bgm()`, `stop_bgm()` 은 현재 로그만 출력하는 stub 상태이다.

---

## 2. 후보 백엔드 비교

### 2.1 pygame.mixer (권장)

| 항목 | 내용 |
|------|------|
| **패키지** | `pygame` (또는 `pygame-ce`) |
| **설치** | `pip install pygame` |
| **크기 추가** | ~15MB (Windows 바이너리 포함, PyInstaller 번들 시) |
| **OGG 지원** | 네이티브 지원 (libvorbis 내장) |
| **MP3 지원** | 플랫폼 의존 (회피 권장, DECISION-AUDIO-007) |
| **스트리밍** | `pygame.mixer.music` — 파일 전체 메모리 로드 없이 스트리밍 |
| **루프** | `pygame.mixer.music.play(loops=-1)` (무한 루프), `loops=N` (N회) |
| **페이드 인/아웃** | `play(fade_ms=...)`, `fadeout(ms)` 내장 API |
| **채널 독립성** | `pygame.mixer.music` (BGM) + `pygame.mixer.Channel` (SFX) 완전 분리 |
| **볼륨 제어** | `pygame.mixer.music.set_volume(0.0~1.0)` — BGM 독립 볼륨 |
| **크로스플랫폼** | Windows / macOS / Linux 모두 지원 |
| **PyInstaller 호환** | 검증된 패턴 다수, `--hidden-import pygame` 필요 |
| **단점** | pygame 풀 패키지 포함으로 ~15MB 추가. tkinter 앱에서 `pygame.init()` 병용 시 이벤트 루프 충돌 가능 → `pygame.mixer.init()` 만 초기화해 회피 가능 |

### 2.2 simpleaudio (현재 SFX 백엔드, BGM 부적합)

| 항목 | 내용 |
|------|------|
| **패키지** | `simpleaudio` |
| **현재 사용** | SFX/UI Sound (DECISION-AUDIO-012) |
| **OGG 지원** | 없음 (WAV 전용) |
| **스트리밍** | 없음 — 파일 전체 메모리 로드 |
| **루프 API** | 없음 — 반복 재생을 위한 별도 스레드 코드 필요 |
| **페이드** | 없음 |
| **BGM 적합성** | 부적합 — OGG 미지원, 루프/페이드 API 없음 |
| **결론** | SFX 전용으로 유지. BGM에는 사용 불가 |

### 2.3 PyOgg + sounddevice

| 항목 | 내용 |
|------|------|
| **패키지** | `PyOgg` + `sounddevice` (2개 의존성) |
| **OGG 지원** | PyOgg가 libvorbis 바인딩 제공 |
| **스트리밍** | 직접 구현 필요 (콜백 기반) |
| **루프/페이드** | 직접 구현 필요 |
| **크기** | 상대적으로 경량 (~5MB) |
| **복잡도** | 높음 — 스트리밍·루프·페이드 모두 수작업 구현 |
| **결론** | 기능 대비 구현 비용 과다. pygame.mixer 대비 우위 없음 |

### 2.4 winsound (현 no-op 전환 전 구 백엔드)

| 항목 | 내용 |
|------|------|
| **패키지** | stdlib (의존성 0) |
| **OGG 지원** | 없음 |
| **BGM 루프** | SND_LOOP 플래그만 (제한적) |
| **크로스플랫폼** | Windows 전용 |
| **결론** | §2.1 한계 전체 (docs/audio/00_audio_policy.md §2.1). BGM 용도 완전 부적합 |

---

## 3. 비교 요약 매트릭스

| 기준 | pygame.mixer | simpleaudio | PyOgg+sounddevice | winsound |
|------|-------------|------------|------------------|---------|
| OGG 스트리밍 재생 | 네이티브 | 불가 | 직접 구현 | 불가 |
| 루프 API | 내장 | 없음 | 직접 구현 | 제한 |
| 페이드 인/아웃 | 내장 | 없음 | 직접 구현 | 없음 |
| BGM/SFX 채널 독립 | 완전 분리 | 불가 | 가능(복잡) | 불가 |
| 크로스플랫폼 | 완전 | 거의 완전 | 완전 | Windows 전용 |
| 패키지 크기 | ~15MB | ~1MB | ~5MB | 0 (stdlib) |
| 구현 복잡도 | 낮음 | 낮음 | 높음 | 낮음 |
| SFX 현재 사용 | 별도 가능 | 이미 도입 | — | — |
| **BGM 도입 권장** | **YES** | NO | NO | NO |

---

## 4. tkinter + pygame.mixer 병용 전략

tkinter 이벤트 루프와 pygame 이벤트 루프의 충돌을 회피하기 위해:

```python
# sound.py Phase 5.1 구현 패턴 (예정)
import pygame.mixer

def _init_mixer():
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        # pygame.init() 은 호출하지 않음 — tkinter 이벤트 루프 충돌 방지
```

`pygame.mixer.init()` 만 단독 초기화하면 `pygame.display` / `pygame.event` 등 tkinter와 충돌하는 모듈이 활성화되지 않는다. 이 패턴은 pygame 공식 문서에서도 인정된 사용법이다.

---

## 5. Phase 5.1 구현 계획 (본 작업 위임)

본 라운드에서 실제 구현은 금지 (Phase 5.1 본 작업 위임). 구현 방향만 기록한다.

### 5.1 requirements.txt 추가 (Phase 5.1)

```
# Phase 5.1 추가 예정 (Tech Lead 승인 필요, DECISION-AUDIO-004)
pygame>=2.5.0
```

> simpleaudio는 유지 (SFX 전용). pygame은 BGM 전용으로 추가.

### 5.2 play_bgm() 구현 시그니처 (Phase 5.1)

```python
def play_bgm(
    self,
    name: str,
    *,
    loop: bool = True,
    fade_in: float = 1.0,
) -> None: ...

def stop_bgm(self, *, fade_out: float = 1.0) -> None: ...

def set_bgm_volume(self, v: float) -> None: ...  # BGM 독립 볼륨
```

상세 docstring은 `src/core/sound.py` 참조 (본 라운드에서 갱신 완료).

### 5.3 PyInstaller hiddenimport (Phase 5.1)

```python
# defensegame.spec
hiddenimports=["pygame", "pygame.mixer"],
```

---

## 6. DECISION 기록

| ID | 결정 내용 | 근거 |
|----|----------|------|
| **DECISION-AUDIO-013** | BGM 백엔드로 **pygame.mixer** 채택 결정 | OGG 스트리밍·루프·페이드 API 내장, tkinter 병용 가능, DECISION-AUDIO-004 조건 충족 경로 명확. 패키지 크기 ~15MB는 DECISION-AUDIO-010 예산(30MB) 내 수용 가능 |

> 주의: DECISION-AUDIO-013은 02_bgm_candidates.md 의 BGM 후보 선정 결정 번호와 동일하게 사용되었음.
> 본 문서의 DECISION-AUDIO-013은 **BGM 백엔드로 pygame.mixer 채택** 결정으로 구분 기록.
> (BGM 후보 선정은 02_bgm_candidates.md §6에 동일 ID로 기록됨 — 추후 DECISION-AUDIO-015로 재번호 권장)

---

## 7. 미결 사항 (OPEN)

| ID | 항목 | 예상 결정 시점 |
|----|------|--------------|
| OPEN-AUDIO-005 | pygame.mixer.init() vs pygame.init() tkinter 충돌 실제 테스트 | Phase 5.1 착수 시 |
| OPEN-AUDIO-006 | simpleaudio + pygame.mixer 공존 시 오디오 드라이버 충돌 검증 | Phase 5.1 착수 시 |
| OPEN-AUDIO-007 | pygame 2.x vs pygame-ce(community edition) 선택 | Phase 5.1 Tech Lead 승인 라운드 |

---

## 8. 변경 이력

| 날짜 | 작성자 | 내용 |
|------|-------|------|
| 2026-05-19 | Audio Engineer | 초안 — pygame.mixer vs simpleaudio vs PyOgg 비교, DECISION-AUDIO-013 기록 |
