"""회귀 매트릭스 Phase 4 — 자동 테스트 케이스.

매트릭스 docs/qa/regression_matrix.md v2 의 Phase 4 신규 ✓ 항목 커버.
DECISION-QA-P4-001~004: Audio(AU-01~06), Balance guard(BL-04~05) 자동화.

커버 항목:
  [AU] AU-01  SoundManager.play_bgm 예외 없음
  [AU] AU-02  SoundManager.play_sfx (sfx) 예외 없음
  [AU] AU-03  SoundManager.play_sfx (ui) 예외 없음
  [AU] AU-04  SoundManager.stop_all 예외 없음
  [AU] AU-05  SoundManager.set_master_volume 예외 없음 (미래 API, no-op 단계도 통과)
  [AU] AU-06  SoundManager.mute 예외 없음 (미래 API, no-op 단계도 통과)
  [BL] BL-04  stage_04 wave 수 무변경 (현재 7)
  [BL] BL-05  stage_05 wave 수 무변경 (현재 10)
  [BL] BL-04  stage_04 reward.grain 무변경 (현재 200)
  [BL] BL-05  stage_05 reward.grain 무변경 (현재 300)
  [BL] BL-04  stage_04 schema 검증 통과 (validate_stage)
  [BL] BL-05  stage_05 schema 검증 통과 (validate_stage)

튜토리얼(TU) 자동화는 Dev Lead(Issue #26) 머지 결과에 의존.
본 파일에서는 import guard 만 등록 — 머지 전 skip, 머지 후 ✓ 전환.
BL-01~03, BL-06~07 은 Dev Team1(Issue #27) 패치 후 추가 예정.

마커: @pytest.mark.regression_p4
"""

from __future__ import annotations

import json

import pytest

# ---------------------------------------------------------------------------
# pytest 마커 등록 (pyproject.toml / pytest.ini 에 추가 권장)
# ---------------------------------------------------------------------------
pytestmark = pytest.mark.regression_p4


# ===========================================================================
# [AU] 오디오 회귀 — SoundManager no-op 스텁 (AU-01~AU-06)
# DECISION-AUDIO-011, docs/audio/00_audio_policy.md §7
# ===========================================================================


def _make_sound_manager():  # type: ignore[return]
    """SoundManager 인스턴스 생성 헬퍼."""
    from src.core.sound import SoundManager

    return SoundManager()


class TestAudioRegressionP4:
    """AU-01~AU-06: SoundManager no-op 스텁 인터페이스 회귀."""

    def test_au01_play_bgm_no_exception(self) -> None:
        """AU-01: play_bgm 호출 시 예외 없음 (no-op 포함)."""
        sm = _make_sound_manager()
        sm.play_bgm("main_menu")
        sm.play_bgm("bgm_main_menu", loop=True)
        sm.play_bgm("bgm_stage_01_battle", loop=False)

    def test_au02_play_sfx_arrow_no_exception(self) -> None:
        """AU-02: play_sfx("sfx_arrow_shoot") 호출 시 예외 없음."""
        sm = _make_sound_manager()
        sm.play_sfx("sfx_arrow_shoot")

    def test_au03_play_sfx_ui_no_exception(self) -> None:
        """AU-03: play_sfx("ui_button_click") 호출 시 예외 없음."""
        sm = _make_sound_manager()
        sm.play_sfx("ui_button_click")
        sm.play_sfx("ui_menu_transition")

    def test_au04_stop_all_no_exception(self) -> None:
        """AU-04: stop_all() 호출 시 예외 없음."""
        sm = _make_sound_manager()
        sm.play_bgm("bgm_main_menu")
        sm.play_sfx("sfx_arrow_shoot")
        sm.stop_all()

    def test_au05_set_master_volume_no_exception(self) -> None:
        """AU-05: set_master_volume(0.5) 호출 시 예외 없음 (미래 API, no-op 단계도 통과).

        Phase 4 후반 백엔드 교체 전에도 인터페이스 존재를 보장.
        """
        sm = _make_sound_manager()
        sm.set_master_volume(0.5)
        sm.set_master_volume(0.0)
        sm.set_master_volume(1.0)

    def test_au06_mute_no_exception(self) -> None:
        """AU-06: mute() 호출 시 예외 없음 (미래 API, no-op 단계도 통과).

        Phase 4 후반 백엔드 교체 전에도 인터페이스 존재를 보장.
        """
        sm = _make_sound_manager()
        sm.mute()

    def test_au06_unmute_no_exception(self) -> None:
        """AU-06 보조: unmute() 호출 시 예외 없음 (mute 짝 메서드)."""
        sm = _make_sound_manager()
        sm.mute()
        sm.unmute()

    def test_au_sound_manager_multiple_calls_stable(self) -> None:
        """AU 통합: 반복 호출 시 상태 오염 없이 안정적으로 동작."""
        sm = _make_sound_manager()
        for _ in range(5):
            sm.play_bgm("bgm_stage_01_battle")
            sm.play_sfx("sfx_enemy_hit")
            sm.stop_all()
        sm.set_master_volume(0.8)
        sm.mute()
        sm.unmute()


