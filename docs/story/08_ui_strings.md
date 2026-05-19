# 08. UI 텍스트 모음 (UI Strings)

> Phase 2 - 기획 파트 산출물 #9 (스토리)
> 의존: `00_story_bible.md`, GDD §8(UI 와이어프레임)
> 본 문서는 게임 내 메뉴·버튼·툴팁·메시지·유닛 설명·도움말 등 **모든 UI 텍스트**를 카테고리별로 정리한다.
> 한국어 표준어, 가족 친화 톤. 키(KEY)는 향후 i18n을 고려해 영문 식별자로 부여.

---

## 0. 페어 토의 메모

- **리더**: "UI 텍스트가 게임의 인상을 좌우한다. 짧고 단단하게. 영어식 번역체 금지."
- **팀원**: "동의. 모든 버튼은 4글자 이내, 모든 메시지는 한 줄. 툴팁은 두 문장 이내."
- **리더**: "실패·에러 메시지에 비난 톤 절대 금지. '곡식이 부족합니다' 같은 부드러운 정보 제공."

### DECISION 라벨

- **DECISION-U01**: 모든 버튼 텍스트는 한국어 자연체. "Save"는 "저장하기"가 아닌 "두기" 같은 자연어. (단, 일반 메뉴는 표준 한국어 게임 용어를 따른다 — "저장", "불러오기" 등.)
- **DECISION-U02**: 키(KEY)는 영문 snake_case. 본 문서가 i18n 리소스 파일의 1차 원천.
- **DECISION-U03**: 한자·전문용어는 항상 한글 + (한자) 병기. 툴팁은 평이한 풀이.

---

## 1. 타이틀 / 메인 메뉴

### 1.1 타이틀 화면

| KEY | 표시 텍스트 |
|---|---|
| `title.game_title` | 안시성: 88일의 약속 |
| `title.subtitle` | Ansi 88 |
| `title.press_to_start` | 화면을 누르면 시작합니다 |
| `title.version` | v0.1.0 |
| `title.copyright` | © 2026 안시성 645 기획팀 |

### 1.2 메인 메뉴 (버튼)

| KEY | 표시 텍스트 |
|---|---|
| `menu.new_game` | 새 게임 |
| `menu.continue` | 이어하기 |
| `menu.stage_select` | 스테이지 |
| `menu.barracks` | 병영 |
| `menu.codex` | 도감 |
| `menu.settings` | 설정 |
| `menu.credits` | 만든 사람들 |
| `menu.quit` | 종료 |

### 1.3 메뉴 부가 텍스트

| KEY | 표시 텍스트 |
|---|---|
| `menu.continue.no_save` | 저장된 진행이 없습니다. 새 게임을 시작하시오. |
| `menu.intro_replay` | 인트로 다시 보기 |
| `menu.quit.confirm` | 정말로 게임을 끝내시겠습니까? |

---

## 2. 스테이지 선택 화면

| KEY | 표시 텍스트 |
|---|---|
| `stage_select.title` | 스테이지 선택 |
| `stage_select.locked` | 잠금 — 이전 스테이지를 먼저 클리어하시오 |
| `stage_select.cleared` | 클리어 |
| `stage_select.best_stars` | 최고 별: {stars}/3 |
| `stage_select.play` | 도전하기 |
| `stage_select.back` | 돌아가기 |

### 2.1 스테이지 이름 (정식)

| KEY | 표시 텍스트 |
|---|---|
| `stage.01.name` | 1. 요동성의 첫눈 |
| `stage.01.subtitle` | 함락 직전의 한 시간 |
| `stage.02.name` | 2. 백암성의 항복 |
| `stage.02.subtitle` | 사람을 살리는 길 |
| `stage.03.name` | 3. 개모성의 횃불 |
| `stage.03.subtitle` | 어둠을 견딘 자 |
| `stage.04.name` | 4. 안시성 외곽 |
| `stage.04.subtitle` | 외성은 내어준다, 본성은 다르다 |
| `stage.05.name` | 5. 안시성 토산 |
| `stage.05.subtitle` | 88일의 약속 |

