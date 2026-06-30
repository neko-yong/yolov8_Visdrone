# FILE_MANIFEST

| 文件路径 | 文件作用 | 是否必须 | 是否需要后续分析重点关注 |
| --- | --- | --- | --- |
| `models/yolov8s_gfpn_lite.yaml` | 当前 full SOD 主模型 YAML | 是 | 是 |
| `models/yolov8s_p2.yaml` | P2 detection head 消融模型 | 否 | 是 |
| `models/yolov8s_gfpn_only.yaml` | GFPN-lite 消融模型 | 否 | 是 |
| `configs/e03_b2_batch8_full_50ep_workers0.yaml` | batch8 full SOD workers0 配置 | 是 | 是 |
| `configs/e03_b2_batch8_full_50ep.yaml` | 旧 batch8 full 配置，旧输出异常 | 是 | 是 |
| `configs/e03_b2_no_piou_50ep_b5.yaml` | no-PIoU SOD 对照配置 | 是 | 是 |
| `configs/e03_full_sod_30ep_b5.yaml` | full SOD 30ep 已完成配置 | 是 | 是 |
| `configs/sod.yaml` | SOD 标准配置入口 | 是 | 是 |
| `configs/stage_a_e03.yaml` | E03 smoke test 配置 | 否 | 否 |
| `configs/visdrone.yaml` | 数据配置参考 | 否 | 否 |
| `train.py` | 统一训练入口，含 PIoU 开关和 Windows workers=0 逻辑 | 是 | 是 |
| `models/modules/__init__.py` | 自定义模块注册和 PIoU monkey patch 入口 | 是 | 是 |
| `models/modules/gfpn.py` | GFPNLite 模块化实现 | 是 | 是 |
| `models/modules/ema.py` | EMAAttention 实现 | 是 | 是 |
| `models/modules/block.py` | C2fEMA 实现 | 是 | 是 |
| `models/loss/__init__.py` | PIoU loss 导出 | 是 | 是 |
| `models/loss/piou.py` | PIoU 实现与 bbox_iou 替换函数 | 是 | 是 |
| `runs/baseline/yolov8s_visdrone_640/results.csv` | baseline 结果 CSV | 是 | 是 |
| `runs/sod/E03_full_sod_30ep_b5/results.csv` | full SOD + PIoU 30ep 结果 CSV | 是 | 是 |
| `runs/sod/E03_no_piou_50ep_b5/results.csv` | no-PIoU 50ep 结果 CSV | 是 | 是 |
| `runs/sod/E03_batch8_full_50ep_workers0/results.csv` | batch8 workers0 当前结果 CSV | 是，如存在 | 是 |
| `model_info.txt` | 模型复杂度与 Detect stride 信息 | 是 | 是 |
| `experiments_log.md` | 实验记录 | 是 | 是 |
| `PROJECT_STATE.md` | 当前项目状态 | 是 | 否 |
| `RUNS_POLICY.md` | runs 输出和 Windows 稳定性规则 | 是 | 否 |
| `SOD_BLUEPRINT.md` | SOD 设计与训练参考 | 是 | 是 |
| `PROJECT_HANDBOOK.md` | 项目维护协议 | 否 | 否 |
| `SOD_MODEL_AUDIT.md` | 本审计说明 | 是 | 是 |
| `FILE_MANIFEST.md` | 本文件清单 | 是 | 否 |
