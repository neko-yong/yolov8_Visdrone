# 接手文档

本文档给新模型或新队友快速接手项目使用。先读本文件，再读 `PROJECT_STATE.md`、`EXPERIMENTS.md`、`PROJECT_LOG.md`。

## 1. 项目一句话

本项目在 VisDrone2019-DET 上复现 YOLOv8s baseline，并实现工程版 SOD-YOLO：GFPN-lite + P2/P3/P4/P5 Detect + C2f-EMA + 可选 PIoU。当前阶段已从 SOD 复现进入 Lite-SOD 轻量化验证，并完成 Lite-SOD-A / Lite-SOD-B / Lite-SOD-C-RA 的 build、model.info、1 epoch tiny smoke 和 5 epoch smoke。

## 2. 当前核心文件

| 路径 | 作用 |
| --- | --- |
| `train.py` | 统一训练入口，读取 `configs/*.yaml` 并调用 Ultralytics YOLO API。 |
| `configs/visdrone.yaml` | 数据集配置，必须指向本机 VisDrone_YOLO。 |
| `configs/e03_b2_no_piou_50ep_b5.yaml` | 当前最值得参考的 no-PIoU SOD 配置。 |
| `configs/lite_sod_a_uniform_no_piou.yaml` | Lite-SOD-A 5 epoch smoke 配置。 |
| `configs/lite_sod_b_ghost_no_piou.yaml` | Lite-SOD-B 5 epoch smoke 配置。 |
| `configs/lite_sod_c_ra_no_piou.yaml` | Lite-SOD-C-RA 5 epoch smoke 配置。 |
| `models/yolov8s_gfpn_lite.yaml` | 当前 full/no-PIoU SOD 主模型结构。 |
| `models/yolov8s_lite_sod_a_uniform.yaml` | Lite-SOD-A 统一通道压缩模型。 |
| `models/yolov8s_lite_sod_b_ghost.yaml` | Lite-SOD-B GhostConv 模型。 |
| `models/yolov8s_lite_sod_c_ra.yaml` | Lite-SOD-C-RA 分辨率感知通道分配模型。 |
| `models/modules/gfpn.py` | GFPNLite 模块化实现。 |
| `models/modules/ema.py` | EMAAttention。 |
| `models/modules/block.py` | C2fEMA。 |
| `models/modules/__init__.py` | 注册 C2fEMA，并按需启用 PIoU monkey patch。 |
| `models/loss/piou.py` | PIoU 实现。 |

当前没有修改 site-packages；GhostConv 来自 Ultralytics 8.4.66。

## 3. 数据与环境

- 数据集：VisDrone2019-DET 转 YOLO 格式。
- 默认数据目录：`datasets/VisDrone_YOLO/`。
- 换机器时只改 `configs/visdrone.yaml`，不要写个人绝对路径。
- 推荐环境：已经跑通 baseline 的 `mypytorch` 环境。
- Windows 长训必须 `workers=0`。

## 4. 当前 SOD 真实结构

- backbone：YOLOv8s 风格 backbone。
- attention：backbone 后半部分使用 `C2fEMA`。
- neck/head：GFPN-lite，主要在 `models/yolov8s_gfpn_lite.yaml` 中以内联层实现。
- Detect：四尺度 `[P2, P3, P4, P5]`。
- Detect 输入层：`[31, 19, 23, 27]`。
- stride：P2=4，P3=8，P4=16，P5=32。
- full SOD 分支通道：P2=128，P3=256，P4=512，P5=1024。
- loss：full SOD 可启用 PIoU；no-PIoU 通过 `model.loss: default` 关闭。

当前 SOD 不是论文原版 1:1，而是工程版近似复现。GFPN 是 GFPN-lite，EMA 和 PIoU 都是项目内实现。

## 5. 当前 Lite-SOD 状态

| 模型 | 文件 | 关键变化 | Params | GFLOPs | 5ep mAP50 | smoke 状态 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Lite-SOD-A | `models/yolov8s_lite_sod_a_uniform.yaml` | P2/P3/P4/P5 统一压缩到 96/192/384/768 | 9,334,136 | 29.2 | 0.09429 | 1ep/5ep completed |
| Lite-SOD-B | `models/yolov8s_lite_sod_b_ghost.yaml` | 基于 A，在层 14/19/20/23/24/27 使用 GhostConv | 8,104,376 | 26.8 | 0.08951 | 1ep/5ep completed |
| Lite-SOD-C-RA | `models/yolov8s_lite_sod_c_ra.yaml` | 基于 B，仅 P2 从 96 压缩到 80 | 8,011,608 | 25.3 | 0.09167 | 1ep/5ep completed |

三者均保持：
- backbone 不变。
- C2f-EMA 不变。
- Detect 仍为 P2/P3/P4/P5 四检测头。
- PIoU 未启用。
- 没有跑任何 Lite-SOD 50 epoch。

## 6. 推荐命令

