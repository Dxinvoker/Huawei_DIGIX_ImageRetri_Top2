'''
Author      : now more
Contact     : lin.honghui@qq.com
LastEditors: Please set LastEditors
LastEditTime: 2020-08-12 15:15:27
Description : 
'''
from ..dataset import build_dataset
from ..transforms import build_transforms

import data.dataloader.sampler as Samplers
import data.dataloader.collate_fn as my_collate_fn
from torch.utils.data import DataLoader

def make_dataloader(cfg_data_pipeline):
    cfg_data_pipeline = cfg_data_pipeline.copy()
    cfg_dataset = cfg_data_pipeline.pop('dataset')
    cfg_transforms = cfg_data_pipeline.pop('transforms')
    cfg_dataloader = cfg_data_pipeline.pop('dataloader')

    transforms = build_transforms(cfg_transforms)
    dataset = build_dataset(cfg_dataset,transforms)

    if 'sampler' in cfg_dataloader:
        cfg_sample = cfg_dataloader.pop('sampler')
        sample_type = cfg_sample.pop('type')
        sampler = getattr(Samplers,sample_type)(dataset.label,**cfg_sample)
        dataloader = DataLoader(dataset,sampler=sampler,**cfg_dataloader)
        return dataloader
    else:
        if "collate_fn" in cfg_dataloader:
            cfg_collate_fn = cfg_dataloader.pop("collate_fn")
            if hasattr(my_collate_fn,cfg_collate_fn):
                collate_fn = getattr(my_collate_fn,cfg_collate_fn)
                dataloader  = DataLoader(dataset,collate_fn=collate_fn,**cfg_dataloader)
                return dataloader
        else:
            dataloader  = DataLoader(dataset,**cfg_dataloader)
            return dataloader