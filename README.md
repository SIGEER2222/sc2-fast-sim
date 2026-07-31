# sc2-fast-sim

高性能 SC2 模拟器（ECS archetype + numpy SoA）。

## 状态

- Phase 1：ECS 核心 + 不变量测试 ✅ 已完成（34 测试通过）
- Phase 2：catalog + scenario 加载（待规划）

设计文档：`../.omx/plans/sc2-fast-sim-design.md`
实施计划：`../.omx/plans/sc2-fast-sim-implementation-plan.md`

## 安装

```bash
pip install -e ".[test]"
```

## 测试

```bash
pytest -v
```
