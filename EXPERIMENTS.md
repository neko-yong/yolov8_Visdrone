# 实验记录文档

本文档只记录已经做过的实验、关键配置、结果和结论。所有训练、验证、消融、异常中断都必须追加到这里。

## 1. 固定基线

| 项目 | 内容 |
| --- | --- |
| 数据集 | VisDrone2019-DET，YOLO 格式 |
| 类别数 | 10 |
| baseline 模型 | YOLOv8s |
| baseline imgsz | 640 |
| baseline batch | 8 |
| baseline 输出 | `runs/baseline/yolov8s_visdrone_640` |

baseline 禁止覆盖。后续实验必须使用独立输出目录。

## 2. 环境与稳定性

- 主要环境：Windows 11，Conda `mypytorch`，Python 3.12.7，RTX 4060 Laptop 8GB。
- 关键依赖：PyTorch 2.3.1+cu118，Ultralytics 8.4.66。
- Windows 长训规则：`workers=0`，建议 `cache=True`，明确 `device=0`。
- 当前训练入口：统一使用 `train.py --config configs/*.yaml`。

## 3. 实验结果总表

| 实验 | 结构/目的 | epoch | batch | imgsz | P | R | mAP50 | mAP50-95 | 状态 | 输出 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| E00 | YOLOv8s baseline | 50 | 8 | 640 | 0.52613 | 0.38791 | 0.38128 | 0.21975 | completed | `runs/baseline/yolov8s_visdrone_640` |
| E00_path_verify | 输出路径验证，不作为正式 baseline | 1 | 8 | 640 | 0.34613 | 0.23571 | 0.20159 | 0.11258 | completed | `runs/baseline/E00_path_verify` |
| E00_smoke_5ep | baseline smoke test | 5 | 8 | 640 | 0.41974 | 0.31958 | 0.29030 | 0.16386 | completed | `runs/baseline/E00_smoke_5ep` |
| E00_stageA | Stage A baseline smoke | 5 | 8 | 640 | 0.42995 | 0.32478 | 0.29783 | 0.16941 | completed | `runs/baseline/E00_stageA_smoke_5ep` |
| E01 | P2 detection head smoke | 5 | 4 | 640 | 0.28222 | 0.17705 | 0.11808 | 0.05946 | completed | `runs/ablation/E01_p2_smoke_5ep_b4` |
| E02 | GFPN-lite smoke | 5 | 8 | 640 | 0.22954 | 0.16922 | 0.11089 | 0.05399 | completed | `runs/ablation/E02_gfpn_smoke_5ep` |
| E03 smoke | GFPN + P2 + EMA + PIoU | 5 | 2 | 640 | 0.26267 | 0.15420 | 0.09754 | 0.04646 | completed | `runs/sod/E03_full_sod_smoke_5ep_b2` |
| E03_full_sod_30ep_b5 | full SOD + PIoU 快速验证 | 30 | 5 | 640 | 0.39933 | 0.30104 | 0.27090 | 0.14619 | completed | `runs/sod/E03_full_sod_30ep_b5` |
| E03_no_piou_50ep_b5 | no-PIoU SOD 对照 | 50 | 5 | 640 | 0.43283 | 0.34470 | 0.31504 | 0.17555 | completed | `runs/sod/E03_no_piou_50ep_b5` |
| E03_batch8_full_50ep | full SOD + PIoU batch8，旧异常记录 | 22 | 8 | 640 | 0.39208 | 0.30873 | 0.26934 | 0.14816 | aborted | `runs/sod/E03_batch8_full_50ep` |
| E03_batch8_full_50ep_workers0 | full SOD + PIoU batch8 workers0 重跑 | 6 | 8 | 640 | 0.26200 | 0.20774 | 0.14834 | 0.07378 | incomplete | `runs/sod/E03_batch8_full_50ep_workers0` |
| E20_Lite-SOD-A_uniform_no_piou_smoke | Lite-SOD-A 1 epoch tiny smoke | 1 | 2 | 640 | 0.03344 | 0.07700 | 0.01529 | 0.00530 | completed | `runs/sod/E20_Lite-SOD-A_uniform_no_piou_smoke` |
| E20_Lite-SOD-A_uniform_no_piou_5ep | Lite-SOD-A 5 epoch smoke | 5 | 4 | 640 | 0.24985 | 0.15747 | 0.09429 | 0.04574 | completed | `runs/sod/E20_Lite-SOD-A_uniform_no_piou_5ep` |
| E21_Lite-SOD-B_ghost_no_piou_smoke | Lite-SOD-B 1 epoch tiny smoke | 1 | 2 | 640 | 0.03029 | 0.07641 | 0.01254 | 0.00421 | completed | `runs/sod/E21_Lite-SOD-B_ghost_no_piou_smoke` |
| E21_Lite-SOD-B_ghost_no_piou_5ep | Lite-SOD-B 5 epoch smoke | 5 | 4 | 640 | 0.24722 | 0.14823 | 0.08951 | 0.04308 | completed | `runs/sod/E21_Lite-SOD-B_ghost_no_piou_5ep` |
| E22_Lite-SOD-C-RA_no_piou_smoke | Lite-SOD-C-RA 1 epoch tiny smoke | 1 | 2 | 640 | 0.02209 | 0.06711 | 0.01041 | 0.00339 | completed | `runs/sod/E22_Lite-SOD-C-RA_no_piou_smoke` |
| E22_Lite-SOD-C-RA_no_piou_5ep | Lite-SOD-C-RA 5 epoch smoke | 5 | 4 | 640 | 0.23364 | 0.15058 | 0.09167 | 0.04386 | completed | `runs/sod/E22_Lite-SOD-C-RA_no_piou_5ep` |
| E20_Lite-SOD-A_uniform_no_piou_50ep_b4 | Lite-SOD-A 正式训练 | 50 | 4 | 640 | 0.42853 | 0.34123 | 0.30901 | 0.17197 | completed | `runs/sod/E20_Lite-SOD-A_uniform_no_piou_50ep_b4` |
| E21_Lite-SOD-B_ghost_no_piou_50ep_b4 | Lite-SOD-B 正式训练 | 50 | 4 | 640 | 0.42397 | 0.32841 | 0.29867 | 0.16580 | completed | `runs/sod/E21_Lite-SOD-B_ghost_no_piou_50ep_b4` |
| E22_Lite-SOD-C-RA_no_piou_50ep_b4 | Lite-SOD-C-RA 正式训练 | 50 | 4 | 640 | 0.40966 | 0.32619 | 0.29814 | 0.16569 | completed | `runs/sod/E22_Lite-SOD-C-RA_no_piou_50ep_b4` |

