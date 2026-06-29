# FILE_MANIFEST

| 文件路径 | 文件作用 | 是否必须 | 是否需要队友修改路径 |
| --- | --- | --- | --- |
| `train.py` | 统一训练入口，读取 `configs/*.yaml` 并调用 YOLOv8 train API | 是 | 否 |
| `configs/visdrone.yaml` | VisDrone 数据集路径模板 | 是 | 是，必须改 `path` |
| `configs/e03_b2_no_piou_50ep_b5.yaml` | no-PIoU SOD 50 epoch 对照配置 | 是 | 通常否，依赖 `configs/visdrone.yaml` |
| `configs/e03_b2_batch8_full_50ep_workers0.yaml` | batch8 full SOD workers0 重跑配置 | 是 | 通常否，依赖 `configs/visdrone.yaml` |
| `configs/e03_b2_batch8_full_50ep.yaml` | 旧 batch8 full 配置参考，旧输出目录已异常中断 | 否 | 建议改 `name` 后再用 |
| `configs/e03_full_sod_30ep_b5.yaml` | full SOD 30 epoch 快速验证配置 | 否 | 通常否 |
| `configs/stage_a_e01.yaml` | P2 smoke test 配置 | 否 | 通常否 |
| `configs/stage_a_e02.yaml` | GFPN smoke test 配置 | 否 | 通常否 |
| `configs/stage_a_e03.yaml` | full SOD smoke test 配置 | 否 | 通常否 |
| `configs/sod.yaml` | full SOD 标准配置入口 | 否 | 通常否 |
| `configs/lite.yaml` | lite 版本配置占位 | 否 | 通常否 |
| `configs/ablation.yaml` | 消融配置入口参考 | 否 | 可能需要适配队友 baseline 配置 |
| `models/yolov8s_gfpn_lite.yaml` | full SOD 模型结构，GFPN-lite + P2 + C2f-EMA | 是 | 否 |
| `models/yolov8s_p2.yaml` | P2 detection head 消融模型 | 否 | 否 |
| `models/yolov8s_gfpn_only.yaml` | GFPN-lite 消融模型 | 否 | 否 |
| `models/modules/__init__.py` | 注册自定义模块与 PIoU monkey patch 入口 | 是 | 否 |
| `models/modules/gfpn.py` | GFPN-lite 模块实现 | 是 | 否 |
| `models/modules/ema.py` | EMA attention 实现 | 是 | 否 |
| `models/modules/block.py` | C2f-EMA 模块实现 | 是 | 否 |
| `models/loss/__init__.py` | PIoU loss 导出入口 | 是，full SOD 需要 | 否 |
| `models/loss/piou.py` | PIoU loss 与 YOLOv8 bbox_iou 替换实现 | 是，full SOD 需要 | 否 |
| `RUNS_POLICY.md` | runs 输出规范 | 是 | 否 |
| `PROJECT_STATE.md` | 当前项目状态摘要 | 否 | 否 |
| `experiments_log.md` | 已有实验记录与风险说明 | 否 | 否 |
| `PROJECT_HANDBOOK.md` | Codex/项目维护规则 | 否 | 否 |
| `SOD_BLUEPRINT.md` | SOD 实验设计与训练参考 | 否 | 否 |
| `requirements.txt` | 依赖参考 | 否 | 否，不建议直接覆盖环境 |
| `export_env.py` | 环境导出辅助脚本 | 否 | 否 |
| `SOD_HANDOFF.md` | 交接说明文档 | 是 | 否 |
| `FILE_MANIFEST.md` | 文件清单 | 是 | 否 |
