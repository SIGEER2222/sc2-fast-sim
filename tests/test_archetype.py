import numpy as np
import pytest
from sc2_fast_sim.ecs.component import Component, component
from sc2_fast_sim.ecs.archetype import Archetype


@component
class Position(Component):
    x: float
    y: float


@component
class Owner(Component):
    owner_id: int


def test_add_row_returns_index_and_stores_values():
    arch = Archetype(frozenset([Position, Owner]))
    idx = arch.add_row(
        entity_id=1,
        components={Position: Position(x=1.5, y=2.5), Owner: Owner(owner_id=10)},
    )
    assert idx == 0
    assert arch.size == 1
    pos = arch.get(Position)
    assert pos[0]["x"] == 1.5
    assert pos[0]["y"] == 2.5
    own = arch.get(Owner)
    assert own[0]["owner_id"] == 10


def test_add_row_multiple_entities_increments_size():
    arch = Archetype(frozenset([Position]))
    arch.add_row(1, {Position: Position(x=0.0, y=0.0)})
    arch.add_row(2, {Position: Position(x=10.0, y=5.0)})
    assert arch.size == 2
    pos = arch.get(Position)
    assert pos[0]["x"] == 0.0
    assert pos[1]["x"] == 10.0


def test_entity_ids_track_row_to_id():
    arch = Archetype(frozenset([Position]))
    arch.add_row(101, {Position: Position(x=0.0, y=0.0)})
    arch.add_row(202, {Position: Position(x=10.0, y=5.0)})
    assert list(arch.entity_ids[: arch.size]) == [101, 202]


def test_remove_row_uses_swap_remove():
    arch = Archetype(frozenset([Position]))
    arch.add_row(1, {Position: Position(x=0.0, y=0.0)})
    arch.add_row(2, {Position: Position(x=10.0, y=5.0)})
    arch.add_row(3, {Position: Position(x=20.0, y=10.0)})
    arch.remove_row(0)  # 删除第 0 行，末尾 swap 进来
    assert arch.size == 2
    pos = arch.get(Position)
    # 第 0 行现在是原最后一行（swap-remove）
    assert pos[0]["x"] == 20.0
    # 中间行不变
    assert pos[1]["x"] == 10.0
    # entity_ids 同步 swap
    assert arch.entity_ids[0] == 3


def test_remove_row_last_row_just_shrinks():
    arch = Archetype(frozenset([Position]))
    arch.add_row(1, {Position: Position(x=0.0, y=0.0)})
    arch.add_row(2, {Position: Position(x=10.0, y=5.0)})
    arch.remove_row(1)  # 删除末尾
    assert arch.size == 1
    pos = arch.get(Position)
    assert pos[0]["x"] == 0.0


def test_get_returns_live_view():
    arch = Archetype(frozenset([Position]))
    arch.add_row(1, {Position: Position(x=1.0, y=2.0)})
    view = arch.get(Position)
    view[0] = (99.0, 88.0)
    fresh = arch.get(Position)
    assert fresh[0]["x"] == 99.0
    assert fresh[0]["y"] == 88.0


def test_set_copies_external_array_into_storage():
    arch = Archetype(frozenset([Position]))
    arch.add_row(1, {Position: Position(x=0.0, y=0.0)})
    external = np.array([(5.0, 6.0)], dtype=Position._dtype)
    arch.set(Position, external)
    assert arch.get(Position)[0]["x"] == 5.0
    # 外部数组后续修改不影响存储（set 是拷贝）
    external[0] = (999.0, 999.0)
    assert arch.get(Position)[0]["x"] == 5.0


def test_grow_when_capacity_exceeded():
    arch = Archetype(frozenset([Position]), capacity=2)
    for i in range(5):
        arch.add_row(i, {Position: Position(x=float(i), y=0.0)})
    assert arch.size == 5
    assert arch.capacity >= 5
    pos = arch.get(Position)
    assert [pos[i]["x"] for i in range(5)] == [0.0, 1.0, 2.0, 3.0, 4.0]
