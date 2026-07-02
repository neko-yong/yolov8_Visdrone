# 日志文档

本文档记录项目做过的增删改查、目录整理、配置同步、异常和交接动作。实验指标写入 `EXPERIMENTS.md`，当前阶段写入 `PROJECT_STATE.md`。

## 1. 维护规则

- 每次任务开始前读取 `PROJECT_HANDOFF.md`、`PROJECT_STATE.md`、`EXPERIMENTS.md`、`PROJECT_LOG.md`。
- 每次任务完成后更新 `PROJECT_STATE.md`。
- 涉及实验、训练、验证、消融或异常结果时更新 `EXPERIMENTS.md`。
- 涉及文件增删改查、目录整理、配置迁移、交接包、文档重构时更新本文档。

## 2. 已完成的主要变更

| 阶段 | 类型 | 内容 |
| --- | --- | --- |
| 初始化 | 文档 | 建立项目维护文档、状态文档、SOD 复现蓝图和实验记录。 |
| 数据阶段 | 新增 | 建立 VisDrone 到 YOLO 格式转换脚本和数据检查脚本。 |
| Baseline | 训练 | 完成 YOLOv8s baseline 训练并记录结果。 |
| runs 整理 | 目录 | 统一 `runs/baseline`、`runs/sod`、`runs/lite`、`runs/ablation`、`runs/tools`、`runs/predict` 分类。 |
| 配置系统 | 新增 | 建立 baseline、SOD、lite、ablation 相关 YAML 配置。 |
| 训练入口 | 新增 | 创建 `train.py`，支持读取 YAML、映射 YOLO train 参数、强制输出到 `runs/<type>/<name>`。 |
| 输出路径修复 | 修改 | 修复 Ultralytics 输出到 `runs/detect/runs/...` 的嵌套问题。 |
| GFPN-lite | 新增 | 添加 `models/modules/gfpn.py`，并建立 GFPN/P2 相关模型 YAML。 |
| P2 head | 修改 | 在模型 YAML 中实现 P2/P3/P4/P5 四尺度 Detect。 |
| C2f-EMA | 新增 | 添加 `models/modules/ema.py`、`models/modules/block.py`，注册 `C2fEMA`。 |
| PIoU | 新增 | 添加 `models/loss/piou.py`，通过运行时注册方式接入 PIoU。 |
| Stage A | 训练 | 完成 E00/E01/E02/E03 5 epoch smoke test。 |
| Stage B2 | 训练 | 完成 E03 no-PIoU 50 epoch 对照；batch8 full 旧训练异常中断。 |
| Windows 稳定性 | 修改 | `train.py` 支持 `workers/cache/device`，Windows 默认 `workers=0`，加入 `spawn` 和 `freeze_support()`。 |
| 文档重构 | 整理 | 合并所有 Markdown，最终只保留 4 个维护文档；删除 `handoff/`。 |
| Lite-SOD-A | 新增/训练 | 创建统一通道压缩模型与配置，完成 build、model.info、1 epoch 和 5 epoch smoke。 |
| Lite-SOD-B | 新增/训练 | 基于 A 引入 GhostConv，完成 build、model.info、1 epoch 和 5 epoch smoke。 |

## 3. Lite-SOD-C-RA 本次变更

| 类型 | 路径 | 内容 |
| --- | --- | --- |
| 新增 | `models/yolov8s_lite_sod_c_ra.yaml` | Lite-SOD-C-RA 模型，基于 Lite-SOD-B，仅将 P2 通道从 96 调整到 80。 |
| 新增 | `configs/lite_sod_c_ra_no_piou_smoke.yaml` | Lite-SOD-C-RA 1 epoch tiny smoke 配置，batch=2，workers=0，cache=true。 |
| 新增 | `configs/lite_sod_c_ra_no_piou.yaml` | Lite-SOD-C-RA 5 epoch smoke 配置，batch=4，workers=0，cache=true。 |
| 新增 | `runs/tools/model_info/lite_sod_c_ra_info.txt` | Lite-SOD-C-RA Params、GFLOPs、Detect、通道和 GhostConv 审计。 |
| 更新 | `EXPERIMENTS.md` | 追加 E22 Lite-SOD-C-RA 和轻量化 smoke 汇总表。 |
| 更新 | `PROJECT_LOG.md` | 记录本次新增/验证/训练动作。 |
| 更新 | `PROJECT_HANDOFF.md` | 更新接手重点到 A/B/C-RA smoke 完成状态。 |
| 更新 | `PROJECT_STATE.md` | 更新当前状态与下一步正式训练矩阵建议。 |

