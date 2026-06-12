# YOLOv8 环境信息

采集环境：Conda `mypytorch`，Windows。详细命令原始输出位于 [`docs/environment/`](docs/environment/)。

## 核心版本

| 项目 | 版本或型号 |
| --- | --- |
| Python | 3.12.7 |
| 操作系统 | Windows 11 (`10.0.26200`) |
| GPU | NVIDIA GeForce RTX 4060 Laptop GPU 8GB |
| NVIDIA 驱动 | 591.86 |
| 驱动支持的 CUDA 版本 | 13.1 |
| PyTorch 构建使用的 CUDA 版本 | 11.8 |
| torch | 2.3.1+cu118 |
| torchvision | 0.18.1+cu118 |
| ultralytics | 8.4.66 |
| numpy | 1.26.4 |
| opencv-python | 4.13.0.92 |

> `nvidia-smi` 显示的 CUDA 13.1 是当前驱动支持的最高 CUDA 版本；项目中的 PyTorch wheel 使用 CUDA 11.8 构建。两者同时出现是正常的。

## 环境验证

在项目根目录运行：

```powershell
conda activate mypytorch
python export_env.py
yolo checks
```

## Windows 快速复现

建议创建全新的 Conda 环境：

```powershell
conda create -n mypytorch python=3.12.7 -y
conda activate mypytorch
python -m pip install --upgrade pip
python -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu118 --no-deps
python export_env.py
yolo checks
```

`requirements.txt` 是当前环境 69 个 pip 包的完整版本快照，包含开发和 Notebook 相关依赖。这里使用 `--no-deps`，是为了严格安装文件中记录的版本，而不是让 pip 的依赖解析器自动替换版本。

## 已知依赖状态

当前环境执行 `pip check` 会报告：

```text
opencv-python 4.13.0.92 has requirement numpy>=2; python_version >= "3.9", but you have numpy 1.26.4.
```

这是当前已安装环境的真实状态。该组合已成功完成 YOLOv8 数据检查、smoke test 和 50 epoch baseline 训练，但同步时不应隐藏这项元数据冲突。若队友只要求复现实验，优先保持本文件记录的精确版本；若要升级依赖，应单独建立新环境并重新验证训练结果。

## 原始命令输出

- [`python_version.txt`](docs/environment/python_version.txt)：`python --version`
- [`pip_list.txt`](docs/environment/pip_list.txt)：`pip list`
- [`nvidia_smi.txt`](docs/environment/nvidia_smi.txt)：`nvidia-smi`
- [`yolo_checks.txt`](docs/environment/yolo_checks.txt)：`yolo checks`
- [`export_env_output.txt`](docs/environment/export_env_output.txt)：`python export_env.py`
