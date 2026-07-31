import numpy as np
import pytest
from sc2_fast_sim.ecs.component import Component, component


def test_component_creates_dataclass_with_fields():
    @component
    class Position(Component):
        x: float
        y: float

    p = Position(x=1.0, y=2.0)
    assert p.x == 1.0
    assert p.y == 2.0


def test_component_dtype_float_fields():
    @component
    class Position(Component):
        x: float
        y: float

    assert Position._dtype.names == ("x", "y")
    assert Position._dtype["x"] == np.float64
    assert Position._dtype["y"] == np.float64


def test_component_dtype_mixed_types():
    @component
    class Health(Component):
        hp: float
        shields: float
        owner: int

    assert Health._dtype.names == ("hp", "shields", "owner")
    assert Health._dtype["hp"] == np.float64
    assert Health._dtype["shields"] == np.float64
    assert Health._dtype["owner"] == np.int64


def test_component_dtype_bool_field():
    @component
    class Alive(Component):
        alive: bool

    assert Alive._dtype["alive"] == np.bool_


def test_component_unsupported_type_raises():
    with pytest.raises(TypeError, match="unsupported type"):

        @component
        class Bad(Component):
            data: str
