from pathlib import Path

import pytest
from sc2_fast_sim.scenario.loader import load_scenario
from sc2_fast_sim.scenario.model import ScenarioDefinition, ScenarioPlayer, ScenarioUnitSpawn, ScenarioCommand

FIXTURE = Path(__file__).parent / "fixtures" / "marine_vs_zergling.json"


def test_load_scenario_from_file_path():
    sc = load_scenario(FIXTURE)
    assert isinstance(sc, ScenarioDefinition)
    assert sc.name == "Marine vs Zergling"
    assert sc.schema_version == "m0.v1"


def test_load_scenario_from_text():
    text = FIXTURE.read_text(encoding="utf-8")
    sc = load_scenario(text)
    assert sc.name == "Marine vs Zergling"


def test_load_scenario_from_dict():
    data = {
        "schema_version": "m0.v1",
        "name": "test",
        "players": [{"id": 1, "name": "P1", "race": "terran"}],
        "spawns": [{"unit_type_id": "Marine", "owner_player_id": 1, "x": 0.0, "y": 0.0}],
        "commands": [],
        "max_loops": 500,
        "seed": 7,
        "strict": False,
        "win_condition": "annihilation",
    }
    sc = load_scenario(data)
    assert sc.name == "test"
    assert sc.max_loops == 500
    assert sc.seed == 7
    assert sc.strict is False


def test_load_scenario_players():
    sc = load_scenario(FIXTURE)
    assert len(sc.players) == 2
    p1 = sc.players[0]
    assert isinstance(p1, ScenarioPlayer)
    assert p1.id == 1
    assert p1.name == "Terran"
    assert p1.race == "terran"
    assert p1.is_ai is True
    p2 = sc.players[1]
    assert p2.race == "zerg"


def test_load_scenario_spawns():
    sc = load_scenario(FIXTURE)
    assert len(sc.spawns) == 2
    s0 = sc.spawns[0]
    assert isinstance(s0, ScenarioUnitSpawn)
    assert s0.unit_type_id == "Marine"
    assert s0.owner_player_id == 1
    assert s0.x == 0.0
    assert s0.y == 0.0
    s1 = sc.spawns[1]
    assert s1.unit_type_id == "Zergling"
    assert s1.x == 10.0


def test_load_scenario_commands():
    sc = load_scenario(FIXTURE)
    assert len(sc.commands) == 2
    c0 = sc.commands[0]
    assert isinstance(c0, ScenarioCommand)
    assert c0.loop == 0
    assert c0.kind == "attack_unit"
    assert c0.issuer_player_id == 1
    assert c0.entity_ids == (1,)
    assert c0.target_entity_id == 2


def test_load_scenario_defaults():
    sc = load_scenario({"name": "empty"})
    assert sc.schema_version == "m0.v1"
    assert sc.players == ()
    assert sc.spawns == ()
    assert sc.commands == ()
    assert sc.max_loops == 10000
    assert sc.seed == 42
    assert sc.strict is True
    assert sc.win_condition == "annihilation"


def test_load_scenario_nonexistent_file_raises():
    with pytest.raises(FileNotFoundError):
        load_scenario(Path("nonexistent_scenario.json"))


def test_scenario_definition_is_frozen():
    sc = load_scenario(FIXTURE)
    with pytest.raises(Exception):
        sc.name = "modified"