---

## 3. 인게임 HUD

### 3.1 자원 표시

| KEY | 표시 텍스트 |
|---|---|
| `hud.grain` | 곡식 |
| `hud.grain.tooltip` | 곡식(穀). 유닛을 모집하고 성벽을 복구하는 데 쓰입니다. |
| `hud.population` | 인구 |
| `hud.population.tooltip` | 동시에 둘 수 있는 병사의 수입니다. |
| `hud.arrows` | 화살 |
| `hud.arrows.tooltip` | 궁수가 공격할 때 한 발씩 소모됩니다. |
| `hud.fame` | 명성 |
| `hud.fame.tooltip` | 별로 얻은 명성. 병영에서 영구 강화에 쓰입니다. |

### 3.2 시간·웨이브

| KEY | 표시 텍스트 |
|---|---|
| `hud.wave_label` | 진군 |
| `hud.wave_progress` | 진군 {current}/{total} |
| `hud.timer` | 시각 |
| `hud.next_wave_in` | 다음 진군까지 {seconds}초 |
| `hud.preview` | 다음 진군 |
| `hud.day_counter` | {day}일째 |

### 3.3 게임 속도

| KEY | 표시 텍스트 |
|---|---|
| `hud.speed.1x` | 보통 속도 (1×) |
| `hud.speed.2x` | 빠르게 (2×) |
| `hud.speed.pause` | 일시정지 |
| `hud.speed.resume` | 다시 시작 |

### 3.4 양만춘 영웅 UI

| KEY | 표시 텍스트 |
|---|---|
| `hero.name` | 양만춘 |
| `hero.name_label` | 안시성주 양만춘 [전승] |
| `hero.hp` | HP {current}/{max} |
| `hero.skill1` | 일점사 |
| `hero.skill2` | 독려의 함성 |
| `hero.skill3` | 화살비 |
| `hero.ultimate` | 결사항전 |
| `hero.skill.ready` | 준비 완료 |
| `hero.skill.cooldown` | {seconds}초 |
| `hero.skill.locked` | 잠김 |
| `hero.respawn_in` | 잠시 후 다시 일어섭니다 ({seconds}초) |

---

## 4. 좌측 패널 — 유닛 / 건물 선택

### 4.1 아군 유닛 이름·코스트

| KEY | 표시 텍스트 |
|---|---|
| `unit.archer.name` | 고구려 궁수 |
| `unit.archer.cost` | 곡식 10 / 인구 1 |
| `unit.spearman.name` | 고구려 창병 |
| `unit.spearman.cost` | 곡식 8 / 인구 1 |
| `unit.long_spearman.name` | 고구려 장창병 |
| `unit.long_spearman.cost` | 곡식 15 / 인구 1 |
| `unit.catapult.name` | 고구려 투석수 |
| `unit.catapult.cost` | 곡식 25 / 인구 2 |
| `unit.cavalry.name` | 고구려 기병 |
| `unit.cavalry.cost` | 곡식 30 / 인구 2 |

### 4.2 아군 유닛 툴팁 (마우스오버 시)

| KEY | 표시 텍스트 |
|---|---|
| `unit.archer.tooltip` | 고구려 궁수\n원거리에서 화살을 쏩니다. 사거리는 길지만 근접에 약합니다. 명적(鳴鏑) — 소리내며 날아가는 화살을 씁니다. |
| `unit.spearman.tooltip` | 고구려 창병\n성벽 가까이 다가오는 적을 막아 시간을 끕니다. 가장 저렴한 전열입니다. |
| `unit.long_spearman.tooltip` | 고구려 장창병\n긴 창으로 중장보병과 기병에 강합니다. 일반 보병에는 평범합니다. |
| `unit.catapult.tooltip` | 고구려 투석수\n돌을 날려 광역으로 데미지를 입힙니다. 사거리가 매우 길고 재장전이 느립니다. |
| `unit.cavalry.tooltip` | 고구려 기병\n사기 게이지가 차오르면 좌·우 출격구에서 측면으로 돌격합니다. 충차의 옆구리에 강합니다. |

