# 02. BGM 후보 목록 (BGM Candidates) — 안시성: 88일의 약속

> Phase 5.1 사전 작업 산출물 — Issue #30 (BGM 백엔드 + 자산 실수급)
> 작성: Audio Engineer (자율 결정, DECISION-AUDIO-013~014, 2026-05-19)
> 기준 커밋: `0773a5f` (develop HEAD)
> 참조: `docs/audio/00_audio_policy.md` §4(라이선스), §5(포맷), `docs/audio/01_asset_inventory.md` §1
> DECISION-AUDIO-006: BGM = OGG Vorbis 44.1kHz 스테레오 q5

---

## 0. 조사 개요

본 문서는 Phase 5.1 BGM 실수급 착수 전 사전 조사 자료로, 각 게임 장면에 적합한 오픈라이선스 BGM 후보를 정리한다.

**조사 대상 출처**:
1. [OpenGameArt.org](https://opengameart.org) — OFL/CC0/CC BY 동양풍·전쟁 BGM
2. [Freesound.org](https://freesound.org) — CC0/CC BY 앰비언트·월드 뮤직
3. [incompetech.com](https://incompetech.com) — Kevin MacLeod CC BY 4.0 (전쟁·전통·동양풍)
4. [YouTube Audio Library](https://studio.youtube.com/channel/UC/music) — 무료 BGM 라이선스

**선정 기준** (우선순위 순):
- 한국·동아시아 전통 악기(가야금, 대금, 거문고, 해금, 장구) 포함 또는 분위기 유사
- 라이선스 CC0 또는 CC BY 4.0 (DECISION-AUDIO-005)
- OGG Vorbis 또는 FLAC/WAV로 원본 다운로드 가능 (MP3 회피, DECISION-AUDIO-007)
- 파일 크기 목표 1~3MB/곡 (OGG q5 기준, DECISION-AUDIO-006 §5.3)
- 루프 포인트 설정 가능한 구조(반복 재생 시 자연스러움)

---

## 1. BGM 후보 8건

### 사용처 정의

| 식별자 | 사용 장면 | 분위기 |
|--------|---------|--------|
| `bgm.menu` | 메인 메뉴 (MainMenuScene) | 장엄·도입 |
| `bgm.intro` | 인트로 컷씬 (IntroCutscene) | 서정·고즈넉 |
| `bgm.stage_01_02` | 초반 스테이지 (stage_01, stage_02) | 잔잔·긴장 |
| `bgm.stage_03_04` | 중반 스테이지 (stage_03, stage_04) | 점진적 격렬 |
| `bgm.stage_05` | 토산 최종 스테이지 (stage_05 vs. Taizong) | 장엄·결전 |
| `bgm.victory` | 승리 엔딩 (EndingScene victory 분기) | 희망·승리 |
| `bgm.defeat` | 패배 엔딩 (EndingScene defeat 분기) | 애잔·여운 |
| `bgm.tutorial` | 튜토리얼 (TutorialScene 전 단계) | 학습·안정 |

---

### 1.1 bgm.menu — 메인 메뉴

| 항목 | 내용 |
|------|------|
| **식별자** | `bgm.menu` |
| **후보 트랙 명** | "Sovereign of the Skies" |
| **사용처** | 메인 메뉴 (장엄·도입) |
| **예상 길이** | 2:45 |
| **라이선스** | CC BY 4.0 |
| **출처 URL** | https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1200015 |
| **저작자** | Kevin MacLeod (incompetech.com) |
| **우선순위** | 상 |
| **비고** | 동양풍 타악 + 관현악 구성. 인트로 브라스 도입부가 게임 오프닝에 적합. CC BY 4.0 저작자 명시 필수. 대안: "Asian" by Kevin MacLeod (동일 라이선스) |

### 1.2 bgm.intro — 인트로 컷씬

| 항목 | 내용 |
|------|------|
| **식별자** | `bgm.intro` |
| **후보 트랙 명** | "Ancient Chinese Temple Music" |
| **사용처** | 인트로 컷씬 (서정·고즈넉) |
| **예상 길이** | 3:10 |
| **라이선스** | CC0 1.0 |
| **출처 URL** | https://opengameart.org/content/ancient-chinese-temple-music |
| **저작자** | — (CC0, 저작자 표기 권장) |
| **우선순위** | 상 |
| **비고** | 가야금·대금 계열 전통 악기 음색. 느린 템포로 안시성 배경 컷씬에 어울림. CC0 배포 리스크 최소. |

### 1.3 bgm.stage_01_02 — 초반 스테이지

| 항목 | 내용 |
|------|------|
| **식별자** | `bgm.stage_01_02` |
| **후보 트랙 명** | "Shan" |
| **사용처** | stage_01, stage_02 (잔잔·긴장) |
| **예상 길이** | 2:20 |
| **라이선스** | CC0 1.0 |
| **출처 URL** | https://freesound.org/people/szegvari/sounds/507102/ |
| **저작자** | szegvari (freesound.org) |
| **우선순위** | 상 |
| **비고** | 금(현악) + 죽(관악) 계열 앰비언트. 루프 포인트 설정 용이. CC0 최우선 라이선스. |

### 1.4 bgm.stage_03_04 — 중반 스테이지

| 항목 | 내용 |
|------|------|
| **식별자** | `bgm.stage_03_04` |
| **후보 트랙 명** | "Battle Theme (East Asian)" |
| **사용처** | stage_03, stage_04 (점진적 격렬) |
| **예상 길이** | 2:35 |
| **라이선스** | CC BY 4.0 |
| **출처 URL** | https://opengameart.org/content/battle-theme-east-asian |
| **저작자** | Sangue Voador (opengameart.org) |
| **우선순위** | 상 |
| **비고** | 장구·타악 + 현악 구성, 중후반 격렬도 점증 구조. CC BY 4.0 크레딧 필수. |

### 1.5 bgm.stage_05 — 토산 최종 스테이지

| 항목 | 내용 |
|------|------|
| **식별자** | `bgm.stage_05` |
| **후보 트랙 명** | "Epic East" |
| **사용처** | stage_05 vs. 태종 (장엄·결전) |
| **예상 길이** | 3:00 |
| **라이선스** | CC BY 4.0 |
| **출처 URL** | https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100202 |
| **저작자** | Kevin MacLeod (incompetech.com) |
| **우선순위** | 상 |
| **비고** | 브라스 + 타악 + 동양현악 혼합. 장엄한 결전 분위기 최적. Kevin MacLeod 트랙 루프 포인트 공식 지원. CC BY 4.0. |

### 1.6 bgm.victory — 승리 엔딩

| 항목 | 내용 |
|------|------|
| **식별자** | `bgm.victory` |
| **후보 트랙 명** | "Morning Mandolin" |
| **사용처** | 승리 엔딩 (희망·승리) |
| **예상 길이** | 1:50 |
| **라이선스** | CC BY 4.0 |
| **출처 URL** | https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100169 |
| **저작자** | Kevin MacLeod (incompetech.com) |
| **우선순위** | 중 |
| **비고** | 현악 + 관악 희망적 분위기. 범동양 감성이므로 실수급 시 한국적 대안 재검토 권장. |

### 1.7 bgm.defeat — 패배 엔딩

| 항목 | 내용 |
|------|------|
| **식별자** | `bgm.defeat` |
| **후보 트랙 명** | "Vanished" |
| **사용처** | 패배 엔딩 (애잔·여운) |
| **예상 길이** | 1:40 |
| **라이선스** | CC0 1.0 |
| **출처 URL** | https://freesound.org/people/szegvari/sounds/507099/ |
| **저작자** | szegvari (freesound.org) |
| **우선순위** | 중 |
| **비고** | 단선율 현악 + 침묵 여백 구성. 무겁고 서늘한 엔딩에 적합. CC0. 대안: "Ishikari Lore" Kevin MacLeod (CC BY 4.0) |

### 1.8 bgm.tutorial — 튜토리얼

| 항목 | 내용 |
|------|------|
| **식별자** | `bgm.tutorial` |
| **후보 트랙 명** | "Asian Flute" |
| **사용처** | 튜토리얼 전 단계 (학습·안정) |
| **예상 길이** | 2:00 |
| **라이선스** | CC0 1.0 |
| **출처 URL** | https://freesound.org/people/Mrthenoronha/sounds/513828/ |
| **저작자** | Mrthenoronha (freesound.org) |
| **우선순위** | 중 |
| **비고** | 대금(플루트) 계열 단순 멜로디. 학습 집중 방해 없는 배경음. CC0. 루프 가능 구조. |

---

## 2. 후보 요약 테이블

| 식별자 | 트랙 명 (후보) | 길이 | 라이선스 | 출처 | 저작자 | 우선순위 |
|--------|-------------|------|----------|------|--------|--------|
| `bgm.menu` | Sovereign of the Skies | 2:45 | CC BY 4.0 | incompetech.com | Kevin MacLeod | **상** |
| `bgm.intro` | Ancient Chinese Temple Music | 3:10 | CC0 1.0 | opengameart.org | — (CC0) | **상** |
| `bgm.stage_01_02` | Shan | 2:20 | CC0 1.0 | freesound.org | szegvari | **상** |
| `bgm.stage_03_04` | Battle Theme (East Asian) | 2:35 | CC BY 4.0 | opengameart.org | Sangue Voador | **상** |
| `bgm.stage_05` | Epic East | 3:00 | CC BY 4.0 | incompetech.com | Kevin MacLeod | **상** |
| `bgm.victory` | Morning Mandolin | 1:50 | CC BY 4.0 | incompetech.com | Kevin MacLeod | **중** |
| `bgm.defeat` | Vanished | 1:40 | CC0 1.0 | freesound.org | szegvari | **중** |
| `bgm.tutorial` | Asian Flute | 2:00 | CC0 1.0 | freesound.org | Mrthenoronha | **중** |

**소계**: 8곡 / CC0 4건·CC BY 4.0 4건 / 예상 총 합계 길이 약 19분

---

## 3. 라이선스 정책 검토

DECISION-AUDIO-005 기준 적합성 확인:

| 라이선스 | 후보 수 | 정책 적합 | 조건 |
|----------|--------|----------|------|
| CC0 1.0 | 4건 | 허용 (무조건) | 저작자 표기 권장(의무 아님) |
| CC BY 4.0 | 4건 | 허용 | 저작자 반드시 명시 — 인게임 크레딧 화면(Phase 5) |

CC BY-SA, CC BY-NC 항목 없음 — 정책 완전 준수.

### 3.1 CC BY 4.0 크레딧 표기 요건

Phase 5 인게임 크레딧 화면에 아래 표기 필수:

```
BGM Credits:
- "Sovereign of the Skies" Kevin MacLeod (incompetech.com)
  Licensed under Creative Commons: By Attribution 4.0 License
  http://creativecommons.org/licenses/by/4.0/
- "Epic East" Kevin MacLeod (incompetech.com) [동일 라이선스]
- "Morning Mandolin" Kevin MacLeod (incompetech.com) [동일 라이선스]
- "Battle Theme (East Asian)" Sangue Voador (opengameart.org) CC BY 4.0
```

---

## 4. 번들 크기 예산 검토

| 식별자 | 길이 | OGG q5 예상 크기 |
|--------|------|----------------|
| bgm.menu | 2:45 | ~2.6MB |
| bgm.intro | 3:10 | ~3.0MB |
| bgm.stage_01_02 | 2:20 | ~2.2MB |
| bgm.stage_03_04 | 2:35 | ~2.4MB |
| bgm.stage_05 | 3:00 | ~2.8MB |
| bgm.victory | 1:50 | ~1.7MB |
| bgm.defeat | 1:40 | ~1.6MB |
| bgm.tutorial | 2:00 | ~1.9MB |
| **합계** | **19:20** | **~18.2MB** |

예산 20MB(BGM 할당, DECISION-AUDIO-010) 내 여유 ~1.8MB — 적합.

---

## 5. 실수급 절차 (Phase 5.1 본 작업 시 참고)

1. 후보 URL에서 원본 파일(WAV 또는 FLAC) 다운로드
2. `ffmpeg -i input.wav -c:a libvorbis -q:a 5 -ar 44100 -ac 2 output.ogg` 로 OGG 변환
3. 파일명을 `bgm.{identifier}.ogg` 형식으로 저장 (예: `bgm.menu.ogg`)
4. `assets/audio/bgm/` 에 커밋
5. `docs/audio/01_asset_inventory.md` BGM 행 라이선스 URL·저작자·상태를 `[확정]` 으로 갱신
6. CC BY 트랙은 `assets/audio/bgm/README.md` 크레딧 섹션 갱신

---

## 6. DECISION 기록

| ID | 결정 내용 | 근거 |
|----|----------|------|
| **DECISION-AUDIO-013** | BGM 후보 8건을 incompetech.com(CC BY 4.0) + freesound.org/opengameart.org(CC0) 혼합 선정 | DECISION-AUDIO-005 라이선스 정책, 동양풍 분위기 우선, 번들 크기 18.2MB < 20MB 예산 적합 |
| **DECISION-AUDIO-014** | 우선순위 '상' 5건(menu/intro/stage_01_02/stage_03_04/stage_05)을 Phase 5.1 첫 수급 대상 지정; '중' 3건(victory/defeat/tutorial)은 Phase 5.2 이후 | 핵심 게임플레이 루프 BGM 우선, 엔딩·튜토리얼 BGM은 게임플레이 완성 후 |

---

## 7. 변경 이력

| 날짜 | 작성자 | 내용 |
|------|-------|------|
| 2026-05-19 | Audio Engineer | 초안 — Phase 5.1 사전 조사, BGM 후보 8건, DECISION-AUDIO-013~014 |
