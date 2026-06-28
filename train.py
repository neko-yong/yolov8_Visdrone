"""统一训练入口：使用 configs/*.yaml 驱动 Ultralytics YOLOv8 实验。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


PROJECT_BY_TYPE = {
    "baseline": "runs/baseline",
    "sod": "runs/sod",
    "lite": "runs/lite",
    "ablation": "runs/ablation",
}

TRAIN_FIELD_MAP = {
    "model": "model",
    "imgsz": "imgsz",
    "epochs": "epochs",
    "batch": "batch",
    "optimizer": "optimizer",
    "lr0": "lr0",
    "momentum": "momentum",
    "weight_decay": "weight_decay",
    "augment": "augment",
}

SKIP_DEFAULT_VALUES = {"default", "YOLOv8默认", "默认"}


def load_yaml(path: Path) -> dict[str, Any]:
    """读取 YAML 文件并保证顶层为字典。"""
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"配置文件顶层必须是字典: {path}")
    return data


def resolve_config_path(path_text: str, root: Path) -> Path:
    """将配置中的相对路径解析到项目根目录。"""
    path = Path(path_text)
    if path.is_absolute():
        return path
    return root / path


def get_experiment_type(config: dict[str, Any]) -> str:
    experiment = config.get("experiment") or {}
    exp_type = experiment.get("type")
    if exp_type not in PROJECT_BY_TYPE:
        allowed = ", ".join(PROJECT_BY_TYPE)
        raise ValueError(f"未知实验类型: {exp_type!r}，允许值: {allowed}")
    return exp_type


def select_ablation(
    config: dict[str, Any],
    ablation_id: str | None,
    config_root: Path,
    project_root: Path,
) -> dict[str, Any]:
    """从 ablation.yaml 中选择一个消融实验，并合成可训练配置。"""
    experiments = config.get("experiments") or []
    if not experiments:
        raise ValueError("ablation 配置缺少 experiments 列表")
    if not ablation_id:
        available = ", ".join(str(item.get("id")) for item in experiments)
        raise ValueError(f"ablation 配置包含多个实验，请指定 --ablation-id。可选: {available}")

    selected = next((item for item in experiments if item.get("id") == ablation_id), None)
    if selected is None:
        available = ", ".join(str(item.get("id")) for item in experiments)
        raise ValueError(f"未找到消融实验 {ablation_id!r}。可选: {available}")

    base_config: dict[str, Any] = {}
    referenced = selected.get("config") or selected.get("base")
    if referenced:
        base_path = resolve_config_path(str(referenced), project_root)
        base_config = load_yaml(base_path)

    common = config.get("common") or {}
    output = selected.get("output") or {}
    selected_model = selected.get("model")
    if selected.get("implementation_note") and not selected_model:
        selected_model = None

    merged = {
        **base_config,
        "experiment": {
            "id": selected.get("id"),
            "name": selected.get("name"),
            "type": "ablation",
            "description": selected.get("description"),
        },
        "data": {
            **(base_config.get("data") or {}),
            "dataset": common.get("dataset", (base_config.get("data") or {}).get("dataset")),
            "config": common.get("data_config", (base_config.get("data") or {}).get("config")),
        },
        "train": {
            **(base_config.get("train") or {}),
            "model": selected_model
            if selected_model is not None
            else (
                None
                if selected.get("implementation_note")
                else (base_config.get("train") or {}).get("model")
            ),
            "imgsz": common.get("imgsz", (base_config.get("train") or {}).get("imgsz")),
            "epochs": common.get("epochs", (base_config.get("train") or {}).get("epochs")),
            "batch": common.get("batch", (base_config.get("train") or {}).get("batch")),
        },
        "output": {
            "project": PROJECT_BY_TYPE["ablation"],
            "name": output.get("name") or selected.get("name"),
        },
    }
    return merged


def build_train_kwargs(config: dict[str, Any], project_root: Path) -> dict[str, Any]:
    """将项目配置映射为 YOLO.train(**kwargs) 参数。"""
    exp_type = get_experiment_type(config)
    train = config.get("train") or {}
    data = config.get("data") or {}
    output = config.get("output") or {}

    if not isinstance(train, dict):
        raise ValueError("配置字段 train 必须是字典")
    if not isinstance(output, dict):
        raise ValueError("配置字段 output 必须是字典")

    model_path = train.get("model")
    if not model_path:
        raise ValueError(
            "当前配置缺少 train.model。"
            "如果这是 SOD/lite 占位配置，请先完成模型结构实现并写入模型 yaml 或权重路径。"
        )

    kwargs: dict[str, Any] = {"model": model_path}

    data_config = data.get("config") or data.get("data_config")
    if data_config:
        kwargs["data"] = str(resolve_config_path(str(data_config), project_root))
    else:
        raise ValueError("配置缺少 data.config，无法定位数据集 yaml")

    for config_key, yolo_key in TRAIN_FIELD_MAP.items():
        if config_key == "model":
            continue
        value = train.get(config_key)
        if value is None:
            continue
        if isinstance(value, str) and value in SKIP_DEFAULT_VALUES:
            continue
        kwargs[yolo_key] = value

    project = output.get("project") or PROJECT_BY_TYPE[exp_type]
    expected_project = PROJECT_BY_TYPE[exp_type]
    if project != expected_project:
        project = expected_project

    name = output.get("name") or (config.get("experiment") or {}).get("name")
    if not name:
        raise ValueError("配置缺少 output.name 或 experiment.name")

    kwargs["project"] = project
    kwargs["name"] = name
    return kwargs


def run_train(train_kwargs: dict[str, Any]) -> None:
    """调用 Ultralytics YOLOv8 训练 API。"""
    from ultralytics import YOLO

    model_path = train_kwargs.pop("model")
    model = YOLO(model_path)
    model.train(**train_kwargs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用 configs/*.yaml 启动 YOLOv8 实验训练")
    parser.add_argument("--config", required=True, type=Path, help="实验配置文件，例如 configs/baseline.yaml")
    parser.add_argument("--ablation-id", help="当 --config 为 configs/ablation.yaml 时指定 Exp1 / Exp2 / Exp3")
    parser.add_argument("--dry-run", action="store_true", help="只打印映射后的 YOLO 参数，不启动训练")
    return parser.parse_args()


def main() -> None:
    try:
        args = parse_args()
        project_root = Path(__file__).resolve().parent
        config_path = args.config if args.config.is_absolute() else project_root / args.config
        config = load_yaml(config_path)

        if get_experiment_type(config) == "ablation":
            config = select_ablation(config, args.ablation_id, config_path.parent, project_root)

        train_kwargs = build_train_kwargs(config, project_root)

        if args.dry_run:
            print("映射后的 YOLOv8 train 参数：")
            for key in sorted(train_kwargs):
                print(f"{key}: {train_kwargs[key]}")
            return

        run_train(train_kwargs)
    except ValueError as error:
        print(f"配置错误: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
