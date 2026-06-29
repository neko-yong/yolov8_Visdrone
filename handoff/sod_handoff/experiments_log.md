# Experiments Log

## E00 - YOLOv8s baseline 640

- 实验编号：E00
- 实验名：YOLOv8s baseline 640
- 路径：`runs/baseline/yolov8s_visdrone_640`
- 指标：P=0.52613, R=0.38791, mAP50=0.38128, mAP50-95=0.21975
- 结论：作为后续分辨率实验、数据增强实验、结构改进实验的对照基线。

## E01 - GFPN-lite + P2 detection head

- 实验编号：E01
- 实验名：E01_p2_gfpn_lite
- 改动：GFPN-lite + P2 detection head
- 模型配置：`models/yolov8s_gfpn_lite.yaml`
- 训练配置：`configs/sod.yaml`
- stride：4/8/16/32
- 当前实现：GFPN-lite + P2 detection head + C2f-EMA
- 状态：ready for training

## E03 - SOD-YOLO PIoU

- 实验编号：E03
- 实验名：E03_sod_yolo_piou
- 改动：GFPN-lite + P2 detection head + C2f-EMA + PIoU loss
- 模型配置：`models/yolov8s_gfpn_lite.yaml`
- 训练配置：`configs/sod.yaml`
- loss：PIoU
- 状态：ready for training

## E00_path_verify - baseline output path check

- 实验编号：E00_path_verify
- 实验名：E00_path_verify
- 类型：路径验证，不作为正式 baseline 结果
- 路径：`runs/baseline/E00_path_verify`
- 训练轮数：1
- 指标：P=0.34613, R=0.23571, mAP50=0.20159, mAP50-95=0.11258
- 结论：修复后的 `train.py` 可将输出写入项目内 `runs/baseline/<name>`，未产生项目内 `runs/detect/runs/...` fallback。

## E00_smoke_5ep - baseline smoke test

- 实验编号：E00_smoke_5ep
- 实验名：E00_smoke_5ep
- 类型：smoke test，不作为正式 baseline 结果
- 路径：`runs/baseline/E00_smoke_5ep`
- 训练轮数：5
- 参数：imgsz=640, batch=8
- 最终指标：P=0.41974, R=0.31958, mAP50=0.29030, mAP50-95=0.16386
- loss趋势：train box 1.68767 -> 1.45625，train cls 1.68091 -> 1.05662，train dfl 0.98809 -> 0.91226
- 验证趋势：val box 1.54971 -> 1.43229，val cls 1.22618 -> 1.04601，val dfl 0.94575 -> 0.90104
- 状态：completed
- 结论：E00 baseline smoke test 已完成，loss 正常下降，mAP 合理上升，未发现 NaN。

## Stage A - structure smoke test

- 阶段：Stage A 结构验证
- 任务：E00 / E01 / E02 / E03 各 5 epochs smoke test
- 数据集：VisDrone2019-DET
- imgsz：640
- 状态：completed

| 实验 | 结构 | 配置 | 输出目录 | batch | P | R | mAP50 | mAP50-95 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E00 | YOLOv8s baseline | `configs/stage_a_e00.yaml` | `runs/baseline/E00_stageA_smoke_5ep` | 8 | 0.42995 | 0.32478 | 0.29783 | 0.16941 | completed |
| E01 | +P2 detection head | `configs/stage_a_e01.yaml` | `runs/ablation/E01_p2_smoke_5ep_b4` | 4 | 0.28222 | 0.17705 | 0.11808 | 0.05946 | completed |
| E02 | +GFPN-lite | `configs/stage_a_e02.yaml` | `runs/ablation/E02_gfpn_smoke_5ep` | 8 | 0.22954 | 0.16922 | 0.11089 | 0.05399 | completed |
| E03 | GFPN + P2 + EMA + PIoU | `configs/stage_a_e03.yaml` | `runs/sod/E03_full_sod_smoke_5ep_b2` | 2 | 0.26267 | 0.15420 | 0.09754 | 0.04646 | completed |

- 说明：E01 batch=8 中断后按显存压力调整为 batch=4；E03 batch=4 中断后按显存压力调整为 batch=2。
- 产物：四个完成目录均包含 `results.csv`、`weights/last.pt`、`weights/best.pt`。

## E03_full_sod_30ep_b5 - full SOD quick verification

- 实验编号：E03
- 实验名：E03_full_sod_30ep_b5
- 类型：最终 SOD 模型快速验证训练
- 配置：`configs/e03_full_sod_30ep_b5.yaml`
- 模型：`models/yolov8s_gfpn_lite.yaml`
- 输出目录：`runs/sod/E03_full_sod_30ep_b5`
- 训练轮数：30
- 参数：imgsz=640, batch=5, optimizer=SGD, lr0=0.005, momentum=0.937, weight_decay=0.0005
- 结构：GFPN-lite + P2 detection head + C2f-EMA + PIoU
- 最终指标：P=0.39933, R=0.30104, mAP50=0.27090, mAP50-95=0.14619
- best epoch：30
- loss曲线摘要：train box 4.78000 -> 1.74771，train cls 4.07522 -> 1.37990，train dfl 2.65254 -> 1.12558
- 验证loss摘要：val box 3.52462 -> 1.70742，val cls 3.28149 -> 1.33101，val dfl 1.91329 -> 1.11579
- 权重：`runs/sod/E03_full_sod_30ep_b5/weights/best.pt`
- 状态：completed
- 说明：此前 `E03_full_sod_50ep` 被中断，本条为按用户要求改为 30 epoch / batch=5 后重新训练得到的完成结果。

