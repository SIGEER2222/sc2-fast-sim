"""Phase 2 端到端验收：加载 marine_vs_zergling.json → spawn → query 验证。"""

from pathlib import Path

from sc2_fast_sim.catalog.units import CATALOG
from sc2_fast_sim.components.core import Position, Health, Owner, Alive
from sc2_fast_sim.ecs.world import World
from sc2_fast_sim.scenario.loader import load_scenario
from sc2_fast_sim.scenario.spawner import spawn_entities

FIXTURE = Path(__file__).parent / "fixtures" / "marine_vs_zergling.json"


def test_load_marine_vs_zergling_and_spawn():
    """加载场景 → spawn → World 含 2 个实体。"""
    sc = load_scenario(FIXTURE)
    world = World()
    ids = spawn_entities(world, sc, CATALOG)

    assert len(ids) == 2
    assert world.next_entity_id == 3


def test_query_returns_single_archetype_with_2_entities():
    """query({Position, Health, Owner, Alive}) 返回 1 个 archetype，size == 2。"""
    sc = load_scenario(FIXTURE)
    world = World()
    spawn_entities(world, sc, CATALOG)

    matched = list(world.query({Position, Health, Owner, Alive}))
    assert len(matched) == 1
    assert matched[0].size == 2


def test_marine_and_zergling_data_correct():
    """验证 Marine（player 1, hp 45, pos 0,0）与 Zergling（player 2, hp 35, pos 10,0）。"""
    sc = load_scenario(FIXTURE)
    world = World()
    spawn_entities(world, sc, CATALOG)

    arch = list(world.query({Position, Health, Owner}))[0]
    pos = arch.get(Position)
    health = arch.get(Health)
    own = arch.get(Owner)
    entity_ids = arch.entity_ids[: arch.size]

    # 按 entity_id 排序确保顺序（Marine 先创建 id=1，Zergling id=2）
    order = sorted(range(arch.size), key=lambda i: entity_ids[i])
    # Marine (id=1)
    marine_idx = order[0]
    assert entity_ids[marine_idx] == 1
    assert pos[marine_idx]["x"] == 0.0
    assert pos[marine_idx]["y"] == 0.0
    assert health[marine_idx]["hp"] == 45.0
    assert own[marine_idx]["owner_id"] == 1
    # Zergling (id=2)
    zerg_idx = order[1]
    assert entity_ids[zerg_idx] == 2
    assert pos[zerg_idx]["x"] == 10.0
    assert pos[zerg_idx]["y"] == 0.0
    assert health[zerg_idx]["hp"] == 35.0
    assert own[zerg_idx]["owner_id"] == 2


def test_scenario_commands_loaded_but_not_executed():
    """commands 已加载到 ScenarioDefinition，但 Phase 2 不执行（无 systems）。"""
    sc = load_scenario(FIXTURE)
    assert len(sc.commands) == 2
    assert sc.commands[0].kind == "attack_unit"
    # Phase 2 不验证执行结果，只验证数据已加载


def test_empty_scenario_spawns_nothing():
    """空场景 spawn 0 实体，World 仍可用。"""
    sc = load_scenario({"name": "empty"})
    world = World()
    ids = spawn_entities(world, sc, CATALOG)
    assert ids == []
    assert world.next_entity_id == 1
    assert list(world.query({Position})) == []