# ===========================================================================
# [BL] 난이도 밸런스 가드 — stage_04~05 무변경 보장 (BL-04~05)
# DECISION-PL-P4-013, docs/13_difficulty_balance.md §7
# ===========================================================================


def _load_stage_raw(stage_id: str) -> dict:
    """src/core/settings.DATA_ROOT 경로에서 stage JSON 로드."""
    from src.core.settings import DATA_ROOT

    path = DATA_ROOT / "stages" / f"{stage_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


class TestBalanceGuardP4:
    """BL-04~BL-05: stage_04~05 무변경 가드 — DECISION-PL-P4-013.

    stage_01~03 난이도 하향(Issue #27) 패치가 stage_04~05 에 영향을 미치지 않았는지 확인.
    현재 데이터 기준값을 고정하여 Dev Team1 패치 후 회귀를 방지한다.
    """

    # ----- BL-04 stage_04 -----

    def test_bl04_stage04_wave_count_unchanged(self) -> None:
        """BL-04: stage_04 wave 수 무변경 — 현재 7개 (DECISION-PL-P4-013)."""
        raw = _load_stage_raw("stage_04")
        assert len(raw["waves"]) == 7, (
            f"stage_04 wave 수가 7이 아님: {len(raw['waves'])}. "
            "stage_04~05 는 난이도 하향 대상이 아닙니다 (DECISION-PL-P4-013)."
        )

    def test_bl04_stage04_reward_grain_unchanged(self) -> None:
        """BL-04: stage_04 reward.grain 무변경 — 현재 200 (DECISION-PL-P4-013)."""
        raw = _load_stage_raw("stage_04")
        reward = raw.get("reward", {})
        assert reward.get("grain") == 200, (
            f"stage_04 reward.grain 이 200이 아님: {reward.get('grain')}. "
            "stage_04~05 는 보상 상향 대상이 아닙니다 (DECISION-PL-P4-013)."
        )

    def test_bl04_stage04_schema_valid(self) -> None:
        """BL-04: stage_04 schema 검증 통과 — 패치 후에도 유효한 JSON 형태 유지."""
        from src.data.schema import validate_stage

        raw = _load_stage_raw("stage_04")
        validate_stage(raw, source="stage_04.json")  # 예외 없으면 통과

    # ----- BL-05 stage_05 -----

    def test_bl05_stage05_wave_count_unchanged(self) -> None:
        """BL-05: stage_05 wave 수 무변경 — 현재 10개 (DECISION-PL-P4-013)."""
        raw = _load_stage_raw("stage_05")
        assert len(raw["waves"]) == 10, (
            f"stage_05 wave 수가 10이 아님: {len(raw['waves'])}. "
            "stage_04~05 는 난이도 하향 대상이 아닙니다 (DECISION-PL-P4-013)."
        )

    def test_bl05_stage05_reward_grain_unchanged(self) -> None:
        """BL-05: stage_05 reward.grain 무변경 — 현재 300 (DECISION-PL-P4-013)."""
        raw = _load_stage_raw("stage_05")
        reward = raw.get("reward", {})
        assert reward.get("grain") == 300, (
            f"stage_05 reward.grain 이 300이 아님: {reward.get('grain')}. "
            "stage_04~05 는 보상 상향 대상이 아닙니다 (DECISION-PL-P4-013)."
        )

    def test_bl05_stage05_schema_valid(self) -> None:
        """BL-05: stage_05 schema 검증 통과 — 패치 후에도 유효한 JSON 형태 유지."""
        from src.data.schema import validate_stage

        raw = _load_stage_raw("stage_05")
        validate_stage(raw, source="stage_05.json")  # 예외 없으면 통과


# ===========================================================================
# [BL] 스키마 — night_vision_radius_multiplier import guard (BL-06 준비)
# DECISION-PL-P4-014: Dev Team1 머지 후 validate_stage 옵션 필드 허용
# ===========================================================================


