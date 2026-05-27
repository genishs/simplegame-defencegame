"""BL-07 클리어율 자동화 시뮬레이션 테스트.

Issue #39 (Phase 4 cleanup): 신규 플레이어가 자동 모드만으로
stage_01~03 첫 시도 클리어 가능 여부 자동 검증.

DECISION-DT1-P4B-001 ~ 005 참조:
  - 방안 A 채택: Mock BattleScene auto-mode 시뮬레이션 (tkinter-free).
  - 5 시드 x 3 스테이지 = 15회 반복.
  - 스테이지별 임계값: 5/5 (100%).
  - 통합 임계값: 14/15 (93.3%) 이상 -> 95%+ 목표 달성.
  - 전체 실행 시간: < 5 초 (테스트 러너 기준).

회귀 매트릭스:
  [BL] BL-07  stage_01 auto-mode 클리어율 5/5  X -> O
  [BL] BL-07  stage_02 auto-mode 클리어율 5/5  X -> O
  [BL] BL-07  stage_03 auto-mode 클리어율 5/5  X -> O

마커: @pytest.mark.slow  (1초 이상 소요)
"""

from __future__ import annotations

import time

import pytest

from src.systems.auto_mode_simulator import SimResult, StageSimulator

pytestmark = pytest.mark.regression_p4

# ---------------------------------------------------------------------------
# 상수
# ---------------------------------------------------------------------------
SEEDS = [0, 1, 2, 3, 4]  # 스테이지당 5개 시드
STAGES = ["stage_01", "stage_02", "stage_03"]
PER_STAGE_THRESHOLD = len(SEEDS)  # 5/5: 스테이지별 클리어 목표
COMBINED_THRESHOLD = 14  # 14/15: 통합 클리어 목표 (93.3%)
MAX_WALL_TIME_S = 5.0  # 15회 합산 허용 실시간 (초)


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _run_stage(stage_id: str, seeds: list[int]) -> list[SimResult]:
    """주어진 seeds 로 stage_id 를 반복 시뮬레이션하고 결과 목록 반환."""
    return [StageSimulator(stage_id, rng_seed=s).run() for s in seeds]


# ---------------------------------------------------------------------------
# BL-07 -- 스테이지별 클리어율
# ---------------------------------------------------------------------------


@pytest.mark.slow
class TestBL07ClearRate:
    """BL-07: stage_01~03 auto-mode 클리어율 5/5 (100%).

    DECISION-DT1-P4B-001: 방안 A 채택 (Mock auto-mode 시뮬레이션).
    DECISION-DT1-P4B-005: 직접 DPS 데미지 모델 사용.
    """

    def test_bl07_stage01_clear_rate(self) -> None:
        """BL-07 stage_01: 5/5 클리어 (seeds 0~4)."""
        results = _run_stage("stage_01", SEEDS)
        clears = sum(1 for r in results if r.cleared)
        failures = [r for r in results if not r.cleared]
        assert clears >= PER_STAGE_THRESHOLD, (
            f"stage_01 클리어율 {clears}/{len(SEEDS)} < {PER_STAGE_THRESHOLD}/{len(SEEDS)}\n"
            f"실패한 시드: {[r.seed for r in failures]}\n"
            f"(BL-07 회귀 매트릭스 임계값 위반, Issue #39)"
        )

    def test_bl07_stage02_clear_rate(self) -> None:
        """BL-07 stage_02: 5/5 클리어 (seeds 0~4)."""
        results = _run_stage("stage_02", SEEDS)
        clears = sum(1 for r in results if r.cleared)
        failures = [r for r in results if not r.cleared]
        assert clears >= PER_STAGE_THRESHOLD, (
            f"stage_02 클리어율 {clears}/{len(SEEDS)} < {PER_STAGE_THRESHOLD}/{len(SEEDS)}\n"
            f"실패한 시드: {[r.seed for r in failures]}\n"
            f"(BL-07 회귀 매트릭스 임계값 위반, Issue #39)"
        )

    def test_bl07_stage03_clear_rate(self) -> None:
        """BL-07 stage_03: 5/5 클리어 (seeds 0~4)."""
        results = _run_stage("stage_03", SEEDS)
        clears = sum(1 for r in results if r.cleared)
        failures = [r for r in results if not r.cleared]
        assert clears >= PER_STAGE_THRESHOLD, (
            f"stage_03 클리어율 {clears}/{len(SEEDS)} < {PER_STAGE_THRESHOLD}/{len(SEEDS)}\n"
            f"실패한 시드: {[r.seed for r in failures]}\n"
            f"(BL-07 회귀 매트릭스 임계값 위반, Issue #39)"
        )

    def test_bl07_combined_clear_rate_95_pct(self) -> None:
        """BL-07 통합: 15회 합산 클리어율 >= 93.3% (14/15 이상, 목표 95%+)."""
        total_clears = 0
        total_runs = 0
        for stage_id in STAGES:
            results = _run_stage(stage_id, SEEDS)
            total_clears += sum(1 for r in results if r.cleared)
            total_runs += len(results)

        rate = total_clears / total_runs
        assert total_clears >= COMBINED_THRESHOLD, (
            f"15회 합산 클리어율 {total_clears}/{total_runs} ({rate*100:.1f}%) < 93.3%\n"
            "(BL-07 회귀 매트릭스 임계값 위반, Issue #39)"
        )