说明：`E03_batch8_full_50ep_workers0` 当前只观察到 6 行 epoch 记录，不能作为 50 epoch 完成结果解释。

## 4. 当前 SOD 模型审计

| 项目 | 内容 |
| --- | --- |
| full SOD 模型 | `models/yolov8s_gfpn_lite.yaml` |
| Neck | GFPN-lite，非论文原版 1:1 |
| Detect | P2 / P3 / P4 / P5 四检测头 |
| Attention | C2f-EMA，插入 backbone 后半部分 |
| Loss | PIoU，可通过 `model.loss: piou` 启用 |
| no-PIoU | `model.loss: default`，不启用 PIoU monkey patch |
| Params | 12,080,440 |
| GFLOPs | 38.2 |
| Detect stride | 4 / 8 / 16 / 32 |
| Detect 输入 | `[31, 19, 23, 27]` |
| 分支通道 | P2=128，P3=256，P4=512，P5=1024 |

当前 SOD 是工程复现版本：GFPN-lite、EMA attention、PIoU 均为近似/简化实现，不是论文原版逐层复刻。

## 5. 轻量化 Smoke 汇总

| Model | Params | GFLOPs | Channels | GhostConv | RA | PIoU | 5ep mAP50 | 5ep mAP50-95 | Status |
| ----- | -----: | -----: | -------- | --------- | -- | ---- | --------: | -----------: | ------ |
| Original SOD | 12,080,440 | 38.2 | 128/256/512/1024 | no | no | optional | 0.27090 | 0.14619 | 30ep PIoU completed |
| Lite-SOD-A | 9,334,136 | 29.2 | 96/192/384/768 | no | no | no | 0.09429 | 0.04574 | 5ep smoke completed |
| Lite-SOD-B | 8,104,376 | 26.8 | 96/192/384/768 | yes | no | no | 0.08951 | 0.04308 | 5ep smoke completed |
| Lite-SOD-C-RA | 8,011,608 | 25.3 | 80/192/384/768 | yes | yes | no | 0.09167 | 0.04386 | 5ep smoke completed |

## 6. Lite-SOD-A 记录

