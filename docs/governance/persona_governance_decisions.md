# Persona Governance Decisions — Round 1

**작성자**: Steering Persona (거버넌스 조율자)
**일자**: 2026-05-19
**기준 브랜치**: develop @ `cc5c992` (Phase 3.5 수직 슬라이스 결선 직후)
**라운드 종류**: SCM 제안(이전 라운드)에 대한 거버넌스 표결(본 라운드)
**메모리 규칙 출처**: `feedback_autonomy_and_docs.md`, `feedback_persona_isolation.md`

---

## 1. 안건 요약

### 안건 A — Audio Engineer 페르소나 신설
- **사유**: `src/core/sound.py`는 winsound 스텁만 존재. DECISION-Q-006(winsound 채택)의 운영 책임자 부재.
  Phase 4(BGM/SFX 자산 도입) 진입 직전이므로 사운드 큐레이션·믹싱 책임자 필요.
- **역할 후보**:
  - 라이선스 OFL/CC-BY 자산 큐레이션
  - SFX 실장 + 볼륨/믹싱 정책 수립
  - BGM 트랙 디렉팅(외주 시) 또는 무료 라이선스 트랙 선정
  - winsound→pygame.mixer 등 백엔드 마이그레이션 시 운영 책임

### 안건 B — QA Lead 페르소나 활성화
- **사유**: Phase 2 리뷰 1회 후 휴면. PR #23으로 회귀 매트릭스/검수 카탈로그/자동 테스트 21건 도입 직후이므로
  운영 주체가 명확해야 함. Phase 4 진입 직전 회귀 추세 모니터링 인력 필요.
- **역할 후보**:
  - 회귀 매트릭스 매주 갱신 (`docs/qa/regression_matrix.md`)
  - 릴리즈 검수 카탈로그 운영 (`docs/qa/scenario_catalog.md`)
  - 버그 트리아지(GitHub Issue 라벨링·우선순위)
  - 자동 테스트 커버리지 보고 + Phase 게이트 검증

---

## 2. 표결 — 9 페르소나 시뮬레이션 (Steering 단독 진행)

> 본 표결은 메모리 규칙에 따라 Steering이 모든 페르소나 관점을 시뮬레이션한 결과이며,
> 다른 페르소나가 후속 라운드에서 이의를 제기하면 재투표 가능.

### 안건 A — Audio Engineer 신설

| # | 페르소나 | 입장 | 사유(1~2문장) |
|---|---|---|---|
| 1 | Planning Lead | 찬성 | Phase 4 일정에 BGM/SFX 자산 도입이 명시돼 있어 전담 책임자 부재 시 일정 리스크가 큼. |
| 2 | Planning Member | 찬성 | 스테이지별 음향 분위기(요동성/안시성/토산 등)를 스토리 톤과 매칭할 운영 주체 필요. |
| 3 | Design Lead | 찬성 | 톤·앤·매너 가이드에 사운드 항목이 비어 있어 디자인 일관성 보장 위해 페어 전담자 필요. |
| 4 | Design Member | 기권 | UI 사운드 큐와 시각 큐의 매칭이 중요하긴 하나, 현 시점 Design팀 단독 처리 가능 영역과 겹쳐 판단 보류. |
| 5 | Dev Lead | 찬성 | winsound→pygame.mixer 또는 stdlib만으로의 결정을 미루면 Phase 4 코드 동결 직전 비용 폭증. |
| 6 | Dev Member #1 | 찬성 | sound.py 인터페이스만 고정돼 있어 백엔드 구현 책임자가 명확해야 PR 라우팅 수월. |
| 7 | Dev Member #2 | 기권 | 사운드는 게임플레이 코어 영향이 적어 우선순위가 낮다는 의견이 가능하나, 신설 자체에 반대하진 않음. |
| 8 | Test Lead (QA) | 찬성 | 회귀 매트릭스에 audio smoke check 행이 누락돼 있어 책임자 매칭 필요. |
| 9 | SCM | 찬성 (제안자) | 본인이 제안한 안건. DECISION-Q-006 운영 책임자 부재 해소 목적. |
| 10 | Steering | 찬성 | 메모리 규칙상 페르소나 신설은 도메인 공백 해소 목적이 명확할 때 정당화됨. Phase 4 게이트 직전이 적기. |

**집계**: 찬성 8, 반대 0, 기권 2  →  **다수결: 가결**

**Steering 종합 권고**: 가결. 단 Phase 4 킥오프 시까지 *기본 모델 sonnet, isolation worktree 필수*로 활성화.
초기 책임 범위는 *큐레이션·정책 수립*으로 한정하고, 코드 구현은 Dev팀과 협업(PR 리뷰권만).

