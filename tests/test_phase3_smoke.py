"""Phase 3 端到端验收：marine_vs_zergling 完整战斗闭环。"""

from pathlib import Path
import pytest
from sc2_fast_sim.catalog.units import CATALOG, MARINE, ZERGLING
from sc2_fast_sim.simulator import run_scenario
from sc2_fast_sim.scenario.loader import load_scenario

FIXTURE = Path(__file__).parent / "fixtures" / "marine_vs_zergling.json"


def test_marine_vs_zergling_completes_under_1000_loops():
    sc = load_scenario(FIXTURE)
    result = run_scenario(sc, CATALOG)
    assert result["loops_run"] <= 1000
    assert result["loops_run"] > 0


def test_marine_vs_zergling_has_winner():
    sc = load_scenario(FIXTURE)
    result = run_scenario(sc, CATALOG)
    # 应该有且仅有一个胜者（或全灭）
    alive = [e for e in result["entities"] if e["alive"]]
    assert len(alive) <= 1
    if len(alive) == 1:
        assert result["winner"] is not None


def test_marine_vs_zergling_damage_dealt():
    """跑完后，至少有一方 HP 下降。"""
    sc = load_scenario(FIXTURE)
    result = run_scenario(sc, CATALOG)
    marines = [e for e in result["entities"] if e["owner"] == 1]
    zerglings = [e for e in result["entities"] if e["owner"] == 2]
    # Marine 初始 hp 45, Zergling 35
    marine_hurt = any(e["hp"] < 45.0 for e in marines)
    zergling_hurt = any(e["hp"] < 35.0 for e in zerglings)
    assert marine_hurt or zergling_hurt


def test_marine_dps_approximately_correct():
    """Marine DPS ≈ 5.9/s，Zergling HP 35，应在 500 frame 内击杀。"""
    sc = load_scenario(FIXTURE)
    result = run_scenario(sc, CATALOG)
    # 不验证精确 frame 数，只验证在合理范围内完成
    assert result["loops_run"] < 500  # 应该远少于 1000


def test_run_multiple_scenarios_deterministic():
    """同样场景跑两次，结果应一致（确定性）。"""
    sc = load_scenario(FIXTURE)
    r1 = run_scenario(sc, CATALOG)
    r2 = run_scenario(sc, CATALOG)
    assert r1["loops_run"] == r2["loops_run"]
    assert r1["winner"] == r2["winner"]