- 模型 YAML：`models/yolov8s_lite_sod_a_uniform.yaml`
- 配置：`configs/lite_sod_a_uniform_no_piou_smoke.yaml`、`configs/lite_sod_a_uniform_no_piou.yaml`
- 通道策略：P2/P3/P4/P5 从 128/256/512/1024 压缩到 96/192/384/768。
- Detect：仍为 P2/P3/P4/P5 四检测头。
- PIoU：未启用。
- GhostConv：未引入。
- model.info：`runs/tools/model_info/lite_sod_a_uniform_info.txt`

## 7. Lite-SOD-B 记录

- 模型 YAML：`models/yolov8s_lite_sod_b_ghost.yaml`
- 配置：`configs/lite_sod_b_ghost_no_piou_smoke.yaml`、`configs/lite_sod_b_ghost_no_piou.yaml`
- 基于 Lite-SOD-A，引入 GhostConv。
- 通道策略：P2/P3/P4/P5 仍为 96/192/384/768。
- GhostConv 替换层：`[14, 19, 20, 23, 24, 27]`
- Detect：仍为 P2/P3/P4/P5 四检测头，输入 `[31, 19, 23, 27]`。
- PIoU：未启用。
- model.info：`runs/tools/model_info/lite_sod_b_ghost_info.txt`

## 8. Lite-SOD-C-RA 记录

Lite-SOD-C-RA 基于 Lite-SOD-B，只做分辨率感知通道分配：P2 从 96 降到 80，P3/P4/P5 保持 192/384/768。

| 项目 | 内容 |
| --- | --- |
| 模型 YAML | `models/yolov8s_lite_sod_c_ra.yaml` |
| tiny 配置 | `configs/lite_sod_c_ra_no_piou_smoke.yaml` |
| 5ep 配置 | `configs/lite_sod_c_ra_no_piou.yaml` |
| 通道策略 | P2/P3/P4/P5 = 80/192/384/768 |
| Detect | 仍为 P2/P3/P4/P5 四检测头，输入 `[31, 19, 23, 27]` |
| GhostConv | 沿用 Lite-SOD-B，替换层 `[14, 19, 20, 23, 24, 27]` |
| PIoU | 未启用 |
| Params | 8,011,608 |
| GFLOPs | 25.3 |
| 相比 Lite-SOD-B | Params 降低 92,768，约 1.14%；GFLOPs 降低 1.5，约 5.60% |
| 相比 Lite-SOD-A | Params 降低 1,322,528，约 14.17%；GFLOPs 降低 3.9，约 13.36% |
| 相比原 SOD | Params 降低 4,068,832，约 33.68%；GFLOPs 降低 12.9，约 33.77% |
| model.info | `runs/tools/model_info/lite_sod_c_ra_info.txt` |

## 9. 关键结论

- Lite-SOD-A/B/C-RA 均已完成 build、model.info、1 epoch tiny smoke 和 5 epoch smoke。
- 三个 Lite 版本均保持 P2/P3/P4/P5 四检测头，均未启用 PIoU。
- Lite-SOD-C-RA 参数和 GFLOPs 最低，5ep mAP50=0.09167，高于 high-risk 阈值 0.06，未出现明显崩溃。
- 5ep smoke 不是正式精度结论；A/B/C 的 5ep mAP50 很接近。
- 后续建议进入 50 epoch 正式训练矩阵时，优先比较 Lite-SOD-A 与 Lite-SOD-C-RA；Lite-SOD-B 可作为 GhostConv 中间对照。

## 10. Lite-SOD 正式训练异常记录

| 实验 | 模型 | epoch | batch | imgsz | P | R | mAP50 | mAP50-95 | 状态 | 输出 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| E20_Lite-SOD-A_uniform_no_piou_50ep | Lite-SOD-A | 2/50 | 8 | 640 | 0.06032 | 0.13450 | 0.03990 | 0.01619 | abnormal / stuck after epoch 2 | `runs/sod/E20_Lite-SOD-A_uniform_no_piou_50ep` |

说明：
- `E20_Lite-SOD-A_uniform_no_piou_50ep` 的 `results.csv` 只到 epoch 2，`results.csv` 和 `weights/last.pt` 长时间未更新。
- 该目录保留为异常记录，不删除、不覆盖，不作为 Lite-SOD-A 正式 50 epoch 结果。
- 已创建 batch=4 回退配置：`configs/lite_sod_a_uniform_no_piou_50ep_b4.yaml`。
- 新正式输出名为 `E20_Lite-SOD-A_uniform_no_piou_50ep_b4`，后续应使用独立目录 `runs/sod/E20_Lite-SOD-A_uniform_no_piou_50ep_b4`。