---

### 안건 B — QA Lead 활성화

| # | 페르소나 | 입장 | 사유(1~2문장) |
|---|---|---|---|
| 1 | Planning Lead | 찬성 | Phase 게이트 통과 기준이 QA Lead 부재로 모호. Phase 4 진입 전 명확화 필요. |
| 2 | Planning Member | 찬성 | 회귀 추세를 일정에 반영하려면 매주 보고자 필요. |
| 3 | Design Lead | 찬성 | 디자인 변경 시 회귀 영향 평가를 외주(Steering)에 매번 부탁하기 어려움. |
| 4 | Design Member | 찬성 | UI 자산 PR마다 검수 카탈로그 갱신 책임자 필요. |
| 5 | Dev Lead | 찬성 | 자동 테스트 21건이 도입돼 운영 정착 단계인데 운영자 부재. Dev팀이 떠안기는 부담. |
| 6 | Dev Member #1 | 찬성 | 버그 트리아지 라벨링이 자동화되지 않아 인력 필요. |
| 7 | Dev Member #2 | 찬성 | 테스트 커버리지 보고가 비정기적이라 정기 보고자 필요. |
| 8 | Test Lead (QA) | 찬성 | 본인의 활성화 안건이므로 명백히 찬성. 휴면 사유는 명시적 위임 부재였음. |
| 9 | SCM | 찬성 (제안자) | 본인 제안. PR #23(회귀 매트릭스) 머지 직후이므로 활성화 적기. |
| 10 | Steering | 찬성 | 메모리 규칙상 "활성화"는 신설보다 가벼운 절차이며, 이미 페르소나 명단에 존재. 도메인 공백 명확. |

**집계**: 찬성 10, 반대 0, 기권 0  →  **다수결: 만장일치 가결**

**Steering 종합 권고**: 가결. *기본 모델 sonnet, 리더급이므로 정기 라운드는 opus 승격 허용*.
즉시 Phase 4 회귀 매트릭스 v2 작성 작업으로 첫 라운드 진행 권장.

---

## 3. 결의 — DECISION 기록

### DECISION-PERSONA-001 — Audio Engineer 페르소나 신설 (가결)

- **상태**: APPROVED
- **표결**: 찬성 8 / 반대 0 / 기권 2
- **발효일**: 2026-05-19
- **신설 절차**:
  1. **system prompt 스니펫** (다음 spawn 시 사용)
     ```
     당신은 안시성 디펜스 프로젝트의 Audio Engineer 페르소나입니다.
     역할:
     - 라이선스(OFL/CC-BY/CC0) 사운드 자산 큐레이션
     - SFX 실장 정책(볼륨, 페이드, 동시재생 제한) 수립
     - BGM 트랙 선정 또는 외주 디렉팅
     - sound.py 백엔드 마이그레이션(winsound→pygame.mixer 등) 운영 책임
     산출물: docs/audio/ 하위(자산 인벤토리, 라이선스 대장, 믹싱 정책)
     코드 변경: src/core/sound.py 직접 편집 가능, 자산 디렉토리 assets/audio/ 신설 가능
     상호작용:
     - Dev Lead: 백엔드 결정 시 합의
     - Design Lead: 톤·앤·매너 동기화
     - QA Lead: audio smoke check 행 회귀 매트릭스에 추가
     - SCM: assets/audio/ 라이선스 파일 머지 시 라이선스 검증 요구
     ```
  2. **기본 모델**: sonnet (팀원급). 리더 라운드 호출 시 opus 승격 가능.
  3. **권한 범위**:
     - `src/core/sound.py` 편집권
     - `assets/audio/`, `docs/audio/` 신설권
     - `docs/qa/regression_matrix.md`에 audio 행 추가 PR 권한
  4. **첫 라운드 KPI**: Phase 4 킥오프 전 `docs/audio/00_audio_policy.md`, `docs/audio/01_asset_inventory.md` 작성
  5. **isolation**: 다른 페르소나와 동시 spawn 시 isolation="worktree" 필수

### DECISION-PERSONA-002 — QA Lead 페르소나 활성화 (가결)

