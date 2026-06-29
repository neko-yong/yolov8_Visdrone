# SOD-YOLO 最小交接包说明

## 1. 当前交接包用途

本交接包用于在已有 YOLOv8 baseline 项目上运行 SOD-YOLO 复现、no-PIoU SOD 对照、batch8 full SOD 训练。包内只包含 SOD 相关必要代码、配置和说明，不包含数据集、完整 runs、训练权重或旧异常训练目录。

## 2. 队友需要具备的前提

- 已有可运行的 YOLOv8 baseline 项目。
- 已有 VisDrone_YOLO 数据集。
- 已有可运行的 Python / Conda / PyTorch / Ultralytics 环境。
- 建议优先使用已经跑通 baseline 的环境，不建议新建或覆盖环境。
- `requirements.txt` 仅作依赖参考；缺什么再装什么，不要直接覆盖已稳定环境。

## 3. 推荐放置方式

将本包内容合并到队友项目根目录。若存在同名文件，必须先备份。

- `train.py`：放到项目根目录，作为统一训练入口。
- `configs/*.yaml`：放到项目根目录下的 `configs/`。
- `models/*.yaml`：放到项目根目录下的 `models/`。
- `models/modules/*.py`：放到项目根目录下的 `models/modules/`。
- `models/loss/*.py`：放到项目根目录下的 `models/loss/`。
- `RUNS_POLICY.md`、`PROJECT_STATE.md`、`experiments_log.md`、`PROJECT_HANDBOOK.md`：放到根目录作为维护参考。

注意：队友如果已有自己的 `train.py` 或 `models/` 自定义目录，不要直接覆盖，先对比差异再合并。

## 4. 数据配置修改

必须修改 `configs/visdrone.yaml`：

```yaml
path: /path/to/VisDrone_YOLO
train: images/train
val: images/val
```

把 `path` 改成队友本机的 VisDrone_YOLO 根目录。不要使用原项目机器上的绝对路径。

## 5. 推荐训练命令

A. dry-run 检查命令：

```bash
python train.py --config configs/e03_b2_batch8_full_50ep_workers0.yaml --dry-run
```

B. no-PIoU SOD 训练命令：

```bash
python train.py --config configs/e03_b2_no_piou_50ep_b5.yaml
```

C. batch8 full SOD workers0 训练命令：

```bash
python train.py --config configs/e03_b2_batch8_full_50ep_workers0.yaml
```

Windows 上推荐直接使用环境内 `python.exe` 的完整路径前台运行，例如：

```bash
C:\path\to\env\python.exe train.py --config configs/e03_b2_batch8_full_50ep_workers0.yaml
```

## 6. 关键稳定性规则

- Windows 下长训必须 `workers=0`。
- batch8 长训必须 `workers=0`。
- 建议 `cache=True`。
- 明确设置 `device=0`。
- 不要使用旧异常目录 `runs/sod/E03_batch8_full_50ep`。
- 每个实验必须使用新的 `name`，避免覆盖历史输出。
- 所有实验输出必须遵守 `RUNS_POLICY.md`：`project=runs/<type>`，`name=Exx_experiment_name`。

## 7. 当前已知风险

- full SOD + PIoU 当前可能不如 baseline。
- PIoU 在当前复现条件下可能拉低整体 mAP 和 recall。
- no-PIoU 版本目前更有希望。
- batch8 在 8GB 显存上可能接近显存上限。
- 如果使用共享 GPU 内存，训练会显著变慢。
- Windows 后台启动、`conda run`、`Start-Process` 可能导致日志或编码问题。
- 推荐直接用环境 `python.exe` 完整路径前台运行训练。

## 8. 结果判断标准

- `results.csv` 每个 epoch 写一行。
- `results.png` 通常在训练结束后生成。
- `best.pt` / `last.pt` 位于 `weights/` 目录下。
- 判断卡死不能只看 `results.csv`，必须结合 GPU 利用率、`last.pt` 修改时间、日志更新时间。
- 若连续 30 分钟没有新 epoch、日志无更新、`last.pt` 无更新，可判定疑似卡死。

## 9. 当前建议实验优先级

1. 优先跑 `configs/e03_b2_no_piou_50ep_b5.yaml`。
2. 再跑 `configs/e03_b2_batch8_full_50ep_workers0.yaml`。
3. 如果要冲 mAP50 约 0.40，建议基于 no-PIoU SOD 做 `imgsz=768` 微调，而不是继续死磕 full SOD + PIoU。

## 10. 可选权重文件

本包默认不包含任何权重。若需要手动传权重，可从原项目中单独选择：

- no-PIoU：`runs/sod/E03_no_piou_50ep_b5/weights/best.pt`
- full SOD 30ep：`runs/sod/E03_full_sod_30ep_b5/weights/best.pt`
- 旧 batch8 full 异常训练权重不建议作为最终结果使用：`runs/sod/E03_batch8_full_50ep/weights/best.pt`
