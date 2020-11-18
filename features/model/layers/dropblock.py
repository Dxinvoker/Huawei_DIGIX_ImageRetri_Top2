'''
Author      : now more
Contact     : lin.honghui@qq.com
LastEditors: Please set LastEditors
Description : 
LastEditTime: 2020-09-12 12:00:12
'''
import torch
import torch.nn.functional as F
from torch import nn
import numpy as np

class DropBlock2D(nn.Module):
    r"""Randomly zeroes spatial blocks of the input tensor.
    As described in the paper
    `DropBlock: A regularization method for convolutional networks`_ ,
    dropping whole blocks of feature map allows to remove semantic
    information as compared to regular dropout.
    Args:
        keep_prob (float, optional): probability of an element to be kept.
        Authors recommend to linearly decrease this value from 1 to desired
        value.
        block_size (int, optional): size of the block. Block size in paper
        usually equals last feature map dimensions.
    Shape:
        - Input: :math:`(N, C, H, W)`
        - Output: :math:`(N, C, H, W)` (same shape as input)
    .. _DropBlock: A regularization method for convolutional networks:
       https://arxiv.org/abs/1810.12890
    """

    def __init__(self, keep_prob=0.9, block_size=7):
        super(DropBlock2D, self).__init__()
        self.keep_prob = keep_prob
        self.block_size = block_size

    def forward(self, input):
        if not self.training or self.keep_prob == 1:
            return input
        gamma = (1. - self.keep_prob) / self.block_size ** 2
        for sh in input.shape[2:]:
            gamma *= sh / (sh - self.block_size + 1)
        M = torch.bernoulli(torch.ones_like(input) * gamma)
        Msum = F.conv2d(M,
                        torch.ones((input.shape[1], 1, self.block_size, self.block_size)).to(device=input.device,
                                                                                             dtype=input.dtype),
                        padding=self.block_size // 2,
                        groups=input.shape[1])
        torch.set_printoptions(threshold=5000)
        mask = (Msum < 1).to(device=input.device, dtype=input.dtype)
        return input * mask * mask.numel() /mask.sum() #TODO input * mask * self.keep_prob ?


class LinearScheduler(nn.Module):
    def __init__(self, dropblock, start_value=1, stop_value=0.9, nr_steps=3e4):
        super(LinearScheduler, self).__init__()
        self.dropblock = dropblock
        self.i = 0
        self.drop_values = np.linspace(start=int(start_value), stop=int(stop_value), num=int(nr_steps))

    def forward(self, x):
        self.step() # 每次迭代 更新 prob
        # print(self.dropblock.keep_prob)
        return self.dropblock(x)

    def step(self):
        if self.i < len(self.drop_values):
            self.dropblock.keep_prob = self.drop_values[self.i]
        self.i += 1