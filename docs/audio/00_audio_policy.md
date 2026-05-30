# 00. 오디오 정책 (Audio Policy) — 안시성: 88일의 약속

> Phase 4 킥오프 산출물 #1
> 작성: Audio Engineer (DECISION-PERSONA-001, 2026-05-19)
> 기준 커밋: `2b247b5` (develop HEAD, v0.3.0-rc.1 직후)
> 참조: `docs/04_technical_architecture.md` §10, `src/core/sound.py`, DECISION-Q-006

---

## 0. 목적 및 범위

본 문서는 게임 **안시성: 88일의 약속**의 오디오 시스템 전반에 대한 정책을 정의한다.
설계 의도, 현재 상태, 장기 기술 방향, 라이선스 정책, 파일 포맷 기준, 번들링 방식, QA 회귀 연동 방법을 포함한다.

**본 문서가 적용되는 범위**:
- `src/core/sound.py` 사운드 백엔드 설계
- `assets/audio/` 디렉터리 자산 관리
- `docs/audio/01_asset_inventory.md` 인벤토리 운영
- Phase 4~5 오디오 기능 구현 로드맵
- QA 회귀 매트릭스의 Audio 열 항목

---

## 1. 사운드 카테고리 정의

(DECISION-AUDIO-001)

| 카테고리 | 식별자 접두사 | 설명 | 재생 특성 |
|----------|--------------|------|-----------|
| **BGM** (Background Music) | `bgm_` | 메인 메뉴·배틀·엔딩 배경음악 | 루프, 장시간, 단일 채널 점유 |
| **SFX** (Sound Effects) | `sfx_` | 전투 효과음 — 발사·타격·사망·스킬 | 짧음, 다채널 동시 재생 가능 |
| **UI Sound** | `ui_` | 버튼 클릭·메뉴 전환·다이얼로그·보상 | 극히 짧음 (<0.3초), 즉시 재생 |
| **Voice / 외침** | `voice_` | 영웅 및 장수 전투 외침, 이벤트 대사 | 짧음-중간, 자막 연동 고려 |

> 각 카테고리는 독립 볼륨 채널을 갖는 것을 장기 목표로 한다 (DECISION-AUDIO-002).

---

## 2. 현재 상태 — winsound 스텁의 한계

(DECISION-Q-006 출발점)

`src/core/sound.py`는 현재 **no-op 스텁** 상태이다. Phase 3 개발 당시 `winsound`(Windows stdlib) 기반
단일 채널 BGM을 임시 구현 후 삭제하고, 백엔드 확정 전까지 인터페이스만 고정하는 방식을 택했다.

### 2.1 현 스텁의 기술적 한계

| 한계 | 내용 |
|------|------|
| **플랫폼 의존** | `winsound`는 Windows 전용. macOS/Linux 배포 시 전면 교체 필요 |
| **단일 채널** | BGM 재생 중 SFX를 재생하면 BGM이 중단됨 |
| **비동기 한계** | `winsound.SND_ASYNC` 플래그는 단일 스레드로 2개 이상 동시 재생 불가 |
| **포맷 제한** | WAV 파일만 지원. OGG/MP3 재생 불가 |
| **볼륨 제어 없음** | 마스터/채널별 볼륨 조절 API 없음 |
| **루프 제어 제한** | `SND_LOOP`는 플래그로만 제어 — 페이드인/아웃 불가 |

### 2.2 현 no-op 스텁의 장점

현재 스텁은 `play_bgm()`, `play_sfx()`, `stop_all()` 인터페이스를 이미 노출하므로,
호출부 코드 변경 없이 백엔드만 교체할 수 있는 구조적 이점이 있다.

---

## 3. 장기 방향 — 외부 패키지 검토

(DECISION-AUDIO-003)

### 3.1 후보 백엔드 비교