### 4.3 건물 / 보조

| KEY | 표시 텍스트 |
|---|---|
| `building.torch.name` | 횃불 |
| `building.torch.cost` | 곡식 5 |
| `building.torch.tooltip` | 횃불\n야간에 시야를 만듭니다. 빛이 닿지 않는 곳의 적은 보이지 않습니다. |
| `building.granary.name` | 곡식 생산소 |
| `building.granary.cost` | 곡식 20 |
| `building.granary.tooltip` | 곡식 생산소\n시간당 곡식 +0.5. 성벽 밖에 짓기 때문에 적의 표적이 됩니다. |

---

## 5. 적 유닛 설명 (도감/툴팁)

### 5.1 적 유닛 이름

| KEY | 표시 텍스트 |
|---|---|
| `enemy.infantry.name` | 당군 보병 |
| `enemy.archer.name` | 당군 궁수 |
| `enemy.heavy.name` | 당군 중장보병 |
| `enemy.scout.name` | 당군 척후 |
| `enemy.cavalry.name` | 당군 기병 |
| `enemy.ram.name` | 당군 충차 |
| `enemy.tower.name` | 당군 공성탑 |
| `enemy.elite.name` | 당군 친위대 |

### 5.2 적 유닛 툴팁

| KEY | 표시 텍스트 |
|---|---|
| `enemy.infantry.tooltip` | 당군 보병\n가장 흔한 적입니다. 다수가 한꺼번에 옵니다. 궁수에 약합니다. |
| `enemy.archer.tooltip` | 당군 궁수\n원거리에서 화살을 쏩니다. 거리를 좁히면 약해집니다. |
| `enemy.heavy.tooltip` | 당군 중장보병\n무거운 갑옷을 입었습니다. 일반 화살에 강하지만 장창에 약합니다. |
| `enemy.scout.tooltip` | 당군 척후\n빠르고 은신을 합니다. 야간에는 횃불 빛 안에서만 보입니다. |
| `enemy.cavalry.tooltip` | 당군 기병\n빠른 돌격으로 전열을 무너뜨립니다. 장창에 약합니다. |
| `enemy.ram.tooltip` | 당군 충차(衝車)\n성문을 들이받습니다. 매우 단단하지만 옆구리에 약점이 있습니다. |
| `enemy.tower.tooltip` | 당군 공성탑(雲梯)\n성벽 높이까지 다가와 안에 든 궁수를 토해냅니다. 멀리서 막아야 합니다. |
| `enemy.elite.tooltip` | 당군 친위대\n황제 직속 정예입니다. 강하고 단단합니다. 마지막에 옵니다. |

### 5.3 보스 유닛

| KEY | 표시 텍스트 |
|---|---|
| `boss.liu.name` | 당의 척후대장 |
| `boss.liu.subtitle` | 리우(劉) |
| `boss.jang.name` | 당의 야습 부대장 |
| `boss.jang.subtitle` | 장(張) |
| `boss.iseje_ram.name` | 이세적의 정예 충차 |
| `boss.iseje_ram.subtitle` | 대총관 이세적이 보냈다 |
| `boss.taejong.name` | 당 태종 이세민 |
| `boss.taejong.subtitle` | 당의 황제 |

---

## 6. 일시정지 메뉴

| KEY | 표시 텍스트 |
|---|---|
| `pause.title` | 일시정지 |
| `pause.resume` | 계속하기 |
| `pause.restart` | 다시 시작 |
| `pause.settings` | 설정 |
| `pause.stage_select` | 스테이지 선택 |
| `pause.to_title` | 타이틀로 |

---

## 7. 클리어 / 패배 메시지

### 7.1 스테이지 클리어 화면