## 4. 本次检查与训练

- YAML 静态检查通过：模型 YAML 与两个配置 YAML 均可解析。
- dry-run 通过：输出目录为 `runs/sod/E22_Lite-SOD-C-RA_no_piou_*`，`workers=0`、`cache=True`、`device=0` 映射正确。
- model build check 通过：8,011,608 Params，25.3 GFLOPs。
- Detect 仍为 P2/P3/P4/P5，输入层 `[31, 19, 23, 27]`。
- 通道策略为 P2/P3/P4/P5 = 80/192/384/768。
- GhostConv 替换层沿用 Lite-SOD-B：`[14, 19, 20, 23, 24, 27]`。
- PIoU 未启用，loss 文件未修改。
- backbone、C2f-EMA、Detect head 均未修改。
- 完成 1 epoch tiny smoke：成功，无 NaN，无 OOM，无 DataLoader 卡死。
- 完成 5 epoch smoke：成功，无 NaN，无 OOM，无 DataLoader 卡死。
- 输出目录：
  - `runs/sod/E22_Lite-SOD-C-RA_no_piou_smoke`
  - `runs/sod/E22_Lite-SOD-C-RA_no_piou_5ep`
- 训练中仍出现 Ultralytics AMP 离线下载检查警告、PyTorch deterministic warning 和部分 Windows 控制台编码显示问题，均为非致命问题。
- 本次没有启动任何 50 epoch 长训；确认不存在 `runs/sod/E22_Lite-SOD-C-RA_no_piou_50ep`。

## 5. 当前输出规范

- 所有训练必须通过 `train.py`。
- 输出路径必须为 `project=runs/<type>`，`name=Exx_experiment_name`。
- 禁止使用 YOLO 默认 `runs/detect/*` 作为正式输出。
- 禁止 `runs/runs/*`、`runs/detect/runs/*` 嵌套。
- baseline 结果不可覆盖。
- 旧异常目录 `runs/sod/E03_batch8_full_50ep` 只作 aborted 记录，不作最终结果。

## 6. Windows 训练稳定性记录

- 曾出现 `YOLOv8 + Windows + 多进程 DataLoader` 疑似死锁。
- batch8 或长训必须显式使用 `workers=0`。
- 推荐 `cache=True`、`device=0`。
- 判断卡死不能只看 `results.csv`，要结合日志、GPU 利用率、`last.pt` 修改时间。
- Windows 后台 `conda run` / `Start-Process` 可能有日志或编码问题；近期 smoke 使用 `mypytorch` 环境 `python.exe` 前台运行。

## 7. Lite-SOD-A 50ep batch8 异常中断记录

- 时间：2026-06-30。
- 异常实验：`E20_Lite-SOD-A_uniform_no_piou_50ep`。
- 输出目录：`runs/sod/E20_Lite-SOD-A_uniform_no_piou_50ep`。
- 现象：`results.csv` 只到 epoch 2，`results.csv` 和 `weights/last.pt` 修改时间长时间未更新；用户判断为异常卡住。
- 当前检查：未发现仍在运行的 `python.exe` 训练进程，`nvidia-smi` 未显示 Python 计算进程。
- 处理：不删除、不覆盖原目录；将其记录为 `abnormal / stuck after epoch 2`，不作为 Lite-SOD-A 正式 50ep 结果。
- 新增回退配置：`configs/lite_sod_a_uniform_no_piou_50ep_b4.yaml`。
- dry-run 结果：`epochs=50`、`batch=4`、`workers=0`、`cache=True`、`device=0`、`loss=default`，输出目录 `runs/sod/E20_Lite-SOD-A_uniform_no_piou_50ep_b4` 当前不存在。
- 本次未自动启动训练，未修改模型 YAML、`train.py` 或 loss。