## 11. Lite-SOD 正式训练结果

| Model | Params | GFLOPs | GhostConv | RA | Batch | Epochs | P | R | mAP50 | mAP50-95 | Best Epoch | Status |
| ----- | -----: | -----: | --------- | -- | ----: | -----: | -: | -: | ----: | -------: | ---------: | ------ |
| YOLOv8s baseline | - | - | no | no | 8 | 50 | 0.52613 | 0.38791 | 0.38128 | 0.21975 | - | completed |
| SOD no-PIoU | 12,080,440 | 38.2 | no | no | 5 | 50 | 0.43283 | 0.34470 | 0.31504 | 0.17555 | - | completed |
| Lite-SOD-A | 9,334,136 | 29.2 | no | no | 4 | 50 | 0.42853 | 0.34123 | 0.30901 | 0.17197 | 50 | completed |
| Lite-SOD-B | 8,104,376 | 26.8 | yes | no | 4 | 50 | 0.42397 | 0.32841 | 0.29867 | 0.16580 | 49 | completed |
| Lite-SOD-C-RA | 8,011,608 | 25.3 | yes | yes | 4 | 50 | 0.40966 | 0.32619 | 0.29814 | 0.16569 | 49 | completed |

### E20_Lite-SOD-A_uniform_no_piou_50ep_b4

- 模型：`models/yolov8s_lite_sod_a_uniform.yaml`。
- 配置：`configs/lite_sod_a_uniform_no_piou_50ep_b4.yaml`。
- 输出：`runs/sod/E20_Lite-SOD-A_uniform_no_piou_50ep_b4`。
- 训练完成度：50/50 epoch。
- batch/imgsz/workers/cache/device：4 / 640 / 0 / true / 0。
- PIoU：未启用，使用默认 YOLOv8 loss。
- 最终 epoch 指标：P=0.42853，R=0.34123，mAP50=0.30901，mAP50-95=0.17197。
- best epoch：按 mAP50-95 为 epoch 50；按 mAP50 峰值为 epoch 46，mAP50=0.30931。
- 总训练时间：`results.csv` 记录约 13095.6 秒，约 3.64 小时。
- 单 epoch 平均时间：约 261.9 秒。
- 关键文件：`results.csv`、`results.png`、`BoxPR_curve.png`、`confusion_matrix.png`、`weights/best.pt`、`weights/last.pt` 均已生成。
- 可视化：存在 `val_batch0_pred.jpg`、`val_batch1_pred.jpg`、`val_batch2_pred.jpg`。
- 异常：本次结果完整写满 50 epoch，未从结果文件观察到 OOM、NaN 或 DataLoader 卡死；未补跑 per-class validation，`results.csv` 仅含整体指标。
- 结论：该目录可作为 Lite-SOD-A 正式 50 epoch batch=4 结果；旧 batch=8 目录 `runs/sod/E20_Lite-SOD-A_uniform_no_piou_50ep` 仍仅作为 abnormal 记录保留。

### E22_Lite-SOD-C-RA_no_piou_50ep_b4

- 状态：训练完成，50/50 epoch。
- 模型：`models/yolov8s_lite_sod_c_ra.yaml`。
- 配置：`configs/lite_sod_c_ra_no_piou_50ep_b4.yaml`。
- 输出：`runs/sod/E22_Lite-SOD-C-RA_no_piou_50ep_b4`。
- 训练参数：epochs=50，batch=4，imgsz=640，workers=0，cache=true，device=0。
- 结构检查：build 成功，Params=8,011,608，GFLOPs=25.3，Detect=4 分支，stride=4/8/16/32。
- 结构约束：P2/P3/P4/P5 通道仍为 80/192/384/768；GhostConv 层仍为 `[14, 19, 20, 23, 24, 27]`；PIoU 未启用。
- 最终 epoch 指标：P=0.40966，R=0.32619，mAP50=0.29814，mAP50-95=0.16569。
- best epoch：按 mAP50 和 mAP50-95 均为 epoch 49，mAP50=0.29945，mAP50-95=0.16604。
- 总训练时间：`results.csv` 记录约 14146.3 秒，约 3.93 小时。
- 单 epoch 平均时间：约 282.9 秒。
- 关键文件：`results.csv`、`results.png`、`BoxPR_curve.png`、`confusion_matrix.png`、`weights/best.pt`、`weights/last.pt` 均已生成。
- 可视化：存在 `val_batch0_pred.jpg`、`val_batch1_pred.jpg`、`val_batch2_pred.jpg`。
- 异常：本次结果完整写满 50 epoch，未从结果文件观察到 OOM、NaN 或 DataLoader 卡死；`PR_curve.png` 未生成，但 `BoxPR_curve.png` 已生成；未补跑 per-class validation。
- 对比 Lite-SOD-A：Params 降低 1,322,528，GFLOPs 降低 3.9；mAP50 低 0.01087，mAP50-95 低 0.00628。
- 结论：该目录可作为 Lite-SOD-C-RA 正式 50 epoch batch=4 结果；C-RA 以轻量化换取少量精度下降。

