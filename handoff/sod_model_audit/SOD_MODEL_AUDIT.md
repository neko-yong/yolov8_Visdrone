# SOD_MODEL_AUDIT

## 1. 当前 SOD 模型真实组成

- 当前 full SOD 模型文件：`models/yolov8s_gfpn_lite.yaml`。
- Neck：GFPN-lite。当前 YAML 中的 GFPN-lite 主要以内联 neck/head 层实现，`models/modules/gfpn.py` 中也保留了模块化 GFPNLite 实现供分析。
- Detect head：P2 / P3 / P4 / P5 四检测头。
- Attention：C2f-EMA。backbone 后半部分将部分 C2f 替换为 `C2fEMA`。
- Loss：full SOD 通过 `models/modules/__init__.py` 中的 `register_yolo_modules(enable_piou=True)` 替换 Ultralytics 的 `bbox_iou` 入口，实现 PIoU。
- no-PIoU 版本：配置 `configs/e03_b2_no_piou_50ep_b5.yaml` 中 `model.loss: default`，因此 `train.py` 不启用 PIoU monkey patch，使用 YOLOv8 默认 box loss。

说明：用户请求中的 `configs/e03_no_piou_50ep_b5.yaml` 在当前项目中不存在，实际对应文件是 `configs/e03_b2_no_piou_50ep_b5.yaml`。

## 2. 当前 SOD 与论文原版差异

- 完整复现部分：P2/P3/P4/P5 四尺度检测头、backbone 后半部分 C2f-EMA、PIoU 接入路径已经实现并可训练。
- 简化实现部分：GFPN 是 GFPN-lite，不是论文原版 1:1 结构；当前实现强调 top-down、bottom-up、Concat fusion、skip connection 和轻量 Conv fusion。
- 近似实现部分：EMA attention 是轻量 channel reweighting 实现，使用 global pooling + coarse scale pooling；可能不是论文原版 EMA 细节。
- PIoU 实现：包含 IoU 基础项、中心点偏移惩罚、角点约束、小目标权重增强；通过兼容 YOLOv8 `bbox_iou(..., CIoU=True)` 入口接入，不是直接重写完整 Ultralytics loss 类。
- 模块命名差异：项目中命名为 `GFPN-lite`、`C2fEMA`、`EMAAttention`、`PIoULoss`，与论文原始命名可能不完全一致。
- 未发现本地修改版 `ultralytics/nn/tasks.py`、`ultralytics/nn/modules/` 或 `ultralytics/utils/loss.py`；当前通过运行时注册和 monkey patch 实现兼容。

## 3. 模型结构摘要

Backbone 层：

| 层号 | 模块 | 输出/说明 |
| --- | --- | --- |
| 0 | Conv | P1/2 |
| 1 | Conv | P2/4 |
| 2 | C2f | backbone P2 skip |
| 3 | Conv | P3/8 |
| 4 | C2f | backbone P3 |
| 5 | Conv | P4/16 |
| 6 | C2fEMA | backbone P4，EMA 增强 |
| 7 | Conv | P5/32 |
| 8 | C2fEMA | backbone P5，EMA 增强 |
| 9 | SPPF | P5 |

Neck / Head 层：

| 层号 | 作用 |
| --- | --- |
| 10-14 | P5 到 P4 top-down 融合，输出 P4 top-down |
| 15-19 | P4 到 P3 top-down 融合，输出 P3 |
| 20-23 | P3 到 P4 bottom-up 融合，输出 P4 |
| 24-27 | P4 到 P5 bottom-up 融合，输出 P5 |
| 28-31 | 从 P3 上采样到 P2，并融合 backbone P2 skip，输出 P2 |
| 32 | Detect(P2, P3, P4, P5) |

检测分支：

| 分支 | 输出层 | stride | 通道 |
| --- | --- | --- | --- |
| P2 | 31 | 4 | 128 |
| P3 | 19 | 8 | 256 |
| P4 | 23 | 16 | 512 |
| P5 | 27 | 32 | 1024 |

