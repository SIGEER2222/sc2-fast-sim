"""移动系统：朝向转向 + 直线移动（numpy 向量化）。

算法参考：OpenHV FlyGuidedIntoTarget.cs 的转向逻辑（105-118 行）。
- 0°=北(+y)，90°=东(+x)，顺时针
- 每帧：先转向目标，朝向对准后直线移动
- 到达目标（距离 < speed）时清除 has_move_target
"""

from __future__ import annotations

import numpy as np

from sc2_fast_sim.components.combat import Movement
from sc2_fast_sim.components.core import Position
from sc2_fast_sim.ecs.world import World


def step_movement(world: World) -> None:
    """对所有有 Movement + Position 的单位执行一帧移动。"""
    for arch in world.query({Position, Movement}):
        pos = arch.get(Position)
        mv = arch.get(Movement)
        n = arch.size
        if n == 0:
            continue

        px = pos["x"][:n]
        py = pos["y"][:n]
        tx = mv["move_target_x"][:n]
        ty = mv["move_target_y"][:n]
        has_tgt = mv["has_move_target"][:n].astype(bool)
        facing = mv["facing"][:n].copy()
        turn_spd = mv["turn_speed"][:n]
        speed = mv["speed"][:n]

        # 计算到目标的方向角（0=北+y，顺时针）
        dx = tx - px
        dy = ty - py
        dist = np.sqrt(dx * dx + dy * dy)
        # atan2(dx, dy)：dx=东，dy=北 → 0=北，90=东
        target_facing = np.degrees(np.arctan2(dx, dy)) % 360.0

        # 转向：选最短弧
        diff = (target_facing - facing) % 360.0
        turn = np.where(diff <= 180.0, diff, diff - 360.0)
        turn_mag = np.minimum(np.abs(turn), turn_spd)
        turn_signed = np.sign(turn) * turn_mag
        new_facing = (facing + turn_signed) % 360.0

        # 只有朝向对准（角度差 < turn_speed 或无目标）才移动
        aligned = (np.abs(turn) < turn_spd + 0.001) | (~has_tgt)

        # 移动
        rad = np.radians(new_facing)
        move_dx = np.sin(rad) * speed  # 东分量
        move_dy = np.cos(rad) * speed  # 北分量

        # 只对有目标且朝向对准的移动
        do_move = has_tgt & aligned
        step = np.minimum(speed, dist)  # 不超过到目标距离
        move_dx = np.where(do_move, np.sin(rad) * step, 0.0)
        move_dy = np.where(do_move, np.cos(rad) * step, 0.0)

        new_px = px + move_dx
        new_py = py + move_dy

        # 到达判定
        new_dist = np.sqrt((tx - new_px) ** 2 + (ty - new_py) ** 2)
        reached = has_tgt & (new_dist < speed * 0.5 + 0.01)

        # 写回
        pos["x"][:n] = new_px
        pos["y"][:n] = new_py
        mv["facing"][:n] = np.where(has_tgt, new_facing, facing)
        mv["has_move_target"][:n] = np.where(reached, False, has_tgt)