| 옵션 | 장점 | 단점 | 도입 시점 후보 |
|------|------|------|---------------|
| **pygame.mixer (독립 사용)** | 안정적 다채널, 크로스플랫폼, OGG 지원, 루프·페이드 API | pygame 풀 패키지 (~15MB), 사용자 정책 재확인 필요 | Phase 5 |
| **simpleaudio** | 경량, 크로스플랫폼, 다채널 | MP3/OGG 직접 불가, 루프 API 없음 | Phase 4 후반 (SFX 한정) |
| **sounddevice + soundfile** | NumPy 기반 정밀 제어 | 의존성 2개, 게임용 API 없음 | 해당 없음 |
| **winsound (현재)** | stdlib, 의존성 0 | §2.1 한계 전체 | 스텁 유지 (현재) |

### 3.2 도입 시점 결정 원칙

**DECISION-AUDIO-004**: 외부 패키지 도입 시점은 다음 조건을 모두 충족할 때로 한다:
1. Phase 4 후반 — 핵심 전투 로직(Phase 4 팀 산출물) 안정화 후
2. `requirements.txt` 변경 PR에서 리드 페르소나(Tech Lead) 명시적 승인
3. DECISION-P3-005(stdlib 우선 원칙)와 충돌 여부 재검토 완료
4. PyInstaller `--onefile` 빌드 사이즈 영향(+목표 ≤ 50MB, DECISION-D-110) 검증

**현 Phase 4 킥오프 기준 권장 경로**: Phase 4 후반에 `simpleaudio`(SFX 전용)를 시범 도입,
BGM은 Phase 5에서 `pygame.mixer` 또는 동급 검토.

---

## 4. 라이선스 정책

(DECISION-AUDIO-005)

본 프로젝트의 오디오 자산은 **상용 배포·재배포 허용** 라이선스만 채택한다.

### 4.1 허용 라이선스 목록

| 라이선스 | 허용 여부 | 조건 |
|----------|----------|------|
| **CC0 1.0 (Public Domain)** | 허용 | 저작자 표시 권장(의무 아님) |
| **CC BY 4.0** | 허용 | 저작자 반드시 명시 (`docs/audio/01_asset_inventory.md`에 기재) |
| **CC BY-SA 4.0** | 조건부 허용 | 게임 전체를 SA 조건으로 배포할 경우만. 단독 사용 지양 |
| **OFL 1.1** | 오디오 해당 없음 (폰트 전용) | 참고 선례: Phase 3.4 폰트 정책 |
| **CC BY-NC** | 금지 | NonCommercial — 상용 배포 불가 |
| **Royalty-Free (비 CC)** | 개별 검토 필요 | "RF" 표기만으로 재배포·번들링 허용 여부 상이 |
| **무출처/불명** | 금지 | 라이선스 확인 불가 자산 사용 불가 |

### 4.2 출처·저작자 명시 규칙

- **모든 외부 오디오 자산**은 `docs/audio/01_asset_inventory.md`에 다음을 필수 기재:
  - 자산 식별자, 파일명, 라이선스 ID, 원본 URL, 저작자(크레딧 표기명)
- 인게임 크레딧 화면(`EndingScene` 또는 별도 Credits Scene)에 오디오 저작자 목록 표시 — Phase 5 구현 시 반영
- **자체 제작** 또는 **AI 생성** 자산은 `[자체제작]` 또는 `[AI생성]` 라벨로 구분하고 생성 도구 명시

### 4.3 라이선스 매트릭스

| 카테고리 | 권장 라이선스 | 차선 | 금지 |
|----------|--------------|------|------|
| BGM | CC0, CC BY 4.0 | CC BY-SA 4.0 (조건 충족 시) | CC BY-NC, 무출처 |
| SFX | CC0, CC BY 4.0 | CC BY-SA 4.0 (조건 충족 시) | CC BY-NC, 무출처 |
| UI Sound | CC0 우선 | CC BY 4.0 | CC BY-NC, 무출처 |
| Voice | CC0, CC BY 4.0, 자체제작 | — | CC BY-NC, 무출처 |

---

## 5. 파일 포맷 기준

(DECISION-AUDIO-006)

### 5.1 권장 포맷

| 카테고리 | 포맷 | 이유 |
|----------|------|------|
| SFX, UI Sound | **WAV (PCM, 비압축)** | 지연 없는 즉시 재생, 짧은 파일은 압축 불필요 |
| BGM | **OGG Vorbis** | 손실 압축으로 파일 크기 절감, 특허·라이선스 부담 없음 |
| Voice | WAV 또는 OGG Vorbis | 길이에 따라 선택 (< 3초 WAV, ≥ 3초 OGG) |