Detect 输入索引：`[31, 19, 23, 27]`。

## 4. 复杂度信息

- Params：12,080,440
- Gradients：12,080,424
- GFLOPs：38.2
- Layers：152
- Detect stride：`[4, 8, 16, 32]`
- Detect nl：4
- Detect nc：10

已保存 `model.info` 审计文件：`model_info.txt`。

## 5. 权重迁移情况

- 当前配置 `train.model: models/yolov8s_gfpn_lite.yaml` 是从 YAML 构建模型，并不是直接在配置中写 `yolov8s.pt`。
- 当前审计没有启动训练，也没有加载权重迁移流程，因此本包内没有新的 `Transferred xxx/yyy items` 日志。
- 从结构上看，新增或改造层包括：C2fEMA、GFPN-lite neck/head、P2 branch、四尺度 Detect 输入、PIoU loss 接入。这些层相对标准 YOLOv8s 很可能无法完整匹配 pretrained 权重。
- 若后续要做权重迁移审计，应在训练日志中重点查看 `Transferred xxx/yyy items`、shape mismatch、Detect head 初始化提示。

## 6. 已有实验结果

| 实验 | 配置/输出 | epoch | batch | imgsz | P | R | mAP50 | mAP50-95 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E00 baseline | `runs/baseline/yolov8s_visdrone_640` | 50 | 8 | 640 | 0.52009 | 0.38806 | 0.38074 | 0.21899 | completed |
| E03 full SOD + PIoU | `runs/sod/E03_full_sod_30ep_b5` | 30 | 5 | 640 | 0.39933 | 0.30104 | 0.27090 | 0.14619 | completed |
| E03 no-PIoU | `runs/sod/E03_no_piou_50ep_b5` | 50 | 5 | 640 | 0.43283 | 0.34470 | 0.31504 | 0.17555 | completed |
| E03 batch8 full workers0 | `runs/sod/E03_batch8_full_50ep_workers0` | 6 | 8 | 640 | 0.26200 | 0.20774 | 0.14834 | 0.07378 | incomplete / only 6 rows observed |

补充：baseline 结果 CSV 中最佳 mAP50 出现在 epoch 47，mAP50=0.38144，mAP50-95=0.21925；表中展示最后一行 epoch 50 指标。

## 7. 轻量化候选位置

- Neck/Head 的 Conv 融合层：13、14、18、19、22、23、26、27、30、31。
- P2/P3/P4/P5 分支通道：当前分别为 128 / 256 / 512 / 1024，可作为 Lite-SOD-B/C 的主要压缩目标。
- Detect 前 Conv：尤其是 P4/P5 的 512/1024 通道层，参数量和 FLOPs 压力更高。
- C2fEMA：当前只在 backbone 6、8 层使用，可评估减少 EMA 或改轻量 attention。
- 当前未发现 GhostConv / GSConv 实现；若引入，需要新增模块并检查 YAML 注册。

不建议优先改动：

- Detect 输入顺序 `[31, 19, 23, 27]`。
- P2/P3/P4/P5 stride 对应关系。
- Concat 输入索引，除非逐层重算通道。
- `train.py` 的 workers/cache/device 稳定性逻辑。
- no-PIoU 对照配置，作为当前更稳的参考组。

## 8. 风险提醒

- 当前 PIoU 在已有实验中可能不如 no-PIoU 稳。
- batch8 在 8GB 显存上压力大，且训练速度可能受共享 GPU 内存影响。
- Windows 长训必须 `workers=0`。
- Lite-SOD-B 修改通道时必须逐层检查 Concat 和 Detect 输入通道。
- P2 分支对小目标有意义，但也明显增加高分辨率计算量。
- full SOD + PIoU 当前不能直接假设优于 baseline，需要继续以 no-PIoU 版本作为重要对照。