## E03_no_piou_50ep_b5 - Stage B2 PIoU ablation

- 实验编号：E03_no_piou
- 实验名：E03_no_piou_50ep_b5
- 类型：Stage B2 消融对照
- 配置：`configs/e03_b2_no_piou_50ep_b5.yaml`
- 模型：`models/yolov8s_gfpn_lite.yaml`
- 输出目录：`runs/sod/E03_no_piou_50ep_b5`
- 训练轮数：50
- 参数：imgsz=640, batch=5, optimizer=SGD, lr0=0.005, momentum=0.937, weight_decay=0.0005
- 结构：GFPN-lite + P2 detection head + C2f-EMA，关闭 PIoU 注册，使用 YOLOv8 默认 box loss
- 最终指标：P=0.43283, R=0.34470, mAP50=0.31504, mAP50-95=0.17555
- loss曲线摘要：train box 3.94435 -> 1.51020，train cls 3.91462 -> 1.20589，train dfl 2.81709 -> 1.18714
- 验证loss摘要：val box 3.02707 -> 1.48625，val cls 3.12058 -> 1.20169，val dfl 2.19575 -> 1.17274
- 权重：`runs/sod/E03_no_piou_50ep_b5/weights/best.pt`
- 状态：completed
- 初步现象：与 `E03_full_sod_30ep_b5` 相比，关闭 PIoU 后 recall 与 mAP 均更高；后续需在同 epoch / 同 batch 下复核。

## E03_batch8_full_50ep - Stage B2 abnormal interruption

- 实验编号：E03_batch8_full
- 实验名：E03_batch8_full_50ep
- 类型：Stage B2 batch 对照异常记录
- 配置：`configs/e03_b2_batch8_full_50ep.yaml`
- 模型：`models/yolov8s_gfpn_lite.yaml`
- 输出目录：`runs/sod/E03_batch8_full_50ep`
- 目标训练轮数：50
- 实际记录轮数：22
- 参数：imgsz=640, batch=8, optimizer=SGD, lr0=0.005, momentum=0.937, weight_decay=0.0005
- 结构：GFPN-lite + P2 detection head + C2f-EMA + PIoU
- 中断前最后指标（epoch 22）：P=0.39208, R=0.30873, mAP50=0.26934, mAP50-95=0.14816
- 中断前最后loss：train box=1.83043，train cls=1.43611，train dfl=1.13493；val box=1.71078，val cls=1.33126，val dfl=1.11412
- 权重：`runs/sod/E03_batch8_full_50ep/weights/last.pt` 与 `best.pt` 已存在，但本实验未完成，不作为最终对照结果
- 状态：aborted
- 异常说明：训练在 Windows + YOLOv8 + 多进程 DataLoader 场景下异常卡死，已人为中断；初步判断为 Windows 多进程 DataLoader 经典死锁问题。
- 后续处理：`SOD_BLUEPRINT.md` 已补充参考训练配置 `workers=0`、`cache=True`、`device=0`；后续 batch8 重跑必须显式应用该配置，避免再次死锁。

## TRAIN_ENTRY_FIX - Windows DataLoader deadlock guard

- 类型：训练入口稳定性修复
- 修改文件：`train.py`、`configs/e03_b2_batch8_full_50ep.yaml`、`RUNS_POLICY.md`
- 改动内容：`train.py` 已支持 `workers`、`cache`、`device` 参数映射；默认 `workers=0`；入口处加入 `multiprocessing.freeze_support()` 与 Windows `spawn` 启动策略。
- batch8配置：`configs/e03_b2_batch8_full_50ep.yaml` 已显式设置 `workers: 0`、`cache: true`、`device: 0`。
- 目的：避免 Windows + YOLOv8 + 多进程 DataLoader 在 batch8/长训中出现卡死。
- 状态：dry-run verified

## SOD_HANDOFF - 最小可运行 SOD 交接包

- 类型：代码与配置交接
- 输出目录：`handoff/sod_handoff/`
- 压缩包：`handoff/sod_handoff.zip`
- 内容范围：SOD 训练入口、SOD/消融模型 YAML、自定义模块、PIoU、SOD 训练配置、运行规范和交接说明。
- 排除内容：`datasets/`、完整 `runs/`、旧异常目录 `runs/sod/E03_batch8_full_50ep`、训练权重、cache、`__pycache__/`、`.git/`、`.venv/`。
- 交接建议：队友优先使用已有 YOLOv8 baseline 环境，先跑 no-PIoU SOD，再跑 full SOD batch8 workers0。