### 5.2 MP3 회피 이유

MP3는 과거 특허(Fraunhofer, Thomson) 이슈가 있었으며, 일부 인코더/디코더는 여전히
플랫폼별 라이선스 조건이 상이하다. 오픈소스 배포 환경에서 OGG Vorbis가 더 명확한 선택이다
(DECISION-AUDIO-007).

### 5.3 기술 규격

| 항목 | SFX / UI Sound | BGM | Voice |
|------|----------------|-----|-------|
| 샘플레이트 | **44,100 Hz** | **44,100 Hz** | **44,100 Hz** |
| 채널 | **모노 (1ch)** | **스테레오 (2ch)** | 모노 권장 |
| 비트 깊이 | 16-bit PCM | (OGG 손실 인코딩) | 16-bit PCM |
| OGG 품질 | 해당 없음 | **q5 (~160kbps)** | q4 (~128kbps) |
| 파일 크기 목표 | < 100KB/파일 | 1~3MB/곡 | < 300KB/파일 |

### 5.4 파일명 컨벤션

영문 snake_case, 카테고리 접두사 사용 (DECISION-AUDIO-008):
```
bgm_main_menu.ogg
bgm_stage_01_battle.ogg
sfx_arrow_shoot.wav
sfx_enemy_hit.wav
sfx_enemy_death.wav
ui_button_click.wav
ui_menu_transition.wav
voice_hero_skill_01.wav
```

---

## 6. PyInstaller 번들링

(DECISION-AUDIO-009)