## 8. Lite-SOD-A 50ep batch4 正式训练完成记录

- 时间：2026-06-30。
- 实验：`E20_Lite-SOD-A_uniform_no_piou_50ep_b4`。
- 配置：`configs/lite_sod_a_uniform_no_piou_50ep_b4.yaml`。
- 模型：`models/yolov8s_lite_sod_a_uniform.yaml`。
- 输出目录：`runs/sod/E20_Lite-SOD-A_uniform_no_piou_50ep_b4`。
- 检查结果：`results.csv` 共 50 行，训练完成 50/50 epoch。
- 最终指标：P=0.42853，R=0.34123，mAP50=0.30901，mAP50-95=0.17197。
- best epoch：按 mAP50-95 为 epoch 50；按 mAP50 峰值为 epoch 46。
- 输出文件：`results.csv`、`results.png`、`BoxPR_curve.png`、`confusion_matrix.png`、`weights/best.pt`、`weights/last.pt`、`val_batch*_pred.jpg` 均存在。
- 训练耗时：`results.csv` 记录约 13095.6 秒，约 3.64 小时。
- 异常记录：未从结果文件观察到 OOM、NaN 或 DataLoader 卡死；`PR_curve.png` 未生成，但 `BoxPR_curve.png` 已生成。
- 本次只查看结果并更新维护文档；未修改模型 YAML、`train.py` 或 loss，未启动新训练。

## 9. Lite-SOD-C-RA 50ep batch4 正式训练配置准备

- 时间：2026-07-01。
- 新增配置：`configs/lite_sod_c_ra_no_piou_50ep_b4.yaml`。
- 计划实验：`E22_Lite-SOD-C-RA_no_piou_50ep_b4`。
- 计划输出目录：`runs/sod/E22_Lite-SOD-C-RA_no_piou_50ep_b4`。
- 输出目录检查：当前不存在，不会覆盖 smoke、E20、baseline 或旧异常目录。
- dry-run 结果：`epochs=50`、`batch=4`、`workers=0`、`cache=True`、`device=0`、`project=runs/sod`、`name=E22_Lite-SOD-C-RA_no_piou_50ep_b4`。
- build check：通过项目注册路径构建成功，Params=8,011,608，Detect=4 分支，stride=4/8/16/32。
- 结构确认：P2/P3/P4/P5 通道为 80/192/384/768；GhostConv 层为 `[14, 19, 20, 23, 24, 27]`；PIoU 未启用。
- 本次未修改模型 YAML、`train.py`、loss、GhostConv 替换层或 C-RA 通道；未启动长训。

## 10. Lite-SOD-C-RA 50ep batch4 正式训练完成记录

- 时间：2026-07-01。
- 实验：`E22_Lite-SOD-C-RA_no_piou_50ep_b4`。
- 配置：`configs/lite_sod_c_ra_no_piou_50ep_b4.yaml`。
- 模型：`models/yolov8s_lite_sod_c_ra.yaml`。
- 输出目录：`runs/sod/E22_Lite-SOD-C-RA_no_piou_50ep_b4`。
- 检查结果：`results.csv` 共 50 行，训练完成 50/50 epoch。
- 最终指标：P=0.40966，R=0.32619，mAP50=0.29814，mAP50-95=0.16569。
- best epoch：按 mAP50 和 mAP50-95 均为 epoch 49。
- 输出文件：`results.csv`、`results.png`、`BoxPR_curve.png`、`confusion_matrix.png`、`weights/best.pt`、`weights/last.pt`、`val_batch*_pred.jpg` 均存在。
- 训练耗时：`results.csv` 记录约 14146.3 秒，约 3.93 小时。
- 异常记录：未从结果文件观察到 OOM、NaN 或 DataLoader 卡死；`PR_curve.png` 未生成，但 `BoxPR_curve.png` 已生成。
- 本次只查看结果并更新维护文档；未修改模型 YAML、`train.py`、loss、GhostConv 替换层或 C-RA 通道，未启动新训练。