| KEY | 표시 텍스트 |
|---|---|
| `result.win.title` | 진군을 격퇴했습니다 |
| `result.win.stars` | 별 평가 |
| `result.win.star_1` | 클리어 |
| `result.win.star_2` | 성문 체력 유지 |
| `result.win.star_3` | 특별 목표 달성 |
| `result.win.fame_gained` | 명성 +{count} |
| `result.win.reward_grain` | 곡식 +{count} |
| `result.win.history_note` | 역사 노트가 도감에 추가되었습니다 |
| `result.win.next_stage` | 다음 스테이지로 |
| `result.win.replay` | 다시 도전 |
| `result.win.to_select` | 스테이지 선택 |

### 7.2 스테이지 패배 화면

| KEY | 표시 텍스트 |
|---|---|
| `result.lose.title` | 다시 매봅시다 |
| `result.lose.message.s1` | "여기서 막지 못하면, 안시성도 위태로워집니다." — 모용손 |
| `result.lose.message.s2` | "백암의 백성도 안시까지는 데려가야 하오." — 양만춘 |
| `result.lose.message.s3` | "어둠은 어렵소. 그러나 한 번 빛을 본 자는 두 번도 본다오." — 양만춘 |
| `result.lose.message.s4` | "외성을 내준 것은 작전이었으나, 본성을 잃은 것은 다른 이야기요." — 양만춘 |
| `result.lose.message.s5` | "안시성은 실제로도 88일이라는 긴 시간을 버텼습니다. 한 번에 되는 일이 아닙니다." |
| `result.lose.retry` | 다시 도전 |
| `result.lose.to_select` | 스테이지 선택 |
| `result.lose.to_title` | 타이틀로 |

### 7.3 별 3개 달성 시 보너스 메시지

| KEY | 표시 텍스트 |
|---|---|
| `result.three_stars.s1` | "한 사람도 잃지 않았소. 안시성에서도 그리 되기를." |
| `result.three_stars.s2` | "두 성을 등에 진 셈이오." |
| `result.three_stars.s3` | "어둠 속에서 한 명도 잃지 않았소. 안시까지 마지막 길이오." |
| `result.three_stars.s4` | "기병이 측면을 갈랐소. 이세적도 오늘 밤은 잠 못 이루겠소." |
| `result.three_stars.s5` | "약속을 지켰소." |

---

## 8. 자원·배치 알림

### 8.1 자원 부족 메시지 (부드러운 톤)

| KEY | 표시 텍스트 |
|---|---|
| `alert.grain_short` | 곡식이 부족하오. |
| `alert.population_full` | 인구가 가득 찼소. 병사를 잃은 뒤 다시 시도하시오. |
| `alert.arrows_low` | 화살이 부족하오. 근접 운영을 검토하시오. |
| `alert.slot_occupied` | 이 자리에는 이미 누군가 서 있소. |
| `alert.invalid_placement` | 이곳에는 배치할 수 없소. |
| `alert.skill_cooldown` | 아직 준비가 안 됐소. {seconds}초 더. |
| `alert.skill_locked` | 이 스킬은 아직 잠겨 있소. |
| `alert.cavalry_not_ready` | 사기가 차야 출격할 수 있소. |

### 8.2 자원 회복·획득

| KEY | 표시 텍스트 |
|---|---|
| `gain.grain` | 곡식 +{count} |
| `gain.arrows` | 화살 +{count} |
| `gain.fame` | 명성 +{count} |
| `gain.wave_clear` | 진군 격퇴! 곡식 +{grain}, 화살 +{arrows} |

---

## 9. 병영 (메타 강화 트리)