Phase 3.4에서 `assets/fonts/`를 PyInstaller spec에 번들링한 선례(#21, DECISION-TL-009)를 그대로 따른다.

### 6.1 디렉터리 구조

```
assets/
├── audio/
│   ├── bgm/          # BGM OGG 파일
│   ├── sfx/          # SFX WAV 파일
│   ├── ui/           # UI Sound WAV 파일
│   └── voice/        # Voice WAV/OGG 파일
├── fonts/            # (기존) Noto Sans KR
└── images/           # (기존) 스프라이트·배경
```

### 6.2 spec 파일 추가 패턴

`defensegame.spec`의 `datas` 리스트에 다음 항목 추가 (Phase 4 후반 구현 시):

```python
datas = [
    ("assets/fonts", "assets/fonts"),   # 기존
    ("assets/audio", "assets/audio"),   # 신규 — DECISION-AUDIO-009
]
```

### 6.3 런타임 경로 해석

폰트 로딩과 동일한 `_MEIPASS` 패턴 사용 (`src/core/fonts.py` 참조):

```python
import sys, os

def _audio_base() -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "assets", "audio")
    return os.path.join(os.path.dirname(__file__), "..", "..", "assets", "audio")
```

### 6.4 번들 크기 예산

| 카테고리 | 파일 수 | 예상 크기 |
|----------|--------|----------|
| BGM | ~8곡 | ~20MB |
| SFX | ~20개 | ~2MB |
| UI Sound | ~10개 | ~0.5MB |
| Voice | ~15개 | ~5MB |
| **합계** | **~53개** | **~27.5MB** |

전체 자산 합계 목표 ≤ 50MB (DECISION-D-110) 내 오디오 할당 **≤ 30MB** (DECISION-AUDIO-010).

---

## 7. QA 회귀 매트릭스 연동

(DECISION-AUDIO-011)

`docs/qa/regression_matrix.md`의 `Audio` 열에 다음 시나리오 행 추가를 QA Lead에게 권장한다.

### 7.1 추가 권장 시나리오

| 시나리오 ID | 시나리오 설명 | Audio 열 | 자동화 가능 여부 |
|------------|-------------|----------|----------------|
| `AU-01` | `SoundManager.play_bgm("main_menu")` 호출 시 예외 없음 (no-op 포함) | ✓ | pytest |
| `AU-02` | `SoundManager.play_sfx("sfx_arrow_shoot")` 호출 시 예외 없음 | ✓ | pytest |
| `AU-03` | `SoundManager.play_sfx("ui_button_click")` 호출 시 예외 없음 | ✓ | pytest |
| `AU-04` | `SoundManager.stop_all()` 호출 시 예외 없음 | ✓ | pytest |
| `AU-05` | `SoundManager.set_master_volume(0.5)` 호출 시 예외 없음 (미래 API) | ✗ | 구현 후 추가 |
| `AU-06` | `SoundManager.mute()` 호출 시 예외 없음 (미래 API) | ✗ | 구현 후 추가 |
| `AU-07` | BGM 루프 재생 중 SFX 동시 재생 가능 (백엔드 교체 후) | ✗ | 구현 후 추가 |
| `AU-08` | PyInstaller 빌드 시 `assets/audio/` 경로 정상 해석 | ✗ | 수동 검수 |

### 7.2 현재 자동화 가능 항목 (no-op 스텁 대상)

AU-01~AU-04는 현재 no-op 스텁으로도 pytest 자동화 가능. `tests/test_sound.py` 신규 파일 생성 권장.

---

## 8. 결정 이력 (DECISION 목록)

| ID | 결정 내용 | 근거 |
|----|----------|------|
| **DECISION-AUDIO-001** | 사운드 카테고리를 BGM/SFX/UI Sound/Voice 4종으로 정의 | 게임 씬 구성(GDD §4) 및 재생 특성 분류 |
| **DECISION-AUDIO-002** | 카테고리별 독립 볼륨 채널을 장기 목표로 설정 | 사용자 경험, 접근성 |
| **DECISION-AUDIO-003** | pygame.mixer(Phase 5) / simpleaudio(Phase 4 후반) 이중 경로로 백엔드 검토 | 의존성 최소화(DECISION-P3-005) + 기능 요구 균형 |
| **DECISION-AUDIO-004** | 외부 패키지 도입은 Phase 4 후반 이후, Tech Lead 승인 필수 | stdlib 우선 원칙, PyInstaller 빌드 크기 검증 |
| **DECISION-AUDIO-005** | 오디오 자산 라이선스는 CC0/CC BY 4.0만 허용 (CC BY-SA 조건부) | 상용 배포 가능성, OFL 1.1 폰트 선례 |
| **DECISION-AUDIO-006** | SFX/UI는 WAV(비압축), BGM은 OGG Vorbis(압축) | 재생 지연·파일 크기·포맷 호환성 |
| **DECISION-AUDIO-007** | MP3 포맷 회피 | 플랫폼별 라이선스 불확실성 |
| **DECISION-AUDIO-008** | 파일명 snake_case + 카테고리 접두사 컨벤션 | 코드 자산 ID 일치, 기존 이미지 자산 컨벤션 통일 |
| **DECISION-AUDIO-009** | PyInstaller spec에 `assets/audio/` 번들링, fonts/ 선례 동일 방식 | Phase 3.4 번들링(#21) 패턴 재사용 |
| **DECISION-AUDIO-010** | 오디오 자산 번들 예산 ≤ 30MB | 전체 ≤ 50MB 목표(DECISION-D-110) 내 배분 |
| **DECISION-AUDIO-011** | 회귀 매트릭스 Audio 열에 AU-01~AU-08 시나리오 추가 권장 | QA Lead 연동, 사운드 회귀 조기 감지 |

---

## 9. 미결 사항 (OPEN)

| ID | 항목 | 예상 결정 시점 |
|----|------|--------------|
| OPEN-AUDIO-001 | pygame.mixer vs simpleaudio 최종 선택 | Phase 4 후반 라운드 |
| OPEN-AUDIO-002 | Voice(외침) 실제 자산 수급 — 자체 제작 vs 오픈 게임 아트 | Phase 5 |
| OPEN-AUDIO-003 | 인게임 크레딧 화면 오디오 저작자 표시 UI 설계 | Phase 5 |
| OPEN-AUDIO-004 | `simpleaudio` 도입 시 Linux/macOS 빌드 테스트 환경 구성 | Phase 4 후반 |