## 11. Lite-SOD-B 50ep batch4 正式训练配置准备

- 时间：2026-07-01。
- 新增配置：`configs/lite_sod_b_ghost_no_piou_50ep_b4.yaml`。
- 计划实验：`E21_Lite-SOD-B_ghost_no_piou_50ep_b4`。
- 计划输出目录：`runs/sod/E21_Lite-SOD-B_ghost_no_piou_50ep_b4`。
- 输出目录检查：当前不存在，不会覆盖 smoke、E20、E22、baseline 或旧异常目录。
- dry-run 结果：`epochs=50`、`batch=4`、`workers=0`、`cache=True`、`device=0`、`project=runs/sod`、`name=E21_Lite-SOD-B_ghost_no_piou_50ep_b4`。
- build check：通过项目注册路径构建成功，Params=8,104,376，Detect=4 分支，stride=4/8/16/32。
- 结构确认：P2/P3/P4/P5 通道为 96/192/384/768；GhostConv 层为 `[14, 19, 20, 23, 24, 27]`；PIoU 未启用。
- 本次未修改模型 YAML、`train.py`、loss、GhostConv 替换层或 C-RA 通道；未启动长训。

## 12. Lite-SOD-B 50ep batch4 正式训练完成记录

- 时间：2026-07-02。
- 实验：`E21_Lite-SOD-B_ghost_no_piou_50ep_b4`。
- 配置：`configs/lite_sod_b_ghost_no_piou_50ep_b4.yaml`。
- 模型：`models/yolov8s_lite_sod_b_ghost.yaml`。
- 输出目录：`runs/sod/E21_Lite-SOD-B_ghost_no_piou_50ep_b4`。
- 检查结果：`results.csv` 共 50 行，训练完成 50/50 epoch。
- 最终指标：P=0.42397，R=0.32841，mAP50=0.29867，mAP50-95=0.16580。
- best epoch：按 mAP50 和 mAP50-95 均为 epoch 49。
- 输出文件：`results.csv`、`results.png`、`BoxPR_curve.png`、`confusion_matrix.png`、`weights/best.pt`、`weights/last.pt`、`val_batch*_pred.jpg` 均存在。
- 训练耗时：`results.csv` 记录约 12968.4 秒，约 3.60 小时。
- 异常记录：未从结果文件观察到 OOM、NaN 或 DataLoader 卡死；`PR_curve.png` 未生成，但 `BoxPR_curve.png` 已生成。
- 本次只查看结果并更新维护文档；未修改模型 YAML、`train.py`、loss、GhostConv 替换层或 C-RA 通道，未启动新训练。

## 13. Lite-SOD 最小训练交付包记录

- 时间：2026-07-02。
- 交付目录：`D:\桌面\Lite-SOD-Train-Package`。
- 操作：创建最小可运行训练包，用于交给队友运行 Lite-SOD-A / B / C-RA。
- 已复制：`train.py`、3 个 Lite-SOD 模型 YAML、3 个 50ep b4 配置、3 个 smoke 配置、`configs/visdrone.yaml`、自定义模块 `models/modules`、PIoU 兼容代码 `models/loss`、model.info、维护文档快照和环境记录。
- 已新建：`DELIVERY_README.md`、`FILE_MANIFEST.md`、`QUICK_CHECK.md`、`requirements_note.txt`、`docs/VALIDATION_REPORT.txt`。
- Ultralytics 处理：未复制完整 `ultralytics/`；当前项目无本地 Ultralytics 源码改动，GhostConv 来自官方 `ultralytics==8.4.66`，C2fEMA 由 `train.py` 运行时注册。
- 未复制：数据集、完整 `runs`、大权重 `best.pt/last.pt`、`.git`、`.venv`、`wandb`、`__pycache__`。
- 最小验证：包内 dry-run 成功；C-RA 模型 build check 成功，参数量为 8,011,608。
- 本次未启动任何训练，未删除或移动原项目文件。
