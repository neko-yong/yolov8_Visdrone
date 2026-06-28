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