Lite-SOD-C-RA dry-run：

```bash
python train.py --config configs/lite_sod_c_ra_no_piou.yaml --dry-run
```

Lite-SOD-C-RA 5 epoch smoke：

```bash
python train.py --config configs/lite_sod_c_ra_no_piou.yaml
```

Windows 推荐直接使用环境内 `python.exe` 前台运行，不建议用复杂后台封装。

## 7. 必守规则

- 不覆盖 baseline。
- 不复用旧异常目录 `runs/sod/E03_batch8_full_50ep`。
- 所有实验必须新建独立 `name`。
- Windows 长训必须 `workers=0`。
- batch8 长训必须 `workers=0`。
- 修改通道或模块前必须检查所有 Concat 和 Detect 输入通道。
- 不要随意改变 Detect 输入顺序和 stride 对应关系。
- 不要在未确认前启动 50 epoch 长训。
- Lite-SOD-C-RA 已完成 smoke；后续应统一选择模型进入正式训练矩阵。

## 8. 后续建议

1. A/B/C-RA smoke 都稳定，mAP50 未出现崩溃。
2. Lite-SOD-C-RA 最轻，且 5ep mAP50 略高于 B；Lite-SOD-A 5ep mAP50 最高。
3. 建议正式 50 epoch 优先跑 Lite-SOD-A 与 Lite-SOD-C-RA；Lite-SOD-B 作为 GhostConv 中间对照按资源决定是否加入。
4. 正式训练前为每个模型新建独立 50 epoch 配置和输出目录，不覆盖 smoke。

## 10. 当前异常与回退

- `E20_Lite-SOD-A_uniform_no_piou_50ep` 是 batch=8 的 Lite-SOD-A 正式训练尝试。
- 该实验只写到 epoch 2，随后 `results.csv` 和 `weights/last.pt` 长时间未更新，已标记为 `abnormal / stuck after epoch 2`。
- 该目录只作为异常记录保留，不作为正式结果，不要覆盖：`runs/sod/E20_Lite-SOD-A_uniform_no_piou_50ep`。
- 已准备 batch=4 回退配置：`configs/lite_sod_a_uniform_no_piou_50ep_b4.yaml`。
- 建议下一次在普通 VS Code 终端前台运行 batch=4 配置，便于观察日志和及时中断。

## 9. 文档地图

- `PROJECT_STATE.md`：当前阶段和下一步，一屏内。
- `EXPERIMENTS.md`：所有实验和结果。
- `PROJECT_LOG.md`：做过的增删改查和异常记录。
- `PROJECT_HANDOFF.md`：接手项目时先读。

## 11. Lite-SOD 正式训练当前进展

- Lite-SOD-A batch=8 正式训练尝试 `E20_Lite-SOD-A_uniform_no_piou_50ep` 已标记为 abnormal / stuck after epoch 2，只保留为异常记录。
- Lite-SOD-A batch=4 回退训练 `E20_Lite-SOD-A_uniform_no_piou_50ep_b4` 已完成 50/50 epoch，可作为 Lite-SOD-A 正式结果。
- Lite-SOD-A 50ep b4 结果：P=0.42853，R=0.34123，mAP50=0.30901，mAP50-95=0.17197，best epoch 按 mAP50-95 为 50。
- Lite-SOD-C-RA batch=4 正式训练 `E22_Lite-SOD-C-RA_no_piou_50ep_b4` 已完成 50/50 epoch，可作为 C-RA 正式结果。
- Lite-SOD-C-RA 50ep b4 结果：P=0.40966，R=0.32619，mAP50=0.29814，mAP50-95=0.16569，best epoch 为 49。
- Lite-SOD-B batch=4 正式训练 `E21_Lite-SOD-B_ghost_no_piou_50ep_b4` 已完成 50/50 epoch，可作为 GhostConv 中间消融对照。
- Lite-SOD-B 50ep b4 结果：P=0.42397，R=0.32841，mAP50=0.29867，mAP50-95=0.16580，best epoch 为 49。
- A/B/C 三组 Lite-SOD 50ep 已补齐；下一步建议统一做 per-class validation 和预测可视化。
- 当前主推轻量模型建议为 Lite-SOD-C-RA：它比 B 更轻，精度几乎持平。

## 12. 外部训练交付包

- 已创建最小可运行训练包：`D:\桌面\Lite-SOD-Train-Package`。
- 队友应首先阅读：`D:\桌面\Lite-SOD-Train-Package\DELIVERY_README.md`。
- 快速检查文档：`D:\桌面\Lite-SOD-Train-Package\QUICK_CHECK.md`。
- 文件清单：`D:\桌面\Lite-SOD-Train-Package\FILE_MANIFEST.md`。
- 包内不包含数据集、完整 runs、大权重、`.git`、`.venv` 或 `__pycache__`。
- 包内已通过 dry-run 和模型 build 最小验证，未启动训练。
