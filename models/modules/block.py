"""Custom YOLO blocks used by the SOD-YOLO reproduction project."""

from __future__ import annotations

import torch
from torch import nn

from ultralytics.nn.modules.conv import Conv
from ultralytics.nn.modules.block import Bottleneck

from .ema import EMAAttention


class C2fEMA(nn.Module):
    """C2f block with EMA attention inserted after bottleneck aggregation."""

    def __init__(
        self,
        c1: int,
        c2: int,
        n: int = 1,
        shortcut: bool = False,
        g: int = 1,
        e: float = 0.5,
        reduction: int = 16,
    ) -> None:
        super().__init__()
        self.c = int(c2 * e)
        self.cv1 = Conv(c1, 2 * self.c, 1, 1)
        self.cv2 = Conv((2 + n) * self.c, c2, 1)
        self.m = nn.ModuleList(
            Bottleneck(self.c, self.c, shortcut, g, k=((3, 3), (3, 3)), e=1.0) for _ in range(n)
        )
        self.ema = EMAAttention(c2, reduction=reduction)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = list(self.cv1(x).chunk(2, 1))
        y.extend(m(y[-1]) for m in self.m)
        return self.ema(self.cv2(torch.cat(y, 1)))

    def forward_split(self, x: torch.Tensor) -> torch.Tensor:
        y = self.cv1(x).split((self.c, self.c), 1)
        y = [y[0], y[1]]
        y.extend(m(y[-1]) for m in self.m)
        return self.ema(self.cv2(torch.cat(y, 1)))
