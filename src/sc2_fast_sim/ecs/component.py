"""ECS Component 基类与 @component 装饰器。

设计依据：sc2-fast-sim-design.md §3.2。
每个 Component 类对应一个 numpy structured array dtype；
同 archetype 内同组件连续存储（SoA）。
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import get_type_hints

import numpy as np

_DTYPE_MAP = {
    bool: np.bool_,
    int: np.int64,
    float: np.float64,
}


@dataclass
class Component:
    """ECS 组件基类。子类用 @component 装饰器装饰。"""


def component(cls):
    """将普通类装饰为 ECS Component。

    - 先应用 @dataclass（使其拥有字段构造器）
    - 再根据字段类型注解生成 numpy dtype（存于 cls._dtype）
    - 标记 cls._component = True
    """
    cls = dataclass(cls)
    hints = get_type_hints(cls)
    np_fields = []
    for f in fields(cls):
        py_type = hints.get(f.name)
        np_type = _DTYPE_MAP.get(py_type)
        if np_type is None:
            raise TypeError(
                f"Component {cls.__name__} field {f.name}: unsupported type {py_type}"
            )
        np_fields.append((f.name, np_type))
    cls._dtype = np.dtype(np_fields)
    cls._component = True
    return cls
