# 无人机视角下的车辆目标检测

本项目基于 Ultralytics YOLOv8 完成 VisDrone2019-DET 无人机视角车辆与道路目标检测，包括原始标注转换、数据集检查、YOLOv8s baseline 训练及结果归档。

## 环境说明

- Windows 11
- Conda 环境：`mypytorch`
- Python 3.12
- Ultralytics 8.4.66
- PyTorch 2.3.1 + CUDA 11.8
- GPU：NVIDIA GeForce RTX 4060 Laptop GPU 8GB

进入环境并检查 Ultralytics：

```powershell
conda activate mypytorch
yolo checks
```

## 数据集

Git 仓库不包含 VisDrone 数据集。下载 VisDrone2019-DET 后，将原始数据放置为：

```text
datasets/VisDrone/
├── VisDrone2019-DET-train/
│   ├── images/
│   └── annotations/
├── VisDrone2019-DET-val/
│   ├── images/
│   └── annotations/
└── VisDrone2019-DET-test-dev/
```

## 数据转换

将 VisDrone 原始标注转换为 Ultralytics YOLO 检测格式：

```powershell
python scripts/convert_visdrone_to_yolo.py
```

转换结果保存在 `datasets/VisDrone_YOLO/`。

## 数据检查

检查图片、标签、空标签和类别实例数量，并随机生成 5 张标注可视化：

```powershell
python scripts/check_dataset.py
```

可视化结果默认保存在 `runs/dataset_check/`。

## Baseline 训练

项目使用本地 YOLOv8s 预训练权重。将 `yolov8s.pt` 放入 `weights/` 后运行：

```powershell
yolo detect train model=weights/yolov8s.pt data=configs/visdrone.yaml imgsz=640 epochs=50 batch=8 workers=4 device=0 project=runs/baseline name=yolov8s_visdrone_640
```

## Baseline 结果

实验配置：YOLOv8s、输入尺寸 640、50 epochs、batch size 8。

| Precision | Recall | mAP50 | mAP50-95 | Best epoch |
| ---: | ---: | ---: | ---: | ---: |
| 0.52613 | 0.38791 | 0.38128 | 0.21975 | 46 |

精选训练曲线、混淆矩阵、PR 曲线和预测样例位于 [`docs/baseline_results/`](docs/baseline_results/)；完整实验记录见 [`experiments_log.md`](experiments_log.md)。

## 仓库说明

受文件大小和数据集许可限制，Git 仓库不包含以下内容：

- `datasets/` 下的原始数据集和转换后数据集
- `weights/` 下的预训练权重
- 训练生成的 `best.pt`、`last.pt` 等模型权重
- `runs/` 下的完整训练、验证和预测输出

复现实验前需自行准备数据集及 `weights/yolov8s.pt`。仓库仅保留可复现代码、配置和少量精选结果文件。