| KEY | 표시 텍스트 |
|---|---|
| `barracks.title` | 병영 — 강화 |
| `barracks.fame_balance` | 보유 명성: {count} |
| `barracks.tier1.name` | 단단한 갑옷 |
| `barracks.tier1.desc` | 모든 아군의 체력이 10% 늘어납니다. |
| `barracks.tier1.cost` | 명성 3 |
| `barracks.tier2.name` | 잘 벼린 화살촉 |
| `barracks.tier2.desc` | 궁수와 양만춘의 공격력이 10% 늘어납니다. |
| `barracks.tier2.cost` | 명성 5 |
| `barracks.tier3.name` | 풍년 |
| `barracks.tier3.desc` | 시작 곡식 +30, 곡식 자동 생산 +0.2/초. |
| `barracks.tier3.cost` | 명성 8 |
| `barracks.tier4.name` | 군기 |
| `barracks.tier4.desc` | 인구 상한 +2. 병사 회복 속도가 2배 빨라집니다. |
| `barracks.tier4.cost` | 명성 12 |
| `barracks.tier5.name` | 안시의 정신 |
| `barracks.tier5.desc` | 양만춘 궁극기 쿨다운 -30초, 부활 쿨다운 -20초. |
| `barracks.tier5.cost` | 명성 18 |
| `barracks.unlock` | 해금하기 |
| `barracks.unlocked` | 해금됨 |
| `barracks.locked` | 잠김 |
| `barracks.requires_prev` | 이전 강화를 먼저 해금하시오. |
| `barracks.requires_fame` | 명성이 부족하오. |

---

## 10. 도감 (코덱스)

| KEY | 표시 텍스트 |
|---|---|
| `codex.title` | 도감 |
| `codex.tab.history` | 역사 노트 |
| `codex.tab.units` | 유닛 |
| `codex.tab.enemies` | 적 |
| `codex.tab.heroes` | 영웅 |
| `codex.locked` | 잠김 — 해당 스테이지를 클리어하시오 |
| `codex.label.fact` | (사실) |
| `codex.label.legend` | [전승] |
| `codex.label.fiction` | [픽션] |
| `codex.note.about_legend` | "[전승]은 정사에는 기록이 없으나 후대의 야사·전승으로 전해지는 내용입니다. 본 게임은 한국 대중에 친숙한 점을 고려해 라벨과 함께 사용합니다." |
| `codex.note.about_fiction` | "[픽션]은 본 게임이 이야기 전개를 위해 창작한 인물·장면입니다. 사료에는 등장하지 않습니다." |

---

## 11. 설정 메뉴

| KEY | 표시 텍스트 |
|---|---|
| `settings.title` | 설정 |
| `settings.audio` | 소리 |
| `settings.master_volume` | 전체 음량 |
| `settings.bgm_volume` | 배경음악 |
| `settings.sfx_volume` | 효과음 |
| `settings.display` | 화면 |
| `settings.fullscreen` | 전체 화면 |
| `settings.windowed` | 창 모드 |
| `settings.text_size` | 글씨 크기 |
| `settings.text_100` | 보통 |
| `settings.text_125` | 크게 |
| `settings.text_150` | 더 크게 |
| `settings.colorblind` | 색약 모드 |
| `settings.colorblind.on` | 켜짐 |
| `settings.colorblind.off` | 꺼짐 |
| `settings.subtitle` | 자막 |
| `settings.subtitle.on` | 항상 켜짐 |
| `settings.keybind` | 키 설정 |
| `settings.save` | 저장 |
| `settings.cancel` | 취소 |
| `settings.reset` | 기본값으로 |

---

## 12. 도움말 (?) — 첫 플레이 가이드