# ---------------------------------------------------------------------------
# BL-07 -- 시뮬레이션 실행 시간 < 5 초
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_bl07_simulation_wall_time_under_5s() -> None:
    """BL-07 성능: 15회 시뮬레이션 합산 실시간 < 5 초.

    CI 환경에서의 속도 회귀를 방지.
    """
    t_start = time.monotonic()
    for stage_id in STAGES:
        for seed in SEEDS:
            StageSimulator(stage_id, rng_seed=seed).run()
    elapsed_wall = time.monotonic() - t_start

    assert elapsed_wall < MAX_WALL_TIME_S, (
        f"15회 시뮬레이션 실시간 {elapsed_wall:.2f}s >= {MAX_WALL_TIME_S}s 초과\n"
        f"(BL-07 성능 임계값 위반, Issue #39)"
    )


# ---------------------------------------------------------------------------
# BL-07 -- 시뮬레이터 무결성 가드
# ---------------------------------------------------------------------------


class TestBL07SimulatorIntegrity:
    """BL-07 시뮬레이터 무결성: SimResult 구조, 불변식, tkinter-free 확인."""

    def test_simresult_structure_stage01(self) -> None:
        """SimResult 가 올바른 필드를 포함한다."""
        result = StageSimulator("stage_01", rng_seed=42).run()
        assert isinstance(result.stage_id, str)
        assert isinstance(result.seed, int)
        assert isinstance(result.cleared, bool)
        assert isinstance(result.lives_remaining, int)
        assert isinstance(result.elapsed_sim_seconds, float)
        assert isinstance(result.enemies_defeated, int)

    def test_cleared_implies_lives_positive(self) -> None:
        """클리어 결과이면 lives_remaining >= 0 이다."""
        for stage_id in STAGES:
            result = StageSimulator(stage_id, rng_seed=0).run()
            if result.cleared:
                assert (
                    result.lives_remaining >= 0
                ), f"{stage_id}: cleared=True 이지만 lives_remaining={result.lives_remaining}"

    def test_sim_elapsed_positive(self) -> None:
        """시뮬레이션 경과 시간이 양수이다."""
        result = StageSimulator("stage_01", rng_seed=0).run()
        assert result.elapsed_sim_seconds > 0

    def test_cleared_run_defeats_enemies(self) -> None:
        """Issue #76 가드: 클리어 결과이면 적을 1체 이상 격파했다.

        명중 보장(호밍)으로 적이 실제 사망하는지 시뮬레이터 레벨에서 검증.
        시뮬레이터는 직접 DPS 모델이라 빗나감이 없으므로 클리어 = 적 격파 동반.
        """
        for stage_id in STAGES:
            result = StageSimulator(stage_id, rng_seed=0).run()
            if result.cleared:
                assert result.enemies_defeated > 0, (
                    f"{stage_id}: cleared=True 이지만 enemies_defeated=0 "
                    "(적이 죽지 않았는데 클리어 — 명중/격파 로직 회귀)"
                )

    def test_lives_decrement_on_castle_breach(self) -> None:
        """Issue #75 가드: 적이 castle 에 도달하면 lives 가 차감된다.

        유닛이 전혀 배치되지 않으면(전투력 0) 적이 막힘 없이 castle 에 도달하므로
        lives 가 크게 줄어든다. 유닛을 정상 배치한 기준 시뮬과 비교해, 무방어
        시뮬의 lives_remaining 이 더 낮음을 검증 — castle-reach → lives 차감
        경로(Issue #62/#75)가 살아 있음을 보장한다.
        """
        baseline = StageSimulator("stage_01", rng_seed=0).run()

        sim = StageSimulator("stage_01", rng_seed=0)
        # 유닛 배치를 비활성화 (전투력 0) — 적이 막힘 없이 castle 통과.
        sim._auto_place_units = lambda stage, allies: allies  # type: ignore[method-assign]
        undefended = sim.run()

        # 무방어 시뮬은 다수의 적이 castle 에 도달 → lives 가 대폭 차감.
        assert undefended.lives_remaining < baseline.lives_remaining, (
            "무방어 시뮬 lives_remaining "
            f"({undefended.lives_remaining}) 이 방어 시뮬 ({baseline.lives_remaining}) "
            "보다 낮지 않음 — castle 차감 경로 회귀"
        )
        # stage_01 lives=20 기준, 무방어 시 최소 절반 이상 손실 기대.
        assert undefended.lives_remaining <= 10, (
            f"무방어인데 lives_remaining={undefended.lives_remaining} (>10) — "
            "castle 차감이 충분히 일어나지 않음"
        )

    def test_no_tkinter_in_simulator_module(self) -> None:
        """auto_mode_simulator 모듈이 tkinter 를 런타임 import 하지 않는다 (DECISION-4.1)."""
        import ast
        from pathlib import Path

        sim_path = Path(__file__).parent.parent / "src" / "systems" / "auto_mode_simulator.py"
        source = sim_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        # TYPE_CHECKING 블록 라인 번호 수집
        tc_linenos: set[int] = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.If)
                and isinstance(node.test, ast.Name)
                and node.test.id == "TYPE_CHECKING"
            ):
                for child in ast.walk(node):
                    ln = getattr(child, "lineno", 0)
                    if ln:
                        tc_linenos.add(ln)
        # 런타임 tkinter import 검사
        violations = []
        for node in ast.walk(tree):
            is_tk = False
            if isinstance(node, ast.Import):
                is_tk = any(a.name == "tkinter" or a.name.startswith("tkinter.") for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                is_tk = node.module is not None and (
                    node.module == "tkinter" or node.module.startswith("tkinter.")
                )
            if is_tk:
                ln = getattr(node, "lineno", 0)
                if ln not in tc_linenos:
                    violations.append(ln)
        assert violations == [], f"auto_mode_simulator.py 에 런타임 tkinter import 감지: lines={violations}"
