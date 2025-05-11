# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 08:55:33 2025

@author: tlee
"""
import os
import shutil
from glob import glob
from tqdm import tqdm

def unload(source,dest):
    for i, file in enumerate(tqdm(glob(f'{source}/**/*.NEF',recursive=True))):
        shutil.copy(file, dest)


ph = unload(source='H:/DCIM',
       dest='D:/Wildlife Photos/Birds/Raw Photos/FloridaTrip')
