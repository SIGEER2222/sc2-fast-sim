"""场景 JSON 加载器。

支持三种输入：文件路径（str/Path）、JSON 字符串、已解析 dict。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from .model import (
    ScenarioCommand,
    ScenarioDefinition,
    ScenarioPlayer,
    ScenarioUnitSpawn,
)


def load_scenario(path_or_text: Union[str, Path, dict]) -> ScenarioDefinition:
    """从文件路径、JSON 字符串或 dict 加载场景。"""
    if isinstance(path_or_text, dict):
        data = path_or_text
    else:
        p = Path(path_or_text)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
        else:
            # 尝试当作 JSON 文本解析（区分路径与文本：含 { 即文本）
            text = str(path_or_text)
            if text.strip().startswith("{"):
                data = json.loads(text)
            else:
                raise FileNotFoundError(f"场景文件不存在: {p}")

    schema = data.get("schema_version", "m0.v1")

    players = tuple(
        ScenarioPlayer(
            id=int(p["id"]),
            name=str(p["name"]),
            race=str(p["race"]),
            allies=tuple(int(a) for a in p.get("allies", [])),
            is_ai=bool(p.get("is_ai", True)),
        )
        for p in data.get("players", [])
    )

    spawns = tuple(
        ScenarioUnitSpawn(
            unit_type_id=str(s["unit_type_id"]),
            owner_player_id=int(s["owner_player_id"]),
            x=float(s["x"]),
            y=float(s["y"]),
            health_override=float(s["health_override"]) if "health_override" in s else None,
            shield_override=float(s["shield_override"]) if "shield_override" in s else None,
        )
        for s in data.get("spawns", [])
    )

    commands = tuple(
        ScenarioCommand(
            loop=int(c["loop"]),
            kind=str(c["kind"]),
            issuer_player_id=int(c["issuer_player_id"]),
            entity_ids=tuple(int(e) for e in c.get("entity_ids", [])),
            target_entity_id=int(c.get("target_entity_id", 0)),
            target_x=float(c.get("target_x", 0.0)),
            target_y=float(c.get("target_y", 0.0)),
            unit_type_id=str(c.get("unit_type_id", "")),
            ability_id=str(c.get("ability_id", "")),
        )
        for c in data.get("commands", [])
    )

    return ScenarioDefinition(
        schema_version=schema,
        name=str(data.get("name", "unnamed")),
        players=players,
        spawns=spawns,
        commands=commands,
        max_loops=int(data.get("max_loops", 10000)),
        seed=int(data.get("seed", 42)),
        strict=bool(data.get("strict", True)),
        win_condition=str(data.get("win_condition", "annihilation")),
    )