### E21_Lite-SOD-B_ghost_no_piou_50ep_b4

- 状态：训练完成，50/50 epoch。
- 模型：`models/yolov8s_lite_sod_b_ghost.yaml`。
- 配置：`configs/lite_sod_b_ghost_no_piou_50ep_b4.yaml`。
- 输出：`runs/sod/E21_Lite-SOD-B_ghost_no_piou_50ep_b4`。
- 训练参数：epochs=50，batch=4，imgsz=640，workers=0，cache=true，device=0。
- 结构检查：build 成功，Params=8,104,376，GFLOPs=26.8，Detect=4 分支，stride=4/8/16/32。
- 结构约束：P2/P3/P4/P5 通道仍为 96/192/384/768；GhostConv 层仍为 `[14, 19, 20, 23, 24, 27]`；PIoU 未启用。
- 最终 epoch 指标：P=0.42397，R=0.32841，mAP50=0.29867，mAP50-95=0.16580。
- best epoch：按 mAP50 和 mAP50-95 均为 epoch 49，mAP50=0.29945，mAP50-95=0.16682。
- 总训练时间：`results.csv` 记录约 12968.4 秒，约 3.60 小时。
- 单 epoch 平均时间：约 259.4 秒。
- 关键文件：`results.csv`、`results.png`、`BoxPR_curve.png`、`confusion_matrix.png`、`weights/best.pt`、`weights/last.pt` 均已生成。
- 可视化：存在 `val_batch0_pred.jpg`、`val_batch1_pred.jpg`、`val_batch2_pred.jpg`。
- 异常：本次结果完整写满 50 epoch，未从结果文件观察到 OOM、NaN 或 DataLoader 卡死；`PR_curve.png` 未生成，但 `BoxPR_curve.png` 已生成；未补跑 per-class validation。
- 对比 Lite-SOD-A：Params 降低 1,229,760，GFLOPs 降低 2.4；mAP50 低 0.01034，mAP50-95 低 0.00617。
- 对比 Lite-SOD-C-RA：Params 高 92,768，GFLOPs 高 1.5；mAP50 高 0.00053，mAP50-95 高 0.00011。
- 结论：Lite-SOD-B 作为 GhostConv 中间对照已补齐；其精度与 C-RA 几乎相同，但复杂度高于 C-RA。

## 12. Lite-SOD A/B/C 正式训练结论

| Model | Params | GFLOPs | Channels | GhostConv | RA | P | R | mAP50 | mAP50-95 | Best Epoch | Status |
| --- | ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Lite-SOD-A | 9,334,136 | 29.2 | 96/192/384/768 | no | no | 0.42853 | 0.34123 | 0.30901 | 0.17197 | 50 | completed |
| Lite-SOD-B | 8,104,376 | 26.8 | 96/192/384/768 | yes | no | 0.42397 | 0.32841 | 0.29867 | 0.16580 | 49 | completed |
| Lite-SOD-C-RA | 8,011,608 | 25.3 | 80/192/384/768 | yes | yes | 0.40966 | 0.32619 | 0.29814 | 0.16569 | 49 | completed |

- Lite-SOD-A 精度最高，但复杂度也最高。
- Lite-SOD-B 引入 GhostConv 后，Params 比 A 降低约 13.18%，GFLOPs 降低约 8.22%，mAP50 下降 0.01034。
- Lite-SOD-C-RA 在 B 基础上进一步压缩 P2，Params 比 B 再降低 92,768，GFLOPs 再降低 1.5，mAP 与 B 基本持平。
- 当前主推轻量模型建议：Lite-SOD-C-RA。它是三者中最轻的，mAP50-95 与 B 仅差 0.00011。