| KEY | 표시 텍스트 |
|---|---|
| `help.title` | 도움말 |
| `help.section.basic` | 기본 조작 |
| `help.basic.click` | 좌클릭으로 유닛을 고르고, 다시 좌클릭으로 빈 칸에 배치합니다. |
| `help.basic.right_click` | 우클릭으로 선택을 취소하거나, 배치된 유닛을 회수할 수 있습니다. |
| `help.basic.space` | 스페이스 키로 일시정지합니다. |
| `help.basic.speed` | F 키로 게임 속도를 보통/빠르게 전환합니다. |
| `help.section.resources` | 자원 |
| `help.resources.grain` | 곡식은 시간에 따라 자동으로 늘어납니다. 유닛 배치와 성벽 복구에 씁니다. |
| `help.resources.population` | 인구는 동시에 둘 수 있는 병사 수입니다. 병사를 잃으면 잠시 후 회복됩니다. |
| `help.resources.arrows` | 화살은 궁수가 공격할 때 줄어듭니다. 부족하면 근접 유닛을 활용합니다. |
| `help.section.hero` | 양만춘 |
| `help.hero.skills` | Q, W, E 키로 양만춘의 스킬을 발동합니다. R 키는 궁극기입니다. |
| `help.hero.control` | 스테이지 5에서는 M 키로 양만춘을 직접 움직일 수 있습니다. |
| `help.section.history` | 역사 |
| `help.history.codex` | 스테이지를 클리어할 때마다 역사 노트가 도감에 한 장씩 추가됩니다. |

---

## 13. 알림 / 토스트

| KEY | 표시 텍스트 |
|---|---|
| `toast.autosave` | 자동 저장되었습니다. |
| `toast.codex_unlocked` | 새 역사 노트가 도감에 추가되었습니다. |
| `toast.skill_unlocked` | 새 스킬이 해금되었습니다. |
| `toast.first_legend_label` | [전승]은 후대 전승으로 전해진 내용입니다. 정사에 직접 기록은 없습니다. |
| `toast.first_fiction_label` | [픽션]은 본 게임이 창작한 보조 인물·장면입니다. |
| `toast.about_intro_characters` | 이 게임의 등장인물 중 양만춘은 후대 전승에 따른 이름이며, 부장 모용손·향이 모자는 본 게임의 창작 인물입니다. 안시성 전투의 큰 줄기는 사료를 따랐습니다. |

---

## 14. 만든 사람들 (Credits)

| KEY | 표시 텍스트 |
|---|---|
| `credits.title` | 만든 사람들 |
| `credits.planning` | 기획 |
| `credits.design` | 디자인 |
| `credits.development` | 개발 |
| `credits.sources` | 역사 자문 |
| `credits.sources.list` | 삼국사기 / 자치통감 / 한국민족문화대백과사전 / 우리역사넷 |
| `credits.music` | 음악 |
| `credits.illustration` | 일러스트 |
| `credits.thanks` | 특별 감사 |
| `credits.thanks.text` | 88일을 버텼던 모든 이들에게 |
| `credits.back` | 돌아가기 |

---

## 15. 종료 / 다이얼로그

| KEY | 표시 텍스트 |
|---|---|
| `dialog.confirm` | 확인 |
| `dialog.cancel` | 취소 |
| `dialog.yes` | 예 |
| `dialog.no` | 아니오 |
| `dialog.ok` | 알겠소 |
| `dialog.close` | 닫기 |
| `dialog.quit.title` | 게임 종료 |
| `dialog.quit.message` | 정말로 안시성을 떠나시겠습니까? 저장하지 않은 진행은 사라집니다. |
| `dialog.restart.title` | 다시 시작 |
| `dialog.restart.message` | 이 스테이지를 처음부터 다시 시작하겠습니까? |

---

## 16. 페어 토의 — 최종 합의

- **리더**: "양만춘 본인의 1인칭/2인칭은 '~하시오/하오/하시오' 위주. 영웅 + 정중함의 균형. 패배 메시지에 짧은 인용 한 줄씩 넣어 톤 일관."
- **팀원**: "동의. 자원 부족 알림도 영웅 톤. '곡식이 부족하오.' 같이 양만춘이 직접 알려주는 느낌."
- **리더**: "[전승]·[픽션] 라벨 설명을 코덱스 진입 시 1회 안내. 교육 가치 명제."
- **공통**: "본 문서가 i18n 리소스의 1차 원천. 개발 인계 시 JSON/Python 딕셔너리로 변환 가능."

**서명**: 기획 리더 / 기획 팀원
**다음**: `09_codex.md`

— UI 스트링 v1.0 끝 —