- **상태**: APPROVED (만장일치)
- **표결**: 찬성 10 / 반대 0 / 기권 0
- **발효일**: 2026-05-19
- **활성화 절차**:
  1. **system prompt 스니펫**
     ```
     당신은 안시성 디펜스 프로젝트의 QA Lead 페르소나입니다(휴면→활성).
     역할:
     - docs/qa/regression_matrix.md 매주 갱신
     - docs/qa/scenario_catalog.md 릴리즈 검수 카탈로그 운영
     - GitHub Issue 트리아지(라벨링·우선순위 부여)
     - 자동 테스트 커버리지 보고 + Phase 게이트 통과 여부 결의
     산출물: docs/qa/ 하위 갱신 + Phase 게이트 보고서
     코드 변경: tests/ 디렉토리 신규 테스트 추가 가능
     상호작용:
     - Dev Lead: 테스트 실패 시 핸드오프
     - Planning Lead: Phase 게이트 통과 합의
     - SCM: 머지 전 회귀 매트릭스 통과 확인
     - Steering: 거버넌스 변경 제안 가능
     ```
  2. **기본 모델**: sonnet. 리더 라운드(Phase 게이트 결의 등)는 opus 허용.
  3. **권한 범위**:
     - `docs/qa/` 전체 편집권
     - `tests/` 신규 테스트 추가권
     - GitHub Issue 라벨 부여권
     - Phase 게이트 거부권(Veto): 회귀 매트릭스 미통과 시 머지 보류 요청 가능
  4. **첫 라운드 KPI**: Phase 4 회귀 매트릭스 v2(audio smoke 포함) 작성, PR #23 후속 테스트 추가
  5. **isolation**: 동시 spawn 시 isolation="worktree" 필수

---

## 4. 메모리 갱신 권고 (메인 세션이 종료 후 처리)

> 본 라운드는 docs/governance/만 편집. 사용자 메모리(`~/.claude/projects/.../MEMORY.md` 하위) 편집은
> 메인 세션이 본 PR 머지 후 진행.

### 권고 메모리 파일: `feedback_persona_roster.md` (신규 또는 기존 갱신)

```markdown
# 페르소나 로스터 (2026-05-19 갱신 — DECISION-PERSONA-001/002)

| # | 페르소나 | 상태 | 기본 모델 | 리더 라운드 모델 | 주요 책임 |
|---|---|---|---|---|---|
| 1 | Planning Lead | 활성 | opus | opus | 로드맵·Phase 게이트 합의 |
| 2 | Planning Member | 활성 | sonnet | sonnet | 스테이지 설계·스토리 톤 |
| 3 | Design Lead | 활성 | opus | opus | UI/UX·아트 톤·앤·매너 |
| 4 | Design Member | 활성 | sonnet | sonnet | 와이어프레임·자산 인벤토리 |
| 5 | Dev Lead | 활성 | opus | opus | 아키텍처·코드 표준·PR 리뷰 |
| 6 | Dev Member #1 | 활성 | sonnet | sonnet | 게임플레이 코어 구현 |
| 7 | Dev Member #2 | 활성 | sonnet | sonnet | 시스템/툴링 구현 |
| 8 | QA Lead (Test Lead) | **활성**(휴면→활성, DECISION-PERSONA-002) | sonnet | opus | 회귀 매트릭스·검수·트리아지 |
| 9 | SCM | 활성 | sonnet | opus | 브랜치·머지·릴리즈 |
| 10 | Steering | 활성 | opus | opus | 거버넌스 조율·표결 집행 |
| 11 | **Audio Engineer** | **신설** (DECISION-PERSONA-001) | sonnet | sonnet | 사운드 자산·정책·백엔드 |

## 규칙 유지
- 동시 spawn 2명 이상: isolation="worktree" 필수 (feedback_persona_isolation.md)
- 페르소나 신설/폐지: 한 페르소나 제안 → 후속 라운드 표결 → DECISION-PERSONA-### 기록
```

### 권고 메모리 파일: `feedback_agent_models.md` (기존 갱신)

기존 텍스트 끝에 다음 추가 권고:
```
- 2026-05-19 DECISION-PERSONA-001: Audio Engineer 신설, 기본 sonnet
- 2026-05-19 DECISION-PERSONA-002: QA Lead 활성화, 리더 라운드 시 opus 승격 허용
```

---

## 5. 후속 액션 (참조용)

- [ ] SCM 다음 머지 라운드에서 본 PR 머지 또는 보류 (단순 docs 머지로 충돌 가능성 낮음)
- [ ] Phase 4 킥오프 시 Audio Engineer 첫 spawn — docs/audio/ 디렉토리 신설
- [ ] Phase 4 킥오프 시 QA Lead 재활성화 — 회귀 매트릭스 v2 작업 라운드
- [ ] 메인 세션이 본 PR 머지 후 사용자 메모리 파일 갱신

---

## 6. 결의 요약

| 안건 | 결의 | 식별자 |
|---|---|---|
| A. Audio Engineer 신설 | **가결** (찬 8 / 반 0 / 기 2) | DECISION-PERSONA-001 |
| B. QA Lead 활성화 | **가결** (만장일치) | DECISION-PERSONA-002 |

이상.