class TestSchemaGuardNightVision:
    """BL-06 준비용: night_vision_radius_multiplier 필드 관련 스키마 guard.

    현재(Dev Team1 패치 전) 단계에서는:
    - validate_stage 가 알 수 없는 옵션 필드를 조용히 무시하는지 확인
      (혹은 필드 자체를 stage_03.json 에 넣어도 기존 검증이 깨지지 않는지 확인)

    Dev Team1 머지 후 stage_03.json 에 실제 필드가 추가되면
    이 테스트를 BL-06 정식 케이스로 교체한다.
    """

    def test_bl06_prep_schema_tolerates_extra_optional_field(self) -> None:
        """BL-06 준비: 스키마가 미등록 옵션 필드를 포함한 stage dict 를 거부하지 않는다.

        validate_stage 는 알 수 없는 키를 오류로 처리하지 않으므로,
        night_vision_radius_multiplier 필드가 stage_03.json 에 추가돼도
        기존 schema 로직이 깨지지 않아야 한다.
        """
        import copy
        import json as _json

        from src.core.settings import DATA_ROOT
        from src.data.schema import validate_stage

        raw = _json.loads((DATA_ROOT / "stages" / "stage_01.json").read_text(encoding="utf-8"))
        raw_copy = copy.deepcopy(raw)
        # 미래 옵션 필드 주입 — 현재 schema 에서 무시되어야 함
        raw_copy["night_vision_radius_multiplier"] = 1.4
        # 예외 없으면 통과 (schema 가 알 수 없는 필드를 거부하지 않음 확인)
        validate_stage(raw_copy, source="stage_01_with_nv_field.json")


# ===========================================================================
# [TU] 튜토리얼 import guard — Dev Lead(Issue #26) 머지 전 skip
# DECISION-QA-P4-004: Dev Lead 머지 후 ✓ 전환
# ===========================================================================


class TestTutorialImportGuard:
    """TU 시나리오 자동 테스트를 위한 import guard.

    tutorial_scene 모듈이 아직 없으면 skip, 있으면 기본 import 검증.
    Dev Lead(Issue #26) 머지 완료 후 본 클래스를 실제 TU-01~TU-09 케이스로 확장.
    """

    def test_tu_guard_tutorial_scene_importable(self) -> None:
        """TU import guard: tutorial_scene 모듈이 있으면 import 성공 확인.

        모듈이 없으면 skip (Dev Lead 머지 전 정상).
        """
        try:
            import importlib

            mod = importlib.import_module("src.scenes.tutorial_scene")
            assert mod is not None, "tutorial_scene 모듈 import 성공했으나 None 반환"
        except ModuleNotFoundError:
            pytest.skip("src.scenes.tutorial_scene 미존재 — Dev Lead(Issue #26) 머지 후 활성화")

    def test_tu_guard_save_slot_tutorial_fields(self) -> None:
        """TU import guard: save_slot 에 tutorial_dismissed/completed 필드가 있으면 검증.

        필드가 없으면 skip (Dev Lead 머지 전 정상).
        """
        try:
            import importlib

            mod = importlib.import_module("src.core.save_slot")
            # save_slot 모듈 내 SaveSlot 클래스 또는 관련 함수 확인
            assert mod is not None
            # tutorial_dismissed 필드 존재 여부 — 없으면 skip
            if not hasattr(mod, "SaveSlot"):
                pytest.skip("SaveSlot 클래스 미존재 — Dev Lead 머지 후 활성화")
            slot_cls = mod.SaveSlot
            # 인스턴스 생성 시도 (기본 생성자 가정)
            try:
                slot = slot_cls()
                has_dismissed = hasattr(slot, "tutorial_dismissed")
                has_completed = hasattr(slot, "tutorial_completed")
                if not (has_dismissed or has_completed):
                    pytest.skip("tutorial_dismissed/completed 필드 미존재 — Dev Lead 머지 후 활성화")
                if has_dismissed:
                    assert isinstance(slot.tutorial_dismissed, bool), "tutorial_dismissed 는 bool 이어야 함"
                if has_completed:
                    assert isinstance(slot.tutorial_completed, bool), "tutorial_completed 는 bool 이어야 함"
            except TypeError:
                pytest.skip("SaveSlot 기본 생성자 없음 — 스키마 확인 필요")
        except ModuleNotFoundError:
            pytest.skip("src.core.save_slot 미존재 — Dev Lead(Issue #26) 머지 후 활성화")
